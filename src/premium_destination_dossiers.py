"""Editorial specifications for destination dossiers using the premium renderer."""

from dataclasses import dataclass, fields


DECISION_DIMENSION_KEYS = {
    "lifestyle_magnetism",
    "global_access",
    "ownership_clarity",
    "regulatory_safety",
    "rental_profit",
    "capital_upside",
    "retirement_fit",
    "exit_liquidity",
    "foreigner_fit",
    "value_entry",
}


@dataclass(frozen=True)
class DossierLens:
    heading: str
    dimension_keys: tuple[str, str]
    paragraphs: tuple[str, ...]
    image_key: str | None = None


@dataclass(frozen=True)
class DossierImage:
    key: str
    src: str
    alt: str
    caption: str
    placement_class: str


@dataclass(frozen=True)
class PremiumDossierSpec:
    destination_id: str
    title: str
    description: str
    h1: str
    lede: str
    author: str
    date_published: str
    date_reviewed: str
    verdict_paragraphs: tuple[str, ...]
    lenses_intro: str
    lenses: tuple[DossierLens, ...]
    score_reads: dict[str, str]
    micro_locations_intro: str
    micro_locations: tuple[dict[str, str], ...]
    checklist: tuple[str, ...]
    references_intro: str
    references: tuple[dict[str, str], ...]
    images: tuple[DossierImage, ...]
    nav_items: tuple[tuple[str, str], ...]


