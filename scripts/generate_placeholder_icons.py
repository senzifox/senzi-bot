from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 400
ASSETS_DIR = Path(__file__).parent.parent / "bot" / "assets"


def play_icon() -> None:
    image = Image.new("RGB", (SIZE, SIZE), (18, 18, 20))
    draw = ImageDraw.Draw(image)
    pad = 24
    draw.rounded_rectangle([pad, pad, SIZE - pad, SIZE - pad], radius=48, fill=(224, 32, 32))

    w, h = 130, 150
    cx, cy = SIZE // 2, SIZE // 2
    draw.polygon(
        [(cx - w // 2 + 10, cy - h // 2), (cx - w // 2 + 10, cy + h // 2), (cx + w // 2, cy)],
        fill=(250, 250, 250),
    )
    image.save(ASSETS_DIR / "placeholder.png")


def currency_icon() -> None:
    image = Image.new("RGB", (SIZE, SIZE), (18, 18, 20))
    draw = ImageDraw.Draw(image)
    pad = 24
    draw.rounded_rectangle([pad, pad, SIZE - pad, SIZE - pad], radius=48, fill=(30, 140, 110))

    cx, cy = SIZE // 2, SIZE // 2
    r = 90
    width = 22

    draw.arc(
        [cx - r, cy - r - 30, cx + r, cy + r - 30],
        start=200,
        end=520,
        fill=(250, 250, 250),
        width=width,
    )
    draw.polygon(
        [(cx + r - 10, cy - 30 - 28), (cx + r + 38, cy - 30), (cx + r - 10, cy - 30 + 28)],
        fill=(250, 250, 250),
    )

    draw.arc(
        [cx - r, cy - r + 30, cx + r, cy + r + 30],
        start=20,
        end=340,
        fill=(250, 250, 250),
        width=width,
    )
    draw.polygon(
        [(cx - r + 10, cy + 30 - 28), (cx - r - 38, cy + 30), (cx - r + 10, cy + 30 + 28)],
        fill=(250, 250, 250),
    )

    image.save(ASSETS_DIR / "currency_placeholder.png")


if __name__ == "__main__":
    play_icon()
    currency_icon()
    print(f"Saved to {ASSETS_DIR}")
