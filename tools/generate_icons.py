"""Genera los iconos PWA y favicon.ico para el Simulador de Charlieplexing."""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(BASE, "icons")
os.makedirs(ICONS, exist_ok=True)

# Colores de la app
GRAD_TOP = (26, 42, 108)     # #1a2a6c
GRAD_BOTTOM = (44, 62, 80)   # #2c3e50
LED_COLORS = [
    (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 128, 255),
    (255, 165, 0), (128, 0, 128), (255, 0, 255), (0, 255, 255),
]


def make_background(size, radius_ratio=0.0):
    """Fondo con degradado diagonal como el body de la app."""
    img = Image.new("RGBA", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size - 2)
            r = int(GRAD_TOP[0] + (GRAD_BOTTOM[0] - GRAD_TOP[0]) * t)
            g = int(GRAD_TOP[1] + (GRAD_BOTTOM[1] - GRAD_TOP[1]) * t)
            b = int(GRAD_TOP[2] + (GRAD_BOTTOM[2] - GRAD_TOP[2]) * t)
            px[x, y] = (r, g, b, 255)
    if radius_ratio > 0:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=255
        )
        img.putalpha(mask)
    return img


def draw_leds(img, size, content_scale=1.0):
    """Dibuja una matriz de ledes estilo charlieplexing, con algunos encendidos."""
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    dg = ImageDraw.Draw(glow)

    margin = size * 0.18 * content_scale
    grid = 3  # matriz 3x3 de ledes
    span = size - 2 * margin
    step = span / (grid - 1) if grid > 1 else span
    led_r = size * 0.085 * content_scale

    on_positions = {(0, 1), (1, 0), (1, 2), (2, 1), (1, 1)}

    for row in range(grid):
        for col in range(grid):
            cx = margin + col * step
            cy = margin + row * step
            color = LED_COLORS[(row * grid + col) % len(LED_COLORS)]
            if (row, col) in on_positions:
                # Halo del led encendido
                halo_r = led_r * 2.2
                for i in range(3):
                    alpha = 60 - i * 15
                    hr = halo_r * (1 - i * 0.22)
                    dg.ellipse(
                        [cx - hr, cy - hr, cx + hr, cy + hr],
                        fill=color + (alpha,),
                    )
                d.ellipse(
                    [cx - led_r, cy - led_r, cx + led_r, cy + led_r],
                    fill=color + (255,),
                )
                # Brillo central
                wr = led_r * 0.45
                d.ellipse(
                    [cx - wr * 0.4, cy - wr * 0.4, cx + wr * 0.9, cy + wr * 0.9],
                    fill=(255, 255, 255, 200),
                )
            else:
                # Led apagado (versión oscura del color)
                dark = tuple(int(c * 0.35) for c in color)
                d.ellipse(
                    [cx - led_r, cy - led_r, cx + led_r, cy + led_r],
                    fill=dark + (255,),
                    outline=(90, 100, 110, 255),
                    width=max(1, size // 128),
                )

    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.03))
    img.alpha_composite(glow)
    img.alpha_composite(overlay)
    return img


def generate(size, path, rounded=False, maskable=False):
    if maskable:
        # Fondo completo sin esquinas; contenido dentro de la zona segura (~80%)
        img = make_background(size)
        img = draw_leds(img, size, content_scale=0.82)
    elif rounded:
        img = make_background(size, radius_ratio=0.22)
        img = draw_leds(img, size)
    else:
        img = make_background(size)
        img = draw_leds(img, size)
    img.save(path, "PNG")
    print("OK", path)


generate(192, os.path.join(ICONS, "icon-192.png"), rounded=True)
generate(512, os.path.join(ICONS, "icon-512.png"), rounded=True)
generate(192, os.path.join(ICONS, "icon-maskable-192.png"), maskable=True)
generate(512, os.path.join(ICONS, "icon-maskable-512.png"), maskable=True)
generate(180, os.path.join(ICONS, "apple-touch-icon.png"))

# favicon.ico multiresolución (16, 32, 48)
fav_sizes = [16, 32, 48]
fav_base = make_background(256, radius_ratio=0.22)
fav_base = draw_leds(fav_base, 256)
fav_imgs = [fav_base.resize((s, s), Image.LANCZOS) for s in fav_sizes]
fav_imgs[0].save(
    os.path.join(BASE, "favicon.ico"),
    format="ICO",
    sizes=[(s, s) for s in fav_sizes],
)
print("OK", os.path.join(BASE, "favicon.ico"))
