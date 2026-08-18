#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import build_unified_app as site  # noqa: E402


WIDTH = 1600
HEIGHT = 900
IVORY = "#FFFDF7"
INK = "#24312D"
MUTED = "#68776F"
LINE = "#D8D1C4"
SAGE = "#C7D3C2"
GREEN = "#5F7F72"
DEEP_GREEN = "#315E50"
BRASS = "#A98A4B"
TERRACOTTA = "#B76F57"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        (
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        )
        if bold
        else (
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        )
    )
    if bold:
        candidates += (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),)
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise RuntimeError("A supported Arial or DejaVu Sans font is required to generate infographics")


def money_short(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value / 1_000:.0f}K"


def load_rankings() -> tuple[list[dict], str]:
    destinations = [
        site.consolidate_destination(item) for item in site.load_json("destinations.json")
    ]
    payload = site.load_retirement_costs()
    return site.retirement_destination_rankings(destinations, payload), payload["as_of"]


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), IVORY)
    return image, ImageDraw.Draw(image)


def brand_header(draw: ImageDraw.ImageDraw, eyebrow: str, title: str, subtitle: str) -> None:
    draw.text((72, 56), "GLOBAL HOME ATLAS", fill=DEEP_GREEN, font=font(22, True))
    draw.text((72, 103), eyebrow.upper(), fill=BRASS, font=font(19, True))
    draw.text((72, 142), title, fill=INK, font=font(45, True))
    draw.text((72, 205), subtitle, fill=MUTED, font=font(23))
    draw.line((72, 250, 1528, 250), fill=LINE, width=2)


def footer(draw: ImageDraw.ImageDraw, as_of: str) -> None:
    draw.line((72, 831, 1528, 831), fill=LINE, width=2)
    draw.text(
        (72, 850),
        "Couple renting · retirement starts today · 30 years · 3.5% withdrawal · 12-month reserve · no outside income",
        fill=MUTED,
        font=font(17),
    )
    draw.text((1528, 850), f"Data reviewed {as_of}", fill=MUTED, font=font(17), anchor="ra")


def draw_required_capital(rankings: list[dict], as_of: str, output: Path) -> None:
    image, draw = canvas()
    brand_header(
        draw,
        "Lowest-cost 10 of 30 retirement destinations",
        "How much capital does a couple need?",
        "Top 10 shown; complete ranks 1–30 are available in the guide.",
    )
    max_value = max(item["metrics"]["required_capital"] for item in rankings)
    bar_x = 510
    bar_max = 880
    row_y = 285
    row_step = 52
    for rank, item in enumerate(rankings, start=1):
        destination = item["destination"]
        value = item["metrics"]["required_capital"]
        y = row_y + (rank - 1) * row_step
        draw.text((72, y + 8), f"{rank}", fill=BRASS, font=font(20, True))
        draw.text((118, y), destination["name"], fill=INK, font=font(19, True))
        draw.text((118, y + 24), destination.get("country") or "", fill=MUTED, font=font(14))
        draw.rounded_rectangle((bar_x, y + 6, bar_x + bar_max, y + 36), radius=10, fill="#EBE5DA")
        width = int(bar_max * value / max_value)
        fill = DEEP_GREEN if rank <= 2 else GREEN
        draw.rounded_rectangle((bar_x, y + 6, bar_x + width, y + 36), radius=10, fill=fill)
        draw.text((1430, y + 5), money_short(value), fill=INK, font=font(19, True))
    footer(draw, as_of)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def draw_capital_breakdown(rankings: list[dict], as_of: str, output: Path) -> None:
    image, draw = canvas()
    brand_header(
        draw,
        "Lowest-cost 10 of 30 retirement destinations",
        "Living-cost funding and property are separate decisions",
        "Top 10 shown; complete ranks 1–30 are available in the guide.",
    )
    columns = [72, 560, 800, 1045, 1285]
    headers = ["DESTINATION", "ANNUAL SPEND", "LIQUID PORTFOLIO", "12-MO RESERVE", "PROPERTY CAPITAL"]
    for x, label in zip(columns, headers):
        draw.text((x, 278), label, fill=BRASS, font=font(15, True))
    row_top = 318
    row_step = 45
    max_property = max(item["metrics"]["property_capital"] for item in rankings)
    for rank, item in enumerate(rankings, start=1):
        destination = item["destination"]
        metrics = item["metrics"]
        y = row_top + (rank - 1) * row_step
        if rank % 2 == 1:
            draw.rounded_rectangle((64, y - 7, 1536, y + 48), radius=8, fill="#F5F1E9")
        draw.text((72, y), f"#{rank}  {destination['name']}", fill=INK, font=font(18, True))
        draw.text((columns[1], y), money_short(metrics["annual_spending"]), fill=INK, font=font(19, True))
        draw.text((columns[2], y), money_short(metrics["liquid_portfolio"]), fill=DEEP_GREEN, font=font(19, True))
        draw.text((columns[3], y), money_short(metrics["emergency_reserve"]), fill=INK, font=font(19, True))
        property_width = int(190 * metrics["property_capital"] / max_property)
        draw.rounded_rectangle((columns[4], y + 27, columns[4] + 190, y + 36), radius=4, fill="#EBE5DA")
        draw.rounded_rectangle((columns[4], y + 27, columns[4] + property_width, y + 36), radius=4, fill=TERRACOTTA)
        draw.text((columns[4], y - 1), money_short(metrics["property_capital"]), fill=INK, font=font(19, True))
    draw.text(
        (72, 791),
        "Portfolio and reserve fund retirement spending. Property capital adds representative purchase price and acquisition costs.",
        fill=MUTED,
        font=font(18),
    )
    footer(draw, as_of)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def main() -> int:
    rankings, as_of = load_rankings()
    top_rankings = rankings[:10]
    assets = ROOT / "src" / "site_assets"
    draw_required_capital(
        top_rankings,
        as_of,
        assets / "retirement-destinations-required-capital.png",
    )
    draw_capital_breakdown(
        top_rankings,
        as_of,
        assets / "retirement-destinations-capital-breakdown.png",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
