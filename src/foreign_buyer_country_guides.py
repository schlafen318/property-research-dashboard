"""Structured content and validation for migrated foreign-buyer country guides."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
import ipaddress
import re
import unicodedata
from urllib.parse import urlsplit
from urllib.parse import unquote_to_bytes


REQUIRED_GUIDE_KEYS = {
    "country",
    "title",
    "description",
    "h1",
    "summary",
    "date_published",
    "date_reviewed",
    "hero_image",
    "direct_answers",
    "eligibility_sections",
    "purchase_steps",
    "cost_rows",
    "acquisition_example",
    "ownership_rules",
    "destination_reads",
    "engagement_links",
    "buyer_checklist",
    "faqs",
    "primary_sources",
    "retirement_guide_slug",
}
REQUIRED_DIRECT_ANSWERS = {"ownership", "residency", "financing", "short_rentals"}
REQUIRED_ENGAGEMENT_PATHS = {
    "/retirement-abroad-calculator/",
    "/retirement-destinations-ranked-by-cost/",
}
REQUIRED_COST_COVERAGE = {
    "acquisition": ("acquisition", "registration tax"),
    "recurring ownership": ("annual", "ownership", "holding", "management", "repair"),
}
REQUIRED_OWNERSHIP_COVERAGE = {
    "owner administration": ("owner", "record", "registration", "address"),
    "building operations": ("condominium", "building", "repair", "management"),
    "rental authority": ("rental", "lodging", "operator"),
    "tax": ("tax",),
    "hazard or insurance": ("hazard", "insurance"),
}

FOREIGN_BUYER_COUNTRY_GUIDES: dict[str, dict] = {
    "japan-property": {
        "country": "Japan",
        "title": "Buying Property in Japan as a Foreigner | Global Home Atlas",
        "description": "Learn how foreigners can buy property in Japan, including ownership rights, the purchase process, taxes, financing, reporting, rental rules, and four markets.",
        "h1": "Buying Property in Japan as a Foreigner",
        "summary": "Foreigners can generally own Japanese land and buildings, but the purchase creates no residence rights and non-resident buyers face reporting, financing, tax, management, and property-specific checks.",
        "date_published": "2026-08-27",
        "date_reviewed": "2026-08-27",
        "hero_image": {
            "src": "/assets/fukuoka-itoshima-coast.webp",
            "alt": "Fukuoka and Itoshima coastline in Japan",
            "caption": "Fukuoka / Itoshima · City access and coastal living",
        },
        "direct_answers": {
            "ownership": {
                "answer": "Yes. Foreign individuals living overseas can generally buy and register Japanese land and buildings. Confirm the title, land category, use controls, and registration documents for the specific asset.",
                "source_urls": [
                    "https://www.moj.go.jp/MINJI/minji05_00574.html",
                    "https://www.moj.go.jp/MINJI/minji05_00589.html",
                    "https://www.mlit.go.jp/common/001050449.pdf",
                ],
            },
            "residency": {
                "answer": "No. Buying property does not create a visa or residence rights. Qualify under a separate immigration route before planning to live in Japan long term.",
                "contextual_link": {
                    "phrase": "Buying property does not create a visa or residence rights.",
                    "url": "https://www.city.fukuoka.lg.jp/keizai/k-yuchi/business/documents/english-faq.pdf",
                },
                "source_urls": [
                    "https://www.city.fukuoka.lg.jp/keizai/k-yuchi/business/documents/english-faq.pdf",
                    "https://www.moj.go.jp/isa/applications/guide/kanri_qa.html",
                    "https://www.mofa.go.jp/ca/fna/page22e_000738.html",
                ],
            },
            "financing": {
                "answer": "Mortgage access is lender-specific. Obtain written terms for residency, income, currency, deposit, guarantor, and property eligibility before making a binding offer.",
                "source_urls": [
                    "https://www.mlit.go.jp/common/001050450.pdf",
                ],
            },
            "short_rentals": {
                "answer": "Private lodging under the national notification framework is capped at 180 days a year and can be further restricted by local rules, condominium bylaws, or the operator contract.",
                "contextual_link": {
                    "phrase": "capped at 180 days a year",
                    "url": "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html",
                },
                "source_urls": [
                    "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html",
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
        },
        "eligibility_sections": [
            {
                "heading": "Overseas buyers need registration-ready identity evidence",
                "body": "A foreign buyer without a Japanese resident record should confirm the accepted government or notarized address evidence, passport copy, Japanese translations, and Roman-letter name evidence before signing. The registration professional should match every document to the buyer name used in the contract and remittance trail.",
                "source_urls": [
                    "https://www.moj.go.jp/MINJI/minji05_00574.html",
                    "https://www.moj.go.jp/MINJI/minji05_00589.html",
                ],
            },
            {
                "heading": "The asset and intended use remain property-specific",
                "body": "Check the registered land and building records, zoning and use limits, flood and other hazards, access, building condition, condominium bylaws, repair plan, and any operator or lease arrangement. Permission to own is not permission for every use.",
                "source_urls": [
                    "https://www.mlit.go.jp/common/001050448.pdf",
                    "https://www.mlit.go.jp/common/001050449.pdf",
                    "https://www.mlit.go.jp/totikensangyo/const/sosei_const_fr3_000074.html",
                    "https://disaportal.gsi.go.jp/",
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
            {
                "heading": "Residence status is a separate decision",
                "body": "Choose an immigration route on its own requirements and timetable. The official long-stay sightseeing route, for example, uses nationality or region, age, savings, insurance, and application-document criteria rather than property ownership.",
                "source_urls": [
                    "https://www.city.fukuoka.lg.jp/keizai/k-yuchi/business/documents/english-faq.pdf",
                    "https://www.moj.go.jp/isa/applications/guide/kanri_qa.html",
                    "https://www.mofa.go.jp/ca/fna/page22e_000738.html",
                ],
            },
        ],
        "purchase_steps": [
            {
                "heading": "Confirm the buyer and intended use",
                "body": "Decide who will hold title, whether the home is for personal use, long-term rent, or lodging, and whether financing is needed. Prepare the exact identity, overseas-address, translation, and funds-source record that the contract, bank, and registration will use.",
                "source_urls": [
                    "https://www.moj.go.jp/MINJI/minji05_00574.html",
                    "https://www.moj.go.jp/MINJI/minji05_00589.html",
                    "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html",
                ],
            },
            {
                "heading": "Appoint independent advisers",
                "body": "Before paying a deposit, assign responsibility for title and registration, contract review, tax, building inspection, translation, and settlement. A non-resident should also identify who will make Japanese-language FEFTA filings and whether a Japanese tax agent is required.",
                "source_urls": [
                    "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html",
                    "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf",
                ],
            },
            {
                "heading": "Check the property before offering",
                "body": "Obtain the land and building registry records and inspect the site, structure, access, utilities, legal use, hazard layers, boundaries, occupancy, leases, and repair history. For a condominium, read the bylaws, minutes, budget, management fees, reserve balance, long-term repair plan, and any owner-use or rental limits.",
                "source_urls": [
                    "https://www.mlit.go.jp/common/001050449.pdf",
                    "https://www.mlit.go.jp/common/001050450.pdf",
                    "https://disaportal.gsi.go.jp/",
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
            {
                "heading": "Review the contract and Important Matters Explanation",
                "body": "Have the Japanese contract, cancellation terms, deposit treatment, defects, fixtures, possession, tax adjustments, finance condition, and Important Matters Explanation reviewed before signing. Confirm the latest municipal flood map and investigate hazards beyond the mandatory flood-map explanation.",
                "source_urls": [
                    "https://www.mlit.go.jp/common/001050448.pdf",
                    "https://www.mlit.go.jp/common/001050450.pdf",
                    "https://www.mlit.go.jp/totikensangyo/const/sosei_const_fr3_000074.html",
                    "https://disaportal.gsi.go.jp/",
                ],
            },
            {
                "heading": "Settle and register the transfer",
                "body": "Coordinate verified remittance, final inspection, remaining-price payment, keys and documents, repayment or release of seller security, and transfer registration for the land and building. Registration is essential to assert ownership against third parties.",
                "source_urls": [
                    "https://www.mlit.go.jp/common/001050449.pdf",
                    "https://www.mlit.go.jp/common/001050450.pdf",
                    "https://www.moj.go.jp/MINJI/minji05_00574.html",
                    "https://www.moj.go.jp/MINJI/minji05_00589.html",
                ],
            },
            {
                "heading": "Complete non-resident reporting and owner administration",
                "body": "If the buyer is non-resident, submit the FEFTA acquisition report through the Bank of Japan within 20 days. Put Japanese tax, insurance, utilities, property management, condominium notices and voting, repairs, and future name or address updates onto an operating calendar.",
                "contextual_link": {
                    "phrase": "submit the FEFTA acquisition report through the Bank of Japan within 20 days",
                    "url": "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html",
                },
                "source_urls": [
                    "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html",
                    "https://www.moj.go.jp/MINJI/minji05_00693.html",
                    "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf",
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
        ],
        "cost_rows": [
            {
                "cost": "Purchase price and settlement adjustments",
                "when": "Contract and settlement",
                "buyer_read": "Keep the agreed asset price separate from taxes and fees. Confirm deposit treatment, final payment, and prorated items in the contract and settlement statement.",
                "source_urls": [
                    "https://www.mlit.go.jp/common/001050450.pdf",
                ],
            },
            {
                "cost": "Acquisition and registration taxes",
                "when": "Registration and after acquisition",
                "buyer_read": "Budget registration and license tax and real-estate acquisition tax using the asset classification, fixed-asset assessment, buyer facts, relief eligibility, and closing date. They are not part of the purchase price.",
                "source_urls": [
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html",
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000072.html",
                ],
            },
            {
                "cost": "Brokerage and professional work",
                "when": "Search through settlement",
                "buyer_read": "Brokerage can arise on a brokered sale. Obtain separate written quotes for brokerage, registration, contract and tax advice, translation, inspection, valuation, banking, and remittance work rather than treating them as taxes.",
                "source_urls": [
                    "https://www.mlit.go.jp/common/001050450.pdf",
                ],
            },
            {
                "cost": "Annual ownership and building costs",
                "when": "Every year and when work falls due",
                "buyer_read": "Model fixed-asset and any city-planning tax, insurance, management fees, repair-reserve contributions, utilities, local management, and property repairs. For a condominium, test the reserve plan for future lump-sum calls.",
                "source_urls": [
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000073.html",
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
            {
                "cost": "Non-resident withholding and tax administration",
                "when": "At affected payment, rental operation, filing, or sale",
                "buyer_read": "Confirm whether a non-resident party causes withholding, Japanese returns, or appointment of a tax agent. The answer depends on the parties, payment path, income, transaction, and available exception.",
                "source_urls": [
                    "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf",
                ],
            },
            {
                "cost": "Eventual sale and transfer-out costs",
                "when": "Resale or other disposal",
                "buyer_read": "Treat sale tax, withholding, brokerage, professional advice, loan release, and transfer registration as a later event, not acquisition cost. Tax depends on the seller, gain, holding period, use, transaction expenses, and sale date.",
                "source_urls": [
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000074.html",
                    "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf",
                ],
            },
        ],
        "acquisition_example": {
            "heading": "Worked acquisition example",
            "intro": "Illustrative cash purchase of a ¥50 million resale apartment. The example assumes fixed-asset assessments of ¥15 million for land and ¥20 million for the building, no mortgage and no tax relief.",
            "rows": [
                {"label": "Purchase price", "amount": "¥50,000,000", "note": "Contract price"},
                {"label": "Brokerage ceiling", "amount": "¥1,716,000", "note": "3% + ¥60,000, then 10% consumption tax"},
                {"label": "Registration and licence tax", "amount": "¥625,000", "note": "1.5% of assumed land assessment plus 2% of assumed building assessment"},
                {"label": "Real-estate acquisition tax", "amount": "¥1,050,000", "note": "3% of both assumed assessments before any relief"},
            ],
            "total": "About ¥53.4 million before legal, registration-professional, inspection, insurance, remittance and settlement-adjustment quotes.",
            "caveat": "This is an illustrative stress case, not a closing quote. Actual tax uses the official assessment, transaction facts, applicable relief and rates in force at completion.",
            "source_urls": [
                "https://www.mlit.go.jp/sumai_literacy_pf/knowledge02/0005/",
                "https://www.nta.go.jp/publication/pamph/koho/kurashi/html/05_1.htm",
                "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000072.html",
            ],
        },
        "ownership_rules": [
            {
                "heading": "Keep the owner record current",
                "body": "From 2026-04-01, a registered owner must register a name or address change within two years. Overseas owners should arrange a reliable route for receiving notices and handling Japanese filings.",
                "source_urls": [
                    "https://www.moj.go.jp/MINJI/minji05_00693.html",
                ],
            },
            {
                "heading": "Fund condominium operations and repairs",
                "body": "A unit owner belongs to the management association and must follow its bylaws and pay management fees and repair-reserve contributions. Review the long-term repair plan, reserve adequacy, decisions, and any domestic-manager appointment for an overseas owner.",
                "source_urls": [
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
            {
                "heading": "Recheck short-rental authority before operating",
                "body": "The national private-lodging notification framework allows no more than 180 days a year, but local ordinances, condominium bylaws, and other lodging regimes may be stricter. An absent owner under this framework must entrust specified duties to a registered administrator.",
                "source_urls": [
                    "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html",
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
            {
                "heading": "Maintain tax and hazard files",
                "body": "Retain acquisition, improvement, rental, tax, insurance, management, and sale records. Recheck current municipal and national hazard information when planning works, insurance, occupancy, or resale.",
                "source_urls": [
                    "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf",
                    "https://disaportal.gsi.go.jp/",
                ],
            },
        ],
        "destination_reads": {
            "fukuoka-itoshima": {
                "best_for": "Year-round city life with coastal access and broad domestic demand",
                "verify_first": "Rail or car dependence, building condition, flood exposure, management and resale depth",
                "asking_price_context": "¥31.8m–¥180m · 3 asking observations · 21 Aug 2026",
            },
            "hakone-izu": {
                "best_for": "Personal use near Tokyo, onsen life and repeat weekend stays",
                "verify_first": "Slope, seismic condition, renovation scope, access, permitted use and thin comparable evidence",
                "asking_price_context": "¥12.3m–¥79.9m · 3 asking observations · 22 Aug 2026",
            },
            "hakuba": {
                "best_for": "Active alpine use with a lower entry point than Niseko",
                "verify_first": "Snow load, winter access, staffing, building condition, operating permissions and exit depth",
                "asking_price_context": "¥77m–¥152.46m · 3 asking observations · 22 Aug 2026",
            },
            "niseko": {
                "best_for": "Premium international resort use for buyers comfortable with high carrying costs",
                "verify_first": "Service charges, operator contract, construction quality, owner-use limits and resale depth",
                "asking_price_context": "¥65m–¥264.44m · 3 asking observations · 22 Aug 2026",
            },
        },
        "engagement_links": [
            {
                "label": "Calculate retirement capital",
                "href": "/retirement-abroad-calculator/?destination=fukuoka-itoshima&plan=own",
            },
            {
                "label": "View retirement cost rankings",
                "href": "/retirement-destinations-ranked-by-cost/",
            },
        ],
        "buyer_checklist": [
            "Match the contract buyer name to the passport, overseas address evidence accepted by the Legal Affairs Bureau, Japanese translations, bank remittance record, and registration application.",
            "Confirm whether the home can legally support personal use, long-term tenancy, or minpaku against zoning, municipal ordinances, condominium bylaws, leases, and operator agreements.",
            "Obtain the Japanese land and building registry records and resolve owners, mortgages, seizures, boundaries, and access.",
            "Inspect the structure and services and review flood, inland-water, landslide, tsunami, storm-surge, and seismic exposure.",
            "Have the Japanese Important Matters Explanation and contract independently translated and reviewed before signing.",
            "For non-resident financing, obtain written lender terms covering loan-to-value, guarantor, income currency, remittance, and property eligibility.",
            "Separate the price from brokerage, registration and licence tax, real-estate acquisition tax, annual fixed-asset and city-planning tax, management, and later sale costs.",
            "Before closing, name who will file the Japanese-language FEFTA report within 20 days, act as tax agent, receive owner notices, insure and manage the home, and update the registry after name or address changes.",
        ],
        "faqs": [
            {
                "question": "Can a foreigner living outside Japan own Japanese property?",
                "answer": "Generally, yes. Official registration procedures expressly address overseas foreign individuals becoming registered owners. The buyer still needs accepted identity and address evidence, Japanese translations where required, and property-specific checks.",
                "source_urls": [
                    "https://www.moj.go.jp/MINJI/minji05_00574.html",
                    "https://www.moj.go.jp/MINJI/minji05_00589.html",
                ],
            },
            {
                "question": "Does buying a home qualify me to live in Japan?",
                "answer": "No property-based residence right is created by the purchase. Residence status has its own legal categories and eligibility. Check the relevant immigration route independently before buying for full-time use.",
                "source_urls": [
                    "https://www.city.fukuoka.lg.jp/keizai/k-yuchi/business/documents/english-faq.pdf",
                    "https://www.moj.go.jp/isa/applications/guide/kanri_qa.html",
                    "https://www.mofa.go.jp/ca/fna/page22e_000738.html",
                ],
            },
            {
                "question": "What must a non-resident buyer report after closing?",
                "answer": "Under FEFTA, a non-resident acquiring Japanese real property or rights in it must report through the Bank of Japan within 20 days after acquisition. The buyer or a Japan-resident agent may file, and the report must be in Japanese.",
                "source_urls": [
                    "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html",
                ],
            },
            {
                "question": "Can I run short-term lodging from the property?",
                "answer": "Only if the chosen legal route and the property permit it. The private-lodging notification framework caps operation at 180 days a year; local ordinances, condominium bylaws, zoning, and operator agreements can impose tighter limits or prohibit it.",
                "source_urls": [
                    "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html",
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
            {
                "question": "What should I check in a Japanese condominium?",
                "answer": "Review the bylaws, recent meeting minutes, management budget, unpaid fees, management charges, repair-reserve balance, long-term repair plan, planned works, rental rules, and owner-use limits. Overseas owners should also decide who receives notices and acts locally.",
                "source_urls": [
                    "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
                ],
            },
            {
                "question": "What percentage should I add for closing costs?",
                "answer": "There is no reliable universal percentage. The exact amount depends on the asset, assessed value, buyer, seller, finance, advisers, tax relief, and date. Ask for a line-item estimate separating price, taxes, brokerage, registration, advice, remittance, ownership, and later sale costs.",
                "source_urls": [
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html",
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000072.html",
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000073.html",
                    "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000074.html",
                    "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf",
                ],
            },
        ],
        "primary_sources": [
            {
                "label": "Ministry of Finance — FEFTA reporting for a non-resident acquiring Japanese real property",
                "url": "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html",
            },
            {
                "label": "Ministry of Justice — mandatory inheritance and owner name/address registration",
                "url": "https://www.moj.go.jp/EN/MINJI/m_minji07_00004.html",
            },
            {
                "label": "Ministry of Justice — current owner name/address change registration guidance",
                "url": "https://www.moj.go.jp/MINJI/minji05_00693.html",
            },
            {
                "label": "MLIT — land-tax overview",
                "url": "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html",
            },
            {
                "label": "National Tax Agency — real-estate taxes for non-residents and foreign corporations",
                "url": "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf",
            },
            {
                "label": "MLIT — Japanese announcement of English real-estate transaction materials",
                "url": "https://www.mlit.go.jp/report/press/totikensangyo13_hh_000269.html",
            },
            {
                "label": "MLIT — flood hazard maps in the Important Matters Explanation",
                "url": "https://www.mlit.go.jp/totikensangyo/const/sosei_const_fr3_000074.html",
            },
            {
                "label": "MLIT and GSI — Hazard Map Portal Site",
                "url": "https://disaportal.gsi.go.jp/",
            },
            {
                "label": "MLIT Housing Bureau — Condominium Management in Japan for Foreign Building Unit Owners",
                "url": "https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf",
            },
            {
                "label": "Japan Tourism Agency — Private Lodging Business Act overview",
                "url": "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html",
            },
            {
                "label": "Ministry of Foreign Affairs — designated-activities long-stay visa",
                "url": "https://www.mofa.go.jp/ca/fna/page22e_000738.html",
            },
            {
                "label": "MLIT — English real-estate transaction materials",
                "url": "https://www.mlit.go.jp/en/report/press/totikensangyo13_hh_000003.html",
            },
            {
                "label": "MLIT — laws related to real-estate transactions in Japan",
                "url": "https://www.mlit.go.jp/common/001050448.pdf",
            },
            {
                "label": "MLIT — real property registration system",
                "url": "https://www.mlit.go.jp/common/001050449.pdf",
            },
            {
                "label": "MLIT — flow of real-estate transactions",
                "url": "https://www.mlit.go.jp/common/001050450.pdf",
            },
            {
                "label": "MLIT — taxes on land acquisition",
                "url": "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000072.html",
            },
            {
                "label": "MLIT — home-purchase cost and brokerage guidance",
                "url": "https://www.mlit.go.jp/sumai_literacy_pf/knowledge02/0005/",
            },
            {
                "label": "National Tax Agency — registration and licence tax rates for a home purchase",
                "url": "https://www.nta.go.jp/publication/pamph/koho/kurashi/html/05_1.htm",
            },
            {
                "label": "MLIT — taxes on holding land",
                "url": "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000073.html",
            },
            {
                "label": "MLIT — taxes on land transfers",
                "url": "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000074.html",
            },
            {
                "label": "Ministry of Justice — address evidence for overseas foreign registered owners",
                "url": "https://www.moj.go.jp/MINJI/minji05_00574.html",
            },
            {
                "label": "Ministry of Justice — ownership-registration applications from April 2024",
                "url": "https://www.moj.go.jp/MINJI/minji05_00589.html",
            },
            {
                "label": "Immigration Services Agency — immigration and residence status Q&A",
                "url": "https://www.moj.go.jp/isa/applications/guide/kanri_qa.html",
            },
            {
                "label": "Fukuoka City — real-estate ownership and residence or immigration status FAQ",
                "url": "https://www.city.fukuoka.lg.jp/keizai/k-yuchi/business/documents/english-faq.pdf",
            },
        ],
        "retirement_guide_slug": "japan-retirement-property-foreign-buyers",
    },
}


def get_foreign_buyer_country_guide(country_hub_slug: str) -> dict | None:
    guide = FOREIGN_BUYER_COUNTRY_GUIDES.get(country_hub_slug)
    return deepcopy(guide) if guide else None


def validate_foreign_buyer_country_guide(
    country_hub_slug: str,
    guide: dict,
    expected_destination_ids: list[str],
) -> None:
    missing = sorted(REQUIRED_GUIDE_KEYS - set(guide))
    if missing:
        raise ValueError(f"{country_hub_slug}: missing {', '.join(missing)}")
    missing_answers = sorted(REQUIRED_DIRECT_ANSWERS - set(guide["direct_answers"]))
    if missing_answers:
        raise ValueError(
            f"{country_hub_slug}: direct_answers missing {', '.join(missing_answers)}"
        )
    if set(guide["direct_answers"]) != REQUIRED_DIRECT_ANSWERS:
        raise ValueError(f"{country_hub_slug}: direct_answers must match required keys")
    for field in ("date_published", "date_reviewed"):
        value = guide[field]
        try:
            parsed_date = date.fromisoformat(value)
        except (TypeError, ValueError):
            parsed_date = None
        if parsed_date is None or parsed_date.isoformat() != value:
            raise ValueError(f"{country_hub_slug}: {field} must be a valid ISO date")
    if not isinstance(guide["retirement_guide_slug"], str) or not guide["retirement_guide_slug"].strip():
        raise ValueError(f"{country_hub_slug}: retirement_guide_slug is required")
    primary_source_urls = _validate_primary_sources(country_hub_slug, guide["primary_sources"])
    _validate_direct_answers(country_hub_slug, guide["direct_answers"], primary_source_urls)
    _validate_sourced_items(country_hub_slug, "eligibility_sections", guide["eligibility_sections"], primary_source_urls)
    _validate_sourced_items(country_hub_slug, "purchase_steps", guide["purchase_steps"], primary_source_urls)
    _validate_sourced_items(country_hub_slug, "ownership_rules", guide["ownership_rules"], primary_source_urls)
    _validate_sourced_items(country_hub_slug, "cost_rows", guide["cost_rows"], primary_source_urls)
    _validate_acquisition_example(
        country_hub_slug, guide["acquisition_example"], primary_source_urls
    )
    _validate_sourced_items(country_hub_slug, "faqs", guide["faqs"], primary_source_urls)
    for field in ("eligibility_sections", "ownership_rules", "buyer_checklist"):
        if not isinstance(guide[field], list) or not guide[field]:
            raise ValueError(f"{country_hub_slug}: {field} requires at least one item")
    missing_destinations = sorted(
        set(expected_destination_ids) - set(guide["destination_reads"])
    )
    if missing_destinations:
        raise ValueError(
            f"{country_hub_slug}: destination_reads missing {', '.join(missing_destinations)}"
        )
    if set(guide["destination_reads"]) != set(expected_destination_ids):
        raise ValueError(f"{country_hub_slug}: destination_reads must match destination_ids")
    for destination_id, destination_read in guide["destination_reads"].items():
        price_context = (
            destination_read.get("asking_price_context")
            if isinstance(destination_read, dict)
            else None
        )
        if not isinstance(price_context, str) or not price_context.strip():
            raise ValueError(
                f"{country_hub_slug}: destination_reads.{destination_id} requires asking_price_context"
            )
    _validate_engagement_links(country_hub_slug, guide["engagement_links"])
    if len(guide["purchase_steps"]) < 5:
        raise ValueError(f"{country_hub_slug}: purchase_steps requires at least five steps")
    if len(guide["cost_rows"]) < 4:
        raise ValueError(f"{country_hub_slug}: cost_rows requires at least four rows")
    _validate_coverage(country_hub_slug, "cost_rows", guide["cost_rows"], REQUIRED_COST_COVERAGE)
    _validate_coverage(
        country_hub_slug,
        "ownership_rules",
        guide["ownership_rules"],
        REQUIRED_OWNERSHIP_COVERAGE,
    )
    if len(guide["faqs"]) < 3:
        raise ValueError(f"{country_hub_slug}: faqs requires at least three questions")
    if not guide["primary_sources"]:
        raise ValueError(f"{country_hub_slug}: primary_sources is required")


def _validate_acquisition_example(
    country_hub_slug: str,
    example: dict,
    primary_source_urls: set[str],
) -> None:
    required = {"heading", "intro", "rows", "total", "caveat", "source_urls"}
    if not isinstance(example, dict):
        raise ValueError(f"{country_hub_slug}: acquisition_example must be an object")
    missing = sorted(required - set(example))
    if missing:
        raise ValueError(
            f"{country_hub_slug}: acquisition_example missing {', '.join(missing)}"
        )
    for field in ("heading", "intro", "total", "caveat"):
        if not isinstance(example[field], str) or not example[field].strip():
            raise ValueError(
                f"{country_hub_slug}: acquisition_example.{field} must be nonblank"
            )
    if not isinstance(example["rows"], list) or len(example["rows"]) < 4:
        raise ValueError(
            f"{country_hub_slug}: acquisition_example.rows requires at least four items"
        )
    for index, row in enumerate(example["rows"]):
        if not isinstance(row, dict) or set(row) != {"label", "amount", "note"}:
            raise ValueError(
                f"{country_hub_slug}: acquisition_example.rows[{index}] requires label, amount and note"
            )
        if any(not isinstance(row[key], str) or not row[key].strip() for key in row):
            raise ValueError(
                f"{country_hub_slug}: acquisition_example.rows[{index}] values must be nonblank"
            )
    _validate_source_urls(
        country_hub_slug,
        "acquisition_example",
        example["source_urls"],
        primary_source_urls,
    )


def _validate_engagement_links(country_hub_slug: str, links: list[dict]) -> None:
    if not isinstance(links, list) or len(links) != 2:
        raise ValueError(
            f"{country_hub_slug}: engagement_links requires exactly two links"
        )
    paths: set[str] = set()
    for index, link in enumerate(links):
        if not isinstance(link, dict) or set(link) != {"label", "href"}:
            raise ValueError(
                f"{country_hub_slug}: engagement_links[{index}] requires label and href"
            )
        if not isinstance(link["label"], str) or not link["label"].strip():
            raise ValueError(
                f"{country_hub_slug}: engagement_links[{index}] requires a nonblank label"
            )
        href = link["href"]
        if not isinstance(href, str) or not href.startswith("/") or href.startswith("//"):
            raise ValueError(
                f"{country_hub_slug}: engagement_links[{index}] requires an internal href"
            )
        paths.add(urlsplit(href).path)
    if paths != REQUIRED_ENGAGEMENT_PATHS:
        raise ValueError(
            f"{country_hub_slug}: engagement_links must link to the calculator and rankings"
        )


def _validate_primary_sources(country_hub_slug: str, primary_sources: list[dict]) -> set[str]:
    if not isinstance(primary_sources, list) or not primary_sources:
        raise ValueError(f"{country_hub_slug}: primary_sources is required")
    urls: set[str] = set()
    for index, source in enumerate(primary_sources):
        if not isinstance(source, dict) or not isinstance(source.get("label"), str) or not source["label"].strip():
            raise ValueError(f"{country_hub_slug}: primary_sources[{index}] requires a nonblank label")
        url = source.get("url")
        if not _is_valid_source_url(url):
            raise ValueError(f"{country_hub_slug}: primary_sources[{index}] requires a valid HTTPS URL")
        if url in urls:
            raise ValueError(f"{country_hub_slug}: primary_sources[{index}] URL must be unique")
        urls.add(url)
    return urls


def _validate_direct_answers(country_hub_slug: str, direct_answers: dict, primary_source_urls: set[str]) -> None:
    for key, answer in direct_answers.items():
        if not isinstance(answer, dict) or not answer.get("answer"):
            raise ValueError(f"{country_hub_slug}: direct_answers.{key} requires answer")
        if not answer.get("source_urls"):
            raise ValueError(f"{country_hub_slug}: direct_answers.{key} requires source_urls")
        _validate_source_urls(country_hub_slug, f"direct_answers.{key}", answer["source_urls"], primary_source_urls)
        _validate_contextual_link(
            country_hub_slug,
            f"direct_answers.{key}",
            answer,
            answer["answer"],
        )


def _validate_sourced_items(country_hub_slug: str, field: str, items: list[dict], primary_source_urls: set[str]) -> None:
    if not isinstance(items, list):
        raise ValueError(f"{country_hub_slug}: {field} must be a list")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{country_hub_slug}: {field}[{index}] must be an object")
        if not item.get("source_urls"):
            raise ValueError(f"{country_hub_slug}: {field}[{index}] requires source_urls")
        _validate_source_urls(country_hub_slug, f"{field}[{index}]", item["source_urls"], primary_source_urls)
        claim = item.get("body") or item.get("buyer_read") or item.get("answer") or ""
        _validate_contextual_link(
            country_hub_slug,
            f"{field}[{index}]",
            item,
            claim,
        )


def _validate_contextual_link(
    country_hub_slug: str,
    location: str,
    item: dict,
    claim: str,
) -> None:
    contextual_link = item.get("contextual_link")
    if contextual_link is None:
        return
    if not isinstance(contextual_link, dict) or set(contextual_link) != {"phrase", "url"}:
        raise ValueError(
            f"{country_hub_slug}: {location}.contextual_link requires phrase and URL"
        )
    phrase = contextual_link["phrase"]
    if not isinstance(phrase, str) or not phrase.strip() or phrase not in claim:
        raise ValueError(
            f"{country_hub_slug}: {location}.contextual_link phrase must appear in the claim"
        )
    if contextual_link["url"] not in item["source_urls"]:
        raise ValueError(
            f"{country_hub_slug}: {location}.contextual_link URL must be registered for that claim"
        )


def _validate_source_urls(
    country_hub_slug: str,
    location: str,
    source_urls: list[str],
    primary_source_urls: set[str],
) -> None:
    if not isinstance(source_urls, list) or not source_urls:
        raise ValueError(f"{country_hub_slug}: {location} requires source_urls")
    for index, url in enumerate(source_urls):
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"{country_hub_slug}: {location}.source_urls[{index}] must be a nonblank URL string")
        if not _is_valid_source_url(url):
            raise ValueError(f"{country_hub_slug}: {location}.source_urls[{index}] must be a valid HTTPS URL")
        if url not in primary_source_urls:
            raise ValueError(f"{country_hub_slug}: {location}.source_urls[{index}] is not registered in primary_sources")


def _is_valid_source_url(url: object) -> bool:
    if not isinstance(url, str) or not url or url != url.strip() or "\\" in url:
        return False
    if any(unicodedata.category(character).startswith("C") or character.isspace() for character in url):
        return False
    if re.search(r"%(?![0-9A-Fa-f]{2})", url):
        return False
    try:
        decoded_url = unquote_to_bytes(url).decode("utf-8")
    except UnicodeDecodeError:
        return False
    if any(unicodedata.category(character).startswith("C") for character in decoded_url):
        return False
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
    except ValueError:
        return False
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or ":" in parsed.netloc
        or parsed.netloc.casefold() != hostname.casefold()
    ):
        return False
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        labels = hostname.split(".")
        if len(hostname) > 253 or any(
            not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
            for label in labels
        ) or not re.fullmatch(r"[A-Za-z]{2,63}", labels[-1]):
            return False
    else:
        return False
    return True


def _validate_coverage(
    country_hub_slug: str,
    field: str,
    items: list[dict],
    categories: dict[str, tuple[str, ...]],
) -> None:
    text = " ".join(
        str(value).lower()
        for item in items
        for value in item.values()
        if isinstance(value, str)
    )
    for category, terms in categories.items():
        if not any(term in text for term in terms):
            raise ValueError(f"{country_hub_slug}: {field} missing {category} coverage")
