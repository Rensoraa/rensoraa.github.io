import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
HTML_FILE = "p100/index.html"
POSTED_LOG = ".github/scripts/posted_images.txt"

def get_posted_images():
    """Load previously posted images from file."""
    if not os.path.exists(POSTED_LOG):
        return set()
    with open(POSTED_LOG, "r") as f:
        return set(f.read().splitlines())

def save_posted_images(images):
    """Save the set of posted images back to the file."""
    with open(POSTED_LOG, "w") as f:
        f.write("\n".join(images))

def main():
    if not WEBHOOK_URL:
        print("Missing DISCORD_WEBHOOK secret.")
        return

    # Load HTML
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    body = soup.body
    if not body:
        print("No <body> found in HTML.")
        return

    posted = get_posted_images()
    new_posted = set(posted)

    # Find all images inside div.screenshot
    imgs = [
        img
        for div in body.find_all("div", class_="screenshot")
        for img in div.find_all("img", src=True)
    ]

    for img in imgs:
        src = img["src"]

        
        if src in posted or "assets/" not in src:
            continue

        alt_text = img.get("alt", "Unknown")
        title_text = img.get("title", "Unknown")

        # Build GitHub Pages URL
        image_url = f"https://{os.getenv('GITHUB_REPOSITORY_OWNER')}.github.io/p100/{quote(src.lstrip('./'))}"
        
        print(f"Posting embed with image: {image_url}")
        # Build embed
        embed = {
            "embeds": [{
                "title": f"📸 New p100 just dropped",
                "description": f"Character: {alt_text}\n{title_text}\n`{src}`",
                "image": {"url": f"{image_url}?v={os.urandom(4).hex()}"},
                "color": 0xFF0000
            }]
        }

        # Post to Discord
        res = requests.post(WEBHOOK_URL, json=embed)
        if res.status_code == 204:
            print(f"Posted {src}")
            new_posted.add(src)
        else:
            print(f"Failed to post {src}: {res.status_code} - {res.text}")

    # Save updated posted images
    save_posted_images(new_posted)

if __name__ == "__main__":
    main()
