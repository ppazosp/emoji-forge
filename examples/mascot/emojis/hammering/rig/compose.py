"""Pose the original cel cutouts using the front view on the hammer model sheet."""

from math import cos, radians, sin
from pathlib import Path

from PIL import Image

RIG = Path(__file__).resolve().parent
SHOT = RIG.parent
# Shoulder rotation, elbow bend, wrist rotation in degrees above the horizontal.
POSES = [
    (9, 7, 8),
    (20, 22, 9),
    (26, 30, 12),
    (14, 10, -8),
    (9, 8, -17),
    (12, 12, -11),
    (9, 7, 8),
    (9, 7, 8),
]


def advance(origin, length, angle):
    a = radians(angle)
    return origin[0] + length * cos(a), origin[1] - length * sin(a)


def layer(sprite, pivot, target, angle, scale=1):
    a = radians(angle)
    c, s = cos(a) / scale, sin(a) / scale
    x, y = target
    return sprite.transform(
        (512, 512),
        Image.Transform.AFFINE,
        (c, -s, pivot[0] - c * x + s * y, s, c, pivot[1] - s * x - c * y),
        Image.Resampling.BICUBIC,
    )


def main():
    stage = Image.open(RIG / "stage.png").convert("RGBA")
    sleeve = Image.open(RIG / "sleeve.png").convert("RGBA")
    mitten = Image.open(RIG / "mitten.png").convert("RGBA")
    hammer = (
        Image.open(SHOT.parents[1] / "images/assets/hammer/model.png")
        .convert("RGBA")
        .crop((120, 70, 340, 391))
    )
    for i, (shoulder, bend, wrist) in enumerate(POSES, 1):
        elbow = advance((283, 289), 40, shoulder)
        grip = advance(elbow, 29, shoulder + bend)
        tool = layer(hammer, (110, 271), grip, shoulder + bend + wrist - 90, 0.46)
        cel = layer(sleeve, (19, 25), (283, 289), shoulder)
        cel.alpha_composite(stage)
        cel.alpha_composite(tool)
        cel.alpha_composite(layer(mitten, (40, 29), grip, shoulder + bend + wrist))
        cel.save(SHOT / f"cels/{i:03}-file.png")
        tool.getchannel("A").save(RIG / f"prop-{i:03}.png")


if __name__ == "__main__":
    main()
