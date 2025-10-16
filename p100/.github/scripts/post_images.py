import os
import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
HTML_FILE = "p100/index.html"
POSTED_LOG = ".github/scripts/posted_images.txt"

def get_posted_images():
    if not os.path.exists(POSTED_LOG):
        return set()
    with open(POSTED_LOG, "r") as f:
        return set(f.read().splitlines())

def save_posted_images(images):
    with open(POSTED_LOG, "w") as f:
        f.write("\n".join(images))

def main():
    if not WEBHOOK_URL:
        print("Missing DISCORD_WEBHOOK secret.")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    body = soup.body
    if not body:
        print("No <body> found.")
        return

    posted = get_posted_images()
    new_posted = set(posted)

    imgs = [img["src"] for img in body.find_all("img", src=True) if "assets/" in img["src"]]

    for src in imgs:
        if src in posted:
            continue

        image_url = f"https://{os.getenv('GITHUB_REPOSITORY_OWNER')}.github.io/{os.getenv('GITHUB_REPOSITORY').split('/')[-1]}/{src}"
        embed = {
            "embeds": [{
                "title": "📸 New P100 Posted",
                "description": f"Image from index.html:\n`{src}`",
                "image": {"url": image_url},
                "color": 0xFF0000
            }]
        }

        res = requests.post(WEBHOOK_URL, json=embed)
        if res.status_code == 204:
            print(f"Posted {src}")
            new_posted.add(src)
        else:
            print(f"Failed to post {src}: {res.status_code} - {res.text}")

    save_posted_images(new_posted)

if __name__ == "__main__":
    main()
