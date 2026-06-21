# Data Schema Recommendation

## destinations.json

Each destination object should follow this structure:

```json
{
  "id": "fukuoka-itoshima",
  "name": "Fukuoka / Itoshima",
  "country": "Japan",
  "region": "Asia-Pacific",
  "category": "Water",
  "bucket": "Priority shortlist",
  "rank": 1,
  "overall_score": 4.28,
  "usd_per_m2": 2620,
  "price_basis": "Built residential benchmark...",
  "price_confidence": "Medium-high",
  "net_yield_estimate": "3–4.8% est. net",
  "gross_yield_reference": "Japan average gross yield 4.55%...",
  "str_revenue": "AirROI 2026: ~$24,963 average annual Airbnb revenue",
  "adr_occupancy": "$152 / 51.0%",
  "yield_confidence": "Medium-high for STR metrics; medium for net yield",
  "ownership_notes": "Open Japan freehold ownership...",
  "red_flags": "Less scarce/trophy than resort markets...",
  "profit_driver": "Excellent airport access...",
  "panel_summary": "The panel would treat this as...",
  "pros": ["..."],
  "cons": ["..."],
  "panel_verdict": "Keep as a top-tier shortlist candidate...",
  "scores": {
    "scenery": {"score": 3.9, "weight": 0.07},
    "airport_access": {"score": 5.0, "weight": 0.07},
    "business_hub_access": {"score": 4.7, "weight": 0.05},
    "year_round_activity": {"score": 4.2, "weight": 0.07},
    "ownership_clarity": {"score": 5.0, "weight": 0.11},
    "str_regulatory_safety": {"score": 3.0, "weight": 0.07},
    "rental_profit_potential": {"score": 3.8, "weight": 0.12},
    "capital_upside": {"score": 4.0, "weight": 0.07},
    "retirement_suitability": {"score": 4.6, "weight": 0.07},
    "exit_liquidity": {"score": 4.1, "weight": 0.06},
    "chinese_foreigner_friendliness": {"score": 4.6, "weight": 0.06},
    "food_quality": {"score": 4.8, "weight": 0.04},
    "standard_of_living": {"score": 4.6, "weight": 0.03},
    "affordability": {"score": 4.2, "weight": 0.11}
  }
}
```

## listings.json

Each listing object should follow this structure:

```json
{
  "destination_id": "fukuoka-itoshima",
  "destination_name": "Fukuoka / Itoshima",
  "property_type": "House / villa",
  "listing_name": "Example listing name",
  "usd_price": 850000,
  "local_currency": "JPY",
  "local_price": 137080000,
  "size_m2": 180,
  "usd_per_m2": 4722,
  "source_name": "RealEstate.co.jp",
  "source_url": "https://...",
  "note": "Short read on what this example represents",
  "confidence": "Medium",
  "captured_date": "2026-06-21"
}
```

## fx_rates.json

```json
{
  "as_of": "2026-06-21",
  "rates_to_usd": {
    "JPY": 0.006199,
    "EUR": 1.14784,
    "CAD": 0.70609,
    "NZD": 0.57370,
    "CHF": 1.24288,
    "THB": 0.0303905,
    "IDR": 0.000056243,
    "VND": 0.0000380084,
    "USD": 1.0
  },
  "source_note": "Rates retrieved during dashboard build conversation; re-check before investment decisions."
}
```

## sources.csv

Suggested columns:

```text
destination,topic,source_name,url,date_accessed,metric_supported,confidence,notes
```

