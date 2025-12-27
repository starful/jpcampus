# scripts/repair_thumbnails.py
import os
import glob

# 깨진 이미지 URL
BROKEN_URL = "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=500"
# 교체할 정상 이미지 URL (일본 거리 풍경)
NEW_URL = "https://images.unsplash.com/photo-1528164344705-47542687000d?w=500"

CONTENT_DIR = "app/content"

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ Content directory not found: {CONTENT_DIR}")
        return

    files = glob.glob(os.path.join(CONTENT_DIR, "*.md"))
    count = 0
    
    print("🛠️ Scanning for broken thumbnails...")
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if BROKEN_URL in content:
            new_content = content.replace(BROKEN_URL, NEW_URL)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Repaired: {os.path.basename(filepath)}")
            count += 1
            
    if count == 0:
        print("✨ No broken thumbnails found.")
    else:
        print(f"🎉 Total {count} files repaired.")

if __name__ == "__main__":
    main()