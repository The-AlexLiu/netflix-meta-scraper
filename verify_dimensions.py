import os
from PIL import Image

IMAGE_DIR = "images"
TARGET_WIDTH = 450
TARGET_HEIGHT = 630

def verify_images():
    if not os.path.exists(IMAGE_DIR):
        print(f"Error: Directory '{IMAGE_DIR}' not found. Run netflix_scraper.py first.")
        return

    files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        print("No images found to verify.")
        return

    print(f"Verifying {len(files)} images...")
    passed = 0
    failed = 0

    for filename in files:
        path = os.path.join(IMAGE_DIR, filename)
        try:
            with Image.open(path) as img:
                w, h = img.size
                if w == TARGET_WIDTH and h == TARGET_HEIGHT:
                    # print(f"[PASS] {filename}: {w}x{h}")
                    passed += 1
                else:
                    print(f"[FAIL] {filename}: {w}x{h} (Expected {TARGET_WIDTH}x{TARGET_HEIGHT})")
                    failed += 1
        except Exception as e:
            print(f"[ERROR] Could not open {filename}: {e}")
            failed += 1

    print("-" * 30)
    print(f"Verification Complete.")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("SUCCESS: All images match the required dimensions (450x630).")
    else:
        print("WARNING: Some images have incorrect dimensions.")

if __name__ == "__main__":
    verify_images()