FUKUOKA_ITOSHIMA_DOSSIER = PremiumDossierSpec(
    destination_id="fukuoka-itoshima",
    title="Fukuoka and Itoshima Retirement Property Dossier",
    description="Assess Fukuoka and Itoshima retirement property through daily life, access, foreign ownership, rental rules, value, resale, hazards, and representative listings.",
    h1="Fukuoka / Itoshima: city ease, coast within reach",
    lede=(
        "Fukuoka / Itoshima is the Atlas’s strongest Japanese proposition for a buyer who wants a home to work on ordinary weekdays, not only on holidays. Fukuoka supplies hospitals, rail, an unusually close airport, food and a large resident economy; Itoshima adds beaches, fields and a slower rhythm west of the city. The pairing is compelling, but it is not interchangeable. A station-area apartment, a Maebaru house and a car-dependent coastal home solve different retirement problems and carry different hazard, maintenance and resale risks."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-21",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is positive with one controlling condition: establish a credible right to live in Japan before treating the property as a retirement home. Foreigners can generally acquire Japanese real estate, but a deed does not create residence status, public-healthcare eligibility or domestic borrowing access. Japan has no general retirement visa. The official designated-activities route for long sightseeing permits six months and may be extended to a maximum of one year for eligible applicants, but it requires substantial savings, private medical travel insurance and does not accept dependent children. Fukuoka City also says that people staying under the sightseeing-and-recreation form of designated activities cannot join its National Health Insurance. A buyer planning full-time retirement therefore needs a different, renewable residence basis confirmed before purchase.",
        "Subject to that constraint, Fukuoka / Itoshima suits a buyer who values safe, service-rich daily life more than trophy scarcity or aggressive yield. It is especially credible for someone comfortable using Japanese professional help, willing to separate Fukuoka’s urban convenience from Itoshima’s coastal logistics, and prepared to own a home for personal utility even if short-term rental income disappoints. It is weaker for anyone who expects the purchase to solve immigration, needs high non-resident leverage, refuses car dependence but wants a remote beach setting, or requires a simple absentee rental business.",
        "Proceed in this order: confirm residence and healthcare; decide whether daily life is urban, rail-oriented Itoshima or coastal and car-led; obtain written financing and total-cost assumptions; then investigate the exact title, building, management regime, permitted use and hazards. The combination can work unusually well, but only when the city-and-coast idea is translated into a specific address and a realistic operating plan."
    ),
    lenses_intro=(
        "The Atlas groups the decision into five paired lenses. The prose below explains what the evidence means for a buyer; the complete ten-dimension assessment appears once in the score table that follows."
    ),
    lenses=(
        DossierLens(
            "Live well between city and coast",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Fukuoka makes a credible retirement base because the things that become more important with age are part of the ordinary city rather than a resort overlay. Groceries, restaurants, neighbourhood clinics, larger hospitals, parks and frequent public transport are embedded in a city of roughly 1.67 million people. Food and waterfront access are genuine lifestyle advantages, but the stronger point is repeatability: the city remains useful in rain, winter and shoulder season. Fukuoka City also operates a medical interpreting call centre with round-the-clock support in 20 languages, a meaningful practical aid even though it is not a substitute for insurance, a regular doctor or Japanese-language help with administration.",
                "Itoshima changes the texture. Around Maebaru and the JR Chikuhi Line, a buyer can retain rail access and town services while reaching the coast by car or bus. Farther north and west, the appeal becomes space, sea, cafés, farm shops and a quieter landscape. That appeal comes with more driving, less frequent public transport and greater variation in nearby medical and household services. Itoshima City’s own transport material describes buses and community services designed partly to reduce areas with poor public-transport access. That is useful infrastructure, but it is also a warning not to equate a scenic listing with an easy car-free retirement.",
                "Test the preferred pattern in the least flattering conditions. Spend ordinary weekdays in the hottest and wettest period, make the grocery and hospital journeys, and return after dark. In Fukuoka, check noise, summer heat, building management and the walk to transit. In Itoshima, check road width, parking, drainage, salt exposure, internet, waste collection and whether essential trips remain manageable if one household member cannot drive. The destination scores well because it offers choices; retirement fit depends on choosing the one that remains workable year after year."
            ),
            "city-access",
        ),
        DossierLens(
            "Reach Fukuoka easily—and integrate beyond the airport",
            ("global_access", "foreigner_fit"),
            (
                "Fukuoka Airport is a structural advantage. Its domestic terminal is connected directly to the subway; the airport states that Hakata is about five minutes away and Tenjin about ten. That compresses the tiring final leg of a journey and makes domestic connections practical. The international terminal is not on the subway and requires a free terminal shuttle, an important detail for a buyer comparing brochure-level access with door-to-door travel. From central Fukuoka, rail also connects west toward Meinohama, Maebaru and parts of Itoshima, so the urban side of the proposition can function without a car.",
                "The advantage fades by degrees as the address moves away from the rail spine. Maebaru has a real town centre and station; many celebrated coastal pockets do not. Itoshima City publishes conventional, community and on-demand bus information, and its official access guidance identifies the Chikuhi Line and local bus network. Those services support daily life but should not be treated as metro-frequency substitutes. For a coastal house, calculate the whole journey from the front door to the airport, hospital and supermarket, including a missed connection, bad weather and luggage. A 40-kilometre map radius is not a lifestyle measure.",
                "Foreigner fit is similarly two-sided. Fukuoka has multilingual municipal support, medical interpretation, universities, international business and an airport accustomed to regional travel. Yet purchase documents, tax notices, condominium meetings, contractor coordination and rural neighbour relationships may still operate in Japanese. Non-resident property reporting to the Ministry of Finance is submitted in Japanese, and the practical burden of managing notices continues after closing. Budget for an independent bilingual lawyer, tax adviser and reliable local contact. Integration is strongest when the buyer uses the city’s international accessibility as a bridge into local systems, not as evidence that those systems can be ignored."
            ),
        ),
        DossierLens(
            "Own clearly, then operate locally",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Japan’s ownership framework is the cleanest part of the case: nationality is not in itself a general bar to acquiring and registering ordinary real estate. But clean title access is only the opening check. A non-resident acquisition can trigger post-transaction reporting under the Foreign Exchange and Foreign Trade Act; the Ministry of Finance says the report is generally due through the Bank of Japan within 20 days. National and local taxes arise on acquisition, during ownership and on disposal, while non-resident rental or sale income can require Japanese filings, withholding and a tax agent. These are manageable obligations when assigned in writing before closing.",
                "The property-level work is less uniform. For an apartment, read the management bylaws, reserve fund, arrears, major-repair plan, minutes, insurance, pet and renovation rules, and any restriction on lodging use. For a detached home, verify boundaries, legal road access, utilities, extensions, construction records, termite and moisture condition, retaining walls and the cost of insuring and maintaining an often lightly documented asset. In coastal Itoshima, salt, wind, drainage and vacant-period management deserve explicit inspection. A low asking price may reflect land value, age or deferred work rather than a bargain.",
                "Hazard diligence must be address-specific. Fukuoka City’s combined maps cover flood, inland-water, landslide, storm-surge, shaking, tsunami and reservoir risks; Itoshima publishes disaster, reservoir, mountain and coastal hazard material. National rules require water-risk map information in the important-matters explanation, but the official guidance also warns that being outside a mapped inundation zone does not mean zero risk. Overlay the latest municipal maps, visit after heavy rain where possible, confirm evacuation access and obtain an insurance quotation before the offer becomes binding. Regulatory safety here comes from disciplined local verification, not from the national ownership rule alone."
            ),
        ),
        DossierLens(
            "Separate ordinary demand from a rental story",
            ("rental_profit", "capital_upside"),
            (
                "Fukuoka’s financial case should begin with ordinary residential demand. The city’s official statistics show a large and growing population, while the airport, universities, employment base and compact urban form support a broad pool of residents. That does not guarantee rent or appreciation, but it is a more durable foundation than assuming every attractive home can become a high-yield holiday rental. A practical apartment near transit should be compared with long-term rents, vacancy, management fees and eventual owner-occupier resale before any tourist upside is added.",
                "Itoshima requires a sharper split. Maebaru and rail-served neighbourhoods participate more directly in the Fukuoka commuter and local-resident economy. A distinctive coastal house may appeal to second-home buyers and visitors but can face seasonal demand, higher cleaning and management costs, limited nearby operators and a thinner resale pool. The Private Lodging Business Act caps the national minpaku route at 180 nights per year, permits tighter local rules and requires an absent owner to entrust specified duties to a registered administrator. Hotel or inn licensing is a different route. Condominium rules and planning controls can narrow the answer further.",
                "Treat rental income as an operating business, not a property characteristic. Before underwriting it, identify the legal route, confirm the exact premises qualify, obtain written local and building approval, price professional management, and model tax, utilities, cleaning, consumables, platform fees, repairs and empty periods. Then compare the result with a long-term tenancy and with no rent at all. Capital upside should likewise be framed as a scenario, not a promise: Fukuoka’s population and infrastructure are supportive; Itoshima’s scarcity and lifestyle recognition may help selected assets; neither rescues an overpaid, poorly accessed or non-compliant property."
            ),
            "seaside-life",
        ),
        DossierLens(
            "Enter with discipline and preserve the exit",
            ("value_entry", "exit_liquidity"),
            (
                "Fukuoka / Itoshima offers several entry points, which is more useful than a single average. An older apartment can provide low-cost access to services but may carry weak reserves or a dated building. A newer house around Maebaru can offer practical space yet needs location and resale testing. A renovated or newly built coastal home can command a substantial lifestyle premium. The representative listings below are asking-price observations, not valuations; they illustrate dispersion rather than establish market value. Compare each candidate with completed transactions in the Ministry of Land’s Real Estate Information Library and commission a property-specific assessment.",
                "Value entry is created by matching price to the buyer pool that will exist on exit. Central Fukuoka and established station areas generally offer more potential resident demand, but entry prices and competition can be higher. Meinohama and the western corridor may balance access and space. Maebaru is easier to explain to a year-round household than an isolated coast road. A singular sea-view house may be emotionally liquid and financially illiquid: the eventual buyer must share the taste, budget, maintenance tolerance and transport assumptions. Do not pay a city-level price for a property with a narrow rural exit.",
                "Model five-year cash outlay rather than purchase price alone. Include brokerage and legal support, registration and acquisition taxes, financing costs, insurance, management, condominium contributions, repairs, equipment replacement, currency movements and sale costs. For a non-resident, add local representation and tax administration. Before exchange, ask two agents who did not source the property how they would resell it, to whom and at what evidence-based range. The best Fukuoka / Itoshima purchase is not necessarily the cheapest or most scenic; it is the asset whose daily utility, carrying cost and future buyer pool remain aligned."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Fukuoka combines food, waterfront and year-round city life; Itoshima adds beaches and space, with a more car-dependent rhythm.",
        "global_access": "Fukuoka Airport reaches Hakata in about five minutes by subway, while coastal Itoshima adds meaningful last-mile time and transport risk.",
        "ownership_clarity": "Fukuoka and Itoshima follow Japan’s generally open foreign-ownership framework, but non-resident reporting, tax administration and Japanese-language professional support remain necessary.",
        "regulatory_safety": "Fukuoka and Itoshima require address-level hazard review; short-stay use also faces the 180-night national cap, local rules and building restrictions.",
        "rental_profit": "Fukuoka has broad long-term residential demand; Itoshima coastal rentals face greater seasonality, management cost, operator dependence and a thinner evidence base.",
        "capital_upside": "Fukuoka’s population and infrastructure support the case, while Itoshima appreciation is more asset-selective and should not be treated as guaranteed.",
        "retirement_fit": "Fukuoka offers hospitals, transit and daily services, but legal residence must precede public-healthcare access; remote Itoshima increases driving dependence.",
        "exit_liquidity": "Fukuoka’s urban and rail-served homes reach a broader buyer pool; singular or isolated Itoshima coastal houses can take longer to resell.",
        "foreigner_fit": "Fukuoka provides multilingual support and strong regional access, but property documents, tax notices and ongoing Itoshima management may still operate in Japanese.",
        "value_entry": "Fukuoka apartments, Maebaru houses and premium Itoshima coastal homes span very different price points, maintenance burdens and future buyer pools.",
    },
    micro_locations_intro=(
        "The useful comparison is not Fukuoka versus Itoshima in the abstract. It is a progression from fully urban and transit-led living to lower-density coastal living. Boundaries below are decision aids rather than price zones; confirm the exact address, school district, planning designation, hazard layers and transport timetable."
    ),
    micro_locations=(
        {"name": "Central Fukuoka", "best_for": "City services", "daily_life": "Urban and transit-led", "diligence": "Building and neighbourhood rules"},
        {"name": "Meinohama corridor", "best_for": "City-coast balance", "daily_life": "Connected western base", "diligence": "Station access and local hazards"},
        {"name": "Maebaru", "best_for": "Practical Itoshima life", "daily_life": "Town services with rail access", "diligence": "Exact walkability and building condition"},
        {"name": "Itoshima coast", "best_for": "Lower-density coastal living", "daily_life": "Car-led and seasonal", "diligence": "Hazards, access and maintenance"},
    ),
    checklist=(
        "Establish the residence and healthcare route.",
        "Confirm financing and the total cash requirement.",
        "Choose the urban or coastal daily-life pattern.",
        "Verify title, planning, condition, governance and access.",
        "Review every site-specific hazard.",
        "Confirm intended rental use and operating rules.",
        "Price maintenance, management, tax, insurance and currency exposure.",
        "Test resale demand before making a binding offer.",
    ),
    references_intro=(
        "Substantive legal, administrative, access, health and hazard claims were reviewed on 21 August 2026 against the official sources below. Rules, municipal maps, transport and listing availability can change. Recheck the current source and obtain Japanese legal, tax, immigration, building and insurance advice for the exact buyer and property before signing. Listing observations are dated asking-price evidence only; they do not verify availability, title, condition, negotiability or completed value."
    ),
    references=(
        {"label": "Japan retirement property guide", "url": "/japan-retirement-property-foreign-buyers/"},
        {"label": "Ministry of Foreign Affairs: designated activities for long sightseeing and recreation", "url": "https://www.mofa.go.jp/ca/fna/page22e_000738.html"},
        {"label": "Ministry of Finance: non-resident real-property reporting under FEFTA", "url": "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html"},
        {"label": "National Tax Agency: non-residents buying, renting or selling Japanese real estate", "url": "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf"},
        {"label": "Ministry of Land: taxes when buying, holding and selling land", "url": "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html"},
        {"label": "Ministry of Land: water-hazard maps in the important-matters explanation", "url": "https://www.mlit.go.jp/totikensangyo/const/sosei_const_fr3_000074.html"},
        {"label": "Ministry of Land: Real Estate Information Library", "url": "https://www.reinfolib.mlit.go.jp/"},
        {"label": "Japan Tourism Agency: Private Lodging Business Act", "url": "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html"},
        {"label": "Fukuoka Airport: official access guidance", "url": "https://www.fukuoka-airport.jp/en/access/"},
        {"label": "Fukuoka City: population and municipal statistics", "url": "https://www.city.fukuoka.lg.jp/shisei/toukei/index.html"},
        {"label": "Fukuoka City: National Health Insurance eligibility", "url": "https://www.city.fukuoka.lg.jp/hofuku/kokuho/hp/seido/03.html"},
        {"label": "Fukuoka City: multilingual medical support", "url": "https://www.city.fukuoka.lg.jp/hofuku/chiikiiryo/health/medical_facilities.html"},
        {"label": "Fukuoka City: comprehensive hazard maps", "url": "https://webmap.city.fukuoka.lg.jp/bousai/c_webmap.html"},
        {"label": "Itoshima City: disaster and coastal hazard maps", "url": "https://www.city.itoshima.lg.jp/li/kurashi/090/010/030/"},
        {"label": "Itoshima City: public transport and bus information", "url": "https://www.city.itoshima.lg.jp/li/kurashi/120/020/"},
        {"label": "Itoshima City: current city-planning map", "url": "https://www.city.itoshima.lg.jp/s021/020/010/020/010/tokeizu-h280914.html"},
    ),
    images=(
        DossierImage("coast", "/assets/fukuoka-itoshima-coast.webp", "Fukuoka and Itoshima coastline", "City access meets the Itoshima coast.", "hero"),
        DossierImage("city-access", "/assets/fukuoka-itoshima-city-access.webp", "Everyday urban access in Fukuoka", "Fukuoka provides the practical urban base.", "wide"),
        DossierImage("seaside-life", "/assets/fukuoka-itoshima-seaside-life.webp", "Everyday seaside life in Itoshima", "Coastal life requires a closer look at access and seasonality.", "wide"),
    ),
    nav_items=(
        ("verdict", "Verdict"),
        ("lenses", "Five destination lenses"),
        ("scores", "Atlas assessment"),
        ("listings", "Representative listings"),
        ("locations", "Where to look"),
        ("checklist", "Buyer checklist"),
        ("sources", "References"),
    ),
)


