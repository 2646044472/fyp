from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "results" / "palm_roi_fastcc" / "palm_roi_128_gray"
OUTPUT = ROOT / "results" / "cr_compcode_10" / "palm_roi_10_contact_sheet.png"

files = sorted(INPUT.glob("*.png"), key=lambda path: int(path.stem))[:10]
cell = 168
margin = 12
columns = 5
rows = (len(files) + columns - 1) // columns
sheet = Image.new("RGB", (columns * cell, rows * cell), "#202020")
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(files):
    image = Image.open(path).convert("L").resize((128, 128), Image.Resampling.NEAREST)
    x = (index % columns) * cell + (cell - 128) // 2
    y = (index // columns) * cell + 24
    sheet.paste(Image.merge("RGB", (image, image, image)), (x, y))
    draw.text((x, 6 + (index // columns) * cell), path.stem, fill="white")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUTPUT)
print(OUTPUT)
