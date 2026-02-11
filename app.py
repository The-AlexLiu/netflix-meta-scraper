from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os
import json
import uuid
import csv
import re
import shutil
from typing import Dict, List
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from openai import OpenAI

app = FastAPI()

# Load env
load_dotenv()
try:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
except Exception as e:
    print(f"Warning: OpenAI client init failed: {e}")
    client = None

# Mount images directory
if not os.path.exists("images"):
    os.makedirs("images")
app.mount("/images", StaticFiles(directory="images"), name="images")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
jobs: Dict[str, dict] = {}

class ScrapeRequest(BaseModel):
    start_date: str = None
    end_date: str = None

def run_scraper_task(job_id: str, start: str, end: str):
    jobs[job_id]["status"] = "running"
    
    cmd = ["python3", "netflix_scraper.py"]
    if start: cmd.extend(["--start", start])
    if end: cmd.extend(["--end", end])
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    for line in process.stdout:
        stripped = line.strip()
        if not stripped:
            continue
        jobs[job_id]["logs"].append(stripped)
        # Parse progress from various output formats
        # Matches: "[3] Title (date)" or "Collected X items" or "Total: X"
        count_match = re.search(r'\[(\d+)\]', stripped)
        if count_match:
            jobs[job_id]["count"] = int(count_match.group(1))
        total_match = re.search(r'Total:\s*(\d+)', stripped)
        if total_match:
            jobs[job_id]["count"] = int(total_match.group(1))
            
    process.wait()
    jobs[job_id]["status"] = "completed" if process.returncode == 0 else "failed"

@app.post("/api/scrape")
async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "logs": [],
        "count": 0,
        "start_date": request.start_date,
        "end_date": request.end_date
    }
    
    # Cleanup old data if starting a new run
    if os.path.exists("netflix_records.csv"):
        os.remove("netflix_records.csv")
    if os.path.exists("images"):
        # We don't delete the whole images folder to preserve cache if needed, 
        # but for a clean run arguably we should? 
        # User request implies they want ONLY the date range content.
        # Let's clean it to be safe and avoid confusion.
        shutil.rmtree("images")
        os.makedirs("images")
        
    background_tasks.add_task(run_scraper_task, job_id, request.start_date, request.end_date)
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]

@app.get("/api/results")
async def get_results():
    CSV_FILE = "netflix_records.csv"
    if not os.path.exists(CSV_FILE):
        return []
    
    results = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results

@app.get("/api/download")
async def download_package():
    zip_filename = "netflix_scraper_export"
    zip_path = f"{zip_filename}.zip"
    
    # Ensure any old zip is removed
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    temp_export_dir = "temp_export"
    if os.path.exists(temp_export_dir):
        shutil.rmtree(temp_export_dir)
        
    os.makedirs(temp_export_dir)
    images_dest = os.path.join(temp_export_dir, "images")
    if not os.path.exists(images_dest):
        os.makedirs(images_dest)
    
    # 1. Copy Title Page if exists
    title_page = os.path.join("images", "Title_Page.jpg")
    if os.path.exists(title_page):
        shutil.copy(title_page, temp_export_dir)

    # 2. Copy scraped images (but NOT CSV)
    if os.path.exists("images"):
        # We want images in an 'images' subfolder or root? User said "images/" folder
        # Let's keep them in 'images' subfolder inside zip for cleanliness, 
        # or root if they want flat list.
        # Plan said: "Zip should contain images/ folder with posters AND the title page."
        # So structure:
        #   netflix_data.zip/
        #       Title_Page.jpg
        #       images/
        #           poster1.jpg
        #           ...
        
        # images_dest is already temp_export_dir/images
        for item in os.listdir("images"):
            if item == "Title_Page.jpg": continue # Already copied to root
            if not item.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): continue
            
            s = os.path.join("images", item)
            d = os.path.join(images_dest, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)

    # Create zip from temp dir
    shutil.make_archive(zip_filename, 'zip', temp_export_dir)
    
    # Cleanup temp dir
    shutil.rmtree(temp_export_dir)
    
    return FileResponse(zip_path, filename="netflix_data.zip", media_type='application/zip')

class NoteRequest(BaseModel):
    start_date: str = None
    end_date: str = None
    override_title: str = None
    override_tags: str = None

@app.post("/api/generate_note")
async def generate_note(request: NoteRequest):
    if not client:
        return {"error": "OpenAI client not initialized. Check .env file."}
        
    # Read CSV and filter
    movies = []
    headers = []
    if os.path.exists("netflix_records.csv"):
        with open("netflix_records.csv", mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filter by date if provided
                # Date format in CSV is "YYYY/M/D" usually
                # Simple string comparison works if strict, but let's just include all for now 
                # or implement basic filtering if strings match.
                # The user scraper filters BEFORE saving to CSV usually? 
                # No, scraper appends? 
                # Actually, app.py cleans CSV on new run (lines 82-83), so CSV contains ONLY current run.
                # So we can just use all rows in CSV.
                movies.append(f"{row.get('Title')} (Released: {row.get('Release Date')})")
    
    if not movies:
        return {"note": "No movies found to generate a note for. Please scrape first!"}
        
    movie_list_str = "\n".join(movies)
    
    prompt = f"""
    You are a popular movie blogger on Xiaohongshu (Little Red Book). 
    Write an enthusiastic, emoji-filled post recommending these new Netflix movies.
    
    Movies:
    {movie_list_str}
    
    Requirements:
    1. Catchy Title with emojis. {f'MUST be exactly: "{request.override_title}"' if request.override_title else 'MUST be under 20 characters (including emojis).'}
    2. Enthusiastic tone.
    3. Brief mention of the movies.
    4. Use tags like {request.override_tags if request.override_tags else '#Netflix #NewMovies #WeekendVibes #MovieRecommendation'}.
    5. Language: Chinese (Simplified).
    6. STRICTLY FORBIDDEN: Do NOT use markdown bold syntax (**text**) or any markdown formatting. Use plain text and emojis only.
    7. Ensure the content is structured for mobile reading (short paragraphs).
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in social media content creation."},
                {"role": "user", "content": prompt}
            ]
        )
        note_content = completion.choices[0].message.content
        # Post-processing to remove any markdown bold syntax if it still appears
        note_content = note_content.replace("**", "").replace("__", "")
        return {"note": note_content}
    except Exception as e:
        return {"error": str(e)}

from title_generator.generate_image import generate_title_image

class TitleRequest(BaseModel):
    date_range: str
    title: str = "收视冠军"

@app.post("/api/generate_title")
async def generate_title(request: TitleRequest):
    try:
        # Output to "images/Title_Page.jpg"
        # Use simple fixed name for now or timestamp?
        # User wants it in the package. So "images/Title_Page.jpg" is good.
        output_path = os.path.join(os.getcwd(), "images", "Title_Page.jpg")
        
        # Run in executor to avoid blocking event loop? Playwright sync api blocks.
        # But for local tool it's fine.
        generated_path = await generate_title_image(request.title, request.date_range, output_path)
        
        if generated_path and os.path.exists(generated_path):
            return {"image_url": "Title_Page.jpg", "full_path": generated_path}
        else:
            return {"error": "Failed to generate image"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    import csv
    import re
    uvicorn.run(app, host="0.0.0.0", port=8000)