PREMIUM_DESTINATION_DOSSIERS = {
    FUKUOKA_ITOSHIMA_DOSSIER.destination_id: FUKUOKA_ITOSHIMA_DOSSIER,
}


def get_premium_dossier(destination_id: str) -> PremiumDossierSpec | None:
    return PREMIUM_DESTINATION_DOSSIERS.get(destination_id)


def validate_premium_dossier(spec: PremiumDossierSpec) -> None:
    if spec.destination_id != "fukuoka-itoshima":
        raise ValueError("premium dossier is registered for the wrong destination")

    for field in fields(spec):
        value = getattr(spec, field.name)
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{field.name} must not be empty")

    if len(spec.lenses) != 5:
        raise ValueError("premium dossier must contain five lenses")
    dimension_keys = [key for lens in spec.lenses for key in lens.dimension_keys]
    if len(dimension_keys) != len(set(dimension_keys)) or set(dimension_keys) != DECISION_DIMENSION_KEYS:
        raise ValueError("lenses must cover every decision dimension exactly once")
    for lens in spec.lenses:
        if not lens.heading.strip() or not lens.paragraphs or any(not paragraph.strip() for paragraph in lens.paragraphs):
            raise ValueError("every lens requires a heading and non-empty paragraphs")

    if set(spec.score_reads) != DECISION_DIMENSION_KEYS:
        raise ValueError("premium dossier requires one research read for every decision dimension")
    if any(not research_read.strip() for research_read in spec.score_reads.values()):
        raise ValueError("premium dossier research reads must not be empty")

    if len(spec.nav_items) > 7:
        raise ValueError("premium dossier navigation may contain at most seven items")
    if not spec.nav_items or spec.nav_items[-1][0] != "sources":
        raise ValueError("references must be the final navigation item")

    if len(spec.images) != 3:
        raise ValueError("premium dossier must contain exactly three images")
    image_keys = [image.key for image in spec.images]
    image_paths = [image.src for image in spec.images]
    if len(image_keys) != len(set(image_keys)) or len(image_paths) != len(set(image_paths)):
        raise ValueError("premium dossier images must be unique")
    if any(not image.alt.strip() for image in spec.images):
        raise ValueError("premium dossier images require alt text")

    if len(spec.micro_locations) < 3:
        raise ValueError("premium dossier requires at least three micro-locations")
    if not 6 <= len(spec.checklist) <= 8:
        raise ValueError("premium dossier checklist must contain six to eight items")
    if not spec.references:
        raise ValueError("premium dossier requires references")


validate_premium_dossier(FUKUOKA_ITOSHIMA_DOSSIER)
