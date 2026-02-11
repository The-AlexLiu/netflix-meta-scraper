import argparse
from playwright.async_api import async_playwright
import os
import asyncio

async def generate_title_image(title, date_range, output_path=None):
    """
    Generates a Redbook title page image (Async).
    
    Args:
        title (str): Main title text (e.g., "收视冠军")
        date_range (str): Date range text (e.g., "2月9日～2月15日")
        output_path (str): Absolute path to save the image. If None, returns None.
        
    Returns:
        str: Path to the generated image.
    """
    if not output_path:
        return None
        
    # Current directory where this script resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_url = f"file://{os.path.join(script_dir, 'index.html')}"
    
    # URL with parameters
    url = f"{file_url}?title={title}&date={date_range}"
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch()
            # Set viewport to exact dimensions required (1242x1656)
            page = await browser.new_page(viewport={"width": 1242, "height": 1656})
            
            print(f"Generating Title Page: {url}")
            await page.goto(url)
            
            # Ensure the element is visible
            await page.wait_for_selector("#capture")
            
            # Taking screenshot full page
            await page.screenshot(path=output_path, full_page=True, type="jpeg", quality=90)
            
            print(f"Title Page Generated: {output_path}")
            await browser.close()
            return output_path
    except Exception as e:
        print(f"Error generating title page: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Redbook Title Page Image")
    parser.add_argument("--title", default="收视冠军", help="Main title text")
    parser.add_argument("--date", default="2月9日～2月15日", help="Date range text")
    parser.add_argument("--output", default="Title_Page.jpg", help="Output filename")
    
    args = parser.parse_args()
    
    generate_title_image(args.title, args.date, os.path.abspath(args.output))
