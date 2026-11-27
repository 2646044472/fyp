from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / "public"
root.mkdir(exist_ok=True)
for size in (192, 512):
    image = Image.new("RGB", (512, 512), "#123426")
    draw = ImageDraw.Draw(image)
    color = "#b9efd4"
    outline = [(213,350),(176,313),(142,266),(151,249),(172,249),(196,273),
               (196,176),(212,160),(228,176),(228,229),(228,148),(245,132),
               (262,148),(262,225),(262,159),(280,144),(295,160),(295,227),
               (295,182),(312,170),(328,186),(328,276),(313,326),(283,350),(213,350)]
    draw.line(outline, fill=color, width=12, joint="curve")
    for x, y, dx, dy in [(112,112,1,1),(400,112,-1,1),(112,400,1,-1),(400,400,-1,-1)]:
        draw.line([(x+42*dx,y),(x,y),(x,y+42*dy)],fill=color,width=8,joint="curve")
    image.resize((size,size), Image.Resampling.LANCZOS).save(root / f"palm-{size}.png")

