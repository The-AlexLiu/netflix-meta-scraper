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

app = FastAPI()

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
    
    # 1. Try to use CSV to filter images
    if os.path.exists("netflix_records.csv"):
        shutil.copy("netflix_records.csv", temp_export_dir)
        try:
            with open("netflix_records.csv", mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    poster = row.get("Poster Filename")
                    if poster and poster != "N/A":
                        src_path = os.path.join("images", poster)
                        if os.path.exists(src_path):
                            shutil.copy(src_path, images_dest)
        except Exception as e:
            print(f"Error filtering images for zip: {e}")
            # If CSV parsing fails, fallback to copying all images
            if os.path.exists("images"):
                 for item in os.listdir("images"):
                    s = os.path.join("images", item)
                    d = os.path.join(images_dest, item)
                    if os.path.isfile(s):
                        shutil.copy2(s, d)
    else:
        # 2. Fallback: No CSV, copy all images if they exist
        if os.path.exists("images"):
            for item in os.listdir("images"):
                s = os.path.join("images", item)
                d = os.path.join(images_dest, item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)

    # Create zip from temp dir
    shutil.make_archive(zip_filename, 'zip', temp_export_dir)
    
    # Cleanup temp dir
    shutil.rmtree(temp_export_dir)
    
    return FileResponse(zip_path, filename="netflix_data.zip", media_type='application/zip')

if __name__ == "__main__":
    import uvicorn
    import csv
    import re
    uvicorn.run(app, host="0.0.0.0", port=8000)
