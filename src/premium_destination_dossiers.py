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
class DossierOrientationGroup:
    label: str
    stops: tuple[tuple[str, str], ...]


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
    market_anchors: tuple[dict[str, str], ...]
    micro_locations_intro: str
    micro_locations: tuple[dict[str, str], ...]
    checklist: tuple[str, ...]
    references_intro: str
    references: tuple[dict[str, str], ...]
    images: tuple[DossierImage, ...]
    nav_items: tuple[tuple[str, str], ...]
    lenses_heading: str
    assessment_intro: str
    listings_intro: str
    market_anchors_intro: str
    orientation_groups: tuple[DossierOrientationGroup, ...]
    orientation_caption: str
    country_guide_url: str
    country_guide_label: str
    rail_comparison: str


FUKUOKA_ITOSHIMA_DOSSIER = PremiumDossierSpec(
    destination_id="fukuoka-itoshima",
    title="Fukuoka and Itoshima Retirement Property Dossier",
    description="Assess Fukuoka and Itoshima retirement property through daily life, access, foreign ownership, rental rules, value, resale, hazards, and representative listings.",
    h1="Fukuoka / Itoshima: city ease, coast within reach",
    lede=(
        "Fukuoka / Itoshima is Japan’s clearest city-and-coast retirement proposition. Fukuoka offers hospitals, rail, an airport minutes from downtown and a deep resident economy; Itoshima adds beaches, fields and a slower rhythm. The choice is not interchangeable: a station-area apartment, a Maebaru house and a car-dependent coastal home deliver different daily lives, maintenance burdens and resale prospects. This dossier shows where each pattern works—and where the romance needs harder diligence."
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
    market_anchors=(
        {
            "location": "Imashuku station catchment",
            "evidence": "121,700–132,400 JPY/m²",
            "buyer_read": "Four normal land comparables in the 2026 MLIT appraisal; the same report places a typical new-build house at about 35–45 million JPY.",
            "source_label": "MLIT 2026 appraisal",
            "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/40/2026401350006.html",
        },
        {
            "location": "Eastern Itoshima / Takata",
            "evidence": "82,900–108,500 JPY/m²",
            "buyer_read": "Four normal land comparables used in the 2025 MLIT appraisal, with the standard residential site assessed at 96,000 JPY/m².",
            "source_label": "MLIT 2025 appraisal",
            "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2025/40/2025402300001.html",
        },
        {
            "location": "Outer Itoshima / Shima and Nijo",
            "evidence": "7,720–41,400 JPY/m²",
            "buyer_read": "Selected 2025 residential land benchmarks show how sharply value changes with rail access, settlement and coastal position.",
            "source_label": "Fukuoka Prefecture 2025 land survey",
            "source_url": "https://www.pref.fukuoka.lg.jp/uploaded/life/792986_62689081_misc.pdf",
        },
    ),
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
        {"label": "Ministry of Land: 2026 Imashuku appraisal and comparable land evidence", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/40/2026401350006.html"},
        {"label": "Ministry of Land: 2025 eastern Itoshima appraisal and comparable land evidence", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2025/40/2025402300001.html"},
        {"label": "Fukuoka Prefecture: 2025 land-price survey", "url": "https://www.pref.fukuoka.lg.jp/uploaded/life/792986_62689081_misc.pdf"},
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
    lenses_heading="Fukuoka / Itoshima through five destination lenses",
    assessment_intro="Here’s how Fukuoka / Itoshima scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three observations show the spread between a practical western-Fukuoka apartment, an Itoshima lifestyle house and a higher-end coastal asset. Local asking price is primary; USD uses the recorded dataset exchange basis.",
    market_anchors_intro="These figures are land evidence—not finished-home prices. They provide a public-market check on the asking listings above and must still be matched for location, building, age and condition.",
    orientation_groups=(
        DossierOrientationGroup(
            "City to coast",
            (
                ("Central Fukuoka", "Urban and transit-led"),
                ("Meinohama corridor", "Connected western base"),
                ("Maebaru", "Town services with rail access"),
                ("Itoshima coast", "Car-led and seasonal"),
            ),
        ),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm the exact route and timetable for every address.",
    country_guide_url="/japan-retirement-property-foreign-buyers/",
    country_guide_label="Japan retirement property guide",
    rail_comparison="Compare Fukuoka / Itoshima with the full Atlas.",
)


ALGARVE_CASCAIS_DOSSIER = PremiumDossierSpec(
    destination_id="algarve-cascais",
    title="Algarve and Cascais Retirement Property Dossier",
    description="Assess Algarve and Cascais retirement property through daily life, access, ownership, residence, rental rules, climate risk, value, resale, and current listings.",
    h1="Algarve / Cascais: two Portuguese coasts, two ownership lives",
    lede=(
        "Algarve / Cascais is a comparison, not a single market. Cascais is a premium Atlantic town tied to Lisbon’s jobs, hospitals, airport and rail network. The Algarve is a long southern region whose eastern towns, central airport corridor and western coast produce different daily routines and buyer pools. Both can support an excellent retirement home; neither should be bought on sunshine alone. The address, residence route, municipal rules and year-round operating plan decide whether the promise survives ordinary life."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is positive for a lifestyle-led buyer who values liveability, established international communities and clear purchase mechanics more than high yield. Cascais is the stronger all-season, low-friction base: Lisbon Airport, major hospitals, urban culture and professional services are within the wider metropolitan system, while the Cascais rail line supports a recognisable car-light pattern. The Algarve offers more geographic and price choice, warmer winters and a deeper holiday-home ecosystem, but the practical answer changes markedly between Faro and Loulé, Tavira in the east, and Lagos in the west. Treating those places as substitutes is the fastest way to misprice access, seasonality and future resale.",
        "One condition sits above the property decision: ownership is not residence. Portugal’s current investment-residence page lists routes such as job creation, research, cultural support and qualifying investment funds; buying an ordinary home is not listed as a qualifying route. A deed can help prove accommodation within a valid residence application, but it does not itself create permission to live in Portugal or automatic access to the National Health Service. Confirm the buyer’s residence basis, tax position and healthcare registration sequence before using a second-home purchase as a retirement plan.",
        "Proceed if the home works without tourist rent, the preferred town remains useful outside summer, and the household accepts the location’s real transport pattern. Look elsewhere if the investment needs aggressive short-stay income, a property-created visa, low entry pricing in a prime coastal district, or effortless car-free living in a dispersed Algarve resort. The strongest purchase is usually an established, legally documented home near the services the buyer will use weekly—not the most dramatic view at the edge of the map."
    ),
    lenses_intro=(
        "The five lenses below pair the Atlas’s ten scoring dimensions and keep the decision in buyer language. Each lens contrasts Cascais with the relevant Algarve submarkets; the complete ten-factor assessment appears once in the score table."
    ),
    lenses=(
        DossierLens(
            "Choose the life that still works in February",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Cascais offers the most complete urban-coastal retirement pattern in this dossier. The town has beaches, a walkable centre, restaurants and an established international community, but its deeper advantage is proximity to the Lisbon metropolitan economy. Groceries, pharmacies, private clinics, rail services and everyday administration do not disappear after the holiday season. The trade-off is price: buyers pay for that repeatability, and quieter villas beyond the rail-served core can still create driving and maintenance dependence.",
                "The Algarve is not one lifestyle. Faro and Loulé provide the broadest year-round service base and the shortest relationship with Faro Airport. Tavira offers a slower eastern-Algarve rhythm, a real town centre and access to the Ria Formosa, while Lagos combines a functioning western town with the scenery and visitor economy that make the region internationally legible. Resort belts and isolated villas can be pleasant, but winter closures, summer congestion, heat, garden care and the distance to routine healthcare become more important than a sea view after the first month.",
                "Healthcare follows residence and registration. Portugal’s health regulator says a foreign resident with a valid residence permit can have the National Register of Users updated so eligible SNS care is assigned under the public system; incomplete documentation can leave the patient financially responsible. Test the preferred base in winter and peak summer, walk to food and pharmacy, make a trial journey to the likely hospital, and ask what happens when one household member no longer drives. Cascais scores highest for repeatable convenience; Algarve retirement fit is strongest in established towns with services rather than seasonal compounds."
            ),
            "tavira-life",
        ),
        DossierLens(
            "Measure the whole journey, then the integration work",
            ("global_access", "foreigner_fit"),
            (
                "Cascais uses Lisbon as its gateway. Lisbon Airport’s official guidance places the airport within the capital’s metro and public-transport system, but Cascais still requires a transfer to rail, taxi or road. The railway is valuable because it links central Cascais and Estoril with Lisbon’s western waterfront, yet door-to-door travel depends on the exact walk, luggage, interchange and time of day. A listing described as ‘near Lisbon’ should be tested from the front door to the terminal rather than measured as a straight line.",
                "Faro Airport is the Algarve gateway, but the last mile expands quickly. Faro and central Algarve locations have the simplest airport relationship. Tavira is east of the airport and can support town-based living, while Lagos lies far to the west and turns a nominally convenient regional airport into a longer road or coach journey. Rail serves parts of the Algarve, but many coastal homes, golf developments and daily errands remain car-led. Calculate airport, supermarket and hospital trips separately; one access score cannot describe every address along a coast more than 150 kilometres long.",
                "English is widely used in both markets, especially in property and tourism, but the legal and operating environment remains Portuguese. Tax registration, title and land-registry work, condominium minutes, municipal planning, insurance claims and contractor coordination need reliable local interpretation. Cascais has the larger Lisbon professional-services pool; the Algarve has mature foreign-buyer networks but more variation between municipalities and operators. Foreigner friendliness is an advantage, not a substitute for an independent lawyer, tax adviser and surveyor who owe duties to the buyer rather than the selling chain."
            ),
        ),
        DossierLens(
            "Buy clearly—and verify the exact permitted use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Portugal’s transaction framework is comparatively legible. The government’s property guide identifies the tax number, land-registry certificate, tax record, use licence, energy certificate and building technical file among the documents used in a purchase. The Tax Authority states that IMT is charged on the higher of the contractual price and taxable patrimonial value, with stamp duty generally charged at 0.8 percent; annual urban-property IMI is normally set by municipalities within a statutory range, and higher-value holdings may also enter AIMI. Obtain a buyer-specific completion statement instead of applying one headline percentage.",
                "Clear acquisition does not mean every building or use is simple. For an apartment in Cascais, Estoril, Faro, Tavira or Lagos, read condominium bylaws, recent minutes, arrears, insurance, reserve position and major works. For a villa, reconcile the registered areas with the physical building, licences, extensions, pool and outbuildings; check boundaries, access, utilities and whether renovation constraints apply. Coastal position adds salt, wind and moisture, while low-density Algarve plots can add private roads, boreholes, septic systems, gardens and expensive vacant-period supervision.",
                "Short-stay operation is property- and municipality-specific. Portugal’s current Alojamento Local guide describes registration by prior communication and allows municipal opposition periods that lengthen in containment areas; national amendments restored meaningful municipal control. Condominium and planning constraints can further narrow the answer, and Loulé began a municipal process for sustainable local-accommodation management in 2025. Do not underwrite tourist rent until the municipality, building documents and condominium position have been checked in writing. Climate diligence belongs in the same file: civil-protection material identifies drought exposure in the Algarve, while flood, wildfire, coastal erosion and extreme heat must be checked address by address."
            ),
        ),
        DossierLens(
            "Separate a durable home from a seasonal business",
            ("rental_profit", "capital_upside"),
            (
                "Cascais has the broader resident-demand story. Its connection to Lisbon, international schools, services and a high-income owner-occupier pool can support long-term demand and resale, although a high purchase price compresses yield. An apartment near the rail line and town services should first be tested against a conventional tenancy, condominium costs and owner-occupier resale. Holiday demand is an optional operating case only after municipal and building approval—not the base case that makes an expensive acquisition work.",
                "The Algarve has a deep visitor economy, but gross booking revenue is not net return. Faro and Loulé can draw from year-round employment and services; Tavira and Lagos mix residents, second-home owners and tourists in different proportions. A managed villa adds cleaning, pool and garden care, utilities, platform fees, local representation, maintenance, insurance and empty periods. Peak summer can look persuasive while winter occupancy, licence restrictions and owner-use dates weaken the annual result. Model long-term rent, compliant short-stay operation and zero rent as three separate cases.",
                "Capital upside should be tied to scarcity that future buyers can understand. Cascais has metropolitan depth and a globally legible name, but the entry premium already reflects much of that quality. Established Algarve towns and proven coastal districts may retain international appeal, yet new supply, water constraints, climate adaptation costs and a thinner buyer pool can change the exit. Do not treat Portugal’s past price growth as a forecast. The asset must still make sense at today’s completed-sale evidence, today’s carrying cost and a conservative resale timetable."
            ),
            "lagos-coast",
        ),
        DossierLens(
            "Enter at the right local price—and protect the exit",
            ("value_entry", "exit_liquidity"),
            (
                "Official completed-sale medians show why one Portugal-wide price is unhelpful. Statistics Portugal’s 2025 housing publication reports materially different municipal levels for Cascais, Loulé and Lagos, while an individual home can sit well above or below its municipality depending on precise street, view, age, condition and legal documentation. The three listing observations below are current asking examples, not valuations. Their purpose is to expose the spread between a Cascais apartment, an eastern-Algarve town apartment and a western-Algarve detached house.",
                "Liquidity follows buyer-pool breadth. A well-located Cascais or Estoril apartment can appeal to local professionals, international residents, downsizers and second-home buyers. Central Algarve homes near services and the airport have a different but still explainable pool. Tavira attracts buyers who value town character and the eastern coast; Lagos attracts buyers who accept western-Algarve distance in exchange for scenery and a recognised leisure market. A singular villa on an isolated road may command emotion at purchase and require patience at sale.",
                "Build a five-year cash model in euros and in the household’s spending currency. Include IMT and stamp duty, legal and registration work, financing, condominium charges, IMI and possible AIMI, insurance, utilities, management, garden or pool care, repairs, climate adaptation, currency movement and selling costs. Ask two agents who did not source the home to identify the likely future buyer and evidence-based resale range. Value entry is not the lowest ticket; it is the price at which daily usefulness, compliance and future demand compensate for the risks actually attached to the address."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Cascais pairs Atlantic town life with Lisbon access; the Algarve adds warmer winters and wider coastal choice, with stronger seasonality outside established towns.",
        "global_access": "Cascais uses Lisbon Airport and metropolitan links; the Algarve uses Faro Airport, but Tavira, Loulé and Lagos have sharply different last-mile journeys.",
        "ownership_clarity": "Cascais and the Algarve share Portugal’s clear purchase framework, though licensed areas, condominium records, taxes and physical buildings still require reconciliation.",
        "regulatory_safety": "Cascais and Algarve municipalities can shape short-stay permissions, while condominium rules, drought, fire, flood and coastal exposure require address-level checks.",
        "rental_profit": "Cascais benefits from resident demand but high entry prices; Algarve income can be seasonal and management-heavy, especially for villas dependent on tourist use.",
        "capital_upside": "Cascais has metropolitan buyer depth and Algarve towns have international appeal, but current premiums, climate costs and local supply limit automatic upside.",
        "retirement_fit": "Cascais offers the easiest all-season service base; Faro, Loulé, Tavira and Lagos can work well when healthcare, transport and winter life are tested.",
        "exit_liquidity": "Cascais and established Algarve towns reach recognisable buyer pools; isolated resort or rural villas can require longer marketing and larger price adjustments.",
        "foreigner_fit": "Cascais and the Algarve have mature international services, but Portuguese tax, registry, municipal, condominium and contractor work still needs independent local support.",
        "value_entry": "Cascais carries a Lisbon-coast premium, while Tavira, Loulé and Lagos offer different tickets; completed-sale evidence matters more than a blended Algarve average.",
    },
    market_anchors=(
        {"location": "Cascais", "evidence": "4,550 EUR/m²", "buyer_read": "Median completed sale value for family dwellings in 2025; a municipal anchor, not a valuation for a particular home.", "source_label": "Statistics Portugal: Construction and Housing 2025", "source_url": "https://ine.pt/xportal/xmain?PUBLICACOESpub_boui=2247645&xpgid=ine_publicacoes&xpid=INE"},
        {"location": "Loulé", "evidence": "3,993 EUR/m²", "buyer_read": "Median completed sale value for family dwellings in 2025, illustrating the central Algarve’s premium municipal baseline.", "source_label": "Statistics Portugal: Construction and Housing 2025", "source_url": "https://ine.pt/xportal/xmain?PUBLICACOESpub_boui=2247645&xpgid=ine_publicacoes&xpid=INE"},
        {"location": "Lagos", "evidence": "3,801 EUR/m²", "buyer_read": "Median completed sale value for family dwellings in 2025; condition, view, legal area and micro-location can move far around it.", "source_label": "Statistics Portugal: Construction and Housing 2025", "source_url": "https://ine.pt/xportal/xmain?PUBLICACOESpub_boui=2247645&xpgid=ine_publicacoes&xpid=INE"},
    ),
    micro_locations_intro=(
        "Where to look begins with two gateways, not one coastal line. Cascais and Estoril belong to Lisbon’s metropolitan orbit. The Algarve runs outward from Faro into central, eastern and western submarkets whose access, seasonality and buyer pools differ. The labels below are decision zones, not price boundaries; verify the municipality, parish, planning status, hazards and actual travel time for every address. Within each zone, walkable town-centre property, a condominium beside the coast and a detached inland villa can have little in common. Compare the home with nearby completed transactions of the same legal type, then repeat the daily-life test from its actual front door. A ten-minute map difference can change car dependence, summer congestion, winter convenience and the number of buyers likely to understand the asset on resale."
    ),
    micro_locations=(
        {"name": "Cascais / Estoril", "best_for": "Metropolitan coastal life", "daily_life": "Rail-linked and service-rich", "diligence": "Entry price, condominium and municipal use"},
        {"name": "Central Algarve", "best_for": "Airport and service access", "daily_life": "Faro / Loulé year-round base", "diligence": "Exact coast-inland position and car use"},
        {"name": "Eastern Algarve", "best_for": "Town-led slower living", "daily_life": "Tavira and Ria Formosa rhythm", "diligence": "Flood, coastal rules and seasonal demand"},
        {"name": "Western Algarve", "best_for": "Scenery and leisure depth", "daily_life": "Lagos-led, more distant from Faro", "diligence": "Water, fire, wind and resale depth"},
    ),
    checklist=(
        "Confirm the residence, tax and healthcare route before treating the purchase as a retirement home.",
        "Choose Cascais or a specific Algarve corridor; do not search both as one market.",
        "Test airport, hospital, grocery and social journeys in winter and peak summer.",
        "Obtain a buyer-specific IMT, stamp-duty, IMI, AIMI and financing statement.",
        "Reconcile title, registered areas, licences, energy record, condition and condominium governance.",
        "Confirm short-stay permission with the municipality and building before underwriting any tourist rent.",
        "Overlay current flood, fire, heat, drought, coastal and insurance evidence for the exact address.",
        "Model five-year carrying cost and identify the likely resale buyer before making a binding offer.",
    ),
    references_intro=(
        "Legal, tax, residence, health, access, market and hazard claims were reviewed on 22 August 2026 against the primary sources below. The next scheduled review is 22 February 2027, or sooner if a cited law, municipal rule, tax table, transport service, hazard map or market release changes. Recheck the live source and obtain independent Portuguese legal, tax, immigration, building and insurance advice for the exact buyer and property before signing. Listing observations are dated asking evidence only and do not verify availability, title, condition, permitted use or completed value."
    ),
    references=(
        {"label": "Portugal government: buying and selling property", "url": "https://www.gov.pt/guias/compra-e-venda-de-imoveis-em-portugal-cidadaos-europeus"},
        {"label": "Portuguese Tax Authority: taxes on buying a home", "url": "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Compra_da_casa/Paginas/default.aspx"},
        {"label": "Portuguese Tax Authority: annual IMI and AIMI", "url": "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Imposto_anual/Paginas/default.aspx"},
        {"label": "AIMA: current residence-by-investment routes", "url": "https://aima.gov.pt/pt/viver/autorizacao-de-residencia-para-investimento-art-90-o-a"},
        {"label": "AIMA: residence documentation and proof of accommodation", "url": "https://aima.gov.pt/pt/decreto-regulamentar-da-lei-de-estrangeiros-alteracoes/perguntas-frequentes"},
        {"label": "Health Regulatory Authority: foreign residents and the National Health Service", "url": "https://www.ers.pt/pt/utentes/perguntas-frequentes/faq/acesso-de-cidadaos-estrangeiros-a-prestacao-de-cuidados-de-saude-no-servico-nacional-de-saude/"},
        {"label": "Portugal government: registration at a health centre", "url": "https://www.gov.pt/servicos/inscrever-se-no-centro-de-saude"},
        {"label": "Portugal government: Alojamento Local registration and municipal control", "url": "https://www.gov.pt/guias/alojamento-local"},
        {"label": "Statistics Portugal: Construction and Housing Statistics 2025", "url": "https://ine.pt/xportal/xmain?PUBLICACOESpub_boui=2247645&xpgid=ine_publicacoes&xpid=INE"},
        {"label": "Lisbon Airport: official public-transport access", "url": "https://live-site.ana.pt/pt/lis/acesso-e-estacionamento/chegar-e-sair-do-aeroporto/transportes-publicos"},
        {"label": "ANA Airports: Faro and Lisbon airport access", "url": "https://www.ana.pt/pt/app-content-type/access"},
        {"label": "National Civil Protection Authority: national risk assessment", "url": "https://prociv.gov.pt/media/h4fgmxul/anr2023_revis%C3%A3o_ultima.pdf"},
        {"label": "Loulé Municipal Assembly: local-accommodation regulation process", "url": "https://assembleia.cm-loule.pt/sessoes/222"},
        {"label": "Lagos municipality: local-accommodation registration evidence", "url": "https://www.cm-lagos.pt/site_content/270-espaco-da-empresa/13284-43-qual-e-a-documentacao-necessaria-para-pedir-o-registo-de-estabelecimento-de-alojamento-local-como-recebo-o-numero-de-registo"},
        {"label": "European Central Bank: euro reference exchange rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("cascais-hero", "/assets/algarve-cascais-coast-hero.webp", "Cascais waterfront promenade and historic town", "Cascais combines an Atlantic town with Lisbon-connected daily life.", "hero"),
        DossierImage("tavira-life", "/assets/algarve-cascais-tavira-daily-life.webp", "Residents walking on a shaded street in Tavira", "Tavira’s appeal is a functioning eastern-Algarve town, not only a holiday season.", "wide"),
        DossierImage("lagos-coast", "/assets/algarve-cascais-lagos-coast.webp", "Coastal path and limestone coves near Lagos", "Lagos trades greater distance from Faro for a distinctive western-Algarve landscape.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Algarve / Cascais through five destination lenses",
    assessment_intro="Here’s how Algarve / Cascais scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations expose the market spread: a Cascais apartment, a Tavira town apartment and a detached Lagos home. EUR is primary; USD uses the recorded ECB reference basis for comparison only.",
    market_anchors_intro="These figures are official municipal completed-sale evidence—not asking prices or valuations for the listings above. Match every candidate for exact location, legal area, building type, age, condition and view.",
    orientation_groups=(
        DossierOrientationGroup("Lisbon gateway", (("Lisbon Airport", "Metropolitan arrival"), ("Cascais / Estoril", "Rail-linked Atlantic base"))),
        DossierOrientationGroup("Faro gateway", (("Faro Airport", "Regional arrival"), ("Central Algarve", "Faro / Loulé"), ("Eastern Algarve", "Tavira corridor"), ("Western Algarve", "Lagos corridor"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Cascais and the Algarve are separate systems; confirm the actual route, timetable and peak-season travel time for every address.",
    country_guide_url="/countries/portugal-property/",
    country_guide_label="Portugal property guide",
    rail_comparison="Compare Algarve / Cascais with the full Atlas.",
)


MADEIRA_DOSSIER = PremiumDossierSpec(
    destination_id="madeira",
    title="Madeira Retirement Property Dossier",
    description="Assess Madeira retirement property through island access, daily life, healthcare, ownership, rental rules, hazards, value, resale, and current market evidence.",
    h1="Madeira: year-round island life, with the exit kept in view",
    lede=(
        "Madeira combines a mild Atlantic climate, a functioning regional capital and exceptional landscape in a compact island market. Funchal can support an ordinary year-round life; Machico and the south coast offer smaller-town alternatives; Calheta trades services for sun, space and scenery. The proposition is credible, but geography controls it: flights, steep roads, specialist healthcare, site hazards and a narrower resale pool must be treated as part of the property—not footnotes to the view."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "Madeira is a strong retirement shortlist for a lifestyle-first buyer who wants Portugal’s ownership framework and a genuinely year-round island community, and who can accept the operating consequences of living in the Atlantic. The clearest version is a practical home in Funchal or another established south-coast town, within a tested journey of groceries, healthcare and the expressway. A buyer who speaks some Portuguese—or budgets for continuing local professional help—will find the administrative burden more manageable. The case does not require aggressive rent or guaranteed appreciation: daily utility is the primary return.",
        "Pause or look elsewhere if the property is expected to create residence rights, if dependable mainland specialist healthcare is non-negotiable, if every important trip must work without a car, or if a short-stay licence and quick resale are needed to make the numbers work. Buying Portuguese property does not itself confer residence. Madeira Airport is the island’s main gateway, and weather can affect operations. SESARAM provides regional hospitals and health units, but an island buyer should confirm the exact specialist-care pathway, emergency transfer plan and private cover rather than infer mainland depth from a Funchal address.",
        "Proceed in order. Confirm residence, tax and healthcare arrangements; choose the daily-life pattern before the property; test airport, hospital and grocery journeys from the exact address; reconcile title, licensed area, access, retaining structures and permitted use; overlay flood, wildfire and slope-risk evidence; then model five-year cost and resale without holiday income. Madeira rewards address-level discipline. The wrong purchase is not necessarily an ugly home—it is a beautiful one whose slope, access, care burden or future buyer pool was discovered after exchange."
    ),
    lenses_intro=(
        "Madeira works differently at island, municipality and street level. These five paired lenses translate the Atlas model into the choices that determine whether an appealing visit becomes a durable home."
    ),
    lenses=(
        DossierLens(
            "Live on the island, not only in its scenery",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Funchal is the island’s most complete retirement base. The centre, São Martinho and the Lido corridor combine supermarkets, restaurants, seafront walking, buses, clinics and access to SESARAM’s hospital network. That density matters after the novelty of the landscape fades. A central apartment can reduce driving and simplify social life, but one steep block can change the real walkability of an apparently convenient address. Test gradients, shade, crossings, pavement condition, noise and the route home with shopping rather than relying on a flat map radius.",
                "Machico offers a smaller, flatter town centre with beach, market and airport proximity, while Santa Cruz and Caniço sit in the east-to-Funchal corridor. Câmara de Lobos provides a working town west of the capital but varies sharply between lower neighbourhoods and hillside addresses. Calheta and Ponta do Sol deliver more sun, ocean views and space, yet many homes depend on winding roads and a car for routine errands. The north coast is greener and quieter, with stronger microclimate variation and a smaller everyday service base. These are different retirement systems, not cosmetic neighbourhood choices.",
                "Healthcare needs a household-specific plan. SESARAM lists hospital and health-centre units across the region, but a directory does not establish appointment speed, language support, specialty availability or the circumstances in which care requires mainland Portugal. Ask the current insurer and a Madeira clinician how existing conditions, prescriptions, emergency transport and complex treatment would work. Then rehearse the trip from the candidate home to the relevant unit. A sunny hillside villa may remain delightful for years, but retirement fit falls quickly if one partner cannot drive or manage its stairs."
            ),
            "machico-life",
        ),
        DossierLens(
            "Use the airport advantage without forgetting the island",
            ("global_access", "foreigner_fit"),
            (
                "Cristiano Ronaldo Madeira International Airport in Santa Cruz is the island’s main external gateway. Official tourism guidance places Funchal roughly 20 to 25 minutes away by road and identifies buses, taxis, transfers and rental cars. Machico and Santa Cruz can shorten the last mile; Calheta and the west extend it. Direct European routes are useful, while Lisbon connections broaden the network. The buyer test is door to door: luggage, an early departure, a disrupted arrival and the cost of a taxi when a household car is unavailable.",
                "Island access is structurally different from mainland access. There is no rail or road alternative when aviation is disrupted, and airport notices periodically warn that adverse weather may affect operations. Keep schedule flexibility for medical appointments and onward international connections, understand airline seasonality, and price a contingency night. Within Madeira, the expressway and tunnel system makes the south coast far more connected than the island’s scale and relief suggest, but local roads can still be steep, narrow and slow. A claimed twenty-minute journey should be driven from the actual gate at the times that matter.",
                "Madeira is accustomed to international residents and tourism, especially in Funchal, Caniço, Ponta do Sol and Calheta. English can smooth property search and daily commerce, but the binding systems remain Portuguese: contracts, registry records, tax notices, condominium meetings, planning files and municipal decisions. Appoint an independent lawyer and tax adviser, verify translations, and retain a reliable local contact for notices and repairs. Foreigner friendliness means professional capacity exists; it does not mean the buyer can outsource judgment or treat an estate agent as independent counsel."
            ),
        ),
        DossierLens(
            "Own clearly, then inspect what holds the hillside up",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Portugal provides a legible route to acquire property, but ownership is separate from residence and tax status. Before a reservation or promissory contract becomes hard to unwind, reconcile the land-registry description, tax record, use licence, energy certificate, plans, boundaries, access rights and any extensions. Confirm who pays condominium debts and whether common-area works are planned. For a detached home, verify that pools, annexes, terraces, access roads and retaining walls are licensed and fall within the legal parcel. A sea view does not cure an area mismatch.",
                "Madeira adds physical diligence that cannot be reduced to a standard survey. The Regional Civil Protection risk assessment covers flash floods, slope movements, wildfire and other hazards; it notes the recurring relationship between rapid flooding and mass movement on steep terrain. Obtain the current municipal planning and hazard layers for the exact coordinates, then have an engineer inspect drainage, cut slopes, retaining structures, rockfall exposure, foundations and vehicle access. Visit after heavy rain if possible and ask how the road, power, water and mobile signal performed in recent severe weather.",
                "Short-stay operation is a separate permission question. Portugal’s Alojamento Local framework requires registration and allows municipal controls; condominium rules, planning status, insurance and later regulatory changes can narrow the answer. Do not pay for a claimed licence until counsel verifies the live registration, transfer consequences, permitted capacity and building position. Model long-term letting and no rent even when tourism looks strong. Regulatory safety on Madeira comes from matching the precise property, municipality and operating plan—not from the island’s popularity with visitors."
            ),
            "calheta-slope",
        ),
        DossierLens(
            "Let resident demand support the case before tourism",
            ("rental_profit", "capital_upside"),
            (
                "Funchal has the island’s broadest ordinary demand: regional government, healthcare, education, commerce and tourism employment create a resident economy beyond holiday arrivals. A practical apartment near services can therefore be tested first against a conventional tenancy and owner-occupier resale. Even there, condominium cost, parking, lift access, legal area and building condition affect net return. The completed-sale median for Funchal is an anchor for context, not evidence that a particular new-build or sea-view unit is correctly priced.",
                "Tourism is economically important and less seasonal than many European islands, but booking demand is not the same as passive profit. Machico mixes airport access and town life; Calheta and Ponta do Sol can command lifestyle premiums but often add pool, garden, vehicle, cleaning, utility and local-management costs. DREM’s tourism releases show substantial year-round accommodation activity, yet they do not prove a particular home can legally operate or achieve a target occupancy. Separate gross revenue, operating margin and owner-use dates, then stress winter pricing and a regulatory interruption.",
                "Capital upside should be attached to durable scarcity and a future buyer pool, not to a general island story. Funchal’s service depth and finite buildable land support selected central and Lido-area assets, but high entry prices can already capitalise that appeal. Câmara de Lobos, Santa Cruz and Machico may offer more practical tickets, while southwest villas compete on view, design and condition in a narrower international market. Infrastructure and tourism can support demand; neither guarantees that a singular house, difficult road or overbuilt apartment will resell at the buyer’s timetable."
            ),
        ),
        DossierLens(
            "Buy for the life you can use—and the buyer who comes next",
            ("value_entry", "exit_liquidity"),
            (
                "Official completed-sale evidence reveals a real hierarchy. DREM reported 2025 medians of 3,100 EUR/m² in Funchal, 2,500 in Santa Cruz and 2,484 in Câmara de Lobos, with premium Funchal parishes above the city figure. Those are municipal medians across transacted family dwellings, not valuations. The three listing observations below deliberately span a Funchal apartment, a Machico apartment and a Calheta house. They show asking dispersion and buyer cases; they do not establish fair value, availability or legal condition.",
                "Value entry depends on use. A well-located older Funchal apartment may offer stronger service access and resale breadth than a larger hillside home, even if its euro per square metre is higher. Machico can provide a coherent smaller-town alternative when airport proximity and a flatter core matter. Calheta can deliver the landscape many buyers imagine, but a villa premium must compensate for car dependence, structural maintenance and a more specialised exit. Compare only against legally similar homes with comparable altitude, access, view, age and condition.",
                "Protect liquidity before making the offer. Ask two agents who did not source the home to identify the likely future buyer, normal marketing period and completed evidence. Model sale costs, currency movement and a price reduction after five years. Confirm that an older owner could reach the entrance, parking and principal rooms; accessibility expands both personal utility and the future buyer pool. Madeira’s best property is not the most photographed one. It is the address whose daily function, all-in carrying cost and resale story remain understandable when the sea view is no longer new."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Madeira pairs a mild climate and dramatic landscape with real Funchal city life; Calheta and the north coast trade services for scenery and quiet.",
        "global_access": "Madeira Airport offers useful European and Lisbon links, but every off-island journey depends on aviation and west-coast homes add a longer road leg.",
        "ownership_clarity": "Madeira follows Portugal’s clear purchase process, while hillside homes still require exact reconciliation of title, licensed areas, access, pools and retaining structures.",
        "regulatory_safety": "Madeira buyers must verify municipal short-stay rules and address-level wildfire, flash-flood and slope risk; a national framework does not settle the property answer.",
        "rental_profit": "Funchal has the broadest resident demand; Machico and Calheta can attract visitors, but management, licence, seasonality and property-care costs reduce headline revenue.",
        "capital_upside": "Madeira’s limited land and year-round appeal support selected assets, though Funchal premiums and specialised Calheta villas already price in much of the story.",
        "retirement_fit": "Funchal offers Madeira’s strongest healthcare and service base; steep streets, driving dependence and possible mainland specialist care weaken remote hillside choices.",
        "exit_liquidity": "Funchal apartments reach Madeira’s broadest buyer pool, while singular Calheta villas and remote north-coast homes can require more time and price flexibility.",
        "foreigner_fit": "Madeira has experienced international services, especially around Funchal and Calheta, but contracts, tax, planning, condominium and municipal work remain Portuguese-led.",
        "value_entry": "Funchal, Machico and Câmara de Lobos offer different practical tickets; Madeira’s lowest prices often carry more slope, access, condition or resale risk.",
    },
    market_anchors=(
        {"location": "Funchal", "evidence": "3,100 EUR/m²", "buyer_read": "Median completed sale value for family dwellings in the 12 months to Q4 2025; a municipal anchor, not a valuation for an individual home.", "source_label": "DREM: local house prices, Q4 2025", "source_url": "https://estatistica.madeira.gov.pt/en/download-now-3/economic/const-hab-gb/house-prices-at-local-level/press-release-house-prices/5726-24-04-2026-for-the-4th-quarter-of-2025-drem-publishes-information-on-the-median-price-of-family-dwellings-in-the-autonomous-region-of-madeira.html"},
        {"location": "Santa Cruz", "evidence": "2,500 EUR/m²", "buyer_read": "Median completed sale value for family dwellings in the 12 months to Q4 2025, covering the airport-side municipality and its varied parishes.", "source_label": "DREM: local house prices, Q4 2025", "source_url": "https://estatistica.madeira.gov.pt/en/download-now-3/economic/const-hab-gb/house-prices-at-local-level/press-release-house-prices/5726-24-04-2026-for-the-4th-quarter-of-2025-drem-publishes-information-on-the-median-price-of-family-dwellings-in-the-autonomous-region-of-madeira.html"},
        {"location": "Câmara de Lobos", "evidence": "2,484 EUR/m²", "buyer_read": "Median completed sale value for family dwellings in the 12 months to Q4 2025; lower and hillside addresses should not be treated as one product.", "source_label": "DREM: local house prices, Q4 2025", "source_url": "https://estatistica.madeira.gov.pt/en/download-now-3/economic/const-hab-gb/house-prices-at-local-level/press-release-house-prices/5726-24-04-2026-for-the-4th-quarter-of-2025-drem-publishes-information-on-the-median-price-of-family-dwellings-in-the-autonomous-region-of-madeira.html"},
    ),
    micro_locations_intro=(
        "The useful map is organised by daily systems rather than views. Funchal is the service centre; the east controls airport proximity; the lower west remains connected to the capital; the southwest trades convenience for climate and scenery. These are orientation zones, not price boundaries. Confirm parish, altitude, gradient, road width, planning status, hazard layers and real journey time for every address. Visit at different times of day, park the car, and complete the last part on foot. On Madeira, a short vertical distance can separate a walkable town home from a car-dependent hillside one. Ask where residents buy groceries, which health unit they use, how waste is collected, and whether delivery and emergency vehicles can reach the entrance without difficulty."
    ),
    micro_locations=(
        {"name": "Funchal / Lido", "best_for": "Service-rich retirement", "daily_life": "Most urban and least car-dependent", "diligence": "Gradient, building, price and noise"},
        {"name": "Santa Cruz / Machico", "best_for": "Airport and smaller-town life", "daily_life": "East-coast access with local centres", "diligence": "Aircraft, wind, road and service depth"},
        {"name": "Câmara de Lobos", "best_for": "Funchal-adjacent value", "daily_life": "Working town with steep variation", "diligence": "Altitude, access, drainage and legal area"},
        {"name": "Ponta do Sol / Calheta", "best_for": "Sun and landscape", "daily_life": "Car-led southwest lifestyle", "diligence": "Slope, structures, management and exit"},
    ),
    checklist=(
        "Confirm residence, tax, healthcare and insurance arrangements independently of the property purchase.",
        "Choose a daily-life zone before viewing homes; do not compare Funchal and Calheta as interchangeable inventory.",
        "Drive the airport, hospital, grocery and social routes from the exact gate in ordinary and adverse conditions.",
        "Reconcile registry, tax record, use licence, plans, boundaries, access, pools, annexes and condominium records.",
        "Commission building and engineering review of drainage, slopes, retaining walls, rockfall exposure and vehicle access.",
        "Confirm live Alojamento Local permission, municipal position, condominium rules and insurance before pricing tourist rent.",
        "Compare current asking evidence with completed sales of the same legal type, altitude, condition and micro-location.",
        "Model five-year ownership and a conservative resale, then identify the likely next buyer before exchange.",
    ),
    references_intro=(
        "Legal, tax, residence, health, access, market and hazard claims were reviewed on 22 August 2026 against the primary sources below. The next scheduled review is 22 February 2027, or sooner if a cited law, municipal rule, tax table, transport service, hazard map, healthcare arrangement or statistics release changes. Recheck the live source and obtain independent Portuguese legal, tax, immigration, engineering and insurance advice for the exact buyer and property before signing. Listing observations are dated asking evidence only and do not verify availability, title, condition, permitted use or completed value."
    ),
    references=(
        {"label": "Portugal government: buying and selling property", "url": "https://www.gov.pt/guias/compra-e-venda-de-imoveis-em-portugal-cidadaos-europeus"},
        {"label": "Portuguese Tax Authority: taxes on buying a home", "url": "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Compra_da_casa/Paginas/default.aspx"},
        {"label": "Portuguese Tax Authority: annual IMI and AIMI", "url": "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Imposto_anual/Paginas/default.aspx"},
        {"label": "AIMA: current residence-by-investment routes", "url": "https://aima.gov.pt/pt/viver/autorizacao-de-residencia-para-investimento-art-90-o-a"},
        {"label": "AIMA: residence documentation and proof of accommodation", "url": "https://aima.gov.pt/pt/decreto-regulamentar-da-lei-de-estrangeiros-alteracoes/perguntas-frequentes"},
        {"label": "Health Regulatory Authority: foreign residents and the National Health Service", "url": "https://www.ers.pt/pt/utentes/perguntas-frequentes/faq/acesso-de-cidadaos-estrangeiros-a-prestacao-de-cuidados-de-saude-no-servico-nacional-de-saude/"},
        {"label": "SESARAM: Madeira hospital units", "url": "https://www.sesaram.pt/portal/o-sesaram/o-sesaram/as-nossas-unidades/hospitais"},
        {"label": "Portugal government: Alojamento Local registration and municipal control", "url": "https://www.gov.pt/guias/alojamento-local"},
        {"label": "DREM: Madeira local house prices, Q4 2025", "url": "https://estatistica.madeira.gov.pt/en/download-now-3/economic/const-hab-gb/house-prices-at-local-level/press-release-house-prices/5726-24-04-2026-for-the-4th-quarter-of-2025-drem-publishes-information-on-the-median-price-of-family-dwellings-in-the-autonomous-region-of-madeira.html"},
        {"label": "DREM: Madeira tourism, Q2 2026", "url": "https://estatistica.madeira.gov.pt/download-now/economica/turismo-pt/turismo-noticias-pt/75-noticias/turismo/5943-14-08-2026-no-2-trimestre-de-2026-as-dormidas-dos-residentes-nacionais-no-alojamento-turistico-da-ram-aumentaram-12-3-em-termos-homologos.html"},
        {"label": "Madeira Tourism Board: how to reach the island", "url": "https://visitmadeira.com/en/travel-info/how-to-get-here/"},
        {"label": "Madeira Tourism Board: island transport", "url": "https://visitmadeira.com/en/travel-info/how-to-move-around/"},
        {"label": "Madeira Regional Civil Protection: regional risk assessment", "url": "https://www.procivmadeira.pt/images/prevencao_preparacao/Corpo%20ARRAM_2023.pdf"},
        {"label": "Madeira Regional Civil Protection: current public warnings", "url": "https://procivmadeira.pt/pt/"},
        {"label": "European Central Bank: euro reference exchange rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("funchal-hero", "/assets/madeira-funchal-hero.webp", "Funchal neighbourhoods descending toward the harbour", "Funchal is Madeira’s deepest year-round service base—and its broadest resale market.", "hero"),
        DossierImage("machico-life", "/assets/madeira-machico-daily-life.webp", "Residents on a shaded street in central Machico", "Machico offers a smaller-town daily rhythm close to Madeira Airport.", "wide"),
        DossierImage("calheta-slope", "/assets/madeira-calheta-slope.webp", "Homes and terraced fields on the steep coast near Calheta", "On the southwest coast, the landscape and the access diligence are the same proposition.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Madeira through five destination lenses",
    assessment_intro="Here’s how Madeira scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show distinct buyer cases in Funchal, Machico and Calheta. EUR is primary; USD uses the recorded ECB reference basis for comparison only.",
    market_anchors_intro="These figures are official municipal completed-sale evidence—not asking prices or valuations for the listings above. Match each candidate for parish, altitude, legal area, property type, age, condition and access.",
    orientation_groups=(
        DossierOrientationGroup("Airport and urban spine", (("Madeira Airport", "Island gateway"), ("Santa Cruz / Machico", "East-coast towns"), ("Funchal / Lido", "Service centre"))),
        DossierOrientationGroup("West from Funchal", (("Câmara de Lobos", "Connected working town"), ("Ponta do Sol", "Southwest transition"), ("Calheta", "Car-led lifestyle coast"))),
    ),
    orientation_caption="Orientation schematic—not to scale. The expressway connects the south coast, but altitude, local roads and weather can change actual journey time sharply.",
    country_guide_url="/countries/portugal-property/",
    country_guide_label="Portugal property guide",
    rail_comparison="Compare Madeira with the full Atlas.",
)


MALAGA_COSTA_DEL_SOL_DOSSIER = PremiumDossierSpec(
    destination_id="malaga-costa-del-sol",
    title="Málaga and Costa del Sol Retirement Property Dossier",
    description="Assess Málaga and Costa del Sol retirement property through daily life, rail and road access, ownership, rental rules, value, resale, hazards, and current market evidence.",
    h1="Málaga / Costa del Sol: buy the everyday coast, not the headline",
    lede=(
        "Málaga and the Costa del Sol combine an international airport, substantial healthcare, established foreign communities and a Mediterranean life that continues beyond summer. But the label hides several markets. Málaga city and the C1 rail corridor can support a less car-dependent routine; Marbella and Estepona offer deeper resort services but rely on the A-7 road spine. Prices, rental permissions and resale depth change sharply by municipality and building. The opportunity is credible only when the buyer chooses the daily system before the view."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "Málaga / Costa del Sol belongs on a retirement shortlist for a buyer who values direct European access, a large international community, year-round restaurants and services, and multiple hospital options. The strongest version is a practical home connected to ordinary daily life: Málaga city for urban depth, Benalmádena or Fuengirola for a rail-served coast, Marbella or San Pedro for a premium service ecosystem, and Estepona for a slower western base. The destination does not need unrestricted holiday rent or guaranteed appreciation to work; personal utility should carry the case.",
        "Pause or look elsewhere if low entry price is essential, if the household cannot tolerate summer heat or water constraints, if every trip must remain car-free beyond Fuengirola, or if a new tourist licence is required to make the budget balance. Property ownership does not create Spanish residence or public-healthcare entitlement. Málaga city has tightened tourist-use approvals, Andalucía requires planning compatibility, and national community-of-owners rules can add another approval layer. A listing advertised with a licence is evidence to verify, not a transferable promise.",
        "Proceed in order. Confirm residence, tax and healthcare; select urban, rail-served or road-led daily life; test airport, hospital and grocery routes from the exact address in summer traffic; reconcile registry, cadastre, planning, occupancy and community records; establish the live rental position with the municipality and building; overlay flood, wildfire, heat and water evidence; then compare completed transactions and model a five-year exit without tourist income. The controlling condition is strict entry-price discipline at a specific address—not confidence in the coast as a whole."
    ),
    lenses_intro=(
        "The coast becomes clearer when treated as connected daily-life systems rather than one resort strip. These five paired lenses show where the proposition strengthens, where it weakens, and what can reverse the decision."
    ),
    lenses=(
        DossierLens(
            "Live where the coast still works on an ordinary Tuesday",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Málaga city offers the deepest non-resort life in the corridor. Markets, culture, universities, neighbourhood commerce, two major public teaching hospitals and the waterfront sit within a substantial resident economy. Centro and the eastern districts can support a walkable routine, while other neighbourhoods depend more on buses or a car. Historic-core charm brings noise, visitor pressure, older buildings and occasional missing lifts. The retirement test is not whether the centre is lively; it is whether groceries, shade, healthcare and a quiet bedroom remain easy in August and in winter.",
                "Benalmádena and Fuengirola provide the clearest coastal compromise for someone who wants beach access without surrendering rail. Arroyo de la Miel, Los Boliches and central Fuengirola have stations, supermarkets, clinics and year-round street life. Hillside parts of Benalmádena, Torreblanca and Mijas Costa can look close on a map while requiring steep walks or daily driving. Visit without a rental car, carry shopping home, and test the route to the station. The C1 line is a practical asset only when the front door can use it comfortably.",
                "Marbella, San Pedro and Estepona support mature international communities, private medicine, restaurants, golf and household services, but their practical pattern is more road-led. Hospital Universitario Costa del Sol is a regional specialty hospital, with high-resolution facilities in Estepona and Mijas, yet entitlement and referral still depend on the household’s legal and insurance position. Test care routes, prescription access and summer congestion. A sea-view urbanisation may deliver privacy while making every meal, appointment and social visit dependent on a driver.",
                "Climate comfort must also be tested inside the home. Visit during the hottest period, close the windows against road or nightlife noise, and note whether shade, cross-ventilation and efficient cooling still make the principal rooms usable. Return in winter to check damp, low sun, building occupation and which nearby businesses remain open. A property that performs only with terraces open or a resort fully staffed is a holiday proposition, not necessarily a durable retirement base."
            ),
            "daily-life",
        ),
        DossierLens(
            "Use the airport and rail advantage before the road takes over",
            ("global_access", "foreigner_fit"),
            (
                "Málaga–Costa del Sol Airport is the destination’s structural advantage. Aena places Málaga centre about twelve minutes away by C1, Benalmádena about eighteen and Fuengirola about thirty-four, with María Zambrano high-speed rail reached in roughly eight. That makes Málaga city and the rail corridor unusually legible for international travel. Measure the whole trip from the property, however: station access, luggage, service hours and the final walk matter more than an airport pin on a listing map.",
                "The rail line ends at Fuengirola. Mijas Costa, Marbella, San Pedro, Estepona and Manilva depend mainly on the A-7/AP-7 road system, buses and taxis. A western address can still be globally accessible, but its last mile is a different proposition. Drive it during weekday peaks and summer changeover periods, price airport transfers, and identify a workable alternative if one household member stops driving. The same distance can feel reasonable on a quiet February morning and exhausting after a delayed flight in August.",
                "The international ecosystem is deep by Spanish coastal standards. Estate agents, lawyers, tax advisers, clinics and service businesses routinely work with foreign residents, especially from Fuengirola westward. That helps, but the legal record remains Spanish and municipal practice remains local. Contracts, tax notices, community meetings and planning files should be understood through independent advisers. Integration is strongest when international support opens the door to local systems; it is weakest when English-speaking sales material is mistaken for due diligence."
            ),
        ),
        DossierLens(
            "Own the home clearly—and verify the use separately",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Spain generally permits foreign buyers to own property, but clear access to title does not remove transaction work. Obtain a current Nota Simple, compare the registry and cadastre with the physical home, verify planning and occupancy status, and identify mortgages, charges, tenants and community debts. For an apartment, read statutes, minutes, budgets, reserve position, litigation, major works and accessibility. For villas and townhouses, confirm boundaries, pools, extensions, retaining walls, utility connections and any works that need regularisation before a deposit becomes difficult to recover.",
                "Tourist use is an address-level legal question. Andalucía’s amended rules require planning compatibility and exclude homes where community statutes expressly prohibit tourist accommodation. Málaga city’s planning controls have already restricted new registrations in saturated neighbourhoods and its 2026 planning work continues to prioritise residential use. Other Costa del Sol municipalities can take different positions. National community approval requirements and building rules add further layers. Ask counsel for a written answer covering the municipality, premises, community, operator and date—not a screenshot of an old registration.",
                "Physical risk also changes block by block. Screen official flood mapping, then review municipal drainage, steep access, wildfire interface, coastal exposure and insurability. AEMET’s Málaga Airport climate normals show hot, nearly rainless midsummer conditions, but annual averages hide heat inside a west-facing apartment and intense autumn rain on a low site. The western water system has required infrastructure designed to improve resilience and emergency transfers. Check shade, cooling, water pressure, garden demand, previous losses and an insurance quotation for the exact property.",
                "Budget separately for the legal home and the operating home. Acquisition tax, notary, registry and advice are only the opening costs; lifts, façades, pools, gardens, security, air-conditioning, pest control and water can dominate later years. Read at least three years of community minutes and accounts, ask for the technical building inspection where applicable, and commission a specialist survey. A low community fee may signal efficiency, or it may signal deferred work and an approaching special assessment."
            ),
            "west-coast",
        ),
        DossierLens(
            "Build the financial case on resident demand, not a licence story",
            ("rental_profit", "capital_upside"),
            (
                "Málaga city has the broadest ordinary rental foundation because employment, education, healthcare and transport operate beyond tourism. Fuengirola and Benalmádena add resident and seasonal demand; Marbella and Estepona have international and service economies but a larger share of resort-led stock. None of that turns a specific apartment into a simple yield asset. Model community fees, management, insurance, utilities, maintenance, vacancy, tax and furnishing before comparing the result with a conventional tenancy and no rental income.",
                "Short-stay revenue should be the final scenario, not the first. A registration may be unavailable, suspended, limited by municipal zoning, blocked by a community, tied to conditions the property no longer meets, or economically weak after professional management. Existing activity must be checked for validity and continuity after sale. If the purchase fails without tourist rent, the buyer has not bought retirement optionality; the buyer has underwritten a regulated hospitality business. Keep owner-use dates and the cost of compliance visible in every revenue model.",
                "Capital upside is plausible where scarcity, service depth and a broad future buyer pool coincide, but rapid price growth has already raised the entry bar. Registered 2025 evidence for Málaga province averaged 3,101 EUR/m², with new homes at 3,387 and used homes at 2,964. Those figures do not value Marbella, Centro Málaga or an Estepona villa; they show why unlike stock must not be averaged into a promise. Future gains should be a sensitivity, not the reason an over-priced home appears affordable."
            ),
        ),
        DossierLens(
            "Pay for a buyer pool you can name on the way out",
            ("value_entry", "exit_liquidity"),
            (
                "Entry value comes from choosing a coherent buyer case. A central Málaga apartment may command a high price per square metre but reach residents, professionals, international buyers and downsizers. A Los Boliches apartment can combine rail, beach and services, provided the building and street remain comfortable year-round. A larger Estepona house may offer space at a lower unit price while adding renovation, car, garden and community costs. Compare total five-year cash outlay, not the portal price or the sea-view premium alone.",
                "The three listing observations below are dated asking examples: a historic-centre Málaga apartment, a rail-served Fuengirola apartment and a western-coast Estepona house. They intentionally differ in legal type, condition and daily system. Official registered-sale figures cover the province and broad new-versus-used categories, so they are context rather than direct comparables. Obtain completed evidence for the same municipality, property type, size, age, condition and micro-location, and ask why a seller’s chosen comparables are genuinely substitutable.",
                "Protect the exit before offering. Ask two agents who did not introduce the property to identify the likely next buyer, normal marketing period and price-sensitive defects. A lift, level approach, parking, walkable services and efficient cooling can widen an older buyer pool. An isolated hillside villa, irregular extension or tourism-dependent studio may require more time and discount. Model sale costs, currency movement and a weaker market after five years. The best Costa del Sol purchase is not the cheapest or most photographed; it is the one whose future buyer can already be described."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Málaga combines city culture and coast; Fuengirola, Marbella and Estepona extend the choice, but summer crowding and road-led urbanisations change daily life.",
        "global_access": "Málaga Airport and the C1 line make the city, Benalmádena and Fuengirola unusually accessible; Marbella and Estepona add a road-dependent final leg.",
        "ownership_clarity": "Málaga / Costa del Sol follows Spain’s open ownership framework, while every home still needs registry, cadastre, planning, occupancy and community records reconciled.",
        "regulatory_safety": "Málaga city restrictions, Andalusian tourist-use rules and community approval make rental permission property-specific; flood, heat and wildfire review must also be address-specific.",
        "rental_profit": "Málaga city has the broadest resident demand; Fuengirola, Marbella and Estepona can add visitor demand, but licences and operating costs constrain net return.",
        "capital_upside": "Costa del Sol demand and infrastructure are supportive, yet rapid appreciation means Málaga, Marbella and Estepona buyers must not rely on continued multiple expansion.",
        "retirement_fit": "Málaga city offers the deepest healthcare and services; Fuengirola retains rail, while Marbella and Estepona provide strong amenities with greater car dependence.",
        "exit_liquidity": "Málaga apartments and established Fuengirola homes reach broad buyer pools; specialised hillside villas west of Marbella need more time and price discipline.",
        "foreigner_fit": "Costa del Sol has deep international professional support, especially around Fuengirola, Marbella and Estepona, but binding legal and municipal work remains Spanish-led.",
        "value_entry": "Málaga and the central coast carry mature premiums; Estepona can offer more space, but transport, renovation and a narrower buyer pool can absorb the discount.",
    },
    market_anchors=(
        {"location": "Málaga province · all homes", "evidence": "3,101 EUR/m²", "buyer_read": "Average price of homes registered in 2025. This broad provincial transaction anchor combines very different municipalities, property types and conditions.", "source_label": "Registradores: 2025 registered housing statistics", "source_url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf"},
        {"location": "Málaga province · new homes", "evidence": "3,387 EUR/m²", "buyer_read": "Average registered price for new homes in 2025. It is a province-wide asset-basis comparison, not a new-build valuation for a specific development.", "source_label": "Registradores: 2025 registered housing statistics", "source_url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf"},
        {"location": "Málaga province · used homes", "evidence": "2,964 EUR/m²", "buyer_read": "Average registered price for used homes in 2025. Age, legal area, lift, condition, exact town and coast access remain essential comparability limits.", "source_label": "Registradores: 2025 registered housing statistics", "source_url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf"},
    ),
    micro_locations_intro=(
        "Use four daily-life patterns, not one Costa del Sol average. Málaga city is the urban and transport base; Benalmádena and Fuengirola are the rail-served coast; Marbella and San Pedro form a premium service corridor; Estepona and Manilva trade airport ease for space and a slower western rhythm. The lines are not price boundaries. Confirm the exact municipality, station or road route, gradient, summer congestion, hospital journey, planning status, community rules and likely future buyer for every address."
    ),
    micro_locations=(
        {"name": "Málaga city / east Málaga", "best_for": "Urban retirement and airport access", "daily_life": "Deepest services and least resort dependence", "diligence": "Noise, heat, lift, flood and tourist-use zone"},
        {"name": "Benalmádena / Fuengirola", "best_for": "Rail-served coastal routine", "daily_life": "Stations, beach and year-round commerce", "diligence": "Gradient, building, crowding and licence"},
        {"name": "Marbella / San Pedro", "best_for": "Premium international services", "daily_life": "Mature coastal ecosystem, mainly road-led", "diligence": "Entry price, traffic, community and resale"},
        {"name": "Estepona / Manilva", "best_for": "Space and western-coast lifestyle", "daily_life": "Slower rhythm with longer airport journey", "diligence": "Car dependence, water, build status and exit"},
    ),
    checklist=(
        "Confirm residence, tax, public-healthcare and private-insurance arrangements independently of the property purchase.",
        "Choose urban, rail-served or road-led daily life before comparing listings across the coast.",
        "Travel the airport, hospital, grocery and social routes from the exact address in summer traffic and without a car.",
        "Reconcile the Nota Simple, cadastre, planning, occupancy, boundaries, extensions, debts and community records.",
        "Obtain a written tourist-use answer covering Andalucía, the municipality, the building, the operator and continuity after sale.",
        "Screen official flood mapping, wildfire interface, heat, water, drainage and insurability for the exact coordinates.",
        "Compare asking evidence with completed transactions of the same legal type, condition and micro-location.",
        "Model five-year ownership and a conservative resale without holiday income, then name the likely future buyer.",
    ),
    references_intro=(
        "Legal, tax, residence, healthcare, transport, climate, market and rental claims were reviewed on 22 August 2026 against the primary sources below. The next scheduled review is 22 February 2027, or sooner if a cited law, municipal rule, tax table, transport service, hazard source or statistics release changes. Recheck the live source and obtain independent Spanish legal, tax, immigration, planning, engineering and insurance advice for the exact buyer and property before signing. Listing observations are dated asking evidence only and do not verify availability, title, condition, legal use, transferability or completed value."
    ),
    references=(
        {"label": "Ministry of Inclusion: non-lucrative residence", "url": "https://www.inclusion.gob.es/en/web/migraciones/w/autorizacion-inicial-de-residencia-temporal-no-lucrativa"},
        {"label": "Spanish Tax Agency: individual tax residence", "url": "https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/residencia-personas-fisicas-juridicas/persona-fisica-residente-espana.html"},
        {"label": "Spanish Tax Agency: non-resident property taxation", "url": "https://sede.agenciatributaria.gob.es/Sede/vivienda-otros-inmuebles/no-residentes-tributacion-inmuebles.html"},
        {"label": "Spanish Social Security: healthcare entitlement", "url": "https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/PrestacionesPensionesTrabajadores/10938/30476/177505"},
        {"label": "Registradores: international buyer guidance", "url": "https://www.registradores.org/gl/documentacion-y-descargas/guias-rapidas"},
        {"label": "Registradores: 2025 registered housing statistics", "url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf"},
        {"label": "Junta de Andalucía: Decree 31/2024 on tourist-use homes", "url": "https://www.juntadeandalucia.es/boja/2024/24/50"},
        {"label": "Málaga City Council: tourist-use limits in saturated neighbourhoods", "url": "https://urbanismo.malaga.eu/anuncios-de-planeamiento/planificacion/modificacion-de-elementos/index.html"},
        {"label": "Málaga City Council: 2026 residential and hospitality-use planning update", "url": "https://www.malaga.eu/el-ayuntamiento/notas-de-prensa/detalle-de-la-nota-de-prensa/index.html?id=178224"},
        {"label": "Aena: Málaga Airport C1 access and journey times", "url": "https://www.aena.es/en/malaga-costa-del-sol/getting-there/trains.html"},
        {"label": "Renfe: Málaga Cercanías network map", "url": "https://www.renfe.com/content/dam/renfe/es/Viajeros/Secciones/Cercanias/Mapas/2025/mapa_malaga_abril_2025.pdf"},
        {"label": "Andalusian Health Service: Hospital Universitario Costa del Sol", "url": "https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/el-sas/servicios-y-centros/informacion-por-centros/25532"},
        {"label": "AEMET: Málaga Airport climate normals", "url": "https://www.aemet.es/en/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=6155A"},
        {"label": "MITECO: national flood-zone mapping system", "url": "https://www.miteco.gob.es/es/agua/temas/gestion-de-los-riesgos-de-inundacion/snczi.html"},
        {"label": "Junta de Andalucía: 2026 Costa del Sol water-system resilience works", "url": "https://www.juntadeandalucia.es/boja/2026/19/45"},
        {"label": "European Central Bank: euro reference exchange rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("city-hero", "/assets/malaga-costa-del-sol-city-hero.webp", "Málaga neighbourhoods, waterfront and coastline in morning light", "Málaga city gives the coast its deepest year-round service and transport base.", "hero"),
        DossierImage("daily-life", "/assets/malaga-costa-del-sol-daily-life.webp", "Older residents walking along a shaded street near the sea on the Costa del Sol", "The rail-served coast works best where ordinary errands remain close and shaded.", "wide"),
        DossierImage("west-coast", "/assets/malaga-costa-del-sol-west-coast.webp", "Homes, the coastal road and dry hills west of Málaga", "West of Fuengirola, road access and the property proposition become inseparable.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Málaga / Costa del Sol through five destination lenses",
    assessment_intro="Here’s how Málaga / Costa del Sol scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show distinct buyer cases in Málaga city, rail-served Fuengirola and road-led Estepona. EUR is primary; USD uses the recorded ECB reference basis for comparison only.",
    market_anchors_intro="These figures are official registered-sale evidence—not asking prices or valuations for the listings above. They are province-wide new-versus-used context; match every candidate for municipality, legal type, area basis, age, condition, access and completed transaction date.",
    orientation_groups=(
        DossierOrientationGroup("C1 airport and rail spine", (("Málaga city", "Urban service base"), ("Málaga Airport", "International gateway"), ("Benalmádena", "Rail-served coast"), ("Fuengirola", "C1 terminus"))),
        DossierOrientationGroup("West by road", (("Mijas Costa", "Road transition"), ("Marbella / San Pedro", "Premium service coast"), ("Estepona", "Western town base"), ("Manilva", "Far-west value edge"))),
    ),
    orientation_caption="Orientation schematic—not to scale. C1 rail ends at Fuengirola; west-coast journey times depend on the A-7/AP-7, local roads, traffic and the exact address.",
    country_guide_url="/countries/spain-property/",
    country_guide_label="Spain property guide",
    rail_comparison="Compare Málaga / Costa del Sol with the full Atlas.",
)


HAKONE_IZU_DOSSIER = PremiumDossierSpec(
    destination_id="hakone-izu",
    title="Hakone and Izu Retirement Property Dossier",
    description="Assess Hakone and Izu retirement property through daily life, access, ownership, rental rules, hazards, value, resale, and current listings.",
    h1="Hakone / Izu: choose the operating system before the onsen",
    lede=(
        "Hakone / Izu is a corridor, not a single retirement market. Atami combines Shinkansen access, hospitals and a steep seaside city; Hakone offers onsen, mountain scenery and frequent use from Tokyo; Ito and Izu-Kogen pair rail with older resort stock; Shimoda delivers the deepest coastal lifestyle with the longest journeys. The same view can therefore sit above very different transport, medical, hazard, maintenance and resale realities. This dossier begins with the life and route a home must support, then tests whether the property earns its price."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is positive for a personal-use-led buyer who selects the address by daily function rather than postcard appeal. Atami is the broadest retirement base: its station sits on the Tokaido Shinkansen and conventional rail network, its centre has ordinary commerce, and International University of Health and Welfare Atami Hospital provides regional emergency and specialist care. Hakone is the stronger repeat-use choice for a Tokyo-based household that accepts buses, gradients and a tourism economy. Ito and Izu-Kogen offer more space and lower-entry older stock along the eastern railway. Shimoda is the most deliberate lifestyle choice because distance, car dependence, healthcare depth and resale narrow toward the peninsula’s south.",
        "Ownership and residence remain separate. Foreigners can generally acquire ordinary Japanese real estate, but a deed does not create a visa, public-healthcare eligibility or access to domestic borrowing. Japan has no general retirement visa. The official designated-activities route for long sightseeing is limited to qualifying nationalities, financial and insurance conditions, normally six months and at most one year after extension; it is not a permanent retirement solution. A buyer who expects to live here full time needs a different renewable residence basis confirmed before purchase, together with tax and healthcare advice for the actual household.",
        "Proceed in this order: establish residence and healthcare; choose Atami city, Hakone mountain, Ito/Izu-Kogen rail-and-car life or the deeper Shimoda coast; travel the exact hospital, grocery and station route in poor weather; then reconcile title, road access, planning, utilities, building condition, management obligations, hot-spring arrangements, hazards and lawful use. Underwrite rental income only after the property and local rules are clear. The corridor can be unusually rewarding, but the winning asset is the one whose everyday logistics and future buyer pool remain credible after the view stops being new."
    ),
    lenses_intro=(
        "The Atlas pairs the ten decision dimensions into five practical questions. Each lens explains what the evidence means for a buyer; the complete assessment appears once in the score table below."
    ),
    lenses=(
        DossierLens(
            "Choose the life that still works on an ordinary Tuesday",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Atami offers the most complete all-season retirement proposition in the corridor. The centre combines a working city, restaurants, shops, rail and a waterfront rather than relying solely on a resort estate. Its major hospital says it supports Atami, Ito, western Kanagawa and the wider Izu Peninsula, with emergency care and multiple specialties. That depth matters more with age than a distant sea view. The qualification is topography: many homes sit on steep roads or steps above the station and coast. A property described as central can still turn groceries, taxis or an urgent hospital journey into a difficult climb.",
                "Hakone is a collection of small operating environments. Hakone-Yumoto is the rail gateway; Gora has the mountain railway and cable-car connection; Sengokuhara is flatter in places and has everyday shops, but depends heavily on buses and roads. The appeal is real—onsen, museums, forest and proximity to Tokyo—but the town’s visitor economy does not create urban healthcare or effortless late-life mobility. Test winter damp, summer humidity, road disruption, bus frequency after dinner and the route to a full hospital. An onsen home is a specialist lifestyle asset, not a substitute for a service base.",
                "Ito and Izu-Kogen sit between those cases. Ito has a municipal hospital, a station, shops and a resident economy; Izu-Kogen spreads villas, resort estates and attractions across hills above the Izukyu line. Shimoda adds beaches and a strong coastal identity but makes long journeys part of the bargain. Spend a weekday outside holiday season in every candidate location. Walk or drive to food, pharmacy, clinic and station; check whether one partner could manage alone; and ask what happens when driving is no longer comfortable. Retirement fit is the durability of that routine, not the quality of a weekend."
            ),
            "daily-life",
        ),
        DossierLens(
            "Measure the whole journey, then the language burden",
            ("global_access", "foreigner_fit"),
            (
                "Atami has the corridor’s strongest transport hinge because the Tokaido Shinkansen connects it to Tokyo while conventional rail continues toward Ito. That does not make every Atami address easy: the final kilometre may involve a steep bus route, taxi or private car. Hakone-Yumoto is about 80 minutes from Shinjuku on a direct Odakyu Romancecar, after which Gora, Sengokuhara and Lake Ashi require the mountain railway, cable car, bus or road. A buyer should time the door-to-door trip with luggage, a missed connection and evening arrival—not quote the fastest station-to-station headline.",
                "The eastern Izu rail spine becomes progressively more remote. Izukyu links Ito, Izu-Kogen, Atagawa, Kawazu and Izukyu-Shimoda, but many celebrated villa areas are not walkable from their named station. Izu-Kogen can mean a short station approach or a steep, car-led estate several kilometres away. Shimoda is the line’s southern terminus, not an extension of Atami convenience. Check the current timetable, last practical arrival, taxi availability, parking and road resilience. A home used frequently will expose every weak interchange; a home occupied full time will expose every necessary drive.",
                "Foreigner fit is strongest where professional help and transport are easiest to assemble, but binding work remains Japanese-led throughout the corridor. Purchase documents, municipal notices, condominium meetings, resort-estate rules, tax administration and contractor coordination may not be available in English. Non-resident property reporting to the Ministry of Finance is submitted in Japanese, and a remote owner needs someone to receive notices and inspect the home after storms. Budget for an independent bilingual lawyer, tax adviser and reliable local manager. International familiarity in a tourism district is useful, but it does not remove the operating language of ownership."
            ),
        ),
        DossierLens(
            "Own clearly, then investigate the difficult parts",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Japan’s general ability for foreigners to own land and buildings is the simple part. The transaction still requires a property-specific chain of evidence: title, liens, boundaries, legal road access, registered floor area, building approvals, utilities, easements, additions and tax treatment. A non-resident acquisition can require a Foreign Exchange and Foreign Trade Act report through the Bank of Japan within 20 days. Acquisition, registration, annual ownership and disposal can each create taxes; non-resident rental or sale income can require filings, withholding and a Japanese tax agent. Assign every obligation in writing before exchange.",
                "Older resort stock needs a deeper physical and governance review. For a condominium, read bylaws, reserve balance, arrears, major-repair plan, minutes, insurance, renovation rules, occupancy and any lodging prohibition. For a detached home, commission structural, moisture, termite, roof, retaining-wall, drainage and septic or sewer checks. In a managed villa estate, identify road, water, security and vegetation charges and whether membership or management obligations transfer. Where a listing includes hot-spring supply, verify the source, right or contract, transfer fee, basic charge, maintenance responsibility and interruption terms. A renovated interior proves none of those points.",
                "Hazards differ sharply by address. Hakone is an active volcanic area; the Japan Meteorological Agency revised its alert-level criteria in 2025, and the town publishes volcanic as well as landslide and flood maps. Atami’s current guide maps tsunami, landslide, flood, storm surge and volcanic risk, while its steep catchments make drainage and retaining structures material. Ito and the eastern coast require tsunami, slope and landslide checks; coastal Shimoda adds evacuation height and route. Overlay current official maps, walk the evacuation path, inspect after rain where possible and obtain an insurer’s terms before a binding offer."
            ),
        ),
        DossierLens(
            "Treat visitor demand as an operating business",
            ("rental_profit", "capital_upside"),
            (
                "The corridor has substantial tourism, but tourism volume is not net rental yield. Atami can combine leisure demand with a broader urban market; Hakone has a powerful onsen and weekend identity; Izu-Kogen and Shimoda attract seasonal coastal and nature stays. Each also creates operating friction: cleaning travel, key access, linen, guest communication, repairs, utilities, platform fees, vacancy and weather disruption. A home with difficult stairs, weak parking or a remote manager may underperform a less scenic address. Use dated, property-specific occupancy and rate evidence, then deduct every local cost rather than applying a regional headline.",
                "Permission is layered. Japan’s national private-lodging route caps minpaku at 180 nights a year, but prefectural, municipal, building and management rules can reduce or prevent use. Kanagawa tells prospective Hakone operators to confirm whether the exact home lies in a restricted area, and hot-spring or food service can require separate permissions. Shizuoka requires notification and says its ordinance can reduce the national maximum depending on location. Condominium bylaws and resort-estate contracts remain separate. Obtain a written answer for the address, operator, absence-management plan, fire safety, guest reporting, tax and transfer continuity before underwriting any income.",
                "Capital upside should come from access, daily utility and scarce property quality—not a generic Tokyo-weekend story. Atami’s rail and service base can support the broadest demand, while Hakone’s globally recognised tourism can support special homes but also produces high operating premiums. Ito and Izu-Kogen may offer inexpensive space, yet old stock, depopulation, deferred maintenance and abundant alternatives can cap appreciation. Shimoda’s beauty attracts committed buyers but its remoteness narrows them. Model a flat nominal resale after full buying, repair and selling costs. If the case fails without appreciation or holiday income, it is not a resilient retirement purchase."
            ),
            "coast-access",
        ),
        DossierLens(
            "Use official land evidence to challenge the asking price",
            ("value_entry", "exit_liquidity"),
            (
                "Official 1 January 2026 land-value observations show why a single corridor price is misleading. A high-ground Nishi-Atami villa-area site was assessed at 26,600 JPY/m²; a Hakone Miyagino villa-subdivision site at 20,500 JPY/m²; and a residential site near Ito’s Matsubara station area at 63,200 JPY/m². These are appraisals of specified bare-land sites, not built-home valuations, averages or transaction prices. Building age, legal access, slope, retaining works, utilities, hot-spring arrangements, management obligations and renovation can make a low total price expensive to own.",
                "The three current listing observations expose those differences. A small Atami apartment near the station asks more per square metre than a larger Hakone house, but the apartment offers a conventional, walkable format and transfers building risk into condominium governance. The Miyagino house provides far more space at a similar total ticket, with age, mountain access and upkeep to investigate. An Izu-Kogen house near the rail area asks a much higher total price and needs its condition, estate charges, route and future buyer justified. These are dated asking observations only; they are comparison prompts, not valuations or recommendations.",
                "Exit liquidity follows the operating system. A conventional Atami apartment near rail and services can reach retirees, second-home users and domestic buyers. A well-located Hakone home can attract Tokyo households, but singular architecture, access or large maintenance costs narrow the pool. Ito and Izu-Kogen resale improves near stations, services and straightforward roads; isolated or highly customised villas require more time and discount discipline. Shimoda depends on a buyer who wants the same remote coastal compromise. Before purchase, name that future buyer and estimate the marketing period and price reduction needed without an exceptional view-led story."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Atami combines city, coast and onsen; Hakone adds mountain culture, while Ito, Izu-Kogen and Shimoda deepen the nature-led lifestyle.",
        "global_access": "Atami has Shinkansen access and Hakone-Yumoto has direct Shinjuku trains; Izu-Kogen and Shimoda add progressively longer rail and road journeys.",
        "ownership_clarity": "Hakone and Izu follow Japan’s generally open ownership framework, while every title, boundary, road, building and non-resident reporting obligation still requires verification.",
        "regulatory_safety": "Hakone volcano rules and Kanagawa lodging limits differ from Atami, Ito and Shimoda procedures; slope, tsunami and building checks remain address-specific.",
        "rental_profit": "Atami and Hakone have strong visitor demand, but Ito, Izu-Kogen and Shimoda seasonality, permissions and remote operations constrain reliable net yield.",
        "capital_upside": "Atami access and Hakone scarcity support selected assets; abundant older Ito and Izu-Kogen stock makes appreciation highly property-specific.",
        "retirement_fit": "Atami offers the deepest transport and hospital base; Ito remains practical, while Hakone, Izu-Kogen and Shimoda need stronger mobility planning.",
        "exit_liquidity": "Atami station-area homes reach the broadest pool; specialised Hakone houses and remote Izu-Kogen or Shimoda villas demand more time and pricing discipline.",
        "foreigner_fit": "Atami and Hakone have tourism-facing services, but legal, tax, municipal, management and contractor work across Ito, Izu-Kogen and Shimoda remains Japanese-led.",
        "value_entry": "Low Hakone and Izu asking tickets can conceal age, access, estate fees and repairs; Atami’s higher unit price may buy broader daily utility.",
    },
    market_anchors=(
        {"location": "Atami · Nishi-Atami villa area", "evidence": "26,600 JPY/m²", "buyer_read": "Official land value at 1 January 2026 for a 420 m² high-ground residential site 4.2 km west of Atami Station. Bare land only; the appraisal notes a landslide-warning context.", "source_label": "MLIT Real Estate Information Library, 2026", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/22/2026222050003.html"},
        {"location": "Hakone · Miyagino villa subdivision", "evidence": "20,500 JPY/m²", "buyer_read": "Official land value at 1 January 2026 for a 485 m² villa-area site about 3.1 km from Gora. Bare land only; national-park and low-rise controls form part of its context.", "source_label": "MLIT Real Estate Information Library, 2026", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/14/2026143820001.html"},
        {"location": "Ito · Matsubara station area", "evidence": "63,200 JPY/m²", "buyer_read": "Official land value at 1 January 2026 for an established residential site near Ito Station. Bare land only; it is not an Izu-Kogen villa valuation or a built-home average.", "source_label": "MLIT Real Estate Information Library, 2026", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/22/2026222080002.html"},
    ),
    micro_locations_intro=(
        "Use four operating patterns rather than one Hakone / Izu average. Atami is the rail-and-hospital base; Hakone-Yumoto, Gora and Sengokuhara are distinct mountain systems; Ito and Izu-Kogen combine a working city with dispersed villa estates; Shimoda and the southern coast trade access for deeper coastal life. Confirm the exact gradient, road, parking, station or bus journey, hospital route, hot-spring or estate contract, hazard layers and likely future buyer for every address."
    ),
    micro_locations=(
        {"name": "Atami", "best_for": "Year-round services and Tokyo access", "daily_life": "Steep seaside city with rail and hospital depth", "diligence": "Slope, landslide, tsunami, building and fees"},
        {"name": "Hakone-Yumoto / Gora / Sengokuhara", "best_for": "Tokyo-adjacent onsen personal use", "daily_life": "Tourism-led mountain towns linked by rail, bus and road", "diligence": "Volcano, access, hot spring, damp and management"},
        {"name": "Ito / Izu-Kogen", "best_for": "Lower-entry east-coast space", "daily_life": "Rail spine with dispersed car-led villa estates", "diligence": "Older stock, estate charges, slope and resale"},
        {"name": "Shimoda / south Izu", "best_for": "Committed beach and nature lifestyle", "daily_life": "Small coastal city at the end of the rail line", "diligence": "Journey time, healthcare, tsunami and exit depth"},
    ),
    checklist=(
        "Confirm a renewable residence route, tax position, healthcare eligibility and private cover independently of the property purchase.",
        "Choose Atami city, Hakone mountain, Ito/Izu-Kogen or Shimoda daily life before comparing asking prices.",
        "Travel the exact station, bus, grocery and hospital routes with luggage, in rain and after dark; repeat without a car where relevant.",
        "Reconcile title, liens, boundaries, legal road access, registered floor area, approvals, utilities, additions and non-resident reporting.",
        "Read condominium or villa-estate governance, reserves, works, arrears, roads, water, vegetation, insurance and every transferable charge.",
        "Verify hot-spring rights or contracts, transfer and recurring fees, supply terms, equipment and interruption responsibility in writing.",
        "Overlay official volcano, landslide, flood and tsunami maps, inspect drainage and retaining structures, test evacuation and obtain insurance terms.",
        "Obtain a written rental answer, cost full repairs and five-year ownership, compare direct evidence and identify the likely resale buyer.",
    ),
    references_intro=(
        "Legal, tax, residence, healthcare, transport, rental, land-value and hazard claims were reviewed on 22 August 2026 against the primary sources below. The next scheduled review is 22 February 2027, or sooner if a cited law, municipal rule, alert level, transport service, hospital provision, land-value release or listing changes. Recheck every live source and obtain independent Japanese legal, tax, immigration, surveying, engineering, insurance and property-management advice for the exact buyer and address before signing. Listing observations are dated asking evidence only and do not verify availability, title, condition, legal use, transferability or completed value."
    ),
    references=(
        {"label": "Japan property guide", "url": "/countries/japan-property/"},
        {"label": "MOFA: long stay for sightseeing and recreation", "url": "https://www.mofa.go.jp/ca/fna/page22e_000738.html"},
        {"label": "Ministry of Finance: non-resident real-property reporting", "url": "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html"},
        {"label": "National Tax Agency: non-resident real-estate tax", "url": "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf"},
        {"label": "MLIT: real-estate transaction and tax guidance", "url": "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html"},
        {"label": "Japan Tourism Agency: Private Lodging Business Act", "url": "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html"},
        {"label": "Kanagawa Prefecture: private-lodging rules and Hakone confirmation", "url": "https://www.pref.kanagawa.jp/docs/e8z/cnt/f762/p1195197.html"},
        {"label": "Shizuoka Prefecture: private-lodging rules", "url": "https://www.pref.shizuoka.jp/kenkofukushi/eiseiyakuji/eiseionsen/1040424/1025059.html"},
        {"label": "Odakyu: Shinjuku to Hakone-Yumoto access", "url": "https://www.odakyu.jp/english/transport/timetable/"},
        {"label": "Izukyu: Ito, Izu-Kogen and Shimoda railway", "url": "https://www.izukyu.co.jp/global_site/index.php"},
        {"label": "IUHW Atami Hospital: emergency department", "url": "https://atami.iuhw.ac.jp/clinic/kyukyu.html"},
        {"label": "Ito Municipal Hospital", "url": "https://ito-shimin-hp.jp/"},
        {"label": "JMA: Hakone volcano monitoring and alerts", "url": "https://ds.data.jma.go.jp/svd/vois/data/tokyo/315_Hakoneyama/315_index.html"},
        {"label": "Hakone Town: volcanic hazard map", "url": "https://www.town.hakone.kanagawa.jp/www/genre/1000500000010/index.html"},
        {"label": "Atami City: current disaster and hazard guide", "url": "https://www.city.atami.lg.jp/kurashi/bousai/1011957/1000585.html"},
        {"label": "Ito City: tsunami disaster plan and mapping", "url": "https://www.city.ito.shizuoka.jp/material/files/group/5/itousibousai-tsunami-r5.pdf"},
        {"label": "MLIT: Hakone Miyagino 2026 land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/14/2026143820001.html"},
        {"label": "MLIT: Atami Nishi-Atami 2026 land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/22/2026222050003.html"},
        {"label": "MLIT: Ito Matsubara 2026 land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/22/2026222080002.html"},
        {"label": "European Central Bank: euro reference exchange rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("atami-hero", "/assets/hakone-izu-atami-hero.webp", "Atami city, railway and steep coast in soft morning light", "Atami is the corridor’s most complete rail-and-service base—but the gradient belongs in every property decision.", "hero"),
        DossierImage("daily-life", "/assets/hakone-izu-daily-life.webp", "Older residents walking near shops and a bus stop in a Hakone onsen town", "In Hakone, ordinary errands and the bus timetable matter as much as the onsen setting.", "wide"),
        DossierImage("coast-access", "/assets/hakone-izu-coast-access.webp", "Homes, railway and road on the steep eastern Izu coast", "Along eastern Izu, the station, road, slope and front door form one operating system.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Hakone and Izu through five destination lenses",
    assessment_intro="Here’s how Hakone and Izu score on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show a walkable Atami apartment, an older Hakone house and an Izu-Kogen villa case. JPY is primary; USD uses the recorded ECB-derived reference basis for comparison only.",
    market_anchors_intro="These are official land-value observations—not built-home valuations, market averages or asking-price targets. Each is a specified bare-land site at 1 January 2026; reconcile every candidate for its exact address, building, access, slope, legal history, utilities, management obligations and completed comparable evidence.",
    orientation_groups=(
        DossierOrientationGroup("Tokyo to Hakone mountain system", (("Shinjuku", "Odakyu gateway"), ("Hakone-Yumoto", "Mountain rail gateway"), ("Gora", "Rail and cable-car hub"), ("Sengokuhara", "Bus-and-road plateau"))),
        DossierOrientationGroup("Tokyo down the eastern Izu spine", (("Tokyo", "Shinkansen origin"), ("Atami", "Rail and service hinge"), ("Ito / Izu-Kogen", "City and villa coast"), ("Shimoda", "Southern terminus"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Journey time and usefulness depend on the current rail or bus timetable, road conditions, weather, luggage, gradient and exact address.",
    country_guide_url="/countries/japan-property/",
    country_guide_label="Japan property guide",
    rail_comparison="Compare Hakone and Izu with the full Atlas.",
)


LAKE_COMO_DOSSIER = PremiumDossierSpec(
    destination_id="lake-como",
    title="Lake Como Retirement Property Dossier",
    description="Assess Lake Como property for retirement through daily life, access, ownership, rental rules, hazards, value, resale, and current listings.",
    h1="Lake Como: choose the everyday lake before the view",
    lede=(
        "Lake Como is not one property market or one retirement experience. Como city provides rail, hospitals and an ordinary urban economy; Cernobbio and the lower western shore add polish close to those services; Tremezzina and Menaggio exchange some convenience for the central lake; Varenna and Bellagio create their own rail, ferry and road logic. A beautiful view can therefore sit above very different stairs, winter routines, maintenance burdens and resale pools. This dossier starts with the life and route a home must support, then tests whether the property earns its premium."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is favourable for a lifestyle-led buyer who chooses the practical lake first. Como city is the broadest retirement base because groceries, hospitals, rail and year-round civic life sit beneath the visitor economy. Cernobbio can preserve much of that access at a higher entry price. Menaggio and Tremezzina work for buyers who accept road and ferry dependence, older buildings and thinner winter services. Varenna has the unusual advantage of a rail station on the eastern shore, while Bellagio is more isolated despite its international name. The correct comparison is not simply town against town: it is the exact front door, gradient, parking or station walk, ferry dependency and future buyer pool.",
        "Property ownership does not create Italian residence or healthcare rights. EU and EEA citizens and several categories of lawfully resident non-EU nationals are exempt from Italy’s reciprocity check; other non-EU buyers may need reciprocity confirmed before purchase. For a non-working retirement route, Italy’s elective residence visa requires stable, sufficient resources and suitable accommodation, and it does not permit employment. A deed can help show accommodation but does not guarantee a visa. Public-healthcare access also follows nationality and residence status, not ownership. Confirm residence, tax and health cover before using the house as the foundation of a move.",
        "Proceed in this order: decide whether the household needs Como’s urban system, a rail-served eastern shore or the road-and-ferry central lake; test the route in bad weather and outside the visitor season; confirm residence, reciprocity, tax and healthcare; then reconcile title, cadastral plan, planning history, condominium records, utilities, access rights, hazards and insurability. Only after those checks should a buyer underwrite holiday income or pay a view premium. Lake Como can be an exceptional long-hold home, but it punishes buyers who treat scenery as a substitute for access, condition and exit discipline."
    ),
    lenses_intro="The five lenses below pair the Atlas’s ten dimensions around the decisions a Lake Como buyer actually makes. They explain the evidence in plain language; the complete score table appears once afterwards.",
    lenses=(
        DossierLens(
            "Live on the lake after the visitors leave",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Lake Como’s appeal is durable: water, mountains, historic centres, walking, food and proximity to Milan create more than a summer postcard. The retirement question is whether that appeal survives an ordinary Tuesday in November. Como city has the deepest year-round mix of shops, cultural life, neighbourhood services and public transport. Cernobbio remains close to that base. Central-lake towns such as Menaggio, Tremezzina and Bellagio retain local communities, but their commercial rhythm is more seasonal and the choice of daily services narrows as the address moves away from a town centre.",
                "Healthcare reinforces the distinction. ASST Lariana operates the Sant’Anna hospital emergency department at San Fermo della Battaglia, outside Como, around the clock. That is a regional asset, not proof that every lakeside home has an easy hospital journey. A central-lake resident may face a long road transfer, traffic, weather and a difficult final approach from the property. Varenna’s rail link does not solve every medical journey; Bellagio and the western shore remain strongly route-dependent. Test the exact trip to a general practitioner, pharmacy, diagnostic service and emergency care before assuming the lake is one healthcare catchment.",
                "The house can magnify or reduce those frictions. A lift, level entrance, covered parking, dry cellar, reliable heating and a walkable supermarket may matter more over ten years than an extra balcony. Old stone homes and converted villas can bring irregular stairs, humidity, shared access, weak insulation and complex common works. Hillside properties can turn a short map distance into repeated driving. Spend time at the address in rain and winter, carry groceries from the real parking point and ask whether one person could live there if the other stopped driving. That is the difference between a holiday proposition and a resilient retirement home."
            ),
            "daily-life",
        ),
        DossierLens(
            "Buy the route as carefully as the property",
            ("global_access", "foreigner_fit"),
            (
                "Como city has the clearest transport case. Trenord states that direct services from Como San Giovanni reach Milano Centrale in about 40 minutes, with roughly hourly departures on the highlighted route. That makes Milan’s rail network and wider services realistically usable, although the door-to-door airport journey still requires a transfer or road leg. The lower lake also benefits from proximity to the A9 corridor. Cernobbio can be close in kilometres yet slower at peak periods, and a home above town may add narrow roads and parking constraints that disappear from a destination-level access score.",
                "The central lake works differently. Navigazione Laghi publishes seasonal Lake Como timetables and operates the Bellagio–Cadenabbia–Varenna–Menaggio ferry network. Ferries are a genuine mobility asset and part of the pleasure of living here, but seasonal timetables, weather and the distance from the landing matter. Varenna connects to the eastern-shore railway, while Menaggio and Tremezzina rely more heavily on roads and ferries. Bellagio occupies a celebrated but less direct position between the branches. A route that is delightful in July may be inconvenient with luggage, a missed boat or a medical appointment in winter.",
                "Foreign buyers will find an established international property and service ecosystem, particularly around Como, Cernobbio, Menaggio and Bellagio. That does not make the transaction English-led. The notarial deed, cadastral records, municipal planning, condominium decisions, tax filings and many contractor relationships remain Italian. Hire an independent notary and legal adviser, obtain translated explanations before commitments become binding, and appoint a local person to monitor notices and urgent work when absent. Foreigner fit is highest where the buyer combines international support with a functioning Italian administrative plan, not where a sales process merely feels familiar."
            ),
        ),
        DossierLens(
            "Separate the right to buy from the right to use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Italy permits broad foreign ownership, but nationality and residence status still matter. The Ministry of Foreign Affairs explains that EU and EEA citizens and specified categories of regularly resident non-EU citizens do not need a reciprocity check; other non-EU buyers may need confirmation that Italians enjoy equivalent rights in the buyer’s country. Resolve that before signing a binding proposal. The purchase process then needs the usual Italian controls: title, liens, cadastral conformity, planning permissions, legal floor area, rights of way, condominium debts, energy documentation and the seller’s authority to transfer every element represented in the listing.",
                "Lake properties add building-specific complications. Villas may include terraces, docks, retaining walls, access roads or outbuildings whose legal status and maintenance responsibility need documentary proof. Apartments in historic buildings require close reading of condominium minutes, reserve decisions, façade and roof plans, allocation tables, heating arrangements and restrictions on alterations or tourist use. A renovated interior does not establish planning conformity, dry construction or sound common parts. Ask a locally experienced surveyor to reconcile the property on site against municipal and cadastral records, and obtain costed answers for anything that remains unresolved.",
                "Hazards are also address-level. Lombardia’s Geoportal publishes current flood-risk mapping, and municipal geological planning records cover instability that can include floods, landslides and slope conditions. Lakefront levels, streams, steep ground, rockfall, drainage and retaining structures vary within the same village. Review official layers, the Comune’s planning and geological documents, historic claims and an insurer’s terms before exchange. Then inspect how water leaves the site and who owns the road, wall or slope above it. A scenic terrace below a steep catchment needs more diligence than a generic regional risk label can provide."
            ),
        ),
        DossierLens(
            "Treat rental income as permission plus operations",
            ("rental_profit", "capital_upside"),
            (
                "Lake Como has powerful visitor demand, but a recognisable name does not produce automatic net yield. Occupancy, achievable rate and season length differ between Como city, Cernobbio, Menaggio, Tremezzina, Varenna and Bellagio. Hillside access, parking, air-conditioning, outdoor space and the walk to a ferry or centre influence both bookings and management cost. A premium view can support rates, but staffing, cleaning, linen, guest access, utilities, platform fees, maintenance and empty periods reduce the headline. Underwrite a personally usable home first and treat rental performance as a property-specific operating business.",
                "The permission stack is national, regional, municipal and building-specific. Italy’s national BDSR system assigns the CIN identification code to tourist accommodation and short lets; Ministry guidance says the code must be displayed and included in advertisements, while regional codes remain relevant. Lombardia also requires its regional process, and the Comune di Como distinguishes non-business tourist letting from business activity and directs operators to the relevant communication or SCIA route. Other lakeside comuni administer their own files. Condominium rules, safety equipment, guest reporting and tax obligations remain separate checks. A CIN is not a substitute for lawful use of the exact property.",
                "Capital upside should therefore rest on scarcity and daily utility rather than assumed holiday income. Como city benefits from a broad resident and Milan-linked market. Cernobbio and the central lake have global recognition and constrained geography, but high entry prices already capitalise much of that appeal. Singular villas may rise strongly in a favourable market yet require long marketing periods and expensive presentation. Older apartments can offer a lower ticket but may face major works or limited accessibility. Model a flat nominal resale, full buying and selling costs, and a renovation reserve; treat any appreciation as the result of buying the right asset, not a destination guarantee."
            ),
            "central-lake",
        ),
        DossierLens(
            "Use public ranges to challenge the asking price",
            ("value_entry", "exit_liquidity"),
            (
                "The official OMI database is useful because it shows how sharply values vary by zone and property type. For 2025’s second half, the normal-condition civil-home range in Como’s Città Murata B1 zone was 2,900–4,200 EUR/m²; Menaggio’s Lungo Lario B5 zone showed 1,750–2,200 EUR/m²; Bellagio’s coastal B1 zone showed 1,350–2,000 EUR/m². Those are administrative zone ranges, not valuations, and they do not capture every view, renovation or trophy premium. Their purpose is to force a clear explanation when an asking price sits far above broad official context.",
                "The three current listing observations make that comparison concrete. A Como Borghi apartment asks more per square metre than its simple urban description might suggest, but it offers newer construction, a lift and a city service base. A smaller Menaggio apartment also asks well above the broad OMI civil-home range, with renovation and centrality offset by an old building, no lift and weak energy performance. A Tremezzina house offers more space at a lower unit price, but its road setting, completion record, garden, systems and eventual maintenance need closer verification. None is a valuation or recommendation; each shows why property facts matter more than a lake-wide average.",
                "Exit liquidity follows the same logic. A conventional Como apartment near services and rail can reach residents, commuters, domestic investors and international buyers. A walkable Menaggio or Varenna home may appeal across personal-use and visitor markets if access and condition are straightforward. A remote or highly individual hillside villa depends on a narrower buyer with the budget and appetite for the same compromises. Before buying, name that future buyer, compare the legal area and condition with completed evidence, and estimate the time and discount needed to sell without an exceptional view-led marketing story."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Lake Como combines water, mountains and historic towns; Como city adds the deepest year-round cultural and daily-service base.",
        "global_access": "Como has direct Milan rail; Varenna has eastern-shore rail, while Menaggio, Tremezzina and Bellagio depend more on road and seasonal ferry links.",
        "ownership_clarity": "Lake Como follows Italy’s established conveyancing system, but non-EU reciprocity and property-level cadastral, planning and access conformity require confirmation.",
        "regulatory_safety": "Como and every lakeside comune apply local files within national and Lombardia rules; flood, landslide, slope and tourist-use checks remain address-specific.",
        "rental_profit": "Lake Como visitor demand is strong, but CIN, regional and municipal compliance, seasonality, access and management costs constrain net rental performance.",
        "capital_upside": "Como’s resident economy and Lake Como’s global scarcity support demand, although high entry prices already reflect much of the destination premium.",
        "retirement_fit": "Como city offers the broadest services and hospital access; Menaggio, Tremezzina, Varenna and Bellagio require more route and winter planning.",
        "exit_liquidity": "Como apartments reach the broadest buyer pool; singular Lake Como villas and car-dependent hillside homes require more time and pricing discipline.",
        "foreigner_fit": "Lake Como has international advisers and agents, but binding notarial, tax, municipal and condominium work remains Italian-led.",
        "value_entry": "Como, Menaggio and Bellagio show wide official OMI ranges; view, renovation, lift, access and future buyer depth determine whether a premium is justified.",
    },
    market_anchors=(
        {"location": "Como · Città Murata B1", "evidence": "OMI 2,900–4,200 EUR/m²", "buyer_read": "2025 H2 normal-condition civil-home zone range. Better-condition and prestigious categories run higher; this is not a property valuation.", "source_label": "Agenzia delle Entrate OMI, 2025 H2", "source_url": "https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm"},
        {"location": "Menaggio · Lungo Lario B5", "evidence": "OMI 1,750–2,200 EUR/m²", "buyer_read": "2025 H2 normal-condition civil-home zone range. Villas and renovated lake-facing homes use different evidence and can price materially above it.", "source_label": "Agenzia delle Entrate OMI, 2025 H2", "source_url": "https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm"},
        {"location": "Bellagio · coastal B1", "evidence": "OMI 1,350–2,000 EUR/m²", "buyer_read": "2025 H2 normal-condition civil-home zone range. The range combines neither trophy views nor verified condition, access and legal conformity.", "source_label": "Agenzia delle Entrate OMI, 2025 H2", "source_url": "https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm"},
    ),
    micro_locations_intro="Use four operating patterns rather than a single Lake Como average. Como city and Cernobbio form the lower-lake service base; Tremezzina and Menaggio are the road-and-ferry western centre; Varenna is the eastern rail-and-ferry hinge; Bellagio is the iconic but less direct central-lake choice. Confirm the exact gradient, parking, station or landing walk, winter services, hospital route, municipal file, hazards and likely future buyer for every address.",
    micro_locations=(
        {"name": "Como city / Cernobbio", "best_for": "Year-round services and Milan access", "daily_life": "Urban or lower-lake routine with deepest support", "diligence": "Traffic, parking, flood, lift and price premium"},
        {"name": "Tremezzina / Menaggio", "best_for": "Central-lake life on the western shore", "daily_life": "Ferry access with stronger road dependence", "diligence": "Seasonality, old buildings, slopes and hospital route"},
        {"name": "Varenna / eastern shore", "best_for": "Rail-and-ferry central-lake access", "daily_life": "Compact villages linked to the eastern railway", "diligence": "Stairs, parking, train noise, rockfall and winter service"},
        {"name": "Bellagio", "best_for": "Iconic central-lake personal use", "daily_life": "Strong visitor ecosystem with indirect access", "diligence": "Ferry dependence, road time, premium and resale depth"},
    ),
    checklist=(
        "Confirm nationality-specific reciprocity, residence, tax and healthcare before linking the purchase to an Italian retirement plan.",
        "Choose Como urban, western road-and-ferry, eastern rail-and-ferry or Bellagio daily life before comparing listings.",
        "Travel the airport, hospital, grocery, station or ferry route from the exact door in winter, rain and visitor traffic.",
        "Reconcile title, liens, cadastral plan, planning history, legal floor area, access rights, utilities and every represented outbuilding.",
        "Read condominium minutes, works, debts, allocation tables, heating, lift and tourist-use rules; survey villas, walls, docks and slopes.",
        "Check official flood and geological layers, drainage, lake or stream exposure, landslide and rockfall context, then obtain an insurance quotation.",
        "Obtain a written short-let answer covering CIN, Lombardia, the exact comune, guest reporting, safety, tax and the condominium.",
        "Compare asking evidence with the correct OMI zone and local transactions, model full five-year costs, and identify the likely resale buyer.",
    ),
    references_intro="Legal, tax, residence, healthcare, transport, market, planning, hazard and rental claims were reviewed on 22 August 2026 against the primary sources below. The next scheduled review is 22 February 2027, or sooner if a cited law, municipal rule, tax table, transport service, hazard source, OMI release or listing changes. Recheck every live source and obtain independent Italian notarial, legal, tax, immigration, planning, engineering and insurance advice for the exact buyer and property before signing. Listing observations are dated asking evidence only and do not verify availability, title, condition, legal use, transferability or completed value.",
    references=(
        {"label": "Italy property guide", "url": "/countries/italy-property/"},
        {"label": "Italian Foreign Ministry: reciprocity and foreign buyers", "url": "https://www.esteri.it/en/temi/diplomazia_giuridica/condizreciprocita/"},
        {"label": "Italian Foreign Ministry: elective residence visa", "url": "https://conslondra.esteri.it/en/servizi-consolari-e-visti/servizi-per-il-cittadino-straniero/visti/elective-residence/"},
        {"label": "Italian Revenue Agency: guide to buying a home", "url": "https://www1.agenziaentrate.gov.it/web_app_entrate/guida_acquisto_casa.html"},
        {"label": "Italian Revenue Agency: OMI property-market database", "url": "https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.htm"},
        {"label": "Italian Health Ministry: foreign citizens and the SSN", "url": "https://www.salute.gov.it/new/it/tema/iscrizione-al-ssn/iscrizione-dei-cittadini-stranieri-al-servizio-sanitario-nazionale-ssn/"},
        {"label": "Italian Tourism Ministry: BDSR and CIN FAQ", "url": "https://www.ministeroturismo.gov.it/faq-banca-dati-strutture-ricettive-bdsr/"},
        {"label": "Lombardia: non-hotel accommodation and tourist letting", "url": "https://www.regione.lombardia.it/cultura-turismo-e-sport/imprese-e-professioni-turistiche/strutture-ricettive-non-alberghiere"},
        {"label": "Comune di Como: tourist letting procedure", "url": "https://su.comune.como.it/su_procedimento/turismo-locazione-turistica/"},
        {"label": "Trenord: Como San Giovanni to Milano Centrale", "url": "https://www.trenord.it/en/routes-and-timetables/most-searched-lines/como-s-giovanni-milano-centrale-route/"},
        {"label": "Navigazione Laghi: Lake Como timetables", "url": "https://www.navigazionelaghi.it/en/tickets-and-timetables-lake-como/"},
        {"label": "ASST Lariana: Sant’Anna emergency department", "url": "https://asst-lariana.it/v2/2/uo/?display=0&uo=157"},
        {"label": "Lombardia Geoportal: current flood-risk mapping", "url": "https://www.geoportale.regione.lombardia.it/it/metadati?_detailSheetMetadata_WAR_gptmetadataportlet_identifier=r_lombar%3A9913a827-9889-4160-a50b-d483fdc5e719&_jsfBridgeRedirect=true&p_p_id=detailSheetMetadata_WAR_gptmetadataportlet&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal"},
        {"label": "Comune di Como: planning and territorial government", "url": "https://www.comune.como.it/amministrazione-trasparente/pianificazione-e-governo-del-territorio/index.html"},
        {"label": "Comune di Como: current building regulation", "url": "https://comune.como.it/amministrazione-trasparente/pianificazione-e-governo-del-territorio/regolamento-edilizio.html"},
        {"label": "European Central Bank: euro reference exchange rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("lower-lake", "/assets/lake-como-lower-lake-hero.webp", "Como city and the lower basin of Lake Como in soft morning light", "The lower lake places urban services and rail beneath the scenery.", "hero"),
        DossierImage("daily-life", "/assets/lake-como-daily-life.webp", "Residents walking through a Lake Como town near everyday shops", "A workable lake home starts with ordinary errands, access and winter life.", "wide"),
        DossierImage("central-lake", "/assets/lake-como-central-lake.webp", "A ferry approaching a central Lake Como village beneath steep slopes", "At the central lake, ferries, roads, gradients and the front door form one decision.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Lake Como through five destination lenses",
    assessment_intro="Here’s how Lake Como scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show distinct buyer cases in Como city, central Menaggio and road-led Tremezzina. EUR is primary; USD uses the recorded ECB reference basis for comparison only.",
    market_anchors_intro="These are official OMI zone ranges—not property valuations, transaction averages or asking-price targets. They are broad 2025 H2 checks on location and asset type; reconcile every candidate for exact zone, condition, legal area, view, access and completed comparable evidence.",
    orientation_groups=(
        DossierOrientationGroup("Western shore and lower-lake road", (("Como city", "Rail and service base"), ("Cernobbio", "Lower-lake premium"), ("Tremezzina", "Road-and-ferry lake"), ("Menaggio", "Central western hub"))),
        DossierOrientationGroup("Eastern rail and central ferry", (("Lecco", "Eastern service base"), ("Varenna", "Rail-and-ferry hinge"), ("Bellagio", "Central-lake destination"), ("Menaggio", "Cross-lake connection"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Rail, road and ferry usefulness depends on the current timetable, weather, traffic, gradient, parking and exact address.",
    country_guide_url="/countries/italy-property/",
    country_guide_label="Italy property guide",
    rail_comparison="Compare Lake Como with the full Atlas.",
)


VALENCIA_DOSSIER = PremiumDossierSpec(
    destination_id="valencia",
    title="Valencia Retirement Property Dossier",
    description="Assess Valencia retirement property through daily life, access, foreign ownership, rental rules, heat and flood risk, value, resale, and representative listings.",
    h1="Valencia: Mediterranean city life that works year-round",
    lede=(
        "Valencia is one of Europe’s strongest all-round retirement-property candidates: a substantial city with beaches, food culture, healthcare, an airport and fast rail rather than a resort that must imitate normal life. The attraction is real, but the address decides the outcome. A Russafa apartment, an El Pla del Real home beside the Turia gardens, an El Cabanyal-Canyamelar flat and a Patacona sea-view property carry different heat, noise, rental, building and resale assumptions. This dossier turns the broad Valencia story into a buyer’s sequence of decisions."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is positive for a buyer seeking a genuine city home with Mediterranean access, provided the purchase works without creating residence or depending on tourist rent. Buying Spanish property does not itself grant a right to live in Spain. The property-linked investor-residence route ended on 3 April 2025, so a prospective retiree must establish a separate lawful route—often the non-lucrative residence route for a non-working applicant—and confirm income, insurance, renewal and tax consequences before committing. Healthcare entitlement also follows residence and social-security status, not the deed. Those are plan-first questions, not closing formalities.",
        "Valencia best suits someone who wants ordinary urban life: markets, restaurants, parks, hospitals, public transport and the sea within one metropolitan area. It can support a car-light routine in central and tram-served districts, and its resident economy gives well-located homes a broader purpose than holiday demand alone. It is less suitable for a buyer who expects unrestricted short-stay letting, treats every coastal address as walkable, cannot tolerate hot summers, or wants a detached villa without accepting suburban driving and a different resale pool.",
        "Proceed in this order: establish residence, healthcare and tax advice; choose the daily-life pattern; inspect the building and community; verify the exact permitted use in writing; overlay flood and heat exposure; then compare the price with public market signals and realistic resale demand. The strongest purchase is usually a comfortable, accessible home that still makes sense as a long-term residence. A tourist licence, sea glimpse or renovation aesthetic should never substitute for that core case."
    ),
    lenses_intro="The five paired lenses below translate the Atlas model into practical choices. The complete ten-dimension assessment appears once in the score table; the prose explains what changes between Valencia’s centre, park edge, maritime districts and northern beach.",
    lenses=(
        DossierLens(
            "Choose the life before the postcode",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Valencia’s principal advantage is that retirement life is not confined to a waterfront strip. The historic centre and Eixample provide shops, food markets, culture and dense services. Russafa is energetic and restaurant-rich, but nightlife, traffic and older buildings make exact-street testing essential. El Pla del Real and the Turia gardens offer a calmer park-led pattern close to universities and established neighbourhood services. Farther east, El Cabanyal-Canyamelar brings tiled façades, local commerce and proximity to the sea, while Malvarrosa feels more overtly beach-facing. Patacona continues the promenade into Alboraya, but the municipal boundary and transport pattern change.",
                "Retirement fit depends less on postcard distance than on the repeat journeys. Map the walk to groceries, pharmacy, primary care and a useful bus, metro or tram stop. Test the lift, entrance steps, pavement shade and late-evening route. Valencia’s La Fe health department provides major hospital and primary-care services, but a pleasant neighbourhood still needs a realistic route to the right facility. A beach home may be level and sociable; it may also be windier, salt-exposed and farther from specialist care. A central apartment may be convenient; it may also be noisy, dark or difficult to cool.",
                "Summer is the honest viewing season. Inspect bedroom orientation, cross-ventilation, shutters, air-conditioning capacity, insulation and the cost of cooling. Valencia maintains a network of climate refuges, which is useful civic infrastructure but not a cure for a heat-trapping home. Return in winter to check damp, daylight and how the promenade or street functions outside peak season. The goal is not the most animated district on a three-day visit. It is an address where meals, movement, healthcare and friendships remain easy when the weather is less flattering and mobility becomes more valuable."
            ),
            "daily-life",
        ),
        DossierLens(
            "Connect the whole journey, not just the airport",
            ("global_access", "foreigner_fit"),
            (
                "Valencia Airport and the metropolitan rail network make the city internationally workable. Aena publishes the airport’s current destination list; Metrovalencia connects the airport to central interchanges, while the city’s bus and tram systems distribute journeys across the urban area. High-speed and long-distance services use Joaquín Sorolla station, close to but separate from Estació del Nord. Adif describes the station as about 800 metres south of Nord, and current access works can alter approaches. A buyer should time the actual door-to-platform journey with luggage rather than rely on a city-level access score.",
                "The centre and Eixample make daily car-free living easiest. El Pla del Real benefits from buses, cycle routes and proximity to the Turia. El Cabanyal-Canyamelar and Malvarrosa have tram and bus options, but the useful line depends on the exact block and destination. Patacona lies in Alboraya: it remains visually continuous with Valencia’s beach, yet local administration and the last kilometre deserve separate checking. For any outer address, test the morning hospital journey, the late return from Joaquín Sorolla and the airport trip during service disruption. A ten-minute map estimate is not the same as resilient access.",
                "Foreign buyers will find international services and a sizeable expatriate community, but integration still rewards Spanish—and sometimes Valencian—language capacity. Reservation contracts, community minutes, planning certificates, tax notices, utilities and contractor discussions may not arrive in English. Appoint an independent lawyer, tax adviser and surveyor rather than relying on the selling chain. Keep a local contact able to receive notices and enter the property. Valencia’s openness is a genuine advantage; the best foreigner fit comes from combining that welcome with professional translation and an effort to participate in the resident neighbourhood."
            ),
        ),
        DossierLens(
            "Own the home—and prove how it may be used",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Foreigners can generally buy Spanish real estate, but a clean purchase requires more than checking the seller’s name. Obtain a current Land Registry extract, compare it with the cadastre and physical property, investigate debts and charges, confirm planning status and legal floor area, and read the community statutes and minutes. For an apartment, scrutinise façade, roof, lift, structural, accessibility and energy works as well as arrears and approved assessments. For a renovated home, verify permissions and completion. Use a technical survey even when the building looks polished; attractive finishes can conceal old services, moisture or unauthorised alterations.",
                "Tourist use is a property-level legal question. The Valencian Community’s Decree-Law 9/2024 changed the regional framework, while Valencia City approved restrictive planning rules in 2026. The city describes neighbourhood caps, location conditions such as ground or first-floor placement with independent access, and community approval requirements; its procedure also requires a favourable planning-compatibility answer or the prescribed evidence of a pending request. Rules and transitional positions can change. Do not advertise, value or finance a home on short-stay income until an independent lawyer has confirmed the exact address, registration, planning status, community consent and operating obligations in writing.",
                "Physical risk is just as local. Valencia’s municipal emergency planning and the Generalitat’s PATRICOVA material should be checked alongside Spain’s national flood-zone system. Review river, coastal and pluvial flood layers, basement and garage exposure, street drainage, evacuation routes and the building’s loss history. Ask what happened during severe rainfall, but verify answers against documents and an insurance quotation. Heat deserves its own assessment: shading, top-floor exposure, mechanical systems and power costs can materially change comfort. Regulatory safety means the legal use, the building and the hazard profile all work together; a clear title alone is insufficient."
            ),
        ),
        DossierLens(
            "Underwrite resident demand before visitor demand",
            ("rental_profit", "capital_upside"),
            (
                "Valencia’s investment resilience starts with a large resident city, universities, employment, transport and year-round demand—not with a holiday calendar. For a rental case, compare ordinary long-term or legally suitable medium-term demand with vacancy, management, tax, community charges, maintenance and tenant regulation. Then model tourist use only if the exact property has a current, transferable and operationally viable legal path. A high nightly rate is irrelevant when planning, community or registration rules prevent the use. The base case should remain acceptable if short-stay revenue is zero.",
                "Public data provide useful scale but not a valuation. Valencia City’s official Q3 2025 series reported 2,725.90 EUR/m² for total free housing and 3,078.20 EUR/m² for homes up to five years old. The Registradores Q1 2026 report placed the Valencia province average for registered housing at 1,716 EUR/m². These measures cover different geographies, periods and property mixes, so the gap is information rather than contradiction. Compare the candidate with the correct district, age, condition and legal area, then seek recent completed evidence and a lender appraisal if financing.",
                "Capital upside is plausible but must be earned through entry discipline. Transit, the Turia, walkable services and high-quality urban fabric can support enduring buyer demand. Russafa’s popularity, El Pla del Real’s established character, Cabanyal’s continuing change and Patacona’s beach premium are different theses, not one rising-market story. Planning works, street quality, building condition and future supply can alter each block. Model flat real prices, higher community costs and a longer resale period. Appreciation should be a benefit of owning a good home in a useful location, never the mechanism that repairs an optimistic purchase price."
            ),
            "coast-access",
        ),
        DossierLens(
            "Pay for utility and preserve the exit",
            ("value_entry", "exit_liquidity"),
            (
                "The representative listings below show why a city average cannot price Valencia. A large Russafa apartment, a smaller El Cabanyal home and a Patacona sea-view property ask buyers to pay for different combinations of space, building quality, neighbourhood energy and coastal scarcity. They are dated asking observations, not completed sales or valuations. Verify legal floor area, terrace treatment, lift access, community charges, energy performance and renovation scope, then compare each with completed transactions and an independent appraisal. Apparent value per square metre can disappear when unusable area or major works are corrected.",
                "Preserve resale by choosing attributes that a broad resident buyer pool understands: comfortable layout, lift or level access, natural light without intolerable heat, manageable fees, sound building governance, useful transport and an address that works all year. Russafa can offer depth but buyers may discount noise and parking. El Pla del Real has established utility but commands a different entry level. El Cabanyal-Canyamelar can combine character and sea access, yet building-by-building diligence is decisive. Patacona may attract lifestyle buyers, but a premium narrows the pool and should be justified by view, orientation, access and construction quality.",
                "Model five-year cash outlay in euros: purchase taxes, notary, registry, legal and technical advice, financing, insurance, community charges, cooling, repairs, renovations, tax administration and eventual sale costs. Add currency stress if income or capital is elsewhere. Before signing, ask two agents who did not source the home who would buy it next, what comparable completed evidence supports the range, and which defect would slow the sale. The right Valencia property is not the most romantic listing; it is the one whose daily usefulness and future buyer pool remain aligned after the novelty fades."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Valencia combines a resident city, Turia park and coast; Russafa energy and Patacona calm suit different daily routines.",
        "global_access": "Valencia Airport, Metrovalencia and Joaquín Sorolla rail are strong, but Patacona and outer addresses add last-mile friction.",
        "ownership_clarity": "Valencia follows Spain’s open purchase framework, while every apartment still needs registry, cadastre, community and alteration checks.",
        "regulatory_safety": "Valencia tourist-use rules, community approval and address-level flood exposure make written property-specific clearance essential.",
        "rental_profit": "Valencia has year-round resident demand; Russafa or Cabanyal tourist income belongs only in a fully verified legal case.",
        "capital_upside": "Valencia infrastructure supports demand, but Cabanyal change and Patacona scarcity do not justify automatic appreciation assumptions.",
        "retirement_fit": "Valencia offers healthcare, flat districts and daily services; summer heat and the exact hospital route still need testing.",
        "exit_liquidity": "Valencia apartments with lifts, transit and broad layouts should resell more easily than compromised or premium-only Patacona stock.",
        "foreigner_fit": "Valencia is internationally accessible, but Spanish-language legal, community, tax and contractor support remains part of responsible ownership.",
        "value_entry": "Valencia value changes sharply between Russafa, El Pla del Real, Cabanyal and Patacona, so city averages require local correction.",
    },
    market_anchors=(
        {"location": "Valencia city — total free housing", "evidence": "2,725.90 EUR/m²", "buyer_read": "Official Q3 2025 appraisal series for the municipality; a broad market signal, not an address-level valuation.", "source_label": "Valencia City statistics / MIVAU", "source_url": "https://www.valencia.es/estadistica/UltDatos/PrecioVivienda_val.pdf"},
        {"location": "Valencia city — homes up to five years old", "evidence": "3,078.20 EUR/m²", "buyer_read": "Official Q3 2025 appraisal series for newer homes; age is only one adjustment and does not price view, district or condition.", "source_label": "Valencia City statistics / MIVAU", "source_url": "https://www.valencia.es/estadistica/UltDatos/PrecioVivienda_val.pdf"},
        {"location": "Valencia province — all registered housing", "evidence": "1,716 EUR/m²", "buyer_read": "Q1 2026 registered-price average across the province; wider geography explains why it cannot appraise a Valencia-city home.", "source_label": "Registradores Q1 2026 report", "source_url": "https://www.registradores.org/documents/d/guest/eri-2026_1t"},
    ),
    micro_locations_intro="Valencia is best read as four daily-life patterns rather than one market. These are orientation aids, not pricing zones; confirm municipal boundary, transport, planning, community rules, legal area, hazards and building condition for the exact address.",
    micro_locations=(
        {"name": "Eixample / Russafa", "best_for": "Food and central energy", "daily_life": "Walkable, animated and urban", "diligence": "Noise, lift, heat and building works"},
        {"name": "El Pla del Real / Turia", "best_for": "Park-led city living", "daily_life": "Established and service-rich", "diligence": "Entry premium and exact transit"},
        {"name": "El Cabanyal-Canyamelar / Malvarrosa", "best_for": "Character near the sea", "daily_life": "Maritime district with tram and buses", "diligence": "Building condition and permitted use"},
        {"name": "Patacona / Alboraya", "best_for": "Promenade and beach outlook", "daily_life": "Coastal and municipality-specific", "diligence": "Premium, salt, access and resale depth"},
    ),
    checklist=(
        "Confirm residence, healthcare and Spanish tax consequences before choosing the property.",
        "Choose the centre, Turia, maritime or Patacona daily-life pattern and test it in summer and winter.",
        "Verify Land Registry, cadastre, planning, legal area, charges and every alteration.",
        "Read community statutes, minutes, accounts, works, arrears, access and tourist-use decisions.",
        "Survey structure, services, damp, cooling, energy performance and salt exposure where relevant.",
        "Check municipal, PATRICOVA and national flood layers, drainage history and insurability.",
        "Obtain a written address-specific answer for any rental or tourist use before underwriting income.",
        "Compare current asking evidence with completed sales, full five-year costs and the likely resale buyer.",
    ),
    references_intro="Legal, tax, residence, healthcare, transport, market, planning, hazard and rental claims were reviewed on 22 August 2026 against the primary sources below. The next scheduled review is 22 February 2027, or sooner if a cited law, municipal rule, transport service, hazard source, market data release or listing changes. Recheck every live source and obtain independent Spanish legal, tax, immigration, planning, technical and insurance advice for the exact buyer and property before signing. Listing observations are dated asking evidence only and do not verify availability, title, condition, permitted use, negotiability or completed value.",
    references=(
        {"label": "Spain retirement property guide", "url": "/spain-retirement-property-foreign-buyers/"},
        {"label": "Spanish Migration Ministry: non-lucrative residence", "url": "https://www.inclusion.gob.es/en/web/migraciones/w/autorizacion-inicial-de-residencia-temporal-no-lucrativa"},
        {"label": "Spanish Government: investor residence ended 3 April 2025", "url": "https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/vivienda-agenda-urbana/Paginas/2025/020425-fin-golden-visa.aspx"},
        {"label": "Spanish Tax Agency: individual tax residence", "url": "https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/residencia-personas-fisicas-juridicas/persona-fisica-residente-espana.html"},
        {"label": "Spanish Tax Agency: non-resident property taxation", "url": "https://sede.agenciatributaria.gob.es/Sede/vivienda-otros-inmuebles/no-residentes-tributacion-inmuebles.html"},
        {"label": "Spanish Tax Agency: VAT or transfer tax on a home", "url": "https://sede.agenciatributaria.gob.es/Sede/iva/iva-operaciones-inmobiliarias/compro-vivienda-tengo-que-pagar-itp.html"},
        {"label": "Spanish Property Registrars: buyer guides and registry information", "url": "https://www.registradores.org/gl/documentacion-y-descargas/guias-rapidas"},
        {"label": "BOE: community approval rule for tourist use", "url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-11152"},
        {"label": "Generalitat Valenciana: Decree-Law 9/2024 tourist housing", "url": "https://www.turisme.gva.es/opencms/opencms/turisme/es/contents/home/noticia/noticia_1725542158000.html"},
        {"label": "Generalitat Valenciana: current tourist-housing FAQ", "url": "https://www.turisme.gva.es/turisme/es/files/pdf/FAQ_viviendas_uso_turistico.pdf"},
        {"label": "Valencia City: 2026 tourist-apartment rules and enforcement", "url": "https://www.valencia.es/cas/actualidad/-/content/val%C3%A8ncia-multiplica-%C3%B3rdenes-cierre-apartamentos-tur%C3%ADsticos-irregulares"},
        {"label": "Valencia City: tourist-housing planning procedure", "url": "https://sede.valencia.es/sede/registro/procedimiento/UA.AT.50?lang=1"},
        {"label": "Aena: Valencia Airport destinations", "url": "https://www.aena.es/en/valencia/airlines-destinations/airport-destinations.html"},
        {"label": "Adif: Valencia Joaquín Sorolla station", "url": "https://www.adif.es/w/03216-valencia-joaquin-sorolla"},
        {"label": "Metrovalencia: official zonal map", "url": "https://www.metrovalencia.es/wp-content/uploads/2023/03/Plano-zonal-tarifario-Metrovalencia-.pdf"},
        {"label": "La Fe: emergency and hospital services", "url": "https://lafe.san.gva.es/es/urgencias"},
        {"label": "Valencia City: climate-refuge network", "url": "https://www.valencia.es/documents/20142/424002/20240802%2BInformacion%2B%2BXarxa%2Bde%2BRefugis%2BClima%CC%80tics%2Bde%2BVale%CC%80ncia_cast.pdf/275c1287-c90f-e5bd-cea9-649efac00b4a?t=1722603141185"},
        {"label": "Valencia City: civil-protection and flood plans", "url": "https://www.valencia.es/cas/bomberos/proteccion-civil"},
        {"label": "Generalitat Valenciana: PATRICOVA map", "url": "https://mediambient.gva.es/ca/mapa-web"},
        {"label": "Valencia City: official housing-price series", "url": "https://www.valencia.es/estadistica/UltDatos/PrecioVivienda_val.pdf"},
        {"label": "Valencia open data: free-housing price per square metre", "url": "https://opendata.vlci.valencia.es/dataset/free-housing-square-meter-price"},
        {"label": "Registradores: Q1 2026 property report", "url": "https://www.registradores.org/documents/d/guest/eri-2026_1t"},
        {"label": "European Central Bank: euro reference exchange rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("turia-city", "/assets/valencia-turia-city-hero.webp", "Valencia skyline and the Turia gardens in warm morning light", "The Turia links everyday city life rather than staging a resort view.", "hero"),
        DossierImage("daily-life", "/assets/valencia-daily-life-market.webp", "Residents shopping on a shaded Valencia neighbourhood street", "Daily value begins with shade, shops, level access and a useful route home.", "wide"),
        DossierImage("coast-access", "/assets/valencia-coast-access.webp", "Valencia beach promenade with residents walking and cycling", "The coast works best when transport and year-round services remain part of the address.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Valencia through five destination lenses",
    assessment_intro="Here’s how Valencia scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show different buyer cases in Russafa, El Cabanyal and Patacona. EUR is primary; USD uses the recorded ECB reference basis for comparison only.",
    market_anchors_intro="These are public market signals—not valuations. The city appraisal series and province-wide registered average cover different geographies and stock; reconcile every candidate for district, legal area, age, condition and completed comparable evidence.",
    orientation_groups=(
        DossierOrientationGroup("Airport, centre and rail", (("Valencia Airport", "Metro gateway"), ("Àngel Guimerà / Colón", "Central interchange"), ("Nord / Joaquín Sorolla", "Rail stations"), ("Turia / El Pla del Real", "Park-led city"))),
        DossierOrientationGroup("Centre to the northern beach", (("Russafa / centre", "Urban daily life"), ("El Cabanyal-Canyamelar", "Maritime district"), ("Malvarrosa", "Valencia beach"), ("Patacona / Alboraya", "Northern promenade"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current services, walking conditions, municipal boundary and the exact door-to-door route.",
    country_guide_url="/countries/spain-property/",
    country_guide_label="Spain property guide",
    rail_comparison="Compare Valencia with the full Atlas.",
)


COSTA_BRAVA_GIRONA_DOSSIER = PremiumDossierSpec(
    destination_id="costa-brava-girona",
    title="Costa Brava and Girona Retirement Property Dossier",
    description="Assess Costa Brava and Girona retirement property through daily life, access, ownership, tourism rules, healthcare, hazards, value, resale, and current listings.",
    h1="Costa Brava / Girona: choose the daily base before the view",
    lede="Costa Brava / Girona is not one retirement market. Girona is a working city with rail, hospitals and year-round services; Begur, Palafrugell and Pals offer village character close to celebrated coves; Palamós, Sant Feliu de Guíxols and Platja d'Aro provide more complete coastal services; L'Escala, Roses and Cadaqués pull the decision north toward wind, seasonality and longer journeys. The best purchase begins by choosing the life that must work in February, then asking whether the property, rules and eventual buyer pool support it.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is positive but address-selective. Costa Brava / Girona suits a buyer who wants Mediterranean landscape without abandoning a real regional economy, accepts that the famous shoreline is car-led, and can separate personal enjoyment from rental promises. Girona city is the easiest year-round base. Palamós, Sant Feliu de Guíxols and Platja d'Aro can support ordinary coastal life with larger service centres. Begur, Palafrugell, Pals, Cadaqués and the smaller coves offer stronger atmosphere but need closer testing of winter opening, gradients, parking, healthcare and property management.",
        "Property ownership does not create Spanish residence. Establish the immigration route, tax residence and healthcare position before purchase, particularly where a non-EU buyer may face time limits or where a household expects public cover. Spain permits foreign ownership, but the transaction sits within national rules, Catalan transfer taxes and municipal planning. Short-stay use is a separate business question: Catalonia's tourist-home regime, the affected-municipality licensing framework, local compatibility and community rules can make an apparently rentable home unsuitable for the intended operation.",
        "Proceed in sequence. Choose city, serviced coast, village hinterland or remote northern coast; travel the airport, rail, supermarket and hospital routes in summer traffic and winter; then verify title, planning, community governance, building condition, water, drainage, coastal exposure and mapped hazards. Obtain a written tax and financing statement, and treat every listing and market statistic as a comparison input rather than a valuation. Finally, identify who would buy the property next. A beautiful view is a benefit only when the address remains usable, lawful and sellable through the whole year."
    ),
    lenses_intro="The five paired lenses below turn the Atlas scores into choices between Girona city, the central serviced coast, the Baix Empordà villages and the more remote northern shore. The complete ten-factor assessment appears once in the table that follows.",
    lenses=(
        DossierLens(
            "Live beyond the summer postcard",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Costa Brava earns its appeal honestly: rocky coves, old stone centres, coastal paths, seafood, landscape and a climate that supports outdoor life for much of the year. The mistake is assuming that every attractive town delivers the same retirement. Girona has markets, culture, neighbourhood services and an ordinary resident rhythm. Palafrugell and Palamós retain substantial local life behind the waterfront. Begur and Pals are quieter and more dispersed, while Cadaqués is singular but geographically constrained. Platja d'Aro is more commercial; Sant Feliu de Guíxols offers a mature town fabric. Visit when beach businesses are closed and judge the remaining life.",
                "Retirement fit depends on mundane distances. Girona puts hospitals, clinics, pharmacies and rail within a compact urban area. On the coast, Palamós has a hospital and larger towns provide primary care, but the correct provider and emergency route vary by address. A hillside home above Sa Riera or Tamariu may require a car for groceries and a steep return walk. Cadaqués and Roses face a longer road connection around the Cap de Creus area; the tramuntana can change comfort and mobility. Confirm ambulance routing, pharmacy hours, specialist referral and whether one household member can manage if the regular driver is unavailable.",
                "Test the physical home for aging as well as holidays. Old-town stairs, split levels, steep plots, polished terraces and distant parking can become daily constraints. Coastal salt and humidity affect metalwork, façades and unused interiors; shaded stone houses may be cool but damp. In Girona, summer heat, tourist noise and lift access matter. In Palafrugell, Pals and inland villages, verify walkability to year-round food and social life. Spend at least one ordinary winter week and one peak-summer week in the exact neighbourhood. The best retirement home makes healthcare, groceries, shade and companionship routine rather than a driving project."
            ),
            "coastal-daily-life",
        ),
        DossierLens(
            "Connect through Girona, then price the coast's last mile",
            ("global_access", "foreigner_fit"),
            (
                "Girona is the transport hinge. The regional R11 rail corridor connects Girona and Figueres with Barcelona, while high-speed services strengthen the city case. Girona-Costa Brava Airport publishes a substantial destination list, but many routes are seasonal, so Barcelona Airport often remains the more dependable international gateway. A buyer should time the entire journey, not quote the nearest runway. Girona city can work with rail and local transport; most Costa Brava addresses require a bus, taxi or car after the station. Friday traffic, summer queues, late arrivals and flight seasonality belong in the access calculation.",
                "The coast divides into practical corridors. Girona to Palafrugell, Begur and Pals uses roads and buses rather than coastal rail. Palamós, Sant Feliu de Guíxols, S'Agaró and Platja d'Aro share a more populated central-southern band, yet the final kilometres still change by hillside and urbanisation. L'Escala and Roses can connect through Figueres; Cadaqués adds a winding final road exposed to congestion and weather. Record door-to-door times to the preferred airport, hospital and railway station in August and January. If the household plans to stop driving, choose an address where daily life already works on foot rather than hoping services improve.",
                "Foreigner fit is high in the sales and hospitality layer but more mixed in ownership operations. Agents and lawyers commonly work in several languages, and established expatriate communities exist along the coast. Municipal notices, community meetings, planning files, contractor discussions and healthcare administration can still be Catalan- or Spanish-led. A remote owner also needs someone able to inspect after storms, receive registered notices and manage water, security and repairs. Hire independent legal and tax advisers, insist on translated documents, and test the local manager's response area. An English sales process does not make Begur, Palamós or Cadaqués administratively hands-off."
            ),
            "village-access",
        ),
        DossierLens(
            "Own clearly, then clear the exact intended use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Foreign buyers can generally own Spanish property, but title access is only the starting point. Obtain an independent registry extract, cadastral comparison, planning certificate where appropriate, debt and community evidence, occupancy documentation and a survey. Reconcile legal and physical area, pools, terraces, annexes and conversions. In an apartment, read budgets, minutes, reserve position, arrears, works and restrictions. In a detached home, verify boundaries, retaining structures, access, septic or mains services and building legality. Girona old-town property, a Begur villa and a Platja d'Aro apartment require different briefs even when all appear straightforward in a portal.",
                "Tax must be priced for the actual transaction. Catalonia applies its current progressive transfer-tax scale to many resale purchases, with different rules and potential rates depending on value, buyer, property and date; new property follows a different national and regional tax path. Add notary, registry, legal, survey, financing, insurance, community and eventual sale costs. Non-resident ownership can create Spanish filings and imputed-income or rental tax, while tax residence changes the frame. Obtain a written buyer-specific completion statement before paying a non-refundable deposit. A round percentage from an old guide is not reliable enough for a Girona apartment or Begur house.",
                "Tourist letting requires address-level clearance. Catalonia defines a tourist-use dwelling around repeated whole-home stays of 31 days or less. Municipal compatibility, registration, urban planning and community rules apply, and the 2023 decree created an additional five-year urban licence and tourist authorisation framework in affected municipalities. Existing operations may have transitional treatment; none of that makes a licence transferable or guaranteed. Confirm the exact municipality, urbanisation and property before attributing rent. The coastal planning framework also covers many Girona shoreline municipalities. Regulatory safety means written confirmation from the competent authority and community, not a seller's historic booking calendar."
            ),
        ),
        DossierLens(
            "Underwrite resident demand before holiday demand",
            ("rental_profit", "capital_upside"),
            (
                "Rental profit differs sharply by format. Girona has students, professionals and resident households, giving a city apartment a broader long-term demand base, though building rules and local rent regulation still need checking. Palamós, Sant Feliu de Guíxols and Platja d'Aro have larger year-round populations than small coves, but holiday demand remains seasonal. Begur, Pals and Cadaqués can command high summer rates for scarce, well-presented homes; they also face cleaning, pool, garden, guest support, linen, platform fees, winter vacancy and manager dependence. Model a lawful long-term case and a no-rent case before treating short stays as upside.",
                "A licence is not a yield. Ask for property-level booking statements, bank-supported revenue, operating invoices and the exact owner calendar. Then deduct tax, management, utilities, community fees, insurance, maintenance, marketing, replacements and vacancy. Verify whether the quoted floor area and bedroom count match authorised documents. A hillside villa near Begur can have attractive weekly rates but costly turnovers and access; a Sant Feliu apartment may trade glamour for easier operations. In Cadaqués, remoteness and peak congestion influence staffing. If the operation depends on one manager or one regulatory interpretation, discount it and make the purchase work without optimistic occupancy.",
                "Capital upside should be tied to scarcity that remains useful. Girona benefits from a diverse regional economy and transport; central coastal towns have resident demand; protected landscape and constrained sites can support selected premium property. Yet scarcity can also mean planning friction, expensive renovation and a narrow buyer pool. Official registered-sale data confirm price differences between Girona, Platja d'Aro and new homes in Begur, but those categories are not interchangeable. Avoid extrapolating a small new-build sample to an older villa or treating an asking-price surge as completed growth. Model flat nominal resale after all costs and buy only if personal utility carries the case."
            ),
        ),
        DossierLens(
            "Buy the micro-market—and name the next buyer",
            ("value_entry", "exit_liquidity"),
            (
                "Value entry begins with segmentation. Girona apartments offer the lowest operational complexity in this comparison, though prime old-town renovations can be expensive. Palafrugell and inland Pals may provide year-round services or space without first-line seafront pricing. Begur's coves and villages command lifestyle premiums that vary by view, walkability, road and condition. Palamós and Sant Feliu de Guíxols offer deeper everyday infrastructure; S'Agaró and parts of Platja d'Aro move into prestige territory. L'Escala, Roses, Llançà and Cadaqués each have distinct wind, access and seasonal profiles. A regional average cannot identify which one is good value.",
                "Use completed evidence before negotiating. The official 2025 registry series reports all-home averages for Girona and Castell d'Aro, Platja d'Aro i S'Agaró, while Begur's highlighted figure covers new homes and only 26 transactions. Those anchors show dispersion, not the value of a candidate. Match municipality, new or used status, legal floor area, age, condition, view, parking, outdoor space and completed date. The three current listings below are direct asking observations for three different buyer cases. They are not recommendations, availability guarantees or appraisals. Commission an independent survey and demand completed local comparables before a binding offer.",
                "Exit liquidity is strongest when future utility is easy to explain. A lift-served Girona apartment near daily services can reach residents and downsizers. A practical Palamós or Sant Feliu home may attract both local and second-home demand. A singular Begur villa or Cadaqués house asks the next buyer to share the same price, access, maintenance and planning tolerance. Before purchase, ask two agents who did not source the listing who would buy it, typical marketing time and what condition or discount closed comparable sales. Model five-year cash outlay and a long sale. Preserve optionality instead of paying for a view that only one buyer understands."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Girona supports year-round culture and services; Begur, Palafrugell and Cadaqués add exceptional coastal character with sharper seasonality.",
        "global_access": "Girona has strong rail links, while Begur, Palamós and Cadaqués add a car- or bus-dependent coastal last mile.",
        "ownership_clarity": "Girona and Costa Brava purchases allow foreign ownership, but every title, cadastral area, planning status and community record needs reconciliation.",
        "regulatory_safety": "Begur, Palafrugell and Platja d'Aro require municipal tourist-use and planning checks alongside community and address-level hazard review.",
        "rental_profit": "Girona supports broader resident demand; Begur and Cadaqués may achieve premium summer rates but carry seasonality, staffing and licence risk.",
        "capital_upside": "Girona's economy and scarce Costa Brava settings support selected homes, but Begur new-build data cannot price older coastal stock.",
        "retirement_fit": "Girona offers the easiest hospital and service access; hillside Begur and remote Cadaqués require stronger driving and support plans.",
        "exit_liquidity": "Girona, Palamós and Sant Feliu reach broader buyer pools than singular villas in remote coves around Begur or Cadaqués.",
        "foreigner_fit": "Girona and established Costa Brava towns offer multilingual advisers, while municipal, community, contractor and healthcare work remains locally administered.",
        "value_entry": "Palafrugell, Pals and Sant Feliu can offer more practical entry than prestige Begur, S'Agaró or Cadaqués addresses.",
    },
    market_anchors=(
        {"location": "Girona municipality", "evidence": "2,565.82 EUR/m²", "buyer_read": "2025 average for all registered home sales; new and used stock are reported separately, so this is not a district or apartment valuation.", "source_label": "Catalonia 2025 registered sales", "source_url": "https://habitatge.gencat.cat/web/.content/home/dades/estadistiques/01_Estadistiques_de_construccio_i_mercat_immobiliari/02_Compravenda_i_preu_de_venda/02_Compravendes_d_habitatges_registrades_i_el_preu_de_venda/Estadistica_PDF/Compravendes_2025.pdf"},
        {"location": "Castell d'Aro, Platja d'Aro i S'Agaró", "evidence": "3,525.81 EUR/m²", "buyer_read": "2025 average for all registered homes across the combined municipality; it does not isolate S'Agaró, sea views, age or condition.", "source_label": "Catalonia 2025 registered sales", "source_url": "https://habitatge.gencat.cat/web/.content/home/dades/estadistiques/01_Estadistiques_de_construccio_i_mercat_immobiliari/02_Compravenda_i_preu_de_venda/02_Compravendes_d_habitatges_registrades_i_el_preu_de_venda/Estadistica_PDF/Compravendes_2025.pdf"},
        {"location": "Begur new homes", "evidence": "4,839.29 EUR/m²", "buyer_read": "2025 average for 26 registered new homes, with a high average size and price; a small new-build sample, not a Begur resale benchmark.", "source_label": "Catalonia 2025 registered sales", "source_url": "https://habitatge.gencat.cat/web/.content/home/dades/estadistiques/01_Estadistiques_de_construccio_i_mercat_immobiliari/02_Compravenda_i_preu_de_venda/02_Compravendes_d_habitatges_registrades_i_el_preu_de_venda/Estadistica_PDF/Compravendes_2025.pdf"},
    ),
    micro_locations_intro="The decision is a chain from rail-served Girona to increasingly seasonal and car-dependent coastal settings. These are operating patterns, not price zones. Verify the exact municipality, address, route, service calendar, planning position, hazard layers and completed evidence.",
    micro_locations=(
        {"name": "Girona city", "best_for": "Year-round urban retirement", "daily_life": "Walkable services and rail", "diligence": "Building, heat, noise and district comparables"},
        {"name": "Begur / Palafrugell / Pals", "best_for": "Village and cove character", "daily_life": "Mixed town and car-led coast", "diligence": "Tourist use, gradients, water, planning and winter services"},
        {"name": "Palamós / Sant Feliu / S'Agaró / Platja d'Aro", "best_for": "Serviced central coast", "daily_life": "Larger towns with seasonal peaks", "diligence": "Community rules, traffic, condition and local pricing"},
        {"name": "L'Escala / Roses / Llançà / Cadaqués", "best_for": "Northern coast and landscape", "daily_life": "Longer journeys and tramuntana exposure", "diligence": "Access, wind, hazards, management and resale depth"},
    ),
    checklist=(
        "Confirm residence, tax residence and healthcare before purchase.",
        "Choose Girona, serviced coast, village hinterland or remote northern coast first.",
        "Travel airport, rail, grocery and hospital routes in summer and winter.",
        "Reconcile title, cadastre, planning, occupancy, community and physical area.",
        "Inspect structure, moisture, salt exposure, drainage, utilities and accessibility.",
        "Overlay current flood, wildfire, coastal and geological hazard evidence.",
        "Clear tourist use, municipal compatibility, community rules and operator costs in writing.",
        "Model five-year cash outlay and name the future resale buyer before signing.",
    ),
    references_intro="Legal, tax, planning, tourism, market, transport, healthcare, hazard and listing claims were reviewed on 22 August 2026. Recheck each time-sensitive source no later than 22 February 2027 and immediately after any law, municipal, licensing, transport, hazard, market-data or listing change. Obtain current Spanish and Catalan legal, tax, immigration, survey, insurance and healthcare advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "Spain property and retirement guide", "url": "/spain-retirement-property-foreign-buyers/"},
        {"label": "Spanish administration: residence for EU and non-EU citizens", "url": "https://administracion.gob.es/pag_Home/en/Tu-espacio-europeo/derechos-obligaciones/ciudadanos/residencia.html"},
        {"label": "Spanish Tax Agency: non-resident property income", "url": "https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/irnr-sin-establecimiento-permanente/rentas-inmuebles.html"},
        {"label": "Catalan Tax Agency: current property transfer tax", "url": "https://atc.gencat.cat/es/tributs/itpajd/operacions/immobles/compravenda-immobles/"},
        {"label": "Catalonia business portal: tourist-use dwellings", "url": "https://canalempresa.gencat.cat/es/03_sectors_d_activitat/06_hostaleria_i_turisme/establiments_turistics/habitatges_d_us_turistic/"},
        {"label": "Catalonia business portal: 2023 tourist-home licensing framework", "url": "https://canalempresa.gencat.cat/es/03_sectors_d_activitat/06_hostaleria_i_turisme/establiments_turistics/habitatges_d_us_turistic/DL3_2023/"},
        {"label": "Catalonia Housing Agency: 2025 registered home sales", "url": "https://habitatge.gencat.cat/web/.content/home/dades/estadistiques/01_Estadistiques_de_construccio_i_mercat_immobiliari/02_Compravenda_i_preu_de_venda/02_Compravendes_d_habitatges_registrades_i_el_preu_de_venda/Estadistica_PDF/Compravendes_2025.pdf"},
        {"label": "Catalonia Territory: Girona coastal planning framework", "url": "https://territori.gencat.cat/ca/01_departament/05_plans/01_planificacio_territorial/plans_urbanistics/plans_directors_urbanistics/pdu_aprovats/Girona/pdu_sns_litoral_gironi/"},
        {"label": "Catalonia rail: R11 regional line", "url": "https://rodalies.gencat.cat/ca/sobre-rodalies/linies-i-estacions/servei_regionals/r11/"},
        {"label": "Aena: Girona-Costa Brava airport destinations", "url": "https://www.aena.es/en/girona-costa-brava/airlines-and-destinations/airport-destinations.html"},
        {"label": "Aena: Girona-Costa Brava airport bus access", "url": "https://www.aena.es/en/girona-costa-brava/getting-there/bus.html"},
        {"label": "Girona health service: Trueta Hospital emergency department", "url": "https://icsgirona.cat/htrueta/es/hospital-trueta/servicio-de-urgencias"},
        {"label": "Catalonia Civil Protection: official risk map", "url": "https://interior.gencat.cat/es/arees_dactuacio/proteccio_civil/mapa_de_proteccio_civil/"},
        {"label": "ICGC: coastal geological-hazard viewer", "url": "https://www.icgc.cat/es/Ambitos-tematicos/Ambito-litoral/Aplicaciones-y-visores/Peligrosidad-litoral"},
        {"label": "Engel & Völkers: Girona Cathedral apartment asking observation", "url": "https://www.engelvoelkers.com/es/en/exposes/35d363ca-c155-543a-8ac1-a0e6958ed064"},
        {"label": "Costa Brava House: Sa Roda house no. 1 asking observation", "url": "https://www.costabravahouse.com/en/luxury-house-begur-sale-pool-sea-view-sa-roda-6170"},
        {"label": "Lucas Fox: Sant Feliu / S'Agaró penthouse asking observation", "url": "https://www.lucasfox.com/property-for-sale/spain/costa-brava/sant-feliu-de-guixols/apartment/pda66170.html"},
    ),
    images=(
        DossierImage("city", "/assets/costa-brava-girona-city-hero.webp", "Girona riverside neighbourhood and old city in warm morning light", "Girona supplies the year-round urban base behind the coastal proposition.", "hero"),
        DossierImage("coastal-daily-life", "/assets/costa-brava-girona-coastal-daily-life.webp", "Residents walking beside a lived-in Costa Brava waterfront outside peak summer", "The best coastal addresses continue to function after the visitor season.", "wide"),
        DossierImage("village-access", "/assets/costa-brava-girona-village-access.webp", "Everyday street in a stone Baix Empordà village with residents and bicycles", "Village character must be tested against access, services and ordinary errands.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Costa Brava / Girona through five destination lenses",
    assessment_intro="Here’s how Costa Brava / Girona scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show a Girona city apartment, a Begur-area house and a Sant Feliu / S'Agaró penthouse. EUR is primary; USD uses the recorded repository reference basis for comparison only.",
    market_anchors_intro="These are public market signals—not valuations. The official series mixes all homes, new homes and different municipalities; reconcile every candidate for location, legal area, age, condition and completed comparable evidence.",
    orientation_groups=(
        DossierOrientationGroup("Girona to the central coast", (("Girona", "Rail and hospital base"), ("Palafrugell / Pals", "Village service belt"), ("Begur", "Coves and hillside homes"), ("Palamós", "Serviced fishing town"))),
        DossierOrientationGroup("Southern and northern coast", (("Sant Feliu / S'Agaró", "Mature town and prestige enclave"), ("Platja d'Aro", "Commercial coastal centre"), ("L'Escala / Roses", "Northern service towns"), ("Cadaqués", "Remote Cap de Creus setting"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current rail, bus, driving and seasonal journey times from the exact address.",
    country_guide_url="/countries/spain-property/",
    country_guide_label="Spain property guide",
    rail_comparison="Compare Costa Brava / Girona with the full Atlas.",
)


CRETE_DOSSIER = PremiumDossierSpec(
    destination_id="crete",
    title="Crete Retirement Property Dossier",
    description="Assess Crete retirement property through daily life, access, residence, ownership, tax, short-term-rental rules, healthcare, hazards, value, resale, and current listings.",
    h1="Crete: choose the working island, not only the sea view",
    lede="Crete is large enough to contain several retirement markets that should not be averaged together. Chania offers a polished historic city and western airport; Apokoronas adds villages, space and a greener landscape with more driving; Rethymno balances a walkable university town with access to both sides of the island; Heraklion has the deepest employment, hospital and administrative base; Agios Nikolaos and Elounda trade on eastern-Crete scenery and premium tourism. This dossier tests which version works in winter, heat and ordinary errands—and whether the title, tax, rental, water and exit plan supports it.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is positive with geographic discipline. Crete suits a buyer who wants a warm-climate European base with a real resident economy, food culture, beaches and enough city infrastructure to support long stays. Chania and Rethymno offer the strongest combination of walkable urban life and western-island appeal. Heraklion is the practical choice for major healthcare, administration and year-round employment. Apokoronas works for a buyer who accepts driving and property maintenance in exchange for village life and space. Agios Nikolaos and Elounda offer an attractive eastern base, but entry price, airport distance and a more tourism-led buyer pool require sharper underwriting.",
        "Buying property does not itself grant a right to live in Greece. EU and other qualifying residents follow their applicable free-movement or national route; third-country nationals need an independent immigration basis or must satisfy the current investor-permit rules. The Ministry of Migration's Golden Visa process is a regulated residence programme, not a general consequence of owning any Cretan home. Separate residence, health insurance and tax residence from the conveyance. A buyer also needs a Greek tax number, transfer-tax handling, independent legal and technical diligence, and a cadastral and planning position that matches the house on the ground.",
        "Proceed in order. Confirm residence, healthcare and tax structure; choose the working geography; travel the airport, hospital, supermarket and beach routes in August traffic and a winter storm; then verify cadastral identity, title, boundaries, permits, legal floor area, road access, water, wastewater, energy, earthquake condition, wildfire and flood exposure. If rental income matters, establish the lawful short-term-rental route and manager before valuing it. Finally, model renovation, cooling, pool, garden, insurance and a slow resale. Crete's value can be compelling, but an informal extension, weak water plan or isolated exit can overwhelm a low entry price.",
    ),
    lenses_intro="The five paired lenses below translate Crete's ten Atlas dimensions into choices between its cities, village belts and resort coast. The complete ten-factor assessment appears once in the score table.",
    lenses=(
        DossierLens(
            "Live on an island that keeps working in winter",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Crete's lifestyle case survives because it is not only a resort. Chania combines a historic harbour, neighbourhood markets, restaurants and a substantial resident population. Rethymno is smaller and more walkable, with university activity and a long urban beach. Heraklion is busier and less postcard-perfect, but it provides the island's broadest concentration of services, commerce and culture. Agios Nikolaos offers a compact waterfront town, while Elounda is more polished and visitor-led. Apokoronas villages such as Armeni, Vamos and Gavalochori add landscape and community, but ordinary life is dispersed. Spend January as well as June before deciding what ‘year-round’ means.",
                "Healthcare is a geography question. The 7th Health Region lists major hospitals in Chania, Rethymno and Heraklion, including the University Hospital, and an eastern network centred on Agios Nikolaos with connected facilities in Sitia, Ierapetra and Neapoli. A dot on that map is not proof that the needed department, appointment, language support or insurer network is available when required. Heraklion has the deepest specialist base; a remote south-coast or mountain address may add a long, winding transfer. Identify the primary-care doctor, pharmacy, emergency hospital and specialist route, then drive them at night and in poor weather.",
                "Ageing in place changes the property brief. Historic Chania and Rethymno can provide walkability but also stairs, noise, limited parking and old buildings. Apokoronas and Lasithi homes often provide ground-floor space and gardens but require a car, external maintenance and reliable help. Summer heat, dust and wildfire smoke increase the importance of insulation, shading, efficient cooling, filtration and backup power. A pool, terraced plot or steep lane can become a burden after an injury. Prefer a legal main-level bedroom and bathroom, step-light access, year-round neighbours and a manager who can respond when the owner is absent.",
            ),
            "apokoronas-daily-life",
        ),
        DossierLens(
            "Choose the airport and road network with the house",
            ("global_access", "foreigner_fit"),
            (
                "Crete has two principal international gateways, but they serve different property patterns. Chania Airport on Akrotiri supports the western side and publishes current flight and ground-transport information through Fraport Greece. Heraklion Airport operates year-round and sits close to the island's largest city; the Hellenic Civil Aviation Authority identifies it as an international airport and notes its city-centre proximity. The new Heraklion airport remains a construction and future-access story, not a current journey assumption. Flight schedules are seasonal, routes change, and a direct summer service may become an Athens connection in winter. Test the annual travel pattern, not the best timetable week.",
                "The north-coast road links Chania, Rethymno, Heraklion and Agios Nikolaos, but Crete is long and local roads vary sharply. Rethymno sits between the two existing airports, which adds choice but not a short transfer. Apokoronas villages can be close to the main road yet depend on narrow last-mile lanes. South-coast and inland mountain areas trade tranquillity for slower access to hospitals, airports and major shops. Eastern Crete adds distance from Heraklion, while Elounda and hillside properties can be congested in peak season. Drive the exact route with luggage, after dark and after heavy rain; a map distance does not show road geometry or summer traffic.",
                "Foreigner fit is supported by Greece's EU framework, established notaries, lawyers, engineers, tax advisers and an international property market. It is not automatic simplicity. The buyer needs an AFM tax number, translated and correctly executed authorities where relevant, independent title and technical advice, a local bank and payment plan, and continuing E9, ENFIA and income-tax administration. Village documents, contractor discussions, condominium meetings and utility matters may proceed in Greek. Appoint independent advisers who owe duties to the buyer, not the agent or developer, and retain a reliable local representative to receive notices, inspect after storms and coordinate urgent work.",
            ),
        ),
        DossierLens(
            "Own the legal building—not the seller's description",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Greek ownership access is generally workable, and the AADE states that a resident or nonresident buyer needs a Greek tax number and must file and pay transfer tax before the contract. Its current buyer guide states a 3% transfer-tax calculation on the property value, subject to the exact transaction and any applicable regime. That headline is not total closing cost. Budget for notary, registry or cadastre, lawyer, engineer, agent, certificates, translations and later ENFIA and tax filings. New construction, VAT history, company ownership and investor-residence structuring require transaction-specific advice rather than applying the used-home rule mechanically.",
                "The technical file is often the controlling risk. Match the contract, cadastral record, survey, building permit, plans, energy certificate and actual measured structure. Verify every veranda enclosure, basement conversion, guest room, pool, retaining wall, pergola and access road. A seller's regularisation document does not by itself prove construction quality, planning suitability or future expandability. In villages, confirm boundary monuments, rights of way, shared courtyards, water source, septic or sewer arrangement and whether a renovation can obtain approvals. In historic Chania or Rethymno, add conservation and common-building constraints. Release funds only against a complete lawyer-and-engineer report.",
                "Short-term letting is a regulated use. AADE requires a property manager using the short-term lease framework to register the property and obtain a Property Register Number, display the required number and file stay information. A tourist accommodation licence or notification follows a different route. Tax, safety and operational requirements can change, while condominium rules and planning may be stricter. Confirm which person will be manager, which legal route applies, whether the exact floor area and bedrooms qualify, and how tax, guest, safety and local-response duties will be met. Do not value a portal calendar or the phrase ‘investment suitable’ as permission.",
            ),
        ),
        DossierLens(
            "Underwrite heat, water and seasonality before rent",
            ("rental_profit", "capital_upside"),
            (
                "Crete has a long visitor season, but rental profit remains location- and property-specific. Chania old town and accessible coast, Rethymno, selected Heraklion demand and the Agios Nikolaos–Elounda corridor can attract guests; an inland village or remote south-coast house serves a different calendar. Gross revenue must absorb management, cleaning, linen, platform fees, utilities, pool and garden care, air-conditioning, repairs, insurance, tax and owner use. Winter occupancy can fall sharply in visitor-led areas. Obtain property-level statements, bank deposits, filed declarations and the future manager's contract; model a weak shoulder season and no tourist rent.",
                "Climate operations are part of the income statement. Civil Protection publishes wildfire, flood, heat, earthquake and other hazard guidance and current maps; Crete also publishes water and irrigation information that reflects local scarcity management. The relevant evidence is parcel-level access, vegetation, slope, drainage, water source and network capacity—not a general island reputation. Ask for water bills, pressure history, storage, pool refill rules and summer outage experience. Inspect roof, shutters, cooling, solar hot water, damp, salt corrosion, retaining walls and defensible space. Obtain an insurance quotation that covers the intended occupancy and letting use before the contingency expires.",
                "Capital upside is supported by demand and a rising Greek market, but should not be inferred from one island average. The Bank of Greece reported continued national apartment-price growth in Q1 2026, including 6.9% year-on-year in ‘other areas of Greece’; that is a broad trend, not a Crete forecast. July portal asking evidence shows meaningful dispersion between the island average, Chania district and Agios Nikolaos. Those are asking indices covering mixed stock, not completed-sale valuations. Airport investment, tourism and scarce legal coastal property may support selected assets, while new supply, informal construction, water pressure and a narrow foreign-buyer pool can undermine others.",
            ),
            "eastern-water-heat",
        ),
        DossierLens(
            "Buy the future buyer pool, not the island average",
            ("value_entry", "exit_liquidity"),
            (
                "Crete can offer European value, but entry points represent different products. A Rethymno apartment may provide walkable services and broad local use but need renovation and building diligence. An Apokoronas house offers more space, village life and western access, with driving and maintenance attached. A compact renovated house near Agios Nikolaos can carry a large coast-and-tourism premium despite its small internal area. Chania's most recognisable areas command higher asking evidence; Heraklion may offer more ordinary urban demand at a lower regional average. Compare legal floor area, condition, parking, cooling, outdoor work and daily access—not island-wide price per square metre alone.",
                "The three listing observations below are deliberately unlike one another. The Armeni house represents a practical village market in Apokoronas. The Rethymno apartment tests an older urban home where renovation and walkability matter more than a pool or view. The Ammoudara / Agios Nikolaos house shows how renovation, a coastal setting and small size can lift the asking price per square metre. None is a recommendation, availability guarantee or valuation. Commission completed comparable evidence for the same legal area and micro-location, then reconcile works, furniture, land, title, pool, parking and energy performance.",
                "Exit liquidity follows usefulness and documentation. A legal, accessible Chania or Heraklion apartment can reach residents, retirees and investors. A well-positioned Rethymno home can appeal to year-round and holiday buyers. An Apokoronas property needs a buyer who accepts village transport and maintenance. A high-premium Elounda or hillside villa reaches a smaller international pool and can wait longer. Before purchase, ask two agents who did not source the home who would buy it next, what completed evidence they would use and how long a realistic sale could take. Model a flat-price exit after all costs and preserve cash for a long marketing period.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Crete combines food, coast and living cities; Chania and Rethymno feel very different from inland Apokoronas or resort-led Elounda.",
        "global_access": "Chania and Heraklion airports support Crete, while seasonal routes, long island roads and eastern or southern last miles reduce convenience.",
        "ownership_clarity": "Crete follows Greece's workable ownership system, but cadastral identity, legal floor area, permits and tax administration remain property-specific.",
        "regulatory_safety": "Crete short-term rentals require the correct AADE registration or tourism route, with planning, safety and condominium limits layered above it.",
        "rental_profit": "Chania, Rethymno and Agios Nikolaos can earn a long season, but management, cooling, pool care and winter weakness compress net income.",
        "capital_upside": "Crete benefits from national price growth and infrastructure, while mixed stock, new supply, water pressure and informal works prevent blanket appreciation claims.",
        "retirement_fit": "Heraklion has Crete's deepest hospital base; Chania and Rethymno support city life, while Apokoronas and Lasithi increase driving dependence.",
        "exit_liquidity": "Crete city homes reach broader resident buyers than an isolated village house or premium Elounda villa with a narrow international pool.",
        "foreigner_fit": "Crete has experienced international advisers, but AFM, Greek documents, tax filings, engineering checks and local management still require coordination.",
        "value_entry": "Heraklion and village Crete can enter below prime Chania or Agios Nikolaos, but condition, access and legal area determine real value.",
    },
    market_anchors=(
        {"location": "Crete residential asking index", "evidence": "€2,579/m²", "buyer_read": "July 2026 average asking price across mixed residential stock; a regional signal, not a completed-sale valuation.", "source_label": "Indomio Crete market trend", "source_url": "https://www.indomio.gr/agora-akiniton/kriti/"},
        {"location": "Chania regional unit", "evidence": "€3,110/m²", "buyer_read": "July 2026 average residential asking price, the highest of Crete's four regional units in the same portal series.", "source_label": "Indomio Crete market trend", "source_url": "https://www.indomio.gr/agora-akiniton/kriti/"},
        {"location": "Agios Nikolaos municipality", "evidence": "€4,049/m²", "buyer_read": "July 2026 average residential asking price across the municipality; local zones ranged widely and product mix remains material.", "source_label": "Indomio Agios Nikolaos market trend", "source_url": "https://www.indomio.gr/en/agora-akiniton/kriti/agios-nikolaos/"},
    ),
    micro_locations_intro="Crete is a sequence of working patterns rather than one market. These groupings are orientation aids, not valuation zones. Confirm exact municipal planning, cadastral identity, airport and hospital journey, water, hazards, legal use and completed comparables for every address.",
    micro_locations=(
        {"name": "Chania / Akrotiri coast", "best_for": "Historic-city life and western airport", "daily_life": "Walkable core with visitor pressure", "diligence": "Parking, conservation, noise, legal area and summer demand"},
        {"name": "Apokoronas villages", "best_for": "Space, landscape and community", "daily_life": "Car-led village network", "diligence": "Access, title, water, wastewater, wildfire and maintenance"},
        {"name": "Rethymno / north-coast centre", "best_for": "Compact year-round urban balance", "daily_life": "Walkable centre between airports", "diligence": "Old building, renovation, parking, shared rules and beach exposure"},
        {"name": "Heraklion to Agios Nikolaos / Elounda", "best_for": "Services or premium eastern coast", "daily_life": "Deep city base grading into resort market", "diligence": "Airport journey, hospital access, price premium, water and exit pool"},
    ),
    checklist=(
        "Confirm residence, healthcare, tax residence and ownership structure.",
        "Choose the working geography before selecting a sea view.",
        "Travel airport, hospital, grocery and beach routes in peak and winter conditions.",
        "Verify AFM, cadastral identity, title, boundaries, road rights and taxes.",
        "Reconcile permits, legal floor area, energy certificate, pool and every extension.",
        "Inspect earthquake condition, cooling, water, wastewater, wildfire, flood and salt exposure.",
        "Clear short-term-rental registration, safety, tax and manager duties in writing.",
        "Model renovation, five-year cash outlay and a slow resale before signing.",
    ),
    references_intro="Legal, tax, residence, cadastral, rental, health, airport, hazard, market and listing claims were reviewed on 22 August 2026. Recheck every time-sensitive source no later than 22 February 2027 and immediately after any tax, residence, planning, cadastral, rental, transport, hazard, water, insurance, market data or listing change. Obtain current Greek legal, immigration, tax, notarial, engineering, planning and insurance advice for the exact buyer and property. Asking evidence is not a valuation or availability guarantee.",
    references=(
        {"label": "Greece property guide", "url": "/countries/greece-property/"},
        {"label": "AADE: before buying a property", "url": "https://www.aade.gr/en/services-information/useful-guides/buying-property/buying-property"},
        {"label": "AADE: after buying a property", "url": "https://www.aade.gr/en/services-information/useful-guides/buying-property/after-buying-property"},
        {"label": "AADE: short-term lease registration", "url": "https://www.aade.gr/en/services-information/useful-guides/buying-property/i-want-lease-my-property-short-term-lease"},
        {"label": "Ministry of Migration: Golden Visa process", "url": "https://migration.gov.gr/en/golden-visa/"},
        {"label": "Hellenic Cadastre: current property records", "url": "https://www.ktimatologio.gr/e-services/14"},
        {"label": "Bank of Greece: Q1 2026 residential price indices", "url": "https://www.bankofgreece.gr/en/news-and-media/press-office/news-list/news?announcement=a096eb19-23d0-44e4-9445-10ef088053fb"},
        {"label": "7th Health Region of Crete: hospitals", "url": "https://www.hc-crete.gr/MonadesYgeias/Home/nosokomeia"},
        {"label": "Civil Protection: current hazard maps and guidance", "url": "https://civilprotection.gov.gr/thematikoi-xartes-sxediwn-politikis-prostasias"},
        {"label": "Region of Crete: current water and irrigation bulletins", "url": "https://www.crete.gov.gr/12o-deltio-ardeysis-2026-gia-tin-periodo-06-08-2026-12-08-2026/"},
        {"label": "Chania Airport: current flights and access", "url": "https://www.chq-airport.gr/en"},
        {"label": "HCAA: Heraklion Airport", "url": "https://www.hcaa.gr/en/our-airports/kratikos-aerolimenas-hrakleioy-n-kazantzakhs"},
        {"label": "Indomio: July 2026 Crete asking index", "url": "https://www.indomio.gr/agora-akiniton/kriti/"},
        {"label": "Indomio: July 2026 Agios Nikolaos asking index", "url": "https://www.indomio.gr/en/agora-akiniton/kriti/agios-nikolaos/"},
        {"label": "IsleScout: Armeni Apokoronas asking observation", "url": "https://islescout.com/property/house-in-armeni-apokoronas-with-2-bedrooms-127-m2"},
        {"label": "Terra Real Estate: Rethymno asking observation", "url": "https://www.terrarealestate.gr/en/properties/1820994"},
        {"label": "Indomio: Ammoudara Agios Nikolaos asking observation", "url": "https://www.indomio.gr/en/aggelies/11086013/"},
    ),
    images=(
        DossierImage("chania", "/assets/crete-chania-hero.webp", "Chania waterfront and living city fabric in calm morning light", "Chania is compelling because the historic harbour sits inside a working western city.", "hero"),
        DossierImage("apokoronas-daily-life", "/assets/crete-apokoronas-daily-life.webp", "Mature residents walking through an Apokoronas village beside ordinary local homes", "Village life trades urban convenience for space, community and more driving.", "wide"),
        DossierImage("eastern-water-heat", "/assets/crete-eastern-water-heat.webp", "Resident checking water storage and shade at an eastern Crete home in summer", "Heat, water and absentee maintenance belong in the ownership plan.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Crete through five destination lenses",
    assessment_intro="Here’s how Crete scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show an Apokoronas village house, a Rethymno urban renovation and a compact renovated home near Agios Nikolaos. EUR figures use the repository reference rate of 1 EUR = 1.14784 USD, dated 22 July 2026.",
    market_anchors_intro="These are July 2026 asking evidence—not valuations. They cover mixed property types and broad boundaries; reconcile every candidate for exact location, legal area, age, condition, land, parking, energy, permitted use and completed comparable sales.",
    orientation_groups=(
        DossierOrientationGroup("Western Crete", (("Chania Airport / Akrotiri", "Western gateway"), ("Chania", "Historic working city"), ("Apokoronas", "Village and coastal belt"), ("Rethymno", "Compact city between gateways"))),
        DossierOrientationGroup("Central and eastern Crete", (("Heraklion Airport", "Current central gateway"), ("Heraklion / University Hospital", "Deepest service base"), ("Agios Nikolaos", "Compact eastern town"), ("Elounda / Lasithi", "Premium coast and dispersed east"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current flights, road works, public transport and peak-season journey times from the exact address.",
    country_guide_url="/countries/greece-property/",
    country_guide_label="Greece property guide",
    rail_comparison="Compare Crete with the full Atlas.",
)


PARK_CITY_DEER_VALLEY_DOSSIER = PremiumDossierSpec(
    destination_id="park-city-deer-valley",
    title="Park City and Deer Valley Retirement Property Dossier",
    description="Assess Park City and Deer Valley retirement property through daily life, access, foreign ownership, tax, nightly-rental rules, snow, wildfire, value, resale, and current listings.",
    h1="Park City / Deer Valley: buy the mountain town, not only the ski week",
    lede="Park City / Deer Valley is one of North America's most accessible major ski markets, but the address changes the proposition. Old Town offers walkability and history; Lower and Upper Deer Valley trade at a service-and-ski premium; Canyons Village combines resort operations with heavy HOA dependence; Park Meadows, Prospector and Kimball Junction offer more ordinary daily life. Jordanelle and Deer Valley East Village add new supply and construction risk. This dossier asks which version works after the holiday ends—and whether the ownership, tax, rental and exit plan supports it.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is selectively positive. Park City / Deer Valley suits an active buyer who values dependable U.S. ownership, Salt Lake City airport access, four-season recreation and a deeper resale market than most small ski towns. It works best when the home has a credible year-round use case, the buyer can absorb high carrying costs without optimistic rent, and the exact zoning and HOA permit the intended operation. Old Town is strongest for a walkable mountain-town life; Park Meadows and Prospector are more residential; Lower Deer Valley offers resort proximity; Canyons Village is operationally convenient but contract- and fee-heavy.",
        "Foreign ownership does not create U.S. immigration status, tax residence or healthcare coverage. A nonresident seller can face FIRPTA withholding, and U.S. real estate can be a U.S.-situated asset for nonresident estate-tax purposes. Those exposures are material at Park City price points and require cross-border tax and estate advice before choosing an ownership structure. The local regulatory question is equally specific: Park City and unincorporated Summit County have different nightly-rental licensing processes, zoning controls and management requirements, while an HOA or resort agreement may be stricter than government rules.",
        "Proceed in order. Establish the immigration, health-insurance, financing, tax and estate framework; choose the daily-life pattern; travel the airport, hospital, grocery and ski routes in a storm and peak traffic; then verify title, survey, zoning, HOA, rental permissions, building condition, snow systems, wildfire exposure and insurance. Read every recurring charge and special-assessment risk. Finally, identify the next buyer and model a slow exit. Park City can be unusually practical for a mountain market, but no amount of access rescues an overpaid property with unclear use or escalating operations."
    ),
    lenses_intro="The five paired lenses below translate the Atlas scores into choices between Park City's historic core, Deer Valley, Canyons Village and the residential basin. The full ten-factor assessment appears once in the score table.",
    lenses=(
        DossierLens(
            "Live well when the lifts are not the plan",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Park City's strongest argument is that it functions beyond skiing. Old Town combines Main Street, restaurants, cultural venues, trails and Park City Mountain access in a compact historic setting. Park Meadows provides larger residential lots and a quieter daily rhythm close to the core. Prospector has apartments, groceries, restaurants, clinics and transit at a more approachable entry point. Kimball Junction has the broadest concentration of everyday retail and services, though it feels suburban rather than like the mining town. Canyons Village and Deer Valley offer polished resort amenities, but ordinary errands often happen elsewhere. Test which environment still feels useful in May and October.",
                "Retirement practicality is credible but not urban. Park City Hospital at Round Valley provides emergency and trauma care, imaging and multiple specialties, while more complex treatment can require travel to the Salt Lake Valley. Confirm the correct provider network, ambulance route and insurance terms rather than relying on distance alone. Elevation, dry air, winter ice and smoke can affect health and mobility. A steep Old Town staircase, snow-covered Deer Valley drive or multi-level Canyons townhouse may become difficult after an injury. Prioritize a flat entrance, main-level bedroom, reliable heating, air conditioning or filtration and a realistic plan for driving less.",
                "The year-round social question is address-specific. Old Town stays animated but can be noisy and visitor-led. Prospector and Park Meadows feel more resident-based. Lower Deer Valley sits close to town; Upper Deer Valley and some gated communities can be quiet outside occupancy peaks. Snyderville Basin connects to schools, shops and trails but spreads daily life across roads. Spend ordinary weeks in the least flattering season, shop for groceries, attend appointments and return after dark. Ask who clears the drive and exterior stairs, and whether the household can reach food, care and company if one person cannot ski, drive or manage snow."
            ),
            "winter-daily-life",
        ),
        DossierLens(
            "Use the airport advantage without ignoring the canyon",
            ("global_access", "foreigner_fit"),
            (
                "Salt Lake City International Airport is a structural advantage, but the final journey still depends on weather and congestion. Park City is commonly reached through Interstate 80, with Kimball Junction encountered before the historic core. Old Town, Deer Valley and Canyons Village each add different local traffic patterns. Current regional commuter service links Park City and Salt Lake City, while Park City Transit provides fare-free local routes across core neighbourhoods and resort bases. Timetables, transfers and seasonal service must be checked for the exact address. A quoted drive time is not the same as a dependable winter door-to-door journey with luggage.",
                "Internal access determines whether a car is optional. Old Town can be genuinely walkable if the home is near Main Street and the Town Lift, but steep streets and winter conditions narrow that advantage. Lower Deer Valley connects readily to the core; Upper Deer Valley and gated hillside homes are more vehicle- or shuttle-dependent. Canyons Village can support a resort stay without a car, yet groceries, hospital visits and wider town life add transfers. Prospector benefits from transit and nearby services. Park Meadows and much of Snyderville Basin are more comfortable with a vehicle. Test routes at commuter and ski peaks, not on a quiet summer afternoon.",
                "Foreigner fit is strong in professional access and weak in automatic simplicity. Park City has agents, lawyers, accountants, managers and resort staff accustomed to international owners. Yet U.S. immigration, federal and state tax, beneficial ownership, estate exposure, banking and insurance can become more complex for a nonresident. HOA documents, title exceptions, inspection reports and nightly-rental agreements are long and consequential even when written in English. Appoint independent counsel rather than relying on the seller's team, and give a trusted local representative authority to receive notices and inspect the home. A familiar legal language does not remove cross-border consequences."
            ),
            "summer-transit",
        ),
        DossierLens(
            "Own freely, then prove the address and use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "The United States generally permits foreign ownership of ordinary residential real estate, which supports Park City's ownership score. The closing still requires exact diligence: title commitment and exceptions, survey, access, easements, water and sewer status, building permits, certificate history, property tax, seller disclosures, inspection and insurance. Condominiums and resort residences add declarations, bylaws, budgets, reserves, insurance allocation, litigation, rental-management terms and transfer fees. Old Town's historic fabric can bring preservation and renovation constraints; newer Canyons or East Village product can bring construction, developer and completion risk. Freehold title is not a substitute for reading the governing package.",
                "Nightly rentals are a location-and-building privilege, not a general Park City right. Park City requires a licence for stays under 30 days where zoning allows, along with an inspection and state tax handling. Unincorporated Summit County separately licenses both the owner and the manager for rentals under 30 days and requires the property to sit in an allowed land-use area. HOA, condominium hotel, resort and lender rules may be tighter. Confirm the municipal boundary first, then zoning, licence history, inspection, occupancy, parking, local-contact and tax duties. Never rely on a portal calendar or a listing's phrase ‘nightly rentals allowed.’",
                "Mountain risk is layered. Park City's building guidance addresses Wildland Urban Interface requirements, snow load, soil conditions and permits. Wildfire exposure can raise insurance cost or reduce availability, especially near wooded slopes; winter adds roof shedding, freeze, ice dam, blocked access and power interruption. Localised drainage and flood questions still matter around creeks and lower sites. Obtain current hazard maps, a specialist inspection and an insurance binder for the exact intended use before the contingency period expires. Ask about roof heat, snow retention, driveway grade, defensible space, air filtration and loss history. A resort-managed building can transfer tasks, but it cannot transfer all risk."
            ),
        ),
        DossierLens(
            "Treat nightly rent as a regulated operation",
            ("rental_profit", "capital_upside"),
            (
                "Park City can produce strong peak revenue, but the gross figure is far from rental profit. Winter holidays, summer recreation and major events support demand, yet occupancy and nightly rate vary by property, access and calendar. Old Town can combine walkability with visitor demand. Lower Deer Valley benefits from resort proximity; Canyons Village offers managed product and amenities; Prospector may enter at a lower price but competes in a different guest segment. Deduct management, housekeeping, platform fees, utilities, hot tub, snow, repairs, insurance, tax, HOA, resort charges, furniture replacement and owner blocks before comparing yield with a long-term tenancy or no rental.",
                "Operations need documentary evidence. Obtain trailing property-level statements, bank deposits, tax filings, manager invoices and the exact future contract. Reconcile the rentable bedroom count and occupancy with permits and HOA rules. Ask whether the licence follows the owner, the premises or neither after transfer. Confirm response-time obligations and who manages a heating failure during a storm. At Canyons Village, a high monthly HOA may fund useful services but can materially compress net income. In Deer Valley, shuttle or club access may depend on separate terms. Model a poor-snow year, weaker event calendar and higher insurance premium rather than capitalising one exceptional winter.",
                "Capital upside is credible but segmented. The Park City Board of REALTORS reported a firm Q1 2026 single-family median in Park City proper, a very different Canyons condo median and strong trailing activity in Lower Deer Valley. Those figures show market depth, not guaranteed appreciation. Deer Valley East Village and Jordanelle introduce major new supply and amenities while also changing traffic, construction and future competition. Established Old Town scarcity is different from a new managed residence; Park Meadows is different again. Buy utility and durable access, not a development announcement. Run a flat-price exit after all transaction and carrying costs and require the personal-use case to survive it."
            ),
        ),
        DossierLens(
            "Pay for a buyer pool you can reach again",
            ("value_entry", "exit_liquidity"),
            (
                "Value entry is relative at Park City prices. A Prospector studio can offer the lowest capital and easier daily services, but size, HOA, building condition and permitted use define the bargain. Old Town commands a walkability and scarcity premium, often in old or heavily rebuilt structures. Lower and Upper Deer Valley price resort access and service. Canyons Village spans modest hotel-style units to luxury residences, with recurring charges and management agreements central to value. Park Meadows provides residential utility; Kimball Junction and Snyderville Basin can offer space and highway access without the same historic or ski premium. Compare like format, boundary and use.",
                "The official market evidence below is deliberately bounded. Park City proper's Q1 2026 single-family median comes from 26 sales. Canyons Village's condo median comes from 26 sales and a changing mix. Lower Deer Valley's $2.85 million figure covers 53 trailing-12-month condo sales, not one quarter. None values the three asking observations. Match completed sale, property type, legal area, age, renovation, furnishings, parking, view, ski access, HOA and rental rights. Commission an inspection and appraisal where useful. An asking price per square metre can be distorted by outdoor area, hotel services or an unusually small unit.",
                "Exit liquidity is better than in many specialist ski towns because the airport, U.S. buyer base and variety of product create multiple demand channels. It is still not uniform. A practical Prospector or Park Meadows home can reach residents and second-home buyers. A well-run Canyons unit depends on building reputation, fees and rental evidence. A Deer Valley estate needs a much smaller high-net-worth pool. New East Village supply may compete with existing stock. Before purchase, ask two agents who did not source the property who would buy it next, typical marketing time and the discount needed to clear. Model a long sale and preserve cash reserves."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Old Town combines culture, dining and trails; Deer Valley and Canyons add polished recreation with more resort dependence.",
        "global_access": "Park City benefits from Salt Lake City airport access, while storms and Interstate 80 traffic still affect the final journey.",
        "ownership_clarity": "Park City offers open U.S. ownership, but title, HOA, historic rules and cross-border tax structure remain property-specific.",
        "regulatory_safety": "Park City and Summit County use different nightly-rental licences, with zoning, inspections and HOA limits layered above them.",
        "rental_profit": "Old Town, Deer Valley and Canyons can earn strong peaks, but management, HOA, snow, tax and insurance compress net results.",
        "capital_upside": "Park City scarcity and Deer Valley expansion support selected assets, while Jordanelle supply and product mix prevent blanket appreciation claims.",
        "retirement_fit": "Park City Hospital and local transit support retirement, but elevation, ice, stairs and specialist-care travel require planning.",
        "exit_liquidity": "Prospector and Park Meadows reach broader buyers than a high-fee Canyons residence or ultra-prime Deer Valley estate.",
        "foreigner_fit": "Park City has international-owner advisers, while FIRPTA, estate tax, immigration, banking and insurance still demand independent coordination.",
        "value_entry": "Prospector and Kimball Junction can enter below Old Town or Deer Valley, but HOA, access and lawful use change value.",
    },
    market_anchors=(
        {"location": "Park City proper single-family homes", "evidence": "$4.016 million", "buyer_read": "Q1 2026 median across 26 sales in MLS Areas 1–9; a broad city-limits signal, not an Old Town or Deer Valley valuation.", "source_label": "Park City Board of REALTORS Q1 2026", "source_url": "https://parkcityrealtors.com/2026/04/2026-1st-quarter-statistics/"},
        {"location": "Canyons Village condominiums", "evidence": "$1.34 million", "buyer_read": "Q1 2026 median across 26 sales generating $48.1 million; the Board cautions that product mix affected the year-on-year change.", "source_label": "Park City Board of REALTORS Q1 2026", "source_url": "https://parkcityrealtors.com/2026/04/2026-1st-quarter-statistics/"},
        {"location": "Lower Deer Valley condominiums", "evidence": "$2.85 million", "buyer_read": "Trailing 12-month median across 53 sales, not a Q1-only figure; use period and property type before comparing a candidate.", "source_label": "Park City Board of REALTORS Q1 2026", "source_url": "https://parkcityrealtors.com/2026/04/2026-1st-quarter-statistics/"},
    ),
    micro_locations_intro="Park City / Deer Valley is a set of operating patterns, not one price band. These groupings are orientation aids rather than valuation zones. Verify the municipal boundary, exact HOA, nightly-rental map, transit, snow access, insurance and completed evidence for every address.",
    micro_locations=(
        {"name": "Old Town / Park City core", "best_for": "Walkability and mountain-town life", "daily_life": "Compact, steep and visitor-active", "diligence": "Historic rules, parking, noise, snow and rental zoning"},
        {"name": "Lower / Upper Deer Valley", "best_for": "Resort service and ski proximity", "daily_life": "Premium and increasingly car or shuttle-led", "diligence": "HOA, shuttle, slope, snow, insurance and resale pool"},
        {"name": "Canyons Village / Snyderville Basin", "best_for": "Managed resort access and highway connection", "daily_life": "Resort core within a broader suburban basin", "diligence": "Fees, manager, zoning, construction and product competition"},
        {"name": "Park Meadows / Prospector / Kimball Junction", "best_for": "Year-round resident practicality", "daily_life": "Services, transit and ordinary errands", "diligence": "Exact walkability, building condition, traffic and HOA"},
    ),
    checklist=(
        "Confirm immigration, healthcare, tax residence and cross-border estate structure.",
        "Choose Old Town, Deer Valley, Canyons or the residential basin first.",
        "Travel airport, hospital, grocery and resort routes in snow and peak traffic.",
        "Verify title, survey, permits, municipal boundary, zoning and historic controls.",
        "Read HOA, reserves, insurance, litigation, management and special-assessment evidence.",
        "Inspect structure, roof, snow systems, freeze protection, wildfire and drainage exposure.",
        "Clear nightly-rental licence, inspection, tax, occupancy and local-manager duties in writing.",
        "Model five-year cash outlay and identify the future resale buyer before signing.",
    ),
    references_intro="Legal, tax, licensing, market, transport, healthcare, hazard and listing claims were reviewed on 22 August 2026. Recheck every time-sensitive source no later than 22 February 2027 and immediately after any tax, zoning, HOA, licensing, transport, hazard, insurance, market data or listing change. Obtain current U.S. and Utah legal, immigration, tax, estate, title, building and insurance advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "United States property guide", "url": "/countries/united-states-property/"},
        {"label": "IRS: FIRPTA withholding", "url": "https://www.irs.gov/individuals/international-taxpayers/firpta-withholding"},
        {"label": "IRS: nonresident estates with U.S. assets", "url": "https://www.irs.gov/individuals/international-taxpayers/some-nonresidents-with-us-assets-must-file-estate-tax-returns"},
        {"label": "Park City: nightly-rental licence and inspection", "url": "https://www.parkcity.org/departments/finance-accounting/apply-for-a-business-licenses/nightly-rental-license"},
        {"label": "Park City: planning and nightly-rental map", "url": "https://parkcity.org/departments/planning"},
        {"label": "Summit County: owner and manager nightly-rental licensing", "url": "https://summitcountyutah.gov/274/Business-Licensing"},
        {"label": "Park City: building, snow, soil and Wildland Urban Interface requirements", "url": "https://parkcity.org/departments/building-department/forms-and-other-information"},
        {"label": "Park City: community code and snow-removal guidance", "url": "https://www.parkcity.org/departments/building-department/community-code-compliance"},
        {"label": "Park City Transit: current local service", "url": "https://www.parkcity.org/departments/transit-bus"},
        {"label": "Park City: current Park City–Salt Lake City commuter timetable", "url": "https://www.parkcity.org/home/showpublisheddocument/76542/638690162463430000"},
        {"label": "Park City Hospital: emergency and trauma care", "url": "https://intermountainhealthcare.org/locations/park-city-hospital/emergency"},
        {"label": "Park City Board of REALTORS: Q1 2026 market report", "url": "https://parkcityrealtors.com/2026/04/2026-1st-quarter-statistics/"},
        {"label": "PCMLS: Prospector Carriage House studio asking observation", "url": "https://www.parkcity-realestate.com/property-search/detail/50/12601822/1940-prospector-ave-park-city-ut-84060/"},
        {"label": "PCMLS: Canyons Fairway Springs townhouse asking observation", "url": "https://www.parkcity-realestate.com/property-search/detail/50/12603567/4232-fairway-ln-park-city-ut-84098/"},
        {"label": "PCMLS: Lower Deer Valley Hidden Oaks home asking observation", "url": "https://www.parkcity-realestate.com/property-search/detail/50/12600813/35-hidden-oaks-ln-park-city-ut-84060/"},
    ),
    images=(
        DossierImage("town", "/assets/park-city-deer-valley-town-hero.webp", "Park City historic town and surrounding Wasatch mountains in calm morning light", "Park City works best when the mountain town remains useful beyond a ski week.", "hero"),
        DossierImage("winter-daily-life", "/assets/park-city-deer-valley-winter-daily-life.webp", "Residents clearing a Park City residential street after winter snow", "Snow access, heating and maintenance are part of ordinary ownership.", "wide"),
        DossierImage("summer-transit", "/assets/park-city-deer-valley-summer-transit.webp", "Mature residents using a Park City bus stop beside a green-season trail", "Year-round utility depends on transport, services and life between winter peaks.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Park City / Deer Valley through five destination lenses",
    assessment_intro="Here’s how Park City / Deer Valley scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show a Prospector studio, a Canyons Village townhouse and a Lower Deer Valley home. USD is both local and comparison currency; each area figure is converted from the listing's stated square feet.",
    market_anchors_intro="These are public market signals—not valuations. They cover different property types, areas and periods; reconcile every candidate for exact location, legal area, age, condition, HOA, permitted use and completed comparable evidence.",
    orientation_groups=(
        DossierOrientationGroup("Salt Lake City to the historic core", (("Salt Lake City Airport", "International gateway"), ("Kimball Junction", "Highway and service hub"), ("Canyons Village", "Western resort base"), ("Old Town", "Historic walkable core"))),
        DossierOrientationGroup("Core to Deer Valley and Jordanelle", (("Prospector / Park Meadows", "Residential daily life"), ("Lower Deer Valley", "Town-adjacent resort area"), ("Upper Deer Valley", "Mid-mountain resort area"), ("East Village / Jordanelle", "Expansion and new supply"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current airport, commuter, local transit, shuttle and storm journey times from the exact address.",
    country_guide_url="/countries/united-states-property/",
    country_guide_label="United States property guide",
    rail_comparison="Compare Park City / Deer Valley with the full Atlas.",
)


HAKUBA_DOSSIER = PremiumDossierSpec(
    destination_id="hakuba",
    title="Hakuba Retirement Property Dossier",
    description="Assess Hakuba retirement property through village life, access, residence, healthcare, ownership, lodging rules, snow operations, value, resale, and current listings.",
    h1="Hakuba: buy the alpine life—and its operating reality",
    lede=(
        "Hakuba offers one of Asia’s most compelling four-season mountain settings, but it is not one seamless resort market. Happo and Wadano concentrate lift access and international hospitality; Echoland and Misorano mix restaurants, forest homes and driving; Iwatake is attracting year-round investment; Kamishiro and Goryu offer a quieter residential rhythm around rail and southern ski areas. A home that works brilliantly for winter holidays may be awkward for ordinary retirement life. This dossier starts with residence, healthcare and daily movement, then tests whether the address, building and operating plan deserve the view."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is selective. Hakuba can be an exceptional base for an active buyer who already has a credible right to live in Japan, enjoys real winter, accepts driving and Japanese-language administration, and values mountain life more than effortless healthcare or a broad resale pool. Foreigners can generally own Japanese real estate, but ownership does not create residence status, public-healthcare eligibility or a retirement visa. Japan’s designated-activities route for long sightseeing is temporary and tightly conditioned, not a permanent-retirement solution. Confirm a renewable residence basis, spouse position, health-insurance route and tax residence before treating any chalet as a long-term home.",
        "Hakuba is weaker for a buyer who expects a property purchase to solve immigration, needs urban specialist care close by, cannot manage heavy snow, or wants passive holiday income without a licensed local operator. The village has clinics, including the Hakuba clinic in Kamishiro, while broader emergency and specialist care reaches beyond the village to institutions such as Omachi General Hospital and Azumi Hospital. That network is meaningful, but it is not equivalent to living beside a large city hospital. Test the exact clinic, pharmacy and emergency journey in winter, and plan how the household functions if driving becomes difficult.",
        "Proceed in order. Establish residence and healthcare; choose the village pattern that matches daily life; travel the airport, station, grocery and hospital routes with luggage and bad weather; then verify title, road, water, sewerage, planning, landscape controls, hazards, structure, heating, roof, insulation and snow management. If income matters, establish the lawful lodging route, operator, staffing, fire-safety and 2026 accommodation-tax obligations in writing. Finally, identify the future buyer and model a long sale. Hakuba rewards deliberate ownership; it punishes treating a winter holiday as a year-round operating plan."
    ),
    lenses_intro="The five paired lenses below translate Hakuba’s Atlas scores into choices a buyer can make. The score table records the complete ten-factor assessment once; the prose shows how the answer changes between village areas and property types.",
    lenses=(
        DossierLens(
            "Live the mountain after the lifts close",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Hakuba’s strongest case is lifestyle. Winter brings world-class snow, a mature ski culture and a community comfortable with international visitors. Green season adds hiking, cycling, rivers, agriculture and cooler mountain air. Happo and Wadano place an owner near lifts, hotels and restaurants, but the visitor economy can feel intense in peak winter and quieter between seasons. Echoland offers an animated dining strip; Misorano spreads into forested residential pockets. Iwatake has a growing year-round recreation identity. Kamishiro and Goryu feel more local and dispersed. The right choice depends on whether the buyer wants resort energy, privacy or ordinary village life.",
                "Retirement practicality is more demanding. Hakuba Station and the Hokujo centre provide municipal functions and everyday services, while southern Kamishiro has clinics and rail stops. Yet many desirable homes sit beyond a comfortable walk from groceries, pharmacy or year-round dining. Snowbanks narrow roads, parking needs active clearing, and an address that seems close on a summer map can become car-dependent in February. Test the daily loop at seven in the morning and after dark: front door to cleared road, supermarket, clinic, restaurant and station. Ask who clears the private drive, roof edge and emergency access when the owner is ill or absent.",
                "Healthcare needs a written sequence. Local clinics can handle primary needs, and Hakuba’s official material lists several village providers. More complex or time-critical care may involve Omachi or Azumi Hospital, so confirm ambulance coverage, winter drive time, department availability and how language support works. Property ownership does not unlock public insurance; eligibility follows residence and enrolment rules. A fit, skiing household may accept that trade-off today, but a retirement home should also work after an injury or reduced mobility. Single-level access, internal stairs, icy approaches, heating reliability and a nearby support person deserve as much attention as the mountain view."
            ),
            "winter-daily-life",
        ),
        DossierLens(
            "Measure the whole journey, not the resort transfer",
            ("global_access", "foreigner_fit"),
            (
                "Hakuba is internationally known but not internationally direct. The common approach uses Tokyo airports, rail to Nagano and a bus to Hakuba, or the slower Oito Line through Matsumoto or Itoigawa. Hakuba Village’s current transport plan identifies the Oito Line, seasonal local routes, the Nagano–Hakuba express bus, demand taxis and multiple ski shuttles. That mix creates options, not metro-level redundancy. A buyer should time front door to airport with a missed bus, delayed train, heavy luggage and an evening arrival. Happo bus terminal and Hakuba Station are different gateways; the useful one depends on the exact address.",
                "Internal movement changes by season. Happo and Wadano can offer lift and hospitality access, yet some slopes and side roads remain difficult on foot. Echoland and Misorano use shuttles in winter but many errands still favour a car. Iwatake lies north of the central village pattern; Kamishiro and Goryu align more closely with southern Oito Line stations but services are dispersed. Seasonal shuttles are designed around skiing, not necessarily medical appointments, grocery bags or late dinners. Read current timetables, ask what operates in May and November, and price a properly equipped vehicle, winter tyres, parking and snow clearing into normal ownership.",
                "Foreigner fit is relatively strong for a Japanese mountain village because the tourism economy includes English-speaking agents, managers and operators. That does not make the ownership system English-first. Registry documents, tax notices, neighbourhood communication, contractor instructions, planning submissions and accommodation-tax filings can remain Japanese-led. An absentee owner may also depend on staff during the same peak weeks when labour and trades are busiest. Appoint an independent bilingual lawyer and tax adviser, verify the manager’s physical coverage area and response standard, and maintain a local contact who can receive notices and enter the home. International hospitality is not the same as administrative self-sufficiency."
            ),
            "green-season-access",
        ),
        DossierLens(
            "Own the house, then prove the site works",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Japan generally allows foreign buyers to acquire ordinary freehold real estate, so Hakuba’s ownership score is strong. The work begins after that headline. Confirm the registered owner, boundaries, easements, legal road connection, utilities, extensions and permits. Hakuba’s current building guidance warns that road status must be checked and that building-confirmation rules apply. The village’s landscape and development framework can affect height, setback, colour and larger projects. A forest lot, converted lodge or older chalet may carry facts that a translated sales summary does not reveal. Use an independent judicial scrivener, lawyer, architect and building inspector before a binding commitment.",
                "Mountain construction requires a different inspection brief. Check structural records, roof form and snow load, insulation, glazing, heating capacity, frozen-pipe protection, ventilation, moisture, drainage, retaining works, balconies, chimneys and the dry room. Identify the water and wastewater system, confirm year-round access for service vehicles, and obtain actual fuel and electricity history. For managed apartments, read the owner-use rules, service charges, reserve position, operator agreement, furniture obligations, insurance and transfer terms. For detached homes, price roof clearing, driveway clearing, exterior treatment and emergency attendance. A beautiful timber interior does not answer whether the property survives an unattended freeze.",
                "Hazards are address-specific. Hakuba’s official map covers flood, landslide, earthquake and evacuation information, while the tourist safety manual identifies steep-slope and debris-flow warning areas. The village also records the 2014 Kamishiro Fault earthquake. Snow brings roof shedding, blocked access and avalanche questions near particular terrain; summer rain adds drainage and slope risk. Check the latest maps, walk the evacuation route and inspect retaining structures, culverts and neighbouring slopes. Ask an insurer to quote the exact building and intended use before purchase. Being outside a coloured map area is not proof of zero risk, and a clear title is not proof of a safe site."
            ),
        ),
        DossierLens(
            "Treat lodging income as a staffed business",
            ("rental_profit", "capital_upside"),
            (
                "Hakuba has powerful winter demand and improving green-season visitation, but gross nightly rates are not net rental profit. A successful operation needs lawful use, guest acquisition, cleaning, linen, snow clearing, heating, key access, repairs, multilingual communication and someone able to respond during storms. Happo and Wadano benefit from recognised resort access; Echoland and Misorano add dining and chalet inventory; Iwatake may benefit from year-round development; Kamishiro and Goryu can offer lower entry and a quieter base. Each area has different occupancy, staffing and transport assumptions. Demand evidence must be property-specific and dated.",
                "Permission is layered. Japan’s national private-lodging route caps minpaku at 180 nights a year and can be tightened by local, building or management rules; hotel and simple-lodging licences are different routes. From 1 June 2026, Hakuba’s accommodation tax applies to qualifying stays in hotels, ryokan, simple lodgings and private-lodging facilities. Operators collect and remit it, and current village guidance sets registration, records and filing duties. Confirm the exact premises, zoning, building and fire-safety position, notification or licence, absent-owner management, owner-use calendar and tax process before assigning any rental value. A listing’s phrase “rental potential” is not legal clearance.",
                "Capital upside is plausible but must be separated from promotional momentum. Official appraisals show strong recent movement in selected resort areas, and the village publishes a growing list of hotel and villa projects. That can improve amenities and international attention; it can also intensify construction, traffic, labour competition, infrastructure pressure and entry pricing. Misorano, Echoland and Iwatake do not share one land value, and a new managed unit does not have the same future buyer as an older Kamishiro house. Model flat nominal resale after all costs. Appreciation should reward scarce quality and durable access, not rescue weak condition, unclear use or an overpaid winter story."
            ),
        ),
        DossierLens(
            "Pay for utility—and preserve a believable exit",
            ("value_entry", "exit_liquidity"),
            (
                "Hakuba’s value-entry score reflects wide dispersion rather than low prices. Official evidence places a 2026 Misorano resort-home site far above an ordinary residential point near Hakuba Station, while a 2025 Echoland commercial benchmark sits higher again. These are specified bare-land or commercial appraisals, not values for finished homes. The three current listings below show the same fragmentation: a large Misorano chalet, a Kamishiro log home and a managed Happo-area apartment ask buyers to pay for different combinations of space, access, condition and operating infrastructure. Compare land, building and contractual value separately rather than relying on one village average.",
                "Entry diligence should expose the costs hidden by format. An older detached house may look inexpensive per square metre but require insulation, roof, heating, plumbing and access work. A log home can demand specialised maintenance. A managed ski apartment may cost much more per square metre while transferring some operating burden to an owner contract and shared budget. Neither format is automatically better. Obtain completed transaction evidence where available, inspect the building, reconcile legal floor area, read every recurring charge and build a five-year cash-outlay model including tax, insurance, utilities, snow, management, repairs, currency and eventual selling costs.",
                "Exit liquidity is the final discipline. A conventional, well-maintained house on a straightforward road near year-round services can reach local residents, Japanese second-home buyers and international purchasers. A large lodge needs an operator or redevelopment buyer. A premium managed apartment depends on the building’s reputation, charges, owner-use rules and rental record. Singular design, remote access or deferred snow damage narrows the pool. Before buying, ask two agents who did not source the property who would buy it next, how long comparable homes took to sell and what discount cleared them. The best Hakuba asset remains useful when the snow year disappoints."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Hakuba combines exceptional winter sport with green-season trails; Happo energy and Kamishiro calm suit distinctly different owners.",
        "global_access": "Hakuba relies on Nagano buses and the Oito Line; Happo terminal convenience does not remove weather-sensitive last-mile travel.",
        "ownership_clarity": "Hakuba follows Japan’s open ownership framework, while every chalet still needs title, road, boundary, utility and building verification.",
        "regulatory_safety": "Hakuba lodging permissions, 2026 accommodation tax, landscape controls and address-level slope or flood hazards require written clearance.",
        "rental_profit": "Happo and Wadano have strong winter demand, but Hakuba cleaning, staffing, snow operations and permissions reduce headline yield.",
        "capital_upside": "Misorano, Echoland and Iwatake development support selected sites, yet construction momentum does not guarantee resale appreciation.",
        "retirement_fit": "Hakuba offers village clinics and active living, but specialist hospitals, winter driving and legal residence constrain easy retirement.",
        "exit_liquidity": "Hakuba homes near services and clear roads reach more buyers; singular lodges and operator-dependent units need longer exits.",
        "foreigner_fit": "Happo and Echoland offer English-facing services, while Hakuba tax, planning, contractor and neighbourhood work remains Japanese-led.",
        "value_entry": "Kamishiro houses can enter below managed Happo apartments, but Hakuba renovation, heating, snow and access costs change the comparison.",
    },
    market_anchors=(
        {"location": "Misorano holiday-home area", "evidence": "27,400 JPY/m²", "buyer_read": "Official 1 January 2026 appraisal for a 999 m² bare-land resort-home site; up 33% year on year, but the report describes a thin, individual market.", "source_label": "MLIT 2026 appraisal", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/20/2026204850001.html"},
        {"location": "Hokujo near Hakuba Station", "evidence": "8,930 JPY/m²", "buyer_read": "Official 1 January 2026 appraisal for a 528 m² bare-land residential site about one kilometre east of Hakuba Station; not a resort-home valuation.", "source_label": "MLIT 2026 appraisal", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/20/2026204850002.html"},
        {"location": "Echoland commercial strip", "evidence": "67,500 JPY/m²", "buyer_read": "Nagano Prefecture’s 1 July 2025 land-price survey appraisal for a 738 m² commercial site; commercial context means it cannot value a nearby chalet.", "source_label": "Nagano Prefecture 2025 land-price survey", "source_url": "https://www.pref.nagano.lg.jp/kensetsu/infra/tochi/chika/documents/66r7hakuba.pdf"},
    ),
    micro_locations_intro="Hakuba is best read as four operating patterns, not one resort average. These are orientation aids rather than price zones. Confirm the exact village address, road status, winter clearing, utilities, planning, hazard layers, nearest services and lawful use before comparing asking prices.",
    micro_locations=(
        {"name": "Happo / Wadano", "best_for": "Lift access and international hospitality", "daily_life": "Resort-led, walkable only in selected pockets", "diligence": "Owner contract, peak traffic, slope, snow and service charges"},
        {"name": "Echoland / Misorano", "best_for": "Restaurants and forest homes", "daily_life": "Mixed walk, shuttle and car pattern", "diligence": "Road, drainage, building condition and lawful lodging use"},
        {"name": "Iwatake / Shinden / Kirikubo", "best_for": "Earlier-stage year-round mountain case", "daily_life": "Village setting north of the centre", "diligence": "Development pipeline, transport, utilities and future buyer pool"},
        {"name": "Kamishiro / Goryu", "best_for": "Quieter residential and southern ski access", "daily_life": "Rail-adjacent in places, otherwise car-led", "diligence": "Healthcare route, heating, snow clearing and resale depth"},
    ),
    checklist=(
        "Confirm a renewable Japan residence basis and healthcare route before purchase.",
        "Choose the Happo, Echoland, Iwatake or Kamishiro daily-life pattern first.",
        "Travel the exact airport, station, grocery and hospital routes in winter.",
        "Verify title, boundary, legal road, utilities, planning and landscape controls.",
        "Inspect structure, roof, snow load, insulation, heating, moisture and freeze protection.",
        "Overlay current flood, slope, earthquake, snow and evacuation evidence.",
        "Clear lodging permission, operator, fire safety, staffing and accommodation tax in writing.",
        "Model five-year cash outlay and name the future resale buyer before signing.",
    ),
    references_intro="Legal, administrative, market, transport, healthcare, hazard and listing claims were reviewed on 22 August 2026 against the sources below. Recheck every time-sensitive source no later than 22 February 2027, and immediately after any law, municipal rule, tax, transport, hazard-map, development, operator or listing change. Obtain current Japanese immigration, legal, tax, building, insurance and healthcare advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "Japan retirement property guide", "url": "/japan-retirement-property-foreign-buyers/"},
        {"label": "Ministry of Foreign Affairs: long sightseeing and recreation status", "url": "https://www.mofa.go.jp/ca/fna/page22e_000738.html"},
        {"label": "Ministry of Finance: non-resident real-property reporting", "url": "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html"},
        {"label": "National Tax Agency: non-resident Japanese real estate tax", "url": "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf"},
        {"label": "Ministry of Land: real-estate tax and transaction guidance", "url": "https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html"},
        {"label": "Japan Tourism Agency: Private Lodging Business Act", "url": "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html"},
        {"label": "Hakuba Village: residence, building, landscape and development guidance", "url": "https://www.vill.hakuba.lg.jp/gyosei/soshikikarasagasu/kensetsuka/tochiriyou_kenchiku/kenchikukeikankaihatsu/index.html"},
        {"label": "Hakuba Village: building standards and road checks", "url": "https://www.vill.hakuba.lg.jp/gyosei/soshikikarasagasu/kensetsuka/tochiriyou_kenchiku/kenchikukeikankaihatsu/kenchikukijunhou/index.html"},
        {"label": "Hakuba Village: current development projects", "url": "https://www.vill.hakuba.lg.jp/gyosei/soshikikarasagasu/kensetsuka/tochiriyou_kenchiku/kenchikukeikankaihatsu/toshikeikakuhou/13382.html"},
        {"label": "Hakuba Village: hazard map", "url": "https://www.vill.hakuba.lg.jp/gyosei/soshikikarasagasu/somuka/somukakari/11/2_1/861.html"},
        {"label": "Hakuba Village: tourist disaster manual", "url": "https://www.vill.hakuba.lg.jp/material/files/group/7/bousaimanyuaruen.pdf"},
        {"label": "Hakuba Village: 2025–2030 public transport plan", "url": "https://www.vill.hakuba.lg.jp/material/files/group/7/2025033101-1.pdf"},
        {"label": "Hakuba Village: 2026 accommodation tax", "url": "https://www.vill.hakuba.lg.jp/gyosei/soshikikarasagasu/zeimuka/kazeigakari/2/syukuhakuzei/13525.html"},
        {"label": "Hakuba Village: accommodation-tax operator guidance", "url": "https://www.vill.hakuba.lg.jp/gyosei/soshikikarasagasu/zeimuka/kazeigakari/2/syukuhakuzei/13857.html"},
        {"label": "Hakuba Village: current village medical providers", "url": "https://www.vill.hakuba.lg.jp/material/files/group/12/kosodategaidobukkuR8.pdf"},
        {"label": "Azumi Hospital: Hakuba clinic and hospital access", "url": "https://www.azumi-ghp.jp/access/"},
        {"label": "Azumi Hospital: emergency and specialist hospital role", "url": "https://www.azumi-ghp.jp/about/gaiyou/"},
        {"label": "Omachi General Hospital: emergency and out-of-hours care", "url": "https://www.omachi-hospital.jp/visit/emergency/"},
        {"label": "MLIT: 2026 Misorano land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/20/2026204850001.html"},
        {"label": "MLIT: 2026 Hokujo residential land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/20/2026204850002.html"},
        {"label": "Nagano Prefecture: 2025 Hakuba land-price survey appraisals", "url": "https://www.pref.nagano.lg.jp/kensetsu/infra/tochi/chika/documents/66r7hakuba.pdf"},
        {"label": "Nikota Realty: Misorano Forest Chalet asking observation", "url": "https://www.nikotarealty.com/properties/misorano-forest-chalet"},
        {"label": "Hakuba Real Estate: Kamishiro Cozy House asking observation", "url": "https://www.hakubarealestate.com/property-listing/kamishiro-cozy-house"},
        {"label": "Hakuba Real Estate: Miru Residences Hakuba 207 asking observation", "url": "https://www.hakubarealestate.com/property-listing/miru-residences-hakuba-207-south-west-corner-dual-key-2-bedroom"},
    ),
    images=(
        DossierImage("alpine-village", "/assets/hakuba-alpine-village-hero.webp", "Hakuba village homes and fields beneath the Northern Japan Alps", "Hakuba’s appeal is a lived mountain landscape, not only a lift map.", "hero"),
        DossierImage("winter-daily-life", "/assets/hakuba-winter-daily-life.webp", "A cleared residential street in Hakuba after heavy winter snow", "A retirement home must remain accessible after the snow arrives.", "wide"),
        DossierImage("green-season-access", "/assets/hakuba-green-season-access.webp", "Residents near a Hakuba village bus stop during green season", "Year-round utility depends on ordinary transport and services between peak seasons.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Hakuba through five destination lenses",
    assessment_intro="Here’s how Hakuba scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show a Misorano chalet, a Kamishiro log home and a managed Happo-area apartment. JPY is primary; USD uses the recorded repository reference basis for comparison only.",
    market_anchors_intro="These are public market signals—not valuations. They compare specified bare-land residential and resort sites with an Echoland commercial site; none appraises a finished chalet or apartment.",
    orientation_groups=(
        DossierOrientationGroup("Northern and central Hakuba", (("Iwatake / Shinden", "Year-round mountain area"), ("Hakuba Station / Hokujo", "Village service centre"), ("Happo / Wadano", "Lift and hospitality core"), ("Echoland / Misorano", "Dining and forest homes"))),
        DossierOrientationGroup("Central to southern Hakuba", (("Happo bus terminal", "Nagano bus gateway"), ("Hakuba Station", "Oito Line gateway"), ("Kamishiro / Iimori", "Residential and clinic area"), ("Goryu", "Southern ski base"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current rail, bus and shuttle timetables, road clearing and the exact winter door-to-door route.",
    country_guide_url="/countries/japan-property/",
    country_guide_label="Japan property guide",
    rail_comparison="Compare Hakuba with the full Atlas.",
)


ANNECY_DOSSIER = PremiumDossierSpec(
    destination_id="annecy",
    title="Annecy Retirement Property Dossier",
    description="Assess Annecy property through year-round daily life, Geneva access, French ownership, tourist-let quotas, DPE, healthcare, hazards, value, resale, and current listings.",
    h1="Annecy: buy the year-round address, not only the lake view",
    lede="Annecy combines a working Alpine city, a celebrated lake and access to Geneva, but those advantages are distributed unevenly. Annecy centre and the Vieille Ville put daily services and the station within reach. Annecy-le-Vieux and Albigny connect established residential life with the north end of the lake. Sevrier and Saint-Jorioz on the west shore offer ordinary town services and a flatter lakeside rhythm. Veyrier-du-Lac, Menthon-Saint-Bernard and Talloires on the east shore sell the most dramatic views, often with steeper access, higher prices and a narrower buyer pool. This dossier tests which address still works in rain, winter traffic and ordinary retirement—not only on a clear summer day.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "Annecy is a premium lifestyle contender, not an effortless investment. The city is safe, useful and beautiful; the lake and mountains remain part of daily life rather than a resort set. Yet the financial case is compressed by high entry prices, modest net yields and a local tourist-let regime designed to protect housing. A foreign buyer can acquire French property, but ownership does not create a visa, residence right or public-healthcare eligibility. Non-EU buyers considering full-time retirement should establish the correct long-stay route first. France-Visas says the visitor route for a private stay over three months requires evidence of resources, accommodation and medical cover and does not permit professional activity. EU and Swiss buyers follow different mobility rules, so one sentence cannot cover every household.",
        "The strongest fit is a buyer who values year-round services, culture, walking and cycling, accepts a premium for scarcity, and can hold without depending on aggressive rent. Annecy centre, Albigny and Annecy-le-Vieux generally give the broadest daily-life case. The west shore can suit a buyer who wants more space and can test the bus, bicycle and road routine. The east shore suits a higher-budget household willing to exchange convenience and exit depth for outlook and village character. Look elsewhere first if the plan requires the home to create residence, a high non-resident mortgage, uncomplicated short-term letting, or a Geneva commute that never meets congestion, border or timetable friction.",
        "Proceed in this order: settle residence and healthcare; decide whether the household is city-led, west-shore practical or east-shore premium; travel the hospital, station, airport and grocery routes in ordinary winter conditions; then investigate the title, copropriété, planning, DPE, hazards and permitted use. Price tourist rent only after Grand Annecy confirms the current registration, change-of-use and quota position for the exact address and owner. The right Annecy purchase is not simply the home with the widest lake view. It is the address whose access, building file, carrying cost and future buyer pool remain convincing after the visitors leave.",
    ),
    lenses_intro="The five paired lenses below turn the postcard into ten buyer decisions. Each asks what daily life requires at a specific address; the score table then shows the complete Atlas assessment once.",
    lenses=(
        DossierLens(
            "Live with the lake after the visitors leave",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Annecy centre has the most complete year-round proposition. The Vieille Ville, station, markets, shops, restaurants, cultural venues and lakefront can form one walkable routine, although the prettiest lanes also bring visitors, noise and older-building constraints. The area around the gare is less romantic but more useful for rail and buses. Toward Albigny and Annecy-le-Vieux, the rhythm becomes more residential while the lake, parks and local services remain accessible. A buyer should walk the actual route to groceries, pharmacy and transit after dark and in rain; a map pin near the lake does not prove comfortable everyday access.",
                "The west shore changes the balance rather than merely lowering the price. Sevrier and Saint-Jorioz have schools, shops, restaurants, cycling and lake access within functioning towns. Some addresses can support a practical routine, but traffic on the main road and the distance between the home, bus stop and services matter. Menthon-Saint-Bernard, Veyrier-du-Lac and Talloires on the east shore offer stronger visual drama and village identity. They also include slopes, narrow roads, smaller service centres and property types whose maintenance and future buyer pool may be more specialised. Test stairs, gradients and parking as seriously as the view.",
                "Healthcare follows residence and geography. Ownership itself does not create access to France's public system; Assurance Maladie ties PUMa to stable and regular residence or another qualifying basis. The Centre Hospitalier Annecy Genevois site at Epagny Metz-Tessy provides 24-hour emergency services, SAMU and specialist flows, but a lake-shore buyer must measure the door-to-door route in congestion and bad weather. Routine care, pharmacy access and the availability of a regular doctor also matter. Retirement fit is strongest where a household can keep its daily life functioning if driving becomes difficult, not where a summer bicycle ride merely looks possible.",
            ),
        ),
        DossierLens(
            "Reach Geneva—and the hospital—without assuming an easy commute",
            ("global_access", "foreigner_fit"),
            (
                "Annecy's connectivity is real but must be described door to door. The multimodal station anchors regional trains and buses; Grand Annecy's mobility guidance places Pringy about one hour twenty-five minutes from Geneva by rail and Annecy about two hours ten minutes from Lyon in its service examples. An official bus route also connects toward Geneva Airport. Those links are useful for periodic international travel. They are not a guarantee of a frictionless daily Geneva commute once the walk, transfer, border conditions, strike risk, late return and final journey to a lake-shore home are included.",
                "Local mobility is equally address-sensitive. Grand Annecy publishes regular lake-shore bus services, with many corridors operating from early morning into the evening, while summer additions are a separate seasonal offer. Do not use July frequency to justify a February purchase. Annecy centre and parts of Annecy-le-Vieux can work without a car for many trips. Sevrier and Saint-Jorioz may combine bus, bicycle and driving. The east shore can be more dependent on the road, particularly from a hillside house. Travel the exact route at the time it will normally be used and add a failed-connection scenario.",
                "Foreigner fit is helped by Geneva's international economy and by the area's experience with cross-border residents, but administration remains French and often technical. The notaire, bank, copropriété manager, insurer, tax office, utility providers and contractors may require French documents and local follow-through. Cross-border work introduces separate residence, tax, healthcare and social-security questions that a property guide cannot settle. Budget for independent French legal and tax advice, and for a bilingual contact if the household cannot handle notices and building meetings. International access is an asset; it does not remove the need to operate locally.",
            ),
            "winter-access-healthcare",
        ),
        DossierLens(
            "Own clearly, then read the building and energy file",
            ("ownership_clarity", "regulatory_safety"),
            (
                "France generally permits a foreigner to acquire ordinary residential property, with the notaire coordinating the authentic deed, searches, registration and transaction funds. That clarity should not be confused with a light diligence file. For an apartment, obtain the copropriété rules, recent meeting minutes, service-charge accounts, arrears, reserve position, planned works, insurance claims, legal disputes, floor-area evidence and any restriction on furnished or tourist use. For a house, verify boundaries, easements, access rights, planning permissions, drainage, retaining structures, roof, insulation and all extensions. A lake-access claim must be documented, not inferred from a photograph.",
                "Energy performance can change both comfort and lawful rental use. France's DPE schedule restricts the long-term letting of G-rated homes from 2025, with F and E stages scheduled for 2028 and 2034. The current Annecy sample includes an E-rated city apartment and an F-rated Veyrier-du-Lac house, showing why the label must lead to an engineering and cost discussion rather than a footnote. Ask what works are technically possible, whether copropriété approval is needed, what subsidies or restrictions apply, and whether the seller's floor area and diagnostic pack match the asset. A low energy grade can affect bills, rentability and resale.",
                "Planning and hazards are parcel decisions. Grand Annecy's PLUi-HMB entered force on 12 March 2026 and its interactive map is the starting point for zoning, but the mairie and a qualified adviser should confirm what the current building may lawfully do. Géorisques records flood, earthquake, ground and other natural-risk context for Annecy; shore and hillside properties add drainage, water, slope, retaining-wall and access questions. Review the official address report, seller's risk statement, catastrophe history, insurance terms and physical site. Being outside one coloured zone is not a guarantee against water or movement.",
            ),
        ),
        DossierLens(
            "Clear the tourist-let quota before underwriting a yield",
            ("rental_profit", "capital_upside"),
            (
                "Annecy's visitor demand is strong, but the legal right to serve it is not an automatic feature of a home. Grand Annecy's change-of-use regime took effect on 1 June 2025, with the transition ending on 1 October 2025. The framework uses registration, local quotas and owner or property limits; secondary residences generally require authorization, while principal residences follow a different route. The applicable zone, legal owner, building rules and current local decisions must be confirmed in writing. A listing described as suitable for seasonal rental is marketing until those checks are complete.",
                "Even a permitted operation must be underwritten like a small hospitality business. Model platform fees, cleaning, linen, utilities, insurance, tax, accounting, guest communication, maintenance, vacancy and the operator's contract. Then compare it with long-term rent, occasional personal use and no rent. Furnished rental falls within French BIC tax rules, and non-residents can owe French tax on French-source income; the 2026 guidance on professional furnished-rental status reinforces the need for buyer-specific advice. A Geneva-facing long-term tenancy may look less exciting but can be easier to operate than a quota-dependent tourist story.",
                "Capital upside is plausible only as an address-and-product thesis. The protected landscape, limited supply and international reach can support selected homes, but the starting price already reflects much of that recognition. Annecy centre and established residential areas have deeper ordinary demand. A west-shore apartment near services can appeal to year-round households. A large east-shore villa may be scarce yet depend on a smaller group able to accept the price, slope and renovation burden. Do not use the lake's global name as a substitute for completed sales, condition adjustments and a realistic exit period.",
            ),
            "west-shore-daily-life",
        ),
        DossierLens(
            "Pay for daily usefulness, not only a lake view",
            ("value_entry", "exit_liquidity"),
            (
                "Official Notaires des Savoie evidence gives three useful anchors for completed sales to 31 December 2025: old Annecy apartments at a median €5,140/m², old houses at €670,000, and new apartments at €6,550/m². These are broad market signals, not prices for a specific building, lake view or commune. The current asking examples below sit on very different parts of the curve: a compact Annecy apartment, a Saint-Jorioz family apartment and a premium Veyrier-du-Lac house. The spread is the lesson. Reconcile every candidate against the correct property type and completed evidence.",
                "Value entry comes from avoiding the wrong premium. In Annecy centre, pay for useful walking access, sound copropriété governance and a credible building rather than an unquantified 'near lake' label. Around Albigny and Annecy-le-Vieux, distinguish genuine service access from a car-led hillside address. In Sevrier and Saint-Jorioz, test the road and bus routine and avoid pricing a compromised plot as waterfront scarcity. In Veyrier-du-Lac, Menthon-Saint-Bernard and Talloires, separate protected outlook, documented access and renovation quality from a costly view that brings slope, energy and maintenance work.",
                "Exit liquidity depends on how many future buyers can use the home. A sensible apartment near the station, lake and services can appeal to local households, French second-home buyers and some international buyers. A well-located west-shore home may retain a credible family market. A singular east-shore house can command attention but take longer to match with a budget, taste and renovation appetite. Model five-year cash outlay including acquisition costs, financing, copropriété contributions, energy works, tax, insurance, repairs and sale costs. Before signing, ask two agents who did not source the property how they would resell it and to whom.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Annecy combines a working Alpine city with lake access; Saint-Jorioz and Talloires trade urban ease for more village character.",
        "global_access": "Annecy station and Pringy rail links support Geneva access, but shore addresses add road, bus and last-mile friction.",
        "ownership_clarity": "Annecy follows France's established notaire-led ownership system; copropriété records, easements, planning and diagnostics remain property-specific.",
        "regulatory_safety": "Annecy tourist quotas, DPE rules and Grand Annecy planning require written address-level checks before rental or renovation assumptions.",
        "rental_profit": "Annecy visitor demand is strong, but quotas, operator costs, tax and high entry prices compress dependable net rental returns.",
        "capital_upside": "Annecy scarcity and Geneva reach support selected assets, while east-shore premiums leave less room for execution errors.",
        "retirement_fit": "Annecy centre and Albigny offer services and mobility; remote shore homes require a tested route to Epagny Metz-Tessy healthcare.",
        "exit_liquidity": "Annecy city apartments reach the broadest buyer pool; singular Veyrier-du-Lac and Talloires houses may need longer exits.",
        "foreigner_fit": "Annecy is internationally connected through Geneva, but French tax, copropriété and cross-border administration still require local professional support.",
        "value_entry": "Annecy, Saint-Jorioz and Veyrier-du-Lac occupy distinct price bands; value depends on daily utility, condition and buyer-pool depth.",
    },
    market_anchors=(
        {"location": "Annecy old apartments", "evidence": "€5,140/m²", "buyer_read": "Median for completed old-apartment sales to 31 December 2025; reconcile the exact quarter, building, condition and outlook.", "source_label": "Notaires des Savoie 2026 report", "source_url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
        {"location": "Annecy old houses", "evidence": "€670,000", "buyer_read": "Median for completed old-house sales to 31 December 2025; it does not price an east-shore lake house or renovation burden.", "source_label": "Notaires des Savoie 2026 report", "source_url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
        {"location": "Annecy new apartments", "evidence": "€6,550/m²", "buyer_read": "Median for completed new-apartment sales to 31 December 2025; programme, parking, VAT and delivery risk still differ.", "source_label": "Notaires des Savoie 2026 report", "source_url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
    ),
    micro_locations_intro="Annecy is best read as four daily-life patterns, not one lake market. These are orientation aids rather than price zones; confirm the commune, parcel, planning, hazard layers, transport and building file for the exact address.",
    micro_locations=(
        {"name": "Annecy centre / Vieille Ville", "best_for": "Walkable city and station life", "daily_life": "Services, culture and lake without routine driving", "diligence": "Noise, tourist pressure, older buildings and copropriété"},
        {"name": "Annecy-le-Vieux / Albigny", "best_for": "Residential city-lake balance", "daily_life": "Established neighbourhoods near the north shore", "diligence": "Slope, transit, exact walkability and building costs"},
        {"name": "Sevrier / Saint-Jorioz / Duingt", "best_for": "Practical west-shore living", "daily_life": "Town services, cycling and more space", "diligence": "Road congestion, bus frequency and daily driving"},
        {"name": "Veyrier-du-Lac / Menthon-Saint-Bernard / Talloires", "best_for": "Premium east-shore outlook", "daily_life": "Village and lake life with steeper access", "diligence": "Price, slope, energy works, access rights and exit depth"},
    ),
    checklist=(
        "Confirm the household's French residence, work-right and healthcare route before purchase.",
        "Choose the city, north-shore, west-shore or east-shore daily-life pattern first.",
        "Travel the exact station, Geneva Airport, grocery and hospital routes in winter traffic.",
        "Verify title, easements, cadastral boundaries, planning permissions and lake access rights.",
        "Read the copropriété file, diagnostics, DPE, planned works, insurance and service charges.",
        "Overlay current flood, earthquake, slope and other Géorisques evidence for the address.",
        "Clear registration, change-of-use quota, building rules, operator and tax in writing before pricing rent.",
        "Model five-year cash outlay and identify the future resale buyer before signing.",
    ),
    references_intro="Legal, administrative, market, transport, healthcare, hazard and listing claims were reviewed on 22 August 2026 against the sources below. Recheck every time-sensitive source no later than 22 February 2027, and immediately after any law, municipal quota, tax, transport, hazard-map, planning, DPE, building or listing change. Obtain current French immigration, legal, tax, notarial, building, insurance and healthcare advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "France property guide", "url": "/countries/france-property/"},
        {"label": "France-Visas: private stay over three months", "url": "https://france-visas.gouv.fr/en/sejour-touristique-de-plus-de-3-mois"},
        {"label": "Assurance Maladie: universal health protection", "url": "https://www.ameli.fr/assure/droits-demarches/principes/protection-universelle-maladie"},
        {"label": "Grand Annecy: tourist accommodation rules", "url": "https://www.grandannecy.fr/entreprendre/etre-accompagne/le-tourisme"},
        {"label": "Ville d'Annecy: 2025 furnished-tourist-let implementation", "url": "https://www.annecy.fr/fileadmin/mediatheque_annecy/Espace_presse/CP_meubl%C3%A9s-application_reglement_%C3%A9t%C3%A9_2025_17.06.25.pdf"},
        {"label": "Grand Annecy: current furnished-tourist-let regulation", "url": "https://www.grandannecy.fr/fileadmin/mediatheque/kiosque/Espace_presse/CP_meubles_de_tourisme.pdf"},
        {"label": "Service Public: DPE and rental restrictions", "url": "https://www.service-public.fr/particuliers/vosdroits/F16096"},
        {"label": "Service Public: tourist-accommodation rule changes", "url": "https://www.service-public.fr/entreprendre/actualites/A17883"},
        {"label": "French tax administration: non-resident French income", "url": "https://www.impots.gouv.fr/international-particulier/dois-je-declarer-mes-revenus-en-france"},
        {"label": "French tax administration: non-resident property income", "url": "https://www.impots.gouv.fr/international-particulier/questions/non-resident-i-receive-income-real-property-property-income-or"},
        {"label": "Service Public: real-estate wealth tax", "url": "https://www.service-public.fr/particuliers/vosdroits/F563"},
        {"label": "Grand Annecy: PLUi-HMB interactive map", "url": "https://espacecitoyen.grandannecy.fr/actualites/actualite/plui-hmb-cartographie-interactive-en-ligne"},
        {"label": "Grand Annecy mobility: train", "url": "https://mobilites.grandannecy.fr/train"},
        {"label": "Grand Annecy mobility: bus", "url": "https://mobilites.grandannecy.fr/bus"},
        {"label": "Centre Hospitalier Annecy Genevois: emergencies", "url": "https://www.ch-annecygenevois.fr/liste-des-services/urgences/"},
        {"label": "Géorisques: Annecy municipal risk report", "url": "https://www.georisques.gouv.fr/mes-risques/connaitre-les-risques-pres-de-chez-moi/rapport2/74010/Annecy/commune/74000"},
        {"label": "Notaires des Savoie: 2026 property-market observatory", "url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
        {"label": "Barnes: Annecy apartment asking observation", "url": "https://www.barnes-montblanc.com/achat-immobilier-luxe/annecy-74000/annecy-ville/appartement-luxe-annecy-74000-3635"},
        {"label": "Compimmo: Saint-Jorioz apartment asking observation", "url": "https://www.compimmo.com/fr/acheter/appartement/saint-jorioz-74410/all/all/all/2"},
        {"label": "Agence Clerc: Veyrier-du-Lac house asking observation", "url": "https://agence-clerc.com/fr/propri%C3%A9t%C3%A9/87077856"},
    ),
    images=(
        DossierImage("city-lake-daily-life", "/assets/annecy-city-lake-daily-life.webp", "Residents walking and cycling between Annecy city streets and the lake on an ordinary morning", "Annecy works best when the lake and daily services share one routine.", "hero"),
        DossierImage("winter-access-healthcare", "/assets/annecy-winter-access-healthcare.webp", "Mature residents waiting for a local bus near Annecy during a wet winter morning", "Test transport and healthcare access in ordinary winter conditions.", "wide"),
        DossierImage("west-shore-daily-life", "/assets/annecy-west-shore-daily-life.webp", "Residents carrying groceries through a west-shore Lake Annecy town", "Saint-Jorioz and Sevrier should be judged as working towns, not summer scenery.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Annecy through five destination lenses",
    assessment_intro="Here’s how Annecy scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations show the spread from a compact Annecy apartment through a Saint-Jorioz family home to a premium Veyrier-du-Lac house. They are asking evidence—not valuations. EUR is primary; USD uses the recorded ECB reference basis.",
    market_anchors_intro="These are official completed-sale market signals—not valuations. They compare broad Annecy product groups and must be adjusted for commune, exact address, view, condition, building, parking and lawful use.",
    orientation_groups=(
        DossierOrientationGroup("City and north shore", (("Annecy station / Vieille Ville", "Walkable city core"), ("Albigny", "Lakefront residential area"), ("Annecy-le-Vieux", "Established north-shore neighbourhoods"), ("Pringy / Epagny Metz-Tessy", "Rail and hospital direction"))),
        DossierOrientationGroup("Lake-shore choices", (("Sevrier", "Near-city west shore"), ("Saint-Jorioz / Duingt", "West-shore towns"), ("Veyrier-du-Lac / Menthon-Saint-Bernard", "Premium east shore"), ("Talloires", "Village and mountain-end setting"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current train, airport-bus and lake-shore timetables, seasonal service, congestion and the exact hospital route.",
    country_guide_url="/countries/france-property/",
    country_guide_label="France property guide",
    rail_comparison="Compare Annecy with the full Atlas.",
)


NISEKO_DOSSIER = PremiumDossierSpec(
    destination_id="niseko",
    title="Niseko Retirement Property Dossier",
    description="Assess Niseko property through Kutchan daily life, resort access, ownership, planning, lodging rules, snow operations, healthcare, value, resale, and current listings.",
    h1="Niseko: buy the operating reality, not only the powder",
    lede="Niseko is not one place or one property market. Kutchan is the working town, with the station, hospital, schools, supermarkets and a resident economy. Hirafu and Kabayama form the best-known international resort core. Hanazono is a more planned and premium resort proposition. Niseko Village, Annupuri and Moiwa create a southern arc with different lifts, operators, roads and buyer pools. The powder, Mount Yotei and international recognition are real advantages; so are the snow-clearing bill, seasonal staffing, car dependence, operator contract and narrow exit on the wrong product. This dossier asks whether a home works in February and May—and whether the legal, operational and resale evidence supports the price.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is selective rather than broadly positive. Niseko can be an exceptional second-home or active-retirement base for a buyer who wants winter sport, cool summers, landscape and an established international resort community, and who can carry substantial fixed costs without depending on optimistic rent. Kutchan gives the proposition ordinary services and year-round life that a pure ski village would lack. Hirafu offers the deepest visitor infrastructure and most recognisable address. Hanazono and the southern resort arc can deliver polished accommodation or quieter mountain access. None should be treated as interchangeable, and the premium resort product is not the default recommendation for a long-term resident.",
        "Property ownership does not create Japanese residence, public-healthcare eligibility or domestic borrowing access. A foreign buyer can generally acquire ordinary Japanese real estate, while a non-resident acquisition may require Foreign Exchange and Foreign Trade Act reporting through the Bank of Japan. Establish the right to live in Japan, healthcare and tax administration before treating a chalet or condo as a retirement home. Then distinguish a private residence from a lodging business. Kutchan and Niseko Town have municipal rules and accommodation taxes; national minpaku, hotel or ryokan routes are separate; a condominium or operator agreement may be stricter again.",
        "Proceed in an operational sequence. Choose between Kutchan town life, Hirafu or Kabayama, Hanazono, and Niseko Village, Annupuri or Moiwa. Travel the exact New Chitose route in winter and shoulder season. Confirm title, legal road access, planning, building records, snow design, utilities, hazard layers and maintenance. For a managed resort unit, read the operator agreement, owner-use calendar, furniture obligation, common charges, reserve position, consumption-tax treatment and complete rental statements. Model heating, snow clearing, insurance, management, empty periods and a slow resale. Buy only when the home remains useful without a record snow year or a marketing-deck yield.",
    ),
    lenses_intro="The five paired lenses below translate Niseko's ten Atlas dimensions into choices between a working town and several resort operating models. The full ten-factor assessment appears once in the score table.",
    lenses=(
        DossierLens(
            "Live beyond the powder calendar",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Niseko's lifestyle magnetism is obvious in winter but must be tested across the year. Hirafu is the most internationally legible base, with restaurants, ski services and visitor energy, yet many businesses shorten hours or close outside peak periods. Hanazono is more planned and resort-led. Niseko Village, Annupuri and Moiwa offer mountain access and a quieter setting, but daily errands are dispersed. Kutchan is different: it is a working town rather than a resort set, with supermarkets, schools, offices, rail and ordinary neighbourhoods. A long-stay buyer should spend November and May locally, not only February, and decide whether calm feels restorative or inconvenient.",
                "Retirement fit begins with healthcare and physical practicality. Kutchan Kosei Hospital is the regional hospital and lists 234 beds, multiple departments and emergency functions, making Kutchan the most practical base of the resort area. That does not guarantee the required specialist, language support, appointment or insurer treatment. More complex care can mean travel toward Otaru or Sapporo. Identify a regular clinic, pharmacy, emergency route and specialist plan before purchase. In winter, test whether an ambulance, taxi or household driver can reach the property after heavy snow, and whether stairs, icy paths or deep roof shedding create avoidable risk.",
                "The home itself should reduce, not romanticise, winter work. Prefer a legal main-level bedroom and bathroom, sheltered entry, safe snow-storage area, reliable heating, freeze protection, mechanical ventilation and a clear contractor plan. Ask who clears the drive and roof, by what service level, where snow is placed and what happens during staff shortages. A remote Kabayama, Annupuri or Moiwa house may offer space and quiet but increase driving and response time. A Kutchan house can provide a broader resident rhythm at a lower entry point. A managed Hirafu or Hanazono unit can remove work while replacing it with fees and operator dependence.",
            ),
            "winter-snow-operations",
        ),
        DossierLens(
            "Reach the resort—and the hospital—in winter",
            ("global_access", "foreigner_fit"),
            (
                "New Chitose is the principal international gateway, but the final journey is material. Official local guidance presents road, rail, bus and shuttle options, with road trips commonly around two hours in normal conditions and rail closer to three hours with transfers. Winter weather, traffic, missed connections and luggage can extend each. Direct resort buses and local shuttles are seasonal; a timetable useful in February may not exist in May. Drive or ride the actual door-to-door journey, including arrival after the final bus, and price private transfer or parking rather than using an airport-to-area headline.",
                "Local movement changes by submarket. Kutchan provides the rail station and ordinary services, but the resort areas climb away from town. Hirafu and Kabayama have the largest concentration of visitor infrastructure, yet steep roads and snowbanks change walkability. Hanazono has a purpose-built resort environment and still depends on the operating calendar. Niseko Village, Annupuri and Moiwa stretch along separate roads with limited cross-resort simplicity. A car improves independence but adds winter tyres, covered parking, snow clearing and driving exposure. Confirm current bus and shuttle service for the exact season, stop and owner status; do not assume a hotel guest service extends to a private owner.",
                "Niseko's international community, bilingual agencies and resort operators improve foreigner fit, but ownership administration remains Japanese. Ministry of Finance reporting is submitted in Japanese. Tax notices, registry documents, planning consultations, contractor discussions and neighbourhood matters may require local support. A branded residence can provide an English-facing interface while binding the owner to a detailed contract. A standalone house provides control while requiring a bilingual lawyer, tax adviser, building inspector and reliable local manager. Future Hokkaido Shinkansen service is a strategic possibility, not current access; the Kutchan tourism plan places later timing beyond the present buying decision.",
            ),
        ),
        DossierLens(
            "Own clearly, then clear the operating permissions",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Japan generally permits foreign ownership of ordinary land and buildings, but clear market access does not remove property-level risk. Verify the registered owner, boundaries, easements, mortgages, legal road frontage, utilities and every structure against the registry, survey and building records. In deep snow, inspect roof form, structural loading, water ingress, drainage, retaining walls and where neighbouring snow is shed. A renovated Kutchan house needs evidence of permitted and competently executed work. A resort condo needs title, common-area rights, bylaws, reserve position, insurance, litigation and a complete schedule of charges.",
                "Planning is especially local. Kutchan expanded landscape and development controls in March 2026, requires advance consultation in designated cases and warns that processing can take around three months. Its guidance also identifies areas where hotel, ryokan or simple-lodging uses are prohibited. That does not make an existing home or rental unlawful; it means the exact parcel, building and intended change must be checked against current maps and written municipal advice. A real-estate listing, former guest use or neighbouring lodge is not permission. Confirm whether extensions, change of use, signage, parking or future redevelopment would be allowed before valuing them.",
                "Short-stay operation has several gates. The national private-lodging route is capped at 180 nights and can require an administrator when the owner is absent. Kutchan publishes additional local restricted areas and periods, including school-related buffers. Hotel and ryokan licensing follows another route. Kutchan and Niseko Town administer their own accommodation taxes, so municipal boundary matters. Condominium bylaws and operator contracts can narrow use further. Obtain written advice that identifies the exact route, manager, fire and safety work, tax registration, reporting, guest response and permitted calendar. If any gate is unclear, underwrite the property as a private home with no tourist income.",
            ),
        ),
        DossierLens(
            "Treat every rental return as an operator statement",
            ("rental_profit", "capital_upside"),
            (
                "Niseko can produce high nightly rates in strong winter weeks, but gross revenue is not owner profit. Reconcile booked nights, achieved rate, cancellations and owner use with bank deposits and tax filings. Deduct operator commission, cleaning, linen, utilities, heating, snow clearing, repairs, furniture replacement, common charges, reserve contributions, insurance, platform fees and accommodation tax administration. Clarify whether quoted income includes or excludes Japanese consumption tax and whether the sale price is net or tax-inclusive. The MUWA observation below illustrates the issue: the page displays a primary net price and a higher total including JCT.",
                "Product and operator matter as much as location. A Hirafu condo may benefit from recognisable positioning and a developed rental ecosystem, but building reputation, room layout, management performance and owner-use restrictions drive outcomes. A Hanazono or Niseko Village residence may be tied more closely to a branded operator and development plan. Annupuri or Moiwa can attract buyers seeking quiet and snow access but may have thinner management and dining options. A standalone Kabayama chalet needs dependable staff, transport and guest response. Obtain several years of property-level statements and the full future contract; do not apply a resort-wide yield to a candidate.",
                "Capital upside is plausible but not assured. International recognition, snow quality and continuing investment support selected assets, while construction cost, planning restrictions and scarcity can constrain supply. The official 2026 Hirafu land appraisal nevertheless describes uncertainty from higher construction costs and regulation and notes an immature standard-site rental market. That is a useful brake on promotional certainty. Future rail and resort expansion may improve access or demand, but they can also bring supply and a long delivery period. Model flat real prices, a weaker winter, higher operating costs and currency movement before paying for an appreciation story.",
            ),
            "green-season-mobility",
        ),
        DossierLens(
            "Pay for the future buyer pool, not the brand alone",
            ("value_entry", "exit_liquidity"),
            (
                "Entry value changes dramatically over a short distance. The three official 1 January 2026 MLIT anchors are bare-land appraisals, not finished-home valuations: ¥200,000/m² for a 529 m² Hirafu resort-home site, ¥67,000/m² for a 330 m² central Kutchan residential site and ¥35,000/m² for a 201 m² northern Kutchan residential site. They show the resort premium and the need to identify what the buyer is paying for. Building area, construction quality, furniture, management rights, legal use, view and snow access must be valued separately. A blended Niseko average hides more than it explains.",
                "The three current asking observations make the same point. The renovated Kutchan house is the working-town entry and includes broker income and yield claims that remain unverified. Kizuna 202 is a smaller Upper Hirafu condo with a resort-location premium and a different management burden. MUWA Niseko 501 is a ski-in/out branded product priced far above both on a per-square-metre basis, with an explicit JCT question. These are dated asking observations, not recommendations, completed sales or proof of value. Commission matched completed evidence and an independent inspection or appraisal where useful.",
                "Exit liquidity follows the next buyer's use case. A practical Kutchan home can reach local households and long-stay buyers, but an older structure may be valued mainly for land. A well-run Hirafu condo can reach an international resort pool, while high common costs or weak statements shrink that pool. A distinctive chalet or ultra-premium branded unit needs fewer, wealthier buyers and can wait longer. Hanazono and the southern resorts have their own brands and operating ecosystems rather than one seamless resale market. Before purchase, ask two agents who did not source the home who would buy it next, on what completed evidence and after what likely marketing period.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Niseko pairs exceptional snow and summer landscape with Kutchan's working-town services; resort life becomes much quieter between peak seasons.",
        "global_access": "Niseko uses New Chitose road, rail and seasonal bus links, while winter weather and resort last miles weaken headline journey times.",
        "ownership_clarity": "Niseko follows Japan's generally open ownership framework, but title, road rights, building records and non-resident reporting remain property-specific.",
        "regulatory_safety": "Kutchan and Niseko layer local planning, lodging and accommodation-tax rules above national minpaku and hotel frameworks.",
        "rental_profit": "Hirafu, Hanazono and Niseko resort units can earn winter peaks, but operator fees, heating, snow and shoulder seasons compress owner returns.",
        "capital_upside": "Niseko's international recognition supports selected assets, while construction cost, regulation, future supply and immature evidence prevent blanket forecasts.",
        "retirement_fit": "Kutchan provides Niseko's hospital and ordinary services; Hirafu, Annupuri and Moiwa add winter access, stairs and driving dependence.",
        "exit_liquidity": "Kutchan homes reach local buyers, while Niseko's premium condos and singular chalets depend on narrower international and operator-sensitive pools.",
        "foreigner_fit": "Niseko has bilingual agencies and operators, but Japanese reporting, tax, planning and contractor work still require independent local support.",
        "value_entry": "Kutchan, Hirafu and branded Niseko products span radically different prices; legal use, management and future buyer pool determine real value.",
    },
    market_anchors=(
        {"location": "Hirafu resort-home site", "evidence": "¥200,000/m²", "buyer_read": "MLIT appraisal for 529 m² of bare land on 1 January 2026, 6.5 km from Kutchan; not a chalet or condo valuation.", "source_label": "MLIT 2026 Hirafu appraisal", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/01/2026014000003.html"},
        {"location": "Central Kutchan residential site", "evidence": "¥67,000/m²", "buyer_read": "MLIT appraisal for 330 m² of bare land on 1 January 2026, about 850 m from Kutchan station; improvements are excluded.", "source_label": "MLIT 2026 central Kutchan appraisal", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/01/2026014000002.html"},
        {"location": "Northern Kutchan residential site", "evidence": "¥35,000/m²", "buyer_read": "MLIT appraisal for 201 m² of bare land on 1 January 2026, about 1.3 km from Kutchan station; one point, not a town-wide valuation.", "source_label": "MLIT 2026 northern Kutchan appraisal", "source_url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/01/2026014000001.html"},
    ),
    micro_locations_intro="Niseko is a chain of daily-life and operating patterns, not one resort average. These groups are orientation aids rather than valuation zones. Confirm the municipal boundary, planning, lawful use, shuttle, snow contract, hazard layers, healthcare journey and completed evidence for every address.",
    micro_locations=(
        {"name": "Kutchan town", "best_for": "Year-round services and value entry", "daily_life": "Working town with rail, hospital and shops", "diligence": "Building age, snow, road, neighbourhood and rental permission"},
        {"name": "Hirafu / Kabayama", "best_for": "International resort depth", "daily_life": "Visitor-led core grading into chalet areas", "diligence": "Operator, planning, walkability, snow, charges and exit premium"},
        {"name": "Hanazono", "best_for": "Planned premium resort use", "daily_life": "Polished and operator-dependent", "diligence": "Contract, owner use, future supply, transport and resale pool"},
        {"name": "Niseko Village / Annupuri / Moiwa", "best_for": "Southern mountain access and quiet", "daily_life": "Dispersed resort arc with more driving", "diligence": "Exact lift, road, shuttle, manager, seasonality and emergency access"},
    ),
    checklist=(
        "Confirm residence, healthcare, tax administration and ownership structure.",
        "Choose Kutchan, Hirafu / Kabayama, Hanazono or the southern resort arc first.",
        "Travel New Chitose, hospital, grocery and resort routes in winter and shoulder season.",
        "Verify title, boundaries, road rights, utilities, planning and legal building records.",
        "Inspect snow load, roof shedding, heating, freeze protection, drainage and hazard layers.",
        "Clear minpaku or lodging permission, accommodation tax and municipal duties in writing.",
        "Audit operator contracts, owner use, charges, JCT treatment and complete rental statements.",
        "Model five-year cash outlay and identify the future resale buyer before signing.",
    ),
    references_intro="Legal, tax, planning, lodging, transport, healthcare, hazard, market and listing claims were reviewed on 22 August 2026. Recheck every time-sensitive source no later than 22 February 2027 and immediately after any tax, planning, listing, transport, hazard, operator, market data or building change. Obtain current Japanese legal, immigration, tax, planning, building, insurance and management advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "Japan retirement property guide", "url": "/japan-retirement-property-foreign-buyers/"},
        {"label": "Ministry of Finance: non-resident real-property reporting", "url": "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html"},
        {"label": "National Tax Agency: non-residents and Japanese real estate", "url": "https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf"},
        {"label": "Japan Tourism Agency: Private Lodging Business Act", "url": "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html"},
        {"label": "Kutchan Town: current private-lodging restrictions", "url": "https://www.town.kutchan.hokkaido.jp/news/tourism/2792/"},
        {"label": "Kutchan Town: 2026 landscape and development controls", "url": "https://www.town.kutchan.hokkaido.jp/town_administration/toshikeikaku/4900/"},
        {"label": "Kutchan Town: 2026 accommodation-tax guide", "url": "https://www.town.kutchan.hokkaido.jp/file/contents/3494/38162/2026tebiki_eigo.pdf"},
        {"label": "Niseko Town: accommodation-tax guidance", "url": "https://www.town.niseko.lg.jp/kurashi/tax/syukuhakuzei/zigyousyamuke_syukuhakuzei"},
        {"label": "Niseko Town: fixed-asset tax", "url": "https://www.town.niseko.lg.jp/kurashi/tax/koteishisan/?wovn=en"},
        {"label": "Niseko official access guide", "url": "https://niseko.co.jp/access/?hl=en"},
        {"label": "Kutchan tourism master plan", "url": "https://niseko.co.jp/wp/wp-content/uploads/2025/12/2020-2031_Kutchan-Town-Tourism-Master-Plan-Revised-Edition-Main.pdf"},
        {"label": "Kutchan Kosei Hospital: official English information", "url": "https://www.dou-kouseiren.com/byouin/kutchan/english/"},
        {"label": "Kutchan Town: current hazard map", "url": "https://www.town.kutchan.hokkaido.jp/news/living_infomation/3467/"},
        {"label": "MLIT: 2026 Hirafu bare-land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/01/2026014000003.html"},
        {"label": "MLIT: 2026 central Kutchan bare-land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/01/2026014000002.html"},
        {"label": "MLIT: 2026 northern Kutchan bare-land appraisal", "url": "https://www.reinfolib.mlit.go.jp/landPrices_/realEstateAppraisalReport/2026/01/2026014000001.html"},
        {"label": "Niseko Real Estate: Kutchan renovated house asking observation", "url": "https://nisekorealestate.com/properties/kutchan-newly-renovated-3br-yotei-view-house"},
        {"label": "Niseko Real Estate: Kizuna 202 asking observation", "url": "https://nisekorealestate.com/properties/kizuna-202"},
        {"label": "Niseko Real Estate: MUWA Niseko 501 asking observation", "url": "https://nisekorealestate.com/properties/muwa-niseko-501"},
    ),
    images=(
        DossierImage("working-town", "/assets/niseko-kutchan-working-town.webp", "Kutchan working town beneath Mount Yotei in a calm winter morning", "Kutchan supplies the working-town services behind the resort story.", "hero"),
        DossierImage("winter-snow-operations", "/assets/niseko-winter-snow-operations.webp", "Residents clearing deep snow around a modest Niseko-area home", "Snow access, heating and maintenance are ordinary ownership costs.", "wide"),
        DossierImage("green-season-mobility", "/assets/niseko-green-season-mobility.webp", "Mature residents carrying groceries near a rural Niseko bus stop in green season", "Shoulder-season mobility reveals whether the address works beyond winter.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Niseko through five destination lenses",
    assessment_intro="Here’s how Niseko scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current observations show the spread from a renovated Kutchan house through an Upper Hirafu condo to a branded ski-in/out residence. They are asking evidence—not valuations. Local JPY is primary; USD uses the recorded dataset exchange basis.",
    market_anchors_intro="These are official bare-land appraisals—not finished-home prices or valuations. They show the resort-to-town gradient and must be reconciled for building, legal use, age, condition, management and exact location.",
    orientation_groups=(
        DossierOrientationGroup("Working town to core resort", (("Kutchan station", "Rail and working-town services"), ("Hirafu / Kabayama", "International resort core"), ("Hanazono", "Planned premium resort"))),
        DossierOrientationGroup("Southern resort arc", (("Hirafu", "Northern reference point"), ("Niseko Village", "Managed resort base"), ("Annupuri", "Quieter mountain access"), ("Moiwa", "Smaller western resort area"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current airport, rail, bus and shuttle timetables, road clearing and the exact winter route.",
    country_guide_url="/countries/japan-property/",
    country_guide_label="Japan property guide",
    rail_comparison="Compare Niseko with the full Atlas.",
)


MALLORCA_DOSSIER = PremiumDossierSpec(
    destination_id="mallorca",
    title="Mallorca Retirement Property Dossier",
    description="Assess Mallorca property through year-round life, island access, Spanish ownership, Balearic tourist rules, healthcare, water, hazards, value, resale, and current listings.",
    h1="Mallorca: buy the year-round address, not the holiday promise",
    lede="Mallorca is not one retirement market. Palma offers hospitals, markets, culture and public transport within a working city. Santa Catalina, Portixol and Son Armadans deliver different urban lives. Calvià, Santa Ponça and Port d'Andratx form a mature southwest buyer market. Sóller and the Tramuntana trade convenience for landscape. Pollença and Alcúdia provide northern bases, while Santanyí and Manacor anchor different eastern routines. This dossier asks which address remains practical after summer flights thin, restaurants close and a house needs ordinary care.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "Mallorca is a strong lifestyle and retirement contender for a buyer who can establish Spanish residence independently, accept island logistics and purchase without depending on tourist rent. Ownership does not create a residence right or healthcare eligibility. Spain ended new property-linked investor residence applications on 3 April 2025. A non-EU buyer considering the non-lucrative route must meet the current resource, insurance and other requirements, while EU, EEA and Swiss households follow different rules. Confirm the route, tax residence and healthcare position for every household member before a reservation contract makes the property decision emotionally or financially difficult to reverse.",
        "The broadest year-round case is Palma, where ordinary employment, healthcare, shops and transport support the visitor economy rather than disappear with it. The southwest can work for a higher-budget buyer who values an international service ecosystem and accepts a price already reflecting that recognition. Sóller, Deià and Valldemossa reward a household comfortable with gradients, narrower roads, older buildings and a more selective resale pool. Pollença and Alcúdia offer northern town life with seasonal pressure; Santanyí gives polished village and coastal demand, while Manacor has a deeper resident economy and a different price logic. The right choice begins with daily routine, not the most photogenic listing.",
        "Proceed in this order: establish residence, healthcare and tax administration; choose a year-round operating pattern; travel the airport, hospital, grocery and maintenance routes in August and winter; then reconcile registry, cadastre, planning, lawful built area, community rules, water and hazards. Assume no new tourist licence and no transferable income stream unless the Consell, Balearic authorities, municipality, community and independent counsel confirm the exact property and owner position in writing. Mallorca works best as a home whose personal value justifies its carrying cost. Any rental or appreciation case should remain a separately verified upside scenario.",
    ),
    lenses_intro="The five paired lenses below turn Mallorca's island appeal into ten buyer decisions. Each tests a specific address and operating plan; the score table then presents the complete Atlas assessment once.",
    lenses=(
        DossierLens(
            "Live as a resident after peak season",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Palma provides Mallorca's clearest all-season base. Santa Catalina combines a market, restaurants and a central walkable position, but nightlife, older buildings and visitor pressure vary street by street. Portixol and El Molinar place the waterfront inside an ordinary city routine, with a premium for that convenience. Son Armadans is quieter and established, though gradients and the exact walk to services matter. The test is not whether the neighbourhood feels lively on a spring weekend. Shop for groceries, reach a pharmacy, use public transport and return after dark in the least convenient season before deciding that a car-free life is realistic.",
                "Outside Palma, every gain has an operating cost. Calvià, Santa Ponça and Bendinat offer managed communities, international services and access to the southwest coast; Port d'Andratx is more exclusive and topographically constrained. Sóller has a real town centre, shops and rail identity, while Deià and Valldemossa are smaller, steeper and more visitor-led. Pollença is an established inland town and Alcúdia adds a historic centre plus coastal settlements. Santanyí has strong village appeal and nearby coves; Manacor is less polished but more rooted in an ordinary regional economy. Visit when shutters are down, rain falls and tradespeople must reach the home.",
                "Healthcare reinforces the geography. IB-SALUT's public network includes Son Espases and Son Llàtzer around Palma, with hospitals in Inca and Manacor, primary-care centres and the 061 emergency service. That network does not mean every address has the same journey or that ownership creates eligibility. Measure the route to routine and emergency care, identify a nearby pharmacy and ask how language support will work. A Tramuntana house, a north-coast apartment and a Santanyí villa can each be compelling, but retirement fit declines if one partner cannot drive, stairs become difficult or winter services no longer cover everyday needs.",
            ),
            "inland-water-daily-life",
        ),
        DossierLens(
            "Fly easily, then account for island dependence",
            ("global_access", "foreigner_fit"),
            (
                "Palma de Mallorca Airport is a major advantage. Aena currently lists 195 destinations operated by 76 companies, and the airport handled 33.8 million passengers in 2025. Those figures demonstrate reach, not year-round frequency. Many routes are seasonal, schedules change and peak volumes create queues and road pressure. Calculate the complete journey from the preferred address with luggage: Palma can be straightforward, the southwest adds road time, Sóller crosses or tunnels through the mountains, and Pollença, Alcúdia, Santanyí or Manacor extend the last mile. Check winter timetables for the connections the household will actually use.",
                "Island dependence becomes visible when a flight is cancelled, a specialist appointment is on the mainland or a large repair needs a particular contractor. Ferries provide another route and are useful for vehicles and freight, but port, sailing time and onward travel must be included. Imported materials, furniture and specialist labour may carry longer lead times. For a rural or coastal home, ask how quickly a plumber, electrician, pool technician or property manager can attend in August and after a storm. Global access scores well because Mallorca is connected; operating resilience depends on planning for the occasions when that connection is slow or disrupted.",
                "Mallorca is accustomed to international owners, and Palma plus the southwest have multilingual agencies, advisers and service providers. That lowers friction without changing the legal language or the need for independent representation. Tax notices, registry records, community meetings, municipal files, utility contracts and rural planning evidence may require Spanish or Catalan follow-through. A buyer based abroad needs a named person to receive notices, inspect after severe weather and authorize repairs. Foreigner fit is strongest for someone who can build a local professional network and participate in the resident economy, not someone expecting an English-speaking resort layer to handle every obligation indefinitely.",
            ),
        ),
        DossierLens(
            "Own clearly, then audit what exists on the land",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Spain generally permits foreign ownership of ordinary residential property, using the notary and Land Registry within an established transaction system. That is only the start of Mallorca diligence. Compare the nota simple, cadastral record, deed, planning file, occupancy evidence and what physically exists. Confirm boundaries, easements, access, utility contracts and any debt or charge. For an apartment, read community statutes, recent minutes, budgets, arrears, planned works, insurance and restrictions on use. A clean registry entry does not prove that every terrace enclosure, pool, guest house or converted storage area was authorised and can be insured or resold as marketed.",
                "Rural fincas deserve a separate legal and technical audit. Ask an independent architect to measure lawful area and trace permissions for extensions, pools, wells, septic systems, retaining walls and outbuildings. Protected land, agricultural classifications and older enforcement histories can limit renovation or regularisation. In Tramuntana properties, investigate slope, road width, retaining structures, drainage and emergency access. Around Santanyí, Manacor, Pollença and other rural zones, water source and wastewater arrangements matter as much as the view. Do not accept 'old enough to be legal' or a cadastral appearance as a professional conclusion. Put every unresolved discrepancy into the contract or walk away.",
                "Hazard review must combine maps with the site. Mallorca faces heat, wildfire, flash flooding, coastal exposure and locally difficult terrain. Balearic drought status is published by demand unit and can change monthly; an island-level colour does not establish a property's lawful well, mains pressure or summer capacity. Check flood layers, drainage paths, vegetation management, defensible access, coastal restrictions, insurance terms and any municipal water measures. Visit after heavy rain where possible and ask for prior claims. Regulatory safety is not produced by one certificate. It comes from reconciling the legal file, physical building, current planning position and an insurer willing to cover the intended use.",
            ),
            "tramuntana-access",
        ),
        DossierLens(
            "Assume no new tourist licence",
            ("rental_profit", "capital_upside"),
            (
                "Mallorca's visitor demand is obvious; the right to monetize it is not. The Balearic 2025 tourism-containment framework bars new tourist places in multi-family buildings and constrains growth through limited one-for-one exchange mechanisms. Island plans, suspensions, quotas and later resolutions shape what can operate. Start every acquisition model with zero tourist rent. If a seller markets an existing licence, obtain its number and full file, then confirm the property, owner, category, capacity, expiry or renewal position, community rules and whether any transfer or continued operation is lawful. A licence claim in an advertisement is evidence to investigate, not an asset to price.",
                "A lawful holiday operation still has a business cost. Model management, guest communication, cleaning, linen, utilities, pool and garden care, insurance, tax, platform fees, repairs and empty periods. Compare the net result with a long-term tenancy and with personal use only. Palma residential demand differs from the southwest resort market; a Sóller townhouse, Pollença home or Santanyí villa has a distinct season and operator pool. Community restrictions or municipal enforcement can eliminate the theoretical case. Ask for filed revenue and expense statements, tax returns and booking records, then have an independent adviser reconcile them rather than relying on the agent's gross-yield percentage.",
                "Capital upside should be treated with the same restraint. Palma's working-city demand and the southwest's international recognition support selected assets, while island planning limits can constrain supply. Those advantages are widely known and reflected in entry prices. Rural scarcity is valuable only if access, lawful area, water and maintenance remain acceptable to a future buyer. Tourism controls can protect residential amenity while reducing an investor's income options. Model flat real prices, higher operating costs and a longer sale before paying for a growth story. The best appreciation defence is a useful, compliant home that another year-round buyer can understand without inheriting unresolved legal or operating risk.",
            ),
        ),
        DossierLens(
            "Enter a mature market and preserve the exit",
            ("value_entry", "exit_liquidity"),
            (
                "Official 2025 completed-registration evidence supplies three bounded anchors: €3,988/m² across all Illes Balears homes, €4,086/m² for Palma homes and €4,244/m² for detached homes across the islands. They are not Mallorca-wide asking averages or valuations for a candidate. They combine locations, conditions and legal qualities that cannot be transferred to one apartment, townhouse or finca. The current listing observations below deliberately span a Platja de Palma apartment, a Sóller townhouse and a Santanyí coastal villa. Their asking prices show product dispersion; they do not establish completed value or confirm that the marketed area and rights are legally saleable.",
                "Value entry is created by matching price to daily utility and the next buyer pool. In Palma, a well-governed apartment near services can reach resident, national and international demand, but tourist streets, noise and building work require discounts. Santa Ponça, Bendinat and Port d'Andratx already carry an international premium; pay it only for documented quality and durable access. Sóller and the Tramuntana reward singular character but can narrow the pool through stairs, parking and renovation. Pollença and Alcúdia have established recognition; Santanyí's polish differs from Manacor's resident base. A sea view never cures unlawful area, poor water or an impossible road.",
                "Exit liquidity is widest where the home remains understandable in ordinary life. Palma usually offers the deepest pool. Established southwest apartments and villas can reach international buyers, but higher ticket sizes slow matching. A practical town home in Sóller, Pollença or Manacor can attract more buyers than an isolated rural estate, even if the estate receives more online attention. Model five-year cash outlay including taxes, financing, community charges, management, water systems, pool and garden care, insurance, repairs and sale costs. Before signing, ask two agents who did not source the property how they would resell it, to whom, using which completed evidence and over what likely period.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Mallorca joins Palma's working-city life with Calvià coast, Sóller landscape and distinct northern and southeast town routines.",
        "global_access": "Mallorca's Palma airport has exceptional breadth, but seasonal flights and longer last miles weaken access outside the capital and southwest.",
        "ownership_clarity": "Mallorca follows Spain's established registry and notary system; lawful area, rural additions, easements and community files remain property-specific.",
        "regulatory_safety": "Mallorca tourist controls, planning, water and hazard rules require written checks with Balearic, island and municipal authorities.",
        "rental_profit": "Mallorca has deep visitor demand, but constrained tourist places, operator costs and seasonality make zero holiday rent the prudent base case.",
        "capital_upside": "Palma and established Mallorca submarkets have mature demand; high entry prices and property-level legality limit blanket appreciation claims.",
        "retirement_fit": "Palma has Mallorca's broadest hospitals, transit and services; Tramuntana and remote coastal homes add driving and emergency-access dependence.",
        "exit_liquidity": "Palma reaches the broadest buyer pool, while singular Sóller, Santanyí and Port d'Andratx homes depend on narrower budgets and tastes.",
        "foreigner_fit": "Mallorca has multilingual services and international owners, but Spanish and Catalan tax, planning and community administration still need local support.",
        "value_entry": "Palma, Calvià, Sóller, Pollença and Manacor occupy different price bands; utility, lawful area and resale depth determine real value.",
    },
    market_anchors=(
        {"location": "Illes Balears all homes", "evidence": "€3,988/m²", "buyer_read": "Average for 2025 completed registrations across all islands and property types; not a Mallorca or property valuation.", "source_label": "Registradores 2025 annual report", "source_url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf/f15ee835-3246-6132-11d0-6495dfeee415?t=1774598855046"},
        {"location": "Palma all homes", "evidence": "€4,086/m²", "buyer_read": "Average for 2025 completed registrations in Palma; district, condition, legal area and outlook still require matched evidence.", "source_label": "Registradores 2025 annual report", "source_url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf/f15ee835-3246-6132-11d0-6495dfeee415?t=1774598855046"},
        {"location": "Illes Balears detached homes", "evidence": "€4,244/m²", "buyer_read": "Average for 2025 completed detached-home registrations across the islands; it does not reconcile land, legality or condition.", "source_label": "Registradores 2025 annual report", "source_url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf/f15ee835-3246-6132-11d0-6495dfeee415?t=1774598855046"},
    ),
    micro_locations_intro="Mallorca is best read as four operating patterns rather than a single island average. These are orientation aids, not valuation zones. Confirm the municipality, parcel, planning, water, hazard, transport, community and lawful-use position for every address.",
    micro_locations=(
        {"name": "Palma", "best_for": "Year-round city services", "daily_life": "Walkable districts, hospitals, culture and airport access", "diligence": "Street noise, building governance, legal area and tourist pressure"},
        {"name": "Calvià / Santa Ponça / Port d'Andratx", "best_for": "International southwest ecosystem", "daily_life": "Polished coastal services with car-led pockets", "diligence": "Entry premium, community, slope, operator and exit depth"},
        {"name": "Sóller / Tramuntana", "best_for": "Landscape and town character", "daily_life": "Mountain setting with variable access and services", "diligence": "Road, stairs, retaining walls, water, planning and wildfire"},
        {"name": "Pollença / Alcúdia / Santanyí / Manacor", "best_for": "Northern and eastern alternatives", "daily_life": "Town-led bases with distinct coastal catchments", "diligence": "Seasonality, exact hospital route, rural legality and water"},
    ),
    checklist=(
        "Confirm residence, healthcare, tax residence and representation before purchase.",
        "Choose Palma, southwest, Tramuntana/west or north/east daily life first.",
        "Travel the airport, hospital, grocery and property routes in summer and winter.",
        "Reconcile registry, cadastre, lawful area, planning, occupancy, easements and community files.",
        "Verify mains or well water, wastewater, pool, drainage and drought constraints.",
        "Overlay current flood, wildfire, heat, coastal and terrain hazards with insurance terms.",
        "Assume zero tourist rent until every property-level permission is confirmed in writing.",
        "Model five-year cash outlay and identify the future resale buyer before signing.",
    ),
    references_intro="Legal, tax, tourism, transport, healthcare, water, hazard, market and listing claims were reviewed on 22 August 2026. Recheck every time-sensitive source no later than 22 February 2027 and immediately after any residence, tax, planning, tourist-place, listing, transport, water, hazard, community or market-data change. Obtain current Spanish and Balearic legal, tax, immigration, planning, building, insurance and property-management advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "Spain retirement property guide", "url": "/spain-retirement-property-foreign-buyers/"},
        {"label": "Spanish Migration Ministry: non-lucrative residence", "url": "https://www.inclusion.gob.es/en/web/migraciones/w/autorizacion-inicial-de-residencia-temporal-no-lucrativa"},
        {"label": "Spanish Government: end of property-linked investor residence", "url": "https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/vivienda-agenda-urbana/Paginas/2025/020425-fin-golden-visa.aspx"},
        {"label": "Spanish Tax Agency: tax residence", "url": "https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/residencia-personas-fisicas-juridicas/persona-fisica-residente-espana.html"},
        {"label": "Spanish Tax Agency: non-resident property taxation", "url": "https://sede.agenciatributaria.gob.es/Sede/vivienda-otros-inmuebles/no-residentes-tributacion-inmuebles.html"},
        {"label": "Spanish Property Registrars: buyer guidance", "url": "https://www.registradores.org/gl/documentacion-y-descargas/guias-rapidas"},
        {"label": "Registradores: 2025 completed-market evidence", "url": "https://www.registradores.org/documents/33383/148210/ERI%2BAnuario%2B2025.pdf/f15ee835-3246-6132-11d0-6495dfeee415?t=1774598855046"},
        {"label": "Balearic Government: tourism containment framework", "url": "https://www.caib.es/sites/contencioturistica/ca/contingut"},
        {"label": "Balearic Official Gazette: Decree-Law 4/2025", "url": "https://caib.es/eboibfront/eli/es-ib/dl/2025/04/11/4/dof/cat/pdf"},
        {"label": "Balearic Official Gazette: 2026 tourist-place resolution", "url": "https://www.caib.es/eboibfront/pdf/ca/2026/35/1215163"},
        {"label": "Aena: Palma airport destinations", "url": "https://www.aena.es/en/palma-de-mallorca/airlines-and-destinations/airport-destinations.html"},
        {"label": "Aena: Palma airport 2025 traffic", "url": "https://www.aena.es/es/prensa/el-aeropuerto-de-palma-de-mallorca-cierra-2025-con-338-millones-de---pasajeros.html"},
        {"label": "IB-SALUT: Balearic public healthcare network", "url": "https://www.ibsalut.es/"},
        {"label": "IB-SALUT: Son Espases hospital", "url": "https://www.ibsalut.es/es/servicio-de-salud/recursos-y-centros-sanitarios/centros-sanitarios/hospitales/hospital-universitari-son-espases"},
        {"label": "Balearic Government: current drought indicators", "url": "https://www.caib.es/sites/aigua/es/index_de_sequera/"},
        {"label": "Balearic Water Portal: official flood hazard and risk maps", "url": "https://www.caib.es/sites/aigua/ca/planos_inundacia/?tipo=alfa"},
        {"label": "Balearic spatial service: official forest-fire risk map", "url": "https://ideib.caib.es/geoserveis/rest/services/public/GOIB_RiscIncendi_IB/MapServer"},
        {"label": "Engel & Völkers: Platja de Palma asking observation", "url": "https://www.engelvoelkers.com/es/en/exposes/07d4ba7b-eafd-5b31-966e-5996db67c3c0"},
        {"label": "Engel & Völkers: Sóller asking observation", "url": "https://www.engelvoelkers.com/es/en/exposes/b6504ee0-9fc7-5b26-801c-ae124e2a138e"},
        {"label": "Mayer & Dau: Santanyí asking observation", "url": "https://mayer-dau.es/en/real-estate/detail/?estate=20089&objektnr=9230"},
        {"label": "European Central Bank: euro reference rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("palma-year-round-life", "/assets/mallorca-palma-year-round-life.webp", "Mature residents walking through a shaded Palma neighbourhood near a market", "Palma's case rests on ordinary year-round city life, not only the waterfront.", "hero"),
        DossierImage("tramuntana-access", "/assets/mallorca-tramuntana-access.webp", "Older residents walking on a steep stone street in Sóller beneath the Tramuntana", "Tramuntana character comes with gradients, access and maintenance decisions.", "wide"),
        DossierImage("inland-water-daily-life", "/assets/mallorca-inland-water-daily-life.webp", "Residents carrying groceries along a shaded inland Mallorca street in summer", "Heat, water and ordinary errands reveal whether an inland address works year-round.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Mallorca through five destination lenses",
    assessment_intro="Here’s how Mallorca scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current observations show the spread from a Platja de Palma apartment through a Sóller townhouse to a Santanyí coastal villa. They are asking evidence—not valuations. Local EUR is primary; USD uses the recorded dataset exchange basis.",
    market_anchors_intro="These 2025 registered, completed-market averages are broad anchors—not asking prices or property valuations. Reconcile each candidate for municipality, property type, lawful area, condition, land, outlook and rights.",
    orientation_groups=(
        DossierOrientationGroup("Palma to the southwest", (("Palma", "Year-round city and hospital base"), ("Calvià / Santa Ponça", "Established southwest coast"), ("Port d'Andratx", "Premium western endpoint"))),
        DossierOrientationGroup("Mountain, north and east", (("Sóller / Tramuntana", "Mountain access and character"), ("Pollença / Alcúdia", "Northern town and coast"), ("Manacor", "Eastern resident hub"), ("Santanyí", "Southeast village and coves"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current road, bus, ferry and flight timetables and the exact hospital, service and airport journey.",
    country_guide_url="/countries/spain-property/",
    country_guide_label="Spain property guide",
    rail_comparison="Compare Mallorca with the full Atlas.",
)


PREMIUM_DESTINATION_DOSSIERS = {
    FUKUOKA_ITOSHIMA_DOSSIER.destination_id: FUKUOKA_ITOSHIMA_DOSSIER,
    ALGARVE_CASCAIS_DOSSIER.destination_id: ALGARVE_CASCAIS_DOSSIER,
    MADEIRA_DOSSIER.destination_id: MADEIRA_DOSSIER,
    MALAGA_COSTA_DEL_SOL_DOSSIER.destination_id: MALAGA_COSTA_DEL_SOL_DOSSIER,
    LAKE_COMO_DOSSIER.destination_id: LAKE_COMO_DOSSIER,
    HAKONE_IZU_DOSSIER.destination_id: HAKONE_IZU_DOSSIER,
    VALENCIA_DOSSIER.destination_id: VALENCIA_DOSSIER,
    HAKUBA_DOSSIER.destination_id: HAKUBA_DOSSIER,
    COSTA_BRAVA_GIRONA_DOSSIER.destination_id: COSTA_BRAVA_GIRONA_DOSSIER,
    PARK_CITY_DEER_VALLEY_DOSSIER.destination_id: PARK_CITY_DEER_VALLEY_DOSSIER,
    CRETE_DOSSIER.destination_id: CRETE_DOSSIER,
    NISEKO_DOSSIER.destination_id: NISEKO_DOSSIER,
    ANNECY_DOSSIER.destination_id: ANNECY_DOSSIER,
    MALLORCA_DOSSIER.destination_id: MALLORCA_DOSSIER,
}


def get_premium_dossier(destination_id: str) -> PremiumDossierSpec | None:
    return PREMIUM_DESTINATION_DOSSIERS.get(destination_id)


def validate_premium_dossier(spec: PremiumDossierSpec) -> None:
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

    if len(spec.market_anchors) != 3:
        raise ValueError("premium dossier requires exactly three official market anchors")
    required_anchor_fields = {"location", "evidence", "buyer_read", "source_label", "source_url"}
    for anchor in spec.market_anchors:
        if required_anchor_fields - anchor.keys() or any(not anchor[field].strip() for field in required_anchor_fields):
            raise ValueError("premium dossier market anchors must be complete")

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
    if not 1 <= len(spec.orientation_groups) <= 2:
        raise ValueError("premium dossier requires one or two orientation groups")
    for group in spec.orientation_groups:
        if not group.label.strip() or len(group.stops) < 2:
            raise ValueError("each orientation group requires a label and at least two stops")
        if any(not name.strip() or not note.strip() for name, note in group.stops):
            raise ValueError("orientation stops must be complete")
    if not 6 <= len(spec.checklist) <= 8:
        raise ValueError("premium dossier checklist must contain six to eight items")
    if not spec.references:
        raise ValueError("premium dossier requires references")


validate_premium_dossier(FUKUOKA_ITOSHIMA_DOSSIER)
validate_premium_dossier(ALGARVE_CASCAIS_DOSSIER)
validate_premium_dossier(MADEIRA_DOSSIER)
validate_premium_dossier(LAKE_COMO_DOSSIER)
validate_premium_dossier(HAKONE_IZU_DOSSIER)
validate_premium_dossier(VALENCIA_DOSSIER)
validate_premium_dossier(HAKUBA_DOSSIER)
validate_premium_dossier(COSTA_BRAVA_GIRONA_DOSSIER)
validate_premium_dossier(PARK_CITY_DEER_VALLEY_DOSSIER)
validate_premium_dossier(CRETE_DOSSIER)
validate_premium_dossier(NISEKO_DOSSIER)
validate_premium_dossier(ANNECY_DOSSIER)
validate_premium_dossier(MALLORCA_DOSSIER)
