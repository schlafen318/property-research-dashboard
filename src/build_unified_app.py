from __future__ import annotations

import json
import os
import re
import shutil
import unicodedata
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"
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
COUNTRY_HUBS = [
    {
        "slug": "spain-property",
        "country": "Spain",
        "title": "Spain Property Guide for Foreign Buyers | Global Home Atlas",
        "description": "Compare Spain property destinations for foreign buyers, including Valencia, Malaga, Costa Brava, and Mallorca across lifestyle, ownership, rentals, and retirement fit.",
        "h1": "Spain Property Guide for Foreign Buyers",
        "thesis": "Spain is one of the deepest lifestyle-property markets in the Atlas because it combines city infrastructure, Mediterranean living, healthcare access, and several resale buyer pools. The discipline is entry price and local rental regulation.",
        "destination_ids": ["valencia", "m-laga-costa-del-sol", "costa-brava-girona", "mallorca"],
        "guide_slugs": ["portugal-vs-spain-retirement-property", "best-places-to-buy-property-in-europe", "buying-property-abroad-for-retirement", "best-places-to-buy-a-second-home-abroad"],
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
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "madeira", "crete", "lake-como", "hakone-izu", "m-laga-costa-del-sol"],
        "faqs": [
            ("What matters most when buying abroad for retirement?", "Ownership clarity, healthcare access, daily convenience, tax and visa planning, and resale liquidity should be weighted before lifestyle appeal."),
            ("Should retirement buyers prioritize rental yield?", "Yield helps offset ownership costs, but retirement buyers should avoid assets where income depends on fragile short-term-rental rules."),
            ("Is a lower purchase price always safer?", "No. A cheap property can be expensive if title, maintenance, healthcare access, or resale demand are weak."),
        ],
    },
    {
        "slug": "best-places-to-buy-vacation-home-abroad",
        "title": "Best Places to Buy a Vacation Home Abroad | Global Home Atlas",
        "description": "Rank global vacation-home destinations by lifestyle pull, rental durability, foreign ownership, value discipline, and long-term exit liquidity.",
        "h1": "Best Places to Buy a Vacation Home Abroad",
        "keyword": "best places to buy a vacation home abroad",
        "theme": "vacation-home acquisition",
        "intent": "buyers who want personal use, repeatable travel demand, and a realistic path to offset carrying costs",
        "destination_ids": ["fukuoka-itoshima", "algarve-cascais", "madeira", "costa-brava-girona", "lake-como", "crete", "phuket-koh-samui", "mallorca"],
        "faqs": [
            ("What makes a strong overseas vacation-home market?", "Look for repeat visitation, airport access, year-round demand, clear local rental rules, and a resale market beyond foreign buyers."),
            ("Are island homes better investments?", "Not automatically. Islands can have scarcity and appeal, but also seasonality, maintenance friction, and regulatory limits."),
            ("How should I use rental estimates?", "Treat rental estimates as underwriting context, then verify permits, net operating costs, occupancy, and local manager quality."),
        ],
    },
    {
        "slug": "best-countries-for-expats-to-buy-property",
        "title": "Best Countries for Expats to Buy Property | Global Home Atlas",
        "description": "A global expat property buying guide comparing ownership rules, foreign-buyer practicality, lifestyle quality, value, and resale depth.",
        "h1": "Best Countries for Expats to Buy Property",
        "keyword": "best countries for expats to buy property",
        "theme": "expat ownership",
        "intent": "globally mobile buyers who need clear foreign ownership, usable infrastructure, and a livable long-term base",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "m-laga-costa-del-sol", "madeira", "crete", "da-nang-hoi-an", "phuket-koh-samui"],
        "faqs": [
            ("Which countries are easiest for expats to buy in?", "Ease depends on title structure, local counsel quality, banking, taxes, and residency rules, not only whether foreign ownership is technically allowed."),
            ("Should expats buy before moving?", "Usually only after validating healthcare, transport, language friction, taxes, and the specific neighborhood through extended stays."),
            ("How should foreign buyers manage legal risk?", "Use independent local counsel, verify title and permits, model taxes, and avoid structures you cannot explain clearly."),
        ],
    },
    {
        "slug": "best-countries-to-buy-property-as-a-foreigner",
        "title": "Best Countries to Buy Property as a Foreigner | Global Home Atlas",
        "description": "Compare countries and destinations for foreign property buyers using ownership clarity, title practicality, lifestyle quality, value discipline, and resale depth.",
        "h1": "Best Countries to Buy Property as a Foreigner",
        "keyword": "best countries to buy property as a foreigner",
        "theme": "foreign-buyer access",
        "intent": "foreign buyers comparing legal access, title clarity, transaction practicality, lifestyle quality, and resale depth before choosing markets for local diligence",
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "m-laga-costa-del-sol", "madeira", "crete", "lake-como", "costa-brava-girona", "hakone-izu", "phuket-koh-samui"],
        "faqs": [
            ("Which countries are best for foreigners to buy property?", "The best options are markets where foreign buyers can understand the title path, hire independent local counsel, fund the purchase cleanly, use the property realistically, and resell into a broad buyer pool."),
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
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "m-laga-costa-del-sol", "lake-como", "madeira", "costa-brava-girona", "crete"],
        "faqs": [
            ("What is the first step to buy property abroad?", "Define the job of the property: retirement base, vacation home, income asset, capital preservation, or a blend."),
            ("How many markets should I compare?", "Start with five to eight markets, then reduce to two or three after legal, tax, visa, and neighborhood checks."),
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
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "madeira", "crete", "hakone-izu", "lake-como", "m-laga-costa-del-sol"],
        "faqs": [
            ("What should retirees verify before buying abroad?", "Retirement buyers should verify healthcare access, visa and tax planning needs, daily convenience, title clarity, insurance, building condition, and future resale demand before focusing on lifestyle appeal."),
            ("Should retirement buyers prioritize rental income?", "Rental income can offset carrying costs, but a retirement property should not depend on fragile short-term-rental assumptions or a structure the buyer cannot comfortably manage."),
            ("How long should I test a market before buying?", "A serious buyer should spend enough time locally to experience daily errands, healthcare access, transport, weather, language friction, and non-peak-season livability before committing capital."),
        ],
    },
    {
        "slug": "best-places-to-buy-a-second-home-abroad",
        "title": "Best Places to Buy a Second Home Abroad | Global Home Atlas",
        "description": "Compare second-home destinations abroad by access, personal-use appeal, rental offset potential, ownership clarity, value discipline, and exit liquidity.",
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
        "destination_ids": ["fukuoka-itoshima", "algarve-cascais", "m-laga-costa-del-sol", "da-nang-hoi-an", "phuket-koh-samui", "bali", "croatia-istria-dalmatia", "costa-brava-girona"],
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
        "destination_ids": ["phuket-koh-samui", "bali", "da-nang-hoi-an", "croatia-istria-dalmatia", "m-laga-costa-del-sol", "algarve-cascais", "lake-como", "andermatt"],
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
        "destination_ids": ["algarve-cascais", "madeira", "valencia", "m-laga-costa-del-sol", "costa-brava-girona", "mallorca"],
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
        "description": "Assess Japan retirement property for foreign buyers, including ownership clarity, lifestyle quality, value, income limits, and resale considerations.",
        "h1": "Japan Retirement Property for Foreign Buyers",
        "keyword": "Japan retirement property foreign buyers",
        "theme": "Japan buyer guide",
        "intent": "foreign buyers considering Japan for lifestyle, retirement optionality, and clean ownership rather than pure yield",
        "destination_ids": ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko", "valencia", "algarve-cascais"],
        "faqs": [
            ("Can foreigners buy property in Japan?", "Foreign buyers can generally buy freehold property in Japan, but financing, taxes, management, and local rules still require careful advice."),
            ("Is Japan good for retirement property?", "Japan can be strong for safety, healthcare, food, transport, and ownership clarity, but visa status and income expectations need separate planning."),
            ("Where should foreign buyers compare in Japan?", "Compare city-adjacent lifestyle markets such as Fukuoka and Itoshima with resort markets such as Hakone, Hakuba, and Niseko."),
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
        "title": "Best Places to Buy Property in Europe | Global Home Atlas",
        "description": "Compare the best places to buy property in Europe for lifestyle, retirement, rental resilience, value discipline, and long-term resale liquidity.",
        "h1": "Best Places to Buy Property in Europe",
        "keyword": "best places to buy property in Europe",
        "theme": "Europe shortlist",
        "intent": "buyers comparing European lifestyle markets with a global investor's discipline",
        "destination_ids": ["valencia", "algarve-cascais", "madeira", "lake-como", "costa-brava-girona", "crete", "annecy", "dolomites-south-tyrol", "mallorca", "croatia-istria-dalmatia"],
        "faqs": [
            ("Where should foreign buyers start in Europe?", "Start with regions that combine livability, transport, healthcare, clear ownership, and a resale market broader than one nationality."),
            ("Is Europe better for lifestyle or yield?", "Europe is often strongest as a lifestyle and capital-preservation decision, while yield depends heavily on local rules and asset selection."),
            ("How should I compare European property markets?", "Compare city access, healthcare, taxation, rental rules, seasonality, entry price, and resale depth at the regional level."),
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
        "destination_ids": ["fukuoka-itoshima", "valencia", "algarve-cascais", "m-laga-costa-del-sol", "madeira", "crete", "lake-como", "hakone-izu", "phuket-koh-samui", "da-nang-hoi-an"],
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
    values = [float(part) for part in re.findall(r"\d+(?:\.\d+)?", value)]
    return max(values) if values else 0


def score(dest: dict, key: str) -> float:
    return float(dest.get("scores", {}).get(key, {}).get("score", 0) or 0)


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


def copy_site_assets() -> None:
    if not SOURCE_ASSETS.exists():
        return
    if PUBLIC_ASSETS.exists():
        shutil.rmtree(PUBLIC_ASSETS)
    PUBLIC_ASSETS.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_ASSETS.iterdir():
        if source.is_file():
            shutil.copy2(source, PUBLIC_ASSETS / source.name)


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


def build_destination_card(dest: dict, listings: list[dict], top_retirement_ids: set[str]) -> str:
    dest_listings = "\n".join(build_listing_card(item) for item in listings)
    pros = "".join(f"<li>{escape(item)}</li>" for item in dest.get("pros", []))
    cons = "".join(f"<li>{escape(item)}</li>" for item in dest.get("cons", []))
    ownership_score = score(dest, "ownership_clarity")
    retirement_score = score(dest, "retirement_suitability")
    yield_score = percentish(dest.get("net_yield_estimate"))
    price_confidence = dest.get("price_confidence") or "Confidence n/a"
    rental_confidence = dest.get("rental", {}).get("confidence") or "Research estimate"
    open_attr = "open" if dest["rank"] <= 2 else ""
    return f"""
      <details
        class="destination-card"
        data-id="{escape(dest["id"])}"
        data-name="{escape(dest["name"].lower())}"
        data-country="{escape((dest.get("country") or "").lower())}"
        data-category="{escape(dest.get("category") or "")}"
        data-score="{dest.get("decision_score", dest.get("overall_score", 0))}"
        data-price="{dest.get("usd_per_m2", 0)}"
        data-yield="{yield_score}"
        data-ownership="{ownership_score}"
        data-retirement="{retirement_score}"
        data-shortlist="{"yes" if dest["rank"] <= 8 else "no"}"
        data-top-retirement="{"yes" if dest["id"] in top_retirement_ids else "no"}"
        {open_attr}
      >
        <summary>
          <div class="rank-mark"><span>#{dest["rank"]}</span></div>
          <div class="summary-copy">
            <p>{escape(dest.get("category") or "Destination")} · {escape(dest.get("country") or "")}</p>
            <h3>{escape(dest["name"])}</h3>
            <span>{escape(dest.get("panel_verdict") or "")}</span>
          </div>
          <div class="score-dial" aria-label="Decision score {dest.get("decision_score", dest.get("overall_score", 0)):.2f} out of 5">
            <strong data-custom-score>{dest.get("decision_score", dest.get("overall_score", 0)):.2f}</strong>
            <small>/ 5</small>
          </div>
          <label class="summary-compare">
            <input type="checkbox" class="compare-toggle" value="{escape(dest["id"])}">
            Compare
          </label>
        </summary>

        <div class="decision-row">
          <button type="button" class="memo-add" data-memo-id="{escape(dest["id"])}">Add to memo shortlist</button>
        </div>

        <section class="metric-strip" aria-label="Key metrics">
          <div>
            <span>Entry benchmark</span>
            <strong>{money(dest.get("usd_per_m2"))}/m2</strong>
            <em data-tone="{confidence_tone(price_confidence)}">{escape(price_confidence)}</em>
          </div>
          <div>
            <span>Net yield</span>
            <strong>{escape(dest.get("net_yield_estimate") or "n/a")}</strong>
            <em data-tone="{confidence_tone(rental_confidence)}">{escape(rental_confidence)}</em>
          </div>
          <div>
            <span>Ownership clarity</span>
            <strong>{ownership_score:.1f}/5</strong>
            <em>Foreign-buyer pathway</em>
          </div>
          <div>
            <span>Retirement fit</span>
            <strong>{retirement_score:.1f}/5</strong>
            <em>Long-term lifestyle</em>
          </div>
        </section>

        <section class="brief-grid">
          <article>
            <h4>Committee Read</h4>
            <p>{escape(dest.get("panel_summary") or "")}</p>
          </article>
          <article>
            <h4>Investment Edge</h4>
            <p>{escape(dest.get("profit_driver") or "")}</p>
          </article>
          <article>
            <h4>Governance Check</h4>
            <p>{escape(dest.get("ownership_notes") or "")}</p>
            <p class="risk-note">{escape(dest.get("red_flags") or "")}</p>
          </article>
        </section>

        <section class="pros-cons">
          <article><h4>Why It Works</h4><ul>{pros}</ul></article>
          <article><h4>What Can Break</h4><ul>{cons}</ul></article>
        </section>

        <section class="score-board">
          <div class="section-heading">
            <h4>10-Dimension Rating</h4>
            <p>Consolidated from the original granular scorecard into the ten dimensions that drive the buy/no-buy decision.</p>
          </div>
          <ul>{build_score_rows(dest)}</ul>
        </section>

        <section class="evidence-board">
          <div class="section-heading">
            <h4>Metric Evidence</h4>
            <p>Assumption trail for the numbers most likely to drive the buy/no-buy decision.</p>
          </div>
          <div class="evidence-grid">{build_evidence_rows(dest)}</div>
        </section>

        <section class="listings-wrap">
          <div class="section-heading">
            <h4>Representative Live-Market References</h4>
            <p>Three listing samples to anchor price, size, property type, and market texture.</p>
          </div>
          <div class="listings">{dest_listings}</div>
        </section>
      </details>
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
                <div><dt>Decision</dt><dd>{dest.get("decision_score", dest.get("overall_score", 0)):.2f}</dd></div>
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
        else if (href.startsWith("/") && !href.startsWith("/#")) track("internal_page_click", {{ href }});
        else if (href === "/#destinations" || href === "#destinations") track("dashboard_open", {{ href }});
        else if (href.startsWith("http") && !href.includes(location.hostname)) track("outbound_click", {{ href }});
        else if (href.startsWith("mailto:")) track("contact_click", {{ href }});
      }});
      document.addEventListener("submit", function (event) {{
        const form = event.target.closest("#custom-shortlist-form");
        if (!form) return;
        event.preventDefault();
        const data = new FormData(form);
        const lines = [
          "Global Home Atlas custom shortlist request",
          "",
          "Name: " + (data.get("name") || ""),
          "Email: " + (data.get("email") || ""),
          "Budget: " + (data.get("budget") || ""),
          "Target regions: " + (data.get("regions") || ""),
          "Primary goal: " + (data.get("goal") || ""),
          "Holding period: " + (data.get("holding_period") || ""),
          "Notes: " + (data.get("notes") || "")
        ];
        track("custom_shortlist_submit", {{
          budget: data.get("budget") || "",
          regions: data.get("regions") || "",
          goal: data.get("goal") || ""
        }});
        location.href = "mailto:{escape(CONTACT_EMAIL)}?subject=" + encodeURIComponent("Custom Global Property Shortlist") + "&body=" + encodeURIComponent(lines.join("\\n"));
      }});
    }})();
  </script>
"""


def head_html(title: str, description: str, canonical: str, schema: list[dict]) -> str:
    return f"""
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='32' fill='%2310241f'/%3E%3Cpath d='M17 37 32 18l15 19v11H36V36h-8v12H17Z' fill='%23fffdf8'/%3E%3C/svg%3E">
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


def related_guide_pages(page: dict, pages: list[dict], limit: int = 4) -> list[dict]:
    current_destinations = set(page.get("destination_ids", []))
    scored = []
    for candidate in pages:
        if candidate["slug"] == page["slug"]:
            continue
        overlap = len(current_destinations.intersection(candidate.get("destination_ids", [])))
        theme_match = int(candidate.get("theme") == page.get("theme"))
        keyword_match = len(set(page.get("keyword", "").lower().split()).intersection(candidate.get("keyword", "").lower().split()))
        scored.append((overlap, theme_match, keyword_match, candidate))
    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return [candidate for *_, candidate in scored[:limit]]


def contextual_related_guides(page: dict, pages: list[dict]) -> str:
    cards = []
    for candidate in related_guide_pages(page, pages):
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


def primary_nav_html(css_prefix: str = "page", include_seo_status: bool = False) -> str:
    seo_status = '<a href="/seo-status/">SEO Status</a>' if include_seo_status else ""
    return f"""
      <nav class="{css_prefix}-nav" aria-label="Primary">
        <a class="{css_prefix}-brand" href="/">Global Home Atlas</a>
        <div class="{css_prefix}-nav-links">
          <a href="/#compare">Compare</a>
          <a href="/guides/">Guides</a>
          <a href="/#destination-index">Destinations</a>
          <a href="/countries/spain-property/">Countries</a>
          <a href="/methodology/">Methodology</a>
          <a href="/contact/">Contact</a>
          {seo_status}
        </div>
        <details class="mobile-menu">
          <summary>Menu</summary>
          <nav aria-label="Mobile primary">
            <a href="/#compare">Compare</a>
            <a href="/countries/spain-property/">Countries</a>
            <a href="/#destination-index">Destinations</a>
            <a href="/guides/">Guides</a>
            <a href="/methodology/">Methodology</a>
            <a href="/contact/">Contact</a>
          </nav>
        </details>
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
          <p>Markets are compared across lifestyle, access, ownership clarity, regulatory safety, yield realism, capital upside, retirement fit, liquidity, foreigner fit, and value entry.</p>
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
          if (query.matches) item.open = index === 0;
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
              <td>{dest.get("decision_score", 0):.2f}</td>
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
                <div><dt>Decision score</dt><dd>{dest.get("decision_score", 0):.2f}/5</dd></div>
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


def build_guide_hub_page(pages: list[dict], destinations: list[dict]) -> str:
    canonical = page_url(GUIDE_HUB_SLUG)
    updated = date.today().isoformat()
    clusters = [
        (
            "Getting Started",
            "Core frameworks for buyers shaping the job of the property before choosing countries, agents, or individual homes.",
            [
                "buy-property-abroad",
                "best-countries-to-buy-property-as-a-foreigner",
                "where-can-foreigners-buy-property",
            ],
        ),
        (
            "Retirement",
            "Pages for buyers testing long-stay livability, healthcare practicality, family use, and future retirement optionality.",
            [
                "best-places-to-buy-property-abroad-for-retirement",
                "buying-property-abroad-for-retirement",
                "japan-retirement-property-foreign-buyers",
            ],
        ),
        (
            "Second Homes",
            "Shortlist paths for seasonal use, family travel, repeat access, vacation rental offset, and future resale flexibility.",
            [
                "best-places-to-buy-a-second-home-abroad",
                "best-places-to-buy-vacation-home-abroad",
                "best-places-to-buy-property-in-europe",
            ],
        ),
        (
            "Risk",
            "Risk-first research for buyers who want to understand what can break before they commit time or capital.",
            [
                "foreign-property-investment-risks",
                "thailand-villa-ownership-foreigners",
                "overseas-property-investment",
            ],
        ),
        (
            "Country Selection",
            "Country and region comparisons for buyers narrowing jurisdictions before local legal and tax work.",
            [
                "portugal-vs-spain-retirement-property",
                "greece-vs-portugal-retirement-property",
                "best-countries-for-expats-to-buy-property",
            ],
        ),
        (
            "Investment",
            "Investment-oriented screens for buyers comparing yield realism, exit liquidity, value entry, and governance risk.",
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
            <div class="page-grid">{guide_cards_for_slugs(slugs, pages, destinations)}</div>
          </section>
        """
        for title, description, slugs in clusters
    )
    top_destinations = destinations[:6]
    top_destination_links = destination_links(top_destinations, limit=6)
    country_links = country_hub_links(limit=7)

    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(GUIDE_HUB_TITLE, GUIDE_HUB_DESCRIPTION, canonical, schema_for_guide_hub(canonical, pages))}
  <style>
{shared_content_css()}
    .page-card span {{ display: block; color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }}
    .page-card p strong {{ color: var(--ink); }}
    .page-card p:last-child {{ display: grid; gap: 6px; }}
    .page-card p:last-child a {{ margin-right: 8px; font-size: 13px; font-weight: 800; }}
  </style>
</head>
<body>
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html(include_seo_status=True)}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">Buyer guide hub · updated {updated}</p>
          <h1>Global Property Buying Guides</h1>
          <p class="page-lede">{GUIDE_HUB_DESCRIPTION} Use this hub to move from broad intent to a shortlist that can survive legal review, long-term lifestyle use, and resale scrutiny.</p>
        </div>
        <aside class="page-hero-card">
          <span>Guide pages</span><strong>{len(pages)}</strong>
          <span>Destinations linked</span><strong>{len(destinations)}</strong>
          <span>Decision model</span><strong>{len(DIMENSIONS)} dimensions</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <section class="page-stats" aria-label="Guide hub metrics">
        <div><span>Primary job</span><strong>Choose a market</strong></div>
        <div><span>Buyer type</span><strong>Global citizen</strong></div>
        <div><span>Risk lens</span><strong>Ownership first</strong></div>
        <div><span>Updated</span><strong>{updated}</strong></div>
      </section>
      {sticky_page_nav([("Start", "getting-started"), ("Retirement", "retirement"), ("Second homes", "second-homes"), ("Risk", "risk"), ("Countries", "country-selection"), ("Investment", "investment")])}
      {trust_brief_html()}
      <div class="page-layout">
        <article class="page-article">
          <section class="page-section">
            <h2>How to Use These Guides</h2>
            <p>Start with the page that matches the job of the property, then compare the linked destination dossiers before talking to local agents. The goal is to avoid falling in love with a listing before the market, ownership path, rental rules, healthcare practicality, and resale depth have been tested.</p>
            <p>Every guide connects back to the same 10-dimension model: lifestyle magnetism, global access, ownership clarity, regulatory safety, rental profit, capital upside, retirement fit, exit liquidity, foreigner fit, and value entry. That keeps broad searches comparable instead of turning each market into a separate story.</p>
          </section>
          <section class="page-section">
            <h2>Country and Region Hubs</h2>
            <p>Use these geographic hubs to move from broad buyer intent into local destination choices, ownership questions, and country-level tradeoffs.</p>
            <nav class="page-grid">{country_links}</nav>
          </section>
          {cluster_html}
        </article>
        <aside class="page-aside">
          <section class="page-aside-card">
            <h2>Use the Atlas</h2>
            <p>Open the dashboard to compare all destination scores and export a shortlist memo.</p>
            <a class="page-button" href="/#destinations" data-track="dashboard_open" data-track-label="guide hub">Open dashboard</a>
            <a class="page-button" href="/contact/#custom-shortlist" data-track="custom_shortlist_cta" data-track-label="guide hub">Request custom shortlist</a>
          </section>
          <section class="page-aside-card">
            <h3>Best Starting Destinations</h3>
            <nav>{top_destination_links}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Trust Layer</h3>
            <nav><a href="/seo-status/">SEO status dashboard</a>{trust_page_links()}</nav>
          </section>
        </aside>
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
                <li>Decision score: {dest.get("decision_score", 0):.2f}/5</li>
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
                <div><dt>Score</dt><dd>{dest.get("decision_score", 0):.2f}/5</dd></div>
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
              <td>{dest.get("decision_score", 0):.2f}/5</td>
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
          <em>{dest.get("decision_score", 0):.2f}/5</em>
        </div>
        """.rstrip()
        for dest in destinations
    )
    return f"""
      <div class="cluster-map" aria-label="Destination cluster visual">
        <div class="cluster-map__grid">{chips}</div>
      </div>
    """


def country_guide_links(hub: dict, pages: list[dict]) -> str:
    by_slug = {page["slug"]: page for page in pages}
    links = []
    for slug in hub.get("guide_slugs", []):
        page = by_slug.get(slug)
        if page:
            links.append(f'<a href="/{escape(page["slug"])}/">{escape(page["h1"])}</a>')
    return "\n".join(links)


def build_country_hub_page(hub: dict, destinations: list[dict], pages: list[dict]) -> str:
    selected = destinations_for_ids(hub["destination_ids"], destinations)
    canonical = country_url(hub)
    updated = date.today().isoformat()
    avg_score = sum(float(dest.get("decision_score", 0) or 0) for dest in selected) / max(1, len(selected))
    best = selected[0] if selected else destinations[0]
    guide_links = country_guide_links(hub, pages)
    peer_country_links = country_hub_links(hub["slug"], limit=6)

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
          <p class="page-lede">{escape(hub["description"])}</p>
        </div>
        <aside class="page-hero-card">
          <span>Markets compared</span><strong>{len(selected)}</strong>
          <span>Average score</span><strong>{avg_score:.2f}/5</strong>
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
      {sticky_page_nav([("Thesis", "country-thesis"), ("Buyer Fit", "buyer-fit"), ("Compare", "destination-comparison"), ("Risk", "risk-posture"), ("Guides", "related-guides")])}
      {mobile_action_strip("#destination-comparison", "Compare", "/contact/#custom-shortlist", "Brief")}
      <section class="brief-panel" aria-label="Country briefing">
        <article><span>Top destination match</span><strong>{escape(best["name"])}</strong><p>{escape(best.get("panel_verdict") or "")}</p></article>
        <article><span>Buyer profile</span><strong>Affluent global planners</strong><p>Best for buyers comparing lifestyle use, legal clarity, tax and ownership friction, rental realism, and future liquidity before local deal work.</p></article>
        <article><span>Risk posture</span><strong>{metric_value(best, "ownership_clarity"):.1f}/5 ownership clarity</strong><p>Use country-level rules as the first screen, then verify title, taxes, rental permissions, and local transaction mechanics by asset.</p></article>
      </section>
      {trust_brief_html()}
      <div class="page-layout">
        <article class="page-article">
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
            <p>Compare these markets against the full destination model and export a shortlist memo.</p>
            <a class="page-button" href="/#destinations" data-track="dashboard_open" data-track-label="{escape(hub["country"])} country hub">Open dashboard</a>
            <a class="page-button" href="/contact/#custom-shortlist" data-track="custom_shortlist_cta" data-track-label="{escape(hub["country"])} country hub">Request custom shortlist</a>
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


def build_seo_page(page: dict, destinations: list[dict], pages: list[dict]) -> str:
    selected = destinations_for_page(page, destinations)
    canonical = page_url(page["slug"])
    top = selected[0]
    runner_up = selected[1] if len(selected) > 1 else selected[0]
    related_links = seo_guide_links(pages, page["slug"], limit=5)
    contextual_links = contextual_related_guides(page, pages)
    title = page["title"]
    description = page["description"]
    updated = date.today().isoformat()
    country_count = len({item.get("country") for item in selected if item.get("country")})

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
    .seo-brand {{ color: var(--ink); font-weight: 900; text-decoration: none; }}
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
    }}
    @media (max-width: 560px) {{
      .seo-shell {{ width: min(100% - 28px, 1120px); }}
      .seo-nav {{ align-items: flex-start; }}
      .seo-nav-links {{ display: none; }}
      .mobile-menu {{ display: block; }}
      .seo-hero {{ padding-bottom: 48px; }}
      .seo-stats, .seo-destination-card, .seo-destination-card dl, .seo-link-grid {{ grid-template-columns: 1fr; }}
      .seo-section {{ padding: 18px; }}
    }}
  </style>
</head>
<body>
  <header class="seo-hero">
    <div class="seo-shell">
      {primary_nav_html("seo")}
      <div class="seo-hero-grid">
        <div>
          <p class="seo-eyebrow">{escape(page["theme"])} · updated {updated}</p>
          <h1>{escape(page["h1"])}</h1>
          <p class="seo-lede">{escape(description)} This guide is written for {escape(page["intent"])}.</p>
          <div class="seo-actions">
          <a class="seo-button" href="/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} hero">Open the full dashboard</a>
          <a class="seo-button secondary" href="#comparison" data-track="guide_compare_jump" data-track-label="{escape(page["h1"])}">Compare markets</a>
          </div>
        </div>
        <aside class="seo-hero-card">
          <span>Top current match</span>
          <strong>{escape(top["name"])}</strong>
          <span>Alternative to test</span>
          <strong>{escape(runner_up["name"])}</strong>
          <span>Markets compared</span>
          <strong>{len(selected)}</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="seo-shell">
      <section class="seo-panel" aria-label="Guide summary">
        <div class="seo-stats">
          <div><span>Primary keyword</span><strong>{escape(page["keyword"])}</strong></div>
          <div><span>Destinations</span><strong>{len(selected)}</strong></div>
          <div><span>Decision model</span><strong>{len(DIMENSIONS)} dimensions</strong></div>
          <div><span>Research status</span><strong>Updated {updated}</strong></div>
        </div>
      </section>
      <div class="seo-content">
        <article class="seo-article">
          <section class="seo-section">
            <h2>How to Read This Shortlist</h2>
            <p><strong>Credibility note:</strong> this page compares {len(selected)} destinations across {country_count} countries using a consistent {len(DIMENSIONS)}-dimension model. It is research-grade destination intelligence, not financial, legal, tax, immigration, or transaction advice.</p>
            <p>The right answer for {escape(page["keyword"])} is rarely the market with the prettiest photos or the highest advertised yield. A global buyer needs a place that can survive legal review, repeated use, currency shifts, maintenance surprises, and a future resale process. Global Home Atlas ranks markets through ten decision dimensions: lifestyle magnetism, global access, ownership clarity, regulatory safety, rental profit, capital upside, retirement fit, exit liquidity, foreigner fit, and value entry.</p>
            <p>That weighting is designed for affluent global citizens who may use one property for several jobs over time. A home can begin as a vacation base, become a semi-retirement address, then eventually need to rent or sell. The best markets on this page are therefore not selected only for near-term excitement. They are selected because the evidence points to a more durable combination of livability, practicality, and investment defensibility.</p>
            <p>Use this page as a first-pass filter. It narrows the research field, highlights where each market is strong, and shows which tradeoffs need professional verification. Before buying, confirm title, taxes, foreign-buyer rules, visa status, insurance, building condition, local rental permits, manager quality, and resale comparables with independent local advisers.</p>
          </section>

          <section class="seo-section" id="comparison">
            <h2>Best Markets to Compare First</h2>
            <p>For this search, the strongest candidates are {escape(top["name"])} and {escape(runner_up["name"])} because they balance high decision scores with practical ownership and lifestyle use. The table below keeps the comparison deliberately concrete: entry benchmark, yield context, ownership clarity, retirement fit, and the committee read. These are the variables most likely to change a real buy/no-buy decision.</p>
            {build_seo_destination_table(selected)}
          </section>

          <section class="seo-section">
            <h2>Market Notes for Serious Buyers</h2>
            <div class="seo-card-grid">
              {build_seo_destination_cards(selected)}
            </div>
          </section>

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

          <section class="seo-section">
            <h2>Related Buying Guides</h2>
            <p>Use these adjacent guides to test the same shortlist from a different buyer intent before committing to local diligence.</p>
            <div class="seo-link-grid">{contextual_links}</div>
          </section>

          <section class="seo-section" id="faq">
            <h2>FAQ</h2>
            {build_faq_html(page.get("faqs", []))}
          </section>
        </article>

        <aside class="seo-aside">
          <section class="seo-aside-card">
            <h2>Use the Full Atlas</h2>
            <p>Compare all 25 destinations, adjust the 10-dimension weighting model, and export a shortlist memo.</p>
            <a class="seo-button" href="/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} aside">Open dashboard</a>
            <a class="seo-button" href="/contact/#custom-shortlist" data-track="custom_shortlist_cta" data-track-label="{escape(page["h1"])}">Request custom shortlist</a>
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
    .page-hero {
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(255, 253, 247, .98) 0 42%, rgba(255, 253, 247, .74) 62%, rgba(199, 211, 194, .28)),
        url("/assets/destination-dossier-coast.jpg");
      background-size: cover;
      background-position: center;
      padding: 18px 0 58px;
    }
    .page-nav { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 70px; }
    .page-brand { color: var(--ink); font-weight: 900; text-decoration: none; }
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
    .page-layout { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 28px; padding: 34px 0 58px; align-items: start; }
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
      .page-stats, .page-grid, .score-list, .trust-brief, .brief-panel { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 560px) {
      .page-shell { width: min(1120px, calc(100% - 28px)); }
      .page-nav { align-items: flex-start; }
      .page-hero-grid > div { max-width: min(100%, 362px); }
      h1 { max-width: min(100%, 362px); font-size: clamp(31px, 9.5vw, 40px); line-height: 1; word-break: break-word; }
      .page-lede { max-width: min(100%, 362px); }
      .page-lede { font-size: 16px; }
      .page-stats, .page-grid, .score-list, .intake-grid, .trust-brief, .brief-panel { grid-template-columns: 1fr; }
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
    }
"""


def schema_for_destination(dest: dict, canonical: str) -> list[dict]:
    return [
        *global_schema_entities(),
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": f"{dest['name']} Property Research",
            "url": canonical,
            "description": f"{dest['name']} property research for global buyers, including ownership clarity, retirement fit, rental context, risks, and destination score.",
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


def build_destination_page(dest: dict, listings: list[dict], destinations: list[dict], pages: list[dict]) -> str:
    slug = destination_slug(dest)
    canonical = destination_url(dest)
    title = f"{dest['name']} Property Research | Global Home Atlas"
    description = (
        f"{dest['name']} property research for global buyers: ownership clarity, retirement fit, "
        f"rental income context, USD/m2 benchmark, risks, and long-term lifestyle thesis."
    )
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
    country_hub = country_hub_for_destination(dest)
    country_hub_link = (
        f'<a href="/countries/{escape(country_hub["slug"])}/">{escape(country_hub["h1"])}</a>'
        if country_hub
        else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
{head_html(title, description, canonical, schema_for_destination(dest, canonical))}
  <style>{shared_content_css()}</style>
</head>
<body class="has-mobile-actions">
  <header class="page-hero">
    <div class="page-shell">
      {primary_nav_html()}
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">{escape(dest.get("category") or "Destination")} · {escape(dest.get("country") or "")} · updated {date.today().isoformat()}</p>
          <h1>{escape(dest["name"])} Property Research</h1>
          <p class="page-lede">{escape(dest.get("panel_summary") or "")}</p>
          <div class="brief-panel">
            <article><span>Verdict</span><strong>{escape(dest.get("panel_verdict") or "Shortlist candidate")}</strong><p>{escape(dest.get("profit_driver") or "")}</p></article>
            <article><span>Best for</span><strong>{escape((dest.get("pros") or ["Lifestyle-led buyers"])[0])}</strong><p>Use this market when lifestyle demand, ownership confidence, and a future resale route can all be underwritten.</p></article>
            <article><span>Watch-outs</span><strong>{escape((dest.get("cons") or ["Verify local risk"])[0])}</strong><p>{escape(dest.get("red_flags") or "Verify current rules, asset condition, and resale depth before acting.")}</p></article>
          </div>
        </div>
        <aside class="page-hero-card">
          <span>Global rank</span><strong>#{dest["rank"]}</strong>
          <span>Decision score</span><strong>{dest.get("decision_score", 0):.2f}/5</strong>
          <span>Entry benchmark</span><strong>{money(dest.get("usd_per_m2"))}/m2</strong>
        </aside>
      </div>
    </div>
  </header>
  <main>
    <div class="page-shell">
      <section class="page-stats" aria-label="Destination metrics">
        <div><span>Net yield</span><strong>{escape(dest.get("net_yield_estimate") or "n/a")}</strong></div>
        <div><span>Ownership</span><strong>{metric_value(dest, "ownership_clarity"):.1f}/5</strong></div>
        <div><span>Retirement</span><strong>{metric_value(dest, "retirement_fit"):.1f}/5</strong></div>
        <div><span>Exit liquidity</span><strong>{metric_value(dest, "exit_liquidity"):.1f}/5</strong></div>
      </section>
      <section class="brief-panel" aria-label="Destination dossier summary">
        <article><span>Decision score</span><strong>{dest.get("decision_score", 0):.2f}/5</strong><p>Composite score across ownership, lifestyle, yield realism, retirement fit, value entry, and future exit quality.</p></article>
        <article><span>Ownership clarity</span><strong>{metric_value(dest, "ownership_clarity"):.1f}/5</strong><p>{escape(dest.get("ownership_notes") or "Confirm title structure, foreign-buyer rules, transfer taxes, and local counsel requirements.")}</p></article>
        <article><span>Lifestyle and retirement fit</span><strong>{metric_value(dest, "retirement_fit"):.1f}/5</strong><p>Use this as a long-stay practicality signal, not a holiday appeal score.</p></article>
      </section>
      {sticky_page_nav([("Verdict", "verdict"), ("Buyer Fit", "buyer-fit"), ("Ownership", "ownership"), ("Lifestyle", "lifestyle"), ("Scores", "scores"), ("Evidence", "evidence"), ("Trust", "trust-context")])}
      {mobile_action_strip("#scores", "Scores", "/#destinations", "Compare")}
      {trust_brief_html()}
      <div class="page-layout">
        <article class="page-article">
          <details class="page-section" id="verdict" open>
            <summary><h2>Investment Thesis</h2></summary>
            <p>{escape(dest.get("profit_driver") or dest.get("panel_verdict") or "")}</p>
            <p>{escape(dest.get("panel_verdict") or "")} This page is built for a global buyer deciding whether {escape(dest["name"])} belongs on a serious property shortlist, not for casual travel inspiration. The useful question is whether the destination can support personal use, ownership confidence, rental realism, retirement optionality, and a future resale process.</p>
          </details>
          <details class="page-section" id="buyer-fit" open>
            <summary><h2>Buyer Fit</h2></summary>
            <div class="page-grid">
              <article class="page-card"><h3>Best Fit</h3><ul>{pros}</ul></article>
              <article class="page-card"><h3>Risk Check</h3><ul>{cons}</ul></article>
            </div>
          </details>
          <details class="page-section" id="ownership" open>
            <summary><h2>Ownership and Governance</h2></summary>
            <p>{escape(dest.get("ownership_notes") or "Confirm title structure, foreign-buyer rules, taxes, transfer process, and local counsel requirements before relying on any market-level conclusion.")}</p>
            <p>{escape(dest.get("red_flags") or "Verify current rules, building condition, liquidity, and rental permissions before committing capital.")}</p>
          </details>
          <details class="page-section" id="lifestyle" open>
            <summary><h2>Lifestyle and Retirement Fit</h2></summary>
            <p>For an affluent global buyer, {escape(dest["name"])} should be evaluated as part of a long-term lifestyle plan rather than a standalone property purchase. The practical test is whether the destination can support repeat visits, extended stays, healthcare and daily convenience, family use, professional access, and a future shift from vacation use to retirement or semi-retirement.</p>
            <p>The Atlas score treats the destination as a portfolio decision. Strong scenery or rental appeal is not enough if the ownership path is unclear, the resale pool is thin, or the buyer would not want to spend real time there outside peak season. This is why the destination page keeps governance, exit liquidity, and retirement fit beside lifestyle and yield.</p>
          </details>
          <details class="page-section" open>
            <summary><h2>Guide Context</h2></summary>
            <p>Use these buying guides to compare {escape(dest["name"])} against other markets that share the same buyer intent, ownership questions, or long-term lifestyle role.</p>
            <nav class="page-grid">{destination_guide_links}</nav>
          </details>
          <details class="page-section" id="scores" open>
            <summary><h2>Score Breakdown</h2></summary>
            <ul class="score-list">{dimension_rows}</ul>
          </details>
          <details class="page-section" id="evidence" open>
            <summary><h2>Evidence Trail</h2></summary>
            <p>{escape(dest.get("price_basis") or "Listing samples are used as evidence anchors for current market texture, not availability guarantees.")}</p>
            {evidence_cards}
          </details>
          <details class="page-section" open>
            <summary><h2>Due Diligence Checklist</h2></summary>
            <ul>
              <li>Verify clean title, transfer process, foreign-buyer restrictions, and beneficial ownership structure with independent local counsel.</li>
              <li>Model acquisition tax, annual property tax, income tax, wealth tax exposure, financing availability, insurance, repairs, and property management fees.</li>
              <li>Confirm short-term-rental rules, licensing, building permissions, homeowners association rules, and realistic net income after vacancy and operating costs.</li>
              <li>Stress-test resale liquidity by reviewing recent comparable transactions, buyer nationality mix, time on market, and local agent depth.</li>
            </ul>
          </details>
        </article>
        <details class="page-aside mobile-resources" open>
          <summary>More resources</summary>
          <section class="page-aside-card">
            <h2>Compare in Atlas</h2>
            <p>Use the dashboard to compare {escape(dest["name"])} against every market in the 10-dimension model.</p>
            <a class="page-button" href="/#destinations" data-track="dashboard_open" data-track-label="{escape(dest["name"])} destination">Open dashboard</a>
            <a class="page-button" href="/contact/#custom-shortlist" data-track="custom_shortlist_cta" data-track-label="{escape(dest["name"])} destination">Request custom shortlist</a>
          </section>
          <section class="page-aside-card">
            <h3>Related Destinations</h3>
            <nav>{peer_links}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Country Context</h3>
            <nav>{country_hub_link or country_hub_links(limit=4)}</nav>
          </section>
          <section class="page-aside-card">
            <h3>Research Guides</h3>
            <nav><a href="/guides/">All buying guides</a>{seo_guide_links(pages, limit=5)}</nav>
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
      <p>Scores and listing benchmarks are research inputs, not financial, legal, tax, or immigration advice.</p>
      <nav><a href="/guides/">All buying guides</a> {seo_guide_links(pages, limit=6)} {trust_page_links()}</nav>
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
            <p>The site prioritizes decision usefulness over destination promotion. Markets can score well while still carrying material risks. Risks are surfaced directly because affluent global buyers need to understand what can break before they spend time on lawyers, agents, flights, or offers.</p>
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
            <p>The product compares destinations before it compares individual homes. That sequence matters. The wrong jurisdiction, ownership structure, or liquidity profile can make a beautiful property a poor decision. The Atlas helps buyers narrow the world to markets worthy of deeper local due diligence.</p>
          </section>
        """
    return """
      <section class="page-section" id="custom-shortlist">
        <h2>Contact and Research Requests</h2>
        <p>For data corrections, research questions, partnership inquiries, or custom shortlist requests, use this intake path. The form opens a structured email so the request can be handled without adding a server-side backend yet.</p>
        <p>Useful context for any request: target countries, budget range, intended use, preferred holding period, rental expectations, citizenship/residency constraints, and whether the priority is retirement, lifestyle, income, capital preservation, or optionality.</p>
        <form class="intake-form" id="custom-shortlist-form">
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
            <label>Holding period<input name="holding_period" placeholder="Example: 7-10 years"></label>
          </div>
          <label>Notes<textarea name="notes" placeholder="Citizenship, family use, healthcare needs, rental expectations, timing, and any must-avoid risks."></textarea></label>
          <button type="submit" data-track="custom_shortlist_submit_click">Prepare request</button>
        </form>
      </section>
      <section class="page-section">
        <h2>Before You Send a Deal</h2>
        <p>Do not send confidential transaction documents until an explicit review process exists. The current site is designed for destination-level research, not legal review of individual property contracts.</p>
      </section>
    """


def build_trust_page(page: dict, destinations: list[dict], pages: list[dict]) -> str:
    canonical = page_url(page["slug"])
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
            <a class="page-button" href="/#destinations" data-track="dashboard_open" data-track-label="{escape(page["h1"])} trust page">Open dashboard</a>
            <a class="page-button" href="/contact/#custom-shortlist" data-track="custom_shortlist_cta" data-track-label="{escape(page["h1"])} trust page">Request custom shortlist</a>
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
    destinations = [consolidate_destination(item) for item in load_json("destinations.json")]
    destinations = sorted(destinations, key=lambda item: item["rank"])
    listings = load_json("listings.json")
    fx = load_json("fx_rates.json")
    listings_by_dest: dict[str, list[dict]] = {}
    for listing in listings:
        listings_by_dest.setdefault(listing["destination_id"], []).append(listing)

    top_retirement_ids = {
        item["id"]
        for item in sorted(destinations, key=lambda d: score(d, "retirement_suitability"), reverse=True)[:5]
    }
    cards = "".join(
        build_destination_card(dest, listings_by_dest.get(dest["id"], []), top_retirement_ids)
        for dest in destinations
    )

    avg_score = sum(float(item.get("decision_score", 0) or 0) for item in destinations) / len(destinations)
    min_price = min(float(item.get("usd_per_m2", 0) or 0) for item in destinations)
    countries = len({item.get("country") for item in destinations if item.get("country")})
    categories = sorted({item.get("category") for item in destinations if item.get("category")})
    category_options = "\n".join(
        f'<option value="{escape(category)}">{escape(category)}</option>' for category in categories
    )
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
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='32' fill='%2310241f'/%3E%3Cpath d='M17 37 32 18l15 19v11H36V36h-8v12H17Z' fill='%23fffdf8'/%3E%3C/svg%3E">
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
    .brand-mark {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(36, 49, 45, .20);
      border-radius: 50%;
      background: rgba(255, 253, 247, .62);
    }
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
    .compare-actions button, .decision-row button {
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      font-weight: 850;
      padding: 0 12px;
    }
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
    .decision-row {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      align-items: center;
      padding: 0 18px 16px;
    }
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
    .hidden { display: none; }
    @media (max-width: 980px) {
      .hero { min-height: auto; padding-bottom: 66px; }
      .hero-grid, .workbench { grid-template-columns: 1fr; }
      .control-panel { position: static; }
      .mobile-jump { display: flex; }
      .spotlight-grid, .guide-grid { grid-template-columns: 1fr; }
      .metric-strip, .brief-grid { grid-template-columns: repeat(2, 1fr); }
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
      .trust-panel { padding: 14px; }
      .trust-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
      .trust-grid div { padding: 10px; }
      .trust-grid strong { font-size: 20px; }
      .insight-bar, .metric-strip, .brief-grid, .pros-cons, .score-board ul, .evidence-grid, .listing, .listing__facts { grid-template-columns: 1fr; }
      .insight-bar { margin: 0 -2px; }
      main { margin-top: -24px; }
      .workbench { padding-top: 14px; }
      .section-header, .section-heading { display: block; }
      #resultCount { display: block; margin-top: 8px; }
      summary { grid-template-columns: 44px minmax(0, 1fr); gap: 12px; min-height: 0; padding: 15px; align-items: start; }
      .rank-mark { width: 40px; height: 40px; }
      .score-dial { grid-column: 2; width: auto; height: auto; display: flex; justify-content: flex-start; gap: 4px; border: 0; border-radius: 0; background: transparent; text-align: left; }
      .summary-compare { grid-column: 2; justify-content: flex-start; width: max-content; padding: 0 10px; }
      .summary-copy span { -webkit-line-clamp: 3; }
      .brief-grid article, .pros-cons article, .score-board, .evidence-board, .listings-wrap, .section-header, .research-note { padding: 15px; }
      .metric-strip div { padding: 14px 15px; }
      .lens-grid, .export-row { grid-template-columns: 1fr 1fr; }
    }
  </style>
</head>
<body>
  <header class="hero" id="top">
    <nav class="topbar" aria-label="Primary">
      <div class="shell topbar__inner">
        <div class="brand"><span class="brand-mark">G</span><span>Global Home Atlas</span></div>
        <div class="top-links">
          <a href="#shortlist">Shortlist</a>
          <a href="#compare">Compare</a>
          <a href="/countries/spain-property/">Countries</a>
          <a href="#research">Research Method</a>
          <a href="#destinations">Destinations</a>
          <a href="/guides/">Guides</a>
          <a href="/methodology/">Methodology</a>
          <a href="/contact/">Contact</a>
        </div>
        <details class="mobile-menu">
          <summary>Menu</summary>
          <nav aria-label="Mobile primary">
            <a href="#compare">Compare</a>
            <a href="/countries/spain-property/">Countries</a>
            <a href="#destination-index">Destinations</a>
            <a href="/guides/">Guides</a>
            <a href="/methodology/">Methodology</a>
            <a href="/contact/">Contact</a>
          </nav>
        </details>
      </div>
    </nav>
    <div class="shell hero-grid">
      <div>
        <p class="eyebrow">Global mobility and property intelligence</p>
        <h1>Global Home Atlas</h1>
        <p class="lede">A calm research atlas for affluent global buyers comparing where a next home, second base, or long-stay investment can work across lifestyle, ownership clarity, yield realism, exit liquidity, and retirement optionality.</p>
        <div class="hero-actions">
          <a class="primary-action" href="#destinations" data-track="dashboard_open" data-track-label="homepage hero">Explore destinations</a>
          <a class="secondary-action" href="/countries/spain-property/" data-track="country_hub_click" data-track-label="homepage hero">Explore countries</a>
          <a class="secondary-action" href="/guides/" data-track="guide_click" data-track-label="homepage hero">Read buying guides</a>
          <a class="secondary-action" href="/methodology/" data-track="methodology_click" data-track-label="homepage hero">Review methodology</a>
        </div>
      </div>
      <aside class="trust-panel" aria-label="Credibility snapshot">
        <h2>Independent, not paid placement</h2>
        <div class="atlas-visual" aria-hidden="true">
          <div class="atlas-visual__label"><span>Atlas route</span>Ownership · lifestyle · exit</div>
          <div class="atlas-visual__route">
            <span>Valencia</span>
            <span>Fukuoka</span>
            <span>Algarve</span>
          </div>
        </div>
        <div class="trust-grid">
          <div><span>Destinations</span><strong>__DEST_COUNT__</strong></div>
          <div><span>Countries</span><strong>__COUNTRY_COUNT__</strong></div>
          <div><span>Decision model</span><strong>10 dimensions</strong></div>
          <div><span>Evidence base</span><strong>__LISTING_COUNT__ samples</strong></div>
          <div><span>Updated</span><strong>__GENERATED__</strong></div>
          <div><span>Advice type</span><strong>Research only</strong></div>
        </div>
      </aside>
    </div>
  </header>

  <main>
    <div class="shell">
      <section class="insight-bar" aria-label="Dataset summary">
        <div><span>Top score</span><strong>__TOP_SCORE__</strong></div>
        <div><span>Average score</span><strong>__AVG_SCORE__</strong></div>
        <div><span>Lowest USD/m2</span><strong>__LOW_PRICE__</strong></div>
        <div><span>Generated</span><strong>__GENERATED__</strong></div>
      </section>
      <section class="landscape-band" aria-label="Global Home Atlas research promise">
        <blockquote>
          Clarity is the ultimate luxury.
          <cite>Research. Perspective. Freedom to choose.</cite>
        </blockquote>
      </section>

      <div class="workbench">
        <aside class="control-panel" id="research">
          <h2>Research Console</h2>
          <p>Filter by thesis, then open each destination for the committee read, risk checks, scores, and listing evidence.</p>
          <form class="toolbar" id="toolbar">
            <div class="field">
              <label for="search">Search</label>
              <input id="search" type="search" placeholder="Destination or country" aria-label="Search destination or country">
            </div>
            <div class="field">
              <label for="category">Terrain</label>
              <select id="category" aria-label="Filter by category">
                <option value="all">All terrain types</option>
                __CATEGORY_OPTIONS__
              </select>
            </div>
            <div class="field">
              <label for="sort">Sort by</label>
              <select id="sort" aria-label="Sort destinations">
                <option value="rank">Panel rank</option>
                <option value="score">Overall score</option>
                <option value="price">Lowest USD/m2</option>
                <option value="yield">Yield potential</option>
                <option value="ownership">Ownership clarity</option>
                <option value="retirement">Retirement suitability</option>
              </select>
            </div>
            <div class="field">
              <label>Investor lens</label>
              <div class="lens-grid" role="group" aria-label="Quick view">
                <button type="button" data-quick="all" aria-pressed="true">All</button>
                <button type="button" data-quick="shortlist">Shortlist</button>
                <button type="button" data-quick="ownership">Clean title</button>
                <button type="button" data-quick="retirement">Retire well</button>
              </div>
            </div>
          </form>
          <div class="export-row">
            <button type="button" id="export">JSON</button>
            <button type="button" id="exportCsv">CSV</button>
          </div>
          <div class="weight-panel">
            <h3>10-Dimension Weights</h3>
            <p>Adjust the investment lens and the decision score recalculates across every destination.</p>
            <div class="weight-controls">
              __WEIGHT_CONTROLS__
            </div>
          </div>
          <div class="mobile-jump" aria-label="Mobile navigation">
            <a href="#compare">Compare</a>
            <a href="/countries/spain-property/">Countries</a>
            <a href="#destinations">Destinations</a>
            <a href="/guides/">Guides</a>
            <a href="/methodology/">Methodology</a>
            <a href="/contact/">Contact</a>
          </div>
          <div class="method-card">
            <h3>Decision Standard</h3>
            <ul>
              <li>Foreign ownership and exit friction are scored before romance.</li>
              <li>Yield is treated as underwriting context, not a promise.</li>
              <li>Listings are evidence anchors, not availability guarantees.</li>
              <li><a href="/research-standards/">Research standards</a>, <a href="/methodology/">methodology</a>, and <a href="/contact/">contact</a> stay one tap away.</li>
            </ul>
          </div>
        </aside>

        <div class="content-stack">
          <section class="section-card" id="shortlist">
            <div class="section-header">
              <div>
                <h2>Priority Shortlist</h2>
                <p>The strongest current candidates surface immediately, then the dashboard lets buyers test ownership, lifestyle, retirement, yield, and exit assumptions.</p>
              </div>
            </div>
            <div class="spotlight-grid">
              __SPOTLIGHT__
            </div>
          </section>

          <section class="section-card" id="conversion">
            <div class="section-header">
              <div>
                <h2>Custom Global Property Shortlist</h2>
                <p>Turn the Atlas into a buyer-specific research brief across lifestyle plan, budget, citizenship constraints, rental expectations, and holding period.</p>
              </div>
              <a class="primary-action" href="/contact/#custom-shortlist" data-track="custom_shortlist_cta" data-track-label="homepage conversion section">Request shortlist</a>
            </div>
          </section>

          <section class="compare-panel" id="compare">
            <div class="section-header">
              <div>
                <h2>Compare 2-4 Destinations</h2>
                <p>Select destinations from the dossiers to compare score, ownership, value, yield, retirement fit, and investment thesis.</p>
              </div>
              <div class="compare-actions">
                <button type="button" id="clearCompare">Clear</button>
                <button type="button" id="exportMemo">Export memo</button>
              </div>
            </div>
            <div id="compareOutput" class="compare-empty">Select at least two destinations to build a comparison table.</div>
          </section>

          <section class="section-card" id="destinations">
            <div class="section-header">
              <div>
                <h2>Destination Dossiers</h2>
                <p>Each dossier combines investment thesis, lifestyle durability, legal clarity, and representative live-market listings.</p>
              </div>
              <span id="resultCount">__DEST_COUNT__ shown</span>
            </div>
            <div class="cards" id="cards">
              __CARDS__
            </div>
            <p class="research-note">FX as of __FX_AS_OF__. Listing data is research-grade and changes quickly; verify live availability, tax treatment, permits, title structure, and local counsel advice before any investment decision.</p>
          </section>
        </div>
      </div>
      <section class="guide-section" id="guides">
        <div class="guide-section__header">
          <div>
            <h2>Buyer Guides</h2>
            <p>Crawlable research pages for the highest-intent searches: retirement property, vacation homes, expat ownership, country comparisons, and overseas investment.</p>
          </div>
          <a href="/guides/" data-track="guide_click" data-track-label="homepage guide section">Browse guides</a>
        </div>
        <div class="guide-grid">
          __SEO_GUIDES__
        </div>
      </section>

      <section class="guide-section" id="destination-index">
        <div class="guide-section__header">
          <div>
            <h2>Destination Research</h2>
            <p>Individual destination dossiers for global buyers who need ownership, retirement, rental, risk, and resale context before local due diligence.</p>
          </div>
          <a href="/destinations/fukuoka-itoshima/" data-track="destination_click" data-track-label="homepage destination section">View top destination</a>
        </div>
        <div class="guide-grid">
          __DESTINATION_GUIDES__
        </div>
      </section>

      <section class="guide-section" id="trust">
        <div class="guide-section__header">
          <div>
            <h2>Trust Layer</h2>
            <p>Research standards, scoring methodology, caveats, and contact context to establish credibility before a buyer relies on the Atlas.</p>
          </div>
          <a href="/research-standards/" data-track="trust_click" data-track-label="homepage trust section">Read standards</a>
        </div>
        <div class="guide-grid">
          __TRUST_GUIDES__
        </div>
      </section>
    </div>
  </main>

  <script type="application/json" id="app-data">__APP_DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById("app-data").textContent);
    const cards = Array.from(document.querySelectorAll(".destination-card"));
    const cardsRoot = document.getElementById("cards");
    const search = document.getElementById("search");
    const category = document.getElementById("category");
    const sort = document.getElementById("sort");
    const resultCount = document.getElementById("resultCount");
    const lensButtons = Array.from(document.querySelectorAll("[data-quick]"));
    const weightInputs = Array.from(document.querySelectorAll("[data-weight-key]"));
    const compareOutput = document.getElementById("compareOutput");
    const compareSelected = new Set();
    const memoShortlist = new Set();
    let quickView = "all";

    const destinationsById = new Map(data.destinations.map((destination) => [destination.id, destination]));
    data.destinations.forEach((destination) => {
      destination.custom_score = destination.decision_score;
    });

    function cardRank(card) {
      return Number(card.querySelector(".rank-mark span").textContent.replace("#", ""));
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
        const card = document.querySelector(`.destination-card[data-id="${destination.id}"]`);
        if (card) {
          card.dataset.score = destination.custom_score;
          card.querySelector("[data-custom-score]").textContent = destination.custom_score.toFixed(2);
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
        const matchesCategory = selectedCategory === "all" || card.dataset.category === selectedCategory;
        const matchesQuick =
          quickView === "all" ||
          (quickView === "shortlist" && card.dataset.shortlist === "yes") ||
          (quickView === "ownership" && Number(card.dataset.ownership) >= 4) ||
          (quickView === "retirement" && card.dataset.topRetirement === "yes");
        const visible = matchesQuery && matchesCategory && matchesQuick;
        card.classList.toggle("hidden", !visible);
        if (visible) shown += 1;
      });

      const sorted = [...cards].sort((a, b) => {
        if (sort.value === "score") return Number(b.dataset.score) - Number(a.dataset.score);
        if (sort.value === "price") return Number(a.dataset.price) - Number(b.dataset.price);
        if (sort.value === "yield") return Number(b.dataset.yield) - Number(a.dataset.yield);
        if (sort.value === "ownership") return Number(b.dataset.ownership) - Number(a.dataset.ownership);
        if (sort.value === "retirement") return Number(b.dataset.retirement) - Number(a.dataset.retirement);
        return cardRank(a) - cardRank(b);
      });
      sorted.forEach((card) => cardsRoot.appendChild(card));
      resultCount.textContent = shown + (shown === 1 ? " destination shown" : " destinations shown");
    }

    function destinationMetric(destination, key) {
      return destination.decision_dimensions.find((item) => item.key === key)?.score || 0;
    }

    function selectedCompareDestinations() {
      return [...compareSelected].map((id) => destinationsById.get(id)).filter(Boolean);
    }

    function renderCompare() {
      const selected = selectedCompareDestinations();
      if (selected.length < 2) {
        compareOutput.className = "compare-empty";
        compareOutput.textContent = selected.length === 1
          ? "Select one more destination to build a comparison table."
          : "Select at least two destinations to build a comparison table.";
        return;
      }
      compareOutput.className = "compare-table-wrap";
      const rows = [
        ["Decision score", ...selected.map((d) => d.custom_score.toFixed(2))],
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
    sort.addEventListener("change", applyFilters);
    weightInputs.forEach((input) => input.addEventListener("input", recalculateScores));
    lensButtons.forEach((button) => {
      button.addEventListener("click", () => {
        quickView = button.dataset.quick;
        lensButtons.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
        applyFilters();
      });
    });
    document.querySelectorAll(".compare-toggle").forEach((checkbox) => {
      checkbox.addEventListener("change", () => setCompare(checkbox.value, checkbox.checked));
    });
    document.querySelectorAll(".summary-compare").forEach((label) => {
      label.addEventListener("click", (event) => event.stopPropagation());
    });
    document.querySelectorAll(".memo-add").forEach((button) => {
      button.addEventListener("click", () => {
        const id = button.dataset.memoId;
        if (memoShortlist.has(id)) {
          memoShortlist.delete(id);
          button.textContent = "Add to memo shortlist";
          if (window.GHA) window.GHA.track("memo_shortlist_remove", { destination_id: id, selected_count: memoShortlist.size });
        } else {
          memoShortlist.add(id);
          button.textContent = "Remove from memo";
          if (window.GHA) window.GHA.track("memo_shortlist_add", { destination_id: id, selected_count: memoShortlist.size });
        }
      });
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

    function memoDestinations() {
      if (compareSelected.size >= 2) return selectedCompareDestinations();
      if (memoShortlist.size) return [...memoShortlist].map((id) => destinationsById.get(id)).filter(Boolean);
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

    function buildMemoHtml() {
      const selected = memoDestinations();
      const generated = new Date().toISOString().slice(0, 10);
      const rows = selected.map((d) => `
        <section>
          <h2>${escapeHtml(d.name)} <span>${escapeHtml(d.country || "")}</span></h2>
          <dl>
            <div><dt>Decision score</dt><dd>${d.custom_score.toFixed(2)} / 5</dd></div>
            <div><dt>USD/m2</dt><dd>$${Number(d.usd_per_m2 || 0).toLocaleString()}</dd></div>
            <div><dt>Net yield</dt><dd>${escapeHtml(d.net_yield_estimate || "n/a")}</dd></div>
            <div><dt>Ownership</dt><dd>${destinationMetric(d, "ownership_clarity").toFixed(1)} / 5</dd></div>
          </dl>
          <h3>Investment thesis</h3>
          <p>${escapeHtml(d.profit_driver || d.panel_summary || "")}</p>
          <h3>Risk check</h3>
          <p>${escapeHtml(d.red_flags || "Verify title, tax, permit, and local market liquidity before committing capital.")}</p>
          <h3>10-dimension rating</h3>
          <table>
            <tbody>${d.decision_dimensions.map((item) => `<tr><th>${escapeHtml(item.label)}</th><td>${Number(item.score).toFixed(1)}</td><td>${escapeHtml(item.evidence)}</td></tr>`).join("")}</tbody>
          </table>
        </section>
      `).join("");
      return `<!doctype html>
        <html><head><meta charset="utf-8"><title>Investor Shortlist Memo</title>
        <style>
          body{font-family:Inter,Arial,sans-serif;margin:40px;color:#24312d;background:#fffdf7;line-height:1.5}
          h1{font-family:Georgia,serif;font-size:42px;line-height:1;margin:0 0 8px} h2{margin-top:32px;border-top:1px solid #ddd4c7;padding-top:24px}
          h2 span{color:#66736c;font-size:16px;font-weight:500} h3{margin-bottom:6px;font-size:13px;text-transform:uppercase;letter-spacing:.06em}
          dl{display:grid;grid-template-columns:repeat(4,1fr);gap:10px} dl div{border:1px solid #ddd4c7;padding:10px;border-radius:6px}
          dt{color:#66736c;font-size:11px;text-transform:uppercase;font-weight:800} dd{margin:4px 0 0;font-weight:800}
          table{width:100%;border-collapse:collapse;margin-top:8px} th,td{text-align:left;border-top:1px solid #ddd4c7;padding:8px;vertical-align:top;font-size:13px}
          @media(max-width:720px){body{margin:20px}dl{grid-template-columns:1fr}}
        </style></head><body>
        <h1>Investor Shortlist Memo</h1>
        <p>Generated ${generated}. Scores use the current 10-dimension weighting model from Global Home Atlas.</p>
        ${rows}
        </body></html>`;
    }

    document.getElementById("exportMemo").addEventListener("click", () => {
      if (window.GHA) window.GHA.track("memo_export", { selected_count: memoDestinations().length });
      downloadFile("investor-shortlist-memo.html", "text/html", buildMemoHtml());
    });

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
        "__TOP_SCORE__": f"{destinations[0]['decision_score']:.2f}",
        "__AVG_SCORE__": f"{avg_score:.2f}",
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
        "__ANALYTICS_HEAD__": analytics_head_tags(),
        "__ANALYTICS_EVENT_SCRIPT__": analytics_event_script(),
    }
    for key, value in replacements.items():
        html = html.replace(key, value)

    ARTIFACTS.mkdir(exist_ok=True)
    out = ARTIFACTS / "unified_destination_dashboard.html"
    index = ARTIFACTS / "index.html"
    cname = ARTIFACTS / "CNAME"
    robots = ARTIFACTS / "robots.txt"
    sitemap = ARTIFACTS / "sitemap.xml"
    indexnow_key_file = ARTIFACTS / f"{INDEXNOW_KEY}.txt"
    html = clean_generated_html(html)
    out.write_text(html, encoding="utf-8")
    index.write_text(html, encoding="utf-8")
    copy_site_assets()
    guide_hub_dir = ARTIFACTS / GUIDE_HUB_SLUG
    guide_hub_dir.mkdir(parents=True, exist_ok=True)
    (guide_hub_dir / "index.html").write_text(
        clean_generated_html(build_guide_hub_page(SEO_PAGES, destinations)),
        encoding="utf-8",
    )
    for page in SEO_PAGES:
        page_dir = ARTIFACTS / page["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            clean_generated_html(build_seo_page(page, destinations, SEO_PAGES)),
            encoding="utf-8",
        )
    destinations_dir = ARTIFACTS / "destinations"
    destinations_dir.mkdir(exist_ok=True)
    for dest in destinations:
        page_dir = destinations_dir / destination_slug(dest)
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            clean_generated_html(build_destination_page(dest, listings_by_dest.get(dest["id"], []), destinations, SEO_PAGES)),
            encoding="utf-8",
        )
    countries_dir = ARTIFACTS / "countries"
    countries_dir.mkdir(exist_ok=True)
    for hub in COUNTRY_HUBS:
        page_dir = countries_dir / hub["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            clean_generated_html(build_country_hub_page(hub, destinations, SEO_PAGES)),
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
        (page_url(GUIDE_HUB_SLUG), "0.90"),
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
