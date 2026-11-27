from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

SOURCES = {
    "americano": "https://images.unsplash.com/photo-1571040328796-b84632420c3b",
    "apple-espresso": "https://images.unsplash.com/photo-1531835207745-506a1bc035d8",
    "cappuccino": "https://images.unsplash.com/photo-1534778101976-62847782c213",
    "pomelo": "https://images.unsplash.com/photo-1583073600538-f219abfb20bc",
    "iced-latte": "https://images.unsplash.com/photo-1584286595398-a59f21d313f5",
    "matcha": "https://images.unsplash.com/photo-1751563721808-3b81940b88f7",
    "chocolate": "https://images.unsplash.com/photo-1586985288206-3cdc4f67cd03",
}

class Preview(HTMLParser):
    image = None
    def handle_starttag(self, tag, values):
        attrs = dict(values)
        if tag == "meta" and attrs.get("property") == "og:image":
            self.image = attrs.get("content")

def get(url):
    with urlopen(Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=20) as response:
        return response.read()

def download(item):
    name, source = item
    image_url = source
    if not source.startswith("https://"):
        parser = Preview()
        parser.feed(get("https://unsplash.com/photos/" + source).decode())
        image_url = parser.image
    if not image_url or not image_url.startswith("https://images.unsplash.com/"):
        raise ValueError(f"Missing photo URL for {name}")
    image_url = image_url.split("?")[0] + "?w=820&fit=max&auto=format"
    image = Image.open(BytesIO(get(image_url))).convert("RGB")
    root = Path("public/drinks")
    root.mkdir(exist_ok=True, parents=True)
    cropped = ImageOps.fit(image, (640, 400), centering=(0.5, 0.43))
    cropped.save(root / (name + ".jpg"), quality=86, optimize=True)
    return name

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=7) as pool:
        futures = {pool.submit(download, pair): pair[0] for pair in SOURCES.items()}
        for future, name in futures.items():
            try:
                print(future.result())
            except Exception as error:
                print(f"{name}: {error}")

