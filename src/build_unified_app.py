from __future__ import annotations

import json
import os
import re
import shutil
import sys
import unicodedata
from copy import deepcopy
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlparse

try:
    from src.seo_content_overrides import apply_content_override, load_content_overrides
    from src.retirement_destination_finder_page import build_retirement_destination_finder_html
    from src.premium_destination_dossiers import (
        PremiumDossierSpec,
        get_premium_dossier,
        validate_premium_dossier,
    )
except ModuleNotFoundError:  # Direct execution: python3 src/build_unified_app.py
    from seo_content_overrides import apply_content_override, load_content_overrides
    from retirement_destination_finder_page import build_retirement_destination_finder_html
    from premium_destination_dossiers import (
        PremiumDossierSpec,
        get_premium_dossier,
        validate_premium_dossier,
    )

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.seo_content_generator import PageContextParser, content_hash

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"
SEO_AUTO_INTERNAL_LINKS_PATH = DATA / "seo_auto_internal_links.json"
SOURCE_ASSETS = ROOT / "src" / "site_assets"
PUBLIC_ASSETS = ARTIFACTS / "assets"
SITE_NAME = "Global Home Atlas"
SITE_DOMAIN = "globalhomeatlas.com"
SITE_URL = f"https://{SITE_DOMAIN}/"
SITE_DESCRIPTION = (
    "Compare global home and property investment destinations with decision scores, "
    "ownership clarity, lifestyle fit, yields, and representative market evidence."
)
GUIDE_HUB_SLUG = "guides"
GUIDE_HUB_TITLE = "Global Property Buying Guides | Global Home Atlas"
GUIDE_HUB_DESCRIPTION = (
    "Browse Global Home Atlas buying guides for overseas property, retirement homes, "
    "second homes, foreign ownership, investment risk, and destination shortlists."
)
SHORTLIST_REVIEW_SLUG = "shortlist-review"
SHORTLIST_REVIEW_TITLE = "Shortlist Review | Global Home Atlas"
SHORTLIST_REVIEW_DESCRIPTION = (
    "Request a Global Home Atlas shortlist review before speaking to agents, with a "
    "research-led route across buyer intent, budget, citizenship, risk, and holding period."
)
FIND_YOUR_FIT_SLUG = "find-your-fit"
FIND_YOUR_FIT_TITLE = "Find Your Best-Fit Property Destination | Global Home Atlas"
FIND_YOUR_FIT_DESCRIPTION = (
    "Answer five practical questions and compare property destinations by buying goal, "
    "budget, preferred setting, intended use, and tolerance for complexity."
)
REPORT_LIBRARY_SLUG = "reports"
REPORT_LIBRARY_TITLE = "Premium Property Research Reports | Global Home Atlas"
REPORT_LIBRARY_DESCRIPTION = (
    "Browse premium Global Home Atlas research brief formats for retirement markets, "
    "second-home shortlists, overseas property risk, and polished buyer memos."
)
RETIREMENT_CALCULATOR_SLUG = "retirement-abroad-calculator"
RETIREMENT_CALCULATOR_TITLE = "Retirement Abroad Calculator: How Much Do You Need? | Global Home Atlas"
RETIREMENT_CALCULATOR_H1 = "Retirement Abroad Calculator"
RETIREMENT_CALCULATOR_DESCRIPTION = (
    "Estimate how much you need to retire abroad, including destination living costs, "
    "inflation, pension and passive income, property costs, and required portfolio capital."
)
RETIREMENT_FINDER_SLUG = "retirement-destination-finder"
RETIREMENT_FINDER_TITLE = "Retirement Destination Finder | Global Home Atlas"
RETIREMENT_FINDER_DESCRIPTION = (
    "Project your retirement savings and monthly investing, then compare destinations "
    "you may be able to afford when renting or buying abroad."
)
RETIREMENT_DESTINATIONS_SLUG = "retirement-destinations-ranked-by-cost"
RETIREMENT_DESTINATIONS_TITLE = "Retirement Destinations Ranked by Cost (2026) | Global Home Atlas"
RETIREMENT_DESTINATIONS_H1 = "30 Retirement Destinations Ranked by How Much You Need"
RETIREMENT_DESTINATIONS_DESCRIPTION = (
    "Compare all 30 Global Home Atlas retirement destinations by required capital, "
    "annual spending, reserves, and optional property costs using one methodology."
)
RETIREMENT_COSTS_PATH = DATA / "retirement_costs.json"
MORTGAGE_PROFILES_PATH = DATA / "mortgage_profiles.json"
RETIREMENT_ENGINE_PATH = ROOT / "src" / "retirement_calculator.js"
RETIREMENT_UI_PATH = ROOT / "src" / "retirement_calculator_ui.js"
PROPERTY_FINANCE_PATH = ROOT / "src" / "property_finance.js"
RETIREMENT_FINDER_ENGINE_PATH = ROOT / "src" / "retirement_destination_finder.js"
RETIREMENT_FINDER_UI_PATH = ROOT / "src" / "retirement_destination_finder_ui.js"
RETIREMENT_RANKING_TABLE_PATH = ROOT / "src" / "retirement_ranking_table.js"
CONTINENT_BY_COUNTRY = {
    "Austria": "europe",
    "Canada": "north-america",
    "Croatia": "europe",
    "France": "europe",
    "Greece": "europe",
    "Indonesia": "asia",
    "Italy": "europe",
    "Japan": "asia",
    "New Zealand": "oceania",
    "Portugal": "europe",
    "Spain": "europe",
    "Switzerland": "europe",
    "Thailand": "asia",
    "United States": "north-america",
    "Vietnam": "asia",
}
RETIREMENT_DESTINATIONS_PAGE = {
    "slug": RETIREMENT_DESTINATIONS_SLUG,
    "title": RETIREMENT_DESTINATIONS_TITLE,
    "description": RETIREMENT_DESTINATIONS_DESCRIPTION,
    "h1": RETIREMENT_DESTINATIONS_H1,
    "keyword": "retirement destinations ranked by cost",
    "theme": "retirement cost comparison",
    "intent": "retirees comparing how location changes annual spending and required retirement capital",
    "destination_ids": [
        "fukuoka-itoshima",
        "hakone-izu",
        "crete",
        "valencia",
        "algarve-cascais",
        "malaga-costa-del-sol",
        "madeira",
        "lake-como",
    ],
}
COUNTRY_HUBS = [
    {
        "slug": "spain-property",
        "country": "Spain",
        "title": "Spain Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare Spain property destinations for foreign buyers, including Valencia, Malaga, Costa Brava, and Mallorca across lifestyle, ownership, rentals, and retirement fit.",
        "h1": "Spain Property Guide for Foreign Buyers",
        "thesis": "Spain is one of the deepest lifestyle-property markets in the Atlas because it combines city infrastructure, Mediterranean living, healthcare access, and several resale buyer pools. The discipline is entry price and local rental regulation.",
        "destination_ids": ["valencia", "malaga-costa-del-sol", "costa-brava-girona", "mallorca"],
        "guide_slugs": ["spain-retirement-property-foreign-buyers", "portugal-vs-spain-retirement-property", "best-places-to-buy-property-in-europe", "buying-property-abroad-for-retirement"],
    },
    {
        "slug": "portugal-property",
        "country": "Portugal",
        "title": "Portugal Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare Portugal property markets for foreign buyers, including Algarve, Cascais, and Madeira across retirement fit, ownership clarity, value, and rental caveats.",
        "h1": "Portugal Property Guide for Foreign Buyers",
        "thesis": "Portugal remains a core benchmark for retirement and second-home planning. It screens well for foreigner practicality and lifestyle, but buyer returns depend heavily on micro-location, licensing, taxes, and entry-price discipline.",
        "destination_ids": ["algarve-cascais", "madeira"],
        "guide_slugs": ["portugal-vs-spain-retirement-property", "greece-vs-portugal-retirement-property", "best-places-to-buy-property-abroad-for-retirement", "best-places-to-buy-a-second-home-abroad"],
    },
    {
        "slug": "japan-property",
        "country": "Japan",
        "title": "Japan Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare Japan property destinations for foreign buyers, including Fukuoka, Itoshima, Hakone, Izu, Hakuba, and Niseko across ownership clarity, lifestyle, and yield realism.",
        "h1": "Japan Property Guide for Foreign Buyers",
        "thesis": "Japan is unusually strong on ownership clarity, safety, food, infrastructure, and healthcare. The main question is not whether foreigners can buy; it is whether the chosen asset and location match the buyer's visa, income, and long-term use case.",
        "destination_ids": ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"],
        "guide_slugs": ["japan-retirement-property-foreign-buyers", "best-countries-to-buy-property-as-a-foreigner", "buying-property-abroad-for-retirement", "best-places-to-buy-vacation-home-abroad"],
    },
    {
        "slug": "united-states-property",
        "country": "United States",
        "title": "United States Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare United States second-home and resort property markets, including Aspen, Park City, Lake Tahoe, and Jackson Hole across ownership clarity, price discipline, rental rules, and climate risk.",
        "h1": "United States Property Guide for Foreign Buyers",
        "thesis": "The United States offers clean title and deep luxury-market liquidity, but resort property underwriting is rarely simple. Buyers need to separate trophy scarcity from income potential, then model local rental rules, insurance, taxes, and carrying costs market by market.",
        "destination_ids": ["park-city-deer-valley", "lake-tahoe", "jackson-hole", "aspen-snowmass"],
        "guide_slugs": ["best-places-to-buy-a-second-home-abroad", "foreign-property-investment-risks", "overseas-property-investment", "where-can-foreigners-buy-property"],
    },
    {
        "slug": "canada-property",
        "country": "Canada",
        "title": "Canada Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare Canada lifestyle property markets for foreign buyers, including Whistler and Vancouver Island across mountain, water, retirement, rental, tax, and policy considerations.",
        "h1": "Canada Property Guide for Foreign Buyers",
        "thesis": "Canada adds a useful North American lifestyle benchmark: clear institutions, strong livability, and real mountain/water appeal. The caution is policy. Foreign-buyer rules, vacancy and speculation taxes, local rental limits, and high carrying costs can change the practical answer.",
        "destination_ids": ["vancouver-island-victoria", "whistler"],
        "guide_slugs": ["best-places-to-buy-property-abroad-for-retirement", "best-places-to-buy-a-second-home-abroad", "foreign-property-investment-risks", "where-can-foreigners-buy-property"],
    },
    {
        "slug": "thailand-property",
        "country": "Thailand",
        "title": "Thailand Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Assess Thailand property for foreign buyers, including Phuket and Koh Samui ownership structures, villa risks, rental appeal, and alternatives.",
        "h1": "Thailand Property Guide for Foreign Buyers",
        "thesis": "Thailand can be compelling for lifestyle, rental demand, and regional access, but the legal structure matters more than the brochure. Villa buyers need to understand land, leasehold, company, and condominium rules before underwriting income.",
        "destination_ids": ["phuket-koh-samui"],
        "guide_slugs": ["thailand-villa-ownership-foreigners", "foreign-property-investment-risks", "where-can-foreigners-buy-property", "overseas-property-investment"],
    },
    {
        "slug": "greece-property",
        "country": "Greece",
        "title": "Greece Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Assess Greece property for foreign buyers through Crete, island-seasonality, retirement practicality, value, ownership clarity, and resale depth.",
        "h1": "Greece Property Guide for Foreign Buyers",
        "thesis": "Greece can offer lifestyle value and Mediterranean appeal, especially where access and services are strong. The risk is assuming island romance automatically creates year-round livability, healthcare practicality, or deep resale liquidity.",
        "destination_ids": ["crete"],
        "guide_slugs": ["greece-vs-portugal-retirement-property", "best-places-to-buy-property-abroad-for-retirement", "best-places-to-buy-property-in-europe", "buy-property-abroad"],
    },
    {
        "slug": "croatia-property",
        "country": "Croatia",
        "title": "Croatia Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Assess Croatia property for foreign buyers through Istria and Dalmatia, including residence, ownership eligibility, title, tourist-rental rules, hazards, access, and resale depth.",
        "h1": "Croatia Property Guide for Foreign Buyers",
        "thesis": "Croatia can offer compelling Adriatic lifestyle value, but residence, ownership eligibility, title reconciliation, lawful construction, tourist-rental consent, seasonal access, and hazard exposure must be verified separately. The strongest retirement cases begin with a year-round operating base rather than a summer view.",
        "destination_ids": ["croatia-istria-dalmatia"],
        "guide_slugs": ["buying-property-abroad-for-retirement", "best-places-to-buy-property-in-europe", "where-can-foreigners-buy-property", "foreign-property-investment-risks"],
    },
    {
        "slug": "italy-property",
        "country": "Italy",
        "title": "Italy Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare Italy property destinations for foreign buyers, including Lake Como and the Dolomites across prestige, lifestyle, value discipline, and exit liquidity.",
        "h1": "Italy Property Guide for Foreign Buyers",
        "thesis": "Italy is strongest when the property thesis is lifestyle, prestige, and capital preservation rather than yield maximization. Buyers should separate globally liquid trophy markets from beautiful but thin local resale markets.",
        "destination_ids": ["lake-como", "dolomites-south-tyrol"],
        "guide_slugs": ["best-places-to-buy-property-in-europe", "best-places-to-buy-vacation-home-abroad", "foreign-property-investment-risks", "buy-property-abroad"],
    },
    {
        "slug": "switzerland-property",
        "country": "Switzerland",
        "title": "Switzerland Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare Switzerland property options for foreign buyers, including Andermatt, Lake Lugano, Valais, and Vaud across ownership limits, liquidity, lifestyle, and entry price.",
        "h1": "Switzerland Property Guide for Foreign Buyers",
        "thesis": "Switzerland is a capital-preservation and lifestyle market with high entry costs and meaningful foreign-buyer constraints. The strongest cases depend on legal access, liquidity, and whether the buyer accepts lower yield for resilience.",
        "destination_ids": ["andermatt", "ticino-lake-lugano", "swiss-valais-vaud-alps"],
        "guide_slugs": ["where-can-foreigners-buy-property", "foreign-property-investment-risks", "best-places-to-buy-vacation-home-abroad", "overseas-property-investment"],
    },
]
GA4_MEASUREMENT_ID = os.environ.get("GA4_MEASUREMENT_ID", "").strip()
BING_SITE_VERIFICATION = os.environ.get("BING_SITE_VERIFICATION", "").strip()
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "hello@globalhomeatlas.com").strip()
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "").strip() or "37c568eb0fbc24832815d94b646237ca"

DIMENSIONS = [
    {
        "key": "lifestyle_magnetism",
        "label": "Lifestyle magnetism",
        "weight": 0.10,
        "sources": ["scenery", "year_round_activity", "food_quality"],
        "evidence": "Natural setting, food culture, and repeatable year-round reasons to be there.",
    },
    {
        "key": "global_access",
        "label": "Global access",
        "weight": 0.10,
        "sources": ["airport_access", "business_hub_access"],
        "evidence": "Airport quality, regional connectivity, and access to global business centres.",
    },
    {
        "key": "ownership_clarity",
        "label": "Ownership clarity",
        "weight": 0.12,
        "sources": ["ownership_clarity"],
        "evidence": "Foreign-buyer pathway, title transparency, transaction practicality, and legal friction.",
    },
    {
        "key": "regulatory_safety",
        "label": "Regulatory safety",
        "weight": 0.08,
        "sources": ["str_regulatory_safety"],
        "evidence": "Short-term-rental and local operating rules that can affect income durability.",
    },
    {
        "key": "rental_profit",
        "label": "Rental profit",
        "weight": 0.13,
        "sources": ["rental_profit_potential"],
        "evidence": "Net-yield potential after operating friction, seasonality, and realistic asset selection.",
    },
    {
        "key": "capital_upside",
        "label": "Capital upside",
        "weight": 0.09,
        "sources": ["capital_upside"],
        "evidence": "Long-term appreciation drivers, scarcity, infrastructure, and demand migration.",
    },
    {
        "key": "retirement_fit",
        "label": "Retirement fit",
        "weight": 0.11,
        "sources": ["retirement_suitability", "standard_of_living"],
        "evidence": "Healthcare, convenience, safety, comfort, and the ability to live there for months.",
    },
    {
        "key": "exit_liquidity",
        "label": "Exit liquidity",
        "weight": 0.09,
        "sources": ["exit_liquidity"],
        "evidence": "Depth and quality of the resale buyer pool when the thesis changes.",
    },
    {
        "key": "foreigner_fit",
        "label": "Foreigner fit",
        "weight": 0.07,
        "sources": ["chinese_foreigner_friendliness"],
        "evidence": "Ease for global and Chinese-speaking buyers across language, services, and local acceptance.",
    },
    {
        "key": "value_entry",
        "label": "Value entry",
        "weight": 0.11,
        "sources": ["affordability"],
        "evidence": "Price discipline, USD/m2 reasonableness, and margin of safety at acquisition.",
    },
]

SEO_PAGES = [
    {
        "slug": "best-places-to-buy-property-abroad-for-retirement",
        "title": "Best Places to Buy Property Abroad for Retirement | Global Home Atlas",
        "description": "Compare the best places to buy property abroad for retirement using ownership clarity, healthcare, lifestyle, value, rental resilience, and exit liquidity.",
        "h1": "Best Places to Buy Property Abroad for Retirement",
        "keyword": "best places to buy property abroad for retirement",
        "theme": "retirement planning",
        "intent": "buyers who want one property to support retirement optionality, seasonal living, and defensible resale value",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "madeira", "crete", "lake-como", "hakone-izu", "malaga-costa-del-sol"],
        "faqs": [
            ("What matters most when buying abroad for retirement?", "Ownership clarity, healthcare access, daily convenience, tax and visa planning, and resale liquidity should be weighted before lifestyle appeal."),
            ("Should retirement buyers prioritize rental yield?", "Yield helps offset ownership costs, but retirement buyers should avoid assets where income depends on fragile short-term-rental rules."),
            ("Is a lower purchase price always safer?", "No. A cheap property can be expensive if title, maintenance, healthcare access, or resale demand are weak."),
        ],
    },
    {
        "slug": "best-places-to-buy-vacation-home-abroad",
        "title": "Best Places to Buy a Vacation Home in the World",
        "description": "Compare the best places to buy a vacation home in the world by lifestyle use, ownership clarity, rental-rule risk, value discipline, and resale depth.",
        "h1": "Best Places to Buy a Vacation Home in the World",
        "keyword": "best country to buy a vacation home",
        "theme": "vacation-home acquisition",
        "intent": "buyers who want personal use, repeatable travel demand, and a realistic path to offset carrying costs",
        "destination_ids": ["fukuoka-itoshima", "algarve-cascais", "madeira", "costa-brava-girona", "lake-como", "crete", "phuket-koh-samui", "mallorca", "andermatt", "annecy"],
        "faqs": [
            ("What are the best places to buy a vacation home in the world?", "The strongest vacation-home locations combine repeat owner use, reliable access, clear ownership, manageable rental rules, defensible entry price, and resale demand beyond one buyer group."),
            ("What makes a strong overseas vacation-home market?", "Look for repeat visitation, airport access, year-round demand, clear local rental rules, and a resale market beyond foreign buyers."),
            ("Are island homes better investments?", "Not automatically. Islands can have scarcity and appeal, but also seasonality, maintenance friction, and regulatory limits."),
        ],
    },
    {
        "slug": "best-countries-for-expats-to-buy-property",
        "title": "Best Countries for Expats to Buy Property | Global Home Atlas",
        "description": "Compare the best countries for expats to buy property by foreign-buyer practicality, ownership rules, lifestyle quality, value, and resale depth.",
        "h1": "Best Countries for Expats to Buy Property",
        "keyword": "best countries for expats to buy property",
        "theme": "expat ownership",
        "intent": "globally mobile buyers who need clear foreign ownership, usable infrastructure, and a livable long-term base",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "malaga-costa-del-sol", "madeira", "crete", "da-nang-hoi-an", "phuket-koh-samui"],
        "faqs": [
            ("Which countries are easiest for expats to buy in?", "Ease depends on title structure, local counsel quality, banking, taxes, and residency rules, not only whether foreign ownership is technically allowed."),
            ("Should expats buy before moving?", "Usually only after validating healthcare, transport, language friction, taxes, and the specific neighborhood through extended stays."),
            ("How should foreign buyers manage legal risk?", "Use independent local counsel, verify title and permits, model taxes, and avoid structures you cannot explain clearly."),
        ],
    },
    {
        "slug": "best-countries-to-buy-property-as-a-foreigner",
        "title": "Best Countries to Buy Property as a Foreigner | Global Home Atlas",
        "description": "Compare where foreigners can buy property with ownership clarity, title practicality, lifestyle quality, value discipline, and resale depth.",
        "h1": "Best Countries to Buy Property as a Foreigner",
        "keyword": "best countries to buy property as a foreigner",
        "theme": "foreign-buyer access",
        "intent": "foreign buyers comparing legal access, title clarity, transaction practicality, lifestyle quality, and resale depth before choosing markets for local diligence",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "malaga-costa-del-sol", "madeira", "crete", "lake-como", "costa-brava-girona", "hakone-izu", "phuket-koh-samui"],
        "faqs": [
            ("What are the best countries to buy property as a foreigner?", "The best options are markets where foreign buyers can understand the title path, hire independent local counsel, fund the purchase cleanly, use the property realistically, and resell into a broad buyer pool."),
            ("What legal risks should foreign buyers check first?", "Start with title structure, transfer process, taxes, permits, foreign ownership restrictions, financing access, rental rules, and whether the structure is simple enough to explain without relying on informal assurances."),
            ("Is freehold ownership always better than leasehold?", "Freehold can be cleaner, but the safer choice depends on enforceability, local rules, asset quality, liquidity, taxes, and whether the buyer understands the full structure before committing capital."),
        ],
    },
    {
        "slug": "buy-property-abroad",
        "title": "Buy Property Abroad: Global Buyer Checklist | Global Home Atlas",
        "description": "Use a structured framework to buy property abroad: shortlist countries, compare ownership risk, underwrite income, and plan exit liquidity.",
        "h1": "Buy Property Abroad",
        "keyword": "buy property abroad",
        "theme": "global purchase process",
        "intent": "buyers moving from inspiration to a disciplined international property shortlist",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "malaga-costa-del-sol", "lake-como", "madeira", "costa-brava-girona", "crete"],
        "faqs": [
            ("What is the first step to buy property abroad?", "Define the job of the property: retirement base, vacation home, income asset, capital preservation, or a blend."),
            ("How many destinations should I compare?", "Start with five to eight destinations, then reduce to two or three after legal, tax, visa, and neighborhood checks."),
            ("What should I verify before an offer?", "Verify title, permits, taxes, financing, insurance, building condition, rental rules, and resale comparables."),
        ],
    },
    {
        "slug": "buying-property-abroad-for-retirement",
        "title": "Buying Property Abroad for Retirement | Global Home Atlas",
        "description": "A retirement-focused framework for buying property abroad, comparing ownership clarity, healthcare practicality, lifestyle fit, value, and resale flexibility.",
        "h1": "Buying Property Abroad for Retirement",
        "keyword": "buying property abroad for retirement",
        "theme": "retirement buyer framework",
        "intent": "retirement-oriented buyers comparing healthcare, daily convenience, ownership practicality, and future resale flexibility before choosing a long-stay market",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "madeira", "crete", "hakone-izu", "lake-como", "malaga-costa-del-sol"],
        "faqs": [
            ("What should retirees verify before buying abroad?", "Retirement buyers should verify healthcare access, visa and tax planning needs, daily convenience, title clarity, insurance, building condition, and future resale demand before focusing on lifestyle appeal."),
            ("Should retirement buyers prioritize rental income?", "Rental income can offset carrying costs, but a retirement property should not depend on fragile short-term-rental assumptions or a structure the buyer cannot comfortably manage."),
            ("How long should I test a market before buying?", "A serious buyer should spend enough time locally to experience daily errands, healthcare access, transport, weather, language friction, and non-peak-season livability before committing capital."),
        ],
    },
    {
        "slug": "best-places-to-buy-a-second-home-abroad",
        "title": "Best Places to Buy a Second Home Abroad | Global Home Atlas",
        "description": "Compare the best places to buy a second home abroad for family use, vacation-home optionality, rental offset, ownership clarity, and resale liquidity.",
        "h1": "Best Places to Buy a Second Home Abroad",
        "keyword": "best places to buy a second home abroad",
        "theme": "second-home shortlist",
        "intent": "affluent buyers comparing vacation use, family use, rental offset, airport access, and long-term asset resilience",
        "destination_ids": ["fukuoka-itoshima", "algarve-cascais", "madeira", "costa-brava-girona", "lake-como", "mallorca", "phuket-koh-samui", "hakuba", "queenstown", "chamonix"],
        "faqs": [
            ("What makes a strong second-home market abroad?", "A strong second-home market combines repeatable owner use, airport access, local services, clear ownership, manageable carrying costs, and resale demand beyond one foreign buyer group."),
            ("Should a second home abroad be rented out?", "Rental offset can help, but buyers should first confirm permits, management quality, net operating costs, seasonality, wear, taxes, and whether personal-use priorities conflict with rental strategy."),
            ("How important is airport access?", "Airport access matters because it affects owner usage, family visits, rental demand, manager oversight, and resale liquidity when the buyer pool is international."),
        ],
    },
    {
        "slug": "overseas-property-investment",
        "title": "Overseas Property Investment: Markets to Compare | Global Home Atlas",
        "description": "Compare overseas property investment destinations by net yield, capital upside, regulatory safety, entry price, and liquidity.",
        "h1": "Overseas Property Investment",
        "keyword": "overseas property investment",
        "theme": "investment underwriting",
        "intent": "investors comparing income, appreciation, governance, and the ability to exit cleanly",
        "destination_ids": ["fukuoka-itoshima", "algarve-cascais", "malaga-costa-del-sol", "da-nang-hoi-an", "phuket-koh-samui", "bali", "croatia-istria-dalmatia", "costa-brava-girona"],
        "faqs": [
            ("What is a good overseas property investment?", "A good investment combines realistic net income, legal clarity, demand durability, price discipline, and a broad future buyer pool."),
            ("Should I chase the highest yield?", "No. High yield can signal regulatory, seasonality, management, title, or liquidity risk."),
            ("How should I compare markets?", "Normalize by net yield, USD per square meter, ownership rules, exit depth, and the lifestyle demand that supports resale."),
        ],
    },
    {
        "slug": "foreign-property-investment-risks",
        "title": "Foreign Property Investment Risks | Global Home Atlas",
        "description": "A practical risk framework for foreign property investment, covering title clarity, rental rules, currency exposure, liquidity, maintenance, and market concentration.",
        "h1": "Foreign Property Investment Risks",
        "keyword": "foreign property investment risks",
        "theme": "risk framework",
        "intent": "buyers searching for a disciplined risk checklist before committing capital to property abroad",
        "destination_ids": ["phuket-koh-samui", "bali", "da-nang-hoi-an", "croatia-istria-dalmatia", "malaga-costa-del-sol", "algarve-cascais", "lake-como", "andermatt"],
        "faqs": [
            ("What are the biggest risks of buying property abroad?", "The major risks are unclear title, foreign-ownership restrictions, changing rental rules, tax surprises, currency movement, weak management, poor building condition, and thin resale liquidity."),
            ("How do currency and tax risks affect returns?", "Currency and taxes can change the real return even when the local property performs well, so buyers should model acquisition costs, annual costs, income taxation, exit costs, and FX movement separately."),
            ("How can buyers reduce title and rental-rule risk?", "Use independent local counsel, verify title and permits directly, avoid opaque structures, confirm rental licensing before underwriting income, and stress-test the investment without optimistic occupancy."),
        ],
    },
    {
        "slug": "portugal-vs-spain-retirement-property",
        "title": "Portugal vs Spain Retirement Property | Global Home Atlas",
        "description": "Compare Portugal and Spain retirement property markets across lifestyle, ownership clarity, value, healthcare practicality, rentals, and resale.",
        "h1": "Portugal vs Spain Retirement Property",
        "keyword": "Portugal vs Spain retirement property",
        "theme": "country comparison",
        "intent": "retirement buyers choosing between Iberian lifestyle, value, and legal-market depth",
        "destination_ids": ["algarve-cascais", "madeira", "valencia", "malaga-costa-del-sol", "costa-brava-girona", "mallorca"],
        "faqs": [
            ("Is Portugal or Spain better for retirement property?", "The better choice depends on tax, residency, healthcare access, local price discipline, and whether you prefer smaller resort markets or deeper city-region liquidity."),
            ("Which has stronger resale liquidity?", "Spain generally offers deeper regional buyer pools in major coastal and city markets, while Portugal can offer focused demand in established expat corridors."),
            ("How should buyers compare Portugal and Spain?", "Compare specific regions, not just countries: Algarve versus Malaga is a more useful decision than Portugal versus Spain in the abstract."),
        ],
    },
    {
        "slug": "greece-vs-portugal-retirement-property",
        "title": "Greece vs Portugal Retirement Property | Global Home Atlas",
        "description": "Compare Greece and Portugal retirement property options for foreign buyers focused on lifestyle, value, ownership, rentals, and long-term livability.",
        "h1": "Greece vs Portugal Retirement Property",
        "keyword": "Greece vs Portugal retirement property",
        "theme": "country comparison",
        "intent": "buyers weighing Mediterranean value, island lifestyle, legal clarity, and retirement resilience",
        "destination_ids": ["crete", "algarve-cascais", "madeira", "croatia-istria-dalmatia", "lake-como", "valencia"],
        "faqs": [
            ("Is Greece cheaper than Portugal for retirement property?", "Some Greek markets can offer attractive entry values, but buyers must compare micro-location, maintenance, flights, seasonality, and resale depth."),
            ("Which is better for year-round living?", "Portugal often screens well for year-round expat infrastructure, while Greece can be compelling where healthcare, access, and local services are strong."),
            ("What is the main risk in island retirement property?", "Seasonality, healthcare distance, maintenance logistics, and narrower resale pools can matter more than the purchase price."),
        ],
    },
    {
        "slug": "japan-retirement-property-foreign-buyers",
        "title": "Japan Retirement Property for Foreign Buyers | Global Home Atlas",
        "description": "Compare Japan retirement property for foreign buyers across lifestyle, access, ownership, residency, reporting, costs, healthcare, rental rules, risks, and four destinations.",
        "h1": "Japan Retirement Property for Foreign Buyers",
        "keyword": "Japan retirement property for foreign buyers",
        "theme": "Japan buyer guide",
        "intent": "foreign buyers deciding whether they can live in Japan long term and whether a Japanese home fits their retirement plan",
        "destination_ids": ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"],
        "author": "Global Home Atlas Research Team",
        "date_published": "2026-06-23",
        "faqs": [
            ("Can buying property give a foreigner residency in Japan?", "No. Property ownership and immigration status are separate. Buyers need an independent status of residence or another lawful basis for each stay."),
            ("Can foreigners buy property in Japan?", "Foreign buyers can generally acquire and register land and buildings, but non-resident reporting, financing, tax, management, and location-specific rules still need professional review."),
            ("Does Japan have a retirement visa?", "Japan does not offer a general retirement visa. A designated-activities route can permit eligible visa-waiver nationals with sufficient savings to stay for six months and, after an extension, up to one year."),
            ("Where should retirement buyers compare in Japan?", "Start with Fukuoka and Itoshima for year-round city access, Hakone and Izu for Tokyo-adjacent lifestyle use, and Hakuba or Niseko only when a seasonal resort property and professional management fit the plan."),
        ],
    },
    {
        "slug": "spain-retirement-property-foreign-buyers",
        "title": "Spain Retirement Property for Foreign Buyers | Global Home Atlas",
        "description": "Compare Spain retirement property for foreign buyers across residency, healthcare, ownership, taxes, rental rules, climate risk, and four distinct destinations.",
        "h1": "Spain Retirement Property for Foreign Buyers",
        "keyword": "Spain retirement property for foreign buyers",
        "theme": "Spain retirement buyer guide",
        "intent": "foreign buyers deciding whether Spain fits their long-term residence, healthcare, lifestyle and property plan",
        "destination_ids": ["valencia", "malaga-costa-del-sol", "costa-brava-girona", "mallorca"],
        "author": "Global Home Atlas Research Team",
        "date_published": "2026-08-21",
        "faqs": [
            ("Does buying property give a foreigner residency in Spain?", "No. Property ownership and immigration status are separate. Spain ended residence permits linked to qualifying investment, including real estate, on 3 April 2025. A buyer needs an independent right or authorization to reside."),
            ("Can foreigners buy property in Spain?", "Foreign buyers can generally acquire Spanish property, but the transaction, financing, taxes, land-registry position, community rules and intended rental use need property-specific review."),
            ("How does healthcare work for foreign retirees in Spain?", "Eligibility depends on residence, social-security coordination and other legal routes, not on owning a home. Confirm the route before moving; some applicants must demonstrate private cover during the residence process."),
            ("Where should retirement buyers compare in Spain?", "Start with Valencia for a balanced year-round city, Málaga and the Costa del Sol for international retirement infrastructure, Costa Brava and Girona for a more seasonal Catalan lifestyle, and Mallorca when island access and premium carrying costs are acceptable."),
        ],
    },
    {
        "slug": "thailand-villa-ownership-foreigners",
        "title": "Thailand Villa Ownership for Foreigners | Global Home Atlas",
        "description": "Understand Thailand villa ownership for foreigners and compare Phuket and Koh Samui against other Asia lifestyle property alternatives.",
        "h1": "Thailand Villa Ownership for Foreigners",
        "keyword": "Thailand villa ownership foreigners",
        "theme": "Thailand ownership",
        "intent": "buyers attracted to Thai villas who need to understand structure, rental appeal, and legal friction",
        "destination_ids": ["phuket-koh-samui", "bali", "da-nang-hoi-an", "fukuoka-itoshima", "algarve-cascais", "madeira"],
        "faqs": [
            ("Can foreigners own villas in Thailand?", "Foreigners need specialist advice because land ownership, leasehold structures, companies, and condominium rules differ materially."),
            ("Are Phuket and Koh Samui good investment markets?", "They can offer strong lifestyle demand, but buyers must underwrite seasonality, management quality, legal structure, and resale buyer depth."),
            ("What should foreign villa buyers avoid?", "Avoid opaque land structures, unrealistic rental guarantees, weak maintenance reserves, and assets dependent on one demand channel."),
        ],
    },
    {
        "slug": "best-places-to-buy-property-in-europe",
        "title": "Best Places to Buy Property in Europe 2026 | Global Home Atlas",
        "description": "Compare the best places to buy property in Europe for foreign buyers focused on lifestyle, retirement, rental resilience, value discipline, and resale liquidity.",
        "h1": "Best Places to Buy Property in Europe",
        "keyword": "best places to buy property in Europe",
        "theme": "Europe shortlist",
        "intent": "buyers comparing European lifestyle markets with a global investor's discipline",
        "destination_ids": ["valencia", "algarve-cascais", "madeira", "lake-como", "costa-brava-girona", "crete", "annecy", "dolomites-south-tyrol", "mallorca", "croatia-istria-dalmatia"],
        "faqs": [
            ("Where should foreign buyers start in Europe?", "Start with regions that combine livability, transport, healthcare, clear ownership, and a resale market broader than one nationality."),
            ("Is Europe better for lifestyle or yield?", "Europe is often strongest as a lifestyle and capital-preservation decision, while yield depends heavily on local rules and asset selection."),
            ("How should I compare European property markets?", "To compare Europe property markets, start with city access, healthcare, taxation, rental rules, seasonality, entry price, and resale depth at the regional level."),
        ],
    },
    {
        "slug": "where-can-foreigners-buy-property",
        "title": "Where Can Foreigners Buy Property? | Global Home Atlas",
        "description": "Compare where foreigners can buy property using ownership clarity, transaction practicality, lifestyle quality, value, and resale depth across global destinations.",
        "h1": "Where Can Foreigners Buy Property?",
        "keyword": "where can foreigners buy property",
        "theme": "foreign ownership map",
        "intent": "early-stage global buyers looking for a practical map of foreign-buyer access and markets worth researching first",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "malaga-costa-del-sol", "madeira", "crete", "lake-como", "hakone-izu", "phuket-koh-samui", "da-nang-hoi-an"],
        "faqs": [
            ("Can foreigners buy freehold property abroad?", "In some markets foreigners can buy freehold property, while others rely on leasehold, condominium rules, local companies, or special structures. The practical answer must be verified locally before purchase."),
            ("Which markets are hardest for foreign buyers?", "Markets become harder when land ownership is restricted, financing is limited, tax treatment is unclear, rental permits are uncertain, or the transaction structure requires assumptions the buyer cannot verify."),
            ("What should I ask a local lawyer before viewing homes?", "Ask about title type, foreign-buyer restrictions, transfer taxes, annual taxes, rental permissions, inheritance issues, financing, insurance, building permits, and how the property can be resold."),
        ],
    },
]

TRUST_PAGES = [
    {
        "slug": "methodology",
        "title": "Methodology | Global Home Atlas",
        "h1": "Methodology",
        "description": "How Global Home Atlas scores global property destinations across lifestyle, ownership clarity, yield realism, retirement fit, liquidity, and value.",
        "theme": "Research process",
    },
    {
        "slug": "research-standards",
        "title": "Research Standards | Global Home Atlas",
        "h1": "Research Standards",
        "description": "The research standards, caveats, data basis, and verification expectations behind Global Home Atlas destination analysis.",
        "theme": "Trust and caveats",
    },
    {
        "slug": "about",
        "title": "About | Global Home Atlas",
        "h1": "About Global Home Atlas",
        "description": "Global Home Atlas helps globally mobile property buyers compare destinations with a disciplined lifestyle and investment framework.",
        "theme": "About",
    },
    {
        "slug": "contact",
        "title": "Contact | Global Home Atlas",
        "h1": "Contact Global Home Atlas",
        "description": "Contact Global Home Atlas for research questions, data corrections, partnerships, and custom global property shortlist requests.",
        "theme": "Contact",
    },
]


def money(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.0f}"


def number(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}"
    return f"{value:,.0f}"


def percentish(value: str | None) -> float:
    if not value:
        return 0
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[–—-]\s*(\d+(?:\.\d+)?)\s*%", value)
    if range_match:
        lower, upper = (float(part) for part in range_match.groups())
        return (lower + upper) / 2
    single_match = re.search(r"(\d+(?:\.\d+)?)\s*%", value)
    return float(single_match.group(1)) if single_match else 0


def yield_range_label(value: str | None) -> str:
    if not value:
        return "n/a"
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[–—-]\s*(\d+(?:\.\d+)?)\s*%", value)
    if range_match:
        return f"{range_match.group(1)}–{range_match.group(2)}%"
    single_match = re.search(r"(\d+(?:\.\d+)?)\s*%", value)
    return f"{single_match.group(1)}%" if single_match else "n/a"


def score(dest: dict, key: str) -> float:
    return float(dest.get("scores", {}).get(key, {}).get("score", 0) or 0)


def is_destination_recommendable(dest: dict) -> bool:
    return dest.get("access_status", "available") != "restricted"


def destination_access_notice_html(dest: dict) -> str:
    if is_destination_recommendable(dest):
        return ""
    summary = dest.get("access_summary") or "Foreign-buyer access is currently restricted."
    return (
        '<aside class="access-notice" role="note">'
        '<strong>Foreign-buyer access restricted</strong>'
        f'<p>{escape(summary)}</p>'
        '</aside>'
    )


def dimension_score(dest: dict, sources: list[str]) -> float:
    values = [score(dest, key) for key in sources if score(dest, key) > 0]
    return sum(values) / len(values) if values else 0


def consolidate_destination(dest: dict) -> dict:
    dimensions = []
    for item in DIMENSIONS:
        value = dimension_score(dest, item["sources"])
        dimensions.append(
            {
                "key": item["key"],
                "label": item["label"],
                "score": round(value, 2),
                "weight": item["weight"],
                "sources": item["sources"],
                "evidence": item["evidence"],
            }
        )
    consolidated = sum(item["score"] * item["weight"] for item in dimensions)
    enriched = dict(dest)
    enriched["decision_dimensions"] = dimensions
    enriched["decision_score"] = round(consolidated, 2)
    return enriched


CITY_DESTINATION_IDS = {
    "annecy",
    "costa-brava-girona",
    "da-nang-hoi-an",
    "dubai",
    "fukuoka-itoshima",
    "gold-coast-sunshine-coast",
    "innsbruck-tyrol",
    "los-angeles-orange-county",
    "malaga-costa-del-sol",
    "miami-fort-lauderdale",
    "perth-margaret-river",
    "sydney-melbourne",
    "valencia",
    "vancouver",
    "vancouver-island-victoria",
}
COASTAL_CITY_IDS = {"dubai", "sydney-melbourne"}


def destination_location_types(dest: dict) -> list[str]:
    """Return all useful location types for a destination, including overlaps."""
    category = dest.get("category") or ""
    location_types: list[str] = []
    if dest.get("id") in CITY_DESTINATION_IDS or category == "City":
        location_types.append("city")
    if category == "Water" or dest.get("id") in COASTAL_CITY_IDS:
        location_types.append("coast-island")
    elif category == "Mountain":
        location_types.append("mountain")
    elif category == "Mountain + Water":
        location_types.extend(("mountain", "lake"))
    return location_types


GOAL_DIMENSION_WEIGHTS = {
    "retirement": {
        "retirement_fit": 0.45,
        "lifestyle_magnetism": 0.25,
        "global_access": 0.15,
        "foreigner_fit": 0.15,
    },
    "second-home": {
        "lifestyle_magnetism": 0.35,
        "global_access": 0.20,
        "exit_liquidity": 0.20,
        "foreigner_fit": 0.15,
        "ownership_clarity": 0.10,
    },
    "investment": {
        "rental_profit": 0.35,
        "capital_upside": 0.25,
        "exit_liquidity": 0.20,
        "value_entry": 0.20,
    },
    "ownership": {
        "ownership_clarity": 0.45,
        "regulatory_safety": 0.30,
        "foreigner_fit": 0.25,
    },
}


def rank_destinations_for_goal(destinations: list[dict], goal: str) -> list[dict]:
    """Rank the full destination universe for a buying goal without excluding any market."""
    weights = GOAL_DIMENSION_WEIGHTS[goal]
    ranked = []
    for destination in destinations:
        dimensions = {
            item["key"]: float(item.get("score", 0) or 0)
            for item in destination.get("decision_dimensions", [])
        }
        goal_score = sum(dimensions.get(key, 0) * weight for key, weight in weights.items())
        enriched = dict(destination)
        enriched["goal_score"] = round(max(0, min(goal_score, 5)), 2)
        ranked.append(enriched)
    return sorted(
        ranked,
        key=lambda item: (float(item["goal_score"]), float(item.get("decision_score", 0) or 0)),
        reverse=True,
    )


FIT_BUDGET_THRESHOLDS = {
    "low": 4000,
    "mid": 8000,
    "high": 15000,
    "flexible": None,
}


def rank_destinations_for_fit(destinations: list[dict], preferences: dict) -> list[dict]:
    """Rank every destination for a reader's broad buying preferences."""
    goal = preferences.get("goal", "retirement")
    setting = preferences.get("setting", "any")
    use = preferences.get("use", "balanced")
    tradeoff = preferences.get("tradeoff", "balanced")
    budget_threshold = FIT_BUDGET_THRESHOLDS.get(preferences.get("budget", "flexible"))
    ranked = []

    for destination in destinations:
        dimensions = {
            item["key"]: float(item.get("score", 0) or 0)
            for item in destination.get("decision_dimensions", [])
        }
        goal_score = rank_destinations_for_goal([destination], goal)[0]["goal_score"]
        setting_score = goal_score if setting == "any" else (
            5.0 if setting in destination_location_types(destination) else 2.0
        )
        price = float(destination.get("usd_per_m2", 0) or 0)
        if budget_threshold is None or not price:
            budget_score = goal_score
        elif price <= budget_threshold:
            budget_score = 5.0
        elif price <= budget_threshold * 1.25:
            budget_score = 3.5
        else:
            budget_score = max(1.0, 5.0 * budget_threshold / price)

        if use == "personal":
            use_score = (dimensions.get("lifestyle_magnetism", 0) + dimensions.get("retirement_fit", 0)) / 2
        elif use == "rental":
            use_score = (dimensions.get("rental_profit", 0) + dimensions.get("regulatory_safety", 0)) / 2
        else:
            use_score = float(destination.get("decision_score", 0) or 0)

        if tradeoff == "clarity":
            tradeoff_score = (
                dimensions.get("ownership_clarity", 0)
                + dimensions.get("regulatory_safety", 0)
                + dimensions.get("foreigner_fit", 0)
            ) / 3
        elif tradeoff == "upside":
            tradeoff_score = (
                dimensions.get("capital_upside", 0) + dimensions.get("rental_profit", 0)
            ) / 2
        else:
            tradeoff_score = float(destination.get("decision_score", 0) or 0)

        fit_score = (
            goal_score * 0.40
            + setting_score * 0.20
            + budget_score * 0.15
            + use_score * 0.15
            + tradeoff_score * 0.10
        )
        enriched = dict(destination)
        enriched["fit_score"] = round(max(0, min(fit_score, 5)), 2)
        enriched["fit_label"] = (
            "Strong fit" if fit_score >= 4.25 else "Worth comparing" if fit_score >= 3.6 else "Conditional fit"
        )
        enriched["recommendable"] = is_destination_recommendable(destination)
        ranked.append(enriched)

    return sorted(
        ranked,
        key=lambda item: (
            bool(item["recommendable"]),
            float(item["fit_score"]),
            float(item.get("decision_score", 0) or 0),
        ),
        reverse=True,
    )


def rank_destinations(destinations: list[dict]) -> list[dict]:
    ranked = sorted(destinations, key=lambda item: float(item.get("decision_score", 0) or 0), reverse=True)
    for index, destination in enumerate(ranked, start=1):
        destination["rank"] = index
    return ranked


def score_width(value: float) -> str:
    return f"{max(0, min(value, 5)) * 20:.0f}%"


def confidence_tone(value: str | None) -> str:
    text = (value or "").lower()
    if "high" in text:
        return "high"
    if "low" in text:
        return "low"
    return "medium"


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_retirement_costs(path: Path = RETIREMENT_COSTS_PATH) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("destinations"), list):
        raise ValueError("Retirement costs must contain a destinations array")
    records = payload["destinations"]
    ids = [item.get("destination_id") for item in records if isinstance(item, dict)]
    if len(ids) != len(records) or len(ids) != len(set(ids)) or any(not item for item in ids):
        raise ValueError("Retirement destination IDs must be present and unique")
    return payload


def load_mortgage_profiles(path: Path = MORTGAGE_PROFILES_PATH) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("countries"), dict):
        raise ValueError("Mortgage profiles must contain a countries object")
    if not isinstance(payload.get("destination_overrides", {}), dict):
        raise ValueError("Mortgage destination overrides must be an object")
    return payload


def resolve_mortgage_profile(destination: dict, payload: dict) -> dict:
    country = destination.get("country")
    country_profile = payload.get("countries", {}).get(country)
    if not isinstance(country_profile, dict):
        raise ValueError(f"Missing mortgage profile for {country}")
    resolved = deepcopy(country_profile)
    override = payload.get("destination_overrides", {}).get(destination.get("id"), {})
    if not isinstance(override, dict):
        raise ValueError(f"Invalid mortgage override for {destination.get('id')}")
    resolved.update(deepcopy(override))
    resolved["country"] = country
    resolved["destination_id"] = destination.get("id")
    return resolved


def copy_site_assets() -> None:
    if not SOURCE_ASSETS.exists():
        return
    if PUBLIC_ASSETS.exists():
        shutil.rmtree(PUBLIC_ASSETS)
    PUBLIC_ASSETS.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_ASSETS.iterdir():
        if source.is_file():
            shutil.copy2(source, PUBLIC_ASSETS / source.name)
    favicon_ico = SOURCE_ASSETS / "favicon.ico"
    if favicon_ico.exists():
        shutil.copy2(favicon_ico, ARTIFACTS / "favicon.ico")


def favicon_links_html() -> str:
    return """  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.svg">
  <link rel="manifest" href="/assets/site.webmanifest">"""


def build_listing_card(item: dict, extra_class: str = "") -> str:
    class_name = "listing" + (f" {extra_class}" if extra_class else "")
    return f"""
      <article class="{escape(class_name)}">
        <div>
          <p class="listing__type">{escape(item.get("property_type") or "Listing")}</p>
          <h5>{escape(item.get("listing_name") or "Representative listing")}</h5>
          <p>{escape(item.get("note") or "")}</p>
        </div>
        <dl class="listing__facts">
          <div><dt>USD price</dt><dd>{money(item.get("usd_price"))}</dd></div>
          <div><dt>USD/m2</dt><dd>{money(item.get("usd_per_m2"))}</dd></div>
          <div><dt>Size</dt><dd>{number(item.get("size_m2"))} m2</dd></div>
          <div><dt>Local</dt><dd>{escape(item.get("local_currency") or "")} {number(item.get("local_price"))}</dd></div>
        </dl>
        <a class="source-link" href="{escape(item.get("source_url") or "#")}" target="_blank" rel="noreferrer" data-track="outbound_listing_click" data-track-label="{escape(item.get("listing_name") or "Representative listing")}">
          {escape(item.get("source_name") or "Source")} · {escape(item.get("confidence") or "n/a")} confidence
        </a>
      </article>
    """


def build_evidence_cards(listings: list[dict], visible_count: int = 2) -> str:
    if not listings:
        return '<p>No representative listing evidence is currently attached to this destination.</p>'
    visible = "\n".join(build_listing_card(item) for item in listings[:visible_count])
    hidden_items = listings[visible_count:]
    if not hidden_items:
        return f'<div class="page-article evidence-list">{visible}</div>'
    hidden = "\n".join(build_listing_card(item) for item in hidden_items)
    hidden_count = len(hidden_items)
    return f"""
      <div class="page-article evidence-list">{visible}</div>
      <details class="evidence-more">
        <summary>Show full evidence trail ({hidden_count} more)</summary>
        <div class="page-article">{hidden}</div>
      </details>
    """


def build_score_rows(dest: dict) -> str:
    rows = []
    for item in dest.get("decision_dimensions", []):
        key = item["key"]
        value = float(item.get("score", 0) or 0)
        weight = float(item.get("weight", 0) or 0)
        label = item.get("label", key.replace("_", " ").title())
        evidence = item.get("evidence") or "Consolidated decision dimension."
        rows.append(
            f"""
            <li class="score-row" data-score-key="{escape(key)}" data-score-value="{value}" data-score-weight="{weight}">
              <div><span>{escape(label)}</span><strong>{value:.1f}</strong></div>
              <i style="--value: {score_width(value)}"></i>
              <small>Base weight {weight * 100:.0f}%</small>
              <p>{escape(evidence)}</p>
            </li>
            """
        )
    return "\n".join(rows)


def build_evidence_rows(dest: dict) -> str:
    rental = dest.get("rental", {})
    rows = [
        ("USD/m2 benchmark", money(dest.get("usd_per_m2")), dest.get("price_basis") or "Listing-sample benchmark; verify against current local comparables.", dest.get("price_confidence") or "Confidence n/a"),
        ("Net yield", dest.get("net_yield_estimate") or "n/a", rental.get("net_yield") or rental.get("gross_yield") or "Yield estimate needs live underwriting by unit type.", rental.get("confidence") or "Research estimate"),
        ("STR revenue", rental.get("revenue") or "n/a", rental.get("adr_occupancy") or "Occupancy and ADR vary by asset quality, local permit status, and seasonality.", rental.get("confidence") or "Research estimate"),
        ("Ownership clarity", f"{score(dest, 'ownership_clarity'):.1f}/5", dest.get("ownership_notes") or "Confirm title structure, foreign-buyer rules, taxes, and transfer process with local counsel.", "Legal pathway"),
        ("Retirement fit", f"{score(dest, 'retirement_suitability'):.1f}/5", "Composite read across healthcare, access, daily convenience, food, safety, and year-round lifestyle resilience.", "Lifestyle score"),
        ("Exit liquidity", f"{score(dest, 'exit_liquidity'):.1f}/5", "Panel score reflects expected resale depth, buyer pool quality, and market transparency.", "Liquidity score"),
    ]
    return "\n".join(
        f"""
        <article class="evidence-item">
          <div><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>
          <p>{escape(text)}</p>
          <em data-tone="{confidence_tone(tone)}">{escape(tone)}</em>
        </article>
        """
        for label, value, text, tone in rows
    )


def build_weight_controls(destinations: list[dict]) -> str:
    controls = []
    for item in DIMENSIONS:
        key = item["key"]
        weight = float(item.get("weight", 0) or 0)
        label = item["label"]
        controls.append(
            f"""
            <label class="weight-control">
              <span>{escape(label)}</span>
              <input type="range" min="0" max="20" step="1" value="{weight * 100:.0f}" data-weight-key="{escape(key)}">
              <strong>{weight * 100:.0f}%</strong>
            </label>
            """
        )
    return "\n".join(controls)


def build_destination_card(
    dest: dict,
    listings: list[dict],
    _legacy_top_retirement_ids: set[str] | None = None,
) -> str:
    ownership_score = score(dest, "ownership_clarity")
    retirement_score = score(dest, "retirement_suitability")
    yield_score = percentish(dest.get("net_yield_estimate"))
    access_label = "restricted" if not is_destination_recommendable(dest) else "available"
    access_summary = dest.get("access_summary") or "Verify the current purchase route."
    access_warning = ""
    if access_label == "restricted":
        access_warning = (
            '<p class="market-row__warning"><strong>Restricted buyer access.</strong> '
            f'{escape(access_summary)}</p>'
        )
    location_types = " ".join(destination_location_types(dest))
    location_label = ", ".join(
        {
            "city": "City",
            "coast-island": "coast / island",
            "mountain": "Mountain",
            "lake": "lake",
        }[item]
        for item in destination_location_types(dest)
    )
    goal_scores = {
        goal: rank_destinations_for_goal([dest], goal)[0]["goal_score"]
        for goal in GOAL_DIMENSION_WEIGHTS
    }
    return f"""
      <article
        class="market-row"
        data-id="{escape(dest["id"])}"
        data-name="{escape(dest["name"].lower())}"
        data-country="{escape((dest.get("country") or "").lower())}"
        data-category="{escape(dest.get("category") or "")}"
        data-location-types="{escape(location_types)}"
        data-score="{dest.get("decision_score", dest.get("overall_score", 0))}"
        data-price="{dest.get("usd_per_m2", 0)}"
        data-yield="{yield_score}"
        data-ownership="{ownership_score}"
        data-retirement="{retirement_score}"
        data-goal-retirement="{goal_scores['retirement']}"
        data-goal-second-home="{goal_scores['second-home']}"
        data-goal-investment="{goal_scores['investment']}"
        data-goal-ownership="{goal_scores['ownership']}"
        data-access="{escape(access_label)}"
      >
        <label class="market-row__select"><input type="checkbox" class="compare-toggle" value="{escape(dest["id"])}" aria-label="Select {escape(dest["name"])} for comparison"><span>Select</span></label>
        <div class="market-row__market">
          <div class="rank-mark"><span>#{dest["rank"]}</span></div>
          <div class="market-row__identity">
            <h3><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></h3>
            <p>{escape(dest.get("country") or "")} · {escape(location_label)}</p>
          </div>
        </div>
        <div class="market-row__metric"><span>Overall rating</span><strong data-custom-score>{dest.get("decision_score", dest.get("overall_score", 0)):.1f}</strong></div>
        <div class="market-row__metric"><span>Price guide</span><strong>{money(dest.get("usd_per_m2"))}/m2</strong></div>
        <div class="market-row__metric"><span>Expected net yield</span><strong>{escape(yield_range_label(dest.get("net_yield_estimate")))}</strong></div>
        <div class="market-row__metric"><span>Ownership clarity</span><strong>{ownership_score:.1f}/5</strong></div>
        {access_warning}
      </article>
    """


def build_spotlight(destinations: list[dict]) -> str:
    cards = []
    for dest in destinations[:3]:
        cards.append(
            f"""
            <article class="spotlight-card">
              <span>#{dest["rank"]}</span>
              <h3>{escape(dest["name"])}</h3>
              <p>{escape(dest.get("country") or "")} · {escape(dest.get("category") or "")}</p>
              <dl>
                <div><dt>Decision</dt><dd>{dest.get("decision_score", dest.get("overall_score", 0)):.1f}</dd></div>
                <div><dt>USD/m2</dt><dd>{money(dest.get("usd_per_m2"))}</dd></div>
                <div><dt>Yield</dt><dd>{escape(dest.get("net_yield_estimate") or "n/a")}</dd></div>
              </dl>
            </article>
            """
        )
    return "\n".join(cards)


def page_url(slug: str | None = None) -> str:
    if not slug:
        return SITE_URL
    return f"{SITE_URL}{slug}/"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normalized.lower())).strip("-")


def destination_slug(dest: dict) -> str:
    return slugify(dest.get("name") or dest["id"])


DESTINATION_IMAGE_ALTS = {
    "fukuoka-itoshima": "Fukuoka waterfront and city skyline",
    "valencia": "Valencia streetscape opening toward the Mediterranean",
    "algarve-cascais": "Portuguese coastal town overlooking the Atlantic",
}


def destination_image_assets(dest: dict) -> dict[str, str]:
    asset_slug = f"market-{destination_slug(dest)}"
    custom_jpg = SOURCE_ASSETS / f"{asset_slug}.jpg"
    if custom_jpg.exists():
        jpg = f"/assets/{asset_slug}.jpg"
        webp_600 = f"/assets/{asset_slug}-600.webp"
        webp_900 = f"/assets/{asset_slug}-900.webp"
    else:
        jpg = "/assets/destination-dossier-coast.jpg"
        webp_600 = "/assets/destination-dossier-coast-600.webp"
        webp_900 = "/assets/destination-dossier-coast-900.webp"
    return {
        "slug": asset_slug,
        "jpg": jpg,
        "webp_600": webp_600,
        "webp_900": webp_900,
        "alt": DESTINATION_IMAGE_ALTS.get(
            dest.get("id") or "",
            f"Editorial landscape of {dest.get('name') or 'the destination'}, {dest.get('country') or ''}".rstrip(", "),
        ),
    }


def destination_path(dest: dict) -> str:
    return f"destinations/{destination_slug(dest)}"


def destination_url(dest: dict) -> str:
    return page_url(destination_path(dest))


def json_ld(data: dict | list[dict]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def clean_generated_html(html: str) -> str:
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def analytics_head_tags() -> str:
    parts = []
    if BING_SITE_VERIFICATION:
        parts.append(f'  <meta name="msvalidate.01" content="{escape(BING_SITE_VERIFICATION)}">')
    if GA4_MEASUREMENT_ID:
        measurement_id = escape(GA4_MEASUREMENT_ID)
        parts.append(
            f"""  <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "{measurement_id}", {{"send_page_view": true}});
  </script>"""
        )
    return "\n".join(parts)


def analytics_event_script() -> str:
    return f"""
  <script>
    (function () {{
      const measurementReady = Boolean("{escape(GA4_MEASUREMENT_ID)}");
      const sessionKey = "gha_session_id";
      const eventKey = "gha_event_queue";
      function sessionId() {{
        let id = localStorage.getItem(sessionKey);
        if (!id) {{
          id = String(Date.now()) + "-" + Math.random().toString(16).slice(2);
          localStorage.setItem(sessionKey, id);
        }}
        return id;
      }}
      function pushLocal(eventName, params) {{
        try {{
          const queue = JSON.parse(localStorage.getItem(eventKey) || "[]");
          queue.push({{
            event: eventName,
            params: params,
            path: location.pathname,
            title: document.title,
            session_id: sessionId(),
            timestamp: new Date().toISOString()
          }});
          localStorage.setItem(eventKey, JSON.stringify(queue.slice(-100)));
        }} catch (error) {{}}
      }}
      function track(eventName, params) {{
        const payload = Object.assign({{
          page_path: location.pathname,
          page_title: document.title
        }}, params || {{}});
        pushLocal(eventName, payload);
        if (measurementReady && typeof window.gtag === "function") {{
          window.gtag("event", eventName, payload);
        }}
      }}
      window.GHA = Object.assign(window.GHA || {{}}, {{ track }});
      document.addEventListener("click", function (event) {{
        const target = event.target.closest("a, button");
        if (!target) return;
        const explicit = target.getAttribute("data-track");
        const href = target.getAttribute("href") || "";
        if (explicit) {{
          track(explicit, {{
            label: target.getAttribute("data-track-label") || target.textContent.trim(),
            href: href
          }});
          return;
        }}
        if (href.startsWith("/destinations/")) track("destination_click", {{ href }});
        else if (href === "/dashboard/#destinations" || href === "/#destinations" || href === "#destinations") track("dashboard_open", {{ href }});
        else if (href.startsWith("/") && !href.startsWith("/#")) track("internal_page_click", {{ href }});
        else if (href.startsWith("http") && !href.includes(location.hostname)) track("outbound_click", {{ href }});
        else if (href.startsWith("mailto:")) track("contact_click", {{ href }});
      }});
      document.addEventListener("submit", function (event) {{
        const form = event.target.closest("#custom-shortlist-form");
        if (!form) return;
        event.preventDefault();
        const data = new FormData(form);
        const lines = [
          "Global Home Atlas shortlist review request",
          "",
          "Name: " + (data.get("name") || ""),
          "Email: " + (data.get("email") || ""),
          "Budget: " + (data.get("budget") || ""),
          "Target regions: " + (data.get("regions") || ""),
          "Primary goal: " + (data.get("goal") || ""),
          "Citizenship / residency: " + (data.get("citizenship") || ""),
          "Rental expectations: " + (data.get("rental_expectations") || ""),
          "Risk tolerance: " + (data.get("risk_tolerance") || ""),
          "Holding period: " + (data.get("holding_period") || ""),
          "Timing: " + (data.get("timing") || ""),
          "Adviser needs: " + (data.get("adviser_needs") || ""),
          "Saved shortlist: " + (data.get("saved_shortlist") || ""),
          "Notes: " + (data.get("notes") || "")
        ];
        track("custom_shortlist_submit", {{
          budget: data.get("budget") || "",
          regions: data.get("regions") || "",
          goal: data.get("goal") || "",
          risk_tolerance: data.get("risk_tolerance") || "",
          timing: data.get("timing") || "",
          adviser_needs: data.get("adviser_needs") || "",
          saved_shortlist: data.get("saved_shortlist") || ""
        }});
        location.href = "mailto:{escape(CONTACT_EMAIL)}?subject=" + encodeURIComponent("Global Home Atlas Shortlist Review") + "&body=" + encodeURIComponent(lines.join("\\n"));
      }});
    }})();
  </script>
"""


def head_html(title: str, description: str, canonical: str, schema: list[dict]) -> str:
    return f"""
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{favicon_links_html()}
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <link rel="canonical" href="{escape(canonical)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{escape(canonical)}">
  <meta name="twitter:card" content="summary_large_image">
{analytics_head_tags()}
  <script type="application/ld+json">{json_ld(schema)}</script>
"""


def destination_lookup(destinations: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in destinations}


def destinations_for_page(page: dict, destinations: list[dict]) -> list[dict]:
    by_id = destination_lookup(destinations)
    picked = [by_id[item] for item in page["destination_ids"] if item in by_id]
    return picked or destinations[:8]


def destinations_for_ids(destination_ids: list[str], destinations: list[dict]) -> list[dict]:
    by_id = destination_lookup(destinations)
    return [by_id[item] for item in destination_ids if item in by_id]


def seo_guide_links(pages: list[dict], current_slug: str | None = None, limit: int | None = None) -> str:
    links = [
        f'<a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a>'
        for page in pages
        if page["slug"] != current_slug
    ]
    if limit:
        links = links[:limit]
    return "\n".join(links)


def load_auto_internal_links(path: Path = SEO_AUTO_INTERNAL_LINKS_PATH) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def related_guide_pages(page: dict, pages: list[dict], limit: int = 4, priority_slugs: list[str] | None = None) -> list[dict]:
    current_destinations = set(page.get("destination_ids", []))
    by_slug = {candidate["slug"]: candidate for candidate in pages}
    priority = []
    seen = {page["slug"]}
    for slug in priority_slugs or []:
        candidate = by_slug.get(slug)
        if not candidate or slug in seen:
            continue
        priority.append(candidate)
        seen.add(slug)
    scored = []
    for candidate in pages:
        if candidate["slug"] in seen:
            continue
        overlap = len(current_destinations.intersection(candidate.get("destination_ids", [])))
        theme_match = int(candidate.get("theme") == page.get("theme"))
        keyword_match = len(set(page.get("keyword", "").lower().split()).intersection(candidate.get("keyword", "").lower().split()))
        scored.append((overlap, theme_match, keyword_match, candidate))
    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return [*priority, *[candidate for *_, candidate in scored]][:limit]


def contextual_related_guides(page: dict, pages: list[dict], auto_links: list[dict] | None = None) -> str:
    priority_slugs = [
        str(item.get("target_slug"))
        for item in auto_links or []
        if item.get("source_slug") == page.get("slug") and item.get("target_slug")
    ]
    cards = []
    for candidate in related_guide_pages(page, pages, priority_slugs=priority_slugs):
        cards.append(
            f"""
            <article class="seo-link-card">
              <span>{escape(candidate["theme"])}</span>
              <h3><a href="/{escape(candidate["slug"])}/">{escape(candidate["h1"])}</a></h3>
              <p>{escape(candidate["description"])}</p>
            </article>
            """.rstrip()
        )
    return "\n".join(cards)


def country_hubs_for_page(page: dict, destinations: list[dict], limit: int = 4) -> list[dict]:
    page_destination_ids = set(page.get("destination_ids", []))
    scored = []
    for hub in COUNTRY_HUBS:
        hub_destination_ids = set(hub.get("destination_ids", []))
        overlap = len(page_destination_ids.intersection(hub_destination_ids))
        if overlap:
            scored.append((overlap, hub))
    if not scored:
        selected_countries = {
            dest.get("country")
            for dest in destinations_for_page(page, destinations)
            if dest.get("country")
        }
        for hub in COUNTRY_HUBS:
            if hub.get("country") in selected_countries:
                scored.append((1, hub))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [hub for _, hub in scored[:limit]]


def country_hub_cards_for_page(page: dict, destinations: list[dict], limit: int = 4) -> str:
    cards = []
    for hub in country_hubs_for_page(page, destinations, limit):
        cards.append(
            f"""
            <article class="seo-link-card">
              <span>{escape(hub["country"])} hub</span>
              <h3><a href="/countries/{escape(hub["slug"])}/" data-track="country_hub_click" data-track-label="{escape(page["h1"])} to {escape(hub["country"])}">{escape(hub["h1"])}</a></h3>
              <p>{escape(hub["description"])}</p>
            </article>
            """.rstrip()
        )
    return "\n".join(cards)


def guide_decision_path_html(page: dict, destinations: list[dict], pages: list[dict]) -> str:
    selected = destinations_for_page(page, destinations)
    top = selected[0]
    runner_up = selected[1] if len(selected) > 1 else selected[0]
    related_cards = contextual_related_guides(page, pages)
    country_cards = country_hub_cards_for_page(page, destinations)
    return f"""
      <section class="decision-path" aria-label="Decision Path">
        <div>
          <p class="seo-eyebrow">Decision Path</p>
          <h2>Compare the strongest route before opening listings</h2>
          <p>Start with {escape(top["name"])} and test it against {escape(runner_up["name"])}. Then use the linked country hubs and adjacent guides to check ownership clarity, lifestyle fit, rental realism, and exit liquidity before talking to agents.</p>
        </div>
        <div class="decision-path__grid">
          <article>
            <span>Step 01</span>
            <strong>Compare destinations</strong>
            <p>Use the dashboard to compare the shortlist across all {len(DIMENSIONS)} decision dimensions.</p>
            <a href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} decision path">Open dashboard</a>
          </article>
          <article>
            <span>Step 02</span>
            <strong>Check country fit</strong>
            <p>Read the relevant country hubs before narrowing to individual homes.</p>
            <a href="/guides/" data-track="guide_click" data-track-label="{escape(page["h1"])} decision path guides">Browse guide hub</a>
          </article>
          <article>
            <span>Step 03</span>
            <strong>Pressure-test the shortlist</strong>
            <p>Turn this guide into a shortlist review once the buyer intent and destinations are clear.</p>
            <a href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(page["h1"])} decision path">Review my shortlist</a>
          </article>
        </div>
        <div class="seo-link-grid">{country_cards}{related_cards}</div>
        <div class="conversion-callout">
          <h3>Turn this guide into a shortlist</h3>
          <p>Bring your budget, buyer profile, holding period, citizenship, and preferred use case into a focused review before speaking to local agents.</p>
          <a class="seo-button" href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(page["h1"])} conversion callout">Start shortlist review</a>
        </div>
      </section>
    """


def vacation_home_quick_answer_html(page: dict, destinations: list[dict]) -> str:
    if page.get("slug") != "best-places-to-buy-vacation-home-abroad":
        return ""
    selected = destinations_for_page(page, destinations)[:10]
    cards = []
    for index, dest in enumerate(selected, start=1):
        cards.append(
            f"""
            <article>
              <span>#{index} vacation-home candidate</span>
              <h3><a href="/destinations/{escape(destination_slug(dest))}/" data-track="destination_click" data-track-label="vacation home quick answer {escape(dest["name"])}">{escape(dest["name"])}</a></h3>
              <p>{escape(dest.get("panel_verdict") or dest.get("panel_summary") or "")}</p>
              <dl>
                <div><dt>Country</dt><dd>{escape(dest.get("country") or "n/a")}</dd></div>
                <div><dt>Entry benchmark</dt><dd>{money(dest.get("usd_per_m2"))}/m2</dd></div>
                <div><dt>Ownership</dt><dd>{metric_value(dest, "ownership_clarity"):.1f}/5</dd></div>
                <div><dt>Exit</dt><dd>{metric_value(dest, "exit_liquidity"):.1f}/5</dd></div>
              </dl>
            </article>
            """.rstrip()
        )
    return f"""
      <section class="quick-answer" aria-label="Quick Answer">
        <div>
          <p class="seo-eyebrow">Quick Answer</p>
          <h2>Best country to buy a vacation home: start with practical ownership and repeat-use demand</h2>
          <p>The strongest vacation-home locations abroad are not only beautiful. They combine repeat travel demand, clear ownership path, realistic rental-rule risk, usable airports, and resale depth. Start with these Atlas candidates, then compare the full scorecard before looking at individual homes.</p>
        </div>
        <div class="quick-answer__grid">{"".join(cards)}</div>
        <div class="conversion-callout">
          <h3>Shortlist vacation-home countries before calling agents</h3>
          <p>Use the dashboard to compare lifestyle pull, ownership clarity, rental realism, and exit liquidity across countries and locations.</p>
          <a class="seo-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="vacation home quick answer">Compare vacation-home locations</a>
        </div>
      </section>
    """


def country_next_step_html(hub: dict, selected: list[dict], pages: list[dict]) -> str:
    best = selected[0] if selected else None
    guide_links = country_guide_links(hub, pages)
    best_name = best["name"] if best else hub["country"]
    return f"""
      <section class="buyer-next-step" aria-label="Buyer Next Step">
        <div>
          <p class="page-eyebrow">Buyer Next Step</p>
          <h2>Turn {escape(hub["country"])} research into a shortlist</h2>
          <p>Start with {escape(best_name)}, compare the related buying guides, then use shortlist review once the buyer profile, holding period, and budget are clear enough for local diligence.</p>
        </div>
        <div class="buyer-next-step__grid">
          <article>
            <span>First screen</span>
            <strong>Country fit</strong>
            <p>Check ownership clarity, tax and transaction friction, visa assumptions, rental rules, and exit liquidity before reviewing listings.</p>
          </article>
          <article>
            <span>Compare</span>
            <strong>Destination evidence</strong>
            <p>Open the dashboard to compare {escape(hub["country"])} destinations against the wider Atlas model.</p>
            <a href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(hub["country"])} buyer next step">Open dashboard</a>
          </article>
          <article>
            <span>Route</span>
            <strong>Related guides</strong>
            <nav>{guide_links}</nav>
          </article>
        </div>
        <div class="conversion-callout">
          <h3>Turn {escape(hub["country"])} research into a shortlist</h3>
          <p>Use a buyer-specific review to compare lifestyle use, legal practicality, budget fit, and the risk items that need professional local checks.</p>
          <a class="page-button" href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(hub["country"])} buyer next step">Review my shortlist</a>
        </div>
      </section>
    """


def guide_links_for_destination(dest: dict, pages: list[dict], limit: int = 5) -> str:
    matches = []
    for page in pages:
        if dest["id"] in page.get("destination_ids", []):
            matches.append(page)
    if not matches:
        matches = pages[:limit]
    return "\n".join(
        f'<a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a>'
        for page in matches[:limit]
    )


def country_path(hub: dict) -> str:
    return f"countries/{hub['slug']}"


def country_url(hub: dict) -> str:
    return page_url(country_path(hub))


def country_hub_for_destination(dest: dict) -> dict | None:
    for hub in COUNTRY_HUBS:
        if dest["id"] in hub.get("destination_ids", []):
            return hub
    return None


def country_hub_links(current_slug: str | None = None, limit: int | None = None) -> str:
    hubs = [hub for hub in COUNTRY_HUBS if hub["slug"] != current_slug]
    if limit:
        hubs = hubs[:limit]
    return "\n".join(f'<a href="/countries/{escape(hub["slug"])}/">{escape(hub["country"])}</a>' for hub in hubs)


def global_schema_entities() -> list[dict]:
    return [
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL,
            "description": SITE_DESCRIPTION,
            "contactPoint": {
                "@type": "ContactPoint",
                "email": CONTACT_EMAIL,
                "contactType": "research inquiries",
            },
        },
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": SITE_URL,
            "description": SITE_DESCRIPTION,
        },
    ]


def trust_page_links(current_slug: str | None = None) -> str:
    return "\n".join(
        f'<a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a>'
        for page in TRUST_PAGES
        if page["slug"] != current_slug
    )


PRIMARY_NAV_LINKS = [
    (f"/{FIND_YOUR_FIT_SLUG}/", "Find your fit"),
    ("/dashboard/", "Destinations"),
    ("/guides/#country-selection", "Countries"),
    ("/guides/", "Guides"),
    ("/methodology/", "Methodology"),
]


def primary_nav_links_html() -> str:
    return "\n".join(f'<a href="{href}">{label}</a>' for href, label in PRIMARY_NAV_LINKS)


def primary_nav_html(css_prefix: str = "page") -> str:
    links = primary_nav_links_html()
    return f"""
      <nav class="{css_prefix}-nav" aria-label="Primary">
        <a class="{css_prefix}-brand" href="/" aria-label="Global Home Atlas home"><img class="primary-brand-logo" src="/assets/global-home-atlas-logo-compact-light.svg" alt="Global Home Atlas"></a>
        <div class="{css_prefix}-nav-links">
          {links}
        </div>
        <details class="mobile-menu">
          <summary>Menu</summary>
          <nav aria-label="Mobile primary">
            {links}
          </nav>
        </details>
      </nav>
    """


def topbar_nav_html() -> str:
    links = primary_nav_links_html()
    return f"""
    <nav class="topbar" aria-label="Primary">
      <div class="shell topbar__inner">
        <a class="brand" href="/" aria-label="Global Home Atlas home"><img class="brand-logo" src="/assets/global-home-atlas-logo-compact-light.svg" alt="Global Home Atlas"></a>
        <div class="top-links">
          {links}
        </div>
        <details class="mobile-menu">
          <summary>Menu</summary>
          <nav aria-label="Mobile primary">
            {links}
          </nav>
        </details>
      </div>
    </nav>
    """


def sticky_page_nav(items: list[tuple[str, str]]) -> str:
    return '<nav class="sticky-jump" aria-label="Page sections">' + "".join(
        f'<a href="#{escape(anchor)}">{escape(label)}</a>' for label, anchor in items
    ) + "</nav>"


def mobile_action_strip(primary_href: str, primary_label: str, secondary_href: str, secondary_label: str) -> str:
    return f"""
      <nav class="mobile-action-strip" aria-label="Priority actions">
        <a href="{escape(primary_href)}">{escape(primary_label)}</a>
        <a href="{escape(secondary_href)}">{escape(secondary_label)}</a>
      </nav>
    """


def trust_brief_html() -> str:
    return """
      <section class="trust-brief" id="trust-context" aria-label="Research credibility">
        <div>
          <span>Methodology</span>
          <strong>10-dimension destination score</strong>
          <p>Destinations are compared across lifestyle, access, ownership clarity, regulatory safety, yield realism, capital upside, retirement fit, liquidity, foreigner fit, and value entry.</p>
        </div>
        <div>
          <span>Research standard</span>
          <strong>Independent destination intelligence</strong>
          <p>Representative listings anchor market texture. They are not offers, availability guarantees, brokerage placements, or paid destination promotion.</p>
        </div>
        <div>
          <span>Update cadence</span>
          <strong>Regenerated with current source data</strong>
          <p>Scores, caveats, and benchmark evidence should be treated as shortlist inputs, then verified with local legal, tax, immigration, and property advisers.</p>
        </div>
      </section>
    """


def mobile_disclosure_script() -> str:
    return """
  <script>
    (() => {
      const query = window.matchMedia("(max-width: 560px)");
      const details = Array.from(document.querySelectorAll("details.page-section"));
      const resources = Array.from(document.querySelectorAll("details.mobile-resources"));
      if (!details.length) return;
      const apply = () => {
        details.forEach((item, index) => {
          if (query.matches) item.open = item.dataset.mobileOpen === "true" || index === 0;
          else item.open = true;
        });
        resources.forEach((item) => {
          item.open = !query.matches;
        });
      };
      apply();
      if (query.addEventListener) query.addEventListener("change", apply);
      else query.addListener(apply);
    })();
  </script>
    """


def destination_links(destinations: list[dict], current_slug: str | None = None, limit: int | None = None) -> str:
    links = []
    for dest in destinations:
        slug = destination_slug(dest)
        if slug == current_slug:
            continue
        links.append(f'<a href="/destinations/{escape(slug)}/">{escape(dest["name"])}</a>')
    if limit:
        links = links[:limit]
    return "\n".join(links)


def build_home_guide_section(pages: list[dict]) -> str:
    cards = []
    for page in pages:
        cards.append(
            f"""            <article>
              <span>{escape(page["theme"])}</span>
              <h3><a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a></h3>
              <p>{escape(page["description"])}</p>
            </article>"""
        )
    return "\n".join(cards)


def build_home_destination_section(destinations: list[dict]) -> str:
    cards = []
    for dest in destinations:
        cards.append(
            f"""
            <article>
              <span>#{dest["rank"]} · {escape(dest.get("country") or "")}</span>
              <h3><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></h3>
              <p>{escape(dest.get("panel_verdict") or dest.get("panel_summary") or "")}</p>
            </article>
            """
        )
    return "\n".join(cards)


def build_home_trust_section() -> str:
    return "\n".join(
        f"""
        <article>
          <span>{escape(page["theme"])}</span>
          <h3><a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a></h3>
          <p>{escape(page["description"])}</p>
        </article>
        """
        for page in TRUST_PAGES
    )


def destination_by_id(destinations: list[dict], destination_id: str) -> dict | None:
    for dest in destinations:
        if dest.get("id") == destination_id:
            return dest
    return None


def build_landing_buyer_paths() -> str:
    paths = [
        (
            "Retirement or lifestyle base",
            "Find destinations where healthcare, daily ease, culture, and resale depth matter more than headline yield.",
            "/best-places-to-buy-property-abroad-for-retirement/",
            "Retirement",
            "01",
            "#8f6f3d",
        ),
        (
            "Second home abroad",
            "Compare places that can support regular owner use, family visits, and sensible rental offset.",
            "/best-places-to-buy-a-second-home-abroad/",
            "Second homes",
            "02",
            "#5f7f72",
        ),
        (
            "Investment-led shortlist",
            "Start with yield realism, entry value, regulatory safety, and exit liquidity before falling in love with the place.",
            "/overseas-property-investment/",
            "Investment",
            "03",
            "#365f6d",
        ),
        (
            "Destinations with clearer ownership",
            "Prioritize title clarity, foreigner fit, and governance where cross-border ownership can be explained simply.",
            "/where-can-foreigners-buy-property/",
            "Ownership",
            "04",
            "#7b5f80",
        ),
    ]
    return "\n".join(
        f"""
        <a class="path-card" href="{href}" data-track="buyer_path_click" data-track-label="{escape(label)}" style="--path-accent: {escape(accent)};">
          <span><b>{escape(icon)}</b>{escape(kicker)}</span>
          <strong>{escape(label)}</strong>
          <p>{escape(copy)}</p>
          <em>Open path</em>
        </a>
        """.rstrip()
        for label, copy, href, kicker, icon, accent in paths
    )


def build_landing_recommendations(destinations: list[dict]) -> str:
    picks = [
        (
            "fukuoka-itoshima",
            "Best overall",
            "Easy ownership, strong day-to-day living and access to a major city.",
            "/assets/market-fukuoka-itoshima.jpg",
            "Fukuoka waterfront and city skyline",
        ),
        (
            "valencia",
            "Best for city and beach",
            "A walkable city with beaches, healthcare, an airport and year-round life.",
            "/assets/market-valencia.jpg",
            "Valencia streetscape opening toward the Mediterranean",
        ),
        (
            "algarve-cascais",
            "Best for retirement",
            "Warm weather, established expat communities and plenty of towns to compare.",
            "/assets/market-algarve-cascais.jpg",
            "Portuguese coastal town overlooking the Atlantic",
        ),
    ]
    cards = []
    for destination_id, label, rationale, image_path, image_alt in picks:
        dest = destination_by_id(destinations, destination_id)
        if not dest:
            continue
        image_stem = image_path.rsplit(".", 1)[0]
        cards.append(
            f"""
            <article class="recommendation-card">
              <div class="recommendation-card__visual">
                <picture>
                  <source type="image/webp" srcset="{escape(image_stem)}-600.webp 600w, {escape(image_stem)}-900.webp 900w" sizes="(max-width: 640px) calc(100vw - 60px), (max-width: 980px) 50vw, 360px">
                  <img class="recommendation-card__image" src="{escape(image_path)}" alt="{escape(image_alt)}" width="900" height="600" loading="lazy" decoding="async">
                </picture>
              </div>
              <div class="recommendation-card__body">
                <span>{escape(label)}</span>
                <h3><a href="/destinations/{escape(destination_slug(dest))}/" data-track="destination_click" data-track-label="landing recommendation {escape(dest['name'])}">{escape(dest["name"])}</a></h3>
                <p>{escape(dest.get("country") or "")} · {escape(dest.get("category") or "")}</p>
                <strong>{dest.get("decision_score", 0):.1f}/5</strong>
                <em>{escape(rationale)}</em>
                <a class="card-link" href="/destinations/{escape(destination_slug(dest))}/" data-track="destination_click" data-track-label="landing recommendation cta {escape(dest['name'])}">See full profile</a>
              </div>
            </article>
            """.rstrip()
        )
    return "\n".join(cards)


def build_landing_more_market_links(destinations: list[dict]) -> str:
    destination_ids = ["crete", "lake-como", "madeira", "phuket-koh-samui", "queenstown", "whistler"]
    links = []
    for destination_id in destination_ids:
        dest = destination_by_id(destinations, destination_id)
        if not dest:
            continue
        links.append(
            f'<a href="/destinations/{escape(destination_slug(dest))}/" data-track="destination_click" data-track-label="more destinations {escape(dest["name"])}">{escape(dest["name"])}</a>'
        )
    if not links:
        return ""
    return f'<nav class="more-markets" aria-label="More featured destinations"><span>More destinations</span>{"".join(links)}</nav>'


def build_market_finder_data(destinations: list[dict]) -> str:
    def bullets(value: str, *, split_and: bool = False) -> list[str]:
        normalized = " ".join((value or "").replace(";", ",").split())
        if not normalized:
            return []
        parts = [part.strip(" .") for part in normalized.split(",") if part.strip(" .")]
        if split_and and len(parts) == 1 and " and " in parts[0]:
            parts = [part.strip(" .") for part in parts[0].split(" and ") if part.strip(" .")]
        return parts[:4]

    dimension_reasons = {
        "retirement_fit": "Strong retirement and long-stay fit",
        "lifestyle_magnetism": "Strong lifestyle appeal",
        "global_access": "Strong international access",
        "foreigner_fit": "Practical for overseas buyers",
        "exit_liquidity": "Stronger resale depth",
        "ownership_clarity": "Clearer ownership pathway",
        "rental_profit": "Stronger rental fundamentals",
        "capital_upside": "Stronger capital-growth potential",
        "value_entry": "More accessible entry value",
        "regulatory_safety": "More stable operating rules",
    }
    payload: dict[str, list[dict]] = {}
    for route, weights in GOAL_DIMENSION_WEIGHTS.items():
        payload[route] = []
        ranked = rank_destinations_for_goal(destinations, route)
        picks = [dest for dest in ranked if is_destination_recommendable(dest)][:3]
        for dest in picks:
            dimensions = {
                item["key"]: float(item.get("score", 0) or 0)
                for item in dest.get("decision_dimensions", [])
            }
            strongest_dimension = max(
                weights,
                key=lambda key: dimensions.get(key, 0) * weights[key],
            )
            reason = dimension_reasons[strongest_dimension]
            item = {
                "name": dest["name"],
                "country": dest.get("country") or "",
                "score": f"{dest.get('decision_score', 0):.1f}",
                "href": f"/destinations/{destination_slug(dest)}/",
                "reason": reason,
                "reasonBullets": bullets(reason),
                "watch": dest.get("red_flags") or "Verify legal, tax, rental, and resale assumptions locally.",
                "watchBullets": bullets(dest.get("red_flags") or "Verify legal, tax, rental, and resale assumptions locally."),
            }
            image_assets = destination_image_assets(dest)
            item["image"] = image_assets["webp_600"]
            item["imageAlt"] = image_assets["alt"]
            payload[route].append(item)
    return json.dumps(payload, ensure_ascii=False)


def build_landing_inspired_routes() -> str:
    routes = [
        (
            "Live well year-round",
            "Valencia, Fukuoka, and the Algarve suit buyers who want the property to support normal life, not only holiday weeks.",
            "Best for",
            "Retirement-optional households, remote founders, and families planning repeat long stays.",
            "/best-places-to-buy-property-abroad-for-retirement/",
        ),
        (
            "Own with clarity",
            "Japan, Spain, and Portugal routes are useful starting points when clean title, adviser depth, and resale process matter.",
            "Best for",
            "Buyers who want to understand the jurisdiction before they compare villas or apartments.",
            "/where-can-foreigners-buy-property/",
        ),
        (
            "Keep optionality",
            "Madeira, Malaga, and selected second-home markets can work when lifestyle pull is balanced against liquidity and regulation.",
            "Best for",
            "Buyers who may use the home personally, rent selectively, and exit if family plans change.",
            "/best-places-to-buy-a-second-home-abroad/",
        ),
    ]
    return "\n".join(
        f"""
        <article>
          <span>Atlas route</span>
          <h3>{escape(title)}</h3>
          <p>{escape(copy)}</p>
          <dl><div><dt>{escape(fit_label)}</dt><dd>{escape(fit)}</dd></div></dl>
          <a href="{escape(href)}" data-track="inspired_route_click" data-track-label="{escape(title)}">Open route</a>
        </article>
        """.rstrip()
        for title, copy, fit_label, fit, href in routes
    )


def destination_executive_summary_cards(dest: dict) -> str:
    pros = dest.get("pros") or []
    cons = dest.get("cons") or []
    best_buyer = pros[0] if pros else "Lifestyle-led global buyers"
    buy_for = dest.get("profit_driver") or dest.get("panel_verdict") or "A balanced overseas property shortlist candidate."
    underwrite = cons[0] if cons else dest.get("red_flags") or "Verify legal, tax, rental, and resale assumptions locally."
    next_step = "Compare against two or three alternatives, then request a shortlist review before contacting local agents."
    cards = [
        ("Best buyer", best_buyer),
        ("Buy for", buy_for),
        ("Underwrite first", underwrite),
        ("Next step", next_step),
    ]
    return "\n".join(
        f"""
        <article>
          <span>{escape(label)}</span>
          <p>{escape(text)}</p>
        </article>
        """.rstrip()
        for label, text in cards
    )


def destination_quick_decision_html(dest: dict) -> str:
    pros = dest.get("pros") or []
    cons = dest.get("cons") or []
    fields = [
        ("Best buyer", pros[0] if pros else "Lifestyle-led global buyer"),
        ("Best use case", dest.get("profit_driver") or "Personal use with investment discipline."),
        ("Ownership", dest.get("ownership_notes") or "Confirm title and foreign-buyer pathway locally."),
        ("Budget signal", f"{money(dest.get('usd_per_m2'))}/m2 benchmark"),
        ("Rental realism", dest.get("net_yield_estimate") or "Underwrite net yield by asset type."),
        ("Main risk", cons[0] if cons else dest.get("red_flags") or "Verify local legal, rental, and resale risk."),
    ]
    items = "\n".join(
        f"<div><span>{escape(label)}</span><strong>{escape(text)}</strong></div>"
        for label, text in fields
    )
    return f"""
      <section class="decision-panel" aria-label="Quick destination decision">
        <div class="decision-panel__intro">
          <span>30-second decision</span>
          <h2>Should this destination stay on your shortlist?</h2>
          <p>{escape(dest.get("panel_verdict") or dest.get("panel_summary") or "Use this destination as a disciplined shortlist candidate, then verify the local transaction details.")}</p>
        </div>
        <div class="decision-panel__facts">{items}</div>
      </section>
    """


def destination_market_summary_html(dest: dict) -> str:
    pros = [str(item).strip() for item in (dest.get("pros") or []) if str(item).strip()]
    cons = [str(item).strip() for item in (dest.get("cons") or []) if str(item).strip()]
    facts = [
        ("Best for", pros[0] if pros else dest.get("profit_driver") or "Long-term global buyers"),
        ("Ownership route", dest.get("ownership_notes") or "Confirm the foreign-buyer route locally."),
        ("Price guide", f"{money(dest.get('usd_per_m2'))}/m2"),
        ("Expected net yield", dest.get("net_yield_estimate") or "Underwrite by property type."),
        ("Main risk", cons[0] if cons else dest.get("red_flags") or "Verify legal, rental, and resale risk."),
    ]
    items = "".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>"
        for label, value in facts
    )
    verdict = dest.get("panel_verdict") or dest.get("panel_summary") or "A destination worth comparing with disciplined local checks."
    return f"""
      <section class="market-summary" aria-label="Destination at a glance">
        <div class="market-summary__verdict">
          <h2>At a glance</h2>
          <p>{escape(verdict)}</p>
        </div>
        <dl class="market-summary__facts">{items}</dl>
      </section>
    """


def destination_query_match_html(dest: dict, pages: list[dict]) -> str:
    destination_id = dest.get("id")
    if destination_id not in {"andermatt", "annecy"}:
        return ""
    if destination_id == "andermatt":
        title = "Andermatt property for foreign buyers: what to check before shortlisting"
        intro = (
            "Andermatt real estate and Swiss resort property for foreign buyers can screen well for scarcity, infrastructure, and Swiss resilience, "
            "but the Atlas view starts with entry price, ownership access, carrying costs, and future buyer depth."
        )
        points = [
            ("Price discipline", "Use the USD/m2 benchmark and listing evidence before assuming resort scarcity creates margin of safety."),
            ("Ownership path", "Check the Swiss foreign-buyer framework and the specific Andermatt exception before comparing units."),
            ("Exit liquidity", "Stress-test whether the buyer pool is deep enough at the target price point and asset type."),
        ]
        related = ["best-places-to-buy-vacation-home-abroad", "foreign-property-investment-risks", "where-can-foreigners-buy-property"]
    else:
        title = "Annecy vacation home and second-home shortlist"
        intro = (
            "An Annecy real estate, vacation home, or second-home thesis in the French Alps depends on lake lifestyle, Geneva access, year-round use, "
            "and whether the selected neighborhood can support both owner enjoyment and resale depth."
        )
        points = [
            ("Use case", "Separate lake-area lifestyle demand from a pure rental-income thesis before reviewing homes."),
            ("Access", "Compare airport and rail practicality with other Alpine and European vacation-home locations."),
            ("Budget fit", "Use listing evidence to distinguish city, lake-village, and premium lake-adjacent pricing."),
        ]
        related = ["best-places-to-buy-vacation-home-abroad", "best-places-to-buy-a-second-home-abroad", "best-places-to-buy-property-in-europe"]
    by_slug = {page["slug"]: page for page in pages}
    guide_cards = []
    for slug in related:
        page = by_slug.get(slug)
        if not page:
            continue
        guide_cards.append(
            f'<a href="/{escape(page["slug"])}/" data-track="guide_click" data-track-label="{escape(dest["name"])} query match {escape(page["h1"])}">{escape(page["h1"])}</a>'
        )
    point_html = "".join(
        f"""
        <article>
          <span>{escape(label)}</span>
          <p>{escape(body)}</p>
        </article>
        """.rstrip()
        for label, body in points
    )
    return f"""
      <section class="query-match-panel" aria-label="{escape(title)}">
        <div>
          <p class="page-eyebrow">Search match</p>
          <h2>{escape(title)}</h2>
          <p>{escape(intro)}</p>
        </div>
        <div class="query-match-panel__grid">{point_html}</div>
        <nav>{''.join(guide_cards)}<a href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(dest["name"])} query match">Review my shortlist</a></nav>
      </section>
    """


def country_locator_svg(dest: dict) -> tuple[str, int, int, str, str]:
    country = dest.get("country") or "Region"
    if country == "Japan":
        svg = """
          <g class="country-outline country-outline--japan">
            <path d="M518 52 C562 42 604 70 612 110 C620 150 586 178 542 166 C500 154 474 120 486 86 C492 68 502 58 518 52 Z" />
            <path d="M432 132 C482 136 532 164 530 198 C528 226 494 242 450 234 C412 228 382 208 344 226 C306 244 266 242 252 218 C238 194 268 174 314 176 C360 178 382 126 432 132 Z" />
            <path d="M310 256 C350 244 388 254 400 280 C386 306 338 314 300 294 C284 282 288 264 310 256 Z" />
            <path d="M206 252 C244 234 288 250 294 286 C300 322 266 346 224 334 C184 322 172 280 206 252 Z" />
            <path d="M142 290 C166 276 198 286 204 310 C196 334 158 344 134 326 C122 312 126 298 142 290 Z" />
            <path d="M252 204 C286 190 324 200 334 226 C322 252 282 264 248 246 C232 232 236 214 252 204 Z" />
          </g>
        """
        if dest.get("id") == "fukuoka-itoshima":
            return svg, 226, 286, "Fukuoka / Itoshima", "Northern Kyushu"
        return svg, 316, 236, dest["name"], "Japan"
    if country == "United States":
        svg = """
          <g class="country-outline">
            <path d="M120 120 C210 82 338 80 452 104 C536 122 594 160 612 220 C546 250 452 264 346 254 C240 244 164 218 108 176 C102 154 106 136 120 120 Z" />
            <path d="M92 238 C132 232 164 246 180 276 C142 294 102 288 76 262 C78 250 84 242 92 238 Z" />
          </g>
        """
        return svg, 372, 178, dest["name"], country
    if country == "Canada":
        svg = """
          <g class="country-outline">
            <path d="M92 76 C188 46 296 58 392 72 C486 84 580 78 642 122 C604 176 542 210 452 222 C350 236 238 218 144 190 C98 176 74 138 92 76 Z" />
          </g>
        """
        return svg, 356, 178, dest["name"], country
    if country in {"Spain", "Portugal", "Italy", "Greece", "France", "Switzerland", "Austria", "Croatia"}:
        svg = """
          <g class="country-outline">
            <path d="M150 96 C250 60 382 68 496 106 C584 136 626 198 590 250 C544 318 406 336 278 304 C170 278 104 218 112 158 C116 130 130 108 150 96 Z" />
            <path d="M518 258 C548 252 576 264 588 288 C566 306 530 306 504 288 C504 274 508 264 518 258 Z" />
          </g>
        """
        return svg, 344, 188, dest["name"], country
    if country in {"Thailand", "Vietnam", "Indonesia"}:
        svg = """
          <g class="country-outline">
            <path d="M300 62 C354 92 388 144 380 198 C374 244 334 286 278 306 C246 268 238 220 252 168 C264 120 278 86 300 62 Z" />
            <path d="M398 228 C458 224 518 244 566 286 C506 306 438 306 378 284 C376 258 382 240 398 228 Z" />
          </g>
        """
        return svg, 360, 214, dest["name"], country
    if country == "New Zealand":
        svg = """
          <g class="country-outline">
            <path d="M360 72 C404 96 426 136 410 174 C378 182 338 164 322 130 C322 104 336 84 360 72 Z" />
            <path d="M298 194 C344 194 382 224 388 268 C356 300 300 306 258 278 C250 238 264 208 298 194 Z" />
          </g>
        """
        return svg, 346, 172, dest["name"], country
    svg = """
      <g class="country-outline">
        <path d="M142 86 C238 46 392 58 514 106 C604 142 636 214 584 276 C522 342 370 344 242 304 C138 272 82 206 106 142 C114 116 126 98 142 86 Z" />
      </g>
    """
    return svg, 360, 190, dest["name"], country


def destination_osm_maps(dest: dict) -> dict[str, dict] | None:
    metadata = {
        "fukuoka-itoshima": {
            "location": {"bbox": (128.0, 30.1, 143.2, 38.8), "marker": (33.5904, 130.2019), "caption": "Marker sits on northern Kyushu, west of central Fukuoka."},
            "area": {"bbox": (130.02, 33.42, 130.58, 33.76), "marker": (33.5904, 130.2019), "caption": "Compare central Fukuoka, station-linked Itoshima, and the beach-adjacent coast."},
        },
        "valencia": {
            "location": {"bbox": (-10.0, 35.2, 4.8, 44.2), "marker": (39.4699, -0.3763), "caption": "Marker shows Valencia on Spain's east coast."},
            "area": {"bbox": (-0.58, 39.28, -0.12, 39.62), "marker": (39.4699, -0.3763), "caption": "Use this map to compare the city core, beach districts, and airport/rail access."},
        },
        "algarve-cascais": {
            "location": {"bbox": (-10.2, 36.5, -6.0, 42.3), "marker": (37.0194, -7.9304), "caption": "Marker anchors the Algarve; Cascais sits farther north near Lisbon."},
            "area": {"bbox": (-9.55, 36.85, -7.35, 39.05), "marker": (37.0194, -7.9304), "caption": "Compare Algarve resort towns with the Lisbon/Cascais corridor."},
        },
        "malaga-costa-del-sol": {
            "location": {"bbox": (-10.0, 35.2, 4.8, 44.2), "marker": (36.7213, -4.4214), "caption": "Marker shows Malaga on Spain's southern Mediterranean coast."},
            "area": {"bbox": (-5.40, 36.42, -3.55, 37.08), "marker": (36.7213, -4.4214), "caption": "Compare Malaga city, airport access, and the Costa del Sol resort corridor."},
        },
        "lake-como": {
            "location": {"bbox": (6.4, 36.4, 18.8, 47.3), "marker": (45.9840, 9.2600), "caption": "Marker shows Lake Como in northern Italy near Milan and the Swiss border."},
            "area": {"bbox": (8.85, 45.65, 9.65, 46.25), "marker": (45.9840, 9.2600), "caption": "Compare western shore, central lake villages, Como town, and access back to Milan."},
        },
        "hakone-izu": {
            "location": {"bbox": (128.0, 30.1, 143.2, 38.8), "marker": (35.2324, 139.1069), "caption": "Marker sits southwest of Tokyo in the Hakone/Izu corridor."},
            "area": {"bbox": (138.75, 34.55, 139.35, 35.35), "marker": (35.2324, 139.1069), "caption": "Compare Hakone access, Izu coast lifestyle, and Tokyo-distance tradeoffs."},
        },
        "madeira": {
            "location": {"bbox": (-18.5, 30.0, -6.0, 42.5), "marker": (32.7607, -16.9595), "caption": "Marker shows Madeira in the Atlantic relative to mainland Portugal."},
            "area": {"bbox": (-17.35, 32.55, -16.55, 33.00), "marker": (32.7607, -16.9595), "caption": "Compare Funchal convenience, south-coast climate, and hill/terrain exposure."},
        },
        "costa-brava-girona": {
            "location": {"bbox": (-10.0, 35.2, 4.8, 44.2), "marker": (41.9794, 2.8214), "caption": "Marker shows Girona and the Costa Brava in northeast Spain near France."},
            "area": {"bbox": (2.40, 41.65, 3.35, 42.45), "marker": (41.9794, 2.8214), "caption": "Compare Girona city access with coastal villages and prime coves."},
        },
        "crete": {
            "location": {"bbox": (19.0, 34.0, 29.0, 42.0), "marker": (35.2401, 24.8093), "caption": "Marker shows Crete south of mainland Greece."},
            "area": {"bbox": (23.30, 34.80, 26.50, 35.80), "marker": (35.2401, 24.8093), "caption": "Compare Chania, Rethymno, Heraklion, and south-coast access."},
        },
        "hakuba": {
            "location": {"bbox": (128.0, 30.1, 143.2, 38.8), "marker": (36.6982, 137.8619), "caption": "Marker shows Hakuba in Nagano, northwest of Tokyo."},
            "area": {"bbox": (137.70, 36.55, 138.05, 36.85), "marker": (36.6982, 137.8619), "caption": "Compare village access, ski areas, and car-dependent locations."},
        },
        "annecy": {
            "location": {"bbox": (-5.0, 41.0, 10.0, 51.5), "marker": (45.8992, 6.1294), "caption": "Marker shows Annecy in the French Alps near Geneva."},
            "area": {"bbox": (5.90, 45.75, 6.35, 46.05), "marker": (45.8992, 6.1294), "caption": "Compare Annecy town, lake villages, and Geneva access."},
        },
        "mallorca": {
            "location": {"bbox": (-10.0, 35.2, 4.8, 44.2), "marker": (39.6953, 3.0176), "caption": "Marker shows Mallorca in the Balearic Islands."},
            "area": {"bbox": (2.25, 39.25, 3.55, 40.10), "marker": (39.6953, 3.0176), "caption": "Compare Palma access, west-coast villages, and north/east resort zones."},
        },
        "croatia-istria-dalmatia": {
            "location": {"bbox": (13.0, 42.0, 19.5, 46.8), "marker": (43.5081, 16.4402), "caption": "Marker anchors Dalmatia; Istria sits farther northwest."},
            "area": {"bbox": (13.30, 42.30, 18.80, 45.70), "marker": (43.5081, 16.4402), "caption": "Compare Istria, Split/Dalmatia, islands, and airport access."},
        },
        "niseko": {
            "location": {"bbox": (128.0, 30.1, 143.2, 45.8), "marker": (42.8048, 140.6874), "caption": "Marker shows Niseko on Hokkaido, southwest of Sapporo."},
            "area": {"bbox": (140.55, 42.65, 140.85, 42.95), "marker": (42.8048, 140.6874), "caption": "Compare Hirafu, Niseko Village, Annupuri, and access to Kutchan."},
        },
        "queenstown": {
            "location": {"bbox": (165.0, -47.5, 179.0, -34.0), "marker": (-45.0312, 168.6626), "caption": "Marker shows Queenstown on New Zealand's South Island."},
            "area": {"bbox": (168.25, -45.25, 169.05, -44.75), "marker": (-45.0312, 168.6626), "caption": "Compare central Queenstown, Frankton access, lakefront, and outer valleys."},
        },
        "phuket-koh-samui": {
            "location": {"bbox": (97.0, 5.0, 106.0, 21.0), "marker": (7.8804, 98.3923), "caption": "Marker anchors Phuket; Koh Samui sits across the peninsula in the Gulf of Thailand."},
            "area": {"bbox": (98.00, 7.50, 100.40, 10.10), "marker": (7.8804, 98.3923), "caption": "Compare Phuket west/south coast with Koh Samui's villa market."},
        },
        "vancouver-island-victoria": {
            "location": {"bbox": (-141.0, 41.0, -52.0, 84.0), "marker": (48.4284, -123.3656), "caption": "Marker shows Victoria on southern Vancouver Island."},
            "area": {"bbox": (-125.50, 48.10, -123.00, 50.00), "marker": (48.4284, -123.3656), "caption": "Compare Victoria, southern island access, and more remote coastal areas."},
        },
        "dolomites-south-tyrol": {
            "location": {"bbox": (6.4, 36.4, 18.8, 47.3), "marker": (46.4983, 11.3548), "caption": "Marker shows South Tyrol in northern Italy near Austria."},
            "area": {"bbox": (10.70, 46.20, 12.50, 46.90), "marker": (46.4983, 11.3548), "caption": "Compare Bolzano access, Dolomite valleys, ski villages, and resort scarcity."},
        },
        "bali": {
            "location": {"bbox": (94.0, -11.0, 142.0, 6.0), "marker": (-8.3405, 115.0920), "caption": "Marker shows Bali within the Indonesian archipelago."},
            "area": {"bbox": (114.40, -8.90, 115.80, -8.00), "marker": (-8.3405, 115.0920), "caption": "Compare south Bali, Canggu/Berawa, Uluwatu, Ubud, and airport access."},
        },
        "chamonix": {
            "location": {"bbox": (-5.0, 41.0, 10.0, 51.5), "marker": (45.9237, 6.8694), "caption": "Marker shows Chamonix in the French Alps near Switzerland and Italy."},
            "area": {"bbox": (6.55, 45.75, 7.15, 46.10), "marker": (45.9237, 6.8694), "caption": "Compare Chamonix centre, Argentiere, Les Houches, and valley access."},
        },
        "park-city-deer-valley": {
            "location": {"bbox": (-125.0, 24.0, -66.5, 49.5), "marker": (40.6461, -111.4980), "caption": "Marker shows Park City east of Salt Lake City in Utah."},
            "area": {"bbox": (-111.70, 40.55, -111.35, 40.78), "marker": (40.6461, -111.4980), "caption": "Compare Park City, Deer Valley, Canyons, and airport-distance tradeoffs."},
        },
        "da-nang-hoi-an": {
            "location": {"bbox": (102.0, 8.0, 110.5, 23.8), "marker": (16.0544, 108.2022), "caption": "Marker shows Da Nang on Vietnam's central coast."},
            "area": {"bbox": (107.90, 15.75, 108.55, 16.25), "marker": (16.0544, 108.2022), "caption": "Compare Da Nang beach districts, airport access, and Hoi An lifestyle."},
        },
        "whistler": {
            "location": {"bbox": (-141.0, 41.0, -52.0, 84.0), "marker": (50.1163, -122.9574), "caption": "Marker shows Whistler north of Vancouver in British Columbia."},
            "area": {"bbox": (-123.25, 49.95, -122.65, 50.25), "marker": (50.1163, -122.9574), "caption": "Compare Whistler Village, Creekside, Nordic, and outer neighbourhoods."},
        },
        "andermatt": {
            "location": {"bbox": (5.8, 45.7, 10.6, 47.9), "marker": (46.6357, 8.5941), "caption": "Marker shows Andermatt in central Switzerland."},
            "area": {"bbox": (8.35, 46.45, 8.85, 46.80), "marker": (46.6357, 8.5941), "caption": "Compare village core, resort development, and alpine pass access."},
        },
        "innsbruck-tyrol": {
            "location": {"bbox": (9.3, 46.3, 17.2, 49.1), "marker": (47.2692, 11.4041), "caption": "Marker shows Innsbruck in Austria's Tyrol region."},
            "area": {"bbox": (11.10, 47.10, 11.75, 47.45), "marker": (47.2692, 11.4041), "caption": "Compare Innsbruck city access, nearby ski villages, and valley locations."},
        },
        "lake-tahoe": {
            "location": {"bbox": (-125.0, 24.0, -66.5, 49.5), "marker": (39.0968, -120.0324), "caption": "Marker shows Lake Tahoe on the California/Nevada border."},
            "area": {"bbox": (-120.35, 38.75, -119.75, 39.35), "marker": (39.0968, -120.0324), "caption": "Compare north shore, south shore, ski access, and cross-border rules."},
        },
        "jackson-hole": {
            "location": {"bbox": (-125.0, 24.0, -66.5, 49.5), "marker": (43.4799, -110.7624), "caption": "Marker shows Jackson Hole in western Wyoming near Grand Teton."},
            "area": {"bbox": (-111.20, 43.25, -110.40, 43.85), "marker": (43.4799, -110.7624), "caption": "Compare Jackson town, Teton Village, Wilson, and protected-land scarcity."},
        },
        "ticino-lake-lugano": {
            "location": {"bbox": (5.8, 45.7, 10.6, 47.9), "marker": (46.0037, 8.9511), "caption": "Marker shows Lugano in Switzerland's Italian-speaking Ticino."},
            "area": {"bbox": (8.50, 45.75, 9.25, 46.25), "marker": (46.0037, 8.9511), "caption": "Compare Lugano city, lake villages, and cross-border Italy access."},
        },
        "aspen-snowmass": {
            "location": {"bbox": (-125.0, 24.0, -66.5, 49.5), "marker": (39.1911, -106.8175), "caption": "Marker shows Aspen/Snowmass in Colorado's Roaring Fork Valley."},
            "area": {"bbox": (-107.10, 39.00, -106.60, 39.35), "marker": (39.1911, -106.8175), "caption": "Compare Aspen core, Snowmass, airport access, and valley alternatives."},
        },
        "swiss-valais-vaud-alps": {
            "location": {"bbox": (5.8, 45.7, 10.6, 47.9), "marker": (46.0960, 7.2280), "caption": "Marker anchors Valais/Vaud alpine resort territory in western Switzerland."},
            "area": {"bbox": (6.70, 45.85, 7.80, 46.55), "marker": (46.0960, 7.2280), "caption": "Compare Verbier, Villars, Crans-Montana, and valley access."},
        },
    }
    item = metadata.get(dest.get("id"))
    if not item:
        return None
    return {
        key: {
            "title": f"{dest['name']} {key} map",
            **value,
        }
        for key, value in item.items()
    }


def osm_embed_html(map_info: dict, class_name: str) -> str:
    west, south, east, north = map_info["bbox"]
    marker_lat, marker_lon = map_info["marker"]
    bbox = f"{west},{south},{east},{north}"
    src = f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={marker_lat},{marker_lon}"
    link = f"https://www.openstreetmap.org/?mlat={marker_lat}&mlon={marker_lon}#map=10/{marker_lat}/{marker_lon}"
    return f"""
      <div class="real-map {escape(class_name)}">
        <iframe title="{escape(map_info["title"])}" loading="eager" referrerpolicy="no-referrer-when-downgrade" src="{escape(src)}"></iframe>
        <a href="{escape(link)}" target="_blank" rel="noreferrer">Open larger map</a>
        <p>{escape(map_info.get("caption") or "")}</p>
      </div>
    """


def destination_location_map_html(dest: dict) -> str:
    country_svg, marker_x, marker_y, marker_label, marker_note = country_locator_svg(dest)
    osm_maps = destination_osm_maps(dest)
    if dest.get("id") == "fukuoka-itoshima":
        routes = [
            ("Seoul", "Short regional flight"),
            ("Taipei", "Regional access"),
            ("Shanghai", "North Asia context"),
        ]
        copy = "Fukuoka / Itoshima sits on Kyushu's north coast: a city-and-coast Japan base with airport access close enough to make repeat visits realistic."
    elif dest.get("country"):
        routes = [
            ("Capital city", "Gateway context"),
            ("Regional hub", "Access comparison"),
            ("Nearby market", "Alternative shortlist"),
        ]
        copy = f"Use this location view to place {dest['name']} in context before comparing listings. The key buyer question is how easily the destination connects to airports, services, and alternative markets."
    else:
        routes = [("Gateway", "Access context"), ("Alternative", "Comparison market"), ("Hub", "Services")]
        copy = f"Use this location view to understand where {dest['name']} sits before moving into micro-location and budget diligence."
    route_html = "\n".join(
        f"<li><span>{escape(label)}</span><strong>{escape(note)}</strong></li>"
        for label, note in routes
    )
    map_html = (
        osm_embed_html(osm_maps["location"], "real-map--location")
        if osm_maps
        else f"""
        <div class="atlas-map atlas-map--location locator-map" aria-hidden="true">
          <span class="locator-map__country-name">{escape(dest.get("country") or "Region")}</span>
          <svg viewBox="0 0 720 360" role="img" aria-label="{escape(dest['name'])} country locator map">
            {country_svg}
            <line class="locator-map__callout" x1="{marker_x}" y1="{marker_y}" x2="{marker_x + 70}" y2="{max(marker_y - 54, 44)}" />
            <circle class="locator-map__dot" cx="{marker_x}" cy="{marker_y}" r="9" />
          </svg>
          <div class="atlas-map__pin locator-map__label" style="--x:{min(marker_x + 95, 650) / 7.2}%; --y:{max(marker_y - 70, 44) / 3.6}%;">
            <span>{escape(marker_label)}</span>
            <strong>{escape(marker_note)}</strong>
          </div>
        </div>
        """
    )
    return f"""
      <section class="page-section location-map-section" id="where-it-is" aria-label="Destination location map">
        <div class="location-map-section__copy">
          <span>Where it is</span>
          <h2>Place the destination before you compare homes</h2>
          <p>{escape(copy)}</p>
        </div>
        {map_html}
        <ul class="map-context-list">{route_html}</ul>
      </section>
    """


def destination_lifestyle_html(dest: dict) -> str:
    name = dest["name"]
    if dest.get("id") == "fukuoka-itoshima":
        tiles = [
            ("City-to-coast rhythm", "Use central Fukuoka for daily convenience and Itoshima for slower coastal weekends, food, beaches, and repeatable personal use."),
            ("Airport advantage", "Fukuoka Airport keeps the thesis practical: the destination works for shorter visits, regional Asia trips, and eventual long-stay routines."),
            ("Food and daily life", "The appeal is not only scenery. Food culture, healthcare, safety, and normal city services make the market easier to use outside peak holiday periods."),
        ]
        intro = "Fukuoka / Itoshima is strongest when it is treated as a livable Japan base with coastal upside, not as a pure resort trophy. The delight is in how ordinary life can work: airport access, ramen and seafood, station-linked errands, beach drives, healthcare, and enough city depth to return throughout the year."
    else:
        tiles = [
            ("Daily usability", f"Test whether {name} supports repeat stays, errands, healthcare, transport, food, and family routines outside the most photogenic season."),
            ("Lifestyle pull", dest.get("profit_driver") or "Look for repeatable reasons to return, not only scenery or listing photography."),
            ("Long-stay resilience", "A destination earns shortlist space when it can work for weeks or months, not just a single holiday visit."),
        ]
        intro = f"{name} should be read first as a place to use, then as a property market. The strongest overseas buys usually combine emotional pull with practical routines: access, healthcare, food, services, and a reason to return outside peak season."
    cards = "\n".join(
        f"<article class=\"page-card\"><span>{escape(label)}</span><h3>{escape(label)}</h3><p>{escape(copy)}</p></article>"
        for label, copy in tiles
    )
    return f"""
      <details class="page-section" id="lifestyle" data-mobile-open="true" open>
        <summary><h2>Why People Choose It</h2></summary>
        <p>{escape(intro)}</p>
        <div class="page-grid delight-grid">{cards}</div>
      </details>
    """


def destination_where_to_look_html(dest: dict) -> str:
    name = dest["name"]
    osm_maps = destination_osm_maps(dest)
    if dest.get("id") == "fukuoka-itoshima":
        areas = [
            ("Central Fukuoka", "Best for liquidity, daily convenience, healthcare, airport access, and a larger resale buyer pool.", "Lower emotional scarcity; more urban than coastal."),
            ("Station-linked Itoshima", "Best for a practical coastal lifestyle that still supports errands, access, and repeat use.", "Value changes sharply by station, age, and micro-location."),
            ("Beach-adjacent Itoshima", "Best for lifestyle appeal, family use, and a more memorable Japan second-home experience.", "Scarcity, maintenance, rental permissions, and resale depth need more diligence."),
        ]
    elif dest.get("category") == "Mountain":
        areas = [
            ("Core village", "Best for walkability, rentals, restaurants, and easier resale.", "Higher entry price and less privacy."),
            ("Access corridor", "Best for value and larger homes if transport remains practical.", "Car dependence and thinner off-season demand."),
            ("Prime view / slope zones", "Best for emotional pull and trophy scarcity.", "Maintenance, seasonality, and price discipline matter more."),
        ]
    elif dest.get("category") == "Water":
        areas = [
            ("Urban base", "Best for services, liquidity, healthcare, and year-round use.", "Less resort emotion."),
            ("Lifestyle coast", "Best for personal use, views, and repeat holiday appeal.", "Asset quality and micro-location drive outcomes."),
            ("Prime waterfront", "Best for scarcity and emotional conviction.", "Expensive, harder to underwrite, and often lower yielding."),
        ]
    else:
        areas = [
            ("Core location", "Best for resale, services, and buyer depth.", "Usually less value on entry."),
            ("Lifestyle fringe", "Best for space, privacy, and personal use.", "Liquidity and daily convenience need testing."),
            ("Trophy pocket", "Best for scarcity and emotional pull.", "Price discipline and exit assumptions matter more."),
        ]
    pin_positions = [(22, 56), (48, 46), (72, 34)]
    markers = "\n".join(
        f"""
        <div class="atlas-map__pin atlas-map__pin--area" style="--x:{pin_positions[index][0]}%; --y:{pin_positions[index][1]}%;">
          <span>{escape(label)}</span>
          <strong>{escape(read)}</strong>
        </div>
        """
        for index, (label, read, watch) in enumerate(areas)
    )
    rows = "\n".join(
        f"""
        <article class="comparison-card">
          <div class="comparison-card__head"><h3>{escape(label)}</h3><span>Area read</span></div>
          <p><strong>Use for:</strong> {escape(read)}</p>
          <p><strong>Underwrite:</strong> {escape(watch)}</p>
        </article>
        """
        for label, read, watch in areas
    )
    area_map_html = (
        osm_embed_html(osm_maps["area"], "real-map--area")
        if osm_maps
        else f"""
        <div class="atlas-map atlas-map--area" aria-label="Destination micro-location map">
          <svg viewBox="0 0 720 360" role="img" aria-label="{escape(name)} area map">
            <path d="M54 250 C150 196 252 202 346 158 C456 108 564 96 674 122" />
            <path d="M82 284 C184 258 284 274 382 226 C480 180 564 176 650 206" />
            <path d="M210 62 L248 322" />
            <path d="M360 42 L390 324" />
            <path d="M520 70 L506 310" />
            <circle cx="164" cy="234" r="46" />
            <circle cx="356" cy="174" r="58" />
            <circle cx="540" cy="132" r="50" />
          </svg>
          <div class="atlas-map__legend">
            <span>City / core</span>
            <span>Access corridor</span>
            <span>Lifestyle edge</span>
          </div>
          {markers}
        </div>
        """
    )
    return f"""
      <details class="page-section" id="where-to-look" data-mobile-open="true" open>
        <summary><h2>Where to Look</h2></summary>
        <p>Micro-location decides whether {escape(name)} feels easy to own, easy to use, and realistic to resell. Start with the role the property should play, then compare locations against that role.</p>
        {area_map_html}
        <div class="page-grid">{rows}</div>
      </details>
    """


def destination_budget_html(dest: dict, listings: list[dict]) -> str:
    if not listings:
        return ""
    ordered = sorted(listings, key=lambda item: item.get("usd_price") or 0)
    cards = "\n".join(build_listing_card(item) for item in ordered[:3])
    return f"""
      <details class="page-section" id="budget" data-mobile-open="true" open>
        <summary><h2>What You Can Buy</h2></summary>
        <p>{escape(dest.get("price_basis") or "Representative listings anchor the market texture. Verify current availability, location, condition, and transaction costs before relying on any sample.")}</p>
        <div class="page-article evidence-list">{cards}</div>
      </details>
    """


def destination_fit_html(dest: dict, pros: str, cons: str) -> str:
    return f"""
      <details class="page-section" id="buyer-fit" data-mobile-open="true" open>
        <summary><h2>Buyer Fit</h2></summary>
        <div class="page-grid">
          <article class="page-card"><span>Good fit</span><h3>If you want</h3><ul>{pros}</ul></article>
          <article class="page-card"><span>Poor fit</span><h3>If you need to avoid</h3><ul>{cons}</ul></article>
        </div>
      </details>
    """


def destination_risk_checklist_html(dest: dict) -> str:
    specific = []
    if dest.get("id") == "fukuoka-itoshima":
        specific = [
            "Confirm STR licensing, building-level rules, and the practical effect of Japan's annual rental caps before underwriting income.",
            "Check distance to rail, airport routing, and day-to-day car dependence for the exact Itoshima micro-location.",
            "Inspect coastal maintenance exposure, building age, earthquake resilience, insurance, and renovation needs.",
            "Stress-test resale depth separately for central Fukuoka, station-linked Itoshima, and beach-adjacent homes.",
        ]
    else:
        specific = [
            "Confirm local rental permissions, building rules, licensing, and realistic net income after vacancy and management.",
            "Inspect building condition, insurance, climate exposure, renovation cost, and property-management depth.",
            "Stress-test resale liquidity by reviewing recent comparable sales, buyer mix, and time on market.",
            "Validate title, transfer process, taxes, financing, and ownership structure with independent local advisers.",
        ]
    items = "\n".join(f"<li>{escape(item)}</li>" for item in specific)
    return f"""
      <details class="page-section" id="risks" open>
        <summary><h2>Risks to Underwrite First</h2></summary>
        <ul>{items}</ul>
      </details>
    """


def destination_compare_html(dest: dict, peers: list[dict]) -> str:
    if not peers:
        return ""
    rows = []
    for peer in peers[:4]:
        rows.append(
            f"""
            <article class="comparison-card">
              <div class="comparison-card__head">
                <h3><a href="/destinations/{escape(destination_slug(peer))}/">{escape(peer["name"])}</a></h3>
                <span>{peer.get("decision_score", 0):.1f}/5</span>
              </div>
              <dl>
                <div><dt>Price</dt><dd>{money(peer.get("usd_per_m2"))}/m2</dd></div>
                <div><dt>Yield</dt><dd>{escape(peer.get("net_yield_estimate") or "n/a")}</dd></div>
              </dl>
              <p>{escape(peer.get("panel_verdict") or peer.get("panel_summary") or "Compare buyer fit, ownership, yield, and exit liquidity.")}</p>
            </article>
            """
        )
    return f"""
      <details class="page-section" id="compare" open>
        <summary><h2>Compare Before You Commit</h2></summary>
        <p>The destination decision gets clearer when {escape(dest["name"])} is compared against a few plausible alternatives rather than judged in isolation.</p>
        <div class="page-grid">{"".join(rows)}</div>
      </details>
    """


def premium_report_catalog() -> list[dict]:
    return [
        {
            "title": "Polished Buyer Memo",
            "copy": "A paid version of the dashboard preview with personalized fit ranking, destinations to avoid, ownership-path notes, transaction-risk priorities, and adviser questions.",
            "best_for": "Best after you have compared 2-4 plausible destinations and need a decision-ready brief.",
            "deliverables": ["Fit-ranked shortlist", "Avoid-list logic", "Ownership path notes", "Adviser question set"],
        },
        {
            "title": "Retirement Market Brief",
            "copy": "A buyer-specific screen for lifestyle durability, healthcare practicality, ownership clarity, tax flags, and future exit options.",
            "best_for": "Best for retirement-optional families choosing between Europe and Asia.",
            "deliverables": ["Retirement fit screen", "Healthcare and access flags", "Tax and ownership caveats", "Resale-depth priorities"],
        },
        {
            "title": "Second-Home Shortlist Memo",
            "copy": "A structured comparison of personal-use appeal, rental offset realism, seasonality, access, and local operating friction.",
            "best_for": "Best before viewings, agent mandates, and property-specific legal work.",
            "deliverables": ["Use-case ranking", "Rental offset reality check", "Seasonality risks", "Operating-friction checklist"],
        },
        {
            "title": "Investment Risk Review",
            "copy": "A risk-first memo that separates yield claims from permits, taxes, financing, liquidity, and asset-management assumptions.",
            "best_for": "Best for buyers who want income support without ignoring downside.",
            "deliverables": ["Yield claim stress test", "Permit and tax risks", "Liquidity screen", "Manager and financing questions"],
        },
    ]


def build_premium_report_teasers() -> str:
    reports = premium_report_catalog()
    return "\n".join(
        f"""
        <article class="report-card">
          <span>Premium brief</span>
          <h3>{escape(report["title"])}</h3>
          <p>{escape(report["copy"])}</p>
          <strong>{escape(report["best_for"])}</strong>
          <a href="/shortlist-review/" data-track="report_teaser_click" data-track-label="{escape(report["title"])}">Discuss this brief</a>
        </article>
        """.rstrip()
        for report in reports
    )


def build_report_library_cards() -> str:
    return "\n".join(
        f"""
        <article class="page-card">
          <span>Premium brief</span>
          <h3>{escape(report["title"])}</h3>
          <p>{escape(report["copy"])}</p>
          <ul>{"".join(f"<li>{escape(item)}</li>" for item in report["deliverables"])}</ul>
          <a class="page-button" href="/shortlist-review/" data-track="report_library_cta" data-track-label="{escape(report["title"])}">Discuss this report</a>
        </article>
        """.rstrip()
        for report in premium_report_catalog()
    )


def country_summary_metrics(hub: dict, destinations: list[dict]) -> dict:
    selected = destinations_for_ids(hub.get("destination_ids", []), destinations)
    if not selected:
        return {"count": 0, "score": 0, "entry": 0, "ownership": 0, "retirement": 0, "liquidity": 0, "top": ""}
    return {
        "count": len(selected),
        "score": sum(float(dest.get("decision_score", 0) or 0) for dest in selected) / len(selected),
        "entry": sum(float(dest.get("usd_per_m2", 0) or 0) for dest in selected) / len(selected),
        "ownership": sum(metric_value(dest, "ownership_clarity") for dest in selected) / len(selected),
        "retirement": sum(metric_value(dest, "retirement_fit") for dest in selected) / len(selected),
        "liquidity": sum(metric_value(dest, "exit_liquidity") for dest in selected) / len(selected),
        "top": selected[0]["name"],
    }


def country_report_recommendation(hub: dict) -> tuple[str, str]:
    slug = hub["slug"]
    if slug in {"portugal-property", "spain-property", "greece-property", "japan-property"}:
        return (
            "Retirement Market Brief",
            "Useful when healthcare, long-stay practicality, tax flags, and future resale matter more than headline yield.",
        )
    if slug in {"thailand-property", "switzerland-property"}:
        return (
            "Investment Risk Review",
            "Useful when ownership structure, permits, taxes, financing, liquidity, and income assumptions need a risk-first screen.",
        )
    return (
        "Second-Home Shortlist Memo",
        "Useful when the buyer needs to balance personal use, rental offset, seasonality, access, and operating friction.",
    )


def build_country_comparison_page(destinations: list[dict], pages: list[dict]) -> str:
    canonical = page_url("country-comparison")
    title = "Compare Countries for Buying Property Abroad | Global Home Atlas"
    description = "Compare country-level property buying routes by ownership clarity, retirement fit, entry value, liquidity, and best-fit buyer type."
    rows = []
    cards = []
    for hub in COUNTRY_HUBS:
        metrics = country_summary_metrics(hub, destinations)
        rows.append(
            f"""
            <tr>
              <td><strong><a href="/countries/{escape(hub["slug"])}/">{escape(hub["country"])}</a></strong><br><span>{escape(hub["description"])}</span></td>
              <td>{metrics["count"]}</td>
              <td>{metrics["score"]:.1f}/5</td>
              <td>{money(metrics["entry"])}/m2</td>
              <td>{metrics["ownership"]:.1f}/5</td>
              <td>{metrics["retirement"]:.1f}/5</td>
              <td>{metrics["liquidity"]:.1f}/5</td>
              <td>{escape(metrics["top"])}</td>
            </tr>
            """.rstrip()
        )
        cards.append(
            f"""
            <article class="page-card">
              <span>{metrics["count"]} destinations</span>
              <h3><a href="/countries/{escape(hub["slug"])}/">{escape(hub["country"])}</a></h3>
              <p>{escape(hub["description"])}</p>
              <p><strong>{metrics["score"]:.1f}/5</strong> average decision score · <strong>{metrics["ownership"]:.1f}/5</strong> ownership clarity</p>
            </article>
            """.rstrip()
        )
    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(title, description, canonical, [*global_schema_entities(), {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Compare Countries for Buying Property Abroad", "url": canonical, "description": description, "dateModified": date.today().isoformat()}])}
  <style>{shared_content_css()}</style>
</head>
<body>
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">Country comparison · updated {date.today().isoformat()}</p>
          <h1>Compare Countries for Buying Property Abroad</h1>
          <p class="page-lede">Choose the country route before choosing the property. This view compares ownership clarity, retirement practicality, entry value, and resale depth at the country level.</p>
        </div>
        <aside class="page-hero-card">
          <span>Countries</span><strong>{len(COUNTRY_HUBS)}</strong>
          <span>Destinations</span><strong>{len(destinations)}</strong>
          <span>Model</span><strong>10 dimensions</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <section class="page-stats" aria-label="Country comparison summary">
        <div><span>Use this for</span><strong>Country-first decisions</strong></div>
        <div><span>Best next step</span><strong>Country hub</strong></div>
        <div><span>Risk lens</span><strong>Ownership and exit</strong></div>
        <div><span>Updated</span><strong>{date.today().isoformat()}</strong></div>
      </section>
      {sticky_page_nav([("Compare", "compare"), ("Country Cards", "country-cards"), ("Guides", "guides")])}
      <div class="page-layout">
        <article class="page-article">
          <section class="page-section" id="compare">
            <h2>Country Comparison Matrix</h2>
            <p>Use this as a first-pass routing tool. A country can look attractive overall while a specific city, title route, or rental rule still changes the decision.</p>
            <div class="comparison-table-wrap">
              <table class="comparison-table">
                <thead>
                  <tr>
                    <th>Country</th>
                    <th>Destinations</th>
                    <th>Avg score</th>
                    <th>Avg entry</th>
                    <th>Ownership</th>
                    <th>Retirement</th>
                    <th>Exit</th>
                    <th>Top match</th>
                  </tr>
                </thead>
                <tbody>{"".join(rows)}</tbody>
              </table>
            </div>
          </section>
          <section class="page-section" id="country-cards">
            <h2>Country Routes</h2>
            <div class="page-grid">{"".join(cards)}</div>
          </section>
          <section class="page-section" id="guides">
            <h2>Helpful Buyer Guides</h2>
            <nav class="page-grid">{seo_guide_links(pages, limit=6)}</nav>
          </section>
        </article>
        <aside class="page-aside mobile-resources" open>
          <summary>Decision Support</summary>
          <section class="page-aside-card">
            <h3>How to use this page</h3>
            <p>Start with country constraints, then move into destination-level due diligence once ownership, taxes, residency, and resale assumptions are plausible.</p>
          </section>
          <section class="page-aside-card">
            <h3>Custom shortlist</h3>
            <p>Need the country route mapped to your citizenship, budget, and holding period?</p>
            <a class="page-button" href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="country comparison">Review my shortlist</a>
          </section>
        </aside>
      </div>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Country comparison is a research starting point, not financial, legal, tax, or immigration advice.</p>
      <nav><a href="/guides/">All buying guides</a> {seo_guide_links(pages, limit=6)} {trust_page_links()}</nav>
    </div>
  </footer>
  {mobile_disclosure_script()}
  {analytics_event_script()}
</body>
</html>
"""


def build_report_library_page(destinations: list[dict], pages: list[dict]) -> str:
    canonical = page_url(REPORT_LIBRARY_SLUG)
    schema = [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Premium Property Research Reports",
            "url": canonical,
            "description": REPORT_LIBRARY_DESCRIPTION,
            "dateModified": date.today().isoformat(),
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Reports", "item": canonical},
            ],
        },
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(REPORT_LIBRARY_TITLE, REPORT_LIBRARY_DESCRIPTION, canonical, schema)}
  <style>{shared_content_css()}</style>
</head>
<body>
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">Premium brief library · updated {date.today().isoformat()}</p>
          <h1>Premium Property Research Reports</h1>
          <p class="page-lede">Use the public Atlas to compare destinations. Use a premium brief when the decision needs buyer-specific ranking, exclusions, risk sequencing, and adviser questions.</p>
        </div>
        <aside class="page-hero-card">
          <span>Report formats</span><strong>{len(premium_report_catalog())}</strong>
          <span>Destinations covered</span><strong>{len(destinations)}</strong>
          <span>Best timing</span><strong>Before agents</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <section class="page-stats" aria-label="Report library summary">
        <div><span>Free tools</span><strong>Compare and export</strong></div>
        <div><span>Paid layer</span><strong>Decision memo</strong></div>
        <div><span>Use before</span><strong>Viewings</strong></div>
        <div><span>Advice status</span><strong>Research only</strong></div>
      </section>
      {sticky_page_nav([("Reports", "reports"), ("Free vs Paid", "free-paid"), ("Process", "process"), ("Start", "start")])}
      {trust_brief_html()}
      <div class="page-layout">
        <article class="page-article">
          <section class="page-section" id="reports">
            <h2>Report Formats</h2>
            <p>Each report format starts from the same Atlas framework, then narrows the analysis around the buyer's actual intent, citizenship or residency context, budget, risk tolerance, and holding period.</p>
            <div class="page-grid">{build_report_library_cards()}</div>
          </section>
          <section class="page-section" id="free-paid">
            <h2>Free Preview vs Paid Memo</h2>
            <div class="offer-comparison">
              <article>
                <span>Free Atlas</span>
                <h3>Useful for first-pass comparison</h3>
                <ul>
                  <li>Destination and country research pages.</li>
                  <li>Saved shortlist and exportable preview.</li>
                  <li>Public scoring methodology and trust layer.</li>
                </ul>
              </article>
              <article>
                <span>Paid brief</span>
                <h3>Useful for a real decision</h3>
                <ul>
                  <li>Buyer-specific shortlist ranking and exclusions.</li>
                  <li>Risk order for legal, tax, immigration, financing, and property review.</li>
                  <li>Next diligence questions for local specialists.</li>
                </ul>
              </article>
            </div>
          </section>
          <section class="page-section" id="process">
            <h2>How to Prepare</h2>
            <ul>
              <li>Open the dashboard and save 2-4 destinations that genuinely fit your budget and lifestyle plan.</li>
              <li>Export the free shortlist preview and check whether the tradeoffs still make sense.</li>
              <li>Use the shortlist review intake to share citizenship, residency, rental expectations, timing, and adviser needs.</li>
            </ul>
          </section>
          <section class="page-section" id="start">
            <h2>Start With a Shortlist Review</h2>
            <p>The first step is not payment. It is a fit and scope check so the report work is matched to the decision you need to make.</p>
            <a class="page-button" href="/shortlist-review/" data-track="report_library_cta" data-track-label="report library start">Start shortlist review</a>
          </section>
        </article>
        <aside class="page-aside">
          <section class="page-aside-card">
            <h2>Build the Source List</h2>
            <p>Use the dashboard to compare destinations before requesting a paid brief.</p>
            <a class="page-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="report library">Open dashboard</a>
          </section>
          <section class="page-aside-card">
            <h3>Useful Guides</h3>
            <nav>{seo_guide_links(pages, limit=6)}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Trust Layer</h3>
            <nav>{trust_page_links()}</nav>
          </section>
        </aside>
      </div>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Premium reports are research briefs, not financial, legal, tax, immigration, or transaction advice.</p>
      <nav><a href="/shortlist-review/">Shortlist review</a> <a href="/dashboard/">Research dashboard</a> {trust_page_links()}</nav>
    </div>
  </footer>
{analytics_event_script()}
</body>
</html>
"""


def build_shortlist_review_page(destinations: list[dict], pages: list[dict]) -> str:
    canonical = page_url(SHORTLIST_REVIEW_SLUG)
    top_links = destination_links(destinations[:5], limit=5)
    guide_links = seo_guide_links(pages, limit=6)
    schema = [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Global Home Atlas Shortlist Review",
            "url": canonical,
            "description": SHORTLIST_REVIEW_DESCRIPTION,
            "provider": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
            "serviceType": "Property destination research",
            "areaServed": "Global",
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Shortlist Review", "item": canonical},
            ],
        },
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(SHORTLIST_REVIEW_TITLE, SHORTLIST_REVIEW_DESCRIPTION, canonical, schema)}
  <style>
{shared_content_css()}
    .offer-steps {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .offer-steps article {{ min-width: 0; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }}
    .offer-steps span, .offer-comparison span {{ color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .offer-steps strong {{ display: block; margin: 8px 0 6px; font-size: 18px; line-height: 1.12; }}
    .offer-steps p {{ margin: 0; color: var(--muted); font-size: 13px; line-height: 1.45; }}
    .offer-comparison {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .offer-comparison article {{ min-width: 0; padding: 18px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }}
    .offer-comparison h3 {{ margin: 8px 0 10px; }}
    .offer-comparison ul {{ margin: 0; padding-left: 18px; color: #3f4d48; }}
    @media (max-width: 860px) {{ .offer-steps, .offer-comparison {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 560px) {{ .offer-steps, .offer-comparison {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">Shortlist review · research before agents</p>
          <h1>Review Your Overseas Property Shortlist</h1>
          <p class="page-lede">Before you speak to agents or chase listings, use a structured review to test whether your countries and destinations match your budget, citizenship, lifestyle plan, risk tolerance, and holding period.</p>
        </div>
        <aside class="page-hero-card">
          <span>Primary job</span><strong>Narrow destinations</strong>
          <span>Best timing</span><strong>Before viewings</strong>
          <span>Output</span><strong>Research route</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <section class="page-stats" aria-label="Shortlist review summary">
        <div><span>Step 1</span><strong>Fit check</strong></div>
        <div><span>Step 2</span><strong>Market screen</strong></div>
        <div><span>Step 3</span><strong>Risk order</strong></div>
        <div><span>Step 4</span><strong>Next diligence</strong></div>
      </section>
      {sticky_page_nav([("Fit", "fit"), ("Process", "process"), ("Output", "output"), ("Briefs", "premium-briefs"), ("Limits", "limits"), ("Specialists", "specialists"), ("Start", "start")])}
      {trust_brief_html()}
      <div class="page-layout">
        <article class="page-article">
          <section class="page-section" id="fit">
            <h2>Who This Is For</h2>
            <p>The shortlist review is for serious international buyers who are still choosing the right destination. It is most useful when the buyer has a budget range, a target use case, and a few possible countries, but has not yet committed to agents, viewings, lawyers, or a specific property.</p>
            <div class="page-grid">
              <article class="page-card"><h3>Good fit</h3><ul><li>Retirement or second-home buyers comparing countries.</li><li>Families balancing lifestyle, healthcare, access, and future resale.</li><li>Investors who want yield realism without ignoring ownership and liquidity.</li></ul></article>
              <article class="page-card"><h3>Not the right fit</h3><ul><li>Property-specific legal, tax, immigration, or contract review.</li><li>Requests for guaranteed returns or rental projections.</li><li>Brokerage, paid placement, or undisclosed listing promotion.</li></ul></article>
            </div>
          </section>
          <section class="page-section" id="process">
            <h2>How the Review Works</h2>
            <div class="offer-steps">
              <article><span>01</span><strong>Clarify the job</strong><p>Define whether the property is for retirement, second-home use, rental support, capital preservation, or mixed goals.</p></article>
              <article><span>02</span><strong>Screen jurisdictions</strong><p>Compare ownership clarity, foreigner fit, tax and residency caveats, rental rules, and adviser depth.</p></article>
              <article><span>03</span><strong>Rank destination fit</strong><p>Use the Atlas model to prioritize destinations that fit the buyer instead of the most photogenic listings.</p></article>
              <article><span>04</span><strong>Order diligence</strong><p>Identify what to verify first with local counsel, tax advisers, immigration advisers, agents, or property managers.</p></article>
            </div>
          </section>
          <section class="page-section" id="output">
            <h2>What You Can Receive</h2>
            <div class="offer-comparison">
              <article>
                <span>Free intake</span>
                <h3>Fit and scope check</h3>
                <ul>
                  <li>Confirm whether your question fits Global Home Atlas research.</li>
                  <li>Identify the most useful starting guides and dashboard filters.</li>
                  <li>Clarify whether a deeper custom research brief is appropriate.</li>
                </ul>
              </article>
              <article>
                <span>Paid research path</span>
                <h3>Decision-ready shortlist brief</h3>
                <ul>
                  <li>Buyer-specific destination shortlist and avoid list.</li>
                  <li>Ownership, lifestyle, rental, retirement, and exit tradeoffs.</li>
                  <li>Suggested next diligence questions for local specialists.</li>
                </ul>
              </article>
            </div>
          </section>
          <section class="page-section" id="premium-briefs">
            <h2>Premium Research Paths</h2>
            <p>These are the natural paid extensions of a shortlist review. They keep the work focused on the decision the buyer needs to make before local advisers and property-specific diligence begin.</p>
            <div class="report-grid">
              {build_premium_report_teasers()}
            </div>
          </section>
          <section class="page-section" id="limits">
            <h2>Independence and Limits</h2>
            <p>Global Home Atlas is research-led and not a brokerage. Representative listings are market evidence, not availability guarantees or paid placement. The review does not replace local legal, tax, immigration, financing, insurance, inspection, or regulated investment advice.</p>
            <p>The goal is to help you decide where diligence time is worth spending before you become anchored to a listing, local sales process, or one adviser’s jurisdiction.</p>
          </section>
          <section class="page-section" id="specialists">
            <h2>Specialist Introduction Path</h2>
            <p>Some buyers eventually need local lawyers, tax advisers, immigration advisers, mortgage brokers, buyer agents, or property managers. Global Home Atlas can help identify the type of specialist to look for, and any future introductions should be clearly disclosed and quality-controlled.</p>
            <div class="page-grid">
              <article class="page-card"><h3>When useful</h3><ul><li>After a destination shortlist is narrowed to one or two jurisdictions.</li><li>When ownership, residency, tax, financing, or rental rules decide the next step.</li><li>Before viewing specific properties or signing local mandates.</li></ul></article>
              <article class="page-card"><h3>Disclosure standard</h3><ul><li>No hidden paid placement in destination rankings.</li><li>Any commercial introduction should be disclosed before referral.</li><li>Buyer remains responsible for independent local due diligence.</li></ul></article>
            </div>
          </section>
          <section class="page-section" id="start">
            <h2>Start the Review</h2>
            <p>Send your budget range, citizenship or residency context, target regions, buying goal, rental expectations, risk tolerance, and timing. If you already saved destinations in the dashboard, include those names in the notes field.</p>
            <a class="page-button" href="/contact/#custom-shortlist" data-track="custom_shortlist_cta" data-track-label="shortlist review page">Open intake form</a>
          </section>
        </article>
        <aside class="page-aside">
          <section class="page-aside-card">
            <h2>Use Before You Submit</h2>
            <p>Compare your selected destinations in the dashboard, export a preview, then request a polished buyer memo when the shortlist is worth deeper review.</p>
            <a class="page-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="shortlist review page">Open dashboard</a>
          </section>
          <section class="page-aside-card">
            <h3>Strong Starting Destinations</h3>
            <nav>{top_links}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Useful Guides</h3>
            <nav>{guide_links}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Trust Layer</h3>
            <nav>{trust_page_links()}</nav>
          </section>
        </aside>
      </div>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Independent research for international property decisions before local diligence begins.</p>
      <nav><a href="/dashboard/">Research dashboard</a> <a href="/contact/#custom-shortlist">Open intake</a> {trust_page_links()}</nav>
    </div>
  </footer>
{analytics_event_script()}
</body>
</html>
"""


def build_landing_country_tiles() -> str:
    priority = ["spain-property", "portugal-property", "japan-property", "united-states-property", "canada-property", "italy-property", "greece-property", "thailand-property", "switzerland-property"]
    by_slug = {hub["slug"]: hub for hub in COUNTRY_HUBS}
    cards = []
    for slug in priority:
        hub = by_slug.get(slug)
        if not hub:
            continue
        cards.append(
            f"""
            <a class="country-tile" href="/{escape(country_path(hub))}/" data-track="country_hub_click" data-track-label="landing {escape(hub['country'])}">
              <span>{len(hub.get("destination_ids", []))} destinations</span>
              <strong>{escape(hub["country"])}</strong>
              <p>{escape(hub["description"])}</p>
            </a>
            """.rstrip()
        )
    return "\n".join(cards)


def build_landing_guide_preview(pages: list[dict]) -> str:
    wanted = [
        RETIREMENT_DESTINATIONS_SLUG,
        "best-places-to-buy-property-abroad-for-retirement",
        "best-countries-to-buy-property-as-a-foreigner",
        "best-places-to-buy-a-second-home-abroad",
        "foreign-property-investment-risks",
        "best-places-to-buy-property-in-europe",
        "where-can-foreigners-buy-property",
    ]
    by_slug = {
        page["slug"]: page
        for page in [RETIREMENT_DESTINATIONS_PAGE, *pages]
    }
    cards = []
    for slug in wanted:
        page = by_slug.get(slug)
        if not page:
            continue
        cards.append(
            f"""
            <article class="guide-card">
              <span>{escape(page["theme"])}</span>
              <h3><a href="/{escape(page["slug"])}/" data-track="guide_click" data-track-label="landing {escape(page['h1'])}">{escape(page["h1"])}</a></h3>
              <p>{escape(page["description"])}</p>
            </article>
            """.rstrip()
        )
    return "\n".join(cards)


def build_landing_explore_links(pages: list[dict]) -> str:
    buying_goals = [
        ("Retirement or lifestyle", "/best-places-to-buy-property-abroad-for-retirement/"),
        ("Second home abroad", "/best-places-to-buy-a-second-home-abroad/"),
        ("Investment-led shortlist", "/overseas-property-investment/"),
        ("Clear foreign ownership", "/where-can-foreigners-buy-property/"),
    ]
    country_slugs = [
        "spain-property",
        "portugal-property",
        "japan-property",
        "united-states-property",
        "canada-property",
        "italy-property",
        "greece-property",
        "thailand-property",
        "switzerland-property",
    ]
    country_by_slug = {hub["slug"]: hub for hub in COUNTRY_HUBS}
    guide_slugs = [
        RETIREMENT_DESTINATIONS_SLUG,
        "best-places-to-buy-property-abroad-for-retirement",
        "best-places-to-buy-a-second-home-abroad",
        "foreign-property-investment-risks",
        "best-places-to-buy-property-in-europe",
        "best-countries-to-buy-property-as-a-foreigner",
    ]
    page_by_slug = {page["slug"]: page for page in [RETIREMENT_DESTINATIONS_PAGE, *pages]}

    countries = [
        (country_by_slug[slug]["country"], f'/{country_path(country_by_slug[slug])}/')
        for slug in country_slugs
        if slug in country_by_slug
    ]
    guides = [
        (page_by_slug[slug]["h1"], f'/{slug}/')
        for slug in guide_slugs
        if slug in page_by_slug
    ]

    def compact_links(items: list[tuple[str, str]], track: str, more_label: str) -> str:
        def item_html(item: tuple[str, str], class_name: str = "") -> str:
            label, href = item
            class_attr = f' class="{class_name}"' if class_name else ""
            track_context = "landing" if track == "guide_click" else "explore"
            return f'<li{class_attr}><a href="{escape(href)}" data-track="{track}" data-track-label="{track_context} {escape(label)}">{escape(label)}</a></li>'

        primary = "".join(item_html(item, "explore-primary") for item in items[:3])
        more = "".join(item_html(item) for item in items[3:])
        return f'<ul>{primary}</ul><details class="explore-more"><summary>{escape(more_label)}</summary><ul>{more}</ul></details>'

    return f"""
      <div class="explore-column">
        <h3>By buying goal</h3>
        {compact_links(buying_goals, "buyer_path_click", "More buying goals")}
        <a class="explore-all" href="/guides/" data-track="guide_click" data-track-label="explore all buying goals">View all</a>
      </div>
      <div class="explore-column">
        <h3>By country</h3>
        {compact_links(countries, "country_hub_click", "More countries")}
        <a class="explore-all" href="/country-comparison/" data-track="country_compare_click" data-track-label="explore all countries">View all</a>
      </div>
      <div class="explore-column">
        <h3>Buying guides</h3>
        {compact_links(guides, "guide_click", "More guides")}
        <a class="explore-all" href="/guides/" data-track="guide_click" data-track-label="explore all guides">View all</a>
      </div>
    """.strip()


def build_landing_trust_cards() -> str:
    cards = [
        ("Ownership clarity before romance", "Markets are screened for foreigner fit, title practicality, and exit friction before lifestyle appeal."),
        ("Yield treated as context", "Rental returns are underwriting inputs, not promises or the sole reason to buy."),
        ("Evidence anchors, not listings ads", "Representative listings help price the market texture; they are not availability guarantees or paid placement."),
    ]
    return "\n".join(
        f"""
        <article class="trust-card">
          <span>{index}</span>
          <strong>{escape(title)}</strong>
          <p>{escape(copy)}</p>
        </article>
        """.rstrip()
        for index, (title, copy) in enumerate(cards, start=1)
    )


def generated_internal_link_html(content: dict) -> str:
    link = content.get("generated_internal_link")
    if not link:
        return ""
    path = urlparse(link["target"]).path or "/"
    return (
        '<p class="generated-seo-link">Continue with '
        f'<a href="{escape(path)}">{escape(link["anchor"])}</a>.</p>'
    )


def build_landing_page(
    destinations: list[dict],
    pages: list[dict],
    listings: list[dict],
    countries: int,
    content_overrides: list[dict] | None = None,
) -> str:
    generated = date.today().isoformat()
    content = apply_content_override(
        {
            "title": "Best Places to Buy Property Abroad | Global Property Markets",
            "description": "Compare the best places to buy property abroad, including global property markets for buying property abroad, vacation homes, second homes, retirement, budget, and exit plan.",
            "generated_intro": "Find overseas property markets that fit your lifestyle, ownership constraints, budget, and exit plan.",
        },
        SITE_URL,
        content_overrides or [],
    )
    generated_link = generated_internal_link_html(content)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{favicon_links_html()}
  <title>{escape(content["title"])}</title>
  <meta name="description" content="{escape(content["description"])}">
  <link rel="canonical" href="{SITE_URL}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="Global Home Atlas">
  <meta property="og:description" content="{escape(content["description"])}">
  <meta property="og:url" content="{SITE_URL}">
  <meta name="twitter:card" content="summary_large_image">
{analytics_head_tags()}
  <script type="application/ld+json">{json_ld(global_schema_entities())}</script>
  <style>
    :root {{
      color: #24312d;
      background: #f5f1e9;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --ink: #24312d;
      --muted: #68776f;
      --line: rgba(36, 49, 45, .13);
      --paper: #fffdf7;
      --cream: #f5f1e9;
      --sage: #c7d3c2;
      --eucalyptus: #5f7f72;
      --brass: #a98a4b;
      --deep: #24312d;
      --shadow: 0 18px 48px rgba(36, 49, 45, .10);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    html, body {{ overflow-x: hidden; }}
    body {{ margin: 0; background: var(--cream); color: var(--ink); }}
    a {{ color: var(--eucalyptus); text-underline-offset: 3px; }}
    p {{ line-height: 1.58; }}
    .shell {{ width: min(1160px, calc(100% - 32px)); margin: 0 auto; }}
    .hero {{
      min-height: 78vh;
      display: grid;
      align-items: center;
      padding: 22px 0 76px;
      background:
        linear-gradient(90deg, rgba(255, 253, 247, .98) 0 38%, rgba(255, 253, 247, .76) 62%, rgba(199, 211, 194, .30)),
        linear-gradient(180deg, rgba(245, 241, 233, .04), rgba(245, 241, 233, .50)),
        url("/assets/atlas-map-coastal-sage.jpg");
      background-size: cover;
      background-position: center;
    }}
    .topbar {{ position: absolute; inset: 0 0 auto; padding: 18px 0; }}
    .topbar__inner {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; }}
    .brand {{ display: flex; align-items: center; gap: 12px; color: var(--ink); font-weight: 900; text-decoration: none; }}
    .brand-logo {{ width: 174px; max-width: 48vw; height: auto; display: block; }}
    .top-links {{ display: flex; gap: 18px; flex-wrap: wrap; }}
    .top-links a {{ color: rgba(36, 49, 45, .76); font-size: 13px; font-weight: 800; text-decoration: none; }}
    .top-links a:hover {{ color: var(--ink); }}
    .mobile-menu {{ display: none; position: relative; }}
    .mobile-menu summary {{ min-height: 42px; display: inline-flex; align-items: center; justify-content: center; padding: 0 13px; border: 1px solid rgba(36, 49, 45, .20); border-radius: 6px; color: var(--ink); font-size: 13px; font-weight: 850; list-style: none; cursor: pointer; }}
    .mobile-menu summary::-webkit-details-marker {{ display: none; }}
    .mobile-menu nav {{ position: absolute; right: 0; top: calc(100% + 8px); z-index: 20; width: min(78vw, 280px); display: grid; gap: 2px; padding: 8px; border: 1px solid rgba(36, 49, 45, .16); border-radius: 8px; background: rgba(255, 253, 247, .98); box-shadow: 0 20px 50px rgba(36, 49, 45, .16); }}
    .mobile-menu nav a {{ padding: 12px; border-radius: 6px; color: var(--ink); text-decoration: none; font-weight: 800; }}
    .hero-grid {{ display: grid; grid-template-columns: minmax(0, 760px); align-items: center; padding-top: 74px; }}
    .eyebrow {{ max-width: 100%; margin: 0 0 12px; color: #806738; font-size: 13px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; overflow-wrap: anywhere; }}
    h1 {{ max-width: 860px; margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(46px, 8vw, 104px); line-height: .9; letter-spacing: 0; }}
    .lede {{ max-width: 720px; margin: 24px 0 0; color: #45534e; font-size: clamp(17px, 2.2vw, 21px); }}
    .hero-actions {{ display: grid; justify-items: start; gap: 12px; margin-top: 28px; }}
    .hero-secondary-actions {{ display: flex; flex-wrap: wrap; align-items: center; gap: 4px 24px; }}
    .primary-action, .secondary-action {{
      min-height: 46px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px;
      border-radius: 6px;
      font-weight: 700;
      text-decoration: none;
      letter-spacing: 0;
    }}
    .primary-action {{ background: var(--eucalyptus); color: #fffdf7; }}
    .secondary-action {{ border: 1px solid rgba(36, 49, 45, .20); background: rgba(255, 253, 247, .66); color: var(--ink); }}
    .text-action {{ min-height: 36px; display: inline-flex; align-items: center; color: var(--ink); font-size: 14px; font-weight: 650; text-decoration: none; letter-spacing: 0; }}
    .text-action::after {{ content: " →"; }}
    .card-link::after, .path-card em::after, .inspired-visual::after {{ content: " ->"; }}
    .primary-action:hover, .secondary-action:hover {{ transform: translateY(-1px); box-shadow: 0 10px 24px rgba(36, 49, 45, .13); }}
    .text-action:hover, .card-link:hover {{ color: #365f6d; }}
    .atlas-visual {{ min-height: 178px; position: relative; overflow: hidden; border: 1px solid rgba(36, 49, 45, .13); border-radius: 8px; background: linear-gradient(135deg, rgba(255, 253, 247, .48), rgba(199, 211, 194, .12)), url("/assets/atlas-map-coastal-sage.jpg"); background-size: cover; background-position: center; }}
    .atlas-visual span {{ position: absolute; left: 14px; top: 14px; padding: 9px 10px; border: 1px solid rgba(36, 49, 45, .12); border-radius: 6px; background: rgba(255, 253, 247, .82); color: var(--ink); font-size: 12px; font-weight: 850; }}
    .map-link {{ position: absolute; width: 14px; height: 14px; border: 2px solid #fffdf7; border-radius: 50%; background: var(--eucalyptus); box-shadow: 0 0 0 5px rgba(95, 127, 114, .22); text-indent: -999px; overflow: hidden; transition: transform .18s ease, background .18s ease; }}
    .map-link:hover, .map-link:focus-visible {{ transform: scale(1.18); background: #806738; }}
    .map-link--canada {{ left: 14%; top: 37%; }}
    .map-link--portugal {{ left: 47%; top: 47%; }}
    .map-link--spain {{ left: 49%; top: 45%; }}
    .map-link--italy {{ left: 53%; top: 42%; }}
    .map-link--greece {{ left: 57%; top: 49%; }}
    .map-link--japan {{ right: 16%; top: 42%; }}
    .map-link--thailand {{ right: 23%; top: 60%; }}
    .map-link--nz {{ right: 9%; bottom: 13%; }}
    main {{ margin-top: -24px; position: relative; z-index: 2; }}
    .section {{ margin-bottom: 20px; padding: 20px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); box-shadow: 0 12px 40px rgba(36, 49, 45, .07); }}
    .section--finder {{ position: relative; overflow: hidden; padding: 24px; border-color: rgba(95, 127, 114, .30); background: linear-gradient(135deg, #fffdf7, #eef4ef); }}
    .section--finder .section-header, .section--finder .finder-grid {{ position: relative; z-index: 1; }}
    .finder-map-cue {{ position: absolute; top: -34px; right: -42px; width: 320px; height: 176px; opacity: .12; background: url("/assets/atlas-map-coastal-sage.jpg") center / cover; mask-image: linear-gradient(120deg, transparent, #000 34%); pointer-events: none; }}
    .section-header {{ display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 18px; }}
    .section-header h2 {{ margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 4vw, 42px); line-height: 1; }}
    .section-header p {{ max-width: 680px; margin: 8px 0 0; color: var(--muted); }}
    .path-grid, .recommendation-grid, .country-grid, .trust-grid, .guide-grid, .explore-grid {{ display: grid; gap: 12px; }}
    .path-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .recommendation-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .country-grid {{ grid-template-columns: repeat(7, minmax(0, 1fr)); }}
    .trust-grid, .guide-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .explore-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .explore-column {{ min-width: 0; padding: 4px 20px 4px 0; }}
    .explore-column + .explore-column {{ padding-left: 20px; border-left: 1px solid var(--line); }}
    .explore-column h3 {{ margin: 0 0 12px; font-size: 18px; }}
    .explore-column ul {{ display: grid; gap: 9px; margin: 0; padding: 0; list-style: none; }}
    .explore-column a {{ color: var(--ink); font-weight: 650; text-decoration-color: rgba(95, 127, 114, .5); }}
    .explore-column .explore-all {{ display: inline-block; margin-top: 14px; color: var(--eucalyptus); font-size: 13px; font-weight: 800; }}
    .explore-more {{ margin-top: 9px; }}
    .explore-more summary {{ width: fit-content; min-height: 44px; display: inline-flex; align-items: center; cursor: pointer; color: var(--muted); font-size: 13px; font-weight: 700; }}
    .explore-more ul {{ margin-top: 9px; }}
    .finder-grid {{ display: grid; grid-template-columns: minmax(250px, 320px) minmax(0, 1fr); gap: 18px; align-items: start; }}
    .finder-panel, .finder-output {{ display: grid; align-content: start; gap: 14px; }}
    .finder-panel {{ padding: 18px 0 0; }}
    .finder-output {{ padding-top: 18px; }}
    .finder-step, .finder-panel label, .finder-result span, .finder-result dt {{ color: #806738; font-size: 11px; font-weight: 800; letter-spacing: .07em; line-height: 1.2; text-transform: uppercase; }}
    .finder-step {{ margin: 0; }}
    .finder-panel label {{ display: grid; gap: 9px; }}
    .finder-panel select {{ min-height: 48px; width: 100%; appearance: none; border: 1px solid rgba(95, 127, 114, .24); border-radius: 7px; background: linear-gradient(180deg, #fff, #f8faf6) padding-box, linear-gradient(135deg, transparent calc(100% - 36px), rgba(95, 127, 114, .10) 0) border-box; color: var(--ink); padding: 0 42px 0 14px; font: inherit; font-size: 13px; font-weight: 650; letter-spacing: 0; text-transform: none; }}
    .finder-panel label {{ position: relative; }}
    .finder-panel label::after {{ content: ""; position: absolute; right: 15px; bottom: 19px; width: 8px; height: 8px; border-right: 2px solid #365f6d; border-bottom: 2px solid #365f6d; transform: rotate(45deg); pointer-events: none; }}
    .finder-panel .secondary-action {{ min-height: 44px; width: 100%; justify-content: center; border-color: rgba(95, 127, 114, .24); background: #f8faf6; font-size: 13px; }}
    .finder-note {{ margin: 2px 0 0; color: var(--muted); font-size: 13px; }}
    .finder-signal {{ margin: 7px 0 0 !important; color: #3f4d48 !important; font-size: 13px !important; line-height: 1.4; }}
    .finder-signal strong {{ color: #806738; font-size: 10px; letter-spacing: .07em; text-transform: uppercase; }}
    .finder-results {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .finder-result {{ min-width: 0; display: grid; align-content: start; padding: 16px; border: 1px solid rgba(95, 127, 114, .22); border-radius: 8px; background: #fffdf7; box-shadow: 0 10px 26px rgba(36, 49, 45, .06); }}
    .finder-result__thumb {{ height: 82px; margin: -8px -8px 12px; overflow: hidden; border-radius: 6px; background: #e8ede7; }}
    .finder-result__thumb img {{ width: 100%; height: 100%; display: block; object-fit: cover; filter: saturate(.72) contrast(.94) brightness(.97) sepia(.06); }}
    .finder-result__thumb--map {{ opacity: .42; background: linear-gradient(rgba(244, 238, 226, .18), rgba(244, 238, 226, .18)), url("/assets/atlas-map-coastal-sage.jpg") center / cover; }}
    .finder-result h3 {{ margin: 8px 0 4px; font-family: Georgia, "Times New Roman", serif; font-size: 19px; font-weight: 700; line-height: 1.12; }}
    .finder-result h3 a {{ color: var(--sage); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    .finder-result p {{ margin: 0 0 10px; color: var(--muted); font-size: 14px; }}
    .finder-result dl {{ display: grid; gap: 11px; margin: 0; }}
    .finder-result dd {{ margin: 5px 0 0; color: #3f4d48; font-size: 13px; line-height: 1.38; }}
    .finder-result ul {{ display: grid; gap: 3px; margin: 0; padding-left: 16px; }}
    .finder-result li {{ padding-left: 1px; }}
    .finder-result li::marker {{ color: var(--brass); }}
    .card-link {{ align-self: end; margin-top: 10px; font-size: 13px; font-weight: 800; text-decoration: none; }}
    .inspired-band {{ display: grid; grid-template-columns: minmax(0, .62fr) minmax(0, 1fr); gap: 16px; align-items: stretch; }}
    .inspired-visual {{
      min-height: 320px;
      display: grid;
      align-items: end;
      padding: 22px;
      border-radius: 8px;
      background:
        linear-gradient(180deg, rgba(36, 49, 45, .08), rgba(36, 49, 45, .58)),
        url("/assets/coastal-sage-landscape-band.jpg");
      background-size: cover;
      background-position: center;
      color: #fffdf7;
      text-decoration: none;
    }}
    .inspired-visual span {{ color: rgba(255, 253, 247, .78); font-size: 12px; font-weight: 900; letter-spacing: .11em; text-transform: uppercase; }}
    .inspired-visual strong {{ display: block; max-width: 420px; margin-top: 8px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(28px, 4vw, 46px); line-height: 1; }}
    .inspired-routes {{ display: grid; gap: 12px; }}
    .inspired-routes article {{ min-width: 0; padding: 16px; border: 1px solid rgba(95, 127, 114, .20); border-left: 4px solid var(--eucalyptus); border-radius: 8px; background: #f9fbf6; }}
    .inspired-routes span, .inspired-routes dt {{ color: var(--brass); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .inspired-routes h3 {{ margin: 7px 0 6px; font-size: 20px; }}
    .inspired-routes p, .inspired-routes dd {{ margin: 0; color: #3f4d48; font-size: 14px; line-height: 1.5; }}
    .inspired-routes dl {{ margin: 12px 0 10px; }}
    .inspired-routes a {{ font-weight: 900; }}
    .report-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .report-card {{ min-width: 0; display: grid; gap: 10px; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: linear-gradient(180deg, #fffdf7, #f4eee2); }}
    .report-card span {{ color: var(--brass); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .report-card h3 {{ margin: 0; font-size: 20px; line-height: 1.14; }}
    .report-card p {{ margin: 0; color: #3f4d48; font-size: 14px; line-height: 1.5; }}
    .report-card strong {{ color: var(--ink); font-size: 13px; line-height: 1.45; }}
    .report-card a {{ font-weight: 900; }}
    .path-card, .country-tile {{ color: var(--ink); text-decoration: none; }}
    .path-card, .recommendation-card, .country-tile, .trust-card, .guide-card {{ min-width: 0; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }}
    .recommendation-card {{ padding: 0; overflow: hidden; }}
    .recommendation-card__visual {{ position: relative; height: clamp(168px, 16vw, 198px); display: block; overflow: hidden; background: #e8ede7; }}
    .recommendation-card__visual::after {{ content: ""; position: absolute; inset: 0; pointer-events: none; background: rgba(244, 238, 226, .08); }}
    .recommendation-card__image {{ width: 100%; height: 100%; display: block; object-fit: cover; filter: saturate(.72) contrast(.94) brightness(.97) sepia(.06); transition: transform .25s ease; }}
    .recommendation-card__visual:hover .recommendation-card__image {{ transform: scale(1.015); }}
    .recommendation-card__body {{ padding: 14px 16px 16px; }}
    .path-card {{ position: relative; border-top: 4px solid var(--path-accent, var(--brass)); transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }}
    .path-card:hover, .recommendation-card:hover, .country-tile:hover, .guide-card:hover {{ transform: translateY(-2px); border-color: rgba(95, 127, 114, .34); box-shadow: 0 14px 30px rgba(36, 49, 45, .08); }}
    .path-card span, .recommendation-card span, .country-tile span, .guide-card span {{ color: #806738; font-size: 12px; font-weight: 900; letter-spacing: .04em; text-transform: uppercase; }}
    .path-card span {{ display: inline-flex; align-items: center; gap: 8px; }}
    .path-card b {{ width: 26px; height: 26px; display: grid; place-items: center; border-radius: 50%; background: color-mix(in srgb, var(--path-accent, var(--brass)) 18%, white); color: var(--path-accent, var(--brass)); font-size: 11px; }}
    .path-card strong, .country-tile strong, .trust-card strong {{ display: block; margin: 8px 0; font-size: 18px; line-height: 1.12; }}
    .path-card p, .recommendation-card p, .country-tile p, .trust-card p, .guide-card p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .path-card em {{ display: inline-block; margin-top: 14px; color: var(--path-accent, var(--brass)); font-size: 13px; font-style: normal; font-weight: 900; }}
    .recommendation-card h3, .guide-card h3 {{ margin: 8px 0 4px; font-size: 18px; line-height: 1.12; }}
    .recommendation-card strong {{ display: block; margin: 12px 0 8px; font-size: 24px; }}
    .recommendation-card em {{ display: block; color: #3f4d48; font-size: 13px; font-style: normal; line-height: 1.45; }}
    .recommendation-card dl {{ display: grid; gap: 8px; margin: 12px 0 0; }}
    .recommendation-card dt {{ color: var(--brass); font-size: 10px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .recommendation-card dd {{ margin: 3px 0 0; color: var(--muted); font-size: 12px; line-height: 1.38; }}
    .recommendation-card summary {{ margin-top: 12px; cursor: pointer; color: var(--ink); font-size: 13px; font-weight: 900; }}
    .more-markets {{ display: flex; flex-wrap: wrap; gap: 7px 14px; margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--line); font-size: 13px; }}
    .more-markets span {{ color: var(--muted); font-weight: 800; }}
    .more-markets a {{ color: var(--ink); }}
    .method-compact {{ display: flex; align-items: center; justify-content: space-between; gap: 24px; }}
    .method-compact h2 {{ margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 4vw, 38px); }}
    .method-compact p {{ margin: 6px 0 0; color: var(--muted); }}
    .method-compact a {{ flex: none; font-weight: 800; }}
    .trust-card span {{ width: 34px; height: 34px; display: grid; place-items: center; margin-bottom: 12px; border-radius: 50%; background: #eef3f0; color: var(--deep); font-weight: 900; }}
    .cta-band {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 18px; align-items: center; padding: 26px; border-radius: 8px; background: var(--deep); color: #fffdf7; }}
    .cta-band h2 {{ margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 4vw, 40px); }}
    .cta-band p {{ max-width: 700px; margin: 8px 0 0; color: rgba(255, 253, 247, .78); }}
    .cta-band .primary-action {{ background: #fffdf7; color: var(--deep); }}
    .cta-band--light {{ margin-bottom: 28px; background: #eef4ef; color: var(--ink); border: 1px solid rgba(95, 127, 114, .25); }}
    .cta-band--light p {{ color: #45534e; }}
    .cta-band--light .primary-action {{ background: var(--eucalyptus); color: #fffdf7; }}
    a:focus-visible, button:focus-visible, select:focus-visible, summary:focus-visible {{ outline: 3px solid rgba(169, 138, 75, .55); outline-offset: 3px; }}
    .footer {{ padding: 26px 0 42px; color: var(--muted); }}
    .footer-grid {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(250px, 340px); gap: 24px; align-items: start; }}
    .footer nav {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }}
    .footer-signup {{ padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: rgba(255, 253, 247, .68); }}
    .footer-signup p {{ margin: 8px 0 12px; }}
    @media (max-width: 980px) {{
      .hero {{ min-height: auto; padding-bottom: 58px; }}
      .hero-grid {{ grid-template-columns: 1fr; }}
      .path-grid, .recommendation-grid, .country-grid, .trust-grid, .guide-grid, .explore-grid, .finder-grid, .finder-results, .inspired-band, .report-grid, .footer-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .explore-column:nth-child(3) {{ grid-column: 1 / -1; padding-left: 0; border-left: 0; }}
    }}
    @media (max-width: 640px) {{
      .shell {{ width: min(1160px, calc(100% - 28px)); }}
      .top-links {{ display: none; }}
      .mobile-menu {{ display: block; }}
      .brand-logo {{ width: 158px; max-width: 66vw; }}
      .hero-grid {{ gap: 18px; padding-top: 80px; }}
      .eyebrow {{ max-width: 330px; font-size: 11px; letter-spacing: .12em; }}
      h1 {{ max-width: min(100%, 362px); font-size: clamp(36px, 10vw, 48px); line-height: 1; overflow-wrap: anywhere; }}
      .lede {{ max-width: min(100%, 362px); margin-top: 18px; font-size: 16px; }}
      .hero-actions {{ gap: 10px; }}
      .hero-actions > .primary-action, .hero-secondary-actions {{ width: 100%; }}
      .hero-secondary-actions {{ display: grid; gap: 2px; }}
      .hero-secondary-actions a {{ width: 100%; min-height: 38px; }}
      .section {{ padding: 18px; }}
      .section--finder {{ padding: 20px; }}
      .finder-map-cue {{ width: 190px; height: 110px; opacity: .09; }}
      .section-header, .cta-band {{ display: block; }}
      .section-header h2 {{ max-width: 300px; font-size: 24px; line-height: 1.05; }}
      .section-header a, .cta-band a {{ margin-top: 14px; }}
      .path-grid, .recommendation-grid, .country-grid, .trust-grid, .guide-grid, .explore-grid, .finder-grid, .finder-results, .inspired-band, .report-grid, .footer-grid {{ grid-template-columns: 1fr; }}
      .recommendation-card__visual {{ height: 158px; }}
      .recommendation-card__image {{ height: 158px; }}
      .explore-column, .explore-column + .explore-column {{ grid-column: auto; padding: 0; border-left: 0; }}
      .explore-column + .explore-column {{ padding-top: 18px; border-top: 1px solid var(--line); }}
      .method-compact {{ display: block; }}
      .method-compact a {{ display: inline-block; margin-top: 12px; }}
      .inspired-visual {{ min-height: 230px; }}
      .atlas-visual {{ min-height: 140px; }}
    }}
  </style>
</head>
<body>
  <header class="hero" id="top">
    {topbar_nav_html()}
    <div class="shell hero-grid">
      <div>
        <p class="eyebrow">Independent overseas property research</p>
        <h1>Global Home Atlas</h1>
        <p class="lede">{escape(content["generated_intro"])}</p>
        {generated_link}
        <div class="hero-actions">
          <a class="primary-action" href="/{FIND_YOUR_FIT_SLUG}/" data-track="homepage_start_click" data-track-label="hero">Find my best-fit destinations</a>
          <nav class="hero-secondary-actions" aria-label="Explore Global Home Atlas">
            <a class="text-action" href="/guides/#country-selection" data-track="country_browse_click" data-track-label="hero">Browse countries</a>
            <a class="text-action" href="/{RETIREMENT_CALCULATOR_SLUG}/" data-track="retirement_calculator_open" data-track-label="hero">Calculate retirement needs</a>
            <a class="text-action" href="/{RETIREMENT_FINDER_SLUG}/">Find affordable retirement destinations</a>
            <a class="text-action" href="/methodology/" data-track="methodology_click" data-track-label="hero">View methodology</a>
          </nav>
        </div>
      </div>
    </div>
  </header>

  <main>
    <div class="shell">
      <section class="section section--finder" id="market-finder">
        <div class="finder-map-cue" aria-hidden="true"></div>
        <div class="section-header">
          <div>
            <h2>Find your destination fit</h2>
            <p>What do you want from your property? Choose a goal to see three destinations worth comparing.</p>
          </div>
        </div>
        <div class="finder-grid">
          <div class="finder-panel">
            <p class="finder-step">1. Choose your goal</p>
            <label for="finderGoal">What are you buying for?
              <select id="finderGoal">
                <option value="retirement">Retirement or lifestyle base</option>
                <option value="second-home">Second home abroad</option>
                <option value="investment">Investment returns</option>
                <option value="ownership">Straightforward ownership</option>
              </select>
            </label>
            <a class="secondary-action" id="finderDetailed" href="/{FIND_YOUR_FIT_SLUG}/?goal=retirement" data-track="fit_finder_open" data-track-label="market finder panel">Refine these matches</a>
          </div>
          <div class="finder-output">
            <p class="finder-step">2. Compare your matches</p>
            <div class="finder-results" id="finderResults" aria-live="polite"></div>
            <p class="finder-note">These are places to research first. Before buying, check local legal, tax, visa and property rules.</p>
          </div>
        </div>
      </section>

      <section class="section" id="recommendations">
        <div class="section-header">
          <div>
            <h2>Three destinations to start with</h2>
            <p>Well-rounded options for buyers who are still deciding where to look.</p>
          </div>
          <a href="/dashboard/" data-track="dashboard_open" data-track-label="recommendations">Compare all destinations</a>
        </div>
        <div class="recommendation-grid">
          {build_landing_recommendations(destinations)}
        </div>
        {build_landing_more_market_links(destinations)}
      </section>

      <section class="section" id="explore">
        <div class="section-header">
          <div>
            <h2>Explore the research</h2>
            <p>Browse by what you want to buy, where you want to look or what you need to learn.</p>
          </div>
        </div>
        <div class="explore-grid">
          {build_landing_explore_links(pages)}
        </div>
      </section>

      <section class="section" id="method">
        <div class="method-compact">
          <div>
            <h2>How we compare destinations</h2>
            <p>We look at ownership rules, realistic returns, daily life and resale potential.</p>
          </div>
          <a href="/research-standards/" data-track="trust_click" data-track-label="landing standards">Research standards</a>
        </div>
      </section>

      <section class="cta-band" id="conversion">
        <div>
          <h2>Want help narrowing your shortlist?</h2>
          <p>Tell us what you need and we’ll review the destinations on your list.</p>
        </div>
        <a class="primary-action" href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="landing cta">Review my shortlist</a>
      </section>
    </div>
  </main>

  <footer class="footer">
    <div class="shell">
      <div class="footer-grid">
        <div>
          <strong>Global Home Atlas</strong>
          <p>Independent research for overseas property decisions. Research only; verify legal, tax, immigration, and property advice locally.</p>
          <nav aria-label="Footer">
            <a href="/dashboard/">Research dashboard</a>
            <a href="/country-comparison/">Compare countries</a>
            <a href="/guides/">Guides</a>
            <a href="/methodology/">Methodology</a>
            <a href="/research-standards/">Research standards</a>
            <a href="/contact/">Contact</a>
          </nav>
        </div>
        <div class="footer-signup">
          <strong>Get destination updates</strong>
          <p>Ask to be notified when new destination research or country hubs are added.</p>
          <a class="secondary-action" href="mailto:{escape(CONTACT_EMAIL)}?subject=Global%20Home%20Atlas%20updates" data-track="contact_click" data-track-label="footer updates">Email {escape(CONTACT_EMAIL)}</a>
        </div>
      </div>
    </div>
  </footer>
  <script>
    (function () {{
      const finderData = {build_market_finder_data(destinations)};
      const select = document.getElementById("finderGoal");
      const results = document.getElementById("finderResults");
      const detailed = document.getElementById("finderDetailed");
      function escapeHtml(value) {{
        return String(value || "").replace(/[&<>"']/g, (char) => ({{
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;"
        }}[char]));
      }}
      function firstItem(items, fallback) {{
        return (items && items.length ? items[0] : fallback) || "";
      }}
      function finderThumbnail(item) {{
        if (!item.image) return '<div class="finder-result__thumb finder-result__thumb--map" aria-hidden="true"></div>';
        return `<div class="finder-result__thumb"><img src="${{escapeHtml(item.image)}}" alt="${{escapeHtml(item.imageAlt)}}" width="600" height="400" loading="lazy" decoding="async"></div>`;
      }}
      function renderFinder() {{
        if (!select || !results) return;
        const route = select.value;
        const picks = finderData[route] || [];
        if (detailed) detailed.href = "/find-your-fit/?goal=" + encodeURIComponent(route);
        results.innerHTML = picks.map((item, index) => `
          <article class="finder-result">
            ${{finderThumbnail(item)}}
            <span>${{index + 1}}</span>
            <h3><a href="${{escapeHtml(item.href)}}" data-track="destination_click" data-track-label="finder ${{escapeHtml(item.name)}}">${{escapeHtml(item.name)}}</a></h3>
            <p>${{escapeHtml(item.country)}} · ${{escapeHtml(item.score)}}/5</p>
            <p class="finder-signal"><strong>Good fit</strong> ${{escapeHtml(firstItem(item.reasonBullets, item.reason))}}</p>
            <p class="finder-signal"><strong>Watch out</strong> ${{escapeHtml(firstItem(item.watchBullets, item.watch))}}</p>
            <a class="card-link" href="${{escapeHtml(item.href)}}" data-track="destination_click" data-track-label="finder cta ${{escapeHtml(item.name)}}">View destination</a>
          </article>
        `).join("");
        if (window.GHA) window.GHA.track("market_finder_change", {{ goal: route, result_count: picks.length }});
      }}
      if (select) select.addEventListener("change", renderFinder);
      renderFinder();
    }})();
  </script>
  {analytics_event_script()}
</body>
</html>
"""


def metric_value(dest: dict, dimension_key: str) -> float:
    for item in dest.get("decision_dimensions", []):
        if item.get("key") == dimension_key:
            return float(item.get("score", 0) or 0)
    return 0


def build_seo_destination_table(destinations: list[dict]) -> str:
    rows = []
    for dest in destinations:
        rows.append(
            f"""
            <tr>
              <td><strong>{escape(dest["name"])}</strong><br><span>{escape(dest.get("country") or "")}</span></td>
              <td>{dest.get("decision_score", 0):.1f}</td>
              <td>{money(dest.get("usd_per_m2"))}/m2</td>
              <td>{escape(dest.get("net_yield_estimate") or "n/a")}</td>
              <td>{metric_value(dest, "ownership_clarity"):.1f}/5</td>
              <td>{metric_value(dest, "retirement_fit"):.1f}/5</td>
              <td>{escape(dest.get("panel_verdict") or "")}</td>
            </tr>
            """.rstrip()
        )
    return f"""
      <div class="seo-table-wrap">
        <table class="seo-table">
          <thead>
            <tr>
              <th>Destination</th>
              <th>Score</th>
              <th>Entry</th>
              <th>Yield</th>
              <th>Ownership</th>
              <th>Retirement</th>
              <th>Committee read</th>
            </tr>
          </thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </div>
    """


def build_seo_destination_cards(destinations: list[dict]) -> str:
    cards = []
    for dest in destinations[:6]:
        cards.append(
            f"""
            <article class="seo-destination-card">
              <div>
                <span>#{dest["rank"]} global scorecard</span>
                <h3><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></h3>
                <p>{escape(dest.get("panel_summary") or "")}</p>
              </div>
              <dl>
                <div><dt>Decision score</dt><dd>{dest.get("decision_score", 0):.1f}/5</dd></div>
                <div><dt>Entry benchmark</dt><dd>{money(dest.get("usd_per_m2"))}/m2</dd></div>
                <div><dt>Ownership</dt><dd>{metric_value(dest, "ownership_clarity"):.1f}/5</dd></div>
                <div><dt>Exit liquidity</dt><dd>{metric_value(dest, "exit_liquidity"):.1f}/5</dd></div>
              </dl>
            </article>
            """.rstrip()
        )
    return "\n".join(cards)


def build_faq_html(faqs: list[tuple[str, str]]) -> str:
    return "\n".join(
        f"""
        <details class="faq-item">
          <summary>{escape(question)}</summary>
          <p>{escape(answer)}</p>
        </details>
        """
        for question, answer in faqs
    )


def is_japan_retirement_guide(page: dict) -> bool:
    return page.get("slug") == "japan-retirement-property-foreign-buyers"


def is_spain_retirement_guide(page: dict) -> bool:
    return page.get("slug") == "spain-retirement-property-foreign-buyers"


def is_editorial_retirement_guide(page: dict) -> bool:
    return is_japan_retirement_guide(page) or is_spain_retirement_guide(page)


def japan_retirement_fit_html() -> str:
    return """
          <section class="seo-section" id="fit">
            <h2>Who Japan suits</h2>
            <p><strong>Japan is a strong fit</strong> for buyers who already have a credible residence route, value safety, transport, food and healthcare access, can operate in a Japanese-language administrative environment, and prefer lifestyle utility over aggressive yield.</p>
            <p><strong>Look elsewhere first</strong> if the property is expected to create residency, easy non-resident leverage is essential, short-term-rental income must carry the investment, or family members need a simple dependent pathway.</p>
            <p>Before making an offer, complete the immigration, financing, tax, hazard, building, management and exit checks in that order. A technically purchasable property is not necessarily a workable retirement plan.</p>
          </section>
    """


def japan_retirement_overview_html() -> str:
    return f"""
          <section class="seo-section" id="residency">
            <p class="seo-eyebrow japan-section-label">Start here</p>
            <h2>Buying property does not give you residency</h2>
            <p>Foreign buyers can generally acquire and register a home in Japan, but ownership does not create a visa, a status of residence, permanent residency, or access to public healthcare. Establish a lawful long-stay route before treating a purchase as a retirement home.</p>
            <p>Japan does not have a general retirement visa. The closest official option for some affluent long-stay visitors is the designated-activities route for sightseeing and recreation. It is limited to nationals of visa-waiver countries or regions, requires savings of at least ¥30 million for the applicant and spouse, normally permits six months, and can reach a maximum of one year after an extension. Dependent children cannot accompany the applicant under this route. See the <a href="https://www.mofa.go.jp/ca/fna/page22e_000738.html" rel="noopener noreferrer">Ministry of Foreign Affairs requirements</a> and the <a href="https://www.moj.go.jp/isa/applications/status/index.html?language=eng" rel="noopener noreferrer">Immigration Services Agency status list</a>.</p>
            <p><strong>Decision rule:</strong> do not buy for full-time retirement until an immigration professional has confirmed the residence path, its renewal limits, and whether a spouse or dependent can use the same plan.</p>
          </section>

          {japan_retirement_fit_html()}

          <section class="seo-section" id="owner-changes">
            <h2>What changed for foreign owners in 2026</h2>
            <h3>Non-resident acquisition reporting</h3>
            <p>Under the Foreign Exchange and Foreign Trade Act, a non-resident who acquires Japanese real estate or a right in it generally must report the acquisition to the Minister of Finance through the Bank of Japan within 20 days. The report is in Japanese and may be filed by a Japan-based agent. Confirm the current scope and exemptions with the <a href="https://www.mof.go.jp/english/policy/international_policy/real_property/index.html" rel="noopener noreferrer">Ministry of Finance</a>.</p>
            <h3>Owner details must stay current</h3>
            <p>From April 2026, registered owners who change their name or address are required to apply for an update within two years. Overseas owners should agree in writing who will monitor notices and handle registration changes. See the <a href="https://www.moj.go.jp/EN/MINJI/m_minji07_00004.html" rel="noopener noreferrer">Ministry of Justice guidance</a>.</p>
            <h3>Rules remain under review</h3>
            <p>The Japanese government is continuing to review how foreign land acquisitions should be recorded and governed. That does not mean a general foreign-buyer ban is in force, but it makes a current legal check essential before exchange and closing. Follow the <a href="https://www.cas.go.jp/jp/seisaku/symbiotic_society/index.html" rel="noopener noreferrer">Cabinet Secretariat review</a>.</p>
          </section>

          <section class="seo-section" id="costs">
            <h2>Financing and ownership costs</h2>
            <p>Do not assume that clear ownership means easy financing. A non-resident without Japanese income or a domestic credit history may face a smaller lender pool, lower loan-to-value limits, additional guarantor requirements, or a cash-only transaction. Obtain written lending terms before making a non-refundable commitment.</p>
            <p>Budget separately for the purchase price, brokerage and legal support, registration and acquisition taxes, insurance, repairs, condominium or resort management fees, annual fixed-asset costs, and eventual sale costs. Japan taxes property at acquisition, during ownership, and on disposal; the applicable reliefs depend on the buyer, asset, use and date. Start with the <a href="https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html" rel="noopener noreferrer">Ministry of Land property-tax overview</a>, then obtain a transaction-specific estimate from a Japanese tax adviser.</p>
            <p><strong>Decision rule:</strong> compare five-year total cash outlay rather than the listing price alone, and keep a separate reserve for building and equipment replacement.</p>
          </section>

          <section class="seo-section" id="practicality">
            <h2>Retirement practicality beyond the purchase</h2>
            <h3>Healthcare follows residence status</h3>
            <p>Owning a home does not itself create eligibility for Japan's public health-insurance system. Eligibility depends on residence and enrolment rules. Confirm coverage before moving and maintain appropriate private or travel insurance for any period outside the public system. The <a href="https://www.mhlw.go.jp/stf/newpage_21539.html" rel="noopener noreferrer">Ministry of Health guidance</a> identifies categories, including short-stay foreign visitors, who are not eligible for National Health Insurance.</p>
            <h3>Earthquake, flood and building diligence</h3>
            <p>Review the property's structural survey, seismic standard and retrofit history, soil and slope conditions, flood, tsunami and landslide exposure, evacuation access, insurance availability, and the condition of roofs, waterproofing, plumbing and heating. Check the national <a href="https://disaportal.gsi.go.jp/" rel="noopener noreferrer">hazard-map portal</a> and the municipality's own maps; national screening does not replace an asset-level inspection.</p>
            <h3>Condominium and absentee-owner governance</h3>
            <p>For an apartment, read the management bylaws, reserve-fund balance, major-repair plan, meeting minutes, arrears, litigation, pet and renovation rules, and any restriction on short-term letting. An overseas owner also needs a reliable domestic contact or manager. MLIT publishes a <a href="https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf" rel="noopener noreferrer">guide for foreign condominium owners</a>.</p>
            <h3>Short-term rentals are regulated</h3>
            <p>Under the national private-lodging route, notified minpaku operations are capped at 180 days a year. Municipal ordinances and condominium rules can be tighter, and hotel or ryokan licensing follows a different route. Verify the exact property before underwriting any income. See the <a href="https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html" rel="noopener noreferrer">Japan Tourism Agency overview</a>.</p>
          </section>
    """


JAPAN_RETIREMENT_DESTINATION_GUIDANCE = {
    "fukuoka-itoshima": {
        "best_for": "Year-round living with airport, healthcare and city services",
        "daily_life": "Best all-round retirement base of this shortlist",
        "diligence": "Flood and tsunami maps, apartment reserves, transport needs in coastal Itoshima",
        "rental": "Prefer long-stay demand; verify any short-stay use building by building",
    },
    "hakone-izu": {
        "best_for": "Tokyo-adjacent second-home or part-time retirement use",
        "daily_life": "Strong leisure access, but car and slope practicality vary",
        "diligence": "Volcanic, landslide and flood exposure, older homes, onsen rights and maintenance",
        "rental": "Treat income as secondary unless the property has a compliant operator",
    },
    "hakuba": {
        "best_for": "Active alpine lifestyle with professional local management",
        "daily_life": "Seasonal resort rather than a default year-round retirement base",
        "diligence": "Snow load, heating, winter access, staffing, building condition and operating permissions",
        "rental": "Operator-dependent and seasonal; stress-test owner-use conflicts and all costs",
    },
    "niseko": {
        "best_for": "Premium resort use for buyers comfortable with high carrying costs",
        "daily_life": "Internationally accessible in winter, less complete for ordinary retirement needs",
        "diligence": "Service charges, operator contract, owner-use limits, construction quality and resale depth",
        "rental": "Do not rely on headline winter revenue; model management, vacancy and shoulder season",
    },
}


def japan_retirement_comparison_html(destinations: list[dict]) -> str:
    rows = []
    for dest in destinations:
        guidance = JAPAN_RETIREMENT_DESTINATION_GUIDANCE[dest["id"]]
        rows.append(
            f"""
            <tr>
              <td><strong><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></strong></td>
              <td>{escape(guidance["best_for"])}</td>
              <td>{escape(guidance["daily_life"])}</td>
              <td>{escape(guidance["diligence"])}</td>
              <td>{escape(guidance["rental"])}</td>
            </tr>
            """.rstrip()
        )
    return f"""
          <section class="seo-section" id="comparison">
            <h2>Four Japanese destinations to compare</h2>
            <p>Choose the type of retirement life before the property. Fukuoka and Itoshima provide the strongest year-round base; Hakone and Izu suit repeat use near Tokyo; Hakuba and Niseko are specialist resort choices that demand stronger management and seasonal-risk tolerance.</p>
            <div class="seo-table-wrap">
              <table class="seo-table">
                <thead><tr><th>Destination</th><th>Best for</th><th>Daily-life read</th><th>Primary diligence</th><th>Rental stance</th></tr></thead>
                <tbody>{"".join(rows)}</tbody>
              </table>
            </div>
          </section>
    """


def japan_retirement_destination_notes_html(destinations: list[dict]) -> str:
    cards = []
    for dest in destinations:
        guidance = JAPAN_RETIREMENT_DESTINATION_GUIDANCE[dest["id"]]
        cards.append(
            f"""
            <article class="seo-destination-card">
              <div>
                <span>{escape(dest.get("country") or "Japan")}</span>
                <h3><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></h3>
                <p>{escape(dest.get("panel_summary") or "")}</p>
              </div>
              <dl>
                <div><dt>Best for</dt><dd>{escape(guidance["best_for"])}</dd></div>
                <div><dt>Verify first</dt><dd>{escape(guidance["diligence"])}</dd></div>
              </dl>
            </article>
            """.rstrip()
        )
    return f"""
          <section class="seo-section">
            <h2>Destination notes for serious buyers</h2>
            <div class="seo-card-grid">{"".join(cards)}</div>
          </section>
    """


def japan_retirement_references_html() -> str:
    return """
          <section class="seo-section" id="sources">
            <h2>References and update policy</h2>
            <p>Legal and administrative claims in this guide use Japanese government sources. Rules can change, and local ordinances or building bylaws may be stricter than national rules. Recheck every linked source and obtain current professional advice before signing.</p>
            <ul>
              <li><a href="https://www.mofa.go.jp/ca/fna/page22e_000738.html" rel="noopener noreferrer">Ministry of Foreign Affairs: long stay for sightseeing and recreation</a></li>
              <li><a href="https://www.mof.go.jp/english/policy/international_policy/real_property/index.html" rel="noopener noreferrer">Ministry of Finance: non-resident real-property reporting</a></li>
              <li><a href="https://www.moj.go.jp/EN/MINJI/m_minji07_00004.html" rel="noopener noreferrer">Ministry of Justice: registration obligations from 2026</a></li>
              <li><a href="https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html" rel="noopener noreferrer">MLIT: property-tax overview</a></li>
              <li><a href="https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf" rel="noopener noreferrer">National Tax Agency: non-resident tax when buying or selling real estate</a></li>
              <li><a href="https://www.mlit.go.jp/report/press/totikensangyo13_hh_000269.html" rel="noopener noreferrer">MLIT: transaction, registration, tax and planning systems</a></li>
              <li><a href="https://www.mlit.go.jp/totikensangyo/const/sosei_const_fr3_000074.html" rel="noopener noreferrer">MLIT: flood-hazard maps in the Important Matters Explanation</a></li>
              <li><a href="https://www.mhlw.go.jp/content/12400000/001406614.pdf" rel="noopener noreferrer">Ministry of Health: health insurance for foreign residents</a></li>
              <li><a href="https://disaportal.gsi.go.jp/" rel="noopener noreferrer">Geospatial Information Authority: national hazard-map portal</a></li>
              <li><a href="https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf" rel="noopener noreferrer">MLIT: guide for foreign condominium owners</a></li>
              <li><a href="https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html" rel="noopener noreferrer">Japan Tourism Agency: Private Lodging Business Act</a></li>
              <li><a href="https://faq.japan-travel.jnto.go.jp/en/plan/airport-access/fukuoka-airport/" rel="noopener noreferrer">JNTO: Fukuoka Airport access</a></li>
              <li><a href="https://www.stat.go.jp/english/data/nenkan/74nenkan/1431-20.html" rel="noopener noreferrer">Statistics Bureau: regional consumer-price comparisons</a></li>
            </ul>
          </section>
    """


SPAIN_RETIREMENT_DESTINATION_GUIDANCE = {
    "valencia": {
        "best_for": "Balanced year-round city life with beach access and everyday services",
        "daily_life": "The broadest retirement base in this shortlist",
        "diligence": "Neighborhood heat, flood exposure, community rules and local rental permissions",
        "rental": "Prefer durable residential demand over a tourist-only income case",
    },
    "malaga-costa-del-sol": {
        "best_for": "International retirement infrastructure, flights and established coastal communities",
        "daily_life": "Easy to enter socially, but the coast varies sharply by municipality",
        "diligence": "Planning history, water and heat exposure, community approval and municipal tourist-use rules",
        "rental": "Underwrite building by building; do not assume an existing holiday listing can continue",
    },
    "costa-brava-girona": {
        "best_for": "Catalan culture, landscape and a quieter second-city or coastal rhythm",
        "daily_life": "Compelling for selective locations, more seasonal away from Girona",
        "diligence": "Winter services, car dependence, coastal planning, wildfire and flood exposure",
        "rental": "Treat licensing and seasonality as constraints, not upside assumptions",
    },
    "mallorca": {
        "best_for": "Premium island living with a deep international buyer and service ecosystem",
        "daily_life": "Highly usable where year-round services remain close",
        "diligence": "Entry price, water and heat resilience, legal building status, community rules and island logistics",
        "rental": "Do not buy on a holiday-rental thesis until the exact asset and permissions are verified",
    },
}


def spain_retirement_fit_html() -> str:
    return """
          <section class="seo-section" id="fit">
            <h2>Who Spain suits</h2>
            <p><strong>Spain is a strong fit</strong> for buyers who can establish an independent residence route, want a genuine year-round social and healthcare environment, accept region-by-region tax and rental rules, and value daily life more than maximum property yield.</p>
            <p><strong>Look elsewhere first</strong> if the purchase is expected to create residency, the financial case depends on unrestricted short-term letting, the buyer cannot tolerate summer heat or water constraints, or the plan requires simple tax treatment across several countries.</p>
            <p>Before offering, confirm residence, tax residence, healthcare, financing, title, planning status, community rules, hazards, rental permission and exit demand—in that order. A home can be legally purchasable while the retirement plan around it remains unworkable.</p>
          </section>
    """


def spain_retirement_overview_html() -> str:
    return f"""
          <section class="seo-section" id="residency">
            <p class="seo-eyebrow editorial-section-label">Start here</p>
            <h2>Buying property does not give you residency</h2>
            <p>Foreign buyers can generally acquire Spanish property, but a deed does not create a visa, residence authorization, permanent residence, public-healthcare entitlement or tax advantage. Spain's investor-residence route—including the former real-estate route—<a href="https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/vivienda-agenda-urbana/Paginas/2025/020425-fin-golden-visa.aspx" rel="noopener noreferrer">ended on 3 April 2025</a>. Treat immigration and property as separate workstreams.</p>
            <p>EU, EEA and Swiss citizens use free-movement rules and registration procedures. For many non-EU retirees, the relevant starting point is Spain's <a href="https://www.inclusion.gob.es/en/web/migraciones/w/autorizacion-inicial-de-residencia-temporal-no-lucrativa" rel="noopener noreferrer">non-lucrative residence</a>, which permits residence without work when the applicant meets the current financial, insurance and other requirements. It is not a property-owner visa, and individual circumstances, family composition and renewal plans matter.</p>
            <p><strong>Decision rule:</strong> do not reserve a retirement home until an immigration adviser has confirmed the route, documentary requirements, renewal conditions and whether each accompanying family member qualifies.</p>
          </section>

          {spain_retirement_fit_html()}

          <section class="seo-section" id="owner-changes">
            <h2>What changed in 2025 and 2026</h2>
            <h3>Property investment no longer creates a residence route</h3>
            <p>The end of Spain's investor visas is not a temporary pause. New buyers must qualify under a different immigration category. Do not rely on property advertising that still connects a purchase price to Spanish residence.</p>
            <h3>New tourist use may need community approval</h3>
            <p>For tourist activity beginning after 3 April 2025 in a building governed by the Horizontal Property Law, the owner should expect to prove express <strong>three-fifths approval</strong> from both owners and participation quotas, subject to the exact facts and transitional position. A January 2026 registry decision illustrates the rule and the narrow protection for activity already validly operating before the change. See the <a href="https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-11152" rel="noopener noreferrer">official BOE decision</a>.</p>
            <h3>The national short-rental register changed again in 2026</h3>
            <p>Spain introduced a national registration procedure for short-duration accommodation under Royal Decree 1312/2024. The Supreme Court's judgment of <strong>19 May 2026</strong> annulled that national registration procedure and related references; the consolidated text now marks the affected articles as annulled. This does not deregulate holiday letting: regional and municipal rules remain, alongside planning, consumer and community-of-owners controls. Check the <a href="https://www.boe.es/boe/dias/2026/06/08/" rel="noopener noreferrer">Supreme Court publication</a> and the current <a href="https://www.boe.es/buscar/act.php?id=BOE-A-2024-26931" rel="noopener noreferrer">consolidated decree</a> immediately before underwriting rental income.</p>
          </section>

          <section class="seo-section" id="costs">
            <h2>Financing and ownership costs</h2>
            <p>Foreign-buyer financing exists, but residence status, euro income, age, credit history, property type and lender policy determine the practical terms. Obtain a written credit decision before paying a deposit whose return depends on financing. Model currency exposure separately if pension or portfolio income is not in euros.</p>
            <p>For tax, separate new from resale property and separate national rules from autonomous-community rates. The Tax Agency states that a new home purchased from a developer is generally subject to <a href="https://sede.agenciatributaria.gob.es/Sede/iva/iva-operaciones-inmobiliarias/compro-vivienda-tengo-que-pagar-itp.html" rel="noopener noreferrer">10% VAT</a>, while a used home is generally subject to transfer tax administered where the property is located. Add notary, registry, legal, valuation, mortgage, insurance, community, maintenance and eventual disposal costs; obtain a location- and buyer-specific closing statement rather than applying one national percentage.</p>
            <p>Non-resident owners may owe Spanish tax on rent, gains and imputed income from urban property. When a buyer acquires Spanish property from a non-resident seller, the Tax Agency says the buyer generally must retain and pay <a href="https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/irnr-sin-establecimiento-permanente/retenciones-irnr-sin-establecimiento-permanente/retencion-adquirente-inmueble.html" rel="noopener noreferrer">3% of the agreed consideration</a> as a payment on account for the seller. Residence planning also changes the frame: a person may become Spanish tax resident by spending <a href="https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/residencia-personas-fisicas-juridicas/persona-fisica-residente-espana.html" rel="noopener noreferrer">more than 183 days</a> in Spain during the calendar year or by locating the main base of economic interests there.</p>
            <p><strong>Decision rule:</strong> compare five-year cash outlay after tax, financing, community fees and maintenance, then commission cross-border tax advice before deciding how many days to spend in Spain.</p>
          </section>

          <section class="seo-section" id="practicality">
            <h2>Retirement practicality beyond the purchase</h2>
            <h3>Healthcare follows residence and entitlement</h3>
            <p>Property ownership does not itself open Spain's National Health System. Social Security guidance ties publicly funded entitlement to Spanish or qualifying foreign residence, social-security status, international coordination or another legal basis. Some economically inactive residents can use an S1, private insurance or a regional special agreement depending on their circumstances. Confirm the route before moving with the <a href="https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/PrestacionesPensionesTrabajadores/10938/30476/177505" rel="noopener noreferrer">Spanish Social Security eligibility guidance</a> and the relevant autonomous-community health service.</p>
            <h3>Flood, wildfire and heat diligence</h3>
            <p>Spain's retirement appeal is inseparable from climate. Screen river, flash-flood and coastal exposure on the national <a href="https://www.miteco.gob.es/es/agua/temas/gestion-de-los-riesgos-de-inundacion/snczi.html" rel="noopener noreferrer">flood-zone mapping system</a>, then check municipal plans, building access, drainage, previous losses and insurability. In wooded or peri-urban areas, inspect wildfire access and defensible space. For every location, test summer heat, shading, ventilation, water security and cooling costs rather than relying on an annual climate average.</p>
            <h3>Planning and community records matter</h3>
            <p>Obtain an up-to-date land-registry extract, compare it with the cadastre and physical property, confirm planning and occupancy status, and review community statutes, minutes, accounts, reserve position, works and litigation. Spain's registrars provide an English-language <a href="https://www.registradores.org/gl/documentacion-y-descargas/guias-rapidas" rel="noopener noreferrer">guide to buying property</a> and translated registry information for international users.</p>
            <h3>Rental permission is asset-specific</h3>
            <p>A tourist-use registration in one region or municipality says little about another. Before assigning value to income, confirm the current autonomous-community regime, municipal zoning, building statutes, community approval, occupancy documentation, platform rules and whether any historic authorization transfers with the property. Underwrite the home first as a retirement asset; treat permitted rental as optionality.</p>
          </section>
    """


def spain_retirement_comparison_html(destinations: list[dict]) -> str:
    rows = []
    for dest in destinations:
        guidance = SPAIN_RETIREMENT_DESTINATION_GUIDANCE[dest["id"]]
        rows.append(
            f"""
            <tr>
              <td><strong><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></strong></td>
              <td>{escape(guidance["best_for"])}</td>
              <td>{escape(guidance["daily_life"])}</td>
              <td>{escape(guidance["diligence"])}</td>
              <td>{escape(guidance["rental"])}</td>
            </tr>
            """.rstrip()
        )
    return f"""
          <section class="seo-section" id="comparison">
            <h2>Four Spanish destinations to compare</h2>
            <p>Choose the retirement pattern before the property. Valencia offers the most balanced year-round city case; Málaga and the Costa del Sol offer the deepest international retirement infrastructure; Costa Brava and Girona suit a more selective Catalan rhythm; Mallorca is the premium island choice when carrying costs and logistics remain comfortable.</p>
            <div class="seo-table-wrap">
              <table class="seo-table">
                <thead><tr><th>Destination</th><th>Best for</th><th>Daily-life read</th><th>Primary diligence</th><th>Rental stance</th></tr></thead>
                <tbody>{"".join(rows)}</tbody>
              </table>
            </div>
          </section>
    """


def spain_retirement_references_html() -> str:
    return """
          <section class="seo-section" id="sources">
            <h2>References and update policy</h2>
            <p>Legal and administrative claims in this guide use Spanish government, EU, tax-agency, Social Security, land-registry, airport and BOE sources. Spain divides important powers among the state, autonomous communities, municipalities and communities of owners. Recheck every linked source and the exact property's local position before signing. This guide was substantively reviewed on 21 August 2026.</p>
            <ul>
              <li><a href="https://www.inclusion.gob.es/en/web/migraciones/w/autorizacion-inicial-de-residencia-temporal-no-lucrativa" rel="noopener noreferrer">Ministry of Inclusion: initial non-lucrative temporary residence</a></li>
              <li><a href="https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/vivienda-agenda-urbana/Paginas/2025/020425-fin-golden-visa.aspx" rel="noopener noreferrer">Government of Spain: investor residence ended on 3 April 2025</a></li>
              <li><a href="https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/residencia-personas-fisicas-juridicas/persona-fisica-residente-espana.html" rel="noopener noreferrer">Tax Agency: individual tax residence in Spain</a></li>
              <li><a href="https://sede.agenciatributaria.gob.es/Sede/vivienda-otros-inmuebles/no-residentes-tributacion-inmuebles.html" rel="noopener noreferrer">Tax Agency: taxation of property owned by non-residents</a></li>
              <li><a href="https://sede.agenciatributaria.gob.es/Sede/iva/iva-operaciones-inmobiliarias/compro-vivienda-tengo-que-pagar-itp.html" rel="noopener noreferrer">Tax Agency: VAT or transfer tax when buying a home</a></li>
              <li><a href="https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/irnr-sin-establecimiento-permanente/retenciones-irnr-sin-establecimiento-permanente/retencion-adquirente-inmueble.html" rel="noopener noreferrer">Tax Agency: purchaser withholding when the seller is non-resident</a></li>
              <li><a href="https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/PrestacionesPensionesTrabajadores/10938/30476/177505" rel="noopener noreferrer">Spanish Social Security: healthcare entitlement and requirements</a></li>
              <li><a href="https://www.sanidad.gob.es/servCiudadanos/internacional/convenioEspecial.htm" rel="noopener noreferrer">Ministry of Health: special healthcare agreement</a></li>
              <li><a href="https://www.registradores.org/gl/documentacion-y-descargas/guias-rapidas" rel="noopener noreferrer">Registradores de España: guide to buying property in Spain</a></li>
              <li><a href="https://sede.registradores.org/site/propiedad?lang=en_EN" rel="noopener noreferrer">Land Registry: extracts and information for international users</a></li>
              <li><a href="https://www.registradores.org/es/web/guest/-/el-precio-medio-de-la-vivienda-crece-un-2-2-en-el-%C3%BAltimo-trimestre-del-a%C3%B1o-y-alcanza-el-9-5-anual-en-2025" rel="noopener noreferrer">Registradores de España: 2025 registered housing-market statistics</a></li>
              <li><a href="https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-11152" rel="noopener noreferrer">BOE: community approval for new tourist-use activity</a></li>
              <li><a href="https://www.boe.es/boe/dias/2026/06/08/" rel="noopener noreferrer">BOE: Supreme Court judgment of 19 May 2026</a></li>
              <li><a href="https://www.boe.es/buscar/act.php?id=BOE-A-2024-26931" rel="noopener noreferrer">BOE: consolidated short-duration accommodation decree</a></li>
              <li><a href="https://www.miteco.gob.es/es/agua/temas/gestion-de-los-riesgos-de-inundacion/snczi.html" rel="noopener noreferrer">MITECO: national flood-zone mapping system</a></li>
              <li><a href="https://www.aena.es/en/valencia/airlines-destinations/airport-destinations.html" rel="noopener noreferrer">Aena: Valencia Airport destinations</a></li>
              <li><a href="https://www.aena.es/en/malaga-costa-del-sol/airlines-and-destinations/airport-destinations.html" rel="noopener noreferrer">Aena: Málaga–Costa del Sol Airport destinations</a></li>
              <li><a href="https://www.aena.es/en/palma-de-mallorca/airlines-and-destinations/airport-destinations.html" rel="noopener noreferrer">Aena: Palma de Mallorca Airport destinations</a></li>
            </ul>
          </section>
    """


def seo_overview_html(page: dict, selected: list[dict]) -> str:
    if is_japan_retirement_guide(page):
        return japan_retirement_overview_html()
    if is_spain_retirement_guide(page):
        return spain_retirement_overview_html()
    country_count = len({item.get("country") for item in selected if item.get("country")})
    return f"""
          <section class="seo-section">
            <h2>How to Read This Shortlist</h2>
            <p><strong>Credibility note:</strong> this page compares {len(selected)} destinations across {country_count} countries using a consistent {len(DIMENSIONS)}-dimension model. It is research-grade destination intelligence, not financial, legal, tax, immigration, or transaction advice.</p>
            <p>The right answer for {escape(page["keyword"])} is rarely the destination with the prettiest photos or the highest advertised yield. A global buyer needs a place that can survive legal review, repeated use, currency shifts, maintenance surprises, and a future resale process. Global Home Atlas ranks destinations through ten decision dimensions: lifestyle magnetism, global access, ownership clarity, regulatory safety, rental profit, capital upside, retirement fit, exit liquidity, foreigner fit, and value entry.</p>
            <p>That weighting is designed for affluent global citizens who may use one property for several jobs over time. A home can begin as a vacation base, become a semi-retirement address, then eventually need to rent or sell. The best destinations on this page are therefore not selected only for near-term excitement. They are selected because the evidence points to a more durable combination of livability, practicality, and investment defensibility.</p>
            <p>Use this page as a first-pass filter. It narrows the research field, highlights where each destination is strong, and shows which tradeoffs need professional verification. Before buying, confirm title, taxes, foreign-buyer rules, visa status, insurance, building condition, local rental permits, manager quality, and resale comparables with independent local advisers.</p>
          </section>
    """


def seo_comparison_html(page: dict, selected: list[dict], top: dict, runner_up: dict) -> str:
    if is_japan_retirement_guide(page):
        return japan_retirement_comparison_html(selected)
    if is_spain_retirement_guide(page):
        return spain_retirement_comparison_html(selected)
    return f"""
          <section class="seo-section" id="comparison">
            <h2>Best Destinations to Compare First</h2>
            <p>For this search, the strongest candidates are {escape(top["name"])} and {escape(runner_up["name"])} because they balance high decision scores with practical ownership and lifestyle use. The table below keeps the comparison deliberately concrete: entry benchmark, yield context, ownership clarity, retirement fit, and the committee read. These are the variables most likely to change a real buy/no-buy decision.</p>
            {build_seo_destination_table(selected)}
          </section>
    """


def seo_destination_notes_html(page: dict, selected: list[dict]) -> str:
    if is_editorial_retirement_guide(page):
        return ""
    return f"""
          <section class="seo-section">
            <h2>Destination Notes for Serious Buyers</h2>
            <div class="seo-card-grid">
              {build_seo_destination_cards(selected)}
            </div>
          </section>
    """


def seo_decision_framework_html(page: dict) -> str:
    if is_editorial_retirement_guide(page):
        return ""
    return """
          <section class="seo-section">
            <h2>Decision Framework</h2>
            <h3>1. Start with ownership clarity</h3>
            <p>Foreign buyers should eliminate markets where the legal structure is hard to explain, hard to finance, or heavily dependent on informal assumptions. A beautiful asset can become a poor decision if land rights, permits, taxes, or resale procedures are unclear. The ownership score in this guide is therefore intentionally prominent.</p>
            <h3>2. Underwrite lifestyle as demand</h3>
            <p>Lifestyle is not decoration. Food, healthcare, airport access, safety, climate, and year-round activity are the forces that make a place usable by the owner and attractive to future buyers or tenants. A market with repeated lifestyle demand has more ways to work if the original plan changes.</p>
            <h3>3. Treat yield as a stress test</h3>
            <p>Rental income should offset risk, not justify ignoring it. Net yield estimates need to survive management fees, vacancy, repairs, taxes, furnishing, platform costs, insurance, and regulatory changes. A lower but cleaner yield in a liquid market can be superior to a headline yield that depends on aggressive occupancy or fragile short-term-rental permissions.</p>
            <h3>4. Plan the exit before entry</h3>
            <p>Affluent buyers often focus on acquisition quality and underweight future liquidity. Exit matters because family plans, residency rules, tax regimes, health needs, and currency preferences can change. Markets with local, regional, and international buyer demand usually deserve a premium over thin markets with one buyer profile.</p>
          </section>
    """


def seo_references_html(page: dict) -> str:
    if is_japan_retirement_guide(page):
        return japan_retirement_references_html()
    if is_spain_retirement_guide(page):
        return spain_retirement_references_html()
    return ""


def schema_for_page(page: dict, canonical: str) -> list[dict]:
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": page_url(GUIDE_HUB_SLUG)},
            {"@type": "ListItem", "position": 3, "name": page["h1"], "item": canonical},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page["h1"],
        "url": canonical,
        "description": page["description"],
        "dateModified": date.today().isoformat(),
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
    }
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": page["h1"],
        "description": page["description"],
        "url": canonical,
        "dateModified": date.today().isoformat(),
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
        "mainEntityOfPage": canonical,
    }
    if page.get("date_published"):
        article["datePublished"] = page["date_published"]
    if page.get("author"):
        article["author"] = {
            "@type": "Organization",
            "name": page["author"],
        }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in page.get("faqs", [])
        ],
    }
    return [*global_schema_entities(), webpage, article, breadcrumb, faq]


def schema_for_guide_hub(canonical: str, pages: list[dict]) -> list[dict]:
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Global Property Buying Guides",
            "url": canonical,
            "description": GUIDE_HUB_DESCRIPTION,
            "dateModified": date.today().isoformat(),
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": index + 1,
                        "name": page["h1"],
                        "url": page_url(page["slug"]),
                    }
                    for index, page in enumerate(pages)
                ],
            },
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Guides", "item": canonical},
            ],
        },
    ]


def guide_cards_for_slugs(slugs: list[str], pages: list[dict], destinations: list[dict]) -> str:
    by_slug = {page["slug"]: page for page in pages}
    cards = []
    for slug in slugs:
        page = by_slug.get(slug)
        if not page:
            continue
        selected = destinations_for_page(page, destinations)[:3]
        market_links = " ".join(
            f'<a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a>'
            for dest in selected
        )
        cards.append(
            f"""
            <article class="page-card">
              <span>{escape(page["theme"])}</span>
              <h3><a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a></h3>
              <p>{escape(page["description"])}</p>
              <p><strong>Use when:</strong> {escape(page["intent"])}</p>
              <p><strong>Start with:</strong> {market_links}</p>
            </article>
            """.rstrip()
        )
    return "\n".join(cards)


def guide_story_list_for_slugs(slugs: list[str], pages: list[dict]) -> str:
    by_slug = {page["slug"]: page for page in pages}
    stories = []
    for slug in slugs:
        page = by_slug.get(slug)
        if not page:
            continue
        stories.append(
            f"""
            <article class="guide-story">
              <span>{escape(page["theme"])}</span>
              <h3><a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a></h3>
              <p>{escape(page["description"])}</p>
              <a class="guide-story__link" href="/{escape(page["slug"])}/">Read guide</a>
            </article>
            """.rstrip()
        )
    return "\n".join(stories)


RETIREMENT_FAQS = [
    (
        "How much do I need to retire abroad?",
        "The answer depends on your destination, household, housing plan, retirement date, reliable outside income, and planning horizon. This calculator estimates annual spending first, then separates the liquid portfolio, property capital, and emergency reserve required.",
    ),
    (
        "How does the calculator handle inflation?",
        "It projects each expense for every year in the retirement horizon. Healthcare and property-related costs can use different assumptions from general living costs, while indexed income rises with inflation and fixed income does not.",
    ),
    (
        "How are pensions and passive income treated?",
        "After-tax pensions, annuities, existing net rental income, and other reliable non-portfolio income reduce the first-year funding gap. Each stream can be treated as inflation-linked or fixed.",
    ),
    (
        "Does the result include buying a retirement property?",
        "Yes. Buy now shows today's purchase cost separately and does not mix it with retirement-year capital. Buy at retirement projects the purchase price and acquisition costs to retirement. Rent and already-own scenarios do not add a new purchase.",
    ),
    (
        "Why are portfolio dividends and interest not subtracted as passive income?",
        "Portfolio dividends and interest are part of the expected portfolio return, not outside income. Counting them separately would understate the portfolio required.",
    ),
]


def schema_for_retirement_calculator(canonical: str) -> list[dict]:
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": RETIREMENT_CALCULATOR_H1,
            "description": RETIREMENT_CALCULATOR_DESCRIPTION,
            "url": canonical,
        },
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": RETIREMENT_CALCULATOR_H1,
            "url": canonical,
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "isAccessibleForFree": True,
            "description": RETIREMENT_CALCULATOR_DESCRIPTION,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": RETIREMENT_CALCULATOR_H1, "item": canonical},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in RETIREMENT_FAQS
            ],
        },
    ]


RETIREMENT_DESTINATIONS_FAQS = [
    (
        "What is the lowest-cost retirement destination in this comparison?",
        "Da Nang / Hoi An has the lowest required retirement capital under this article's standard couple-renting scenario. The comparison covers all 30 destinations currently covered by Global Home Atlas, not every place retirees could choose.",
    ),
    (
        "Why rank retirement destinations instead of countries?",
        "Housing, transport, healthcare access, and daily costs vary widely inside one country. Destination-level comparisons are more useful for planning, while the country remains visible for legal, tax, visa, and healthcare context.",
    ),
    (
        "Does the ranking include pension or passive income?",
        "No. The common ranking scenario assumes no pension or other passive income so every destination is comparable. The retirement calculator lets readers add reliable after-tax income separately.",
    ),
    (
        "Is property included in the retirement cost ranking?",
        "No. The ranking assumes renting. Representative property price plus acquisition costs is shown separately because buying decisions can dominate the comparison and depend heavily on property type and micro-location.",
    ),
]


def schema_for_retirement_destinations_article(
    canonical: str, rankings: list[dict]
) -> list[dict]:
    images = [
        f"{SITE_URL}assets/retirement-destinations-required-capital.png",
        f"{SITE_URL}assets/retirement-destinations-capital-breakdown.png",
    ]
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": RETIREMENT_DESTINATIONS_H1,
            "url": canonical,
            "description": RETIREMENT_DESTINATIONS_DESCRIPTION,
            "dateModified": date.today().isoformat(),
        },
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": RETIREMENT_DESTINATIONS_H1,
            "description": RETIREMENT_DESTINATIONS_DESCRIPTION,
            "url": canonical,
            "datePublished": "2026-08-18",
            "dateModified": date.today().isoformat(),
            "image": images,
            "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
            "mainEntityOfPage": canonical,
        },
        *[
            {
                "@context": "https://schema.org",
                "@type": "ImageObject",
                "contentUrl": image,
                "creditText": SITE_NAME,
                "copyrightNotice": SITE_NAME,
            }
            for image in images
        ],
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Guides", "item": page_url(GUIDE_HUB_SLUG)},
                {"@type": "ListItem", "position": 3, "name": RETIREMENT_DESTINATIONS_H1, "item": canonical},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in RETIREMENT_DESTINATIONS_FAQS
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "Retirement destinations ranked by required capital",
            "numberOfItems": len(rankings),
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": item["destination"]["name"],
                    "url": page_url(
                        f'destinations/{destination_slug(item["destination"])}'
                    ),
                }
                for position, item in enumerate(rankings, start=1)
            ],
        },
    ]


def retirement_benchmark_total(record: dict, household: str) -> float:
    profile = record["profiles"][household]
    return sum(float(value) for value in profile["categories_usd"].values()) + float(profile["annual_rent_usd"])


def retirement_capital_requirement(record: dict, household: str) -> dict[str, float]:
    annual_spending = retirement_benchmark_total(record, household)
    liquid_portfolio = annual_spending / 0.035
    emergency_reserve = annual_spending
    property_capital = float(record["property"]["representative_price_usd"]) * (
        1 + float(record["property"]["acquisition_cost_rate"])
    )
    return {
        "annual_spending": annual_spending,
        "liquid_portfolio": liquid_portfolio,
        "emergency_reserve": emergency_reserve,
        "required_capital": liquid_portfolio + emergency_reserve,
        "property_capital": property_capital,
    }


def retirement_destination_rankings(destinations: list[dict], retirement_payload: dict) -> list[dict]:
    destination_by_id = {item["id"]: item for item in destinations}
    rankings = []
    for record in retirement_payload["destinations"]:
        destination = destination_by_id[record["destination_id"]]
        rankings.append(
            {
                "record": record,
                "destination": destination,
                "metrics": retirement_capital_requirement(record, "couple"),
            }
        )
    rankings.sort(key=lambda item: item["metrics"]["required_capital"])
    return rankings


def split_rankings(
    rankings: list[dict], visible_count: int = 10
) -> tuple[list[dict], list[dict]]:
    if visible_count < 1:
        raise ValueError("visible_count must be positive")
    return rankings[:visible_count], rankings[visible_count:]


def build_find_your_fit_page(destinations: list[dict]) -> str:
    payload_destinations = []
    for destination in destinations:
        dimensions = {
            item["key"]: float(item.get("score", 0) or 0)
            for item in destination.get("decision_dimensions", [])
        }
        image_assets = destination_image_assets(destination)
        payload_destinations.append(
            {
                "id": destination["id"],
                "name": destination["name"],
                "country": destination.get("country") or "",
                "href": f"/destinations/{destination_slug(destination)}/",
                "price": float(destination.get("usd_per_m2", 0) or 0),
                "yield": yield_range_label(destination.get("net_yield_estimate")),
                "decisionScore": float(destination.get("decision_score", 0) or 0),
                "locationTypes": destination_location_types(destination),
                "goalScores": {
                    goal: rank_destinations_for_goal([destination], goal)[0]["goal_score"]
                    for goal in GOAL_DIMENSION_WEIGHTS
                },
                "dimensions": dimensions,
                "recommendable": is_destination_recommendable(destination),
                "watch": destination.get("access_summary")
                if not is_destination_recommendable(destination)
                else destination.get("red_flags")
                or destination.get("main_risk")
                or "Verify current ownership, tax, rental, and resale assumptions locally.",
                "image": image_assets["webp_600"],
                "imageAlt": image_assets["alt"],
            }
        )

    payload = json.dumps(
        {
            "destinations": payload_destinations,
            "universeCount": len(payload_destinations),
            "budgetThresholds": FIT_BUDGET_THRESHOLDS,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")
    canonical = page_url(FIND_YOUR_FIT_SLUG)
    schema = [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": "Find your destination fit",
            "url": canonical,
            "description": FIND_YOUR_FIT_DESCRIPTION,
            "dateModified": date.today().isoformat(),
        },
    ]
    html = """<!doctype html>
<html lang="en">
<head>
__HEAD__
  <style>
    :root { color: #24312d; background: #f5f1e9; font-family: Inter, ui-sans-serif, system-ui, sans-serif; --ink:#24312d; --muted:#66766f; --line:rgba(36,49,45,.15); --paper:#fffdf7; --sage:#c7d3c2; --green:#5f7f72; --gold:#a98a4b; }
    * { box-sizing: border-box; }
    html, body { overflow-x: hidden; }
    body { margin: 0; min-width: 320px; }
    a { color: var(--green); text-underline-offset: 3px; }
    p, li { line-height: 1.55; }
    button, input { font: inherit; }
    .page-shell { width: min(1080px, calc(100% - 32px)); margin: 0 auto; }
    .fit-hero { padding: 18px 0 54px; background: linear-gradient(120deg, #fffdf7 0 58%, #e7eee8); }
    .page-nav { display:flex; align-items:center; justify-content:space-between; gap:18px; margin-bottom:62px; }
    .page-brand { display:flex; align-items:center; text-decoration:none; }
    .primary-brand-logo { width:174px; max-width:48vw; display:block; }
    .page-nav-links { display:flex; gap:18px; flex-wrap:wrap; }
    .page-nav-links a { color:rgba(36,49,45,.76); font-size:13px; font-weight:800; text-decoration:none; }
    .mobile-menu { display:none; position:relative; }
    .mobile-menu summary { min-height:42px; display:inline-flex; align-items:center; padding:0 13px; border:1px solid var(--line); border-radius:6px; font-weight:800; list-style:none; cursor:pointer; }
    .mobile-menu summary::-webkit-details-marker { display:none; }
    .mobile-menu nav { position:absolute; right:0; top:48px; z-index:20; width:260px; display:grid; gap:4px; padding:10px; border:1px solid var(--line); border-radius:8px; background:var(--paper); box-shadow:0 18px 44px rgba(36,49,45,.14); }
    .mobile-menu nav a { padding:10px; color:var(--ink); font-weight:800; text-decoration:none; }
    .eyebrow { margin:0 0 10px; color:#806738; font-size:12px; font-weight:900; letter-spacing:.1em; text-transform:uppercase; }
    h1 { max-width:760px; margin:0; font-family:Georgia,serif; font-size:clamp(42px,7vw,78px); line-height:.96; }
    .lede { max-width:720px; margin:20px 0 0; color:#46554f; font-size:19px; }
    main { padding:34px 0 64px; }
    .fit-layout { display:grid; grid-template-columns:minmax(0, .9fr) minmax(280px, .45fr); gap:24px; align-items:start; }
    .fit-panel, .fit-note, .fit-results { border:1px solid var(--line); border-radius:10px; background:var(--paper); box-shadow:0 16px 42px rgba(36,49,45,.07); }
    .fit-panel { padding:28px; }
    .fit-progress { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:24px; color:var(--muted); font-size:13px; font-weight:800; }
    .fit-progress span { flex:1; height:5px; overflow:hidden; border-radius:9px; background:#e6e6df; }
    .fit-progress i { display:block; width:20%; height:100%; background:var(--green); transition:width .2s ease; }
    fieldset { min-width:0; margin:0; padding:0; border:0; }
    legend { max-width:680px; margin-bottom:8px; font-family:Georgia,serif; font-size:clamp(27px,4vw,38px); font-weight:700; line-height:1.05; }
    .question-help { margin:0 0 20px; color:var(--muted); }
    .choice-list { display:grid; gap:9px; }
    .choice { position:relative; display:grid; grid-template-columns:auto 1fr; gap:12px; align-items:start; padding:14px; border:1px solid var(--line); border-radius:8px; cursor:pointer; }
    .choice:has(input:checked) { border-color:var(--green); background:#eef4ef; box-shadow:inset 0 0 0 1px var(--green); }
    .choice input { margin-top:3px; accent-color:var(--green); }
    .choice strong { display:block; }
    .choice small { display:block; margin-top:3px; color:var(--muted); line-height:1.4; }
    .fit-actions { display:flex; justify-content:space-between; gap:12px; margin-top:24px; }
    .fit-actions button, .results-actions a, .results-actions button { min-height:44px; display:inline-flex; align-items:center; justify-content:center; padding:0 15px; border:1px solid var(--line); border-radius:6px; background:var(--paper); color:var(--ink); font-weight:800; text-decoration:none; cursor:pointer; }
    .fit-actions .primary, .results-actions .primary { border-color:var(--green); background:var(--green); color:#fff; }
    .fit-note { padding:22px; }
    .fit-note p { margin:0; color:#46554f; }
    .fit-results { grid-column:1 / -1; padding:28px; }
    .fit-results[hidden], [hidden] { display:none !important; }
    .results-header { display:flex; align-items:end; justify-content:space-between; gap:20px; margin-bottom:20px; }
    .results-header h2 { margin:0; font-family:Georgia,serif; font-size:clamp(30px,5vw,48px); }
    .results-header p { margin:8px 0 0; color:var(--muted); }
    .fit-result-list { display:grid; gap:12px; }
    .fit-result { display:grid; grid-template-columns:132px minmax(0,1fr) 150px; gap:18px; align-items:start; padding:16px; border:1px solid var(--line); border-radius:9px; background:#fff; }
    .fit-result img { width:132px; height:96px; object-fit:cover; border-radius:6px; filter:saturate(.82); }
    .fit-result h3 { margin:0 0 4px; font-size:22px; }
    .fit-result h3 a { color:var(--ink); text-decoration:none; }
    .fit-result .place { margin:0 0 10px; color:var(--muted); font-size:14px; }
    .fit-result ul { margin:0; padding-left:18px; color:#42514b; }
    .fit-result .watch { margin:9px 0 0; color:#6c4f43; font-size:13px; }
    .fit-result__facts { display:grid; gap:9px; }
    .fit-result__facts span { color:var(--muted); font-size:11px; font-weight:900; letter-spacing:.06em; text-transform:uppercase; }
    .fit-result__facts strong { display:block; margin-top:2px; }
    .fit-label { color:#365f52; }
    .other-results { margin-top:18px; border-top:1px solid var(--line); padding-top:16px; }
    .other-results summary { cursor:pointer; font-weight:850; }
    .other-results ol { columns:2; gap:36px; padding-left:24px; }
    .other-results li { break-inside:avoid; padding:5px 0; }
    .other-results small { color:var(--muted); }
    .restriction-note { margin:14px 0 0; color:#6c4f43; font-size:13px; }
    .results-actions { display:flex; flex-wrap:wrap; gap:10px; margin-top:22px; }
    .page-footer { padding:28px 0 46px; border-top:1px solid var(--line); color:var(--muted); }
    @media(max-width:760px) {
      .page-nav-links { display:none; } .mobile-menu { display:block; }
      .fit-layout { grid-template-columns:1fr; } .fit-note { order:-1; }
      .fit-panel, .fit-results { padding:20px; }
      .fit-result { grid-template-columns:88px minmax(0,1fr); }
      .fit-result img { width:88px; height:78px; }
      .fit-result__facts { grid-column:1 / -1; grid-template-columns:repeat(3,1fr); }
      .other-results ol { columns:1; }
    }
    @media(max-width:480px) {
      .page-shell { width:min(1080px, calc(100% - 24px)); }
      .fit-hero { padding-bottom:38px; } .page-nav { margin-bottom:44px; }
      h1 { font-size:40px; }
      .lede { font-size:16px; }
      .fit-result { grid-template-columns:1fr; }
      .fit-result img { width:100%; height:150px; }
      .fit-result__facts { grid-column:auto; }
      .results-header { display:block; }
    }
  </style>
</head>
<body>
  <header class="fit-hero">
    <div class="page-shell">
__PRIMARY_NAV__
      <h1>Find your destination fit</h1>
      <p class="lede">Tell us what the property needs to do for you. We will evaluate every destination currently in the Atlas and explain which ones deserve a closer look.</p>
    </div>
  </header>
  <main>
    <div class="page-shell fit-layout">
      <section class="fit-panel" id="fitQuestionnaire">
        <div class="fit-progress"><span><i id="fitProgressBar"></i></span><b id="fitProgressText">Question 1 of 5</b></div>
        <form id="fitForm">
          <fieldset data-fit-step="0">
            <legend>What are you buying for?</legend>
            <p class="question-help">This sets the strongest priorities in your match.</p>
            <div class="choice-list">
              <label class="choice"><input type="radio" name="goal" value="retirement" checked><span><strong>Retirement or lifestyle base</strong><small>Daily life, healthcare, access and long-stay comfort.</small></span></label>
              <label class="choice"><input type="radio" name="goal" value="second-home"><span><strong>Second home</strong><small>Repeat visits, lifestyle appeal, access and resale depth.</small></span></label>
              <label class="choice"><input type="radio" name="goal" value="investment"><span><strong>Investment-led purchase</strong><small>Rental realism, capital upside, value and exit liquidity.</small></span></label>
              <label class="choice"><input type="radio" name="goal" value="ownership"><span><strong>Straightforward ownership</strong><small>Clear title, foreign-buyer access and regulatory stability.</small></span></label>
            </div>
          </fieldset>
          <fieldset data-fit-step="1" hidden>
            <legend>What is your approximate purchase budget?</legend>
            <p class="question-help">This is an early market screen based on each destination's price-per-square-metre guide, not a listing quote.</p>
            <div class="choice-list">
              <label class="choice"><input type="radio" name="budget" value="low" checked><span><strong>Under roughly $300,000</strong><small>Prioritise markets near or below $4,000/m².</small></span></label>
              <label class="choice"><input type="radio" name="budget" value="mid"><span><strong>Roughly $300,000–$600,000</strong><small>Consider markets up to about $8,000/m².</small></span></label>
              <label class="choice"><input type="radio" name="budget" value="high"><span><strong>Roughly $600,000–$1.2 million</strong><small>Consider markets up to about $15,000/m².</small></span></label>
              <label class="choice"><input type="radio" name="budget" value="flexible"><span><strong>Flexible or above $1.2 million</strong><small>Do not use price as a strong screen.</small></span></label>
            </div>
          </fieldset>
          <fieldset data-fit-step="2" hidden>
            <legend>What kind of setting feels right?</legend>
            <p class="question-help">Destinations can belong to more than one setting.</p>
            <div class="choice-list">
              <label class="choice"><input type="radio" name="setting" value="any" checked><span><strong>No strong preference</strong><small>Let the other answers lead.</small></span></label>
              <label class="choice"><input type="radio" name="setting" value="city"><span><strong>City</strong><small>Services, transport and year-round daily life.</small></span></label>
              <label class="choice"><input type="radio" name="setting" value="coast-island"><span><strong>Coast or island</strong><small>Water access, warm-weather use and holiday appeal.</small></span></label>
              <label class="choice"><input type="radio" name="setting" value="mountain"><span><strong>Mountain</strong><small>Outdoor access, seasons and resort-market dynamics.</small></span></label>
              <label class="choice"><input type="radio" name="setting" value="lake"><span><strong>Lake</strong><small>Waterside living with a mountain or regional setting.</small></span></label>
            </div>
          </fieldset>
          <fieldset data-fit-step="3" hidden>
            <legend>How will you use the property?</legend>
            <p class="question-help">This changes how much lifestyle or rental fundamentals matter.</p>
            <div class="choice-list">
              <label class="choice"><input type="radio" name="use" value="personal" checked><span><strong>Mainly personal use</strong><small>Prioritise lifestyle quality and long-stay comfort.</small></span></label>
              <label class="choice"><input type="radio" name="use" value="balanced"><span><strong>Personal use with some rental offset</strong><small>Balance daily appeal with realistic operating economics.</small></span></label>
              <label class="choice"><input type="radio" name="use" value="rental"><span><strong>Mainly rental income</strong><small>Give more weight to rental profit and regulatory safety.</small></span></label>
            </div>
          </fieldset>
          <fieldset data-fit-step="4" hidden>
            <legend>Which trade-off matters most?</legend>
            <p class="question-help">No market is frictionless. Choose what should break a close tie.</p>
            <div class="choice-list">
              <label class="choice"><input type="radio" name="tradeoff" value="clarity" checked><span><strong>Ownership clarity</strong><small>Prefer simpler legal pathways and more stable operating rules.</small></span></label>
              <label class="choice"><input type="radio" name="tradeoff" value="balanced"><span><strong>Balanced fundamentals</strong><small>Keep the Atlas's overall decision model as the tie-breaker.</small></span></label>
              <label class="choice"><input type="radio" name="tradeoff" value="upside"><span><strong>Income and upside</strong><small>Accept more market complexity for stronger return potential.</small></span></label>
            </div>
          </fieldset>
          <div class="fit-actions"><button type="button" id="fitBack" hidden>Back</button><button type="button" class="primary" id="fitNext">Continue</button><button type="submit" class="primary" id="fitSubmit" hidden>See my matches</button></div>
        </form>
      </section>
      <aside class="fit-note">
        <p><strong>All __DESTINATION_COUNT__ current destinations are evaluated.</strong> Restricted markets stay out of the recommended five. Your answers remain in this browser.</p>
      </aside>
      <section class="fit-results" id="fitResults" hidden data-universe-count="__DESTINATION_COUNT__">
        <div class="results-header"><div><h2>Five destinations to compare</h2><p id="fitResultSummary"></p></div></div>
        <div class="fit-result-list" id="fitResultList"></div>
        <details class="other-results" id="fitOtherResults"><summary id="fitOtherSummary">Other destinations considered</summary><ol id="fitOtherList"></ol></details>
        <p class="restriction-note" id="fitRestrictionNote"></p>
        <div class="results-actions"><button type="button" id="fitEdit">Edit my answers</button><a class="primary" href="/dashboard/">Explore all destinations</a></div>
      </section>
    </div>
  </main>
  <footer class="page-footer"><div class="page-shell"><strong>Global Home Atlas</strong><p>Research guidance only. Verify current legal, tax, immigration, financing, insurance, and property details locally.</p></div></footer>
  <script type="application/json" id="fit-data">__FIT_DATA__</script>
  <script>
    (() => {
      const data = JSON.parse(document.getElementById("fit-data").textContent);
      const form = document.getElementById("fitForm");
      const questionnaire = document.getElementById("fitQuestionnaire");
      const steps = Array.from(form.querySelectorAll("[data-fit-step]"));
      const back = document.getElementById("fitBack");
      const next = document.getElementById("fitNext");
      const submit = document.getElementById("fitSubmit");
      const results = document.getElementById("fitResults");
      let activeStep = 0;
      const locationLabels = { city:"city setting", "coast-island":"coast or island setting", mountain:"mountain setting", lake:"lake setting" };
      const dimensionLabels = { lifestyle_magnetism:"lifestyle appeal", global_access:"international access", ownership_clarity:"ownership clarity", regulatory_safety:"regulatory safety", rental_profit:"rental fundamentals", capital_upside:"capital upside", retirement_fit:"long-stay comfort", exit_liquidity:"resale depth", foreigner_fit:"foreigner practicality", value_entry:"value at entry" };
      const goalLabels = { retirement:"retirement or lifestyle", "second-home":"second-home use", investment:"investment-led buying", ownership:"clear ownership" };

      function escapeHtml(value) {
        return String(value || "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
      }
      function showStep(index) {
        activeStep = Math.max(0, Math.min(index, steps.length - 1));
        steps.forEach((step, stepIndex) => { step.hidden = stepIndex !== activeStep; });
        back.hidden = activeStep === 0;
        next.hidden = activeStep === steps.length - 1;
        submit.hidden = activeStep !== steps.length - 1;
        document.getElementById("fitProgressText").textContent = `Question ${activeStep + 1} of ${steps.length}`;
        document.getElementById("fitProgressBar").style.width = `${((activeStep + 1) / steps.length) * 100}%`;
      }
      function values() { return Object.fromEntries(new FormData(form).entries()); }
      function average(item, keys) { return keys.reduce((sum, key) => sum + Number(item.dimensions[key] || 0), 0) / keys.length; }
      function scoreItem(item, answers) {
        const goalScore = Number(item.goalScores[answers.goal] || item.decisionScore || 0);
        const settingScore = answers.setting === "any" ? goalScore : (item.locationTypes.includes(answers.setting) ? 5 : 2);
        const threshold = data.budgetThresholds[answers.budget];
        let budgetScore = goalScore;
        if (threshold && item.price) {
          if (item.price <= threshold) budgetScore = 5;
          else if (item.price <= threshold * 1.25) budgetScore = 3.5;
          else budgetScore = Math.max(1, 5 * threshold / item.price);
        }
        const useScore = answers.use === "personal" ? average(item, ["lifestyle_magnetism", "retirement_fit"]) : answers.use === "rental" ? average(item, ["rental_profit", "regulatory_safety"]) : item.decisionScore;
        const tradeoffScore = answers.tradeoff === "clarity" ? average(item, ["ownership_clarity", "regulatory_safety", "foreigner_fit"]) : answers.tradeoff === "upside" ? average(item, ["capital_upside", "rental_profit"]) : item.decisionScore;
        const fitScore = Math.max(0, Math.min(5, goalScore * .4 + settingScore * .2 + budgetScore * .15 + useScore * .15 + tradeoffScore * .1));
        return { ...item, fitScore, fitLabel: fitScore >= 4.25 ? "Strong fit" : fitScore >= 3.6 ? "Worth comparing" : "Conditional fit", budgetScore };
      }
      function reasons(item, answers) {
        const output = [`Strong relative fit for ${goalLabels[answers.goal]}.`];
        if (answers.setting !== "any" && item.locationTypes.includes(answers.setting)) output.push(`Matches your preferred ${locationLabels[answers.setting]}.`);
        if (item.budgetScore >= 3.5) output.push("Fits the broad price screen you selected.");
        const strongest = Object.entries(item.dimensions).sort((a,b) => b[1] - a[1])[0];
        if (strongest) output.push(`One of its strongest signals is ${dimensionLabels[strongest[0]] || strongest[0]}.`);
        return output.slice(0, 3);
      }
      function resultCard(item, index, answers) {
        return `<article class="fit-result"><img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.imageAlt)}" width="600" height="400" loading="lazy" decoding="async"><div><h3><a href="${escapeHtml(item.href)}">${index + 1}. ${escapeHtml(item.name)}</a></h3><p class="place">${escapeHtml(item.country)}</p><ul>${reasons(item, answers).map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}</ul><p class="watch"><strong>Watch:</strong> ${escapeHtml(item.watch)}</p></div><div class="fit-result__facts"><div><span>Fit</span><strong class="fit-label">${escapeHtml(item.fitLabel)}</strong></div><div><span>Price guide</span><strong>${item.price ? "$" + Number(item.price).toLocaleString() + "/m²" : "n/a"}</strong></div><div><span>Net yield</span><strong>${escapeHtml(item.yield)}</strong></div></div></article>`;
      }
      function renderResults() {
        const answers = values();
        const ranked = data.destinations.map((item) => scoreItem(item, answers)).sort((a,b) => Number(b.recommendable) - Number(a.recommendable) || b.fitScore - a.fitScore || b.decisionScore - a.decisionScore);
        const top = ranked.filter((item) => item.recommendable).slice(0, 5);
        const topIds = new Set(top.map((item) => item.id));
        const others = ranked.filter((item) => !topIds.has(item.id));
        const restricted = ranked.filter((item) => !item.recommendable);
        document.getElementById("fitResultList").innerHTML = top.map((item, index) => resultCard(item, index, answers)).join("");
        document.getElementById("fitResultSummary").textContent = `${data.universeCount} destinations evaluated for ${goalLabels[answers.goal]}. Fit labels are directional research guidance, not investment scores.`;
        document.getElementById("fitOtherSummary").textContent = `${others.length} other destinations considered`;
        document.getElementById("fitOtherList").innerHTML = others.map((item) => `<li><a href="${escapeHtml(item.href)}">${escapeHtml(item.name)}</a> <small>— ${escapeHtml(item.recommendable ? item.fitLabel : "buyer access restricted")}</small></li>`).join("");
        document.getElementById("fitRestrictionNote").textContent = restricted.length ? `${restricted.length} destinations were evaluated but kept out of the recommended five because current foreign-buyer access is restricted.` : "";
        questionnaire.hidden = true;
        results.hidden = false;
        results.scrollIntoView({ behavior:"smooth", block:"start" });
        if (window.GHA) window.GHA.track("fit_finder_complete", { goal:answers.goal, budget:answers.budget, setting:answers.setting, use:answers.use, tradeoff:answers.tradeoff, universe_count:data.universeCount });
      }
      next.addEventListener("click", () => showStep(activeStep + 1));
      back.addEventListener("click", () => showStep(activeStep - 1));
      form.addEventListener("submit", (event) => { event.preventDefault(); renderResults(); });
      document.getElementById("fitEdit").addEventListener("click", () => { results.hidden = true; questionnaire.hidden = false; showStep(0); questionnaire.scrollIntoView({ behavior:"smooth", block:"start" }); });
      const requestedGoal = new URLSearchParams(location.search).get("goal");
      const goalInput = requestedGoal && form.querySelector(`input[name="goal"][value="${CSS.escape(requestedGoal)}"]`);
      if (goalInput) goalInput.checked = true;
      showStep(0);
    })();
  </script>
__ANALYTICS__
</body>
</html>
"""
    return (
        html.replace("__HEAD__", head_html(FIND_YOUR_FIT_TITLE, FIND_YOUR_FIT_DESCRIPTION, canonical, schema).strip())
        .replace("__PRIMARY_NAV__", primary_nav_html().strip())
        .replace("__DESTINATION_COUNT__", str(len(destinations)))
        .replace("__FIT_DATA__", payload)
        .replace("__ANALYTICS__", analytics_event_script())
    )


def schema_for_retirement_finder(canonical: str) -> list[dict]:
    return [
        *global_schema_entities(),
        {
            "@type": "WebApplication",
            "@id": f"{canonical}#calculator",
            "name": "Retirement Destination Finder",
            "url": canonical,
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "description": RETIREMENT_FINDER_DESCRIPTION,
            "isAccessibleForFree": True,
        },
    ]


def build_retirement_destination_finder_page(
    destinations: list[dict],
    retirement_payload: dict,
    mortgage_payload: dict,
) -> str:
    retirement_ids = {item["destination_id"] for item in retirement_payload["destinations"]}
    eligible_destinations = [item for item in destinations if item["id"] in retirement_ids]
    mortgage_profiles = {
        item["id"]: resolve_mortgage_profile(item, mortgage_payload)
        for item in eligible_destinations
    }
    browser_destinations = [
        {
            **item,
            "continent": CONTINENT_BY_COUNTRY.get(item.get("country", ""), ""),
            "recommendable": is_destination_recommendable(item),
        }
        for item in eligible_destinations
    ]
    payload = {
        "asOf": retirement_payload.get("as_of"),
        "destinations": browser_destinations,
        "retirementCosts": retirement_payload["destinations"],
        "mortgageProfiles": mortgage_profiles,
        "defaultBuyerProfile": mortgage_payload["default_buyer_profile"],
    }
    region_options = "".join(
        f'<option value="{escape(region)}">{escape(region.replace("-", " ").title())}</option>'
        for region in sorted({item["continent"] for item in browser_destinations if item["continent"]})
    )
    canonical = page_url(RETIREMENT_FINDER_SLUG)
    return build_retirement_destination_finder_html(
        head=head_html(
            RETIREMENT_FINDER_TITLE,
            RETIREMENT_FINDER_DESCRIPTION,
            canonical,
            schema_for_retirement_finder(canonical),
        ).strip(),
        navigation=primary_nav_html().strip(),
        region_options=region_options,
        universe_count=len(eligible_destinations),
        payload_json=json.dumps(payload, separators=(",", ":")).replace("</", "<\\/"),
        retirement_engine=RETIREMENT_ENGINE_PATH.read_text(encoding="utf-8").replace("</script>", "<\\/script>"),
        property_engine=PROPERTY_FINANCE_PATH.read_text(encoding="utf-8").replace("</script>", "<\\/script>"),
        finder_engine=RETIREMENT_FINDER_ENGINE_PATH.read_text(encoding="utf-8").replace("</script>", "<\\/script>"),
        finder_ui=RETIREMENT_FINDER_UI_PATH.read_text(encoding="utf-8").replace("</script>", "<\\/script>"),
        analytics=analytics_event_script(),
    )


def retirement_calculator_callout(css_class: str, source_label: str) -> str:
    return f"""
      <section class="{escape(css_class)}">
        <h2>Estimate your retirement capital</h2>
        <p>Start with destination expenses in today's money, then account for inflation, reliable pension and passive income, housing, property acquisition, and a liquid portfolio.</p>
        <a class="page-button" href="/{RETIREMENT_CALCULATOR_SLUG}/" data-track="retirement_calculator_open" data-track-label="{escape(source_label)}">Open the retirement abroad calculator</a>
      </section>
    """


def build_retirement_calculator_page(destinations: list[dict], retirement_payload: dict) -> str:
    canonical = page_url(RETIREMENT_CALCULATOR_SLUG)
    destination_by_id = {item["id"]: item for item in destinations}
    records = retirement_payload["destinations"]
    browser_records = []
    options = []
    source_links = []
    for record in records:
        item = dict(record)
        destination = destination_by_id.get(record["destination_id"], {})
        item["name"] = destination.get("name", record["destination_id"].replace("-", " ").title())
        item["continent"] = CONTINENT_BY_COUNTRY.get(destination.get("country", ""), "")
        browser_records.append(item)
        options.append(f'<option value="{escape(item["destination_id"])}">{escape(item["name"])}</option>')
        first_source = item["sources"][0]
        source_links.append(
            f'<li><a href="{escape(first_source["url"])}" rel="nofollow noopener">{escape(item["name"])} cost evidence</a> '
            f'({escape(first_source["source_date"])}) · {escape(item["confidence"]["overall"])} confidence</li>'
        )
    def benchmark_panel(household: str) -> str:
        label = "Couple" if household == "couple" else "Single retiree"
        ranked_records = sorted(
            browser_records,
            key=lambda item: retirement_capital_requirement(item, household)["required_capital"],
        )
        rows = []
        for rank, item in enumerate(ranked_records, start=1):
            metrics = retirement_capital_requirement(item, household)
            rows.append(
                f'<tr class="benchmark-row" data-continent="{escape(item["continent"])}"><td>{rank}</td><th scope="row">{escape(item["name"])}</th>'
                f'<td>{money(metrics["annual_spending"])}</td>'
                f'<td>{money(metrics["liquid_portfolio"])}</td>'
                f'<td>{money(metrics["emergency_reserve"])}</td>'
                f'<td><strong>{money(metrics["required_capital"])}</strong></td>'
                f'<td>{money(metrics["property_capital"])}</td></tr>'
            )
        hidden = " hidden" if household == "single" else ""
        return (
            f'<div class="benchmark-panel" data-benchmark-panel="{household}"{hidden}>'
            f'<div class="table-wrap"><table><caption>{label} retirement capital by destination in today\'s USD</caption>'
            '<thead><tr><th>Rank</th><th>Destination</th><th>Annual spending</th><th>Liquid portfolio</th><th>Emergency reserve</th><th>Required retirement capital</th><th>Property capital</th></tr></thead>'
            f'<tbody data-benchmark-visible>{"".join(rows[:10])}</tbody></table></div>'
            '<details class="benchmark-more" data-benchmark-more><summary data-benchmark-summary>View ranks 11–30</summary><div class="table-wrap"><table>'
            f'<caption>{label} retirement capital for ranks 11–30</caption>'
            '<thead><tr><th>Rank</th><th>Destination</th><th>Annual spending</th><th>Liquid portfolio</th><th>Emergency reserve</th><th>Required retirement capital</th><th>Property capital</th></tr></thead>'
            f'<tbody data-benchmark-expandable>{"".join(rows[10:])}</tbody></table></div></details></div>'
        )

    benchmark_panels = benchmark_panel("couple") + benchmark_panel("single")
    faq_html = "\n".join(
        f'<details><summary>{escape(question)}</summary><p>{escape(answer)}</p></details>'
        for question, answer in RETIREMENT_FAQS
    )
    page_data = json.dumps(
        {"as_of": retirement_payload["as_of"], "currency": retirement_payload["currency"], "destinations": browser_records},
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    engine_js = RETIREMENT_ENGINE_PATH.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
    ui_js = RETIREMENT_UI_PATH.read_text(encoding="utf-8").replace("</script>", "<\\/script>") if RETIREMENT_UI_PATH.exists() else ""
    html = """<!doctype html>
<html lang="en">
<head>
__HEAD__
  <style>
    :root { color: #24312d; background: #f5f1e9; font-family: Inter, ui-sans-serif, system-ui, sans-serif; --ink:#24312d; --muted:#66736c; --line:#d8d1c4; --paper:#fffdf7; --green:#315e50; }
    * { box-sizing: border-box; } body { margin:0; line-height:1.55; } a { color:#245c4b; } h1,h2 { font-family:Georgia,serif; line-height:1.08; } h1 { font-size:clamp(38px,7vw,68px); margin:.4rem 0 1rem; } h2 { font-size:clamp(27px,4vw,38px); }
    .calc-shell { width:min(1120px, calc(100% - 32px)); margin:0 auto; } .calc-nav { display:flex; align-items:center; justify-content:space-between; gap:24px; padding:18px 0; border-bottom:1px solid rgba(255,255,255,.18); } .calc-brand { color:#fff; text-decoration:none; font-weight:900; } .calc-nav-links { display:flex; flex-wrap:wrap; gap:16px; } .calc-nav-links a { color:#f5f1e9; text-decoration:none; font-size:14px; }
    .calc-hero { color:#fff; background:#243f37; padding-bottom:46px; } .eyebrow { text-transform:uppercase; letter-spacing:.08em; font-size:12px; font-weight:800; color:#d8c28d; margin-top:42px; } .lede { max-width:760px; font-size:18px; color:#e2e8e4; } .calc-modes { display:flex; flex-wrap:wrap; gap:18px; margin-top:22px; font-weight:750; } .calc-modes a { color:#fff; } .calc-modes a[aria-current] { color:#d8c28d; text-decoration:none; border-bottom:2px solid #d8c28d; }
    main { padding:32px 0 70px; } .calculator-layout { display:grid; grid-template-columns:minmax(0,1fr) minmax(300px,.76fr); gap:24px; align-items:start; } .calc-panel { background:var(--paper); border:1px solid var(--line); border-radius:10px; padding:clamp(18px,3vw,30px); } .detailed-projection { margin-top:24px; } .detailed-projection > h2 { margin-top:0; } .projection-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:0 28px; align-items:start; } .field-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:15px; } .field { min-width:0; } label,.field-label { display:block; font-weight:750; margin:0 0 6px; } input,select,button { width:100%; min-height:46px; border:1px solid #a9a398; border-radius:6px; background:#fff; color:var(--ink); padding:10px 12px; font:inherit; } input:focus,select:focus,button:focus { outline:3px solid #d6b96f; outline-offset:2px; } .check { display:flex; gap:8px; align-items:center; font-weight:600; margin-top:8px; } .check input { width:20px; min-height:20px; } fieldset { border:0; padding:0; margin:24px 0 0; } legend { font-family:Georgia,serif; font-size:23px; font-weight:700; margin-bottom:12px; } .hint { color:var(--muted); font-size:13px; margin:6px 0 0; } details.assumptions { margin:24px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:13px 0; } summary { cursor:pointer; font-weight:800; } .primary { background:var(--green); color:#fff; border-color:var(--green); font-weight:850; cursor:pointer; }
    .result-panel { position:sticky; top:18px; } .result-panel h2 { margin-top:0; } .result-decision { margin:14px 0 20px; padding:15px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); font-family:Georgia,serif; font-size:22px; line-height:1.3; } .key-figures { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; } .key-figures div { border-top:1px solid var(--line); padding-top:10px; } .key-figures span { display:block; color:var(--muted); font-size:12px; } .key-figures strong { display:block; margin-top:3px; font-family:Georgia,serif; font-size:27px; line-height:1.1; } .save-intent { padding-top:2px; } .save-intent .text-button { font-weight:750; } .result-period { padding:18px 0; border-top:1px solid var(--line); } .result-period h3 { font-family:Georgia,serif; font-size:21px; margin:0 0 10px; } .result-total { font-family:Georgia,serif; font-size:clamp(34px,5vw,48px); line-height:1; margin:8px 0; } .result-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin:16px 0 0; } .result-grid div { border-top:1px solid var(--line); padding-top:10px; } .result-grid span { display:block; color:var(--muted); font-size:12px; } .result-grid strong { display:block; font-size:20px; } .result-grid strong.is-negative { color:#9b2c20; } .result-grid small { display:block; color:var(--muted); font-size:12px; line-height:1.4; margin-top:4px; } #ret-errors { color:#8a2b20; font-weight:700; } .is-hidden { display:none; }
    .accumulation-figure { position:relative; margin:0; padding:18px 0; border-top:1px solid var(--line); } .accumulation-figure h3 { font-family:Georgia,serif; font-size:21px; margin:0 0 10px; } .chart-legend { display:flex; gap:18px; color:var(--muted); font-size:12px; margin-bottom:8px; } .chart-key::before { content:""; display:inline-block; width:10px; height:10px; margin-right:6px; background:#315e50; } .chart-key.contribution::before { background:#c29b45; } .accumulation-chart { display:block; width:100%; height:auto; overflow:visible; } .chart-axis { stroke:var(--line); stroke-width:1; } .chart-target { stroke:#9b6a33; stroke-width:1.5; stroke-dasharray:5 4; } .chart-target-label { fill:#7a5227; font-size:11px; font-weight:700; } .chart-axis-label { fill:var(--muted); font-size:10px; } .chart-lump { fill:#315e50; } .chart-contribution { fill:#c29b45; } .chart-year { opacity:0; transform:translateY(8px); animation:ret-year-in .35s ease forwards; animation-delay:var(--year-delay); cursor:pointer; outline:none; } .chart-year.is-active rect,.chart-year:focus-visible rect { stroke:#24312d; stroke-width:2px; } .chart-tooltip { position:absolute; z-index:2; top:60px; right:0; width:min(245px,calc(100% - 20px)); padding:11px 13px; border-radius:6px; background:#24312d; color:#fff; box-shadow:0 8px 24px rgba(36,49,45,.2); font-size:12px; } .chart-tooltip strong { display:block; font-size:14px; margin-bottom:5px; } .chart-tooltip div { display:flex; justify-content:space-between; gap:12px; } .chart-tooltip span { color:#dfe7e3; } .result-comparison { padding:16px 0; border-top:1px solid var(--line); } .result-comparison h3,.result-comparison summary { font-family:Georgia,serif; font-size:21px; } .result-table { min-width:0; font-size:13px; background:transparent; } .result-table th,.result-table td { padding:8px 5px; white-space:normal; } .result-table td { text-align:right; } .result-table .is-selected { background:#f1eee4; } @keyframes ret-year-in { to { opacity:1; transform:translateY(0); } }
    .text-button { width:auto; min-height:0; padding:0; border:0; border-radius:0; background:none; color:#245c4b; text-decoration:underline; cursor:pointer; font-size:13px; }
    .current-cost-comparison { margin-top:24px; } .current-cost-comparison h2 { margin:0 0 8px; } .current-cost-layout { display:grid; grid-template-columns:minmax(230px,.72fr) minmax(0,1.28fr); gap:28px; align-items:start; margin-top:20px; } .optional-label { color:var(--muted); font-weight:400; } .current-cost-result { border-left:1px solid var(--line); padding-left:28px; } .current-cost-summary { margin:0; font-family:Georgia,serif; font-size:23px; line-height:1.28; } .current-cost-annual { margin:7px 0 20px; color:var(--muted); } .current-cost-bars { display:grid; gap:14px; } .current-cost-bar-heading { display:flex; justify-content:space-between; gap:16px; margin-bottom:5px; } .current-cost-bar-heading span { color:var(--muted); white-space:nowrap; } .current-cost-track { height:10px; background:#e7e1d6; } .current-cost-fill { display:block; height:100%; background:#7d968b; transition:width .35s ease; } .current-cost-row.destination .current-cost-fill { background:var(--green); } .target-comparison { margin-top:22px; padding-top:18px; border-top:1px solid var(--line); } .target-comparison h3 { margin:0 0 12px; font-family:Georgia,serif; font-size:21px; } .target-figures { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; } .target-figures div { border-top:1px solid var(--line); padding-top:9px; } .target-figures span { display:block; color:var(--muted); font-size:12px; } .target-figures strong { display:block; margin-top:3px; font-family:Georgia,serif; font-size:24px; } .target-difference { margin:12px 0 0; font-weight:750; }
    .cost-sidecar { width:min(560px,100%); max-width:none; height:100dvh; max-height:none; margin:0 0 0 auto; padding:0; border:0; background:transparent; overflow:hidden; } .cost-sidecar[open] { animation:cost-sidecar-in .25s ease-out; } .cost-sidecar::backdrop { background:rgba(24,34,30,.42); } .cost-sidecar-panel { height:100%; padding:24px; overflow:auto; background:var(--paper); box-shadow:-12px 0 32px rgba(36,49,45,.18); } .cost-sidecar-header { position:sticky; top:-24px; z-index:1; display:flex; align-items:flex-start; justify-content:space-between; gap:20px; margin:-24px -24px 14px; padding:24px; border-bottom:1px solid var(--line); background:var(--paper); } .cost-sidecar-header h2 { margin:0; font-size:30px; } .cost-sidecar-close { width:auto; min-height:40px; padding:7px 10px; background:transparent; cursor:pointer; } .cost-sidecar-chart { display:grid; gap:5px; } .cost-row { min-height:0; padding:9px 10px; border:1px solid transparent; border-radius:3px; background:transparent; text-align:left; cursor:pointer; } .cost-row:hover,.cost-row:focus-visible { border-color:var(--line); background:#f5f1e9; } .cost-row.is-current { border-color:var(--green); } .cost-row-heading { display:flex; justify-content:space-between; gap:16px; } .cost-row-heading > span { color:var(--muted); white-space:nowrap; } .cost-bar-track { display:block; height:8px; margin-top:6px; background:#e7e1d6; } .cost-bar-fill { display:block; height:100%; background:#56806f; } @keyframes cost-sidecar-in { from { transform:translateX(100%); } to { transform:translateX(0); } }
    .content-section { padding:34px 0; border-top:1px solid var(--line); } .benchmark-controls { display:flex; flex-wrap:wrap; gap:14px; margin:20px 0 14px; } .benchmark-control { width:min(240px,100%); } .table-wrap { overflow-x:auto; } table { width:100%; min-width:1080px; border-collapse:collapse; background:var(--paper); } caption { padding:12px; text-align:left; color:var(--muted); font-weight:750; } th,td { text-align:left; padding:12px; border-bottom:1px solid var(--line); white-space:nowrap; } th { white-space:normal; } .benchmark-more { margin-top:18px; } .benchmark-more > summary { display:inline-block; padding:8px 0; color:var(--green); cursor:pointer; } .benchmark-more > summary:focus-visible { outline:3px solid #d6b96f; outline-offset:4px; } .benchmark-more .table-wrap { margin-top:10px; } .scenario-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; } .scenario-grid article { border-left:3px solid #bfa45f; padding-left:14px; } .faq details { padding:14px 0; border-bottom:1px solid var(--line); } .related { display:flex; flex-wrap:wrap; gap:16px; } footer { padding:30px 0; background:#243f37; color:#e2e8e4; } footer a { color:#fff; }
    @media(max-width:780px) { .calculator-layout,.projection-grid,.current-cost-layout { grid-template-columns:1fr; } .result-panel { position:static; } .calc-nav-links { display:none; } .scenario-grid { grid-template-columns:1fr; } .current-cost-result { border-left:0; border-top:1px solid var(--line); padding:20px 0 0; } }
    @media(max-width:520px) { .calc-shell { width:min(100% - 22px,1120px); } .field-grid,.result-grid { grid-template-columns:1fr; } h1 { overflow-wrap:anywhere; } th,td { padding:10px 8px; font-size:13px; } }
    @media(prefers-reduced-motion:reduce) { .chart-year,.cost-sidecar[open] { animation:none; opacity:1; transform:none; } }
  </style>
</head>
<body>
  <header class="calc-hero"><div class="calc-shell">
    <nav class="calc-nav" aria-label="Primary"><a class="calc-brand" href="/">Global Home Atlas</a><div class="calc-nav-links"><a href="/find-your-fit/">Find your fit</a><a href="/dashboard/">Destinations</a><a href="/guides/#country-selection">Countries</a><a href="/guides/">Guides</a><a href="/methodology/">Methodology</a></div></nav>
    <p class="eyebrow">International retirement planning tool</p><h1>Retirement Abroad Calculator</h1>
    <p class="lede">Estimate comfortable destination spending, project it to retirement, and separate the portfolio, property capital, and reserve you may need.</p><p class="hint">All amounts are in today's USD unless marked “at retirement”.</p><nav class="calc-modes" aria-label="Retirement calculator mode"><a href="/retirement-abroad-calculator/" aria-current="page">Plan for a destination</a><a href="/retirement-destination-finder/">Find destinations I can afford</a></nav>
  </div></header>
  <main><div class="calc-shell">
    <section class="calculator-layout" aria-label="Retirement calculator">
      <form class="calc-panel" id="retirement-calculator" novalidate>
        <fieldset><legend>Your retirement</legend><div class="field-grid">
          <div class="field"><label for="ret-current-age">Current age</label><input id="ret-current-age" type="number" min="18" max="99" value="50" required></div>
          <div class="field"><label for="ret-retirement-age">Planned retirement age</label><input id="ret-retirement-age" type="number" min="19" max="100" value="60" required></div>
          <div class="field"><label for="ret-household">Household</label><select id="ret-household"><option value="single">Single retiree</option><option value="couple" selected>Retired couple</option></select></div>
          <div class="field"><label for="ret-horizon">Retirement horizon (years)</label><input id="ret-horizon" type="number" min="1" max="60" value="30"></div>
        </div></fieldset>
        <fieldset><legend>Destination and housing</legend><div class="field-grid">
          <div class="field"><label for="ret-destination">Destination</label><select id="ret-destination">__OPTIONS__</select><p class="hint"><button class="text-button" id="ret-cost-compare-open" type="button">Compare destination retirement costs</button></p></div>
          <div class="field"><label for="ret-housing-plan">Housing plan</label><select id="ret-housing-plan"><option value="rent" selected>Rent</option><option value="own">Already own</option><option value="buy_now">Buy now</option><option value="buy_retirement">Buy at retirement</option></select></div>
          <div class="field"><label id="ret-monthly-spending-label" for="ret-monthly-spending">Monthly retirement living expenses including rent</label><input id="ret-monthly-spending" type="number" min="0" step="1" value="0"><p class="hint" id="ret-housing-guidance">Monthly retirement living expenses, including rent.</p></div>
          <div class="field" id="ret-property-field"><label for="ret-property-budget">Home purchase budget today</label><input id="ret-property-budget" type="number" min="0" step="1" value="0"><p class="hint">Prefilled with today's representative destination price. Edit it to match the home you expect to buy; acquisition costs are added separately.</p></div>
        </div></fieldset>
        <fieldset><legend>Income you receive now (monthly)</legend><p class="hint">Income rises annually with general inflation and the selected share is invested monthly.</p><div class="field-grid">
          <div class="field"><label for="ret-monthly-income">After-tax monthly income</label><input id="ret-monthly-income" type="number" min="0" step="100" value="0"></div>
          <div class="field"><label for="ret-income-invested-rate">Share invested from income (%)</label><input id="ret-income-invested-rate" type="number" min="0" max="100" step="1" value="20"><p class="hint" id="ret-monthly-investment-preview">Monthly contribution: $0</p></div>
        </div></fieldset>
        <fieldset><legend>Income continuing after retirement (annual)</legend><p class="hint">Use after-tax amounts expected to continue in retirement. Do not include dividends from the portfolio being calculated.</p><div class="field-grid">
          <div class="field"><label for="ret-pension">Pension</label><input id="ret-pension" type="number" min="0" step="100" value="24000"><label class="check"><input id="ret-pension-indexed" type="checkbox" checked> Inflation-linked</label></div>
          <div class="field"><label for="ret-other-income">Other non-portfolio income</label><input id="ret-other-income" type="number" min="0" step="100" value="18000"><label class="check"><input id="ret-other-indexed" type="checkbox"> Inflation-linked</label></div>
          <div class="field"><label for="ret-rental-income">Net rental income</label><input id="ret-rental-income" type="number" min="0" step="100" value="0"><p class="hint">Only include income from a separate rental property. Leave at $0 when your destination home is for your own use.</p><label class="check"><input id="ret-rental-indexed" type="checkbox"> Inflation-linked</label></div>
        </div></fieldset>
        <fieldset><legend>Portfolio assumption</legend>
          <label for="ret-expected-return">Expected annual portfolio return after fees (%)</label>
          <input id="ret-expected-return" type="number" min="-5" max="15" step="0.1" required>
          <p class="hint">Required. Enter your own straight-line return assumption; this is not a guaranteed return or probability-of-success estimate.</p>
        </fieldset>
        <details class="assumptions"><summary>Advanced assumptions</summary><div class="field-grid">
          <div class="field"><label for="ret-general-inflation">General inflation (%)</label><input id="ret-general-inflation" type="number" min="0" max="15" step="0.1"></div>
          <div class="field"><label for="ret-healthcare-inflation">Healthcare inflation (%)</label><input id="ret-healthcare-inflation" type="number" min="0" max="15" step="0.1"></div>
          <div class="field"><label for="ret-property-inflation">Property inflation (%)</label><input id="ret-property-inflation" type="number" min="0" max="15" step="0.1"></div>
          <div class="field"><label for="ret-reserve-months">Emergency reserve (months)</label><input id="ret-reserve-months" type="number" min="0" max="36" step="1" value="12"></div>
        </div></details>
        <div id="ret-errors" role="alert" tabindex="-1"></div><button class="primary" id="ret-calculate" type="submit">Update estimate</button>
      </form>
      <section class="calc-panel result-panel" id="ret-results" aria-live="polite" aria-atomic="true">
        <h2>Your planning estimate</h2><p class="hint" id="ret-result-status">Complete the inputs and calculate.</p>
        <p class="result-decision" id="ret-plan-summary">Enter your assumptions to see what to invest today and each month.</p>
        <section class="result-period" id="ret-today-section" aria-label="Key planning figures"><div class="key-figures">
          <div><span>Needed today</span><strong id="ret-total-today">—</strong></div><div><span>Needed at retirement</span><strong id="ret-total-retirement-summary">—</strong></div><div><span>Monthly contribution</span><strong id="ret-monthly-contribution">—</strong></div><div id="ret-home-summary" hidden><span id="ret-home-today-label">Home purchase today</span><strong id="ret-home-today">—</strong></div>
        </div>
        </section>
        <div class="save-intent" id="ret-save-action" hidden>
          <button class="text-button" id="ret-save-intent-button" type="button" data-track="retirement_calculator_save_intent" data-track-label="retirement calculator result">Save this plan</button>
          <p class="hint" id="ret-save-intent-status" role="status" hidden>Saved plans are being evaluated. Your figures have not been stored.</p>
        </div>
      </section>
    </section>
    <section class="calc-panel detailed-projection" id="ret-detailed-projection" hidden aria-labelledby="ret-detailed-projection-heading">
        <h2 id="ret-detailed-projection-heading">Your detailed projection</h2><div class="projection-grid">
        <figure class="accumulation-figure" id="ret-accumulation-figure" hidden><h3>How your retirement investment grows</h3><div class="chart-legend" aria-hidden="true"><span class="chart-key">Lump sum invested today</span><span class="chart-key contribution">Monthly contributions</span></div><div class="chart-tooltip" id="ret-accumulation-tooltip" role="status" hidden><strong id="ret-tooltip-heading"></strong><div><span>Lump sum + growth</span><b id="ret-tooltip-lump"></b></div><div><span>Contributions + growth</span><b id="ret-tooltip-contributions"></b></div><div><span>Total</span><b id="ret-tooltip-total"></b></div></div><svg class="accumulation-chart" id="ret-accumulation-chart" role="img" aria-labelledby="ret-accumulation-title ret-accumulation-desc" viewBox="0 0 640 288"><title id="ret-accumulation-title">Projected retirement investment growth</title><desc id="ret-accumulation-desc">Complete the calculator to see annual progression.</desc><line class="chart-target" id="ret-accumulation-target" x1="22" x2="618"></line><text class="chart-target-label" id="ret-accumulation-target-label" x="618" text-anchor="end"></text><g id="ret-accumulation-bars"></g></svg><figcaption class="hint" id="ret-accumulation-caption"></figcaption></figure>
        <section class="result-comparison" id="ret-sensitivity" hidden><h3>How the return assumption changes your estimate</h3><p class="hint">One percentage point below and above your assumption.</p><table class="result-table"><thead><tr><th>Scenario</th><th>Return</th><th>Needed today</th></tr></thead><tbody id="ret-sensitivity-rows"></tbody></table></section>
        <section class="result-period" aria-labelledby="ret-funding-breakdown-heading"><h3 id="ret-funding-breakdown-heading">How today's funding is used</h3><div class="result-grid"><div><span>Invest today for retirement</span><strong id="ret-invest-today">—</strong></div><div><span>Contributions + growth at retirement</span><strong id="ret-contribution-retirement">—</strong></div></div></section>
        <section class="result-period" id="ret-retirement-section" aria-labelledby="ret-retirement-heading"><h3 id="ret-retirement-heading">What you need at retirement</h3>
          <div class="result-total" id="ret-total-retirement">—</div><p>Total capital at retirement</p>
          <div class="result-grid"><div><span>Liquid portfolio</span><strong id="ret-liquid-portfolio">—</strong></div><div><span>Emergency reserve</span><strong id="ret-emergency-reserve">—</strong></div><div><span id="ret-property-retirement-label">Home purchase at retirement</span><strong id="ret-property-retirement">—</strong></div></div>
        </section>
        <details class="result-comparison" id="ret-housing-comparison" hidden><summary>Compare housing plans</summary><p class="hint">Uses your current lifestyle level and destination assumptions.</p><table class="result-table"><thead><tr><th>Plan</th><th>Needed today</th><th>At retirement</th></tr></thead><tbody id="ret-housing-comparison-rows"></tbody></table></details>
        <section class="result-period" id="ret-first-year-section" aria-labelledby="ret-first-year-heading"><h3 id="ret-first-year-heading">First retirement year</h3>
          <div class="result-grid"><div><span id="ret-first-expenses-label">Annual spending incl. rent</span><strong id="ret-first-expenses">—</strong></div><div><span>Reliable outside income</span><strong id="ret-outside-income">—</strong></div><div><span>Portfolio withdrawal needed</span><strong id="ret-funding-gap">—</strong></div><div><span>Expected return after fees</span><strong id="ret-result-return">—</strong></div><div><span>First-year portfolio withdrawal</span><strong id="ret-result-implied-withdrawal">—</strong><small id="ret-withdrawal-explanation">First-year funding gap ÷ liquid portfolio. Descriptive only—not a recommended safe withdrawal rate.</small></div><div><span>Net return after withdrawal</span><strong id="ret-result-net-return">—</strong><small id="ret-net-return-explanation">Expected return minus first-year portfolio withdrawal.</small></div></div>
        </section>
        </div>
        <p class="hint" id="ret-result-assumptions">Planning estimate only; not financial, tax, legal, immigration, healthcare, or investment advice.</p>
      </section>
    <section class="calc-panel current-cost-comparison" id="ret-current-cost-comparison" hidden aria-labelledby="ret-current-cost-heading">
      <h2 id="ret-current-cost-heading">Compare with where you live now</h2>
      <p class="hint">Use your household's current monthly spending, including housing, in today's USD. This comparison does not change your retirement estimate.</p>
      <div class="current-cost-layout">
        <div class="field-grid">
          <div class="field"><label for="ret-current-location">Current location <span class="optional-label">(optional)</span></label><input id="ret-current-location" type="text" autocomplete="address-level2" placeholder="For example, London"></div>
          <div class="field"><label for="ret-current-monthly-spending">Current monthly spending</label><input id="ret-current-monthly-spending" type="number" min="1" step="1" inputmode="decimal" placeholder="Enter amount"><p class="hint">Include housing and use the same household basis as the destination estimate.</p></div>
        </div>
        <div class="current-cost-result" id="ret-current-cost-result" hidden aria-live="polite">
          <p class="current-cost-summary" id="ret-current-cost-summary"></p>
          <p class="current-cost-annual" id="ret-current-cost-annual"></p>
          <div class="current-cost-bars" id="ret-current-cost-bars">
            <div class="current-cost-row"><div class="current-cost-bar-heading"><strong id="ret-current-cost-label">Where you live now</strong><span id="ret-current-cost-amount"></span></div><div class="current-cost-track" aria-hidden="true"><span class="current-cost-fill" id="ret-current-cost-bar"></span></div></div>
            <div class="current-cost-row destination"><div class="current-cost-bar-heading"><strong id="ret-current-cost-destination-label">Destination</strong><span id="ret-current-cost-destination-amount"></span></div><div class="current-cost-track" aria-hidden="true"><span class="current-cost-fill" id="ret-current-cost-destination-bar"></span></div></div>
          </div>
          <div class="target-comparison">
            <h3>Retirement funding target</h3>
            <div class="target-figures"><div><span id="ret-current-target-label">Where you live now</span><strong id="ret-current-target"></strong></div><div><span id="ret-destination-target-label">Destination</span><strong id="ret-destination-target"></strong></div></div>
            <p class="target-difference" id="ret-target-difference"></p>
            <p class="hint">Liquid portfolio plus emergency reserve, using the same planning assumptions. Excludes any separate home purchase.</p>
          </div>
          <p class="hint">A directional comparison, not a like-for-like purchasing-power or tax analysis.</p>
        </div>
      </div>
    </section>
    <dialog class="cost-sidecar" id="ret-cost-sidecar" aria-labelledby="ret-cost-sidecar-title">
      <div class="cost-sidecar-panel"><header class="cost-sidecar-header"><div><h2 id="ret-cost-sidecar-title">Compare monthly living expenses</h2><p class="hint" id="ret-cost-sidecar-context"></p></div><button class="cost-sidecar-close" id="ret-cost-sidecar-close" type="button" aria-label="Close destination comparison">Close</button></header><div class="cost-sidecar-chart" id="ret-cost-sidecar-chart"></div></div>
    </dialog>
    <noscript><p class="calc-panel"><strong>The interactive calculator requires JavaScript.</strong> You can still review the destination cost ranking and methodology using the links below.</p></noscript>
    <section class="content-section"><h2>How to read this estimate</h2><p>The model projects destination expenses and reliable retirement income, then shows the portfolio, reserve, and property capital needed under the return you enter. Portfolio dividends and interest belong inside that expected return rather than being counted again as outside income.</p><p class="related"><a href="/retirement-destination-finder/">Find destinations your plan can support</a><a href="/retirement-destinations-ranked-by-cost/" data-track="retirement_calculator_guide_click">Compare destination retirement costs</a><a href="/methodology/">Read the methodology</a><a href="/buying-property-abroad-for-retirement/" data-track="retirement_calculator_guide_click">Plan a retirement property purchase</a></p></section>
    <section class="content-section faq"><h2>Frequently asked questions</h2>__FAQ__</section>
  </div></main>
  <footer><div class="calc-shell">Global Home Atlas · Research for overseas property and long-stay decisions · <a href="/contact/">Contact</a></div></footer>
  <script id="retirement-destination-data" type="application/json">__DATA__</script>
  <script>__ENGINE__</script>
  <script>__UI__</script>
__ANALYTICS__
  <script>if(window.GHARetirementCalculatorUI){window.GHARetirementCalculatorUI.initRetirementCalculator("retirement-calculator",JSON.parse(document.getElementById("retirement-destination-data").textContent));}</script>
</body></html>"""
    replacements = {
        "__HEAD__": head_html(RETIREMENT_CALCULATOR_TITLE, RETIREMENT_CALCULATOR_DESCRIPTION, canonical, schema_for_retirement_calculator(canonical)),
        "__OPTIONS__": "".join(options),
        "__BENCHMARK_PANELS__": benchmark_panels,
        "__AS_OF__": escape(retirement_payload["as_of"]),
        "__SOURCES__": "".join(source_links),
        "__FAQ__": faq_html,
        "__DATA__": page_data,
        "__ENGINE__": engine_js,
        "__UI__": ui_js,
        "__ANALYTICS__": analytics_event_script(),
    }
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html


def build_retirement_destinations_article(destinations: list[dict], retirement_payload: dict) -> str:
    canonical = page_url(RETIREMENT_DESTINATIONS_SLUG)
    rankings = retirement_destination_rankings(destinations, retirement_payload)
    visible_rankings, expandable_rankings = split_rankings(rankings)
    ranking_header = """<thead><tr>
      <th scope="col" aria-sort="none"><button type="button" class="sort-button" data-sort-key="rank"><span>Cost rank</span><span class="sort-indicator" aria-hidden="true">↕</span></button></th>
      <th scope="col" aria-sort="none"><button type="button" class="sort-button" data-sort-key="atlas"><span>Atlas rank</span><span class="sort-indicator" aria-hidden="true">↕</span></button></th>
      <th scope="col" aria-sort="none"><button type="button" class="sort-button" data-sort-key="name"><span>Destination</span><span class="sort-indicator" aria-hidden="true">↕</span></button></th>
      <th scope="col" aria-sort="none"><button type="button" class="sort-button" data-sort-key="annual"><span>Annual cost incl. rent</span><span class="sort-indicator" aria-hidden="true">↕</span></button></th>
      <th scope="col" aria-sort="ascending"><button type="button" class="sort-button" data-sort-key="savings"><span>Savings needed</span><span class="sort-indicator" aria-hidden="true">↑</span></button></th>
      <th scope="col" aria-sort="none"><button type="button" class="sort-button" data-sort-key="property"><span>Home purchase estimate</span><span class="sort-indicator" aria-hidden="true">↕</span></button></th>
    </tr></thead>"""
    table_rows = []
    destination_notes = []
    source_links = []
    for rank, item in enumerate(rankings, start=1):
        destination = item["destination"]
        record = item["record"]
        metrics = item["metrics"]
        slug = destination_slug(destination)
        table_rows.append(
            f"""
            <tr class="ranking-row" data-rank="{rank}" data-atlas="{destination["rank"]}" data-name="{escape(destination["name"])}" data-annual="{metrics["annual_spending"]}" data-savings="{metrics["required_capital"]}" data-property="{metrics["property_capital"]}">
              <td>{rank}</td>
              <td>{destination["rank"]}</td>
              <th scope="row"><a href="/destinations/{escape(slug)}/">{escape(destination["name"])}</a><br><span>{escape(destination.get("country") or "")}</span></th>
              <td>{money(metrics["annual_spending"])}</td>
              <td><strong>{money(metrics["required_capital"])}</strong></td>
              <td>{money(metrics["property_capital"])}</td>
            </tr>
            """.rstrip()
        )
        destination_notes.append(
            f"""
            <li>
              <div class="destination-note-heading"><span>{rank}</span><h3><a href="/destinations/{escape(slug)}/">{escape(destination["name"])}</a> <small>{escape(destination.get("country") or "")}</small></h3><strong>{money(metrics["required_capital"])}</strong></div>
              <p>{escape(destination.get("panel_summary") or "Review the destination dossier for lifestyle, ownership, access, and resale context.")}</p>
            </li>
            """.rstrip()
        )
        first_source = record["sources"][0]
        source_links.append(
            f'<li><a href="{escape(first_source["url"])}" rel="nofollow noopener">{escape(first_source["name"])}</a> '
            f'— {escape(first_source["metric_supported"])} ({escape(first_source["source_date"])})</li>'
        )

    visible_rows = "".join(table_rows[: len(visible_rankings)])
    expandable_rows = "".join(table_rows[len(visible_rankings) :])
    top_destination_notes = "".join(destination_notes[: len(visible_rankings)])
    lowest = rankings[0]["metrics"]["required_capital"]
    highest = rankings[-1]["metrics"]["required_capital"]
    lowest_name = rankings[0]["destination"]["name"]
    highest_name = rankings[-1]["destination"]["name"]
    faq_html = build_faq_html(RETIREMENT_DESTINATIONS_FAQS)
    ranking_js = RETIREMENT_RANKING_TABLE_PATH.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
    html = f"""<!doctype html>
<html lang="en">
<head>
{head_html(RETIREMENT_DESTINATIONS_TITLE, RETIREMENT_DESTINATIONS_DESCRIPTION, canonical, schema_for_retirement_destinations_article(canonical, rankings))}
  <meta property="og:image" content="{SITE_URL}assets/retirement-destinations-required-capital.png">
  <meta property="og:image:width" content="1600">
  <meta property="og:image:height" content="900">
  <style>
{shared_content_css()}
    .page-hero {{ padding-bottom: 48px; }}
    .page-hero-grid {{ grid-template-columns: minmax(0, 820px); }}
    .page-hero h1 {{ font-size: clamp(40px, 6vw, 72px); }}
    .page-actions {{ display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 22px; }}
    .page-button-secondary {{ border: 1px solid var(--teal); background: rgba(255, 253, 247, .76); color: var(--ink); }}
    main {{ margin-top: 0; }}
    .article-toc {{ max-width: 820px; display: flex; flex-wrap: wrap; gap: 10px 18px; margin: 0 auto; padding: 18px 0; border-bottom: 1px solid var(--line); }}
    .article-toc span {{ color: var(--muted); font-size: 13px; font-weight: 850; }}
    .article-toc a {{ font-size: 13px; font-weight: 800; }}
    .article-layout {{ max-width: 820px; margin: 0 auto; padding: 20px 0 58px; }}
    .article-body {{ min-width: 0; }}
    .article-section {{ min-width: 0; padding: 30px 0; border-bottom: 1px solid var(--line); }}
    .article-section h2 {{ margin: 0 0 12px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 4vw, 40px); line-height: 1.05; }}
    .article-section h3 {{ margin: 18px 0 8px; }}
    .article-section p {{ color: #3f4d48; }}
    .article-callout {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-top: 22px; padding: 18px 0; border-top: 1px solid var(--line); }}
    .article-callout strong {{ display: block; margin-bottom: 4px; font-size: 17px; }}
    .article-callout p {{ margin: 0; font-size: 14px; }}
    .table-wrap {{ width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }}
    table {{ width: 100%; min-width: 680px; border-collapse: collapse; background: #fff; }}
    caption {{ padding: 14px; text-align: left; font-weight: 850; }}
    th, td {{ padding: 12px; border-top: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 13px; }}
    thead th {{ color: var(--muted); font-size: 11px; letter-spacing: .05em; text-transform: uppercase; }}
    .sort-button {{ display: inline-flex; align-items: center; gap: 5px; width: 100%; padding: 0; border: 0; background: transparent; color: inherit; font: inherit; font-weight: 850; letter-spacing: inherit; text-align: left; text-transform: inherit; cursor: pointer; }}
    .sort-button:focus-visible {{ outline: 3px solid var(--gold); outline-offset: 4px; }}
    .sort-indicator {{ color: var(--teal); font-size: 14px; line-height: 1; }}
    tbody th span {{ color: var(--muted); font-weight: 600; }}
    .ranking-more {{ margin-top: 18px; }}
    .ranking-more > summary {{ display: inline-block; padding: 8px 0; color: var(--teal); font-weight: 850; cursor: pointer; }}
    .ranking-more > summary:focus-visible {{ outline: 3px solid var(--gold); outline-offset: 4px; }}
    .ranking-more .table-wrap {{ margin-top: 10px; }}
    .infographic {{ margin: 18px 0 0; }}
    .infographic img {{ display: block; width: 100%; height: auto; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }}
    .infographic figcaption {{ margin-top: 10px; color: var(--muted); font-size: 13px; line-height: 1.5; }}
    .download-link {{ display: inline-flex; margin-top: 10px; font-weight: 850; }}
    .destination-notes {{ margin: 18px 0 0; padding: 0; list-style: none; border-top: 1px solid var(--line); }}
    .destination-notes li {{ padding: 20px 0; border-bottom: 1px solid var(--line); }}
    .destination-note-heading {{ display: grid; grid-template-columns: 32px minmax(0, 1fr) auto; gap: 10px; align-items: baseline; }}
    .destination-note-heading span {{ color: var(--gold); font-weight: 900; }}
    .destination-note-heading h3 {{ margin: 0; }}
    .destination-note-heading small {{ margin-left: 6px; color: var(--muted); font-family: Inter, ui-sans-serif, system-ui, sans-serif; font-size: 12px; font-weight: 700; }}
    .destination-note-heading strong {{ font-size: 14px; }}
    .destination-notes p {{ margin: 8px 0 0 42px; }}
    .article-related {{ display: flex; flex-wrap: wrap; gap: 10px 18px; margin-top: 18px; }}
    .article-related a {{ font-weight: 800; }}
    .method-list {{ padding-left: 20px; }}
    .source-more {{ margin-top: 18px; border-top: 1px solid var(--line); padding-top: 12px; }}
    .source-more > summary {{ color: var(--teal); font-weight: 800; cursor: pointer; }}
    .source-more > summary:focus-visible {{ outline: 3px solid var(--gold); outline-offset: 4px; }}
    .source-list {{ overflow-wrap: anywhere; }}
    @media (max-width: 560px) {{ .article-callout {{ align-items: flex-start; flex-direction: column; }} .destination-note-heading {{ grid-template-columns: 28px minmax(0, 1fr); }} .destination-note-heading strong {{ grid-column: 2; }} .destination-notes p {{ margin-left: 38px; }} }}
  </style>
</head>
<body>
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <h1>{RETIREMENT_DESTINATIONS_H1}</h1>
          <p class="page-lede">All 30 Global Home Atlas retirement destinations compared under one transparent scenario. The rank answers a narrow financial question—how much capital a couple renting would need—not which place offers the best life.</p>
          <div class="page-actions"><a class="page-button" href="/{RETIREMENT_CALCULATOR_SLUG}/" data-track="retirement_calculator_open" data-track-label="ranked retirement article hero">Calculate your plan</a><a class="page-button page-button-secondary" href="/{RETIREMENT_FINDER_SLUG}/">Find destinations I can afford</a><a class="page-button page-button-secondary" href="#ranking">View rankings</a></div>
        </div>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <nav class="article-toc" aria-label="In this article"><span>In this article</span><a href="#ranking">Ranking</a><a href="#components">What drives the cost</a><a href="#destinations">Destination notes</a><a href="#methodology">Methodology</a><a href="#faq">FAQ</a></nav>
      <div class="article-layout">
        <article class="article-body">
          <section class="article-section" id="quick-answer"><h2>The quick answer</h2><p>Among the 30 destinations, {escape(lowest_name)} has the lowest modeled requirement at <strong>{money(lowest)}</strong>, while {escape(highest_name)} has the highest at <strong>{money(highest)}</strong>. The gap is driven by recurring annual spending because the ranking assumes renting and funds the spending gap from a liquid portfolio.</p><p>This is not a list of every cheap place to retire. It compares the 30 Global Home Atlas destinations with complete retirement-cost coverage, using the same researched inputs as our retirement planning model.</p><aside class="article-callout"><div><strong>Make the estimate personal</strong><p>Add your retirement date, expenses, pension, passive income, and housing plan.</p></div><a class="page-button" href="/{RETIREMENT_CALCULATOR_SLUG}/" data-track="retirement_calculator_open" data-track-label="ranked retirement article callout">Open calculator</a></aside></section>
          <section class="article-section" id="ranking"><h2>Retirement destinations ranked by savings needed</h2><p>Each row uses today's USD and the same assumptions. The home purchase estimate is optional and does not affect the cost rank. Select a column heading to reorder all 30 destinations.</p><details class="source-more"><summary>How annual cost is estimated</summary><p>Annual cost includes rent, food and household spending, utilities and communications, private healthcare, transport, dining and leisure, travel, visa and administration costs, and contingency. Home purchase costs are separate.</p></details><div class="table-wrap"><table><caption>Estimated retirement savings by destination for a couple renting</caption>{ranking_header}<tbody data-ranking-visible>{visible_rows}</tbody></table></div>
            <details class="ranking-more"><summary>View 20 more destinations</summary><div class="table-wrap"><table><caption>Additional retirement destinations</caption>{ranking_header}<tbody data-ranking-additional>{expandable_rows}</tbody></table></div></details>
            <figure class="infographic"><img src="/assets/retirement-destinations-required-capital.png" width="1600" height="900" alt="Lowest-cost 10 of 30 retirement destinations ranked by required capital for a couple renting" loading="eager"><figcaption>This chart shows the lowest-cost 10 of 30. Required capital combines the liquid portfolio and 12-month reserve; property is excluded from rank. Complete ranks 1–30 are in the tables above.</figcaption><a class="download-link" href="/assets/retirement-destinations-required-capital.png" download data-track="infographic_download" data-track-label="required retirement capital ranking">Download this infographic as PNG</a></figure>
          </section>
          <section class="article-section" id="components"><h2>Why the capital figures differ</h2><p>Required liquid portfolio capital magnifies differences in annual spending: at a 3.5% withdrawal rate, every additional $10,000 of first-year spending adds about $285,700 to the modeled portfolio. The emergency reserve then adds another year of expenses.</p><p>Property capital tells a different story. It combines the representative purchase price with estimated acquisition costs and can be much higher—or much lower—than the cost rank suggests. It is shown separately because buying is optional and listing samples are not market-wide medians.</p>
            <figure class="infographic"><img src="/assets/retirement-destinations-capital-breakdown.png" width="1600" height="900" alt="Capital breakdown for the lowest-cost 10 of 30 retirement destinations" loading="lazy"><figcaption>This chart shows the lowest-cost 10 of 30. Living-cost funding and optional property acquisition are separate decisions. Complete ranks 1–30 are in the tables above.</figcaption><a class="download-link" href="/assets/retirement-destinations-capital-breakdown.png" download data-track="infographic_download" data-track-label="retirement capital breakdown">Download the capital breakdown as PNG</a></figure>
          </section>
          <section class="article-section" id="destinations"><h2>What to know about the top 10</h2><p>The cost rank is a starting point, not a recommendation. Visa eligibility, taxes, healthcare access, language, neighborhood choice, climate, ownership rules, and resale depth require separate review.</p><ol class="destination-notes">{top_destination_notes}</ol></section>
          <section class="article-section" id="destinations-not-countries"><h2>Destinations, not countries</h2><p>Country averages hide the decision retirees actually make. Valencia and Málaga share Spain's national framework, while Fukuoka / Itoshima and Hakone / Izu share Japan's, but housing, transport, access, and daily routines differ locally. We therefore rank destinations and keep the country visible as legal, tax, visa, and healthcare context.</p><p>The ranking does not rank lifestyle quality. A higher-cost destination may be the better personal fit, and a lower-cost destination can carry trade-offs that matter more than the savings.</p></section>
          <section class="article-section" id="methodology"><h2>Methodology and assumptions</h2><p>The ranking models a couple renting, with retirement starting today. It is designed for comparison rather than personal advice.</p><ul class="method-list"><li>30-year retirement horizon.</li><li>3.5% withdrawal rate.</li><li>12 months of expenses held as an emergency reserve.</li><li>No pension or other passive income.</li><li>Comfortable, not luxury, destination budgets in today's USD.</li><li>Liquid portfolio equals annual spending divided by 3.5%.</li><li>Required retirement capital equals liquid portfolio plus the reserve.</li><li>Property capital equals representative purchase price plus acquisition costs and is excluded from rank.</li></ul><p>Portfolio dividends and interest are already part of the portfolio withdrawal and must not be subtracted again as passive income. Reliable after-tax pension, annuity, business, or net rental income can reduce your personal funding gap in the <a href="/{RETIREMENT_CALCULATOR_SLUG}/">calculator</a>.</p><p>See the full <a href="/methodology/">research methodology</a>. Data reviewed {escape(retirement_payload["as_of"])}.</p><details class="source-more"><summary>Sources and data notes</summary><ul class="source-list">{''.join(source_links)}</ul></details></section>
          <section class="article-section"><h2>Use the ranking without over-reading it</h2><p>Start with the cost range, then test a personal scenario. Change household spending, retirement date, pension and passive income, housing plan, inflation, and planning horizon before comparing property. A financially viable location can still fail on residency, tax, healthcare, or day-to-day fit.</p><p>Continue with <a href="/best-places-to-buy-property-abroad-for-retirement/">the retirement property destination guide</a>, then open destination dossiers and consult qualified local legal, tax, immigration, healthcare, and financial advisers before acting.</p><nav class="article-related" aria-label="Related research"><a href="/buying-property-abroad-for-retirement/">Buying abroad for retirement</a><a href="/guides/">All guides</a><a href="/methodology/">Research methodology</a></nav></section>
          <section class="article-section faq" id="faq"><h2>Frequently asked questions</h2>{faq_html}</section>
        </article>
      </div>
    </div>
  </main>
  <footer class="page-footer"><div class="page-shell"><strong>{SITE_NAME}</strong><p>Research for overseas property and long-stay decisions. Planning estimates are not financial, tax, legal, immigration, healthcare, or investment advice.</p><nav><a href="/guides/">Guides</a> <a href="/methodology/">Methodology</a> <a href="/contact/">Contact</a></nav></div></footer>
{analytics_event_script()}
  <script>{ranking_js}</script>
  <script>if(window.GHARetirementRankingTable){{window.GHARetirementRankingTable.initRetirementRankingTable(document.getElementById("ranking"));}}</script>
</body>
</html>"""
    return html


def build_guide_hub_page(pages: list[dict], destinations: list[dict]) -> str:
    canonical = page_url(GUIDE_HUB_SLUG)
    updated = date.today().isoformat()
    clusters = [
        (
            "Getting Started",
            "Start here if you are defining the role of the property and the markets worth researching before speaking with agents.",
            [
                "buy-property-abroad",
                "best-countries-to-buy-property-as-a-foreigner",
                "where-can-foreigners-buy-property",
            ],
        ),
        (
            "Retirement",
            "Research long-stay livability, healthcare practicality, family use, and the flexibility to retire there later.",
            [
                RETIREMENT_DESTINATIONS_SLUG,
                "best-places-to-buy-property-abroad-for-retirement",
                "buying-property-abroad-for-retirement",
                "japan-retirement-property-foreign-buyers",
            ],
        ),
        (
            "Second Homes",
            "Compare seasonal use, family travel, repeat access, realistic rental offset, and future resale flexibility.",
            [
                "best-places-to-buy-a-second-home-abroad",
                "best-places-to-buy-vacation-home-abroad",
                "best-places-to-buy-property-in-europe",
            ],
        ),
        (
            "Risk",
            "Understand the ownership, regulatory, income, and exit risks that deserve attention before capital is committed.",
            [
                "foreign-property-investment-risks",
                "thailand-villa-ownership-foreigners",
                "overseas-property-investment",
            ],
        ),
        (
            "Country Comparisons",
            "Compare jurisdictions before moving on to local legal, tax, and property-specific diligence.",
            [
                "portugal-vs-spain-retirement-property",
                "greece-vs-portugal-retirement-property",
                "best-countries-for-expats-to-buy-property",
            ],
        ),
        (
            "Investment",
            "Test yield realism, entry value, governance risk, and exit liquidity alongside lifestyle value.",
            [
                "overseas-property-investment",
                "best-places-to-buy-property-in-europe",
                "foreign-property-investment-risks",
            ],
        ),
    ]
    cluster_html = "\n".join(
        f"""
          <section class="page-section" id="{slugify(title)}">
            <h2>{escape(title)}</h2>
            <p>{escape(description)}</p>
            <div class="guide-story-grid">{guide_story_list_for_slugs(slugs, pages)}</div>
          </section>
        """
        for title, description, slugs in clusters
    )
    country_links = country_hub_links(limit=7)
    featured_page = next((page for page in pages if page["slug"] == RETIREMENT_DESTINATIONS_SLUG), pages[0])

    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(GUIDE_HUB_TITLE, GUIDE_HUB_DESCRIPTION, canonical, schema_for_guide_hub(canonical, pages))}
  <style>
{shared_content_css()}
    .guide-page-hero {{ min-height: 430px; background-position: center; }}
    .guide-page-hero .page-hero-grid {{ grid-template-columns: minmax(0, 720px); }}
    .guide-page-layout {{ display: block; max-width: 980px; margin: 0 auto; padding-top: 42px; }}
    .guide-page-layout .page-article {{ gap: 56px; }}
    .guide-section-nav {{ display: flex; gap: 22px; margin: 0; padding: 15px 0; overflow-x: auto; border-bottom: 1px solid var(--line); font-size: 12px; font-weight: 800; letter-spacing: .045em; white-space: nowrap; scrollbar-width: thin; }}
    .guide-section-nav a {{ color: var(--ink); text-decoration: none; }}
    .guide-section-nav a:hover {{ color: var(--gold); }}
    .guide-kicker {{ margin: 0 0 12px; color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .1em; text-transform: uppercase; }}
    .guide-intro {{ max-width: 720px; }}
    .guide-intro h2 {{ margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(28px, 4.3vw, 44px); line-height: 1.02; }}
    .journey-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 26px; margin-top: 28px; }}
    .journey-card {{ min-width: 0; padding-top: 15px; border-top: 1px solid var(--ink); color: var(--ink); text-decoration: none; }}
    .journey-card span {{ display: block; color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .journey-card strong {{ display: block; margin: 14px 0 8px; font-family: Georgia, "Times New Roman", serif; font-size: 22px; font-weight: 700; line-height: 1.05; }}
    .journey-card p {{ margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }}
    .guide-feature {{ display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(260px, .9fr); gap: 34px; align-items: stretch; padding: 28px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
    .guide-feature__image {{ min-height: 330px; background: linear-gradient(150deg, rgba(36,49,45,.1), rgba(36,49,45,.46)), url("/assets/destination-dossier-coast.jpg"); background-position: center; background-size: cover; }}
    .guide-feature__copy {{ display: flex; flex-direction: column; justify-content: center; }}
    .guide-feature__copy h2 {{ margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(31px, 4vw, 47px); line-height: 1.01; }}
    .guide-feature__copy p {{ color: #3f4d48; }}
    .guide-text-link {{ display: inline-block; align-self: flex-start; margin-top: 14px; color: var(--ink); font-size: 13px; font-weight: 900; text-decoration: none; border-bottom: 1px solid currentColor; }}
    .guide-country-links {{ display: flex; flex-wrap: wrap; gap: 9px 18px; margin-top: 18px; }}
    .guide-country-links a {{ font-weight: 800; }}
    .guide-catalog {{ display: grid; gap: 46px; }}
    .guide-catalog .page-section {{ padding: 0; border: 0; background: transparent; }}
    .guide-catalog .page-section > p {{ max-width: 650px; margin-top: 0; }}
    .guide-story-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; margin-top: 22px; }}
    .guide-story {{ min-width: 0; padding-top: 15px; border-top: 3px solid var(--gold); }}
    .guide-story:nth-child(2) {{ border-top-color: var(--eucalyptus); }} .guide-story:nth-child(3) {{ border-top-color: var(--terracotta); }}
    .guide-story span {{ color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .guide-story h3 {{ margin: 9px 0; font-family: Georgia, "Times New Roman", serif; font-size: 24px; line-height: 1.06; }}
    .guide-story p {{ margin: 0; color: var(--muted); font-size: 14px; line-height: 1.5; }}
    .guide-story__link {{ display: inline-block; margin-top: 12px; font-size: 13px; font-weight: 900; }}
    .guide-research-note {{ padding: 20px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
    .guide-research-note p {{ max-width: 710px; margin: 0; color: #3f4d48; }}
    @media (max-width: 860px) {{ .journey-grid, .guide-story-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .guide-feature {{ grid-template-columns: 1fr; gap: 24px; }} .guide-feature__image {{ min-height: min(54vw, 390px); }} }}
    @media (max-width: 560px) {{ .guide-page-hero {{ min-height: 350px; }} .guide-section-nav {{ gap: 17px; margin: 0 -2px; padding: 13px 2px; }} .journey-grid, .guide-story-grid {{ grid-template-columns: 1fr; gap: 22px; }} .guide-page-layout {{ padding-top: 26px; }} .guide-page-layout .page-article {{ gap: 38px; }} .journey-card {{ padding-top: 13px; }} .guide-feature {{ padding: 22px 0; }} .guide-feature__image {{ min-height: 250px; }} .guide-feature__copy h2 {{ font-size: 34px; }} }}
  </style>
</head>
<body>
  <header class="page-hero guide-page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">Global Property Buying Guides · updated {updated}</p>
          <h1>A considered guide to buying a home abroad</h1>
          <p class="page-lede">Stories, places, and practical perspective for the life you are planning next.</p>
        </div>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <nav class="guide-section-nav" aria-label="Guide sections"><a href="#choose-journey">Start here</a><a href="#featured-research">Featured story</a><a href="#retirement">Retirement</a><a href="#second-homes">Second homes</a><a href="#investment">Investment</a><a href="#country-comparisons">Places</a></nav>
      <div class="page-layout guide-page-layout">
        <article class="page-article">
          <section id="choose-journey">
            <div class="guide-intro">
              <p class="guide-kicker">Where to begin</p>
              <h2>Choose the question that matters most to you.</h2>
            </div>
            <div class="journey-grid">
              <a class="journey-card" href="#retirement" data-track="guide_journey_click" data-track-label="Retirement"><span>A new chapter</span><strong>Retirement or lifestyle base</strong><p>Healthcare, climate, community, and the rhythm of daily life.</p></a>
              <a class="journey-card" href="#second-homes" data-track="guide_journey_click" data-track-label="Second homes"><span>A second address</span><strong>Second home abroad</strong><p>Family time, repeat stays, and ownership that feels uncomplicated.</p></a>
              <a class="journey-card" href="#investment" data-track="guide_journey_click" data-track-label="Investment"><span>A thoughtful investment</span><strong>Investment-led shortlist</strong><p>Value, income, regulation, and the quality of your eventual exit.</p></a>
              <a class="journey-card" href="#risk" data-track="guide_journey_click" data-track-label="Ownership and risk"><span>Before you commit</span><strong>Ownership and risk first</strong><p>Rules, taxes, title, and the questions worth settling early.</p></a>
            </div>
          </section>
          {retirement_calculator_callout("guide-research-note", "guide hub")}
          <section class="guide-feature" id="featured-research">
            <div class="guide-feature__image" role="img" aria-label="Coastal destination landscape"></div>
            <div class="guide-feature__copy">
              <p class="guide-kicker">The featured story</p>
              <h2>{escape(featured_page["h1"])}</h2>
              <p>{escape(featured_page["description"])}</p>
              <a class="guide-text-link" href="/{escape(featured_page["slug"])}/">Read the story</a>
            </div>
          </section>
          <section class="guide-research-note">
            <p><strong>How to read the Atlas:</strong> Use each guide to form a shortlist, then compare destination evidence and local professional advice before you commit to a property.</p>
          </section>
          <section>
            <p class="guide-kicker">Browse by country</p>
            <h2>Country and region hubs</h2>
            <nav class="guide-country-links">{country_links}</nav>
          </section>
          <section class="guide-catalog" aria-label="Browse all buying guides">{cluster_html}</section>
        </article>
      </div>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Global property destination research for lifestyle-led investors and long-term planners.</p>
      <nav>{seo_guide_links(pages, limit=8)} {trust_page_links()}</nav>
    </div>
  </footer>
{analytics_event_script()}
</body>
</html>
"""


def schema_for_country_hub(hub: dict, selected: list[dict], canonical: str) -> list[dict]:
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": hub["h1"],
            "url": canonical,
            "description": hub["description"],
            "dateModified": date.today().isoformat(),
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": index + 1,
                        "name": dest["name"],
                        "url": destination_url(dest),
                    }
                    for index, dest in enumerate(selected)
                ],
            },
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Countries", "item": f"{SITE_URL}guides/"},
                {"@type": "ListItem", "position": 3, "name": hub["country"], "item": canonical},
            ],
        },
    ]


def country_destination_cards(destinations: list[dict]) -> str:
    cards = []
    for dest in destinations:
        cards.append(
            f"""
            <article class="page-card">
              <span>#{dest["rank"]} global rank</span>
              <h3><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></h3>
              <p>{escape(dest.get("panel_verdict") or dest.get("panel_summary") or "")}</p>
              <ul>
                <li>Decision score: {dest.get("decision_score", 0):.1f}/5</li>
                <li>Ownership clarity: {metric_value(dest, "ownership_clarity"):.1f}/5</li>
                <li>Retirement fit: {metric_value(dest, "retirement_fit"):.1f}/5</li>
                <li>Entry benchmark: {money(dest.get("usd_per_m2"))}/m2</li>
              </ul>
            </article>
            """.rstrip()
        )
    return "\n".join(cards)


def country_destination_mobile_cards(destinations: list[dict]) -> str:
    cards = []
    for dest in destinations:
        cards.append(
            f"""
            <article class="comparison-card">
              <div class="comparison-card__head">
                <span>#{dest["rank"]}</span>
                <h3><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></h3>
              </div>
              <dl>
                <div><dt>Score</dt><dd>{dest.get("decision_score", 0):.1f}/5</dd></div>
                <div><dt>Ownership</dt><dd>{metric_value(dest, "ownership_clarity"):.1f}/5</dd></div>
                <div><dt>Retirement</dt><dd>{metric_value(dest, "retirement_fit"):.1f}/5</dd></div>
                <div><dt>Exit</dt><dd>{metric_value(dest, "exit_liquidity"):.1f}/5</dd></div>
              </dl>
              <p>{escape(dest.get("panel_verdict") or "")}</p>
            </article>
            """.rstrip()
        )
    return f'<div class="mobile-comparison-cards" aria-label="Mobile destination comparison">{"".join(cards)}</div>'


def country_destination_table(destinations: list[dict]) -> str:
    rows = []
    for dest in destinations:
        rows.append(
            f"""
            <tr>
              <td><strong><a href="/destinations/{escape(destination_slug(dest))}/">{escape(dest["name"])}</a></strong><br><span>{escape(dest.get("category") or "")}</span></td>
              <td>{dest.get("decision_score", 0):.1f}/5</td>
              <td>{metric_value(dest, "ownership_clarity"):.1f}/5</td>
              <td>{metric_value(dest, "retirement_fit"):.1f}/5</td>
              <td>{metric_value(dest, "exit_liquidity"):.1f}/5</td>
              <td>{escape(dest.get("panel_verdict") or "")}</td>
            </tr>
            """.rstrip()
        )
    return f"""
      <div class="comparison-table-wrap">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Destination</th>
              <th>Decision</th>
              <th>Ownership</th>
              <th>Retirement</th>
              <th>Exit</th>
              <th>Briefing read</th>
            </tr>
          </thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </div>
    """


def country_cluster_visual(destinations: list[dict]) -> str:
    chips = "\n".join(
        f"""
        <div>
          <span>#{dest["rank"]}</span>
          <strong>{escape(dest["name"])}</strong>
          <em>{dest.get("decision_score", 0):.1f}/5</em>
        </div>
        """.rstrip()
        for dest in destinations
    )
    return f"""
      <div class="cluster-map" aria-label="Destination cluster visual">
        <div class="cluster-map__grid">{chips}</div>
      </div>
    """


def destination_editorial_figure_html(
    image: dict[str, str], caption: str, figure_class: str = ""
) -> str:
    classes = f"{figure_class} destination-editorial-figure".strip()
    return (
        f'<figure class="{classes}">'
        f'<img src="{escape(image["src"])}" alt="{escape(image["alt"])}">'
        f'<figcaption>{escape(caption)}</figcaption></figure>'
    )


def country_guide_links(hub: dict, pages: list[dict]) -> str:
    by_slug = {page["slug"]: page for page in pages}
    links = []
    for slug in hub.get("guide_slugs", []):
        page = by_slug.get(slug)
        if page:
            links.append(f'<a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a>')
    return "\n".join(links)


def build_country_hub_page(
    hub: dict,
    destinations: list[dict],
    pages: list[dict],
    content_overrides: list[dict] | None = None,
) -> str:
    canonical = country_url(hub)
    hub = apply_content_override(hub, canonical, content_overrides or [])
    selected = destinations_for_ids(hub["destination_ids"], destinations)
    updated = date.today().isoformat()
    avg_score = sum(float(dest.get("decision_score", 0) or 0) for dest in selected) / max(1, len(selected))
    best = selected[0] if selected else destinations[0]
    guide_links = country_guide_links(hub, pages)
    peer_country_links = country_hub_links(hub["slug"], limit=6)
    report_title, report_reason = country_report_recommendation(hub)
    retirement_ids = {item["destination_id"] for item in load_retirement_costs()["destinations"]}
    retirement_callout = (
        retirement_calculator_callout("page-section", "country hub")
        if retirement_ids.intersection(hub["destination_ids"])
        else ""
    )
    intro = hub.get("generated_intro") or hub["description"]
    generated_link = generated_internal_link_html(hub)

    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(hub["title"], hub["description"], canonical, schema_for_country_hub(hub, selected, canonical))}
  <style>{shared_content_css()}</style>
</head>
<body class="has-mobile-actions">
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">{escape(hub["country"])} country hub · updated {updated}</p>
          <h1>{escape(hub["h1"])}</h1>
          <p class="page-lede">{escape(intro)}</p>
          {generated_link}
        </div>
        <aside class="page-hero-card">
          <span>Destinations compared</span><strong>{len(selected)}</strong>
          <span>Average score</span><strong>{avg_score:.1f}/5</strong>
          <span>Top match</span><strong>{escape(best["name"])}</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <section class="page-stats" aria-label="Country hub metrics">
        <div><span>Country</span><strong>{escape(hub["country"])}</strong></div>
        <div><span>Destinations</span><strong>{len(selected)}</strong></div>
        <div><span>Decision model</span><strong>{len(DIMENSIONS)} dimensions</strong></div>
        <div><span>Updated</span><strong>{updated}</strong></div>
      </section>
      {sticky_page_nav([("Thesis", "country-thesis"), ("Buyer Fit", "buyer-fit"), ("Brief", "premium-brief"), ("Compare", "destination-comparison"), ("Risk", "risk-posture"), ("Guides", "related-guides")])}
      {mobile_action_strip("#destination-comparison", "Compare", "/shortlist-review/", "Brief")}
      <section class="brief-panel" aria-label="Country briefing">
        <article><span>Top destination match</span><strong>{escape(best["name"])}</strong><p>{escape(best.get("panel_verdict") or "")}</p></article>
        <article><span>Buyer profile</span><strong>Affluent global planners</strong><p>Best for buyers comparing lifestyle use, legal clarity, tax and ownership friction, rental realism, and future liquidity before local deal work.</p></article>
        <article><span>Risk posture</span><strong>{metric_value(best, "ownership_clarity"):.1f}/5 ownership clarity</strong><p>Use country-level rules as the first screen, then verify title, taxes, rental permissions, and local transaction mechanics by asset.</p></article>
      </section>
      {trust_brief_html()}
      {country_next_step_html(hub, selected, pages)}
      <div class="page-layout">
        <article class="page-article">
          {retirement_callout}
          <details class="page-section" id="country-thesis" open>
            <summary><h2>Country Thesis</h2></summary>
            <p>{escape(hub["thesis"])}</p>
            <p>This page is a country-level filter for global buyers. Use it to decide whether {escape(hub["country"])} deserves deeper local diligence before comparing individual homes, agents, or legal structures.</p>
          </details>
          <details class="page-section" id="buyer-fit" open>
            <summary><h2>Buyer Fit</h2></summary>
            <div class="brief-panel">
              <article><span>Best for</span><strong>Lifestyle-led capital</strong><p>Buyers who value repeated owner use, healthcare and access, jurisdictional clarity, and a defensible resale path.</p></article>
              <article><span>Watch-outs</span><strong>Micro-market discipline</strong><p>Do not underwrite the country average. Local rules, asset condition, manager quality, and seasonality decide the actual result.</p></article>
              <article><span>Ownership clarity</span><strong>Verify locally</strong><p>Confirm title path, foreign-buyer restrictions, transfer taxes, rental licensing, inheritance treatment, and exit process before offers.</p></article>
            </div>
          </details>
          <details class="page-section" id="premium-brief" open>
            <summary><h2>Recommended Premium Brief</h2></summary>
            <div class="page-grid">
              <article class="page-card">
                <span>Best fit for {escape(hub["country"])}</span>
                <h3>{escape(report_title)}</h3>
                <p>{escape(report_reason)}</p>
                <a class="page-button" href="/reports/" data-track="country_report_cta" data-track-label="{escape(hub["country"])} {escape(report_title)}">View report options</a>
              </article>
              <article class="page-card">
                <span>Next step</span>
                <h3>Build a shortlist first</h3>
                <p>Save one or two {escape(hub["country"])} destinations in the dashboard, export the preview, then request a buyer-specific review.</p>
                <a class="page-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(hub["country"])} report prep">Open dashboard</a>
              </article>
            </div>
          </details>
          <details class="page-section" id="destination-comparison" open>
            <summary><h2>Destination Comparison</h2></summary>
            <p>Use this country table to compare score, ownership, retirement practicality, exit liquidity, and the briefing read before opening a destination dossier.</p>
            {country_cluster_visual(selected)}
            {country_destination_mobile_cards(selected)}
            {country_destination_table(selected)}
          </details>
          <details class="page-section" id="risk-posture" open>
            <summary><h2>How to Underwrite {escape(hub["country"])}</h2></summary>
            <ul>
              <li>Start with ownership clarity, transfer process, taxes, and whether the structure is simple enough to explain without informal assumptions.</li>
              <li>Stress-test the market for retirement fit, healthcare practicality, airport access, year-round services, and non-peak-season livability.</li>
              <li>Separate headline yield from realistic net income after manager quality, vacancy, repairs, taxes, licensing, furnishing, and currency movement.</li>
              <li>Plan exit liquidity before entry by checking buyer depth, comparable transactions, agent quality, and whether demand depends on one foreign-buyer group.</li>
            </ul>
          </details>
          <details class="page-section" id="related-guides" open>
            <summary><h2>Related Buying Guides</h2></summary>
            <nav class="page-grid">{guide_links}</nav>
          </details>
        </article>
        <details class="page-aside mobile-resources" open>
          <summary>More resources</summary>
          <section class="page-aside-card">
            <h2>Use the Atlas</h2>
              <p>Compare these destinations against the full destination model and export a shortlist memo.</p>
            <a class="page-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(hub["country"])} country hub">Open dashboard</a>
            <a class="page-button" href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(hub["country"])} country hub">Review my shortlist</a>
          </section>
          <section class="page-aside-card">
            <h3>Recommended Brief</h3>
            <p><strong>{escape(report_title)}</strong></p>
            <p>{escape(report_reason)}</p>
            <a class="page-button" href="/reports/" data-track="country_report_cta" data-track-label="{escape(hub["country"])} aside {escape(report_title)}">View reports</a>
          </section>
          <section class="page-aside-card">
            <h3>Other Country Hubs</h3>
            <nav>{peer_country_links}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Trust Layer</h3>
            <nav>{trust_page_links()}</nav>
          </section>
        </details>
      </div>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Country hubs are research inputs, not financial, legal, tax, immigration, or transaction advice.</p>
      <nav>{country_hub_links(hub["slug"], limit=6)} {seo_guide_links(pages, limit=4)}</nav>
    </div>
  </footer>
{mobile_disclosure_script()}
{analytics_event_script()}
</body>
</html>
"""


def build_seo_page(
    page: dict,
    destinations: list[dict],
    pages: list[dict],
    auto_links: list[dict] | None = None,
    content_overrides: list[dict] | None = None,
) -> str:
    canonical = page_url(page["slug"])
    page = apply_content_override(page, canonical, content_overrides or [])
    selected = destinations_for_page(page, destinations)
    top = selected[0]
    runner_up = selected[1] if len(selected) > 1 else selected[0]
    related_links = seo_guide_links(pages, page["slug"], limit=5)
    contextual_links = contextual_related_guides(page, pages, auto_links=auto_links)
    title = page["title"]
    description = page["description"]
    intro = page.get("generated_intro") or description
    generated_link = generated_internal_link_html(page)
    updated = date.today().isoformat()
    is_japan_article = is_japan_retirement_guide(page)
    is_spain_article = is_spain_retirement_guide(page)
    is_editorial_article = is_editorial_retirement_guide(page)
    country_count = len({item.get("country") for item in selected if item.get("country")})
    author_weight = 400 if is_editorial_article else 750
    published = escape(page.get("date_published", ""))
    author_dates = (
        f"Published {published} · Updated {updated}"
        if is_editorial_article
        else f"First published {published}"
    )
    author_html = (
        f'<p class="seo-byline" style="margin:12px 0 0;color:rgba(36,49,45,.68);font-size:13px;font-weight:{author_weight}">By {escape(page["author"])} · {author_dates}</p>'
        if page.get("author") and page.get("date_published")
        else ""
    )
    hero_eyebrow = "" if is_editorial_article else f'<p class="seo-eyebrow">{escape(page["theme"])} · updated {updated}</p>'
    hero_detail_html = f"{author_html}\n{generated_link}" if author_html else generated_link
    overview_html = seo_overview_html(page, selected)
    comparison_html = seo_comparison_html(page, selected, top, runner_up)
    destination_notes_html = seo_destination_notes_html(page, selected)
    decision_framework_html = seo_decision_framework_html(page)
    references_html = seo_references_html(page)
    retirement_callout = (
        retirement_calculator_callout("seo-section", "buying guide")
        if page["slug"] in {
            "buying-property-abroad-for-retirement",
            "best-places-to-buy-property-abroad-for-retirement",
            "japan-retirement-property-foreign-buyers",
            "spain-retirement-property-foreign-buyers",
        }
        else ""
    )
    seaside_life_figure = destination_editorial_figure_html(
        {
            "src": "/assets/fukuoka-itoshima-seaside-life.webp",
            "alt": "A quiet coastal lane, local produce and everyday seaside life in Itoshima",
        },
        "Itoshima · Everyday life keeps the coast close",
        "japan-inline-visual",
    )
    city_access_figure = destination_editorial_figure_html(
        {
            "src": "/assets/fukuoka-itoshima-city-access.webp",
            "alt": "Fukuoka waterfront promenade connecting calm public space with the compact city",
        },
        "Fukuoka · Waterfront calm with compact-city convenience",
        "japan-inline-visual",
    )
    spain_daily_life_figure = destination_editorial_figure_html(
        {
            "src": "/assets/spain-malaga-daily-life.webp",
            "alt": "A shaded Málaga neighborhood where residents walk past cafés and Mediterranean planting",
        },
        "Málaga · Daily life extends beyond the holiday season",
        "editorial-inline-visual",
    )
    spain_access_figure = destination_editorial_figure_html(
        {
            "src": "/assets/spain-mallorca-access-lifestyle.webp",
            "alt": "A lived-in Mallorcan coastal town with stone homes, local streets and the sea nearby",
        },
        "Mallorca · Island appeal works best with year-round services close by",
        "editorial-inline-visual",
    )
    editorial_content = ""
    if page["slug"] == "japan-retirement-property-foreign-buyers":
        editorial_content = f"""
          <section class="seo-section" id="lenses"><h2>Japan through five retirement lenses</h2><p>Japan is compelling for retirement not because it is cheap or effortless, but because a few places make daily life unusually dependable. We use the same ten-pillar methodology as the Atlas, grouped here into five questions that matter most when a home must work for months, not weekends.</p></section>
          <section class="seo-section"><h2>Live well, year after year</h2><p><a class="editorial-destination-link" href="/destinations/fukuoka-itoshima/">Fukuoka and Itoshima</a> are the strongest all-season answer: city hospitals, a serious food culture and Kyushu at the doorstep, with coast available when the day should slow down. Hakone and Izu exchange city energy for onsen, gardens and a Tokyo-adjacent rhythm. Hakuba and Niseko are more deliberate choices: outstanding winter, increasingly credible green-season activity, but a life shaped by snow and shoulder season.</p><p>Healthcare follows a sequence. A long-stay residence status comes first; then you register an address with the municipality. The Ministry of Health says eligible foreign residents, including those living in Japan for more than three months, can join the public system—through employee cover when employed, or National Health Insurance otherwise. A property deed does not create residency or coverage. Fukuoka therefore has the clearest retirement utility of the four, while a mountain or resort home asks you to accept longer journeys for specialist care and a more seasonal social calendar.</p>{seaside_life_figure}</section>
          <section class="seo-section"><h2>Reach it easily—and feel at home there</h2><p>Fukuoka wins on friction: JNTO notes that Hakata is a five-minute train ride from Fukuoka Airport. That changes how often a home gets used, and makes Korea, Taiwan and wider Asian connections genuinely convenient. Hakone and Izu work for Tokyo-based lives; Hakuba and Niseko require a winter-transfer plan, not a romantic assumption about the last mile.</p><p>Niseko has the most established international resort ecosystem and strong Chinese-speaking familiarity. Fukuoka offers deeper year-round urban services. In every location, Japanese remains the language of tradespeople, clinics and municipal administration; politeness is generous, but integration comes through repetition and language effort rather than an English-speaking bubble.</p>{city_access_figure}</section>
          <section class="seo-section"><h2>Own and operate cleanly</h2><p>Foreigners can generally own Japanese land and buildings freehold. That clarity is a real advantage, but it is separate from residency, financing and public-health eligibility. For a non-resident purchase, the Ministry of Finance says FEFTA reporting is generally required through the Bank of Japan within 20 days after acquisition. Real estate acquisition tax and registration licence tax are separate purchase costs; fixed-asset tax is an ongoing owner cost. Where the seller is also non-resident, Japanese withholding rules can affect settlement, so the payment route needs a tax adviser before contracts are exchanged.</p><p>Before signing, the agent's Important Matters Explanation is where the relevant rights, restrictions and hazard information should be explained; closing and registration then record the transfer. The explanation must show the property's location on the official flood-hazard map. Treat that as a starting point, not a clean bill of health: in Hakone and Izu, older stock, slope, typhoon and earthquake exposure are part of the asset; in Hakuba and Niseko, snow load, winter access and heating systems are. Rental use is equally market-specific. In Niseko and Hakuba, the operating model matters as much as the chalet: management, snow response and local compliance shape the income result. Minpaku is capped nationally at 180 days a year, and local rules can be tighter.</p></section>
          <section class="seo-section"><h2>Income and upside need different stories</h2><p>Fukuoka's case is domestic and regional demand: a practical city base, resilient travel and a lower entry benchmark than global resorts. Hakone and Izu benefit from Tokyo weekend demand, but old homes and uneven rental evidence make them a personal-use-first decision. Hakuba is the earlier-stage ski proposition—lower entry than Niseko, a growing international profile and summer hiking or biking, offset by execution-heavy winter operations.</p><p>Niseko is the premium version: global Asian and Australian ski demand, high winter rates and branded-residence appeal. The cost is a far higher entry level, substantial operating friction and a more concentrated seasonal thesis. Neither resort should be described with a single yield number; owner use, management, snow, maintenance and the local permit route decide the outcome.</p></section>
          <section class="seo-section"><h2>Preserve the exit—and the entry discipline</h2><p>Fukuoka is the broadest retirement asset of the four because domestic city demand sits beneath the foreign-buyer story. Hakone and Izu can offer striking low entry prices, but the gap between a charming bargain and an expensive renovation is wide. Hakuba has thinner liquidity than Niseko, so the price paid and the operator selected matter more.</p><p>Niseko has the clearest international resort buyer pool, but prime Hirafu pricing already reflects that recognition. The retirement conclusion is not that one location wins every pillar: choose Fukuoka for year-round use, Hakone or Izu for Tokyo-adjacent escape, Hakuba for earlier-stage mountain upside, and Niseko only when the premium winter thesis and its costs are fully acceptable.</p></section>
        """
    elif page["slug"] == "spain-retirement-property-foreign-buyers":
        editorial_content = f"""
          <section class="seo-section" id="lenses"><h2>Spain through five retirement lenses</h2><p>Spain succeeds as a retirement base when the buyer chooses a real community rather than a holiday proposition. The same national framework produces very different outcomes across an inland Valencia neighborhood, a Costa del Sol apartment, a Girona townhouse and a Mallorcan village. These five questions connect the property to the life it must support.</p></section>
          <section class="seo-section"><h2>Live well, year after year</h2><p><a class="editorial-destination-link" href="/destinations/valencia/" data-track="destination_click">Valencia</a> offers the most balanced version of urban Mediterranean retirement: a substantial city, beaches, culture and daily services without requiring a resort routine. <a class="editorial-destination-link" href="/destinations/malaga-costa-del-sol/" data-track="destination_click">Málaga and the Costa del Sol</a> make entry socially easier through established international communities, but municipality and neighborhood selection determine whether life remains pleasant outside the visitor economy. <a class="editorial-destination-link" href="/destinations/costa-brava-girona/" data-track="destination_click">Girona and the Costa Brava</a> reward buyers seeking Catalan character and landscape, while <a class="editorial-destination-link" href="/destinations/mallorca/" data-track="destination_click">Mallorca</a> offers a polished island ecosystem at a higher price and with more logistical dependence.</p><p>Healthcare, shade, walkability, groceries, public transport and year-round social life matter more after the first month than a sea view. Test each location in its hottest period and in winter. A retirement home should remain comfortable when restaurants close, visitors leave, a car cannot be used and a specialist appointment is required.</p>{spain_daily_life_figure}</section>
          <section class="seo-section"><h2>Reach Spain easily—and choose the right rhythm</h2><p>Spain has unusual depth for repeat international use. Málaga, Valencia and Palma support broad air networks, while high-speed rail strengthens the mainland city case. Access alone is not enough: model the full door-to-door journey, seasonal schedules, onward transport and whether friends or family can visit without a complex transfer.</p><p>Valencia is the easiest place in this shortlist to build an ordinary urban routine. Málaga and the Costa del Sol are strongest for internationally connected coastal living. Girona and the Costa Brava divide between a functioning second city and car-dependent coastal settlements. Mallorca's air access is extensive, but island life still concentrates maintenance, medical travel and family logistics into a different rhythm.</p>{spain_access_figure}</section>
          <section class="seo-section"><h2>Own and operate with regional discipline</h2><p>Spain's land-registry and notarial systems provide a recognizable ownership path, but a registry extract is not a substitute for full diligence. The buyer must reconcile title, cadastre, planning status, physical works, occupancy documentation, debts, community records and intended use. Coastal extensions, converted terraces, rural buildings and older planning histories deserve particular scrutiny.</p><p>Operation is regional and local. Transfer taxes differ by autonomous community; tourist-use rules can sit at regional, municipal and building levels; water, flood, wildfire and heat exposure vary by site. A buyer who cannot explain which authority controls each issue is not ready to price the asset.</p></section>
          <section class="seo-section"><h2>Income and upside need a local story</h2><p>Spain has a deep foreign-buyer market, but national demand does not make every home liquid. Registradores reported that foreign purchasers represented 13.8% of Spanish home sales in 2025, with especially high shares in the Balearic Islands and Valencia. That supports international depth; it does not validate a particular price or yield.</p><p>Valencia and Málaga have the broadest mix of local, national and international demand in this shortlist. Mallorca has a powerful international buyer pool but a high entry threshold and more policy sensitivity. Costa Brava and Girona range from globally recognized enclaves to thin, highly seasonal micro-markets. Underwrite long-term value from location quality and ordinary usability, not from a tourist licence whose status may change.</p></section>
          <section class="seo-section"><h2>Preserve the exit—and the life around it</h2><p>Exit quality begins at purchase. Favor understandable title, legal building status, manageable community costs, climate resilience and a layout that appeals beyond one nationality or rental strategy. Avoid paying a premium for informal alterations, assumed licences or a view that comes with difficult access and weak year-round services.</p><p>The retirement conclusion is conditional: choose Valencia for the strongest all-round urban base; Málaga and the Costa del Sol for established international infrastructure; Girona or the Costa Brava for a more selective Catalan life; and Mallorca when premium island living, travel dependence and carrying costs all fit comfortably. The best property is the one that remains useful even if short-term rental income disappears.</p></section>
        """
    generic_intro = f"""
          <section class="seo-section">
            <h2>How to Read This Shortlist</h2>
            <p><strong>Credibility note:</strong> this page compares {len(selected)} destinations across {country_count} countries using a consistent {len(DIMENSIONS)}-dimension model. It is research-grade destination intelligence, not financial, legal, tax, immigration, or transaction advice.</p>
            <p>The right answer for {escape(page["keyword"])} is rarely the destination with the prettiest photos or the highest advertised yield. A global buyer needs a place that can survive legal review, repeated use, currency shifts, maintenance surprises, and a future resale process.</p>
          </section>
        """
    if is_editorial_article:
        overview_html = f"{overview_html}{editorial_content}"
    hero_actions = "" if is_editorial_article else f'''<div class="seo-actions"><a class="seo-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} hero">Open the full dashboard</a><a class="seo-button secondary" href="#comparison" data-track="guide_compare_jump" data-track-label="{escape(page["h1"])}">Compare destinations</a></div>'''
    hero_aside = "" if is_editorial_article else f'''<aside class="seo-hero-card"><span>Top current match</span><strong>{escape(top["name"])}</strong><span>Alternative to test</span><strong>{escape(runner_up["name"])}</strong><span>Destinations compared</span><strong>{len(selected)}</strong></aside>'''
    guide_summary = "" if is_editorial_article else f'''<section class="seo-panel" aria-label="Guide summary"><div class="seo-stats"><div><span>Primary keyword</span><strong>{escape(page["keyword"])}</strong></div><div><span>Destinations</span><strong>{len(selected)}</strong></div><div><span>Decision model</span><strong>{len(DIMENSIONS)} dimensions</strong></div><div><span>Research status</span><strong>Updated {updated}</strong></div></div></section>'''
    decision_path = "" if is_editorial_article else guide_decision_path_html(page, destinations, pages)
    destination_notes_title = "Four places to test in person" if is_japan_article else "Destination Notes for Serious Buyers"
    decision_framework_html = seo_decision_framework_html(page)
    callout_before_overview = "" if is_editorial_article else retirement_callout
    callout_after_overview = retirement_callout if is_editorial_article else ""
    body_class = (
        "seo-page seo-page--japan"
        if is_japan_article
        else "seo-page seo-page--editorial-retirement"
        if is_spain_article
        else "seo-page"
    )
    editorial_hero_visual = (
        destination_editorial_figure_html(
            {
                "src": "/assets/fukuoka-itoshima-coast.webp",
                "alt": "The blue-green sea, beach and wooded coastline of Itoshima near Fukuoka",
            },
            "Fukuoka / Itoshima · Coast, culture and city convenience",
            "japan-hero-visual",
        )
        if is_japan_article
        else destination_editorial_figure_html(
            {
                "src": "/assets/spain-valencia-coast-hero.webp",
                "alt": "Older residents and cyclists using Valencia's green Turia Gardens corridor in warm morning light",
            },
            "Valencia · A year-round city with the Mediterranean close by",
            "editorial-hero-visual",
        )
        if is_spain_article
        else hero_aside
    )
    japan_guide_rail = f'''
        <aside class="seo-aside japan-guide-rail">
          <nav aria-label="In this guide">
            <p class="seo-eyebrow">In this guide</p>
            <a href="#residency">Residency first</a>
            <a href="#fit">Who Japan suits</a>
            <a href="#owner-changes">2026 owner changes</a>
            <a href="#costs">Financing and costs</a>
            <a href="#practicality">Retirement practicality</a>
            <a href="#lenses">Five retirement lenses</a>
            <a href="#comparison">Compare destinations</a>
            <a href="#faq">Common questions</a>
            <a href="#sources">References</a>
          </nav>
          <div class="japan-guide-rail__action">
            <p>Compare Japan with every destination in the Atlas.</p>
            <a class="seo-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} aside">Open the Atlas</a>
          </div>
          <p class="japan-guide-rail__note">Research inputs only. Verify current legal, tax and immigration rules locally.</p>
        </aside>
    '''
    spain_guide_rail = f'''
        <aside class="seo-aside editorial-guide-rail">
          <nav aria-label="In this guide">
            <p class="seo-eyebrow">In this guide</p>
            <a href="#residency">Residency first</a>
            <a href="#fit">Who Spain suits</a>
            <a href="#owner-changes">2025–2026 changes</a>
            <a href="#costs">Financing and costs</a>
            <a href="#practicality">Retirement practicality</a>
            <a href="#lenses">Five retirement lenses</a>
            <a href="#comparison">Compare destinations</a>
            <a href="#faq">Common questions</a>
            <a href="#sources">References</a>
          </nav>
          <div class="editorial-guide-rail__action">
            <p>Compare Spain with every destination in the Atlas.</p>
            <a class="seo-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} aside">Open the Atlas</a>
          </div>
          <p class="editorial-guide-rail__note">Research inputs only. Verify current legal, tax and immigration rules locally.</p>
        </aside>
    '''
    standard_guide_rail = f'''
        <aside class="seo-aside">
          <section class="seo-aside-card">
            <h2>Use the Full Atlas</h2>
            <p>Compare every destination, adjust the 10-dimension weighting model, and export a shortlist memo.</p>
            <a class="seo-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} aside">Open dashboard</a>
            <a class="seo-button" href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(page["h1"])}">Review my shortlist</a>
          </section>
          <section class="seo-aside-card">
            <h3>Related Guides</h3>
            <nav><a href="/guides/">All buying guides</a>{related_links}</nav>
          </section>
          <section class="seo-aside-card">
            <h3>Trust Layer</h3>
            <nav>{trust_page_links()}</nav>
          </section>
          <section class="seo-aside-card">
            <h3>Research Caveat</h3>
            <p>Scores and listing benchmarks are research inputs, not financial, legal, tax, or immigration advice. Verify current rules locally before acting.</p>
          </section>
        </aside>
    '''
    guide_rail = (
        japan_guide_rail
        if is_japan_article
        else spain_guide_rail
        if is_spain_article
        else standard_guide_rail
    )

    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(title, description, canonical, schema_for_page(page, canonical))}
  <style>
    :root {{
      color: #24312d;
      background: #f5f1e9;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --ink: #24312d;
      --muted: #68776f;
      --line: rgba(36, 49, 45, .13);
      --paper: #fffdf7;
      --ivory: #fffdf7;
      --stone: #ebe5da;
      --sage: #c7d3c2;
      --eucalyptus: #5f7f72;
      --sea-glass: #b9ced0;
      --brass: #a98a4b;
      --terracotta: #b76f57;
      --deep: #24312d;
      --teal: #5f7f72;
      --gold: #a98a4b;
      --clay: #b76f57;
      --editorial-serif: "Iowan Old Style", "Baskerville", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      --editorial-sans: "Avenir Next", Avenir, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-width: 320px; }}
    a {{ color: var(--teal); text-underline-offset: 3px; overflow-wrap: anywhere; }}
    p, li {{ line-height: 1.65; }}
    .seo-shell {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; }}
    .seo-hero {{
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(255, 253, 247, .97) 0 40%, rgba(255, 253, 247, .74) 62%, rgba(199, 211, 194, .30)),
        url("/assets/coastal-sage-landscape-band.jpg");
      background-size: cover;
      background-position: center;
      padding: 18px 0 64px;
    }}
    .seo-nav {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 78px; }}
    .seo-brand {{ display: flex; align-items: center; color: var(--ink); font-weight: 900; text-decoration: none; }}
    .primary-brand-logo {{ width: 174px; max-width: 48vw; height: auto; display: block; }}
    .seo-nav-links {{ display: flex; gap: 18px; flex-wrap: wrap; }}
    .seo-nav-links a {{ color: rgba(36, 49, 45, .76); text-decoration: none; font-size: 13px; font-weight: 800; }}
    .mobile-menu {{ display: none; position: relative; }}
    .mobile-menu summary {{ min-height: 42px; display: inline-flex; align-items: center; justify-content: center; padding: 0 13px; border: 1px solid rgba(36, 49, 45, .20); border-radius: 6px; color: var(--ink); font-size: 13px; font-weight: 850; list-style: none; cursor: pointer; }}
    .mobile-menu summary::-webkit-details-marker {{ display: none; }}
    .mobile-menu nav {{ position: absolute; right: 0; top: calc(100% + 8px); z-index: 20; width: min(78vw, 280px); display: grid; gap: 2px; padding: 8px; border: 1px solid rgba(36, 49, 45, .16); border-radius: 8px; background: rgba(255, 253, 247, .98); box-shadow: 0 20px 50px rgba(36, 49, 45, .16); }}
    .mobile-menu nav a {{ padding: 12px; border-radius: 6px; color: var(--ink); text-decoration: none; font-weight: 800; }}
    .seo-hero-grid {{ display: grid; grid-template-columns: minmax(0, 1fr) 310px; gap: 28px; align-items: end; }}
    .seo-eyebrow {{ margin: 0 0 12px; color: var(--brass); font-size: 12px; font-weight: 900; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ margin: 0; max-width: 900px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(40px, 7vw, 86px); line-height: .95; letter-spacing: 0; }}
    .seo-lede {{ max-width: 760px; margin: 22px 0 0; color: rgba(36, 49, 45, .72); font-size: clamp(16px, 2vw, 20px); }}
    .seo-hero-card {{ padding: 16px; border: 1px solid rgba(36, 49, 45, .13); border-radius: 8px; background: rgba(255, 253, 247, .72); box-shadow: 0 18px 44px rgba(36, 49, 45, .08); backdrop-filter: blur(16px); }}
    .seo-hero-card span {{ display: block; color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .seo-hero-card strong {{ display: block; margin: 6px 0 14px; font-size: 24px; }}
    .seo-actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 26px; }}
    .seo-button {{ display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0 15px; border-radius: 6px; background: var(--eucalyptus); color: #fffdf7; font-weight: 850; text-decoration: none; }}
    .seo-button.secondary {{ background: rgba(255, 253, 247, .58); color: var(--ink); border: 1px solid rgba(36, 49, 45, .20); }}
    main {{ margin-top: -32px; }}
    .seo-panel {{ border: 1px solid var(--line); border-radius: 8px; background: var(--paper); overflow: hidden; box-shadow: 0 18px 50px rgba(36, 49, 45, .08); }}
    .seo-stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--line); }}
    .seo-stats div {{ min-width: 0; padding: 16px; background: var(--paper); }}
    .seo-stats span, dt {{ display: block; color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }}
    .seo-stats strong, dd {{ display: block; margin: 5px 0 0; font-weight: 900; overflow-wrap: anywhere; }}
    .decision-path {{ display: grid; gap: 18px; margin-top: 18px; padding: 22px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); box-shadow: 0 18px 50px rgba(36, 49, 45, .06); }}
    .decision-path h2 {{ margin: 0 0 10px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 4vw, 40px); line-height: 1.04; }}
    .decision-path p {{ margin: 0; color: #3f4d48; }}
    .decision-path__grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .decision-path__grid article, .conversion-callout {{ min-width: 0; padding: 15px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    .decision-path__grid span {{ color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .decision-path__grid strong {{ display: block; margin: 6px 0; font-size: 18px; line-height: 1.15; }}
    .decision-path__grid a {{ display: inline-flex; margin-top: 10px; font-weight: 850; }}
    .conversion-callout {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: center; background: #eef4ec; }}
    .conversion-callout h3 {{ margin: 0 0 6px; font-size: 22px; line-height: 1.12; }}
    .quick-answer {{ display: grid; gap: 18px; margin-top: 18px; padding: 22px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); box-shadow: 0 18px 50px rgba(36, 49, 45, .06); }}
    .quick-answer h2 {{ margin: 0 0 10px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 4vw, 40px); line-height: 1.04; }}
    .quick-answer p {{ margin: 0; color: #3f4d48; }}
    .quick-answer__grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .quick-answer__grid article {{ min-width: 0; padding: 15px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    .quick-answer__grid span {{ color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .quick-answer__grid h3 {{ margin: 7px 0; font-size: 18px; line-height: 1.15; }}
    .quick-answer__grid dl {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 12px 0 0; }}
    .quick-answer__grid dl div {{ padding: 9px; border-radius: 6px; background: #f2f5f1; }}
    .seo-content {{ display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 28px; padding: 34px 0 58px; align-items: start; }}
    .seo-article {{ display: grid; gap: 28px; min-width: 0; }}
    .seo-section {{ min-width: 0; padding: 24px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }}
    .seo-section h2 {{ margin: 0 0 12px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(25px, 4vw, 38px); line-height: 1.04; }}
    .seo-section h3 {{ margin: 18px 0 8px; font-size: 18px; }}
    .seo-section p {{ color: #3f4d48; }}
    .seo-table-wrap {{ width: 100%; max-width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }}
    .seo-table {{ width: 100%; min-width: 820px; border-collapse: collapse; background: #fff; }}
    .seo-table th, .seo-table td {{ padding: 12px; border-top: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 13px; }}
    .seo-table th {{ color: var(--muted); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }}
    .seo-table span {{ color: var(--muted); }}
    .seo-card-grid {{ display: grid; gap: 12px; }}
    .seo-link-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .seo-link-card {{ min-width: 0; padding: 15px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    .seo-link-card span {{ color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .seo-link-card h3 {{ margin: 8px 0; }}
    .seo-link-card p {{ margin: 0; font-size: 14px; }}
    .seo-destination-card {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(220px, .54fr); gap: 16px; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    .seo-destination-card span {{ color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .seo-destination-card h3 {{ margin: 7px 0; }}
    .seo-destination-card dl {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 0; }}
    .seo-destination-card dl div {{ padding: 10px; border-radius: 6px; background: #f2f5f1; }}
    .seo-aside {{ position: sticky; top: 16px; display: grid; gap: 14px; }}
    .seo-aside-card {{ padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }}
    .seo-aside-card h2, .seo-aside-card h3 {{ margin: 0 0 10px; font-size: 16px; }}
    .seo-aside-card nav {{ display: grid; gap: 10px; }}
    .seo-aside-card p, .seo-aside-card a {{ font-size: 14px; }}
    .japan-hero-visual, .japan-guide-rail, .editorial-hero-visual, .editorial-guide-rail {{ display: none; }}
    .seo-page--japan {{ color: #202825; background: #f3efe5; font-family: var(--editorial-sans); }}
    .seo-page--japan .seo-shell {{ width: min(1220px, calc(100% - 48px)); }}
    .seo-page--japan .seo-hero {{ padding: 20px 0 44px; border-bottom: 1px solid rgba(32, 40, 37, .28); background: #f3efe5; }}
    .seo-page--japan .seo-nav {{ margin-bottom: 42px; padding-bottom: 16px; border-bottom: 3px solid #202825; }}
    .seo-page--japan .seo-nav-links {{ gap: 24px; }}
    .seo-page--japan .seo-nav-links a {{ color: #202825; font-size: 11px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; }}
    .seo-page--japan .seo-hero-grid {{ grid-template-columns: minmax(0, .95fr) minmax(360px, .72fr); gap: clamp(32px, 6vw, 80px); align-items: stretch; }}
    .seo-page--japan .seo-hero-grid > div {{ display: flex; flex-direction: column; justify-content: center; padding: 24px 0 18px; }}
    .seo-page--japan h1 {{ max-width: 760px; font-family: var(--editorial-serif); font-size: clamp(54px, 6.6vw, 92px); font-weight: 500; line-height: .93; letter-spacing: -.035em; }}
    .seo-page--japan .seo-lede {{ max-width: 680px; margin-top: 28px; color: #48534f; font-family: var(--editorial-serif); font-size: clamp(19px, 2vw, 24px); line-height: 1.42; }}
    .seo-page--japan .seo-eyebrow {{ color: #9a5a2d; font-size: 10px; letter-spacing: .16em; }}
    .seo-page--japan .japan-section-label {{ font-weight: 500; }}
    .seo-page--japan .japan-hero-visual {{ display: grid; grid-template-rows: 1fr auto; min-height: 530px; margin: 0; background: #202825; }}
    .seo-page--japan .japan-hero-visual img {{ display: block; width: 100%; height: 100%; min-height: 0; object-fit: cover; }}
    .seo-page--japan .japan-hero-visual figcaption {{ padding: 11px 14px; color: #f3efe5; font-size: 10px; letter-spacing: .1em; text-transform: uppercase; }}
    .seo-page--japan main {{ margin-top: 0; }}
    .seo-page--japan .seo-content {{ grid-template-columns: minmax(0, 830px) 220px; justify-content: space-between; gap: clamp(48px, 8vw, 112px); padding: 72px 0 84px; }}
    .seo-page--japan .seo-article {{ gap: 0; }}
    .seo-page--japan .seo-section {{ padding: 46px 0; border: 0; border-top: 1px solid rgba(32, 40, 37, .28); border-radius: 0; background: transparent; }}
    .seo-page--japan .seo-article > .seo-section:first-child {{ padding-top: 0; border-top: 0; }}
    .seo-page--japan .seo-section h2 {{ max-width: 720px; margin-bottom: 20px; font-family: var(--editorial-serif); font-size: clamp(34px, 4vw, 50px); font-weight: 500; line-height: 1.02; letter-spacing: -.025em; }}
    .seo-page--japan .seo-section h3 {{ margin-top: 28px; font-size: 16px; letter-spacing: .01em; }}
    .seo-page--japan .seo-section p, .seo-page--japan .seo-section li {{ color: #384540; font-size: 17px; line-height: 1.72; }}
    .seo-page--japan .seo-section p {{ max-width: 72ch; }}
    .seo-page--japan .seo-section p + p {{ margin-top: 1.25em; }}
    .seo-page--japan .editorial-destination-link {{ color: #202825; font-weight: 600; text-decoration-color: rgba(32, 40, 37, .45); text-decoration-thickness: 1px; text-underline-offset: .16em; }}
    .seo-page--japan .editorial-destination-link:hover {{ text-decoration-color: #9a5a2d; }}
    .seo-page--japan .japan-inline-visual {{ margin: 32px 0 0; }}
    .seo-page--japan .japan-inline-visual img {{ display: block; width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }}
    .seo-page--japan .japan-inline-visual figcaption {{ margin-top: 10px; color: #68726d; font-size: 12px; letter-spacing: .03em; }}
    .seo-page--japan .seo-table-wrap {{ margin-top: 28px; border: 0; border-top: 3px solid #202825; border-bottom: 1px solid #202825; border-radius: 0; }}
    .seo-page--japan .seo-table {{ background: transparent; }}
    .seo-page--japan .seo-table th, .seo-page--japan .seo-table td {{ padding: 16px 12px; border-color: rgba(32, 40, 37, .2); }}
    .seo-page--japan .seo-table th {{ color: #202825; font-size: 10px; letter-spacing: .11em; }}
    .seo-page--japan .seo-destination-card {{ padding: 22px 0; border: 0; border-top: 1px solid rgba(32, 40, 37, .22); border-radius: 0; background: transparent; }}
    .seo-page--japan .seo-destination-card dl div {{ padding: 10px 12px; border-radius: 0; background: rgba(199, 211, 194, .28); }}
    .seo-page--japan .seo-link-grid {{ gap: 0; border-top: 1px solid rgba(32, 40, 37, .22); }}
    .seo-page--japan .seo-link-card {{ padding: 20px 18px 20px 0; border: 0; border-bottom: 1px solid rgba(32, 40, 37, .22); border-radius: 0; background: transparent; }}
    .seo-page--japan .seo-button {{ border-radius: 0; background: #202825; font-size: 12px; letter-spacing: .05em; text-transform: uppercase; }}
    .seo-page--japan .japan-guide-rail {{ position: sticky; top: 24px; display: block; padding-top: 14px; border-top: 3px solid #202825; }}
    .seo-page--japan .japan-guide-rail nav {{ display: grid; }}
    .seo-page--japan .japan-guide-rail .seo-eyebrow {{ font-size: 12px; font-weight: 600; }}
    .seo-page--japan .japan-guide-rail nav a {{ padding: 11px 0; border-top: 1px solid rgba(32, 40, 37, .16); color: #202825; font-size: 14px; font-weight: 500; text-decoration: none; }}
    .seo-page--japan .japan-guide-rail__action {{ margin-top: 28px; padding: 18px 0; border-top: 1px solid rgba(32, 40, 37, .28); border-bottom: 1px solid rgba(32, 40, 37, .28); }}
    .seo-page--japan .japan-guide-rail__action p {{ margin-top: 0; font-family: var(--editorial-serif); font-size: 17px; line-height: 1.35; }}
    .seo-page--japan .japan-guide-rail .seo-button {{ font-weight: 500; }}
    .seo-page--japan .japan-guide-rail__note {{ color: #68726d; font-size: 12px; line-height: 1.55; }}
    .seo-page--japan .faq-item summary {{ font-family: var(--editorial-serif); font-size: 18px; font-weight: 600; }}
    .seo-page--japan .seo-footer {{ background: #202825; color: #e7e1d6; }}
    .seo-page--japan .seo-footer a {{ color: #c8b58a; }}
    .seo-page--editorial-retirement {{ color: #24312d; background: #f4efe4; font-family: var(--editorial-sans); }}
    .seo-page--editorial-retirement .seo-shell {{ width: min(1220px, calc(100% - 48px)); }}
    .seo-page--editorial-retirement .seo-hero {{ padding: 20px 0 44px; border-bottom: 1px solid rgba(36, 49, 45, .28); background: #f4efe4; }}
    .seo-page--editorial-retirement .seo-nav {{ margin-bottom: 42px; padding-bottom: 16px; border-bottom: 3px solid #24312d; }}
    .seo-page--editorial-retirement .seo-nav-links {{ gap: 24px; }}
    .seo-page--editorial-retirement .seo-nav-links a {{ color: #24312d; font-size: 11px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; }}
    .seo-page--editorial-retirement .seo-hero-grid {{ grid-template-columns: minmax(0, .95fr) minmax(360px, .72fr); gap: clamp(32px, 6vw, 80px); align-items: stretch; }}
    .seo-page--editorial-retirement .seo-hero-grid > div {{ display: flex; flex-direction: column; justify-content: center; padding: 24px 0 18px; }}
    .seo-page--editorial-retirement h1 {{ max-width: 760px; font-family: var(--editorial-serif); font-size: clamp(54px, 6.6vw, 92px); font-weight: 500; line-height: .93; letter-spacing: -.035em; }}
    .seo-page--editorial-retirement .seo-lede {{ max-width: 680px; margin-top: 28px; color: #4b5651; font-family: var(--editorial-serif); font-size: clamp(19px, 2vw, 24px); line-height: 1.42; }}
    .seo-page--editorial-retirement .seo-eyebrow {{ color: #a44e2f; font-size: 10px; letter-spacing: .16em; }}
    .seo-page--editorial-retirement .editorial-section-label {{ font-weight: 500; }}
    .seo-page--editorial-retirement .editorial-hero-visual {{ display: grid; grid-template-rows: 1fr auto; min-height: 530px; margin: 0; background: #24312d; }}
    .seo-page--editorial-retirement .editorial-hero-visual img {{ display: block; width: 100%; height: 100%; min-height: 0; object-fit: cover; }}
    .seo-page--editorial-retirement .editorial-hero-visual figcaption {{ padding: 11px 14px; color: #f4efe4; font-size: 10px; letter-spacing: .1em; text-transform: uppercase; }}
    .seo-page--editorial-retirement main {{ margin-top: 0; }}
    .seo-page--editorial-retirement .seo-content {{ grid-template-columns: minmax(0, 830px) 220px; justify-content: space-between; gap: clamp(48px, 8vw, 112px); padding: 72px 0 84px; }}
    .seo-page--editorial-retirement .seo-article {{ gap: 0; }}
    .seo-page--editorial-retirement .seo-section {{ padding: 46px 0; border: 0; border-top: 1px solid rgba(36, 49, 45, .28); border-radius: 0; background: transparent; }}
    .seo-page--editorial-retirement .seo-article > .seo-section:first-child {{ padding-top: 0; border-top: 0; }}
    .seo-page--editorial-retirement .seo-section h2 {{ max-width: 720px; margin-bottom: 20px; font-family: var(--editorial-serif); font-size: clamp(34px, 4vw, 50px); font-weight: 500; line-height: 1.02; letter-spacing: -.025em; }}
    .seo-page--editorial-retirement .seo-section h3 {{ margin-top: 28px; font-size: 16px; letter-spacing: .01em; }}
    .seo-page--editorial-retirement .seo-section p, .seo-page--editorial-retirement .seo-section li {{ color: #3b4943; font-size: 17px; line-height: 1.72; }}
    .seo-page--editorial-retirement .seo-section p {{ max-width: 72ch; }}
    .seo-page--editorial-retirement .seo-section p + p {{ margin-top: 1.25em; }}
    .seo-page--editorial-retirement .editorial-destination-link {{ color: #24312d; font-weight: 600; text-decoration-color: rgba(36, 49, 45, .45); text-decoration-thickness: 1px; text-underline-offset: .16em; }}
    .seo-page--editorial-retirement .editorial-destination-link:hover {{ text-decoration-color: #a44e2f; }}
    .seo-page--editorial-retirement .editorial-inline-visual {{ margin: 32px 0 0; }}
    .seo-page--editorial-retirement .editorial-inline-visual img {{ display: block; width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }}
    .seo-page--editorial-retirement .editorial-inline-visual figcaption {{ margin-top: 10px; color: #6e756f; font-size: 12px; letter-spacing: .03em; }}
    .seo-page--editorial-retirement .seo-table-wrap {{ margin-top: 28px; border: 0; border-top: 3px solid #24312d; border-bottom: 1px solid #24312d; border-radius: 0; }}
    .seo-page--editorial-retirement .seo-table {{ background: transparent; }}
    .seo-page--editorial-retirement .seo-table th, .seo-page--editorial-retirement .seo-table td {{ padding: 16px 12px; border-color: rgba(36, 49, 45, .2); }}
    .seo-page--editorial-retirement .seo-table th {{ color: #24312d; font-size: 10px; letter-spacing: .11em; }}
    .seo-page--editorial-retirement .seo-link-grid {{ gap: 0; border-top: 1px solid rgba(36, 49, 45, .22); }}
    .seo-page--editorial-retirement .seo-link-card {{ padding: 20px 18px 20px 0; border: 0; border-bottom: 1px solid rgba(36, 49, 45, .22); border-radius: 0; background: transparent; }}
    .seo-page--editorial-retirement .seo-button {{ border-radius: 0; background: #24312d; font-size: 12px; font-weight: 500; letter-spacing: .05em; text-transform: uppercase; }}
    .seo-page--editorial-retirement .editorial-guide-rail {{ position: sticky; top: 24px; display: block; padding-top: 14px; border-top: 3px solid #24312d; }}
    .seo-page--editorial-retirement .editorial-guide-rail nav {{ display: grid; }}
    .seo-page--editorial-retirement .editorial-guide-rail .seo-eyebrow {{ font-size: 12px; font-weight: 600; }}
    .seo-page--editorial-retirement .editorial-guide-rail nav a {{ padding: 11px 0; border-top: 1px solid rgba(36, 49, 45, .16); color: #24312d; font-size: 14px; font-weight: 500; text-decoration: none; }}
    .seo-page--editorial-retirement .editorial-guide-rail__action {{ margin-top: 28px; padding: 18px 0; border-top: 1px solid rgba(36, 49, 45, .28); border-bottom: 1px solid rgba(36, 49, 45, .28); }}
    .seo-page--editorial-retirement .editorial-guide-rail__action p {{ margin-top: 0; font-family: var(--editorial-serif); font-size: 17px; line-height: 1.35; }}
    .seo-page--editorial-retirement .editorial-guide-rail__note {{ color: #6e756f; font-size: 12px; line-height: 1.55; }}
    .seo-page--editorial-retirement .faq-item summary {{ font-family: var(--editorial-serif); font-size: 18px; font-weight: 600; }}
    .seo-page--editorial-retirement .seo-footer {{ background: #24312d; color: #e9e1d4; }}
    .seo-page--editorial-retirement .seo-footer a {{ color: #d2b988; }}
    .faq-item {{ border-top: 1px solid var(--line); padding: 14px 0; }}
    .faq-item summary {{ cursor: pointer; font-weight: 850; }}
    .faq-item p {{ margin-bottom: 0; }}
    .seo-footer {{ padding: 26px 0 40px; border-top: 1px solid var(--line); color: var(--muted); }}
    .seo-footer nav {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; }}
    @media (max-width: 860px) {{
      .seo-nav {{ margin-bottom: 48px; }}
      .seo-hero-grid, .seo-content {{ grid-template-columns: 1fr; }}
      .seo-aside {{ position: static; }}
      .seo-stats {{ grid-template-columns: repeat(2, 1fr); }}
      .decision-path__grid, .conversion-callout, .quick-answer__grid {{ grid-template-columns: 1fr; }}
      .seo-page--japan .seo-hero-grid {{ grid-template-columns: 1fr; }}
      .seo-page--japan .japan-hero-visual {{ min-height: 400px; }}
      .seo-page--japan .seo-content {{ grid-template-columns: 1fr; padding-top: 52px; }}
      .seo-page--japan .japan-guide-rail {{ position: static; display: grid; grid-template-columns: 1fr 1fr; gap: 28px; order: -1; }}
      .seo-page--japan .japan-guide-rail__action {{ margin-top: 0; }}
      .seo-page--editorial-retirement .seo-hero-grid {{ grid-template-columns: 1fr; }}
      .seo-page--editorial-retirement .editorial-hero-visual {{ min-height: 400px; }}
      .seo-page--editorial-retirement .seo-content {{ grid-template-columns: 1fr; padding-top: 52px; }}
      .seo-page--editorial-retirement .editorial-guide-rail {{ position: static; display: grid; grid-template-columns: 1fr 1fr; gap: 28px; order: -1; }}
      .seo-page--editorial-retirement .editorial-guide-rail__action {{ margin-top: 0; }}
    }}
    @media (max-width: 560px) {{
      .seo-shell {{ width: min(100% - 28px, 1120px); }}
      .seo-nav {{ align-items: flex-start; }}
      .seo-nav-links {{ display: none; }}
      .mobile-menu {{ display: block; }}
      .seo-hero {{ padding-bottom: 48px; }}
      .seo-stats, .seo-destination-card, .seo-destination-card dl, .seo-link-grid, .quick-answer__grid dl {{ grid-template-columns: 1fr; }}
      .seo-section {{ padding: 18px; }}
      .seo-page--japan .seo-shell {{ width: min(100% - 28px, 1220px); }}
      .seo-page--japan .seo-nav {{ margin-bottom: 24px; }}
      .seo-page--japan .seo-hero-grid > div {{ padding-top: 10px; }}
      .seo-page--japan h1 {{ font-size: clamp(46px, 14vw, 66px); }}
      .seo-page--japan .japan-hero-visual {{ min-height: 300px; }}
      .seo-page--japan .seo-section {{ padding: 36px 0; }}
      .seo-page--japan .seo-section h2 {{ font-size: clamp(32px, 10vw, 42px); }}
      .seo-page--japan .seo-section p, .seo-page--japan .seo-section li {{ font-size: 16px; }}
      .seo-page--japan .japan-guide-rail {{ grid-template-columns: 1fr; gap: 14px; }}
      .seo-page--editorial-retirement .seo-shell {{ width: min(100% - 28px, 1220px); }}
      .seo-page--editorial-retirement .seo-nav {{ margin-bottom: 24px; }}
      .seo-page--editorial-retirement .seo-hero-grid > div {{ padding-top: 10px; }}
      .seo-page--editorial-retirement h1 {{ font-size: clamp(46px, 14vw, 66px); }}
      .seo-page--editorial-retirement .editorial-hero-visual {{ min-height: 300px; }}
      .seo-page--editorial-retirement .seo-section {{ padding: 36px 0; }}
      .seo-page--editorial-retirement .seo-section h2 {{ font-size: clamp(32px, 10vw, 42px); }}
      .seo-page--editorial-retirement .seo-section p, .seo-page--editorial-retirement .seo-section li {{ font-size: 16px; }}
      .seo-page--editorial-retirement .editorial-guide-rail {{ grid-template-columns: 1fr; gap: 14px; }}
    }}
  </style>
</head>
<body class="{body_class}">
  <header class="seo-hero">
    <div class="seo-shell">
      {primary_nav_html("seo")}
      <div class="seo-hero-grid">
        <div>
          {hero_eyebrow}
          <h1>{escape(page["h1"])}</h1>
          <p class="seo-lede">{escape(intro)} This guide is written for {escape(page["intent"])}.</p>
          {hero_detail_html}
          {hero_actions}
        </div>
        {editorial_hero_visual}
      </div>
    </div>
  </header>
  <main>
    <div class="seo-shell">
      {guide_summary}
      {decision_path}
      {vacation_home_quick_answer_html(page, destinations)}
      <div class="seo-content">
        <article class="seo-article">
          {callout_before_overview}
          {overview_html}
          {callout_after_overview}
          {comparison_html}
          {destination_notes_html}
          {decision_framework_html}

          <section class="seo-section">
            <h2>Related Buying Guides</h2>
            <p>Use these adjacent guides to test the same shortlist from a different buyer intent before committing to local diligence.</p>
            <div class="seo-link-grid">{contextual_links}</div>
          </section>

          <section class="seo-section" id="faq">
            <h2>FAQ</h2>
            {build_faq_html(page.get("faqs", []))}
          </section>
          {references_html}
        </article>

        {guide_rail}
      </div>
    </div>
  </main>
  <footer class="seo-footer">
    <div class="seo-shell">
      <strong>{SITE_NAME}</strong>
      <p>Global property destination research for lifestyle-led investors and long-term planners.</p>
      <nav><a href="/guides/">All buying guides</a> {seo_guide_links(pages, page["slug"])} {trust_page_links()}</nav>
    </div>
  </footer>
{analytics_event_script()}
</body>
</html>
"""


def shared_content_css() -> str:
    return """
    :root {
      color: #24312d;
      background: #f5f1e9;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --ink: #24312d;
      --muted: #68776f;
      --line: rgba(36, 49, 45, .13);
      --paper: #fffdf7;
      --ivory: #fffdf7;
      --stone: #ebe5da;
      --sage: #c7d3c2;
      --eucalyptus: #5f7f72;
      --sea-glass: #b9ced0;
      --brass: #a98a4b;
      --terracotta: #b76f57;
      --deep: #24312d;
      --teal: #5f7f72;
      --gold: #a98a4b;
      --clay: #b76f57;
    }
    * { box-sizing: border-box; }
    html, body { overflow-x: hidden; }
    body { margin: 0; min-width: 320px; }
    a { color: var(--teal); text-underline-offset: 3px; overflow-wrap: anywhere; }
    p, li { line-height: 1.65; }
    .page-shell { width: min(1120px, calc(100% - 32px)); margin: 0 auto; }
    .access-notice { margin: 18px 0; padding: 14px 16px; border-left: 4px solid var(--terracotta); background: #f8ebe6; }
    .access-notice strong { font-size: 14px; }
    .access-notice p { margin: 4px 0 0; color: #59443d; font-size: 14px; }
    .page-hero {
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(255, 253, 247, .98) 0 42%, rgba(255, 253, 247, .74) 62%, rgba(199, 211, 194, .28)),
        var(--destination-hero-image, url("/assets/destination-dossier-coast.jpg"));
      background-size: cover;
      background-position: center;
      padding: 18px 0 58px;
    }
    .page-nav { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 70px; }
    .page-brand { display: flex; align-items: center; color: var(--ink); font-weight: 900; text-decoration: none; }
    .primary-brand-logo { width: 174px; max-width: 48vw; height: auto; display: block; }
    .page-nav-links { display: flex; gap: 18px; flex-wrap: wrap; }
    .page-nav-links a { color: rgba(36, 49, 45, .76); text-decoration: none; font-size: 13px; font-weight: 800; }
    .mobile-menu { display: none; position: relative; }
    .mobile-menu summary {
      min-height: 42px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 13px;
      border: 1px solid rgba(36, 49, 45, .20);
      border-radius: 6px;
      color: var(--ink);
      font-size: 13px;
      font-weight: 850;
      list-style: none;
      cursor: pointer;
    }
    .mobile-menu summary::-webkit-details-marker { display: none; }
    .mobile-menu nav {
      position: absolute;
      right: 0;
      top: calc(100% + 8px);
      z-index: 20;
      width: min(78vw, 280px);
      display: grid;
      gap: 2px;
      padding: 8px;
      border: 1px solid rgba(36, 49, 45, .16);
      border-radius: 8px;
      background: rgba(255, 253, 247, .98);
      box-shadow: 0 20px 50px rgba(36, 49, 45, .16);
    }
    .mobile-menu nav a { padding: 12px; border-radius: 6px; color: var(--ink); text-decoration: none; font-weight: 800; }
    .mobile-menu nav a:focus, .mobile-menu nav a:hover { background: rgba(199, 211, 194, .38); }
    .page-hero-grid { display: grid; grid-template-columns: minmax(0, 1fr) 310px; gap: 28px; align-items: end; }
    .page-hero-grid > *, .page-layout > * { min-width: 0; }
    .page-eyebrow { margin: 0 0 12px; color: var(--brass); font-size: 12px; font-weight: 900; letter-spacing: .12em; text-transform: uppercase; }
    h1 { margin: 0; max-width: 900px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(40px, 7vw, 86px); line-height: .95; letter-spacing: 0; overflow-wrap: anywhere; }
    .page-lede { max-width: 760px; margin: 22px 0 0; color: rgba(36, 49, 45, .72); font-size: clamp(16px, 2vw, 20px); }
    .page-hero-card { padding: 16px; border: 1px solid rgba(36, 49, 45, .13); border-radius: 8px; background: rgba(255, 253, 247, .72); box-shadow: 0 18px 44px rgba(36, 49, 45, .08); backdrop-filter: blur(16px); }
    .page-hero-card span { display: block; color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .page-hero-card strong { display: block; margin: 6px 0 14px; font-size: 24px; overflow-wrap: anywhere; }
    .page-button { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0 15px; border-radius: 6px; background: var(--eucalyptus); color: #fffdf7; font-weight: 850; text-decoration: none; }
    main { margin-top: -30px; }
    .page-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; overflow: hidden; border: 1px solid var(--line); border-radius: 8px; background: var(--line); box-shadow: 0 18px 50px rgba(36, 49, 45, .08); }
    .page-stats div { min-width: 0; padding: 16px; background: var(--paper); }
    .page-stats span, dt { display: block; color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .page-stats strong, dd { display: block; margin: 5px 0 0; font-weight: 900; overflow-wrap: anywhere; }
    .buyer-next-step { display: grid; gap: 18px; margin-top: 20px; padding: 22px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); box-shadow: 0 18px 50px rgba(36, 49, 45, .06); }
    .buyer-next-step h2 { margin: 0 0 10px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 4vw, 40px); line-height: 1.04; }
    .buyer-next-step p { margin: 0; color: #3f4d48; }
    .buyer-next-step__grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
    .buyer-next-step__grid article, .conversion-callout { min-width: 0; padding: 15px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .buyer-next-step__grid span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .buyer-next-step__grid strong { display: block; margin: 6px 0; font-size: 18px; line-height: 1.15; }
    .buyer-next-step__grid nav { display: grid; gap: 8px; margin-top: 8px; }
    .buyer-next-step__grid a { font-weight: 850; }
    .conversion-callout { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: center; background: #eef4ec; }
    .conversion-callout h3 { margin: 0 0 6px; font-size: 22px; line-height: 1.12; }
    .page-layout { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 28px; padding: 34px 0 58px; align-items: start; }
    .destination-layout { grid-template-columns: minmax(0, 1fr); }
    .page-article { display: grid; gap: 24px; min-width: 0; }
    .page-section { min-width: 0; padding: 24px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
    .page-section h2 { margin: 0 0 12px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(25px, 4vw, 38px); line-height: 1.04; }
    .page-section h3 { margin: 18px 0 8px; font-size: 18px; }
    .page-section p, .page-section li { color: #3f4d48; }
    .page-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .page-section nav.page-grid a { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 8px; background: #fff; font-weight: 850; text-decoration: none; }
    .page-card { min-width: 0; padding: 15px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }
    .page-card h3 { margin-top: 0; }
    .page-card ul { margin: 0; padding-left: 18px; }
    .page-card .page-button { margin-top: 12px; }
    .report-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
    .report-card {
      min-width: 0;
      display: grid;
      gap: 10px;
      padding: 16px;
      border: 1px solid rgba(36, 49, 45, .16);
      border-radius: 8px;
      background: linear-gradient(180deg, #fffdf7, #f4eee2);
    }
    .report-card span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .report-card h3 { margin: 0; font-size: 19px; line-height: 1.14; }
    .report-card p { margin: 0; color: #3f4d48; font-size: 14px; line-height: 1.5; }
    .report-card strong { color: var(--ink); font-size: 13px; line-height: 1.45; }
    .report-card a { font-weight: 900; }
    .offer-comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .offer-comparison article { min-width: 0; padding: 18px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }
    .offer-comparison span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .offer-comparison h3 { margin: 8px 0 10px; }
    .offer-comparison ul { margin: 0; padding-left: 18px; color: #3f4d48; }
    .sticky-jump {
      position: sticky;
      top: 0;
      z-index: 12;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      margin: 18px 0 0;
      padding: 10px 0;
      background: linear-gradient(180deg, #f5f1e9 72%, rgba(245, 241, 233, 0));
      scrollbar-width: none;
    }
    .sticky-jump a {
      flex: 0 0 auto;
      padding: 9px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fffdf7;
      color: var(--ink);
      font-size: 13px;
      font-weight: 850;
      text-decoration: none;
    }
    .mobile-action-strip { display: none; }
    .trust-brief {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 1px;
      overflow: hidden;
      margin-top: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--line);
    }
    .trust-brief div { min-width: 0; padding: 16px; background: #fffdf7; }
    .trust-brief span, .brief-panel span {
      color: var(--gold);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .trust-brief strong { display: block; margin: 6px 0; font-size: 16px; }
    .trust-brief p { margin: 0; color: var(--muted); font-size: 13px; }
    .brief-panel {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }
    .brief-panel article { min-width: 0; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }
    .brief-panel strong { display: block; margin-top: 6px; font-size: 18px; overflow-wrap: anywhere; word-break: break-word; }
    .brief-panel p { margin: 8px 0 0; color: var(--muted); font-size: 13px; overflow-wrap: anywhere; }
    .executive-summary {
      margin-top: 18px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 253, 247, .88);
      box-shadow: 0 18px 44px rgba(36, 49, 45, .06);
    }
    .executive-summary h2 { margin: 0 0 6px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(25px, 3.4vw, 36px); line-height: 1.04; }
    .executive-summary > p { max-width: 760px; margin: 0 0 14px; color: var(--muted); }
    .executive-summary__grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    .executive-summary article { min-width: 0; padding: 13px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .executive-summary span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .executive-summary p { margin: 8px 0 0; color: #3f4d48; font-size: 13px; line-height: 1.45; overflow-wrap: anywhere; }
    .decision-panel {
      display: grid;
      grid-template-columns: minmax(0, .9fr) minmax(0, 1.4fr);
      gap: 1px;
      overflow: hidden;
      margin-top: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--line);
      box-shadow: 0 18px 50px rgba(36, 49, 45, .08);
    }
    .decision-panel__intro, .decision-panel__facts div { min-width: 0; background: var(--paper); }
    .decision-panel__intro { padding: 20px; }
    .decision-panel span, .page-card span {
      color: var(--gold);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .decision-panel h2 { margin: 8px 0 10px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(26px, 3.4vw, 38px); line-height: 1.04; }
    .decision-panel p { margin: 0; color: #3f4d48; }
    .decision-panel__facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px; }
    .decision-panel__facts div { padding: 16px; }
    .decision-panel__facts strong { display: block; margin-top: 5px; font-size: 15px; line-height: 1.35; overflow-wrap: anywhere; }
    .market-summary {
      display: grid;
      grid-template-columns: minmax(220px, .75fr) minmax(0, 1.7fr);
      gap: 24px;
      margin-top: 18px;
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
    }
    .market-summary h2 { margin: 0 0 8px; font-family: Georgia, "Times New Roman", serif; font-size: 28px; }
    .market-summary p { margin: 0; color: #3f4d48; }
    .market-summary__facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px 24px; margin: 0; }
    .market-summary__facts div { min-width: 0; }
    .market-summary__facts dt { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .market-summary__facts dd { margin: 4px 0 0; font-weight: 700; line-height: 1.4; overflow-wrap: anywhere; }
    .destination-actions {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 20px 22px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #eef4ec;
    }
    .destination-actions h2 { margin: 0 0 4px; font-size: 21px; }
    .destination-actions p { margin: 0; color: var(--muted); }
    .destination-actions nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .continue-research h2 { margin-bottom: 16px; }
    .continue-research__grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 22px; }
    .continue-research h3 { margin: 0 0 8px; font-size: 15px; }
    .continue-research nav { display: grid; gap: 7px; font-size: 14px; }
    .destination-updated { margin: -8px 0 0; color: var(--muted); font-size: 13px; text-align: right; }
    .query-match-panel {
      display: grid;
      gap: 16px;
      margin-top: 18px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      box-shadow: 0 18px 44px rgba(36, 49, 45, .06);
    }
    .query-match-panel h2 { margin: 0 0 10px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(25px, 3.4vw, 36px); line-height: 1.04; }
    .query-match-panel p { margin: 0; color: #3f4d48; }
    .query-match-panel__grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
    .query-match-panel__grid article { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .query-match-panel__grid span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .query-match-panel nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .query-match-panel nav a { font-weight: 850; }
    .delight-grid { margin-top: 14px; }
    .location-map-section {
      display: grid;
      grid-template-columns: minmax(0, .72fr) minmax(0, 1.2fr) minmax(180px, .48fr);
      gap: 16px;
      align-items: stretch;
      margin-top: 18px;
    }
    .location-map-section__copy span {
      color: var(--gold);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .location-map-section__copy h2 { margin: 8px 0 10px; font-family: Georgia, "Times New Roman", serif; font-size: clamp(25px, 3vw, 34px); line-height: 1.04; }
    .location-map-section__copy p { margin: 0; color: #3f4d48; }
    .real-map {
      min-height: 270px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #e9eee9;
      position: relative;
    }
    .real-map iframe {
      display: block;
      width: 100%;
      height: 100%;
      min-height: 270px;
      border: 0;
      filter: saturate(.78) contrast(.96);
    }
    .real-map a {
      position: absolute;
      right: 10px;
      bottom: 10px;
      z-index: 2;
      padding: 7px 9px;
      border: 1px solid rgba(36, 49, 45, .14);
      border-radius: 999px;
      background: rgba(255, 253, 247, .92);
      color: var(--ink);
      font-size: 11px;
      font-weight: 850;
      text-decoration: none;
    }
    .real-map p {
      position: absolute;
      left: 10px;
      bottom: 10px;
      z-index: 2;
      max-width: min(70%, 360px);
      margin: 0;
      padding: 8px 10px;
      border: 1px solid rgba(36, 49, 45, .12);
      border-radius: 8px;
      background: rgba(255, 253, 247, .92);
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    .real-map--area { min-height: 320px; margin: 16px 0; }
    .real-map--area iframe { min-height: 320px; }
    .atlas-map {
      position: relative;
      min-height: 270px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background:
        linear-gradient(135deg, rgba(255, 253, 247, .96), rgba(185, 206, 208, .26)),
        repeating-linear-gradient(0deg, rgba(36, 49, 45, .045) 0 1px, transparent 1px 54px),
        repeating-linear-gradient(90deg, rgba(36, 49, 45, .045) 0 1px, transparent 1px 54px);
    }
    .atlas-map svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
    }
    .atlas-map path, .atlas-map circle {
      fill: none;
      stroke: rgba(95, 127, 114, .34);
      stroke-width: 3;
      vector-effect: non-scaling-stroke;
    }
    .atlas-map circle { stroke: rgba(169, 138, 75, .28); stroke-width: 2; }
    .locator-map .country-outline path {
      fill: rgba(95, 127, 114, .22);
      stroke: rgba(36, 49, 45, .42);
      stroke-width: 2;
    }
    .locator-map .country-outline--japan path { fill: rgba(95, 127, 114, .24); }
    .locator-map .locator-map__callout {
      stroke: rgba(183, 111, 87, .72);
      stroke-width: 2;
      stroke-dasharray: 4 5;
    }
    .locator-map .locator-map__dot {
      fill: var(--terracotta);
      stroke: #fffdf7;
      stroke-width: 3;
      filter: drop-shadow(0 3px 8px rgba(36, 49, 45, .22));
    }
    .locator-map__country-name {
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 2;
      padding: 7px 10px;
      border: 1px solid rgba(36, 49, 45, .12);
      border-radius: 999px;
      background: rgba(255, 253, 247, .84);
      color: var(--gold);
      font-size: 10px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .locator-map__label::before { display: none; }
    .atlas-map__pin {
      position: absolute;
      left: var(--x);
      top: var(--y);
      z-index: 2;
      width: min(190px, 44%);
      transform: translate(-50%, -50%);
      padding: 10px;
      border: 1px solid rgba(36, 49, 45, .14);
      border-radius: 8px;
      background: rgba(255, 253, 247, .88);
      box-shadow: 0 12px 26px rgba(36, 49, 45, .08);
    }
    .atlas-map__pin::before {
      content: "";
      position: absolute;
      left: 50%;
      top: calc(100% - 2px);
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--terracotta);
      transform: translate(-50%, 0);
      box-shadow: 0 0 0 4px rgba(183, 111, 87, .18);
    }
    .atlas-map__pin span, .map-context-list span, .atlas-map__legend span {
      color: var(--gold);
      font-size: 10px;
      font-weight: 900;
      letter-spacing: .07em;
      text-transform: uppercase;
    }
    .atlas-map__pin strong { display: block; margin-top: 4px; color: var(--ink); font-size: 12px; line-height: 1.25; }
    .map-context-list {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .map-context-list li { padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }
    .map-context-list strong { display: block; margin-top: 4px; font-size: 13px; line-height: 1.3; }
    .atlas-map--area { min-height: 300px; margin: 16px 0; }
    .atlas-map--area .atlas-map__pin { width: min(210px, 36%); }
    .atlas-map__legend {
      position: absolute;
      right: 12px;
      bottom: 12px;
      z-index: 2;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .atlas-map__legend span {
      padding: 7px 9px;
      border: 1px solid rgba(36, 49, 45, .12);
      border-radius: 999px;
      background: rgba(255, 253, 247, .84);
    }
    .comparison-table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }
    .comparison-table { width: 100%; min-width: 760px; border-collapse: collapse; background: #fff; }
    .comparison-table th, .comparison-table td { padding: 12px; border-top: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 13px; }
    .comparison-table th { color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .mobile-comparison-cards { display: none; }
    .comparison-card { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }
    .comparison-card__head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
    .comparison-card__head span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .comparison-card h3 { margin: 0; font-size: 18px; }
    .comparison-card dl { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 12px 0; }
    .comparison-card dl div { min-width: 0; padding: 9px; border-radius: 6px; background: #f2f5f1; }
    .comparison-card p { margin: 0; color: var(--muted); font-size: 13px; }
    details.page-section > summary {
      list-style: none;
      cursor: pointer;
    }
    details.page-section > summary::-webkit-details-marker { display: none; }
    details.page-section > summary h2 { margin-bottom: 0; }
    details.page-section[open] > summary h2 { margin-bottom: 12px; }
    .cluster-map {
      min-height: 240px;
      display: grid;
      align-items: end;
      margin: 16px 0;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background:
        radial-gradient(circle at 24% 34%, rgba(95, 127, 114, .30) 0 4px, transparent 5px),
        radial-gradient(circle at 62% 48%, rgba(169, 138, 75, .32) 0 4px, transparent 5px),
        radial-gradient(circle at 76% 62%, rgba(185, 206, 208, .50) 0 4px, transparent 5px),
        linear-gradient(135deg, rgba(255, 253, 247, .94), rgba(199, 211, 194, .30)),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='900' height='440' viewBox='0 0 900 440'%3E%3Cpath d='M70 110h760M70 210h760M70 310h760M180 58v324M340 58v324M500 58v324M660 58v324' stroke='%2324312d' stroke-opacity='.08'/%3E%3Cpath d='M80 266c132-78 254-86 366-24 108 60 214 54 374-34' fill='none' stroke='%235f7f72' stroke-opacity='.22' stroke-width='3'/%3E%3C/svg%3E");
      background-size: cover;
      background-position: center;
    }
    .cluster-map__grid { display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-end; }
    .cluster-map__grid div {
      min-width: min(180px, 100%);
      padding: 10px;
      border: 1px solid rgba(36, 49, 45, .12);
      border-radius: 8px;
      background: rgba(255, 253, 247, .82);
      box-shadow: 0 10px 24px rgba(36, 49, 45, .06);
    }
    .cluster-map__grid span, .cluster-map__grid em { color: var(--muted); font-size: 11px; font-style: normal; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .cluster-map__grid strong { display: block; margin: 4px 0; }
    .intake-form { display: grid; gap: 14px; margin-top: 16px; }
    .saved-shortlist-bridge {
      margin-top: 16px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #eef3f0;
    }
    .saved-shortlist-bridge span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .saved-shortlist-bridge p { margin: 6px 0 0; color: #3f4d48; font-size: 14px; line-height: 1.45; }
    .intake-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .intake-form label { display: grid; gap: 6px; color: var(--muted); font-size: 12px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .intake-form input, .intake-form select, .intake-form textarea {
      width: 100%;
      min-height: 44px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 10px 12px;
      font: inherit;
      letter-spacing: 0;
      text-transform: none;
    }
    .intake-form textarea { min-height: 120px; resize: vertical; }
    .intake-form button {
      width: max-content;
      min-height: 44px;
      border: 0;
      border-radius: 6px;
      background: var(--deep);
      color: #fffdf7;
      padding: 0 16px;
      font: inherit;
      font-weight: 850;
      cursor: pointer;
    }
    .score-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin: 0; padding: 0; list-style: none; }
    .score-list li { padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .score-list div { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
    .score-list i { display: block; height: 6px; margin: 8px 0; border-radius: 999px; background: linear-gradient(90deg, var(--teal) var(--value), #e6e1d8 var(--value)); }
    .page-aside { position: sticky; top: 16px; display: grid; gap: 14px; }
    .mobile-resources > summary { display: none; list-style: none; cursor: pointer; }
    .mobile-resources > summary::-webkit-details-marker { display: none; }
    .page-aside-card { padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
    .page-aside-card h2, .page-aside-card h3 { margin: 0 0 10px; font-size: 16px; }
    .page-aside-card nav { display: grid; gap: 10px; }
    .page-aside-card p, .page-aside-card a { font-size: 14px; }
    .evidence-list { margin-top: 12px; }
    .listing { min-width: 0; display: grid; grid-template-columns: minmax(0, 1fr) minmax(220px, .55fr); gap: 14px; padding: 15px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf7; }
    .listing__type { margin: 0 0 5px; color: var(--gold) !important; font-size: 11px !important; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .listing h5 { margin: 0 0 5px; font-size: 16px; }
    .listing p { margin: 0; color: var(--muted); font-size: 13px; }
    .listing__facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; margin: 0; }
    .listing dd { margin: 3px 0 0; font-weight: 900; }
    .source-link { grid-column: 1 / -1; font-size: 13px; font-weight: 850; }
    .evidence-more { margin-top: 12px; }
    .evidence-more > summary {
      min-height: 44px;
      display: inline-flex;
      align-items: center;
      padding: 0 14px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fffdf7;
      color: var(--ink);
      font-weight: 850;
      cursor: pointer;
      list-style: none;
    }
    .evidence-more > summary::-webkit-details-marker { display: none; }
    .evidence-more[open] > summary { margin-bottom: 12px; }
    .page-footer { padding: 26px 0 40px; border-top: 1px solid var(--line); color: var(--muted); }
    .page-footer nav { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; }
    @media (max-width: 860px) {
      .page-nav { margin-bottom: 48px; }
      .page-nav-links { display: none; }
      .mobile-menu { display: block; }
      .page-hero-grid, .page-layout { grid-template-columns: 1fr; }
      .page-aside { position: static; }
      .page-stats, .page-grid, .score-list, .trust-brief, .brief-panel, .executive-summary__grid, .report-grid, .offer-comparison, .decision-panel, .location-map-section, .query-match-panel__grid, .market-summary { grid-template-columns: repeat(2, 1fr); }
      .buyer-next-step__grid, .conversion-callout { grid-template-columns: 1fr; }
      .continue-research__grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .location-map-section .map-context-list { grid-column: 1 / -1; grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (max-width: 560px) {
      .page-shell { width: min(1120px, calc(100% - 28px)); }
      .page-nav { align-items: flex-start; }
      .page-hero-grid > div { max-width: min(100%, 362px); }
      h1 { max-width: min(100%, 362px); font-size: clamp(31px, 9.5vw, 40px); line-height: 1; word-break: break-word; }
      .page-lede { max-width: min(100%, 362px); }
      .page-lede { font-size: 16px; }
      .page-article, .page-section, .page-card, .brief-panel, .brief-panel article, .trust-brief, .trust-brief div, .comparison-card, .mobile-resources, .page-aside-card, .executive-summary, .executive-summary article, .decision-panel, .decision-panel__intro, .decision-panel__facts div, .market-summary, .market-summary__facts div, .location-map-section, .atlas-map, .real-map, .map-context-list li, .buyer-next-step, .buyer-next-step__grid article, .conversion-callout {
        width: 100%;
        max-width: 100%;
        min-width: 0;
      }
      .page-section p, .page-section li, .page-card p, .brief-panel p, .trust-brief p, .comparison-card p, .page-aside-card p {
        max-width: 100%;
        overflow-wrap: anywhere;
        word-break: normal;
      }
      .page-stats, .page-grid, .score-list, .intake-grid, .trust-brief, .brief-panel, .executive-summary__grid, .report-grid, .offer-comparison, .decision-panel, .decision-panel__facts, .market-summary, .market-summary__facts, .location-map-section, .location-map-section .map-context-list, .query-match-panel__grid { grid-template-columns: 1fr; }
      .continue-research__grid { grid-template-columns: 1fr; }
      .destination-actions { align-items: flex-start; }
      .page-section { padding: 18px; }
      body.has-mobile-actions { padding-bottom: 74px; }
      main { margin-top: -18px; }
      .page-hero { padding-bottom: 44px; }
      .page-hero-card { display: none; }
      .page-hero .brief-panel { gap: 8px; }
      .page-hero .brief-panel article { padding: 13px; }
      .mobile-resources {
        position: static;
        display: block;
        padding: 18px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--paper);
      }
      .mobile-resources > summary {
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 23px;
        font-weight: 900;
      }
      .mobile-resources > summary::after {
        content: "+";
        flex: 0 0 auto;
        width: 28px;
        height: 28px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--line);
        border-radius: 999px;
        color: var(--teal);
        font-family: Inter, ui-sans-serif, system-ui, sans-serif;
        font-size: 16px;
      }
      .mobile-resources[open] > summary { margin-bottom: 12px; }
      .mobile-resources[open] > summary::after { content: "-"; }
      .mobile-resources .page-aside-card { margin-top: 10px; }
      .listing, .listing__facts { grid-template-columns: 1fr; }
      .page-stats {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        box-shadow: none;
      }
      .sticky-jump {
        margin-top: 12px;
        padding: 8px 0;
        background: linear-gradient(180deg, #f5f1e9 80%, rgba(245, 241, 233, 0));
      }
      .sticky-jump a { padding: 8px 10px; font-size: 12px; }
      .mobile-action-strip {
        position: fixed;
        right: 12px;
        bottom: 12px;
        left: 12px;
        z-index: 40;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        padding: 8px;
        border: 1px solid rgba(36, 49, 45, .14);
        border-radius: 8px;
        background: rgba(255, 253, 247, .96);
        box-shadow: 0 18px 46px rgba(36, 49, 45, .20);
        backdrop-filter: blur(14px);
      }
      .mobile-action-strip a {
        min-width: 0;
        min-height: 42px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0 10px;
        border-radius: 6px;
        background: var(--eucalyptus);
        color: #fffdf7;
        font-size: 12px;
        font-weight: 850;
        text-align: center;
        text-decoration: none;
      }
      .mobile-action-strip a + a { background: #fffdf7; color: var(--ink); border: 1px solid var(--line); }
      details.page-section > summary {
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      details.page-section > summary::after {
        content: "+";
        flex: 0 0 auto;
        width: 28px;
        height: 28px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--line);
        border-radius: 999px;
        color: var(--teal);
        font-weight: 900;
      }
      details.page-section[open] > summary::after { content: "-"; }
      details.page-section > summary h2 { font-size: 23px; }
      .comparison-table-wrap { display: none; }
      .mobile-comparison-cards { display: grid; gap: 10px; }
      .cluster-map { min-height: 160px; padding: 12px; }
      .cluster-map__grid { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 2px; }
      .cluster-map__grid div { flex: 0 0 170px; }
      .location-map-section { gap: 12px; margin-top: 12px; }
      .real-map, .real-map iframe { min-height: 300px; }
      .real-map--area, .real-map--area iframe { min-height: 360px; }
      .real-map p {
        left: 8px;
        right: 8px;
        bottom: 8px;
        max-width: none;
        padding: 7px 8px;
        font-size: 11px;
      }
      .real-map a {
        top: 8px;
        right: 8px;
        bottom: auto;
      }
      .atlas-map { min-height: 245px; }
      .atlas-map--area { min-height: 440px; }
      .atlas-map__pin { width: min(160px, 48%); padding: 8px; }
      .atlas-map--area .atlas-map__pin { width: min(170px, 52%); }
      .atlas-map__pin strong { font-size: 11px; }
      .atlas-map__legend { right: 8px; bottom: 8px; gap: 5px; }
      .atlas-map__legend span { padding: 6px 7px; font-size: 9px; }
    }
"""


def premium_dossier_schema(dest: dict, canonical: str, spec: PremiumDossierSpec) -> list[dict]:
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": spec.h1,
            "description": spec.description,
            "datePublished": spec.date_published,
            "dateModified": spec.date_reviewed,
            "author": {"@type": "Organization", "name": spec.author},
            "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "image": f"{SITE_URL.rstrip('/')}{spec.images[0].src}",
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Destinations", "item": f"{SITE_URL}dashboard/"},
                {"@type": "ListItem", "position": 3, "name": dest["name"], "item": canonical},
            ],
        },
    ]


def premium_dossier_figure(image, *, hero: bool = False) -> str:
    class_name = "premium-hero-visual" if hero else f"premium-inline-visual {escape(image.placement_class)}"
    return (
        f'<figure class="{class_name}">'
        f'<img src="{escape(image.src)}" alt="{escape(image.alt)}" loading="{"eager" if hero else "lazy"}">'
        f'<figcaption>{escape(image.caption)}</figcaption>'
        "</figure>"
    )


def premium_dossier_score_table(dest: dict, spec: PremiumDossierSpec) -> str:
    dimensions = dest.get("decision_dimensions", [])
    if len(dimensions) != 10 or len({item["key"] for item in dimensions}) != 10:
        raise ValueError(f"{dest['id']} premium dossier requires exactly 10 score dimensions")
    rows = "".join(
        '<tr class="premium-score-row">'
        f'<th scope="row" data-label="Dimension">{escape(item["label"])}</th>'
        f'<td class="premium-number" data-label="Score">{float(item["score"]):.1f}/5</td>'
        f'<td class="premium-number" data-label="Weight">{float(item["weight"]) * 100:.0f}%</td>'
        f'<td data-label="Atlas read">{escape(spec.score_reads[item["key"]])}</td>'
        "</tr>"
        for item in dimensions
    )
    return (
        '<div class="premium-table-wrap premium-card-table-wrap"><table class="premium-score-table premium-card-table">'
        '<thead><tr><th>Dimension</th><th>Score</th><th>Weight</th><th>Atlas read</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


def premium_dossier_listing_table(rows: list[dict]) -> str:
    required = {
        "property_type",
        "listing_name",
        "local_currency",
        "local_price",
        "usd_price",
        "size_m2",
        "usd_per_m2",
        "source_name",
        "source_url",
        "captured_date",
        "confidence",
        "note",
        "fx_basis",
    }
    if not 3 <= len(rows) <= 5:
        raise ValueError("premium dossier requires three to five representative listings")
    body = []
    for row in rows:
        missing = required - row.keys()
        if missing or any(row[field] in (None, "") for field in required):
            raise ValueError(f"incomplete representative listing: {sorted(missing)}")
        body.append(
            '<tr class="premium-listing-row">'
            f'<th scope="row" data-label="Observation">{escape(row["listing_name"])}</th>'
            f'<td data-label="Type">{escape(row["property_type"])}</td>'
            f'<td class="premium-number" data-label="Asking price">{float(row["local_price"]):,.0f} {escape(row["local_currency"])}</td>'
            f'<td class="premium-number" data-label="USD comparison">{money(row["usd_price"])}</td>'
            f'<td class="premium-number" data-label="Area / basis">{float(row["size_m2"]):,.1f} m²<br><span class="premium-area-basis">{escape(row.get("area_basis", "Portal-stated area"))}</span></td>'
            f'<td class="premium-number" data-label="USD/m²">{money(row["usd_per_m2"])}/m²</td>'
            f'<td data-label="Source / captured"><a href="{escape(row["source_url"])}" rel="noopener noreferrer">{escape(row["source_name"])}</a><br><span>{escape(row["captured_date"])}</span></td>'
            f'<td data-label="Confidence">{escape(row["confidence"])}</td>'
            f'<td data-label="What it represents">{escape(row["note"])}</td>'
            "</tr>"
        )
    return (
        '<div class="premium-table-wrap premium-card-table-wrap"><table class="premium-listing-table premium-card-table">'
        '<thead><tr><th>Observation</th><th>Type</th><th>Asking price</th><th>USD comparison</th><th>Area / basis</th><th>USD/m²</th><th>Source / captured</th><th>Confidence</th><th>What it represents</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>'
    )


def premium_dossier_lenses_html(spec: PremiumDossierSpec) -> str:
    images = {item.key: item for item in spec.images}
    sections = []
    for lens in spec.lenses:
        paragraphs = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in lens.paragraphs)
        figure = premium_dossier_figure(images[lens.image_key]) if lens.image_key else ""
        sections.append(f'<div class="premium-lens"><h3>{escape(lens.heading)}</h3>{paragraphs}{figure}</div>')
    return (
        '<section class="premium-section" id="lenses">'
        f'<h2>{escape(spec.lenses_heading)}</h2>'
        f'<p>{escape(spec.lenses_intro)}</p>{"".join(sections)}</section>'
    )


def premium_dossier_micro_locations_html(spec: PremiumDossierSpec) -> str:
    rows = "".join(
        '<tr>'
        f'<th scope="row">{escape(item["name"])}</th>'
        f'<td>{escape(item["best_for"])}</td>'
        f'<td>{escape(item["daily_life"])}</td>'
        f'<td>{escape(item["diligence"])}</td>'
        "</tr>"
        for item in spec.micro_locations
    )
    groups = []
    for group in spec.orientation_groups:
        stops = "".join(
            '<li class="premium-location-stop">'
            f'<strong>{escape(name)}</strong><span>{escape(note)}</span>'
            '</li>'
            for name, note in group.stops
        )
        groups.append(
            '<div class="premium-orientation-group">'
            f'<h3>{escape(group.label)}</h3><ol>{stops}</ol></div>'
        )
    return (
        '<section class="premium-section" id="locations"><h2>Where to look</h2>'
        f'<p>{escape(spec.micro_locations_intro)}</p>'
        '<figure class="premium-location-orientation" aria-labelledby="location-orientation-caption">'
        f'<div class="premium-orientation-groups">{"".join(groups)}</div>'
        f'<figcaption id="location-orientation-caption">{escape(spec.orientation_caption)}</figcaption>'
        '</figure>'
        '<div class="premium-table-wrap"><table class="premium-location-table">'
        '<thead><tr><th>Micro-location</th><th>Best for</th><th>Daily life</th><th>Primary diligence</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div></section>'
    )


def premium_dossier_market_anchors_html(spec: PremiumDossierSpec) -> str:
    anchors = "".join(
        '<div class="premium-market-anchor">'
        f'<dt>{escape(anchor["location"])}</dt>'
        f'<dd><strong>{escape(anchor["evidence"])}</strong> {escape(anchor["buyer_read"])}</dd>'
        f'<dd class="premium-anchor-source"><a href="{escape(anchor["source_url"])}" rel="noopener noreferrer">{escape(anchor["source_label"])}</a></dd>'
        '</div>'
        for anchor in spec.market_anchors
    )
    return (
        '<div class="premium-market-anchors" id="official-market-anchors">'
        '<h3>Official market anchors</h3>'
        f'<p>{escape(spec.market_anchors_intro)}</p>'
        f'<dl>{anchors}</dl></div>'
    )


def premium_dossier_references_html(spec: PremiumDossierSpec) -> str:
    links = "".join(
        f'<li><a href="{escape(item["url"])}" rel="noopener noreferrer">{escape(item["label"])}</a></li>'
        for item in spec.references
    )
    return (
        '<section class="premium-section premium-references" id="sources">'
        '<h2>References and update policy</h2>'
        f'<p>{escape(spec.references_intro)}</p><ol>{links}</ol></section>'
    )


def premium_dossier_css() -> str:
    return """
    :root {
      color: #24312d;
      background: #f4efe4;
      --ink: #24312d;
      --muted: #69736e;
      --line: rgba(36, 49, 45, .24);
      --paper: #f4efe4;
      --accent: #a44e2f;
      --serif: "Iowan Old Style", "Baskerville", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      --sans: "Avenir Next", Avenir, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body.premium-dossier { margin: 0; min-width: 320px; overflow-x: hidden; color: var(--ink); background: var(--paper); font-family: var(--sans); }
    .premium-shell { width: min(1220px, calc(100% - 48px)); margin: 0 auto; }
    .premium-dossier a { color: #516f65; text-underline-offset: .18em; }
    .premium-dossier p, .premium-dossier li { font-size: 17px; line-height: 1.72; }
    .premium-dossier .page-nav { display: flex; align-items: center; justify-content: space-between; gap: 24px; margin: 0 0 38px; padding: 18px 0 16px; border-bottom: 3px solid var(--ink); }
    .premium-dossier .page-brand { display: flex; }
    .premium-dossier .primary-brand-logo { display: block; width: 174px; max-width: 48vw; }
    .premium-dossier .page-nav-links { display: flex; gap: 24px; }
    .premium-dossier .page-nav-links a { color: var(--ink); font-size: 11px; font-weight: 500; letter-spacing: .08em; text-decoration: none; text-transform: uppercase; }
    .premium-dossier .mobile-menu { display: none; position: relative; }
    .premium-dossier .mobile-menu summary { min-height: 44px; display: inline-flex; align-items: center; padding: 0 13px; border: 1px solid var(--line); cursor: pointer; list-style: none; }
    .premium-dossier .mobile-menu summary::-webkit-details-marker { display: none; }
    .premium-dossier .mobile-menu nav { position: absolute; right: 0; z-index: 20; width: min(78vw, 280px); display: grid; padding: 8px; border: 1px solid var(--line); background: #f9f5ed; }
    .premium-dossier .mobile-menu nav a { min-height: 44px; padding: 12px; color: var(--ink); text-decoration: none; }
    .premium-hero { padding-bottom: 42px; border-bottom: 1px solid var(--line); }
    .premium-hero-grid { display: grid; grid-template-columns: minmax(0, .95fr) minmax(360px, .72fr); gap: clamp(32px, 6vw, 80px); align-items: stretch; }
    .premium-hero-copy { min-width: 0; display: flex; flex-direction: column; justify-content: center; padding: 24px 0 18px; }
    .premium-hero h1 { max-width: 760px; margin: 0; overflow-wrap: anywhere; font-family: var(--serif); font-size: clamp(54px, 6.6vw, 88px); font-weight: 500; line-height: .93; letter-spacing: -.035em; }
    .premium-lede { max-width: 680px; margin: 28px 0 0; color: #4b5651; font-family: var(--serif); font-size: clamp(19px, 2vw, 24px) !important; line-height: 1.42 !important; }
    .premium-byline { margin: 20px 0 0; color: var(--muted); font-size: 12px !important; font-weight: 400; }
    .premium-hero-visual { display: grid; grid-template-rows: 1fr auto; min-height: 520px; margin: 0; background: var(--ink); }
    .premium-hero-visual img { display: block; width: 100%; height: 100%; min-height: 0; object-fit: cover; }
    .premium-hero-visual figcaption { padding: 11px 14px; color: #f4efe4; font-size: 10px; letter-spacing: .1em; text-transform: uppercase; }
    .premium-content { display: grid; grid-template-columns: minmax(0, 830px) 220px; justify-content: space-between; gap: clamp(48px, 8vw, 112px); padding: 72px 0 84px; align-items: start; }
    .premium-article { min-width: 0; }
    .premium-section { padding: 46px 0; border-top: 1px solid var(--line); }
    .premium-article > .premium-section:first-child { padding-top: 0; border-top: 0; }
    .premium-section h2 { max-width: 720px; margin: 0 0 20px; font-family: var(--serif); font-size: clamp(34px, 4vw, 50px); font-weight: 500; line-height: 1.02; letter-spacing: -.025em; }
    .premium-lens { padding: 42px 0 0; }
    .premium-lens + .premium-lens { margin-top: 42px; border-top: 1px solid rgba(36, 49, 45, .16); }
    .premium-lens h3 { max-width: 690px; margin: 0 0 18px; font-family: var(--serif); font-size: clamp(29px, 3.2vw, 42px); font-weight: 500; line-height: 1.05; letter-spacing: -.02em; }
    .premium-section p { max-width: 72ch; color: #3b4943; }
    .premium-section p + p { margin-top: 1.25em; }
    .premium-inline-visual { margin: 32px 0 0; }
    .premium-inline-visual img { display: block; width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
    .premium-inline-visual figcaption { margin-top: 10px; color: var(--muted); font-size: 12px; letter-spacing: .03em; }
    .premium-score-total { margin: 22px 0 0; font-family: var(--serif); font-size: 21px !important; }
    .premium-table-wrap { width: 100%; max-width: 100%; margin-top: 28px; overflow-x: auto; border-top: 3px solid var(--ink); border-bottom: 1px solid var(--ink); }
    .premium-table-wrap table { width: 100%; min-width: 760px; border-collapse: collapse; background: transparent; }
    .premium-listing-table { min-width: 1180px !important; }
    .premium-table-wrap th, .premium-table-wrap td { padding: 15px 11px; border-top: 1px solid rgba(36, 49, 45, .18); text-align: left; vertical-align: top; font-size: 13px; line-height: 1.5; }
    .premium-table-wrap thead th { border-top: 0; color: var(--ink); font-size: 10px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; }
    .premium-table-wrap tbody th { font-weight: 600; }
    .premium-number { white-space: nowrap; font-variant-numeric: tabular-nums; }
    .premium-area-basis { display: inline-block; max-width: 130px; white-space: normal; font-size: 11px; line-height: 1.35; }
    .premium-table-wrap span { color: var(--muted); }
    .premium-disclaimer { color: var(--muted) !important; font-size: 13px !important; }
    .premium-market-anchors { margin-top: 34px; padding-top: 28px; border-top: 1px solid var(--line); }
    .premium-market-anchors h3 { margin: 0 0 10px; font-family: var(--serif); font-size: 30px; font-weight: 500; }
    .premium-market-anchors dl { margin: 24px 0 0; border-top: 3px solid var(--ink); }
    .premium-market-anchor { display: grid; grid-template-columns: minmax(150px, .34fr) minmax(0, 1fr); gap: 7px 24px; padding: 18px 0; border-bottom: 1px solid rgba(36, 49, 45, .18); }
    .premium-market-anchor dt { grid-row: 1 / span 2; font-weight: 600; }
    .premium-market-anchor dd { margin: 0; color: #3b4943; font-size: 14px; line-height: 1.55; }
    .premium-market-anchor dd strong { display: block; margin-bottom: 3px; color: var(--ink); font-size: 17px; font-variant-numeric: tabular-nums; }
    .premium-anchor-source { font-size: 12px !important; }
    .premium-location-orientation { margin: 30px 0 0; padding: 24px 0; border-top: 3px solid var(--ink); border-bottom: 1px solid var(--line); }
    .premium-orientation-groups { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 34px; }
    .premium-orientation-group h3 { margin: 0 0 20px; color: var(--muted); font-family: var(--sans); font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }
    .premium-location-orientation ol { position: relative; display: grid; grid-template-columns: repeat(var(--stop-count, 4), minmax(0, 1fr)); gap: 18px; margin: 0; padding: 0; list-style: none; }
    .premium-orientation-group ol { grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)); }
    .premium-location-orientation ol::before { content: ""; position: absolute; top: 8px; right: 8%; left: 8%; height: 1px; background: var(--ink); }
    .premium-location-stop { position: relative; padding-top: 25px; }
    .premium-location-stop::before { content: ""; position: absolute; top: 3px; left: 0; width: 11px; height: 11px; border: 2px solid var(--paper); border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
    .premium-location-stop strong, .premium-location-stop span { display: block; }
    .premium-location-stop strong { font-size: 14px; }
    .premium-location-stop span { margin-top: 5px; color: var(--muted); font-size: 12px; line-height: 1.4; }
    .premium-location-orientation figcaption { margin-top: 20px; color: var(--muted); font-size: 12px; }
    .premium-checklist { margin: 24px 0 0; padding-left: 26px; }
    .premium-checklist li { padding: 8px 0 8px 6px; border-top: 1px solid rgba(36, 49, 45, .14); }
    .premium-handoff { margin-top: 30px; padding-top: 22px; border-top: 1px solid var(--line); }
    .premium-handoff a { font-weight: 600; }
    .premium-references ol { columns: 2; column-gap: 38px; margin: 28px 0 0; padding-left: 22px; }
    .premium-references li { break-inside: avoid; padding: 0 0 10px 4px; font-size: 13px; line-height: 1.5; }
    .premium-rail { position: sticky; top: 24px; padding-top: 14px; border-top: 3px solid var(--ink); }
    .premium-rail h2 { margin: 0 0 8px; color: var(--accent); font-size: 11px; font-weight: 600; letter-spacing: .11em; text-transform: uppercase; }
    .premium-rail nav { display: grid; }
    .premium-rail nav a { padding: 11px 0; border-top: 1px solid rgba(36, 49, 45, .16); color: var(--ink); font-size: 14px; font-weight: 500; text-decoration: none; }
    .premium-rail-action { margin-top: 28px; padding: 18px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    .premium-rail-action p { margin: 0 0 14px; font-family: var(--serif); font-size: 17px; line-height: 1.35; }
    .premium-button { display: inline-flex; min-height: 44px; align-items: center; padding: 0 15px; background: var(--ink); color: #f4efe4 !important; font-size: 12px; font-weight: 500; letter-spacing: .05em; text-decoration: none; text-transform: uppercase; }
    .premium-footer { padding: 28px 0 42px; border-top: 1px solid var(--line); color: var(--muted); }
    .premium-footer p { margin: 6px 0 0; font-size: 13px; }
    @media (max-width: 900px) {
      .premium-hero-grid, .premium-content { grid-template-columns: minmax(0, 1fr); }
      .premium-hero-visual { min-height: 400px; }
      .premium-content { padding-top: 52px; }
      .premium-rail { position: static; order: -1; }
      .premium-rail nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .premium-rail nav a:nth-child(2n) { padding-left: 18px; }
    }
    @media (max-width: 560px) {
      .premium-shell { width: min(100% - 28px, 1220px); }
      .premium-dossier .page-nav-links { display: none; }
      .premium-dossier .mobile-menu { display: block; }
      .premium-hero h1 { font-size: clamp(46px, 15vw, 64px); }
      .premium-hero-visual { min-height: 330px; }
      .premium-content { padding: 42px 0 64px; }
      .premium-section { padding: 38px 0; }
      .premium-section p, .premium-section li { font-size: 16px; }
      .premium-lens { padding-top: 34px; }
      .premium-lens + .premium-lens { margin-top: 34px; }
      .premium-rail nav { grid-template-columns: 1fr; }
      .premium-rail nav a:nth-child(2n) { padding-left: 0; }
      .premium-references ol { columns: 1; }
      .premium-card-table-wrap { overflow: visible; border-top: 0; border-bottom: 0; }
      .premium-card-table { display: block; min-width: 0 !important; }
      .premium-card-table thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; }
      .premium-card-table tbody { display: grid; gap: 18px; }
      .premium-card-table tbody tr { display: grid; grid-template-columns: 1fr; padding: 16px 0; border-top: 3px solid var(--ink); }
      .premium-card-table tbody th, .premium-card-table tbody td { display: grid; grid-template-columns: minmax(104px, .42fr) minmax(0, 1fr); gap: 12px; padding: 9px 0; border-top: 1px solid rgba(36, 49, 45, .16); }
      .premium-card-table tbody th::before, .premium-card-table tbody td::before { content: attr(data-label); color: var(--muted); font-size: 10px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; }
      .premium-card-table tbody th { font-size: 16px; }
      .premium-market-anchor { grid-template-columns: 1fr; }
      .premium-market-anchor dt { grid-row: auto; }
      .premium-orientation-groups { grid-template-columns: 1fr; }
      .premium-location-orientation ol { grid-template-columns: 1fr; gap: 0; }
      .premium-location-orientation ol::before { top: 10px; bottom: 18px; left: 6px; width: 1px; height: auto; }
      .premium-location-stop { padding: 0 0 22px 30px; }
      .premium-location-stop::before { top: 4px; left: 0; }
    }
    """


def build_premium_destination_page(
    dest: dict,
    listings: list[dict],
    destinations: list[dict],
    pages: list[dict],
    spec: PremiumDossierSpec,
) -> str:
    del destinations, pages
    validate_premium_dossier(spec)
    canonical = destination_url(dest)
    rows = [row for row in listings if row.get("destination_id") == dest["id"]]
    verdict = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in spec.verdict_paragraphs)
    checklist = "".join(f"<li>{escape(item)}</li>" for item in spec.checklist)
    rail_links = "".join(f'<a href="#{escape(anchor)}">{escape(label)}</a>' for anchor, label in spec.nav_items)
    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(spec.title, spec.description, canonical, premium_dossier_schema(dest, canonical, spec))}
  <style>{premium_dossier_css()}</style>
</head>
<body class="premium-dossier">
  <header class="premium-hero">
    <div class="premium-shell">
      {primary_nav_html()}
      <div class="premium-hero-grid">
        <div class="premium-hero-copy">
          <h1>{escape(spec.h1)}</h1>
          <p class="premium-lede">{escape(spec.lede)}</p>
          <p class="premium-byline">By {escape(spec.author)} · Published {escape(spec.date_published)} · Reviewed {escape(spec.date_reviewed)}</p>
        </div>
        {premium_dossier_figure(spec.images[0], hero=True)}
      </div>
    </div>
  </header>
  <main>
    <div class="premium-shell premium-content">
      <article class="premium-article">
        <section class="premium-section" id="verdict"><h2>The verdict</h2>{verdict}</section>
        {premium_dossier_lenses_html(spec)}
        <section class="premium-section" id="scores">
          <h2>The Atlas assessment</h2>
          <p>{escape(spec.assessment_intro)}</p>
          {premium_dossier_score_table(dest, spec)}
          <p class="premium-score-total"><strong>Weighted assessment: {float(dest["decision_score"]):.1f}/5.</strong> Reviewed {escape(spec.date_reviewed)}. <a href="/methodology/">Read the scoring methodology</a>.</p>
        </section>
        <section class="premium-section" id="listings">
          <h2>Representative property evidence</h2>
          <p>{escape(spec.listings_intro)}</p>
          {premium_dossier_listing_table(rows)}
          <p class="premium-disclaimer">Asking-price evidence only. Global Home Atlas has not verified availability, title, legal use, building condition, negotiability, fees or completed transaction value.</p>
          {premium_dossier_market_anchors_html(spec)}
        </section>
        {premium_dossier_micro_locations_html(spec)}
        <section class="premium-section" id="checklist">
          <h2>Buyer checklist—in decision order</h2>
          <ol class="premium-checklist">{checklist}</ol>
          <p class="premium-handoff">For the national residence, tax and ownership framework, read the <a href="{escape(spec.country_guide_url)}">{escape(spec.country_guide_label)}</a>. To size the plan, use the <a href="/{RETIREMENT_CALCULATOR_SLUG}/" data-track="retirement_calculator_open" data-track-label="destination page">retirement abroad calculator</a>. To compare the destination with other markets, <a href="/dashboard/">open the full Atlas</a>.</p>
        </section>
        {premium_dossier_references_html(spec)}
      </article>
      <aside class="premium-rail" aria-label="In this dossier">
        <h2>In this dossier</h2><nav>{rail_links}</nav>
        <div class="premium-rail-action"><p>{escape(spec.rail_comparison)}</p><a class="premium-button" href="/dashboard/">Open the Atlas</a></div>
      </aside>
    </div>
  </main>
  <footer class="premium-footer"><div class="premium-shell"><strong>{SITE_NAME}</strong><p>Independent research for global home buyers. Verify current legal, tax, immigration and property rules locally.</p></div></footer>
{analytics_event_script()}
</body>
</html>
"""


def schema_for_destination(
    dest: dict,
    canonical: str,
    *,
    title: str | None = None,
    description: str | None = None,
) -> list[dict]:
    effective_title = title or f"{dest['name']} Property Research"
    effective_description = description or f"{dest['name']} property research for global buyers, including ownership clarity, retirement fit, rental context, risks, and destination score."
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": effective_title,
            "url": canonical,
            "description": effective_description,
            "dateModified": date.today().isoformat(),
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Destinations", "item": f"{SITE_URL}#destinations"},
                {"@type": "ListItem", "position": 3, "name": dest["name"], "item": canonical},
            ],
        },
    ]


def build_destination_page(
    dest: dict,
    listings: list[dict],
    destinations: list[dict],
    pages: list[dict],
    content_overrides: list[dict] | None = None,
) -> str:
    premium_spec = get_premium_dossier(dest["id"])
    premium_rows = [row for row in listings if row.get("destination_id") == dest["id"]]
    has_destination_override = any(
        row.get("target_url") == destination_url(dest)
        for row in (content_overrides or [])
    )
    premium_ready = (
        premium_spec is not None
        and not has_destination_override
        and len(dest.get("decision_dimensions", [])) == 10
        and 3 <= len(premium_rows) <= 5
    )
    if premium_ready:
        return build_premium_destination_page(dest, listings, destinations, pages, premium_spec)

    slug = destination_slug(dest)
    canonical = destination_url(dest)
    title = f"{dest['name']} Property Research | Global Home Atlas"
    description = (
        f"{dest['name']} property research for global buyers: ownership clarity, retirement fit, "
        f"rental income context, USD/m2 benchmark, risks, and long-term lifestyle thesis."
    )
    content = apply_content_override(
        {
            "title": title,
            "description": description,
            "generated_intro": dest.get("panel_summary") or "",
        },
        canonical,
        content_overrides or [],
    )
    title = content["title"]
    description = content["description"]
    intro = content["generated_intro"]
    generated_link = generated_internal_link_html(content)
    peer_destinations = [
        item
        for item in destinations
        if item["id"] != dest["id"] and (item.get("country") == dest.get("country") or item.get("category") == dest.get("category"))
    ][:6]
    pros = "".join(f"<li>{escape(item)}</li>" for item in dest.get("pros", []))
    cons = "".join(f"<li>{escape(item)}</li>" for item in dest.get("cons", []))
    evidence_cards = build_evidence_cards(listings)
    dimension_rows = "\n".join(
        f"""
        <li>
          <div><span>{escape(item["label"])}</span><strong>{float(item.get("score", 0)):.1f}/5</strong></div>
          <i style="--value: {score_width(float(item.get("score", 0) or 0))}"></i>
          <p>{escape(item.get("evidence") or "")}</p>
        </li>
        """
        for item in dest.get("decision_dimensions", [])
    )
    peer_links = destination_links(peer_destinations, limit=6) or destination_links(destinations, slug, limit=6)
    destination_guide_links = guide_links_for_destination(dest, pages)
    market_summary = destination_market_summary_html(dest)
    query_match_section = destination_query_match_html(dest, pages)
    location_map = destination_location_map_html(dest)
    lifestyle_section = destination_lifestyle_html(dest)
    buyer_fit_section = destination_fit_html(dest, pros, cons)
    where_to_look_section = destination_where_to_look_html(dest)
    budget_section = destination_budget_html(dest, listings)
    risk_section = destination_risk_checklist_html(dest)
    compare_section = destination_compare_html(dest, peer_destinations)
    country_hub = country_hub_for_destination(dest)
    country_hub_link = (
        f'<a href="/countries/{escape(country_hub["slug"])}/">{escape(country_hub["h1"])}</a>'
        if country_hub
        else ""
    )
    retirement_ids = {item["destination_id"] for item in load_retirement_costs()["destinations"]}
    retirement_callout = retirement_calculator_callout("page-section", "destination page") if dest["id"] in retirement_ids else ""
    destination_image = destination_image_assets(dest)
    access_notice = destination_access_notice_html(dest)

    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(title, description, canonical, schema_for_destination(dest, canonical, title=title, description=description))}
  <style>{shared_content_css()}</style>
</head>
<body>
  <header class="page-hero" style="--destination-hero-image: url('{escape(destination_image['webp_900'])}')">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">{escape(dest.get("category") or "Destination")} · {escape(dest.get("country") or "")}</p>
          <h1>{escape(dest["name"])}</h1>
          <p class="page-lede">{escape(intro)}</p>
          {generated_link}
        </div>
        <aside class="page-hero-card">
          <span>Global rank</span><strong>#{dest["rank"]}</strong>
          <span>Overall rating</span><strong>{dest.get("decision_score", 0):.1f}/5</strong>
          <span>Price guide</span><strong>{money(dest.get("usd_per_m2"))}/m2</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      {access_notice}
      {market_summary}
      {query_match_section}
      {location_map}
      {sticky_page_nav([("Overview", "overview"), ("Buyer fit", "buyer-fit"), ("Areas", "where-to-look"), ("Costs and risks", "budget"), ("Evidence", "evidence"), ("Compare", "compare")])}
      <div class="page-layout destination-layout">
        <article class="page-article">
          {retirement_callout}
          <details class="page-section" id="overview" data-mobile-open="true" open>
            <summary><h2>Shortlist Verdict</h2></summary>
            <p>{escape(dest.get("profit_driver") or dest.get("panel_verdict") or "")}</p>
            <p>{escape(dest.get("panel_verdict") or "")} The useful question is whether {escape(dest["name"])} can support personal use, ownership confidence, rental realism, retirement optionality, and a future resale process without relying on a single perfect listing.</p>
          </details>
          {lifestyle_section}
          {buyer_fit_section}
          {where_to_look_section}
          {budget_section}
          <details class="page-section" id="ownership" open>
            <summary><h2>Ownership and Governance</h2></summary>
            <p>{escape(dest.get("ownership_notes") or "Confirm title structure, foreign-buyer rules, taxes, transfer process, and local counsel requirements before relying on any market-level conclusion.")}</p>
            <p>{escape(dest.get("red_flags") or "Verify current rules, building condition, liquidity, and rental permissions before committing capital.")}</p>
          </details>
          {risk_section}
          <details class="page-section" id="scores" open>
            <summary><h2>Score Breakdown</h2></summary>
            <ul class="score-list">{dimension_rows}</ul>
          </details>
          <details class="page-section" id="evidence" open>
            <summary><h2>Evidence Trail</h2></summary>
            <p>{escape(dest.get("price_basis") or "Listing samples are used as evidence anchors for current market texture, not availability guarantees.")}</p>
            {evidence_cards}
          </details>
          {compare_section}
          <section class="destination-actions" aria-label="Destination actions">
            <div>
              <h2>Ready to compare?</h2>
              <p>Place {escape(dest["name"])} beside your other plausible destinations.</p>
            </div>
            <nav>
              <a class="page-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(dest["name"])} destination">Compare destinations</a>
              <a href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(dest["name"])} destination">Review my shortlist</a>
            </nav>
          </section>
          <section class="page-section continue-research" id="continue-research">
            <h2>Continue your research</h2>
            <div class="continue-research__grid">
              <div><h3>Related destinations</h3><nav>{peer_links}</nav></div>
              <div><h3>Country guides</h3><nav>{country_hub_link or country_hub_links(limit=4)}</nav></div>
              <div><h3>Buying guides</h3><nav><a href="/guides/">All buying guides</a>{destination_guide_links}</nav></div>
              <div><h3>How we research</h3><nav>{trust_page_links()}</nav></div>
            </div>
          </section>
          <p class="destination-updated">Last updated {date.today().isoformat()}</p>
        </article>
      </div>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Scores and listing benchmarks are research inputs, not financial, legal, tax, or immigration advice.</p>
    </div>
  </footer>
{mobile_disclosure_script()}
{analytics_event_script()}
</body>
</html>
"""


def schema_for_trust_page(page: dict, canonical: str) -> list[dict]:
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": page["h1"],
            "url": canonical,
            "description": page["description"],
            "dateModified": date.today().isoformat(),
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": page["h1"], "item": canonical},
            ],
        },
    ]


def trust_page_body(page: dict) -> str:
    slug = page["slug"]
    if slug == "methodology":
        dimensions = "\n".join(
            f"<li><strong>{escape(item['label'])}</strong>: {escape(item['evidence'])} Base weight {item['weight'] * 100:.0f}%.</li>"
            for item in DIMENSIONS
        )
        return f"""
          <section class="page-section">
            <h2>What the Score Measures</h2>
            <p>Global Home Atlas uses a 10-dimension decision model to compare property destinations for buyers who care about lifestyle, legal clarity, rental realism, retirement optionality, and long-term exit quality. The model is deliberately practical: it rewards places that can be lived in, rented responsibly, owned with confidence, and sold into a real buyer pool.</p>
            <ul>{dimensions}</ul>
          </section>
          <section class="page-section">
            <h2>How to Use the Score</h2>
            <p>The score is a shortlist tool, not a purchase instruction. It helps compare destinations on a consistent basis, then forces the buyer to investigate the local legal, tax, financing, building, and neighborhood questions that decide the actual transaction.</p>
            <p>Weights are visible because different buyers should be able to challenge the model. A retirement buyer may raise healthcare and convenience. A pure investor may raise yield and exit liquidity. A lifestyle buyer may raise access and year-round activity.</p>
          </section>
        """
    if slug == "research-standards":
        return """
          <section class="page-section">
            <h2>Data Basis</h2>
            <p>Global Home Atlas combines destination scorecards, representative listing samples, pricing benchmarks, rental context, ownership notes, and committee-style qualitative reads. Listings are evidence anchors for market texture and price range. They are not availability guarantees and should not be treated as offers.</p>
            <p>Every page carries a verification expectation: buyers must confirm title, taxes, permits, foreign ownership rules, local rental rules, building condition, financing, insurance, and resale liquidity through qualified local professionals before making an investment decision.</p>
          </section>
          <section class="page-section">
            <h2>Editorial Standard</h2>
            <p>The site prioritizes decision usefulness over destination promotion. Destinations can score well while still carrying material risks. Risks are surfaced directly because affluent global buyers need to understand what can break before they spend time on lawyers, agents, flights, or offers.</p>
            <p>Global Home Atlas is research content. It is not financial, legal, tax, immigration, or investment advice.</p>
          </section>
        """
    if slug == "about":
        return """
          <section class="page-section">
            <h2>Why Global Home Atlas Exists</h2>
            <p>Global property search is usually split between beautiful listing portals and fragmented local advice. That is not enough for globally mobile buyers who are choosing a future lifestyle base, retirement option, or cross-border investment. Global Home Atlas organizes the decision around comparable scores, market caveats, listing evidence, and long-term livability.</p>
            <p>The target user is an affluent global citizen who wants to know where a property can support life plans over many years: family use, seasonal living, income support, healthcare access, resilience, and eventual exit.</p>
          </section>
          <section class="page-section">
            <h2>What Makes the Atlas Different</h2>
            <p>The product compares destinations before it compares individual homes. That sequence matters. The wrong jurisdiction, ownership structure, or liquidity profile can make a beautiful property a poor decision. The Atlas helps buyers narrow the world to destinations worthy of deeper local due diligence.</p>
          </section>
        """
    return """
      <section class="page-section" id="custom-shortlist">
        <h2>Request a Shortlist Review</h2>
        <p>Use this intake when you want the Atlas translated into a buyer-specific research brief. The first step is a structured review of your goals, budget, citizenship constraints, risk tolerance, and saved destinations.</p>
        <div class="page-grid">
          <article class="page-card">
            <span>Free intake</span>
            <h3>Fit and scope check</h3>
            <p>Share the decision you are trying to make. The response can clarify whether a custom shortlist, paid research brief, or local adviser route is the right next step.</p>
          </article>
          <article class="page-card">
            <span>Paid research path</span>
            <h3>Decision-ready shortlist</h3>
            <p>A focused destination shortlist matched to your budget, lifestyle plan, citizenship constraints, rental expectations, risk tolerance, and holding period.</p>
          </article>
          <article class="page-card">
            <span>What it is not</span>
            <h3>No legal or tax advice</h3>
            <p>The brief helps you choose where to spend diligence time. Local lawyers, tax advisers, immigration advisers, and property inspectors still need to verify transaction details.</p>
          </article>
          <article class="page-card">
            <span>Best use</span>
            <h3>Before agents and listings</h3>
            <p>The review is most useful before a buyer starts touring homes, because jurisdiction, liquidity, permits, and ownership structure should narrow the search first.</p>
          </article>
          <article class="page-card">
            <span>Later-stage support</span>
            <h3>Specialist direction</h3>
            <p>Once the shortlist narrows, the next step may be local legal, tax, immigration, financing, buyer-agent, or property-management review. Any commercial introduction should be disclosed before referral.</p>
          </article>
        </div>
        <div class="saved-shortlist-bridge" id="savedShortlistBridge" hidden>
          <span>Saved from dashboard</span>
          <p id="savedShortlistBridgeText">No saved destinations detected in this browser.</p>
        </div>
        <form class="intake-form" id="custom-shortlist-form">
          <input type="hidden" name="saved_shortlist" id="savedShortlistInput">
          <div class="intake-grid">
            <label>Name<input name="name" autocomplete="name" required></label>
            <label>Email<input name="email" type="email" autocomplete="email" required></label>
            <label>Budget range<input name="budget" placeholder="Example: US$750k-1.5m"></label>
            <label>Target regions<input name="regions" placeholder="Example: Portugal, Japan, Thailand"></label>
            <label>Primary goal
              <select name="goal">
                <option>Retirement optionality</option>
                <option>Vacation home</option>
                <option>Rental income</option>
                <option>Capital preservation</option>
                <option>Mixed lifestyle and investment</option>
              </select>
            </label>
            <label>Citizenship / residency<input name="citizenship" placeholder="Example: US citizen, Singapore PR"></label>
            <label>Rental expectations
              <select name="rental_expectations">
                <option>Personal use first, rental optional</option>
                <option>Rental offset expected</option>
                <option>Income-led investment</option>
                <option>No rental plans</option>
              </select>
            </label>
            <label>Risk tolerance
              <select name="risk_tolerance">
                <option>Low: clean ownership and liquidity matter most</option>
                <option>Medium: balanced lifestyle and return tradeoffs</option>
                <option>Higher: willing to underwrite complexity for upside</option>
              </select>
            </label>
            <label>Holding period<input name="holding_period" placeholder="Example: 7-10 years"></label>
            <label>Timing<input name="timing" placeholder="Example: researching now, buy in 12-24 months"></label>
            <label>Adviser needs<input name="adviser_needs" placeholder="Example: local lawyer, tax, residency, buyer agent"></label>
          </div>
          <label>Notes<textarea name="notes" placeholder="Citizenship, family use, healthcare needs, rental expectations, timing, and any must-avoid risks."></textarea></label>
          <button type="submit" data-track="custom_shortlist_submit_click">Prepare request</button>
        </form>
      </section>
      <section class="page-section">
        <h2>Before You Send a Deal</h2>
        <p>Do not send confidential transaction documents until an explicit review process exists. The current site is designed for destination-level research, not legal review of individual property contracts.</p>
        <p>Useful requests are framed around decisions: where to focus, which countries to avoid, what risks to underwrite first, and what kind of local adviser should be involved before property-specific diligence begins.</p>
      </section>
    """


def build_trust_page(page: dict, destinations: list[dict], pages: list[dict]) -> str:
    canonical = page_url(page["slug"])
    saved_shortlist_script = ""
    if page["slug"] == "contact":
        destination_lookup = {
            dest["id"]: {"name": dest["name"], "country": dest.get("country") or ""}
            for dest in destinations
        }
        saved_shortlist_script = f"""
  <script>
    (() => {{
      const destinationsById = {json.dumps(destination_lookup, ensure_ascii=False)};
      const bridge = document.getElementById("savedShortlistBridge");
      const bridgeText = document.getElementById("savedShortlistBridgeText");
      const input = document.getElementById("savedShortlistInput");
      if (!bridge || !bridgeText || !input) return;
      let saved = [];
      try {{
        const raw = JSON.parse(localStorage.getItem("gha_memo_shortlist") || "[]");
        saved = Array.isArray(raw) ? raw.map((id) => destinationsById[id]).filter(Boolean) : [];
      }} catch (error) {{
        saved = [];
      }}
      if (!saved.length) return;
      const names = saved.map((item) => item.name + (item.country ? " (" + item.country + ")" : ""));
      input.value = names.join(", ");
      bridge.hidden = false;
      bridgeText.textContent = names.length + (names.length === 1 ? " destination will be included: " : " destinations will be included: ") + names.join(", ");
      if (window.GHA) window.GHA.track("saved_shortlist_intake_prefill", {{ selected_count: names.length }});
    }})();
  </script>
        """
    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(page["title"], page["description"], canonical, schema_for_trust_page(page, canonical))}
  <style>{shared_content_css()}</style>
</head>
<body>
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">{escape(page["theme"])} · updated {date.today().isoformat()}</p>
          <h1>{escape(page["h1"])}</h1>
          <p class="page-lede">{escape(page["description"])}</p>
        </div>
        <aside class="page-hero-card">
          <span>Destinations</span><strong>{len(destinations)}</strong>
          <span>Decision dimensions</span><strong>{len(DIMENSIONS)}</strong>
          <span>Guide pages</span><strong>{len(pages)}</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <section class="page-stats" aria-label="Trust metrics">
        <div><span>Model</span><strong>10 dimensions</strong></div>
        <div><span>Destinations</span><strong>{len(destinations)}</strong></div>
        <div><span>Listings</span><strong>75 samples</strong></div>
        <div><span>Updated</span><strong>{date.today().isoformat()}</strong></div>
      </section>
      {sticky_page_nav([("Method", "trust-context"), ("Guides", "guides-link"), ("Destinations", "destinations-link"), ("Contact", "custom-shortlist")])}
      {trust_brief_html()}
      <div class="page-layout">
        <article class="page-article">{trust_page_body(page)}</article>
        <aside class="page-aside">
          <section class="page-aside-card">
            <h2>Explore the Atlas</h2>
            <p>Open the dashboard to compare all destinations and adjust the scoring weights.</p>
            <a class="page-button" href="/dashboard/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} trust page">Open dashboard</a>
            <a class="page-button" href="/shortlist-review/" data-track="shortlist_review_click" data-track-label="{escape(page["h1"])} trust page">Review my shortlist</a>
          </section>
          <section class="page-aside-card" id="guides-link">
            <h3>Research Guides</h3>
            <nav><a href="/guides/">All buying guides</a>{seo_guide_links(pages, limit=6)}</nav>
          </section>
          <section class="page-aside-card" id="destinations-link">
            <h3>Destination Examples</h3>
            <nav>{destination_links(destinations, limit=6)}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Trust Pages</h3>
            <nav>{trust_page_links(page["slug"])}</nav>
          </section>
        </aside>
      </div>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Global property destination research for lifestyle-led investors and long-term planners.</p>
      <nav><a href="/guides/">All buying guides</a> {seo_guide_links(pages, limit=6)} {destination_links(destinations, limit=6)}</nav>
    </div>
  </footer>
{saved_shortlist_script}
{analytics_event_script()}
</body>
</html>
"""


def build_brand_mockups_page() -> str:
    canonical = page_url("brand-mockups")
    title = "Global Home Atlas Brand Mockups"
    description = "Three visual directions for the Global Home Atlas premium atlas, briefing, and destination dossier experience."
    schema = [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "url": canonical,
            "description": description,
            "dateModified": date.today().isoformat(),
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        },
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(title, description, canonical, schema)}
  <style>
{shared_content_css()}
    main {{ margin-top: 0; }}
    .mockup-stage {{
      padding: 34px 0 64px;
      background: #f5f1e9;
    }}
    .mockup-frame {{
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fffdf7;
      box-shadow: 0 22px 70px rgba(36, 49, 45, .12);
    }}
    .mockup-frame img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .logo-options {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }}
    .logo-card {{
      min-width: 0;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fffdf7;
      box-shadow: 0 18px 50px rgba(36, 49, 45, .08);
    }}
    .logo-card__stage {{
      min-height: 168px;
      display: grid;
      place-items: center;
      padding: 20px;
      border: 1px solid rgba(36, 49, 45, .10);
      border-radius: 8px;
      background:
        linear-gradient(135deg, rgba(255, 253, 247, .94), rgba(238, 244, 239, .72)),
        radial-gradient(circle at 30% 24%, rgba(185, 206, 208, .28), transparent 42%);
    }}
    .logo-card svg {{
      width: min(100%, 360px);
      height: auto;
      overflow: visible;
    }}
    .logo-card span {{
      display: block;
      margin-top: 14px;
      color: var(--gold);
      font-size: 11px;
      font-weight: 850;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    .logo-card h2 {{
      margin: 7px 0 6px;
      font-size: 18px;
    }}
    .logo-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .mockup-notes {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .mockup-notes article {{
      min-width: 0;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fffdf7;
    }}
    .mockup-notes span {{
      color: var(--gold);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    .mockup-notes h2 {{
      margin: 8px 0;
      font-size: 18px;
    }}
    .mockup-notes p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    @media (max-width: 760px) {{
      .logo-options {{ grid-template-columns: 1fr; }}
      .mockup-notes {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">Brand exploration · visual directions</p>
          <h1>Global Home Atlas Brand Mockups</h1>
          <p class="page-lede">{description}</p>
        </div>
        <aside class="page-hero-card">
          <span>Directions</span><strong>5</strong>
          <span>Primary lane</span><strong>Atlas intelligence</strong>
          <span>Color study</span><strong>Nordic + Coastal</strong>
        </aside>
      </div>
    </div>
  </header>
  <main class="mockup-stage">
    <div class="page-shell">
      <section class="logo-options" aria-label="Global Home Atlas logo directions">
        <article class="logo-card">
          <div class="logo-card__stage">
            <svg viewBox="0 0 360 116" role="img" aria-labelledby="logoCompassTitle">
              <title id="logoCompassTitle">Compass monogram logo concept</title>
              <circle cx="54" cy="58" r="38" fill="none" stroke="#a98a4b" stroke-width="2"/>
              <circle cx="54" cy="58" r="24" fill="none" stroke="#5f7f72" stroke-width="1.6" opacity=".75"/>
              <path d="M54 20v76M16 58h76" stroke="#a98a4b" stroke-width="1.4"/>
              <path d="M54 30 61 58 54 86 47 58Z" fill="#24312d"/>
              <path d="M26 58 54 51 82 58 54 65Z" fill="#c7d3c2"/>
              <circle cx="54" cy="58" r="4" fill="#a98a4b"/>
              <text x="112" y="43" fill="#24312d" font-family="Inter, Arial, sans-serif" font-size="17" font-weight="760" letter-spacing="2.2">GLOBAL</text>
              <text x="112" y="65" fill="#24312d" font-family="Inter, Arial, sans-serif" font-size="17" font-weight="760" letter-spacing="2.2">HOME ATLAS</text>
              <text x="112" y="86" fill="#a98a4b" font-family="Inter, Arial, sans-serif" font-size="8.5" font-weight="750" letter-spacing="1.35">INDEPENDENT RESEARCH FOR GLOBAL PROPERTY DECISIONS</text>
            </svg>
          </div>
          <span>Style 01</span>
          <h2>Compass Monogram</h2>
          <p>Most classic and premium. Reads as navigation, judgment, and global orientation.</p>
        </article>
        <article class="logo-card">
          <div class="logo-card__stage">
            <svg viewBox="0 0 360 116" role="img" aria-labelledby="logoMeridianTitle">
              <title id="logoMeridianTitle">Meridian home logo concept</title>
              <circle cx="55" cy="58" r="39" fill="#fffdf7" stroke="#24312d" stroke-width="1.8"/>
              <path d="M25 58h60M55 20c-13 10-21 24-21 38s8 28 21 38M55 20c13 10 21 24 21 38s-8 28-21 38" fill="none" stroke="#5f7f72" stroke-width="1.6" opacity=".72"/>
              <path d="M34 62 55 43l21 19v17H62V67H48v12H34Z" fill="#24312d"/>
              <circle cx="55" cy="58" r="3" fill="#a98a4b"/>
              <text x="114" y="48" fill="#24312d" font-family="Georgia, 'Times New Roman', serif" font-size="26" font-weight="700">Global Home Atlas</text>
              <path d="M115 61h136" stroke="#a98a4b" stroke-width="1.4"/>
              <text x="115" y="82" fill="#68776f" font-family="Inter, Arial, sans-serif" font-size="10" font-weight="650" letter-spacing="2">GLOBAL PROPERTY INTELLIGENCE</text>
            </svg>
          </div>
          <span>Style 02</span>
          <h2>Meridian Home</h2>
          <p>Most literal. Balances home search with world-map intelligence and clear title.</p>
        </article>
        <article class="logo-card">
          <div class="logo-card__stage">
            <svg viewBox="0 0 360 116" role="img" aria-labelledby="logoSealTitle">
              <title id="logoSealTitle">Atlas seal logo concept</title>
              <circle cx="58" cy="58" r="43" fill="#24312d"/>
              <circle cx="58" cy="58" r="34" fill="none" stroke="#a98a4b" stroke-width="2"/>
              <path d="M35 70c9-23 37-23 46 0" fill="none" stroke="#fffdf7" stroke-width="3" stroke-linecap="round"/>
              <path d="M39 54c11-11 27-11 38 0" fill="none" stroke="#c7d3c2" stroke-width="3" stroke-linecap="round"/>
              <path d="M58 35v47M41 58h34" stroke="#fffdf7" stroke-width="2" opacity=".78"/>
              <text x="121" y="46" fill="#24312d" font-family="Inter, Arial, sans-serif" font-size="14" font-weight="750" letter-spacing="4">GLOBAL HOME</text>
              <text x="121" y="80" fill="#24312d" font-family="Georgia, 'Times New Roman', serif" font-size="38" font-weight="700">Atlas</text>
            </svg>
          </div>
          <span>Style 03</span>
          <h2>Atlas Seal</h2>
          <p>Most institutional. Works well for reports, methodology, and premium memos.</p>
        </article>
        <article class="logo-card">
          <div class="logo-card__stage">
            <svg viewBox="0 0 360 116" role="img" aria-labelledby="logoLedgerTitle">
              <title id="logoLedgerTitle">Dossier ledger logo concept</title>
              <rect x="18" y="22" width="80" height="72" rx="8" fill="#fffdf7" stroke="#24312d" stroke-width="2"/>
              <path d="M35 43h46M35 58h30M35 73h39" stroke="#5f7f72" stroke-width="3" stroke-linecap="round"/>
              <path d="M74 36 86 28 82 43Z" fill="#a98a4b"/>
              <circle cx="74" cy="36" r="4" fill="#24312d"/>
              <path d="M121 34h120M121 82h120" stroke="#c7d3c2" stroke-width="2"/>
              <text x="121" y="66" fill="#24312d" font-family="Georgia, 'Times New Roman', serif" font-size="31" font-weight="700">Global Home Atlas</text>
              <text x="247" y="66" fill="#5f7f72" font-family="Inter, Arial, sans-serif" font-size="13" font-weight="650" letter-spacing="2"></text>
            </svg>
          </div>
          <span>Style 04</span>
          <h2>Dossier Ledger</h2>
          <p>Most research-led. Emphasizes scorecards, diligence, and decision memos.</p>
        </article>
        <article class="logo-card">
          <div class="logo-card__stage" style="background:#071f1d;">
            <svg viewBox="0 0 360 116" role="img" aria-labelledby="logoDarkAtlasTitle">
              <title id="logoDarkAtlasTitle">Dark cartographic atlas logo concept</title>
              <g transform="translate(22 19)" fill="none" stroke="#a98a4b" stroke-width="1.7">
                <circle cx="39" cy="39" r="31"/>
                <circle cx="39" cy="39" r="19" opacity=".8"/>
                <path d="M39 2v74M2 39h74M18 18l42 42M60 18 18 60"/>
                <path d="M39 14 47 39 39 64 31 39Z" fill="#071f1d"/>
              </g>
              <circle cx="61" cy="58" r="4" fill="#a98a4b"/>
              <text x="116" y="40" fill="#fffdf7" font-family="Inter, Arial, sans-serif" font-size="16" font-weight="760" letter-spacing="2.4">GLOBAL</text>
              <text x="116" y="62" fill="#fffdf7" font-family="Inter, Arial, sans-serif" font-size="16" font-weight="760" letter-spacing="2.4">HOME ATLAS</text>
              <text x="116" y="84" fill="#a98a4b" font-family="Inter, Arial, sans-serif" font-size="8.5" font-weight="750" letter-spacing="1.35">INDEPENDENT RESEARCH FOR GLOBAL PROPERTY DECISIONS</text>
            </svg>
          </div>
          <span>Style 05</span>
          <h2>Dark Cartographic</h2>
          <p>Closest to the mockup: compact compass device, brass detail, and private-bank restraint.</p>
        </article>
        <article class="logo-card">
          <div class="logo-card__stage">
            <svg viewBox="0 0 360 116" role="img" aria-labelledby="logoLightCartographicTitle">
              <title id="logoLightCartographicTitle">Light cartographic atlas logo concept</title>
              <g transform="translate(22 19)" fill="none" stroke="#a98a4b" stroke-width="1.7">
                <circle cx="39" cy="39" r="31"/>
                <circle cx="39" cy="39" r="19" opacity=".85"/>
                <path d="M39 2v74M2 39h74M18 18l42 42M60 18 18 60"/>
                <path d="M39 14 47 39 39 64 31 39Z" fill="#fffdf7"/>
              </g>
              <circle cx="61" cy="58" r="4" fill="#a98a4b"/>
              <text x="116" y="40" fill="#24312d" font-family="Inter, Arial, sans-serif" font-size="16" font-weight="760" letter-spacing="2.4">GLOBAL</text>
              <text x="116" y="62" fill="#24312d" font-family="Inter, Arial, sans-serif" font-size="16" font-weight="760" letter-spacing="2.4">HOME ATLAS</text>
              <text x="116" y="84" fill="#806738" font-family="Inter, Arial, sans-serif" font-size="8.5" font-weight="750" letter-spacing="1.35">INDEPENDENT RESEARCH FOR GLOBAL PROPERTY DECISIONS</text>
            </svg>
          </div>
          <span>Style 06</span>
          <h2>Light Cartographic</h2>
          <p>Same mark and hierarchy as the dark version, adapted for the current pale header.</p>
        </article>
      </section>
      <section class="mockup-frame" aria-label="Global Home Atlas design mockup board">
        <img src="/brand-mockups/global-home-atlas-mockups.png" alt="Three Global Home Atlas homepage design mockups: Atlas Intelligence, Private Briefing, and Destination Dossier">
      </section>
      <section class="mockup-frame" aria-label="Global Home Atlas second design mockup board" style="margin-top: 22px;">
        <img src="/brand-mockups/global-home-atlas-mockups-2.png" alt="Two Global Home Atlas homepage design mockups: Jurisdiction Ledger and Lifestyle Index">
      </section>
      <section class="mockup-frame" aria-label="Global Home Atlas color tone exploration board" style="margin-top: 22px;">
        <img src="/brand-mockups/global-home-atlas-color-tones.png" alt="Global Home Atlas color tone exploration comparing Nordic Mineral and Mediterranean Ledger across Atlas Intelligence, Private Briefing, and Destination Dossier">
      </section>
      <section class="mockup-frame" aria-label="Global Home Atlas relaxed Coastal Sage color exploration board" style="margin-top: 22px;">
        <img src="/brand-mockups/global-home-atlas-coastal-sage.png" alt="Global Home Atlas relaxed Coastal Sage color exploration across Atlas Intelligence, Private Briefing, and Destination Dossier">
      </section>
      <section class="mockup-notes" aria-label="Mockup direction notes">
        <article>
          <span>Direction 1</span>
          <h2>Atlas Intelligence</h2>
          <p>Best for homepage brand impact: dark cartography, coordinates, trust metrics, and premium decision framing.</p>
        </article>
        <article>
          <span>Direction 2</span>
          <h2>Private Briefing</h2>
          <p>Best for methodology, guide hubs, and comparison surfaces where density and credibility matter most.</p>
        </article>
        <article>
          <span>Direction 3</span>
          <h2>Destination Dossier</h2>
          <p>Best for destination and country pages: verdicts, watch-outs, ownership clarity, score bars, and buyer-fit modules.</p>
        </article>
        <article>
          <span>Direction 4</span>
          <h2>Jurisdiction Ledger</h2>
          <p>Best for making ownership clarity, legal structure, tax friction, and exit risk feel like the brand's core intelligence edge.</p>
        </article>
        <article>
          <span>Direction 5</span>
          <h2>Lifestyle Index</h2>
          <p>Best for adding emotional warmth while keeping the product grounded in long-stay fit, healthcare, access, and daily-life signals.</p>
        </article>
        <article>
          <span>Color tone A</span>
          <h2>Nordic Mineral</h2>
          <p>Cooler, quieter, and more institutional: graphite, stone, mist grey, muted pine, glacier blue-grey, and restrained brass.</p>
        </article>
        <article>
          <span>Color tone B</span>
          <h2>Mediterranean Ledger</h2>
          <p>Warmer and more editorial: ivory, ink charcoal, olive, muted terracotta, aged gold, and parchment neutrals.</p>
        </article>
        <article>
          <span>Color tone C</span>
          <h2>Coastal Sage</h2>
          <p>Most relaxed and approachable: warm ivory, soft sage, eucalyptus, sea-glass blue, weathered stone, muted terracotta, aged brass, and charcoal ink.</p>
        </article>
      </section>
    </div>
  </main>
  <footer class="page-footer">
    <div class="page-shell">
      <strong>{SITE_NAME}</strong>
      <p>Brand and visual direction board for the premium atlas experience.</p>
      <nav><a href="/">Dashboard</a><a href="/guides/">Guides</a><a href="/methodology/">Methodology</a></nav>
    </div>
  </footer>
{analytics_event_script()}
</body>
</html>
"""


def build() -> Path:
    content_overrides = load_content_overrides()
    destinations = [consolidate_destination(item) for item in load_json("destinations.json")]
    destinations = rank_destinations(destinations)
    retirement_costs = load_retirement_costs()
    mortgage_profiles = load_mortgage_profiles()
    guide_pages = [RETIREMENT_DESTINATIONS_PAGE, *SEO_PAGES]
    listings = load_json("listings.json")
    fx = load_json("fx_rates.json")
    listings_by_dest: dict[str, list[dict]] = {}
    for listing in listings:
        listings_by_dest.setdefault(listing["destination_id"], []).append(listing)

    cards = "".join(
        build_destination_card(dest, listings_by_dest.get(dest["id"], []))
        for dest in destinations
    )

    avg_score = sum(float(item.get("decision_score", 0) or 0) for item in destinations) / len(destinations)
    min_price = min(float(item.get("usd_per_m2", 0) or 0) for item in destinations)
    countries = len({item.get("country") for item in destinations if item.get("country")})
    auto_internal_links = load_auto_internal_links()
    for entry in content_overrides:
        target = entry["target_url"]
        if target == SITE_URL:
            base_html = build_landing_page(destinations, guide_pages, listings, countries, content_overrides=[])
        elif target.startswith(f"{SITE_URL}countries/"):
            slug = target.removeprefix(f"{SITE_URL}countries/").strip("/")
            hub = next((item for item in COUNTRY_HUBS if item["slug"] == slug), None)
            if hub is None:
                raise ValueError(f"Unsupported SEO content target URL: {target}")
            base_html = build_country_hub_page(hub, destinations, SEO_PAGES, content_overrides=[])
        elif target.startswith(f"{SITE_URL}destinations/"):
            slug = target.removeprefix(f"{SITE_URL}destinations/").strip("/")
            dest = next((item for item in destinations if destination_slug(item) == slug), None)
            if dest is None:
                raise ValueError(f"Unsupported SEO content target URL: {target}")
            base_html = build_destination_page(
                dest, listings_by_dest.get(dest["id"], []), destinations, SEO_PAGES, content_overrides=[]
            )
        else:
            slug = target.removeprefix(SITE_URL).strip("/")
            page = next((item for item in SEO_PAGES if item["slug"] == slug), None)
            if page is None:
                raise ValueError(f"Unsupported SEO content target URL: {target}")
            base_html = build_seo_page(
                page, destinations, SEO_PAGES, auto_links=auto_internal_links, content_overrides=[]
            )
        parser = PageContextParser()
        parser.feed(base_html)
        allowed_hashes = {content_hash(
            parser.values["title"], parser.values["description"], parser.values["h1"],
            parser.values["intro"], tuple(parser.faqs),
        )}
        artifact_path = ARTIFACTS / target.removeprefix(SITE_URL).strip("/") / "index.html"
        if target == SITE_URL:
            artifact_path = ARTIFACTS / "index.html"
        if artifact_path.exists():
            prior_parser = PageContextParser()
            prior_parser.feed(artifact_path.read_text(encoding="utf-8"))
            allowed_hashes.add(content_hash(
                prior_parser.values["title"], prior_parser.values["description"], prior_parser.values["h1"],
                prior_parser.values["intro"], tuple(prior_parser.faqs),
            ))
        if entry["base_content_hash"] not in allowed_hashes:
            raise ValueError(f"Stale SEO content base hash: {target}")
    category_options = """
      <option value="city">City</option>
      <option value="coast-island">Coast / island</option>
      <option value="mountain">Mountain</option>
      <option value="lake">Lake</option>
    """
    app_data = json.dumps(
        {
            "destinations": destinations,
            "listings": listings,
            "fx": fx,
            "generated": date.today().isoformat(),
        },
        ensure_ascii=False,
    )

    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  __FAVICON_LINKS__
  <title>Global Home Atlas | Compare Global Property Investment Destinations</title>
  <meta name="description" content="Compare global home and property investment destinations with decision scores, ownership clarity, lifestyle fit, yields, and representative market evidence.">
  <link rel="canonical" href="https://globalhomeatlas.com/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Global Home Atlas">
  <meta property="og:title" content="Global Home Atlas">
  <meta property="og:description" content="Compare global home and property investment destinations with decision scores, ownership clarity, lifestyle fit, yields, and representative market evidence.">
  <meta property="og:url" content="https://globalhomeatlas.com/">
  <meta name="twitter:card" content="summary_large_image">
  __ANALYTICS_HEAD__
  <script type="application/ld+json">__HOME_SCHEMA__</script>
  <style>
    :root {
      color: #24312d;
      background: #f5f1e9;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-synthesis: none;
      text-rendering: optimizeLegibility;
      --ink: #24312d;
      --muted: #68776f;
      --line: rgba(36, 49, 45, .13);
      --paper: #fffdf7;
      --cream: #f5f1e9;
      --ivory: #fffdf7;
      --stone: #ebe5da;
      --sage: #c7d3c2;
      --eucalyptus: #5f7f72;
      --sea-glass: #b9ced0;
      --brass: #a98a4b;
      --terracotta: #b76f57;
      --deep: #24312d;
      --teal: #5f7f72;
      --gold: #a98a4b;
      --clay: #b76f57;
      --blue: #7f9ea0;
      --shadow: 0 18px 48px rgba(36, 49, 45, .10);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin: 0; min-width: 320px; }
    button, input, select { font: inherit; }
    button { cursor: pointer; }
    a { color: var(--teal); overflow-wrap: anywhere; text-decoration-thickness: 1px; text-underline-offset: 3px; }
    p { line-height: 1.55; }
    .shell { width: min(1220px, calc(100% - 32px)); margin: 0 auto; }
    .hero {
      position: relative;
      isolation: isolate;
      min-height: 88vh;
      display: grid;
      align-items: end;
      padding: 24px 0 28px;
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(255, 253, 247, .97) 0 34%, rgba(255, 253, 247, .72) 54%, rgba(199, 211, 194, .28)),
        linear-gradient(180deg, rgba(245, 241, 233, .12), rgba(245, 241, 233, .46)),
        url("/assets/atlas-map-coastal-sage.jpg");
      background-size: cover;
      background-position: center;
    }
    .hero::after {
      content: "";
      position: absolute;
      inset: auto 0 0;
      height: 34%;
      background: linear-gradient(180deg, rgba(245, 241, 233, 0), var(--cream));
      z-index: -1;
    }
    .topbar {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      z-index: 2;
      padding: 18px 0;
    }
    .topbar__inner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 18px;
    }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 850; letter-spacing: .02em; }
    .brand-logo { width: 164px; max-width: 46vw; height: auto; display: block; }
    .top-links { display: flex; gap: 18px; align-items: center; }
    .top-links a { color: rgba(36, 49, 45, .76); text-decoration: none; font-size: 13px; font-weight: 750; }
    .mobile-menu { display: none; position: relative; }
    .mobile-menu summary {
      min-height: 42px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 13px;
      border: 1px solid rgba(36, 49, 45, .20);
      border-radius: 6px;
      color: var(--ink);
      font-size: 13px;
      font-weight: 850;
      list-style: none;
      cursor: pointer;
    }
    .mobile-menu summary::-webkit-details-marker { display: none; }
    .mobile-menu nav {
      position: absolute;
      right: 0;
      top: calc(100% + 8px);
      z-index: 12;
      width: min(78vw, 280px);
      display: grid;
      gap: 2px;
      padding: 8px;
      border: 1px solid rgba(36, 49, 45, .16);
      border-radius: 8px;
      background: rgba(255, 253, 247, .98);
      box-shadow: 0 20px 50px rgba(36, 49, 45, .16);
    }
    .mobile-menu nav a { padding: 12px; border-radius: 6px; color: var(--ink); text-decoration: none; font-weight: 800; }
    .atlas-visual {
      margin-top: 14px;
      min-height: 180px;
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(36, 49, 45, .13);
      border-radius: 8px;
      background:
        radial-gradient(circle at 30% 34%, rgba(95, 127, 114, .50) 0 3px, transparent 4px),
        radial-gradient(circle at 62% 46%, rgba(169, 138, 75, .62) 0 4px, transparent 5px),
        radial-gradient(circle at 72% 58%, rgba(185, 206, 208, .72) 0 3px, transparent 4px),
        linear-gradient(135deg, rgba(255, 253, 247, .56), rgba(199, 211, 194, .14)),
        url("/assets/atlas-map-coastal-sage.jpg");
      background-size: cover;
      background-position: center;
    }
    .atlas-visual__label {
      position: absolute;
      left: 14px;
      top: 14px;
      display: grid;
      gap: 4px;
      padding: 10px;
      border: 1px solid rgba(36, 49, 45, .12);
      border-radius: 6px;
      background: rgba(255, 253, 247, .78);
      color: var(--ink);
      font-size: 12px;
      font-weight: 850;
    }
    .atlas-visual__label span { color: var(--muted); font-size: 10px; letter-spacing: .08em; text-transform: uppercase; }
    .atlas-visual__route {
      position: absolute;
      right: 12px;
      bottom: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      max-width: 80%;
    }
    .atlas-visual__route span {
      padding: 6px 8px;
      border: 1px solid rgba(36, 49, 45, .12);
      border-radius: 999px;
      background: rgba(255, 253, 247, .78);
      color: var(--ink);
      font-size: 11px;
      font-weight: 850;
    }
    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
      gap: 28px;
      align-items: end;
      padding-top: 92px;
    }
    .eyebrow {
      margin: 0 0 12px;
      color: var(--brass);
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .14em;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      max-width: 930px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(44px, 8vw, 104px);
      line-height: .88;
      letter-spacing: 0;
    }
    .lede {
      max-width: 760px;
      margin: 24px 0 0;
      color: rgba(36, 49, 45, .72);
      font-size: clamp(16px, 2.2vw, 20px);
    }
    .trust-panel {
      padding: 18px;
      border: 1px solid rgba(36, 49, 45, .13);
      border-radius: 8px;
      background: rgba(255, 253, 247, .72);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }
    .trust-panel h2 {
      margin: 0 0 12px;
      font-size: 15px;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    .trust-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .trust-grid div { padding: 12px; border-radius: 6px; background: rgba(199, 211, 194, .28); }
    .trust-grid span { display: block; color: var(--muted); font-size: 11px; font-weight: 850; text-transform: uppercase; }
    .trust-grid strong { display: block; margin-top: 5px; font-size: 22px; }
    .hero-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 26px; }
    .primary-action, .secondary-action {
      min-height: 46px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px;
      border-radius: 6px;
      font-weight: 850;
      text-decoration: none;
    }
    .primary-action { background: var(--eucalyptus); color: #fffdf7; }
    .secondary-action { border: 1px solid rgba(36, 49, 45, .20); color: var(--ink); background: rgba(255, 253, 247, .58); }
    main { margin-top: -34px; position: relative; z-index: 3; }
    .insight-bar {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--line);
      box-shadow: var(--shadow);
    }
    .insight-bar div { min-width: 0; padding: 18px; background: var(--paper); }
    .insight-bar span, dt {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .06em;
      text-transform: uppercase;
    }
    .insight-bar strong { display: block; margin-top: 7px; font-size: clamp(20px, 3vw, 28px); }
    .dashboard-onboarding {
      margin-top: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      overflow: hidden;
      box-shadow: 0 12px 40px rgba(36, 49, 45, .07);
    }
    .dashboard-onboarding__head { padding: 18px; border-bottom: 1px solid var(--line); }
    .dashboard-onboarding__head h2 { margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(24px, 4vw, 38px); }
    .dashboard-onboarding__head p { max-width: 720px; margin: 7px 0 0; color: var(--muted); }
    .dashboard-onboarding__grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; background: var(--line); }
    .dashboard-onboarding__grid article { min-width: 0; padding: 16px; background: #fffdf7; }
    .dashboard-onboarding__grid span { color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .dashboard-onboarding__grid strong { display: block; margin: 7px 0; font-size: 17px; line-height: 1.15; }
    .dashboard-onboarding__grid p { margin: 0; color: var(--muted); font-size: 13px; }
    .workbench {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
      padding: 24px 0 54px;
    }
    .control-panel {
      position: sticky;
      top: 14px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 253, 247, .92);
      box-shadow: 0 12px 40px rgba(36, 49, 45, .08);
      backdrop-filter: blur(18px);
    }
    .control-panel h2 { margin: 0 0 4px; font-size: 19px; }
    .control-panel p { margin: 0 0 14px; color: var(--muted); font-size: 13px; }
    .toolbar { display: grid; gap: 10px; }
    .field label { display: block; margin: 0 0 6px; color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .toolbar input, .toolbar select {
      min-height: 46px;
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 0 12px;
    }
    .lens-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 4px; }
    .lens-grid button, .export-row button {
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-weight: 800;
    }
    .lens-grid button[aria-pressed="true"] { background: var(--eucalyptus); color: #fffdf7; border-color: var(--eucalyptus); }
    .export-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }
    .weight-panel {
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }
    .weight-panel h3 { margin: 0 0 8px; font-size: 14px; }
    .weight-panel p { margin: 0 0 10px; color: var(--muted); font-size: 12px; }
    .weight-controls { display: grid; gap: 9px; }
    .weight-control {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 96px 38px;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
      font-weight: 780;
    }
    .weight-control input { width: 100%; accent-color: var(--teal); }
    .weight-control strong { color: var(--ink); text-align: right; font-size: 12px; }
    .compare-panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      overflow: hidden;
    }
    .compare-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .compare-actions button, .compare-actions a, .decision-row button {
      min-height: 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-weight: 850;
      padding: 0 12px;
      text-decoration: none;
    }
    .compare-actions a { background: var(--deep); color: #fffdf7; }
    .compare-table-wrap { overflow-x: auto; }
    .compare-table { width: 100%; border-collapse: collapse; min-width: 720px; }
    .compare-table th, .compare-table td {
      padding: 11px 12px;
      border-top: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 13px;
    }
    .compare-table th { color: var(--muted); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }
    .compare-empty { padding: 18px; color: var(--muted); border-top: 1px solid var(--line); }
    .memo-upgrade {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: center;
      padding: 16px 18px;
      border-top: 1px solid var(--line);
      background: #f5f1e9;
    }
    .memo-upgrade h3 { margin: 0 0 6px; font-size: 15px; }
    .memo-upgrade p { margin: 0; color: var(--muted); font-size: 13px; }
    .memo-upgrade ul {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 10px 0 0;
      padding: 0;
      list-style: none;
    }
    .memo-upgrade li {
      padding: 6px 8px;
      border: 1px solid rgba(36, 49, 45, .12);
      border-radius: 999px;
      background: #fffdf7;
      color: #3f4d48;
      font-size: 12px;
      font-weight: 800;
    }
    .memo-upgrade a {
      min-height: 42px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 14px;
      border-radius: 6px;
      background: var(--eucalyptus);
      color: #fffdf7;
      font-weight: 850;
      text-decoration: none;
      white-space: nowrap;
    }
    .decision-row {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      align-items: center;
      padding: 0 18px 16px;
    }
    .destination-card > .access-notice { margin: 0 18px 16px; }
    .access-notice { padding: 14px 16px; border-left: 4px solid var(--clay); background: #f8ebe6; }
    .access-notice strong { font-size: 14px; }
    .access-notice p { margin: 4px 0 0; color: #59443d; font-size: 14px; line-height: 1.45; }
    .method-card {
      margin-top: 16px;
      padding: 14px;
      border-radius: 8px;
      background: #eef3f0;
    }
    .method-card h3 { margin: 0 0 8px; font-size: 14px; }
    .method-card ul { margin: 0; padding-left: 18px; color: var(--muted); font-size: 13px; line-height: 1.45; }
    .mobile-jump {
      display: none;
      gap: 8px;
      overflow-x: auto;
      padding: 12px 16px;
      margin: 0 -16px;
      scrollbar-width: none;
    }
    .mobile-jump a {
      flex: 0 0 auto;
      padding: 9px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--ink);
      text-decoration: none;
      font-size: 13px;
      font-weight: 800;
    }
    .content-stack { display: grid; gap: 18px; min-width: 0; }
    .section-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      overflow: hidden;
    }
    .section-header {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }
    .section-header h2 { margin: 0; font-size: clamp(22px, 4vw, 34px); font-family: Georgia, "Times New Roman", serif; }
    .section-header p { margin: 6px 0 0; color: var(--muted); max-width: 680px; }
    #resultCount { white-space: nowrap; color: var(--muted); font-size: 13px; font-weight: 850; }
    .spotlight-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--line); }
    .spotlight-card { min-width: 0; padding: 18px; background: #fffdf7; }
    .spotlight-card span {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: var(--deep);
      color: #fffdf7;
      font-weight: 900;
    }
    .spotlight-card h3 { margin: 14px 0 4px; font-size: 19px; }
    .spotlight-card p { margin: 0 0 14px; color: var(--muted); font-size: 13px; }
    .spotlight-card dl { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 0; }
    .spotlight-card dd { margin: 4px 0 0; font-weight: 850; }
    .cards { display: grid; gap: 12px; }
    .destination-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      overflow: hidden;
    }
    .destination-card[open] { box-shadow: var(--shadow); }
    .destination-card > summary {
      min-height: 116px;
      display: grid;
      grid-template-columns: 56px minmax(0, 1fr) 84px 96px;
      gap: 14px;
      align-items: center;
      padding: 18px;
      cursor: pointer;
      list-style: none;
    }
    .destination-card > summary::-webkit-details-marker { display: none; }
    .rank-mark {
      width: 48px;
      height: 48px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      background: #eef3f0;
      color: var(--deep);
      font-weight: 900;
    }
    .summary-copy p { margin: 0 0 6px; color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .summary-copy h3 { margin: 0 0 6px; font-size: clamp(20px, 3.4vw, 26px); line-height: 1.05; }
    .summary-copy span {
      display: -webkit-box;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.4;
      overflow: hidden;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    .score-dial {
      width: 76px;
      height: 76px;
      display: grid;
      place-items: center;
      align-content: center;
      border: 1px solid rgba(23, 107, 98, .2);
      border-radius: 50%;
      background: radial-gradient(circle at 50% 50%, #fff 52%, #dbe9e5 53%);
      text-align: center;
    }
    .score-dial strong { display: block; color: var(--teal); font-size: 21px; line-height: 1; }
    .score-dial small { color: var(--muted); font-weight: 800; }
    .summary-compare {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-size: 13px;
      font-weight: 850;
    }
    .summary-compare input { width: 17px; height: 17px; accent-color: var(--teal); }
    .metric-strip {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      background: var(--line);
      border-top: 1px solid var(--line);
    }
    .metric-strip div { min-width: 0; padding: 16px 18px; background: #fbfaf6; }
    .metric-strip strong { display: block; margin: 6px 0; font-size: 19px; }
    .metric-strip em {
      display: inline-flex;
      max-width: 100%;
      padding: 4px 7px;
      border-radius: 999px;
      background: #edf3f1;
      color: var(--muted);
      font-size: 11px;
      font-style: normal;
      font-weight: 800;
      overflow-wrap: anywhere;
    }
    .metric-strip em[data-tone="high"] { background: #e7f2dc; color: #47652f; }
    .metric-strip em[data-tone="low"] { background: #f8e8df; color: #8a3f28; }
    .brief-grid, .pros-cons {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1px;
      background: var(--line);
      border-top: 1px solid var(--line);
    }
    .brief-grid article, .pros-cons article, .score-board, .listings-wrap { padding: 18px; background: var(--paper); }
    .brief-grid h4, .pros-cons h4, .section-heading h4 { margin: 0 0 8px; font-size: 14px; letter-spacing: .04em; text-transform: uppercase; }
    .brief-grid p, .pros-cons li, .section-heading p, .listing p { color: var(--muted); font-size: 14px; }
    .risk-note { color: #8a3f28 !important; }
    .pros-cons { grid-template-columns: repeat(2, 1fr); }
    .pros-cons ul { margin: 0; padding-left: 18px; }
    .score-board, .listings-wrap { border-top: 1px solid var(--line); }
    .section-heading { display: flex; justify-content: space-between; gap: 18px; align-items: end; margin-bottom: 14px; }
    .section-heading p { margin: 0; max-width: 560px; }
    .score-board ul {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .score-row {
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }
    .score-row div { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
    .score-row span { color: var(--muted); font-size: 13px; font-weight: 760; }
    .score-row strong { font-size: 15px; }
    .score-row i {
      display: block;
      height: 6px;
      margin-top: 8px;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--teal) var(--value), #e6e1d8 var(--value));
    }
    .score-row small { display: block; margin-top: 6px; color: var(--muted); font-size: 11px; font-weight: 760; }
    .score-row p { margin: 7px 0 0; color: var(--muted); font-size: 12px; line-height: 1.4; }
    .evidence-board { padding: 18px; border-top: 1px solid var(--line); background: var(--paper); }
    .evidence-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .evidence-item { padding: 13px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    .evidence-item div { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
    .evidence-item span { color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .evidence-item strong { font-size: 15px; }
    .evidence-item p { margin: 8px 0; color: var(--muted); font-size: 13px; }
    .evidence-item em {
      display: inline-flex;
      padding: 4px 7px;
      border-radius: 999px;
      background: #edf3f1;
      color: var(--muted);
      font-size: 11px;
      font-style: normal;
      font-weight: 800;
    }
    .listings { display: grid; gap: 10px; }
    .listing {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(220px, .74fr);
      gap: 14px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }
    .listing__type { margin: 0 0 5px; color: var(--gold) !important; font-size: 11px !important; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
    .listing h5 { margin: 0 0 5px; font-size: 16px; }
    .listing p { margin: 0; }
    .listing__facts { display: grid; grid-template-columns: repeat(2, 1fr); gap: 9px; margin: 0; }
    .listing dd { margin: 3px 0 0; font-weight: 900; }
    .source-link { grid-column: 1 / -1; font-size: 13px; font-weight: 850; }
    .research-note {
      padding: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    .guide-section {
      margin: 0 0 54px;
      padding: 26px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      box-shadow: 0 12px 40px rgba(36, 49, 45, .07);
    }
    .guide-section__header {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      margin-bottom: 18px;
    }
    .guide-section__header h2 {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(24px, 4vw, 38px);
    }
    .guide-section__header p { margin: 6px 0 0; color: var(--muted); max-width: 680px; }
    .guide-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .guide-grid article {
      min-width: 0;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }
    .guide-grid span {
      color: var(--gold);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .guide-grid h3 { margin: 8px 0; font-size: 18px; line-height: 1.15; }
    .guide-grid p { margin: 0; color: var(--muted); font-size: 14px; }
    .landscape-band {
      min-height: 210px;
      display: grid;
      align-items: end;
      margin: 0 0 54px;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background:
        linear-gradient(90deg, rgba(36, 49, 45, .72), rgba(36, 49, 45, .20) 52%, rgba(255, 253, 247, .10)),
        url("/assets/coastal-sage-landscape-band.jpg");
      background-size: cover;
      background-position: center;
      box-shadow: 0 12px 40px rgba(36, 49, 45, .07);
    }
    .landscape-band blockquote {
      max-width: 620px;
      margin: 0;
      padding: 28px;
      color: #fffdf7;
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(22px, 4vw, 34px);
      line-height: 1.1;
    }
    .landscape-band cite { display: block; margin-top: 10px; font-family: Inter, ui-sans-serif, system-ui, sans-serif; font-size: 12px; font-style: normal; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
    .compact-hero {
      padding: 96px 0 34px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(90deg, #fffdf7, #eef3f0);
    }
    .compact-hero .topbar { position: absolute; }
    .compact-hero__content h1 { font-size: clamp(42px, 7vw, 72px); line-height: .95; }
    .compact-hero__content .lede { max-width: 760px; margin-top: 14px; font-size: 17px; }
    main { margin-top: 0; }
    .dashboard-shell { display: grid; gap: 18px; padding: 22px 0 54px; }
    .filter-bar {
      position: sticky;
      top: 0;
      z-index: 8;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 253, 247, .96);
      box-shadow: 0 10px 30px rgba(36, 49, 45, .08);
      backdrop-filter: blur(16px);
    }
    .filter-bar .toolbar { grid-template-columns: minmax(190px, 1.35fr) repeat(3, minmax(145px, .75fr)); align-items: end; }
    .advanced-controls { margin-top: 12px; border-top: 1px solid var(--line); }
    .advanced-controls > summary { width: fit-content; padding: 12px 2px 0; color: var(--teal); cursor: pointer; font-size: 13px; font-weight: 850; }
    .advanced-controls__grid { display: grid; grid-template-columns: 1.4fr .6fr; gap: 14px; padding-top: 14px; }
    .advanced-controls__grid > section { margin: 0; padding: 14px; border: 1px solid var(--line); border-radius: 7px; background: #fff; }
    .advanced-controls__grid h2 { margin: 0 0 8px; font-size: 15px; }
    .advanced-controls .weight-panel { padding-top: 14px; border-top: 1px solid var(--line); }
    .market-list { overflow: hidden; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); }
    .market-list__header { display: flex; justify-content: space-between; gap: 18px; align-items: end; padding: 18px; }
    .market-list__header p { margin: 5px 0 0; color: var(--muted); font-size: 14px; }
    .market-list__labels, .market-row { display: grid; grid-template-columns: minmax(250px, 1.7fr) 92px 120px 140px 120px; gap: 16px; align-items: center; }
    .market-list__labels { padding: 10px 16px; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); background: #eef3f0; color: var(--muted); font-size: 10px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }
    .market-list__market-labels { display: flex; align-items: center; gap: 5px; }
    .market-sort { min-width: 0; padding: 0; border: 0; background: transparent; color: inherit; font-size: inherit; font-weight: inherit; letter-spacing: inherit; text-transform: inherit; white-space: nowrap; }
    .market-sort--text { text-align: left; }
    .market-sort--numeric { width: 100%; text-align: right; }
    .market-sort:hover, .market-sort:focus-visible, .market-sort[aria-pressed="true"] { color: var(--ink); }
    .sort-indicator { display: inline-block; width: 9px; text-align: center; }
    .cards { gap: 0; }
    .market-row { min-width: 0; padding: 12px 16px; border-bottom: 1px solid var(--line); }
    .market-row:last-child { border-bottom: 0; }
    .market-row__market { min-width: 0; display: grid; grid-template-columns: 38px minmax(0, 1fr); gap: 10px; align-items: center; }
    .market-row .rank-mark { width: 36px; height: 36px; border-radius: 6px; font-size: 12px; }
    .market-row__identity { min-width: 0; }
    .market-row__identity h3 { margin: 0; font-size: 16px; line-height: 1.15; }
    .market-row__identity h3 a { color: var(--ink); text-decoration: none; }
    .market-row__identity p { margin: 3px 0 0; color: var(--muted); font-size: 12px; }
    .market-row__metric span { display: none; }
    .market-row__metric { text-align: right; }
    .market-row__metric strong { font-size: 13px; }
    .market-row__warning { grid-column: 1 / -1; margin: -2px 0 2px 48px; color: #7a3e2b; font-size: 12px; }
    .market-row__select { display: none; }
    body.compare-mode .market-row { grid-template-columns: 34px minmax(250px, 1.7fr) 92px 120px 140px 120px; }
    body.compare-mode .market-row__select { display: grid; justify-items: center; gap: 3px; color: var(--muted); font-size: 9px; text-transform: uppercase; }
    .market-list__tools { display: flex; align-items: center; gap: 12px; }
    #compareModeToggle, .compare-selection-bar button {
      min-height: 38px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-weight: 800;
    }
    #compareModeToggle[aria-pressed="true"] { background: var(--eucalyptus); border-color: var(--eucalyptus); color: #fff; }
    .compare-selection-bar { display: flex; justify-content: space-between; align-items: center; gap: 14px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: #eef3f0; }
    .compare-selection-bar > div { display: flex; flex-wrap: wrap; gap: 8px; }
    .compare-panel { margin: 0; }
    .hidden { display: none; }
    @media (max-width: 980px) {
      .hero { min-height: auto; padding-bottom: 66px; }
      .hero-grid, .workbench { grid-template-columns: 1fr; }
      .control-panel { position: static; }
      .mobile-jump { display: flex; }
      .spotlight-grid, .guide-grid, .dashboard-onboarding__grid { grid-template-columns: 1fr; }
      .metric-strip, .brief-grid { grid-template-columns: repeat(2, 1fr); }
      .filter-bar { position: static; }
      .filter-bar .toolbar { grid-template-columns: 1fr 1fr; }
      .market-list__labels { display: none; }
      .market-row { grid-template-columns: minmax(220px, 1.5fr) repeat(2, minmax(100px, .7fr)); }
      body.compare-mode .market-row { grid-template-columns: 34px minmax(220px, 1.5fr) repeat(2, minmax(100px, .7fr)); }
      .market-row__metric:nth-of-type(4), .market-row__metric:nth-of-type(5) { display: none; }
    }
    @media (max-width: 680px) {
      .shell { width: min(1220px, calc(100% - 28px)); }
      .top-links { display: none; }
      .mobile-menu { display: block; }
      .hero { min-height: auto; align-items: end; padding-bottom: 36px; }
      .hero-grid { gap: 16px; padding-top: 78px; }
      .hero-grid > div { max-width: min(100%, 362px); }
      h1 { max-width: min(100%, 362px); font-size: clamp(34px, 10vw, 44px); line-height: 1; overflow-wrap: anywhere; }
      .lede { margin-top: 18px; font-size: 16px; }
      .hero-actions { margin-top: 18px; }
      .atlas-visual__route { left: 10px; right: 10px; max-width: none; justify-content: flex-end; }
      .atlas-visual__route span { padding: 5px 7px; font-size: 10px; }
      .trust-panel { padding: 14px; }
      .trust-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
      .trust-grid div { padding: 10px; }
      .trust-grid strong { font-size: 20px; }
      .insight-bar, .metric-strip, .brief-grid, .pros-cons, .score-board ul, .evidence-grid, .listing, .listing__facts { grid-template-columns: 1fr; }
      .insight-bar { margin: 0 -2px; }
      main { margin-top: -24px; }
      .workbench { padding-top: 14px; }
      .section-header, .section-heading { display: block; }
      .memo-upgrade { grid-template-columns: 1fr; }
      .memo-upgrade a { width: 100%; }
      #resultCount { display: block; margin-top: 8px; }
      summary { grid-template-columns: 44px minmax(0, 1fr); gap: 12px; min-height: 0; padding: 15px; align-items: start; }
      .rank-mark { width: 40px; height: 40px; }
      .score-dial { grid-column: 2; width: auto; height: auto; display: flex; justify-content: flex-start; gap: 4px; border: 0; border-radius: 0; background: transparent; text-align: left; }
      .summary-compare { grid-column: 2; justify-content: flex-start; width: max-content; padding: 0 10px; }
      .summary-copy span { -webkit-line-clamp: 3; }
      .brief-grid article, .pros-cons article, .score-board, .evidence-board, .listings-wrap, .section-header, .research-note { padding: 15px; }
      .metric-strip div { padding: 14px 15px; }
      .lens-grid, .export-row { grid-template-columns: 1fr 1fr; }
      .compact-hero { padding: 88px 0 28px; }
      .compact-hero__content h1 { font-size: 44px; }
      .dashboard-shell { padding-top: 14px; }
      .filter-bar .toolbar, .advanced-controls__grid { grid-template-columns: 1fr; }
      .market-list__header { display: block; padding: 15px; }
      .market-row { grid-template-columns: 1fr 1fr; gap: 10px; padding: 14px 15px; }
      body.compare-mode .market-row { grid-template-columns: 1fr 1fr; }
      .market-row__market { grid-column: 1 / -1; }
      .market-row__metric { display: block !important; }
      .market-row__metric { text-align: left; }
      .market-row__metric span { display: block; color: var(--muted); font-size: 10px; font-weight: 900; letter-spacing: .05em; text-transform: uppercase; }
      .market-row__metric strong { display: block; margin-top: 3px; }
      .market-row__warning { margin-left: 0; }
      body.compare-mode .market-row__select { grid-column: 1 / -1; display: flex; align-items: center; justify-items: initial; gap: 8px; }
      .market-list__tools, .compare-selection-bar { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <header class="compact-hero" id="top">
    __PRIMARY_NAV__
    <div class="shell compact-hero__content">
      <p class="eyebrow">Global Home Atlas</p>
      <h1>Destinations</h1>
      <p class="lede">Search __DEST_COUNT__ destinations by price, expected yield, ownership clarity, and overall fit.</p>
    </div>
  </header>

  <main>
    <div class="shell dashboard-shell">
      <section class="filter-bar" aria-label="Destination filters">
        <form class="toolbar" id="toolbar">
          <div class="field field--search"><label for="search">Search</label><input id="search" type="search" placeholder="Destination or country" aria-label="Search destination or country"></div>
          <div class="field"><label for="category">Location type</label><select id="category" aria-label="Filter by location type"><option value="all">All location types</option>__CATEGORY_OPTIONS__</select></div>
          <div class="field"><label for="sort">Sort by</label><select id="sort" aria-label="Sort destinations"><option value="rank">Rank</option><option value="name">Destination name</option><option value="score">Overall rating</option><option value="price">Lowest price</option><option value="yield">Expected net yield</option><option value="ownership">Ownership clarity</option><option value="access">Buyer access</option><option value="retirement">Retirement</option></select></div>
          <div class="field"><label for="buyerGoal">Buying goal</label><select id="buyerGoal"><option value="all">Overall fit</option><option value="retirement">Retirement / lifestyle</option><option value="second-home">Second home</option><option value="investment">Investment-led</option><option value="ownership">Clear ownership</option></select></div>
        </form>
      </section>

      <div class="compare-selection-bar hidden" id="compareSelectionBar" aria-live="polite">
        <strong id="compareSelectionCount">0 destinations selected</strong>
        <div><button type="button" id="openCompare">Compare</button><button type="button" id="saveSelection">Save</button><button type="button" id="clearCompare">Clear</button><button type="button" id="exportMemo">Export</button></div>
      </div>

      <section class="compare-panel hidden" id="compare">
        <div class="section-header"><div><h2>Compare selected destinations</h2></div></div>
        <div id="compareOutput" class="compare-empty">Select at least two destinations to compare.</div>
      </section>

      <section class="market-list" id="markets">
        <div class="market-list__header"><p>Choose a destination name for the full research.</p><div class="market-list__tools"><span id="resultCount">__DEST_COUNT__ shown</span><button type="button" id="compareModeToggle" aria-pressed="false">Compare destinations</button></div></div>
        <div class="market-list__labels">
          <span class="market-list__market-labels"><button type="button" class="market-sort market-sort--text" data-column-sort="rank" data-sort-label="rank">Rank <span class="sort-indicator" aria-hidden="true">↑</span></button><span aria-hidden="true">/</span><button type="button" class="market-sort market-sort--text" data-column-sort="name" data-sort-label="destination name">Destination <span class="sort-indicator" aria-hidden="true"></span></button></span>
          <button type="button" class="market-sort market-sort--numeric" data-column-sort="score" data-sort-label="overall rating">Overall rating <span class="sort-indicator" aria-hidden="true"></span></button>
          <button type="button" class="market-sort market-sort--numeric" data-column-sort="price" data-sort-label="price guide">Price guide <span class="sort-indicator" aria-hidden="true"></span></button>
          <button type="button" class="market-sort market-sort--numeric" data-column-sort="yield" data-sort-label="expected net yield">Expected net yield <span class="sort-indicator" aria-hidden="true"></span></button>
          <button type="button" class="market-sort market-sort--numeric" data-column-sort="ownership" data-sort-label="ownership clarity">Ownership clarity <span class="sort-indicator" aria-hidden="true"></span></button>
        </div>
        <div class="cards" id="cards">__CARDS__</div>
        <p class="research-note">FX as of __FX_AS_OF__. Verify current prices, availability, taxes, permits, title, and local advice before acting.</p>
      </section>

      <details class="advanced-controls">
        <summary>Advanced research tools</summary>
        <div class="advanced-controls__grid">
          <section class="weight-panel"><h2>Score weights</h2><p>Adjust the model only when your priorities differ from the default.</p><div class="weight-controls">__WEIGHT_CONTROLS__</div></section>
          <section><h2>Data exports</h2><div class="export-row"><button type="button" id="export">JSON</button><button type="button" id="exportCsv">CSV</button></div></section>
        </div>
      </details>
    </div>
  </main>

  <script type="application/json" id="app-data">__APP_DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById("app-data").textContent);
    const cards = Array.from(document.querySelectorAll(".market-row"));
    const cardsRoot = document.getElementById("cards");
    const search = document.getElementById("search");
    const category = document.getElementById("category");
    const sort = document.getElementById("sort");
    const sortButtons = Array.from(document.querySelectorAll("[data-column-sort]"));
    const resultCount = document.getElementById("resultCount");
    const buyerGoal = document.getElementById("buyerGoal");
    const weightInputs = Array.from(document.querySelectorAll("[data-weight-key]"));
    const comparePanel = document.getElementById("compare");
    const compareOutput = document.getElementById("compareOutput");
    const compareModeToggle = document.getElementById("compareModeToggle");
    const compareSelectionBar = document.getElementById("compareSelectionBar");
    const compareSelectionCount = document.getElementById("compareSelectionCount");
    const compareSelected = new Set();
    const goalLabels = { retirement: "retirement / lifestyle", "second-home": "second home", investment: "investment-led buying", ownership: "clear ownership" };
    const defaultSortDirections = { rank: "asc", name: "asc", score: "desc", price: "asc", yield: "desc", ownership: "desc", access: "asc", retirement: "desc" };
    let sortKey = sort.value;
    let sortDirection = defaultSortDirections[sortKey];

    const destinationsById = new Map(data.destinations.map((destination) => [destination.id, destination]));
    data.destinations.forEach((destination) => {
      destination.custom_score = destination.decision_score;
    });

    function cardRank(card) {
      return Number(card.querySelector(".rank-mark span").textContent.replace("#", ""));
    }

    function updateSortIndicators() {
      sortButtons.forEach((button) => {
        const active = button.dataset.columnSort === sortKey;
        const directionLabel = sortDirection === "asc" ? "ascending" : "descending";
        button.setAttribute("aria-pressed", String(active));
        button.setAttribute("aria-label", active
          ? `Sort by ${button.dataset.sortLabel}, currently ${directionLabel}`
          : `Sort by ${button.dataset.sortLabel}`);
        button.querySelector(".sort-indicator").textContent = active ? (sortDirection === "asc" ? "↑" : "↓") : "";
      });
    }

    function activeWeights() {
      const raw = Object.fromEntries(weightInputs.map((input) => [input.dataset.weightKey, Number(input.value)]));
      const total = Object.values(raw).reduce((sum, value) => sum + value, 0);
      if (!total) {
        return Object.fromEntries(data.destinations[0].decision_dimensions.map((item) => [item.key, item.weight]));
      }
      return Object.fromEntries(Object.entries(raw).map(([key, value]) => [key, value / total]));
    }

    function recalculateScores() {
      const weights = activeWeights();
      weightInputs.forEach((input) => {
        input.closest(".weight-control").querySelector("strong").textContent = input.value + "%";
      });
      data.destinations.forEach((destination) => {
        const score = destination.decision_dimensions.reduce((sum, item) => sum + item.score * (weights[item.key] || 0), 0);
        destination.custom_score = Number(score.toFixed(2));
        const card = document.querySelector(`.market-row[data-id="${destination.id}"]`);
        if (card) {
          card.dataset.score = destination.custom_score;
          card.querySelector("[data-custom-score]").textContent = destination.custom_score.toFixed(1);
        }
      });
      renderCompare();
      applyFilters();
    }

    function applyFilters() {
      const query = search.value.trim().toLowerCase();
      const selectedCategory = category.value;
      let shown = 0;

      cards.forEach((card) => {
        const matchesQuery = !query || card.dataset.name.includes(query) || card.dataset.country.includes(query);
        const locationTypes = (card.dataset.locationTypes || "").split(" ");
        const matchesCategory = selectedCategory === "all" || locationTypes.includes(selectedCategory);
        const visible = matchesQuery && matchesCategory;
        card.classList.toggle("hidden", !visible);
        if (visible) shown += 1;
      });

      const sorted = [...cards].sort((a, b) => {
        let comparison = 0;
        if (buyerGoal.value !== "all") {
          const goalKey = "goal" + buyerGoal.value.split("-").map((part) => part[0].toUpperCase() + part.slice(1)).join("");
          comparison = Number(a.dataset[goalKey]) - Number(b.dataset[goalKey]);
          if (comparison === 0) comparison = Number(a.dataset.score) - Number(b.dataset.score);
          return comparison === 0 ? cardRank(a) - cardRank(b) : -comparison;
        }
        if (sortKey === "name") comparison = a.dataset.name.localeCompare(b.dataset.name);
        else if (sortKey === "score") comparison = Number(a.dataset.score) - Number(b.dataset.score);
        else if (sortKey === "price") comparison = Number(a.dataset.price) - Number(b.dataset.price);
        else if (sortKey === "yield") comparison = Number(a.dataset.yield) - Number(b.dataset.yield);
        else if (sortKey === "ownership") comparison = Number(a.dataset.ownership) - Number(b.dataset.ownership);
        else if (sortKey === "access") comparison = a.dataset.access.localeCompare(b.dataset.access);
        else if (sortKey === "retirement") comparison = Number(a.dataset.retirement) - Number(b.dataset.retirement);
        else comparison = cardRank(a) - cardRank(b);
        if (comparison === 0) return cardRank(a) - cardRank(b);
        return sortDirection === "asc" ? comparison : -comparison;
      });
      sorted.forEach((card) => cardsRoot.appendChild(card));
      const countLabel = shown + (shown === 1 ? " destination" : " destinations");
      resultCount.textContent = buyerGoal.value === "all"
        ? countLabel + " shown"
        : countLabel + " ranked for " + goalLabels[buyerGoal.value];
    }

    function destinationMetric(destination, key) {
      return destination.decision_dimensions.find((item) => item.key === key)?.score || 0;
    }

    function selectedCompareDestinations() {
      return [...compareSelected].map((id) => destinationsById.get(id)).filter(Boolean);
    }

    function renderCompare() {
      const selected = selectedCompareDestinations();
      compareSelectionCount.textContent = selected.length + (selected.length === 1 ? " destination selected" : " destinations selected");
      compareSelectionBar.classList.toggle("hidden", selected.length === 0 && !document.body.classList.contains("compare-mode"));
      comparePanel.classList.toggle("hidden", selected.length < 2);
      if (selected.length < 2) {
        compareOutput.className = "compare-empty";
        compareOutput.textContent = selected.length === 1
          ? "Select one more destination to build a comparison table."
          : "Select at least two destinations to build a comparison table.";
        return;
      }
      compareOutput.className = "compare-table-wrap";
      const rows = [
        ["Decision score", ...selected.map((d) => d.custom_score.toFixed(1))],
        ["USD/m2", ...selected.map((d) => "$" + Number(d.usd_per_m2 || 0).toLocaleString())],
        ["Net yield", ...selected.map((d) => d.net_yield_estimate || "n/a")],
        ["Ownership", ...selected.map((d) => destinationMetric(d, "ownership_clarity").toFixed(1) + "/5")],
        ["Rental profit", ...selected.map((d) => destinationMetric(d, "rental_profit").toFixed(1) + "/5")],
        ["Retirement fit", ...selected.map((d) => destinationMetric(d, "retirement_fit").toFixed(1) + "/5")],
        ["Exit liquidity", ...selected.map((d) => destinationMetric(d, "exit_liquidity").toFixed(1) + "/5")],
        ["Panel thesis", ...selected.map((d) => d.profit_driver || d.panel_verdict || "n/a")]
      ];
      compareOutput.innerHTML = `
        <table class="compare-table">
          <thead><tr><th>Metric</th>${selected.map((d) => `<th>${d.name}<br><small>${d.country || ""}</small></th>`).join("")}</tr></thead>
          <tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${String(cell)}</td>`).join("")}</tr>`).join("")}</tbody>
        </table>
      `;
    }

    function setCompare(id, checked) {
      if (checked && compareSelected.size >= 4 && !compareSelected.has(id)) {
        document.querySelector(`.compare-toggle[value="${id}"]`).checked = false;
        return;
      }
      if (checked) compareSelected.add(id);
      else compareSelected.delete(id);
      if (window.GHA) window.GHA.track("compare_selection", { destination_id: id, selected: checked, selected_count: compareSelected.size });
      renderCompare();
    }

    search.addEventListener("input", applyFilters);
    category.addEventListener("change", applyFilters);
    buyerGoal.addEventListener("change", applyFilters);
    sort.addEventListener("change", () => {
      buyerGoal.value = "all";
      sortKey = sort.value;
      sortDirection = defaultSortDirections[sortKey] || "asc";
      updateSortIndicators();
      applyFilters();
    });
    sortButtons.forEach((button) => {
      button.addEventListener("click", () => {
        buyerGoal.value = "all";
        const nextSortKey = button.dataset.columnSort;
        if (sortKey === nextSortKey) sortDirection = sortDirection === "asc" ? "desc" : "asc";
        else {
          sortKey = nextSortKey;
          sortDirection = defaultSortDirections[sortKey] || "asc";
        }
        sort.value = sortKey;
        updateSortIndicators();
        applyFilters();
      });
    });
    weightInputs.forEach((input) => input.addEventListener("input", recalculateScores));
    document.querySelectorAll(".compare-toggle").forEach((checkbox) => {
      checkbox.addEventListener("change", () => setCompare(checkbox.value, checkbox.checked));
    });
    compareModeToggle.addEventListener("click", () => {
      const active = !document.body.classList.contains("compare-mode");
      document.body.classList.toggle("compare-mode", active);
      compareModeToggle.setAttribute("aria-pressed", String(active));
      compareModeToggle.textContent = active ? "Done comparing" : "Compare destinations";
      renderCompare();
    });
    document.getElementById("openCompare").addEventListener("click", () => {
      if (selectedCompareDestinations().length < 2) return;
      comparePanel.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    document.getElementById("saveSelection").addEventListener("click", () => {
      localStorage.setItem("gha_memo_shortlist", JSON.stringify([...compareSelected]));
      compareSelectionCount.textContent = compareSelected.size + (compareSelected.size === 1 ? " market saved" : " markets saved");
      if (window.GHA) window.GHA.track("shortlist_save", { selected_count: compareSelected.size });
    });
    document.getElementById("clearCompare").addEventListener("click", () => {
      compareSelected.clear();
      document.querySelectorAll(".compare-toggle").forEach((checkbox) => {
        checkbox.checked = false;
      });
      renderCompare();
    });

    function downloadFile(filename, type, content) {
      const blob = new Blob([content], { type });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    }

    document.getElementById("export").addEventListener("click", () => {
      if (window.GHA) window.GHA.track("data_export_json", { destination_count: data.destinations.length });
      downloadFile("destination-property-dashboard-data.json", "application/json", JSON.stringify(data, null, 2));
    });

    document.getElementById("exportCsv").addEventListener("click", () => {
      if (window.GHA) window.GHA.track("data_export_csv", { destination_count: data.destinations.length });
      const rows = [
        ["rank", "destination", "country", "category", "decision_score", "custom_score", "usd_per_m2", "net_yield", "ownership_score", "retirement_score"],
        ...data.destinations.map((d) => [
          d.rank,
          d.name,
          d.country || "",
          d.category || "",
          d.decision_score,
          d.custom_score,
          d.usd_per_m2,
          d.net_yield_estimate || "",
          destinationMetric(d, "ownership_clarity"),
          destinationMetric(d, "retirement_fit")
        ])
      ];
      const csv = rows.map((row) => row.map((cell) => '"' + String(cell).replaceAll('"', '""') + '"').join(",")).join("\\n");
      downloadFile("destination-property-summary.csv", "text/csv", csv);
    });

    function previewDestinations() {
      if (compareSelected.size >= 2) return selectedCompareDestinations();
      return [...data.destinations].sort((a, b) => b.custom_score - a.custom_score).slice(0, 4);
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      })[char]);
    }

    function buildPreviewHtml() {
      const selected = previewDestinations();
      const generated = new Date().toISOString().slice(0, 10);
      const rows = selected.map((d) => `
        <section>
          <h2>${escapeHtml(d.name)} <span>${escapeHtml(d.country || "")}</span></h2>
          <dl>
            <div><dt>Decision score</dt><dd>${d.custom_score.toFixed(1)} / 5</dd></div>
            <div><dt>USD/m2</dt><dd>$${Number(d.usd_per_m2 || 0).toLocaleString()}</dd></div>
            <div><dt>Net yield</dt><dd>${escapeHtml(d.net_yield_estimate || "n/a")}</dd></div>
            <div><dt>Ownership</dt><dd>${destinationMetric(d, "ownership_clarity").toFixed(1)} / 5</dd></div>
          </dl>
          <h3>Investment thesis</h3>
          <p>${escapeHtml(d.profit_driver || d.panel_summary || "")}</p>
          <h3>Risk check</h3>
          <p>${escapeHtml(d.red_flags || "Verify title, tax, permit, and local market liquidity before committing capital.")}</p>
          <h3>Next diligence questions</h3>
          <ul>
            <li>Which ownership structure is available to this buyer profile, and what local counsel should verify first?</li>
            <li>What rental, tax, insurance, financing, and building-permit assumptions could change the underwriting?</li>
            <li>How deep is the resale pool outside peak season, and who is the likely future buyer?</li>
          </ul>
          <h3>10-dimension rating</h3>
          <table>
            <tbody>${d.decision_dimensions.map((item) => `<tr><th>${escapeHtml(item.label)}</th><td>${Number(item.score).toFixed(1)}</td><td>${escapeHtml(item.evidence)}</td></tr>`).join("")}</tbody>
          </table>
        </section>
      `).join("");
      return `<!doctype html>
        <html><head><meta charset="utf-8"><title>Atlas Comparison Preview</title>
        <style>
          body{font-family:Inter,Arial,sans-serif;margin:40px;color:#24312d;background:#fffdf7;line-height:1.5}
          h1{font-family:Georgia,serif;font-size:42px;line-height:1;margin:0 0 8px} h2{margin-top:32px;border-top:1px solid #ddd4c7;padding-top:24px}
          h2 span{color:#66736c;font-size:16px;font-weight:500} h3{margin-bottom:6px;font-size:13px;text-transform:uppercase;letter-spacing:.06em}
          dl{display:grid;grid-template-columns:repeat(4,1fr);gap:10px} dl div{border:1px solid #ddd4c7;padding:10px;border-radius:6px}
          dt{color:#66736c;font-size:11px;text-transform:uppercase;font-weight:800} dd{margin:4px 0 0;font-weight:800}
          .next{margin:22px 0;padding:16px;border:1px solid #ddd4c7;border-radius:8px;background:#f5f1e9}
          .upgrade{margin:22px 0;padding:16px;border:1px solid #c7d3c2;border-radius:8px;background:#eef3f0}
          .next p{margin:6px 0 0}
          table{width:100%;border-collapse:collapse;margin-top:8px} th,td{text-align:left;border-top:1px solid #ddd4c7;padding:8px;vertical-align:top;font-size:13px}
          @media(max-width:720px){body{margin:20px}dl{grid-template-columns:1fr}}
        </style></head><body>
        <h1>Atlas Comparison Preview</h1>
        <p>Generated ${generated}. This free preview uses the current 10-dimension weighting model from Global Home Atlas.</p>
        <div class="next">
          <h2>How to use this memo</h2>
          <p>Use this as a pre-adviser briefing. It should help you decide which jurisdictions deserve legal, tax, immigration, financing, insurance, and property-management review before you become anchored to a listing.</p>
          <p>For a buyer-specific paid memo, open https://globalhomeatlas.com/shortlist-review/ and include the destinations in this preview.</p>
        </div>
        <div class="upgrade">
          <h2>What the polished buyer memo adds</h2>
          <p>The paid memo adds personalized fit ranking, destinations to avoid, ownership-path notes for your citizenship/residency context, transaction-risk priorities, and next questions for local legal, tax, immigration, financing, and property-management specialists.</p>
        </div>
        ${rows}
        </body></html>`;
    }

    document.getElementById("exportMemo").addEventListener("click", () => {
      if (window.GHA) {
        window.GHA.track("memo_export", { selected_count: previewDestinations().length });
        window.GHA.track("memo_preview_export", { selected_count: previewDestinations().length });
      }
      downloadFile("atlas-comparison-preview.html", "text/html", buildPreviewHtml());
    });

    updateSortIndicators();
    recalculateScores();
  </script>
  __ANALYTICS_EVENT_SCRIPT__
</body>
</html>
"""
    replacements = {
        "__DEST_COUNT__": str(len(destinations)),
        "__COUNTRY_COUNT__": str(countries),
        "__LISTING_COUNT__": str(len(listings)),
        "__FX_AS_OF__": escape(fx.get("as_of", "n/a")),
        "__TOP_SCORE__": f"{destinations[0]['decision_score']:.1f}",
        "__AVG_SCORE__": f"{avg_score:.1f}",
        "__LOW_PRICE__": money(min_price),
        "__GENERATED__": date.today().isoformat(),
        "__CATEGORY_OPTIONS__": category_options,
        "__WEIGHT_CONTROLS__": build_weight_controls(destinations),
        "__SPOTLIGHT__": build_spotlight(destinations),
        "__CARDS__": cards,
        "__SEO_GUIDES__": build_home_guide_section(SEO_PAGES),
        "__DESTINATION_GUIDES__": build_home_destination_section(destinations),
        "__TRUST_GUIDES__": build_home_trust_section(),
        "__APP_DATA__": app_data,
        "__HOME_SCHEMA__": json_ld(global_schema_entities()),
        "__FAVICON_LINKS__": favicon_links_html().strip(),
        "__ANALYTICS_HEAD__": analytics_head_tags(),
        "__ANALYTICS_EVENT_SCRIPT__": analytics_event_script(),
        "__PRIMARY_NAV__": topbar_nav_html().strip(),
    }
    for key, value in replacements.items():
        html = html.replace(key, value)

    ARTIFACTS.mkdir(exist_ok=True)
    out = ARTIFACTS / "unified_destination_dashboard.html"
    index = ARTIFACTS / "index.html"
    dashboard_dir = ARTIFACTS / "dashboard"
    cname = ARTIFACTS / "CNAME"
    robots = ARTIFACTS / "robots.txt"
    sitemap = ARTIFACTS / "sitemap.xml"
    indexnow_key_file = ARTIFACTS / f"{INDEXNOW_KEY}.txt"
    dashboard_html = clean_generated_html(html)
    landing_html = clean_generated_html(
        build_landing_page(
            destinations,
            guide_pages,
            listings,
            countries,
            content_overrides=content_overrides,
        )
    )
    out.write_text(dashboard_html, encoding="utf-8")
    index.write_text(landing_html, encoding="utf-8")
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    (dashboard_dir / "index.html").write_text(dashboard_html, encoding="utf-8")
    copy_site_assets()
    fit_finder_dir = ARTIFACTS / FIND_YOUR_FIT_SLUG
    fit_finder_dir.mkdir(parents=True, exist_ok=True)
    (fit_finder_dir / "index.html").write_text(
        clean_generated_html(build_find_your_fit_page(destinations)),
        encoding="utf-8",
    )
    guide_hub_dir = ARTIFACTS / GUIDE_HUB_SLUG
    guide_hub_dir.mkdir(parents=True, exist_ok=True)
    (guide_hub_dir / "index.html").write_text(
        clean_generated_html(build_guide_hub_page(guide_pages, destinations)),
        encoding="utf-8",
    )
    retirement_calculator_dir = ARTIFACTS / RETIREMENT_CALCULATOR_SLUG
    retirement_calculator_dir.mkdir(parents=True, exist_ok=True)
    (retirement_calculator_dir / "index.html").write_text(
        clean_generated_html(build_retirement_calculator_page(destinations, retirement_costs)),
        encoding="utf-8",
    )
    retirement_finder_dir = ARTIFACTS / RETIREMENT_FINDER_SLUG
    retirement_finder_dir.mkdir(parents=True, exist_ok=True)
    (retirement_finder_dir / "index.html").write_text(
        clean_generated_html(
            build_retirement_destination_finder_page(destinations, retirement_costs, mortgage_profiles)
        ),
        encoding="utf-8",
    )
    retirement_article_dir = ARTIFACTS / RETIREMENT_DESTINATIONS_SLUG
    retirement_article_dir.mkdir(parents=True, exist_ok=True)
    (retirement_article_dir / "index.html").write_text(
        clean_generated_html(build_retirement_destinations_article(destinations, retirement_costs)),
        encoding="utf-8",
    )
    country_comparison_dir = ARTIFACTS / "country-comparison"
    country_comparison_dir.mkdir(parents=True, exist_ok=True)
    (country_comparison_dir / "index.html").write_text(
        clean_generated_html(build_country_comparison_page(destinations, SEO_PAGES)),
        encoding="utf-8",
    )
    shortlist_review_dir = ARTIFACTS / SHORTLIST_REVIEW_SLUG
    shortlist_review_dir.mkdir(parents=True, exist_ok=True)
    (shortlist_review_dir / "index.html").write_text(
        clean_generated_html(build_shortlist_review_page(destinations, SEO_PAGES)),
        encoding="utf-8",
    )
    report_library_dir = ARTIFACTS / REPORT_LIBRARY_SLUG
    report_library_dir.mkdir(parents=True, exist_ok=True)
    (report_library_dir / "index.html").write_text(
        clean_generated_html(build_report_library_page(destinations, SEO_PAGES)),
        encoding="utf-8",
    )
    for page in SEO_PAGES:
        page_dir = ARTIFACTS / page["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            clean_generated_html(
                build_seo_page(
                    page,
                    destinations,
                    SEO_PAGES,
                    auto_links=auto_internal_links,
                    content_overrides=content_overrides,
                )
            ),
            encoding="utf-8",
        )
    destinations_dir = ARTIFACTS / "destinations"
    destinations_dir.mkdir(exist_ok=True)
    for dest in destinations:
        page_dir = destinations_dir / destination_slug(dest)
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            clean_generated_html(
                build_destination_page(
                    dest,
                    listings_by_dest.get(dest["id"], []),
                    destinations,
                    SEO_PAGES,
                    content_overrides=content_overrides,
                )
            ),
            encoding="utf-8",
        )
    countries_dir = ARTIFACTS / "countries"
    countries_dir.mkdir(exist_ok=True)
    for hub in COUNTRY_HUBS:
        page_dir = countries_dir / hub["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            clean_generated_html(
                build_country_hub_page(
                    hub,
                    destinations,
                    SEO_PAGES,
                    content_overrides=content_overrides,
                )
            ),
            encoding="utf-8",
        )
    for page in TRUST_PAGES:
        page_dir = ARTIFACTS / page["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            clean_generated_html(build_trust_page(page, destinations, SEO_PAGES)),
            encoding="utf-8",
        )
    brand_mockups_dir = ARTIFACTS / "brand-mockups"
    brand_mockups_dir.mkdir(parents=True, exist_ok=True)
    (brand_mockups_dir / "index.html").write_text(
        clean_generated_html(build_brand_mockups_page()),
        encoding="utf-8",
    )
    cname.write_text(f"{SITE_DOMAIN}\n", encoding="utf-8")
    robots.write_text(
        f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}sitemap.xml
""",
        encoding="utf-8",
    )
    indexnow_key_file.write_text(f"{INDEXNOW_KEY}\n", encoding="utf-8")
    sitemap_urls = [
        (SITE_URL, "1.0"),
        (page_url(FIND_YOUR_FIT_SLUG), "0.94"),
        (page_url("dashboard"), "0.92"),
        (page_url(SHORTLIST_REVIEW_SLUG), "0.90"),
        (page_url(REPORT_LIBRARY_SLUG), "0.88"),
        (page_url("country-comparison"), "0.88"),
        (page_url(GUIDE_HUB_SLUG), "0.90"),
        (page_url(RETIREMENT_CALCULATOR_SLUG), "0.92"),
        (page_url(RETIREMENT_FINDER_SLUG), "0.92"),
        (page_url(RETIREMENT_DESTINATIONS_SLUG), "0.90"),
        *[(page_url(page["slug"]), "0.85") for page in SEO_PAGES],
        *[(country_url(hub), "0.82") for hub in COUNTRY_HUBS],
        *[(destination_url(dest), "0.80") for dest in destinations],
        *[(page_url(page["slug"]), "0.70") for page in TRUST_PAGES],
        (page_url("brand-mockups"), "0.40"),
    ]
    sitemap_entries = "\n".join(
        f"""  <url>
    <loc>{escape(loc)}</loc>
    <lastmod>{date.today().isoformat()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{priority}</priority>
  </url>"""
        for loc, priority in sitemap_urls
    )
    sitemap.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</urlset>
""",
        encoding="utf-8",
    )
    return out


if __name__ == "__main__":
    print(build())
