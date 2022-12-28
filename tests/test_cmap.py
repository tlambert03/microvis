import colorsys
from typing import Any

import numpy as np
import pytest

from cmap.color import RGBA8, parse, parse_hsl_string, parse_rgb_string


@pytest.mark.parametrize(
    "color",
    [
        "royalblue",
        "Royal Blue",
        (65, 105, 225),
        [65, 105, 225],
        np.array([65, 105, 225]),
        RGBA8(65, 105, 225),
        "rgb(65, 105, 225)",
        "rgb(65 105 225)",
        "rgb(65,105,225)",
        (0.2549019607843137, 0.4117647058823529, 0.8823529411764706, 1.0),
        (65 / 255, 105 / 255, 225 / 255),
        "#4169E1",
    ],
    ids=str,
)
def test_color_parse(color: Any) -> None:
    assert parse(color).to_8bit() == RGBA8(65, 105, 225)


@pytest.mark.parametrize(
    "color, expected",
    [
        ("rgb(2, 3, 4)", (2, 3, 4)),
        ("rgb(100%, 0%, 0%)", (255, 0, 0)),
        ("rgb(100%,none, 0%)", (255, 0, 0)),
        ("rgba(2, 3, 4, 0.5)", (2, 3, 4, 0.5)),
        ("rgba(2, 3, 4, 50%)", (2, 3, 4, 0.5)),
        ("rgb(-2, 3, 4)", (0, 3, 4)),
        ("rgb(100, 200, 300)", (100, 200, 255)),
        ("rgb(20, 10, 0, -10)", (20, 10, 0, 0)),
        ("rgb(100%, 200%, 300%)", (255, 255, 255)),
        ("rgb(100%, 200%, 300%)", (255, 255, 255)),
        ("rgb(128 none none / none)", (128, 0, 0, 0)),
    ],
)
def test_rgb_parse(color: str, expected: tuple) -> None:
    assert parse_rgb_string(color) == expected


@pytest.mark.parametrize(
    "color, expected",
    [
        ("hsl(120, 100%, 50%)", (0, 255, 0)),
        ("hsla(120, 100%, 50%, 0.25)", (0, 255, 0, 0.25)),
        ("hsla(120, 100%, 50% / none)", (0, 255, 0, 0)),
    ],
)
def test_hsl_parse(color: str, expected: tuple) -> None:

    h, s, ll, *a = parse_hsl_string(color)
    rgb = tuple(np.array(colorsys.hls_to_rgb(h / 360, ll, s)) * 255)
    assert rgb == expected[:3]
    if a:
        assert a[0] == expected[3]
