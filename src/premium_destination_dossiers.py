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
    role: str = ""


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
    property_anchor_indexes: tuple[int | None, ...] = ()


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
        "Five questions determine whether the city-and-coast proposition will remain useful in ordinary life: where daily services sit, how the last mile works, what the exact property permits, whether demand survives outside peak periods, and who is likely to buy on exit."
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
                "Fukuoka / Itoshima offers several entry points, but they serve different buyer pools. A rail-accessible apartment can provide lower-cost access to services but may carry weak reserves or a dated building. A newer house around Maebaru can offer practical space yet needs location and resale testing. A renovated or newly built coastal home can command a substantial lifestyle premium while reaching fewer year-round buyers. Compare the exact candidate with completed transactions in the Ministry of Land’s Real Estate Information Library and commission a property-specific assessment.",
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
        DossierImage("coast", "/assets/fukuoka-itoshima-coast.webp", "Fukuoka and Itoshima coastline", "City access meets the Itoshima coast.", "hero", "defining-place"),
        DossierImage("city-access", "/assets/fukuoka-itoshima-city-access.webp", "Everyday urban access in Fukuoka", "Fukuoka provides the practical urban base.", "wide", "built-environment-access"),
        DossierImage("seaside-life", "/assets/fukuoka-itoshima-seaside-life.webp", "Narrow coastal residential lane in Itoshima with roadside drainage and the sea beyond", "On the Itoshima coast, road width, drainage and salt exposure belong in the ownership decision.", "wide", "decision-texture"),
    ),
    nav_items=(
        ("verdict", "Verdict"),
        ("lenses", "Five destination lenses"),
        ("scores", "Atlas assessment"),
        ("listings", "What homes cost"),
        ("locations", "Where to look"),
        ("checklist", "Buyer checklist"),
        ("sources", "References"),
    ),
    lenses_heading="Fukuoka / Itoshima through five destination lenses",
    assessment_intro="Here’s how Fukuoka / Itoshima scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="The current examples run from about ¥31.8 million for a rail-accessible western-Fukuoka apartment to ¥180 million for a large coastal holiday house. Access to rail and ordinary services matters more to resale depth than proximity to the sea alone.",
    market_anchors_intro="Public land evidence confirms a steep city-to-coast gradient, but land and finished homes are not interchangeable. Building age, condition, legal area and access can outweigh the headline location.",
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
    property_anchor_indexes=(0, 1, 2),
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
    date_reviewed="2026-08-23",
    verdict_paragraphs=(
        "The verdict is selectively positive. Park City / Deer Valley suits an active eligible buyer who values a familiar title framework, Salt Lake City airport access, four-season recreation and a deeper resale market than most small ski towns. Utah restricted-entity eligibility still requires legal review. It works best when the home has a credible year-round use case, the buyer can absorb high carrying costs without optimistic rent, and the exact zoning and HOA permit the intended operation. Old Town is strongest for a walkable mountain-town life; Park Meadows and Prospector are more residential; Lower Deer Valley offers resort proximity; Canyons Village is operationally convenient but contract- and fee-heavy.",
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
                "Many individual foreign buyers can acquire ordinary Utah residential real estate, but Utah's Restrictions on Foreign Acquisitions of Land Act restricts defined restricted foreign entities. Buyer nationality, control, entity structure, the land and timing therefore require current Utah legal review. The closing still needs exact diligence: title commitment and exceptions, survey, access, easements, water and sewer status, permits, certificate history, property tax, disclosures, inspection and insurance. Condominiums and resort residences add declarations, bylaws, budgets, reserves, insurance allocation, litigation, rental-management terms and transfer fees. Old Town can bring preservation constraints; newer Canyons or East Village product can bring construction and completion risk. Freehold title is not a substitute for reading the governing package.",
                "Nightly rentals are a location-and-building privilege, not a general Park City right. Park City requires a licence for stays under 30 days where zoning allows, along with an inspection and state tax handling. Unincorporated Summit County separately licenses both the owner and the manager for rentals under 30 days. HOA, condominium hotel, resort and lender rules may be tighter. Confirm the municipal boundary first, then obtain written zoning and lawful-use confirmation alongside licence history, inspection, occupancy, parking, local-contact and tax duties. Never rely on a portal calendar or a listing's phrase ‘nightly rentals allowed.’",
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
        "ownership_clarity": "Many foreign individuals can acquire Park City homes, but Utah restricted foreign entities, title, HOA and cross-border tax require review.",
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
    references_intro="Legal, tax, licensing, market, transport, healthcare, hazard and listing claims were reviewed on 23 August 2026. Recheck every time-sensitive source no later than 23 February 2027 and immediately after any tax, zoning, HOA, licensing, transport, hazard, insurance, market data or listing change. Obtain current U.S. and Utah legal, immigration, tax, estate, title, building and insurance advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "United States property guide", "url": "/countries/united-states-property/"},
        {"label": "U.S. Department of State: visitor visa", "url": "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html"},
        {"label": "IRS: FIRPTA withholding", "url": "https://www.irs.gov/individuals/international-taxpayers/firpta-withholding"},
        {"label": "IRS: nonresident rental income from U.S. real property", "url": "https://www.irs.gov/individuals/international-taxpayers/nonresident-aliens-real-property-located-in-the-us"},
        {"label": "IRS: nonresident estates with U.S. assets", "url": "https://www.irs.gov/individuals/international-taxpayers/some-nonresidents-with-us-assets-must-file-estate-tax-returns"},
        {"label": "Utah Legislature: Restrictions on Foreign Acquisitions of Land Act", "url": "https://le.utah.gov/xcode/Title63L/Chapter13/63L-13.html"},
        {"label": "Park City: nightly-rental licence and inspection", "url": "https://www.parkcity.org/departments/finance-accounting/apply-for-a-business-licenses/nightly-rental-license"},
        {"label": "Park City: current planning resources", "url": "https://www.parkcity.gov/services/planning/index.php"},
        {"label": "Summit County: owner and manager nightly-rental licensing", "url": "https://summitcountyutah.gov/274/Business-Licensing"},
        {"label": "Park City: Wildland Urban Interface code", "url": "https://www.parkcity.org/departments/building-department/wildland-urban-interface-code"},
        {"label": "Park City: building, snow, soil and permit resources", "url": "https://parkcity.org/departments/building-department/forms-and-other-information"},
        {"label": "Park City: community code compliance", "url": "https://www.parkcity.gov/services/building/community_code_compliance/index.php"},
        {"label": "Park City Transit: current fare-free local service", "url": "https://www.parkcity.gov/services/transit/about/index.php"},
        {"label": "Park City Transit: 2026 routes and Park City–Salt Lake City commuter service", "url": "https://www.parkcity.gov/services/transit/routes_schedules/index.php"},
        {"label": "Salt Lake City International Airport: ground transportation", "url": "https://slcairport.com/parking-and-transportation/ground-transportation/"},
        {"label": "Park City Hospital: emergency and trauma care", "url": "https://prod.intermountainhealth.org/locations/park-city-hospital/emergency"},
        {"label": "Park City Hospital: current medical services", "url": "https://prod.intermountainhealth.org/locations/park-city-hospital/medical-services"},
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
            "winter-access-healthcare",
        ),
        DossierLens(
            "Reach Geneva—and the hospital—without assuming an easy commute",
            ("global_access", "foreigner_fit"),
            (
                "Annecy's connectivity is real but must be described door to door. The multimodal station anchors regional trains and buses; Grand Annecy's mobility guidance places Pringy about one hour twenty-five minutes from Geneva by rail and Annecy about two hours ten minutes from Lyon in its service examples. An official bus route also connects toward Geneva Airport. Those links are useful for periodic international travel. They are not a guarantee of a frictionless daily Geneva commute once the walk, transfer, border conditions, strike risk, late return and final journey to a lake-shore home are included.",
                "Local mobility is equally address-sensitive. Grand Annecy publishes regular lake-shore bus services, with many corridors operating from early morning into the evening, while summer additions are a separate seasonal offer. Do not use July frequency to justify a February purchase. Annecy centre and parts of Annecy-le-Vieux can work without a car for many trips. Sevrier and Saint-Jorioz may combine bus, bicycle and driving. The east shore can be more dependent on the road, particularly from a hillside house. Travel the exact route at the time it will normally be used and add a failed-connection scenario.",
                "Foreigner fit is helped by Geneva's international economy and by the area's experience with cross-border residents, but administration remains French and often technical. The notaire, bank, copropriété manager, insurer, tax office, utility providers and contractors may require French documents and local follow-through. Cross-border work introduces separate residence, tax, healthcare and social-security questions that a property guide cannot settle. Budget for independent French legal and tax advice, and for a bilingual contact if the household cannot handle notices and building meetings. International access is an asset; it does not remove the need to operate locally.",
            ),
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


CROATIA_ISTRIA_DALMATIA_DOSSIER = PremiumDossierSpec(
    destination_id="croatia-istria-dalmatia",
    title="Croatia Istria and Dalmatia Retirement Property Dossier",
    description="Assess retirement property in Istria and Dalmatia through residence, foreign ownership, title, tourist rules, healthcare, access, hazards, value, resale, and current listings.",
    h1="Croatia: choose the operating base before the Adriatic view",
    lede="Croatia's coast is not one retirement market. Split is a working regional city with hospitals, an airport and year-round services. Trogir and Kaštela keep the mainland close while changing building and traffic constraints. Rovinj, Pula and Poreč create distinct Istrian routines. Hvar and Brač add island character—and ferry dependence. The useful question is not whether the Adriatic is beautiful. It is which address remains practical in January, during an August heat wave and when a title, repair or medical journey needs attention.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "Croatia can be a strong retirement-home choice for a buyer who establishes residence independently, matches the property to an all-season service base and accepts more document reconciliation than the scenery suggests. A deed does not create a right to remain in Croatia or automatic healthcare cover. EEA citizens follow the registration framework for stays beyond three months; third-country nationals need a qualifying temporary-stay basis. The digital-nomad route is for eligible remote workers, not a general retirement visa. Long-term residence for a third-country national normally follows five years of qualifying legal stay. Confirm the route, absences, household eligibility, tax residence and HZZO position before a deposit turns a lifestyle decision into an immigration problem.",
        "Ownership rules also depend on nationality and asset type. EU, Icelandic, Liechtenstein and Norwegian buyers generally acquire ordinary real estate on Croatian terms, subject to exempted categories. Swiss buyers have their own registration condition. Other foreign nationals normally require reciprocity and ministerial consent for the specific property. Agricultural land, protected areas and corporate structures need separate analysis. Even when a buyer may acquire, the transaction is only as clear as the land-registry entry, cadastral parcel, lawful construction, use permit, access, utilities, co-ownership and physical building. Historic stone houses, divided apartments and rural plots make that reconciliation especially important.",
        "Proceed in this order: confirm residence, healthcare, ownership eligibility and tax administration; choose the year-round operating pattern; then audit title, cadastre, planning, permits, energy certificate, community governance, hazards and insurance. Start the income model with zero tourist rent. A categorisation decision, tax registration, eVisitor operation and—inside a multi-unit building—the required co-owner and adjoining-neighbour consents are property and operator questions, not transferable marketing labels. Croatia works best when personal utility supports the carrying cost. Treat seasonal rent and appreciation as separately verified scenarios rather than the reason an address is affordable.",
    ),
    lenses_intro="The five paired lenses below turn Croatia's long coastline into ten buyer decisions. Each tests a particular base and operating plan; the score table then presents the complete Atlas assessment once.",
    lenses=(
        DossierLens(
            "Live in a town that still works in winter",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Split offers the coast's strongest combination of ordinary city life and Adriatic access. Hospitals, specialists, markets, schools, ferries and municipal services serve residents rather than only visitors. The historic centre is magnetic, but stairs, stone surfaces, noise, summer crowding and restricted vehicle access can undermine an older household's routine. Residential districts outside the palace may be less cinematic and more useful. Test the walk to groceries and a pharmacy, the route to KBC Split, parking, lift access and winter social life. A split apartment marketed as two tourist units should also be judged as a future home: layout, legal subdivision, sound insulation and community relations matter after the rental story is removed.",
                "Istria offers a different pattern. Pula has the peninsula's deepest hospital, administrative and transport base. Rovinj carries exceptional character and an international premium; its old town also brings stairs, parking and service-access constraints. Poreč has a broad visitor economy and year-round residents, while inland towns trade the waterfront for space, quieter streets and road dependence. Rovinjsko Selo can be close to Rovinj without being walkable to its daily services. Visit in January and August. Check which shops remain open, how heating performs in damp or windy weather, whether a car is essential and how quickly a doctor, pharmacy, technician or carer can reach the address.",
                "Trogir and Kaštela can preserve mainland access while offering smaller-scale coastal life. Trogir's protected historic fabric and bridge traffic change parking, deliveries and renovation. Kaštela stretches along multiple settlements, so an attractive seafront description can conceal a weak walking route or road exposure. Hvar and Brač deepen the lifestyle appeal but add ferry timetables, weather disruption and smaller local service pools. An island home can work for an active household with redundancy, storage and local help; it is weaker for someone who needs frequent specialist care or same-day contractor access. Retirement fit therefore follows the least convenient recurring journey, not the best summer evening.",
            ),
        ),
        DossierLens(
            "Count the full journey, including the ferry",
            ("global_access", "foreigner_fit"),
            (
                "Split Airport handled 3,881,186 passengers in 2025, but the monthly pattern matters more than the annual headline: July handled 786,945 passengers and January 35,479. That gap captures the destination's access strength and seasonality. Split is about 20 kilometres from the airport and Trogir about 6 kilometres, while congestion can widen door-to-door times. Winter schedules are much thinner than summer schedules. Before buying, test the actual routes the household will use—not only whether an airline serves Split in July. Pula and Dubrovnik airports support other coastal zones, but route breadth, frequency and onward transport vary by season and should be rechecked each year.",
                "Island access needs its own operating budget. Jadrolinija publishes route-specific 2026 sailing schedules, but a timetable does not eliminate weather, queues, vehicle reservations, port parking or the onward trip. Hvar town, Stari Grad, Supetar and other ports serve different property catchments. The same island can produce a simple summer foot-passenger arrival and a demanding winter medical or repair journey. Price the airport-to-port transfer, ferry, luggage, car and final road. Ask what happens when the last sailing is missed, a vehicle ferry is full or strong wind interrupts service. Keep several days of essentials and identify who can open the house when the owner is abroad.",
                "Croatia's international familiarity reduces some friction, especially in Rovinj, Poreč, Split, Trogir and Hvar. It does not change the official language of contracts, land records, tax notices, planning files or community decisions. A buyer abroad needs an OIB where required for Croatian administration, independent Croatian legal and tax advice, and a reliable person to receive notices and inspect after storms or water failures. For third-country ownership, reciprocity and ministerial consent can make the process longer and property-specific. Foreigner fit is strongest for a household willing to build a local professional network and participate in ordinary Croatian systems, not one expecting an English-language resort layer to carry every obligation.",
            ),
        ),
        DossierLens(
            "Reconcile the registry, cadastre and building",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Croatia's land registry and cadastre are available through the official Uređena zemlja system, but matching records remain a buyer task. The land-registry extract establishes registered rights and charges; the cadastral plan describes the parcel and physical record. Compare both with the sale contract, official construction act, use permit, energy certificate and what an independent surveyor measures on site. Confirm seller authority, co-ownership, mortgages, litigation, easements, access and utilities. Registration—not merely signing—acquires title. In an apartment, verify the condominium unit, storage, parking, terraces, reserve fund, manager, arrears and recent decisions. In a stone house, trace every floor, annex and change of use.",
                "Planning review belongs beside title review. The state ISPU system publishes spatial plans and building information, but a map screenshot is not a legal opinion on a parcel. Coastal setbacks, protected historic fabric, agricultural classification, Natura or other protected status, road access and municipal plans can limit renovation or new work. Pools, terraces, auxiliary buildings, converted attics and divided tourist units may not align across title, cadastre and permits. Ask an independent architect or engineer for a written lawful-area schedule. A seller's claim that an older addition is tolerated, visible in cadastre or capable of later legalisation is not a substitute for a current permit and enforcement analysis.",
                "Hazard diligence must combine official maps, site inspection and insurance. Croatian Waters maps river, groundwater, dam and high-sea flooding under three probability scenarios. Coastal and karst addresses also need drainage, retaining-wall and flash-runoff review. The fire service's 2026 programme directs extra resources toward higher-risk coastal and island areas, while DHMZ issues heat and wind warnings that can affect vulnerable residents, ferries and small craft. Check vegetation, defendable access, hydrants, evacuation routes, wind exposure, roof and shutters, prior claims, water storage and firefighting access. Being outside a mapped flood outline does not prove the property will drain or insure well.",
            ),
            "istria-access-diligence",
        ),
        DossierLens(
            "Treat tourist rent as a regulated business",
            ("rental_profit", "capital_upside"),
            (
                "Croatia has deep summer visitor demand, but a home is not automatically lawful tourist accommodation. Verify the current categorisation decision, registered capacity, owner or host status, tax position, guest-registration process and local obligations for the exact premises. The Tourism Ministry maintains current categorised-property lists; an advertisement or plaque alone is not confirmation that a new owner can continue. In multi-unit buildings, the Building Management and Maintenance Act requires prior written consent from a two-thirds majority of co-owners plus every directly adjoining co-owner for short-term rental. Consent has a defined term and can be revoked after repeated house-rule breaches. Read the actual consent and transition position with Croatian counsel.",
                "A lawful operation still faces a short season and real costs. Model management, guest communication, cleaning, linen, utilities, cooling, platform fees, tourist and income taxes, insurance, community charges, pool and garden work, repairs, empty months and travel for owner oversight. Split and Pula have more year-round demand than a beach settlement or island villa, but product and location still determine long-term rent. An Hvar pool villa has a different booking window and operator pool from a Rovinj-area apartment. Obtain filed revenue and expense records, reconcile them with eVisitor or other official records where lawfully available, and compare the net result with a normal tenancy and personal use only.",
                "Capital upside should not be inferred from Croatia's tourism growth or euro membership. Official 2025 transaction evidence shows wide dispersion: the median apartment price was €2,743/m² across Istria County, €4,068/m² in Split and €3,921/m² in Dubrovnik. Those completed-market anchors mix neighbourhoods and property quality; they do not price a candidate. Split's resident economy and established historic towns support selected demand, while scarce island or waterfront homes can attract international buyers. The same scarcity can narrow the resale pool and amplify permitting, access or insurance problems. Model flat real prices and a longer exit before paying for a view or rental narrative.",
            ),
            "island-operating-reality",
        ),
        DossierLens(
            "Buy the future buyer's practical home",
            ("value_entry", "exit_liquidity"),
            (
                "The representative listings below deliberately span three operating patterns: a compact new apartment in Rovinjsko Selo, an established Split apartment and a Hvar pool villa. Their asking prices use seller-stated living area so the €/m² arithmetic is internally consistent, but none is a valuation. The Rovinj-area example includes a garden and parking outside the living-area denominator. The Split seller says the apartment was divided into two units, which requires legal and community reconciliation. The Hvar villa adds land, pool and furnished condition that a simple living-area comparison cannot capture. Compare each with completed transactions matched for location, lawful area, age, condition, rights and access.",
                "Value entry comes from daily utility at the chosen address. A Pula apartment near services may be less expensive than Rovinj and easier to operate year-round. A Split district outside the historic core can reach a broader resident pool than a tourism-optimised palace unit. Kaštela or Trogir can offer airport proximity but require street, traffic and building checks. Inland Istria can deliver space, yet heating, driving and resale demand must be priced. On Hvar or Brač, pay an island premium only when ferry logistics, local management, water, wastewater and lawful construction are already solved. A sea view cannot compensate for an unresolved right, unusable stair or impossible delivery route.",
                "Exit liquidity is deepest where another buyer can understand the home without adopting the seller's holiday business. Split and Pula generally offer the broadest resident logic. Rovinj and Poreč add international recognition but can carry high entry prices. Trogir's heritage and Hvar's brand reach global buyers, while ticket size, access and seasonality reduce the number who can act. Before signing, ask two agents who did not source the property how they would resell it, to whom, using which completed evidence and over what period. Model five-year cash outlay including tax, legal work, financing, community charges, management, repairs, insurance, currency and selling costs. Preserve optionality rather than depending on one exit story.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Croatia pairs Split and Pula city life with Rovinj, Trogir and island character; each brings a different year-round rhythm.",
        "global_access": "Split's airport and motorway support Dalmatia, while Istria and the islands add seasonal flights, road time and ferry dependence.",
        "ownership_clarity": "Croatia has digital land records, but nationality, reciprocity, title, cadastre, lawful area and exempted land remain property-specific.",
        "regulatory_safety": "Istria and Dalmatia require parcel-level planning, building, flood, fire, wind and community checks before a coastal purchase.",
        "rental_profit": "Croatia has strong summer demand, but categorisation, co-owner consent, management cost and empty months constrain the net case.",
        "capital_upside": "Split, Rovinj and established islands have recognised demand; high entry prices and legal or access defects limit blanket upside claims.",
        "retirement_fit": "Split and Pula offer the deepest services; Trogir, inland Istria, Hvar and Brač add driving, stairs or ferry dependence.",
        "exit_liquidity": "Split and Pula reach broader resident pools, while trophy Rovinj, Hvar and singular stone homes need narrower budgets and tastes.",
        "foreigner_fit": "Croatia is internationally familiar, but third-country reciprocity and Croatian-language legal, tax and planning work require local support.",
        "value_entry": "Istria, Split, Trogir and the islands occupy different price bands; lawful area, daily utility and resale depth determine real value.",
    },
    market_anchors=(
        {"location": "Istria County apartments", "evidence": "€2,743/m²", "buyer_read": "Median for 2025 completed apartment transactions across Istria County; not a Rovinj, Pula or property valuation.", "source_label": "Croatian Ministry 2025 market review", "source_url": "https://mpgi.gov.hr/UserDocsImages/dokumenti/stambeno/Rasic_Pregled-trzista-nekretnina_2024_2025.pdf"},
        {"location": "Split apartments", "evidence": "€4,068/m²", "buyer_read": "Highest reported 2025 municipal median for completed apartment transactions; district, legal area and condition still require matched evidence.", "source_label": "Croatian Ministry 2025 market review", "source_url": "https://mpgi.gov.hr/UserDocsImages/dokumenti/stambeno/Rasic_Pregled-trzista-nekretnina_2024_2025.pdf"},
        {"location": "Dubrovnik apartments", "evidence": "€3,921/m²", "buyer_read": "2025 completed-transaction median used as a southern-coast premium comparator, not a valuation for Dalmatia generally.", "source_label": "Croatian Ministry 2025 market review", "source_url": "https://mpgi.gov.hr/UserDocsImages/dokumenti/stambeno/Rasic_Pregled-trzista-nekretnina_2024_2025.pdf"},
    ),
    micro_locations_intro="Croatia is best read as four operating patterns rather than one coastal average. These are orientation aids, not valuation zones. Confirm municipality, parcel, ownership eligibility, title, permits, transport, healthcare, hazards and lawful use for every address.",
    micro_locations=(
        {"name": "Split", "best_for": "Year-round city and hospital base", "daily_life": "Urban services, airport and ferry hub", "diligence": "Legal subdivision, noise, stairs, parking and community"},
        {"name": "Trogir / Kaštela", "best_for": "Mainland coast near the airport", "daily_life": "Smaller settlements with road-led access", "diligence": "Historic fabric, traffic, title, permits and drainage"},
        {"name": "Pula / Rovinj / Poreč / inland Istria", "best_for": "Peninsula choice", "daily_life": "City, polished coast or quieter inland pattern", "diligence": "Entry premium, heating, driving, planning and fire"},
        {"name": "Hvar / Brač", "best_for": "Island lifestyle", "daily_life": "Seasonal towns and ferry-linked services", "diligence": "Sailings, water, wastewater, management and emergency access"},
    ),
    checklist=(
        "Confirm residence, healthcare, tax residence, OIB and representation before purchase.",
        "Confirm nationality-specific ownership eligibility, reciprocity and any ministerial consent.",
        "Choose Split, mainland coast, Istria or island daily life before choosing a view.",
        "Travel the airport, hospital, grocery, port and property routes in summer and winter.",
        "Reconcile land registry, cadastre, lawful area, permits, use, access and utilities.",
        "Overlay current flood, fire, heat, wind and coastal hazards with insurance terms.",
        "Assume zero tourist rent until categorisation, consents, tax and operator duties are confirmed.",
        "Model five-year cash outlay and identify the future resale buyer before signing.",
    ),
    references_intro="Residence, ownership, tax, title, planning, tourism, healthcare, transport, hazard, market and listing claims were reviewed on 22 August 2026. Recheck every time-sensitive source no later than 22 February 2027 and immediately after any residence, reciprocity, tax, planning, tourist-rental, listing, transport, hazard, healthcare or market-data change. Obtain current Croatian legal, tax, immigration, planning, building, insurance and property-management advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "Croatian Interior Ministry: EEA residence", "url": "https://mup.gov.hr/aliens-281621/stay-and-work/stay-and-work-of-eea-nationals-and-their-family-members-281689/281689"},
        {"label": "Croatian Interior Ministry: third-country stay", "url": "https://mup.gov.hr/aliens-281621/digital-nomads/281622"},
        {"label": "Croatian Interior Ministry: long-term residence", "url": "https://mup.gov.hr/aliens-281621/stay-and-work/permanent-stay/281682"},
        {"label": "Croatian Government: foreign property ownership", "url": "https://www.gov.hr/en/real-estate-purchase-for-foreign-nationals/1291"},
        {"label": "Croatian Government: property purchase checks", "url": "https://www.gov.hr/en/purchase-of-real-property/1282"},
        {"label": "Croatian Government: real-estate transfer tax", "url": "https://www.gov.hr/en/real-estate-transfer-tax/1464"},
        {"label": "Uređena zemlja: land registry and cadastre", "url": "https://oss.uredjenazemlja.hr/en"},
        {"label": "ISPU: official spatial-planning system", "url": "https://portal-ispu.gov.hr/en/e-services"},
        {"label": "Croatian Tourism Ministry: categorised accommodation", "url": "https://mint.gov.hr/kategorizacija-11512/11512"},
        {"label": "Official Gazette: Building Management and Maintenance Act", "url": "https://narodne-novine.nn.hr/clanci/sluzbeni/2024_12_152_2502.html"},
        {"label": "HZZO: health insurance in Croatia", "url": "https://hzzo.hr/en/national-contact-point-ncp/health-insurance-republic-croatia"},
        {"label": "Split Airport: passenger statistics", "url": "https://www.split-airport.hr/statistics/"},
        {"label": "Jadrolinija: 2026 Split sailing schedule", "url": "https://www.jadrolinija.hr/download/05995d6650992c77457e0686c75aae6c"},
        {"label": "Croatian Waters: flood hazard and risk maps", "url": "https://www.voda.hr/en/node/7088"},
        {"label": "Croatian Firefighting Association: 2026 programme", "url": "https://hvz.gov.hr/program-aktivnosti/1788"},
        {"label": "DHMZ: Croatian coastal climate", "url": "https://www.meteo.hr/klima_e.php?param=k1&section=klima_hrvatska"},
        {"label": "Croatian Ministry: 2025 property market review", "url": "https://mpgi.gov.hr/UserDocsImages/dokumenti/stambeno/Rasic_Pregled-trzista-nekretnina_2024_2025.pdf"},
        {"label": "Opereta: Rovinjsko Selo asking observation", "url": "https://www.opereta.hr/en/real-estate/apartment/121643-sale-apartment-2-room-istarska-zupanija-rovinjsko-selo"},
        {"label": "Croatia Property Sales: Split asking observation", "url": "https://www.croatiapropertysales.com/hr/hrvatska-split-apartman-na-prodaju-5802/"},
        {"label": "Croatia Property Sales: Hvar asking observation", "url": "https://www.croatiapropertysales.com/croatia-hvar-villa-for-sale-5399/"},
        {"label": "European Central Bank: euro reference rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("split-year-round-life", "/assets/croatia-split-year-round-life.webp", "Older residents walking through a shaded Split neighbourhood near a market", "Split's case rests on ordinary year-round city life as much as the waterfront.", "hero"),
        DossierImage("istria-access-diligence", "/assets/croatia-istria-access-diligence.webp", "Mature couple walking along a stone street in an Istrian hill town", "Istrian character changes with gradients, parking, road access and distance from services.", "wide"),
        DossierImage("island-operating-reality", "/assets/croatia-island-operating-reality.webp", "Residents carrying groceries from a ferry along a Croatian island quay", "An island home depends on ferries, local help and ordinary supplies after summer.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Croatia through five destination lenses",
    assessment_intro="Here’s how Croatia scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current observations show the spread from a Rovinjsko Selo apartment through a Split apartment to a Hvar villa. They are asking evidence—not valuations. Local EUR is primary; USD uses the recorded dataset exchange basis.",
    market_anchors_intro="These 2025 completed-transaction medians are broad anchors—not asking prices or property valuations. Reconcile each candidate for municipality, property type, lawful living area, condition, land, access, outlook and rights.",
    orientation_groups=(
        DossierOrientationGroup("Istrian peninsula", (("Pula", "Hospital and administrative base"), ("Rovinj / Poreč", "Premium western coast"), ("Inland Istria", "Space and hill-town routine"))),
        DossierOrientationGroup("Central Dalmatia and islands", (("Split", "Year-round regional city"), ("Kaštela / Trogir", "Airport-side mainland coast"), ("Brač", "Frequent ferry-linked island"), ("Hvar", "Premium seasonal island"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current road, bus, airport and ferry timetables and the exact hospital, service and port journey.",
    country_guide_url="/countries/croatia-property/",
    country_guide_label="Croatia property guide",
    rail_comparison="Compare Croatia with the full Atlas.",
)


QUEENSTOWN_DOSSIER = PremiumDossierSpec(
    destination_id="queenstown",
    title="Queenstown Retirement Property Dossier",
    description="Assess Queenstown property through overseas-buyer eligibility, alpine daily life, visitor-accommodation rules, hazards, healthcare, access, value, resale, and current listings.",
    h1="Queenstown: secure the right to buy before the alpine view",
    lede="Queenstown can deliver a rare combination of mountain scenery, outdoor life, airport access and an international community. It is also an expensive, supply-constrained market where many overseas people cannot buy ordinary residential land. A credible case begins with legal eligibility, not a listing. The property then has to work through winter roads, steep sites, visitor-accommodation rules, hazard maps, limited local hospital depth and a resale pool that changes sharply between Frankton apartments, Queenstown Hill houses, Arrowtown character homes and Jacks Point new builds.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is positive only for a legally eligible, well-capitalised buyer who will use Queenstown for its ordinary life as well as its scenery. Frankton is the most practical year-round base because the airport, Lakes District Hospital, supermarkets, employment and transport converge there. Queenstown town, Queenstown Hill and Fernhill put the lake and centre closer but add gradients, parking, congestion and winter access questions. Arrowtown and Lake Hayes offer a stronger community rhythm and more space, with a longer service journey. Jacks Point and Hanley's Farm provide newer stock and planned neighbourhoods, but make the household more dependent on a car and the State Highway 6 corridor.",
        "Pause before browsing if the buyer is an overseas person without a qualifying pathway. LINZ says overseas people usually cannot buy a house or land. New Zealand citizens and ordinarily resident residence-class visa holders can buy without restriction; some residence-class visa holders can apply for consent for one home; temporary visa holders generally cannot. A separate pathway effective 6 March 2026 allows qualifying investor-visa holders to seek consent for an existing dwelling with a purchase price of more than NZ$5 million; when buying land to build, the land purchase and construction prices must together exceed NZ$5 million. The Temporary Retirement Visitor Visa is still a temporary visa and does not itself solve ordinary residential eligibility. Sensitive-land rules can create an additional consent question near lakes, reserves and other protected features.",
        "Proceed in a strict order. Obtain a written eligibility opinion for the buyer, entity and parcel. Choose the daily-life base before the property. Confirm the record of title, LIM, lawful floor area, building work, body-corporate records, insurance and finance. Check the address in QLDC planning, visitor-accommodation and hazard systems. Drive the hospital, grocery, airport and winter route at peak time. If rent matters, register the property and obtain written confirmation of permitted nights or resource consent. Model rates, insurance, heating, maintenance, management, empty periods and a slower sale. Buy only if the home remains useful without tourist income or automatic capital growth.",
    ),
    lenses_intro="The five paired lenses translate Queenstown's ten Atlas dimensions into the legal, daily-life and property choices that can reverse the decision. The complete ten-factor assessment appears once in the score table.",
    lenses=(
        DossierLens(
            "Live through winter, not only the ski week",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Queenstown's lifestyle appeal survives beyond the postcard when the household actively uses the trails, lake, golf, food and community. The test is whether the same address works during a cold inversion, a busy holiday week and a quiet shoulder season. Frankton offers the broadest ordinary routine: supermarkets, medical care, the airport and public transport are close. Queenstown town and Fernhill place restaurants and the lake nearby, but steep walks, visitor traffic and parking can erode convenience. Arrowtown has a calmer resident centre and established social life. Jacks Point and Lake Hayes reward space and mountain access while making errands more deliberate.",
                "Retirement fit is more selective than lifestyle magnetism. Lakes District Hospital in Frankton has a 24-hour emergency department, primary birthing, district nursing and selected outpatient clinics. Health New Zealand describes it as a smaller rural hospital; tertiary services are centred in Dunedin, with some specialist pathways also involving Southland. A buyer managing cardiac, oncology, neurological or complex surgical care should map the actual referral journey, weather alternative and accommodation plan. Confirm New Zealand healthcare eligibility separately from property ownership and keep suitable private cover where needed. A home near Frankton can reduce routine friction, but it does not create specialist depth.",
                "The dwelling should make alpine life safer. Prefer sun, insulation, effective heating, mechanical ventilation, a low-slip entry, internal garage access and a main-level bedroom and bathroom where mobility may change. Inspect retaining walls, drainage, roof condition, glazing and freeze exposure. On Queenstown Hill or Fernhill, test the driveway after frost and the walking route with groceries. In Arrowtown, check heritage or character constraints before changing an older house. In Jacks Point and Hanley's Farm, read design controls, service arrangements and owners' obligations. A lake view is not compensation for a dark living room, unsafe stairs or an uninsurable slope.",
            ),
        ),
        DossierLens(
            "Use the airport advantage without underestimating the last mile",
            ("global_access", "foreigner_fit"),
            (
                "Queenstown Airport is a genuine advantage for a small alpine market. It links directly to New Zealand's three largest cities and Australian destinations; FY26 international passenger movements passed one million and total movements were expected around 2.8 million. That is regional access, not a global hub. Long-haul trips normally connect through Auckland, Christchurch, Sydney, Melbourne or Brisbane, and winter weather can disrupt schedules. Frankton places the terminal minutes from daily services. Arrowtown, Lake Hayes and Jacks Point add road time. Queenstown town can be close in kilometres yet slow when Frankton Road and the town centre are congested.",
                "Ground transport is inexpensive but uneven by address and time. Orbus currently charges NZ$2.50 for an adult Bee Card trip and serves the airport, town, Frankton, Arrowtown and several residential areas. A timetable is not proof that an isolated street, early flight or specialist appointment is practical without a car. NZTA says Frankton Road carries roughly 25,000 to 30,000 vehicles a day, and freezing conditions constrain winter road construction. Snow and ice can close or slow regional roads, including the Crown Range. Test the exact commute in school, airport and ski peaks; identify an alternative when the household cannot or should not drive.",
                "Queenstown's international workforce and visitor economy make everyday English-language integration easier than in many resort markets. The harder fit is administrative and legal. Overseas-investment consent, immigration, tax, title, planning, building and body-corporate decisions follow New Zealand systems and must be handled by the buyer's own advisers. A marketing claim that a property is 'AIP eligible' is not a determination for the buyer or parcel. A non-resident owner also needs reliable local oversight after frost, wind, a leak or an alarm. Foreigner fit is strongest for someone willing to establish residence and a local operating network, not for a remote buyer expecting the agent to remain the manager.",
            ),
        ),
        DossierLens(
            "Clear eligibility, lawful use and the hazard map",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Ownership clarity begins with the Overseas Investment Act rather than the title search. LINZ sets different pathways for citizens, ordinarily resident residence-class visa holders, residence-class holders who need consent, Australians and Singaporeans, qualifying investor-visa holders, and other overseas people. Confirm the buyer's exact status before committing to finance, due diligence or an auction. Then obtain the record of title and check the seller, estate, caveats, easements, access and any sensitive-land issue. The LIM, council property file and building inspection should reconcile every structure and consent. For an apartment, examine body-corporate minutes, long-term maintenance plan, insurance, remediation, levies and visitor-use rules.",
                "Visitor accommodation is property-specific. QLDC requires residential visitor accommodation to be registered. The number of permitted nights and operating standards depend on the District Plan zone and address; activity beyond permitted standards can require resource consent. A current or former listing on a booking platform does not prove that a new owner may continue. Check the ePlan, registration, consent, conditions, fire requirements, parking, noise rules, rates category and body-corporate or neighbourhood covenants. Obtain written advice for the intended occupancy pattern. If the file is incomplete or an application is merely 'in process', value the property as a private home with no tourist income.",
                "Natural hazards vary over very short distances. QLDC's official layers include landslide, debris-flow, rockfall, erosion, avalanche, faults and liquefaction; its flood strategy maps inundation areas, and local reserve planning identifies earthquake, debris-flow, rockfall and high wildfire exposure around Queenstown's steep vegetated slopes. Order the current LIM, then commission site-specific geotechnical, drainage, retaining-wall, wildfire and insurance review where the address warrants it. Check emergency access and evacuation, not only the building footprint. A property outside one mapped polygon can still face overland flow, falling material, smoke, road closure or an insurance exclusion.",
            ),
            "slope-hazard-diligence",
        ),
        DossierLens(
            "Underwrite rent as a consented operation",
            ("rental_profit", "capital_upside"),
            (
                "Queenstown has powerful visitor demand, but gross nightly rates are not owner return. Start with the lawful calendar for the exact property, then reconcile achieved nights, rates, cancellations and owner use with bank and tax records. Deduct management, cleaning, linen, utilities, heating, platform fees, rates, insurance, body-corporate charges, repairs, furniture replacement and empty periods. A Frankton Road apartment may have a mature accommodation ecosystem but also remediation, management and GST questions. A Queenstown Hill house may have more owner flexibility but higher maintenance and access burden. A Hanley's Farm home-and-income layout still needs lawful-unit and rental-use confirmation.",
                "Long-term demand provides a second case because Queenstown has a resident workforce and constrained housing supply. That does not make every holiday product a good tenancy. Parking, heating, storage, bedroom legality, commute and lease terms determine resident demand. Compare a normal tenancy, registered visitor accommodation and personal use under the same five-year cash model. Tax treatment can differ: IRD taxes New Zealand rental profit and applies wider land-sale rules; for residential property sold on or after 1 July 2024, the bright-line test generally looks at a two-year period, subject to exclusions and other tax rules. Commission buyer-specific tax advice before relying on a net yield.",
                "Capital upside is supported by scarcity, global recognition and an expanding resident and visitor economy, but recent evidence is not a straight line. QV reported an average Queenstown home value of NZ$1,941,732 in May 2026 after four months of modest growth; by July its index showed only a 0.2% quarterly gain while the national market weakened. These are broad modelled values, not a candidate valuation. Planning constraints and difficult sites can limit supply, while high construction costs and buyer eligibility can limit demand. Pay for lawful utility and a recognisable buyer case, not a forecast built from tourism growth alone.",
            ),
            "planned-community-daily-life",
        ),
        DossierLens(
            "Enter through utility and preserve the buyer pool",
            ("value_entry", "exit_liquidity"),
            (
                "Entry value differs by operating pattern. The current Frankton Road apartment observation is NZ$839,000 for 68 square metres and offers a lower ticket with body-corporate and visitor-use diligence. The Hanley's Farm home-and-income observation is NZ$1.78 million for 237 square metres and adds a separate unit, newer construction and car dependence. The Queenstown Hill observation is NZ$3.49 million for 322 square metres, with slope, new-build and pending visitor-consent questions. Their floor-area comparisons are internally consistent, but land, views, parking, condition, GST and legal use differ. They are asking observations, not valuations or proof of availability.",
                "Official rating values show the submarket spread without pretending to be sale prices. QLDC's 2024 revaluation reports average residential capital values of NZ$1,711,114 in Frankton, NZ$2,171,809 in Arrowtown and NZ$3,025,016 across Wakatipu Heights, Panorama and Queenstown. These values were assessed for rates using market evidence around 1 September 2024; they are not current valuations, internal-area comparisons or offers. Use them to test whether a listing's submarket story is plausible, then commission matched completed sales and an independent valuation. A single Queenstown-wide dollar-per-square-metre number cannot price an apartment, historic cottage and alpine house.",
                "Exit liquidity follows legal eligibility, ticket size and ordinary usefulness. A warm, well-run Frankton apartment can reach resident, downsizer and eligible second-home buyers, though body-corporate or visitor-use problems shrink the pool. Arrowtown character reaches lifestyle demand but can be expensive and alteration-sensitive. A practical Jacks Point or Lake Hayes house may appeal to local households; a singular steep-site or NZ$5 million-plus trophy home needs fewer buyers. Before purchase, ask two agents who did not source the listing how they would resell it, which completed sales they would use, and how long the category can take. Model a slow sale and full selling costs.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Queenstown combines lake, mountains and year-round outdoor life; Frankton, Arrowtown and Jacks Point produce very different daily rhythms.",
        "global_access": "Queenstown Airport offers strong domestic and Australian links, while long-haul travel, winter weather and Frankton-road congestion add connection risk.",
        "ownership_clarity": "Queenstown title systems are clear, but overseas-buyer eligibility and sensitive-land consent can prevent an otherwise ordinary residential purchase.",
        "regulatory_safety": "Queenstown requires address-level visitor-use, building, body-corporate, landslide, flood, rockfall, wildfire and insurance diligence.",
        "rental_profit": "Queenstown has deep visitor and resident demand, but lawful nights, management, heating, rates and body-corporate costs control the net return.",
        "capital_upside": "Queenstown scarcity and recognition support selected homes; high entry prices, buyer restrictions and a patchy 2026 market limit broad upside claims.",
        "retirement_fit": "Frankton offers emergency care and daily services, but Queenstown's complex specialist treatment can require travel to Dunedin or Southland.",
        "exit_liquidity": "Frankton and practical family homes reach broader pools; Queenstown Hill trophy properties and compromised alpine sites need fewer eligible buyers.",
        "foreigner_fit": "Queenstown is internationally familiar, yet residence, overseas-investment consent, tax and remote property management still require local professional support.",
        "value_entry": "Queenstown entry spans Frankton apartments, Jacks Point houses and premium Wakatipu slopes; lawful utility matters more than one resort average.",
    },
    market_anchors=(
        {"location": "Frankton residential", "evidence": "NZ$1,711,114", "buyer_read": "Average 2024 council capital rating value across 422 residential assets; assessed around 1 September 2024 and not a current property valuation.", "source_label": "QLDC 2024 revaluation", "source_url": "https://www.qldc.govt.nz/services/rates-property/revaluation-and-how-it-affects-rates"},
        {"location": "Arrowtown residential", "evidence": "NZ$2,171,809", "buyer_read": "Average 2024 council capital rating value across 1,263 residential assets; not a sale median, floor-area comparison or candidate valuation.", "source_label": "QLDC 2024 revaluation", "source_url": "https://www.qldc.govt.nz/services/rates-property/revaluation-and-how-it-affects-rates"},
        {"location": "Wakatipu Heights / Panorama / Queenstown", "evidence": "NZ$3,025,016", "buyer_read": "Average 2024 council capital rating value across 709 residential assets; broad rating evidence, not a current valuation for Queenstown Hill.", "source_label": "QLDC 2024 revaluation", "source_url": "https://www.qldc.govt.nz/services/rates-property/revaluation-and-how-it-affects-rates"},
    ),
    micro_locations_intro="Queenstown is best read as four daily-life patterns rather than one resort average. Confirm buyer eligibility, the exact title, QLDC zone, lawful use, winter route, healthcare access, hazard layers and insurance for every address.",
    micro_locations=(
        {"name": "Frankton / Remarkables Park", "best_for": "Most practical year-round base", "daily_life": "Airport, hospital, shops, work and buses", "diligence": "Traffic, airport noise, body corporate and future planning"},
        {"name": "Queenstown town / Hill / Fernhill", "best_for": "Town access and lake outlook", "daily_life": "Restaurants and visitor energy with steep streets", "diligence": "Slope, frost, parking, noise, retaining walls and visitor use"},
        {"name": "Arrowtown / Lake Hayes", "best_for": "Community rhythm and space", "daily_life": "Village or suburban life with a longer service trip", "diligence": "Heritage, commute, sun, hazards and transport"},
        {"name": "Jacks Point / Hanley's Farm", "best_for": "Newer planned-community housing", "daily_life": "Golf, trails and family stock south of Frankton", "diligence": "Car dependence, design controls, services, wind and exit"},
    ),
    checklist=(
        "Obtain a written LINZ eligibility and sensitive-land opinion for the buyer, entity and parcel.",
        "Confirm the residence, healthcare and tax plan separately from property ownership.",
        "Choose Frankton, central slopes, Arrowtown / Lake Hayes or Jacks Point daily life first.",
        "Travel the airport, hospital, grocery and property routes in winter and peak traffic.",
        "Reconcile title, LIM, lawful floor area, building file, inspection and body-corporate records.",
        "Overlay QLDC flood, landslide, rockfall, liquefaction and wildfire evidence with insurance.",
        "Assume zero short-stay income until registration, permitted nights or consent are confirmed.",
        "Model five-year cash outlay and a slow sale to the next legally eligible buyer.",
    ),
    references_intro="Ownership, residence, tax, title, planning, visitor-accommodation, healthcare, transport, hazard, market and listing claims were reviewed on 22 August 2026. Recheck every time-sensitive source no later than 22 February 2027 and immediately after any ownership, residence, tax, planning, rental, listing, transport, hazard, healthcare or market-data change. Obtain current New Zealand legal, tax, immigration, overseas-investment, planning, building, geotechnical, insurance and property-management advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "LINZ: buying residential property to live in", "url": "https://www.linz.govt.nz/guidance/overseas-investment/buying-residential-property-live"},
        {"label": "LINZ: NZ$5 million-plus house pathway", "url": "https://www.linz.govt.nz/guidance/overseas-investment/ways-invest/pathways-migrants-and-visa-holders/investing-residential-land-over-5-million"},
        {"label": "LINZ: Overseas Investment Act reform", "url": "https://www.linz.govt.nz/our-work/overseas-investment-regulation/reform-overseas-investment-act"},
        {"label": "LINZ: residential development pathways", "url": "https://www.linz.govt.nz/guidance/overseas-investment/ways-invest/investing-residential-land-develop"},
        {"label": "Immigration New Zealand: Temporary Retirement Visitor Visa", "url": "https://www.immigration.govt.nz/visas/temporary-retirement-visitor-visa/"},
        {"label": "QLDC: short-term visitor accommodation", "url": "https://www.qldc.govt.nz/services/rates-property/short-term-visitor-accommodation"},
        {"label": "QLDC: resource-consent check", "url": "https://www.qldc.govt.nz/services/resource-consents/do-i-need-a-resource-consent"},
        {"label": "QLDC: other land-hazard layers", "url": "https://gis.qldc.govt.nz/server/rest/services/Hazards/Other_Land_Hazards/MapServer"},
        {"label": "QLDC: liquefaction layer", "url": "https://gis.qldc.govt.nz/server/rest/services/Hazards/Liquefaction/MapServer"},
        {"label": "QLDC: flood management and maps", "url": "https://www.qldc.govt.nz/your-council/council-documents/strategies-and-publications/flood-management-strategy/"},
        {"label": "QLDC: Ben Lomond and Queenstown Hill reserve hazards", "url": "https://www.qldc.govt.nz/media/kkbl4ds3/te-taumata-o-hakitekura-ben-lomond-and-te-tapunui-queenstown-hill-reserve-management-plan_nov25.pdf"},
        {"label": "Health New Zealand: Lakes District Hospital", "url": "https://www.healthnz.govt.nz/hospitals-services/hospitals/otago-southland/lakes-district-hospital"},
        {"label": "Health New Zealand: Otago and Southland hospital network", "url": "https://www.healthnz.govt.nz/careers/locations/otago-and-southland"},
        {"label": "Queenstown Airport: destinations", "url": "https://www.queenstownairport.co.nz/flights/destinations/"},
        {"label": "Queenstown Airport: FY26 international milestone", "url": "https://www.queenstownairport.co.nz/corporate/news-media/media-releases/trans-tasman-travel/"},
        {"label": "Otago Regional Council: Queenstown Orbus fares", "url": "https://www.orc.govt.nz/orbus/fares"},
        {"label": "NZTA: Queenstown transport package", "url": "https://www.nzta.govt.nz/projects/queenstown-package"},
        {"label": "QLDC: Crown Range winter-road closures", "url": "https://www.qldc.govt.nz/media/sq2cs0z3/qldc_scuttlebutt_aug-sep-2022_issue150-web.pdf"},
        {"label": "QV: May 2026 House Price Index", "url": "https://www.qv.co.nz/news/qv-house-price-index-may-2026-southern-centres-gain-ground-in-patchy-property-market/"},
        {"label": "QV: July 2026 House Price Index", "url": "https://www.qv.co.nz/news/qv-house-price-index-july-2026-winter-chill-settles-over-cautious-housing-market/"},
        {"label": "QLDC: 2024 residential revaluation", "url": "https://www.qldc.govt.nz/services/rates-property/revaluation-and-how-it-affects-rates"},
        {"label": "IRD: non-resident property tax", "url": "https://www.ird.govt.nz/international/individuals/tax-for-non-resident-taxpayers"},
        {"label": "Settled.govt.nz: property due diligence", "url": "https://www.settled.govt.nz/buying-a-home/researching-the-property/doing-your-homework/"},
        {"label": "Realestate.co.nz: Frankton Road asking observation", "url": "https://www.realestate.co.nz/43093321/residential/sale/unit-606-327-frankton-road-queenstown-central?lid=jyzkx2cbid2g"},
        {"label": "Listed.co.nz: Hanley's Farm asking observation", "url": "https://www.listed.co.nz/property/5200"},
        {"label": "Realestate.co.nz: Queenstown Hill asking observation", "url": "https://www.realestate.co.nz/43060560/residential/sale/79-middleton-road-queenstown-hill"},
        {"label": "European Central Bank: euro reference rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("frankton-daily-life", "/assets/queenstown-frankton-daily-life.webp", "Older residents carrying groceries through Frankton with Lake Wakatipu and mountains beyond", "Frankton makes the strongest year-round case through ordinary services, not resort spectacle.", "hero"),
        DossierImage("slope-hazard-diligence", "/assets/queenstown-winter-access-healthcare.webp", "Mature couple walking beside a frosty sloping Queenstown street near a parked car", "Winter access, gradients and the hospital route belong in the property decision.", "wide"),
        DossierImage("planned-community-daily-life", "/assets/queenstown-planned-community-daily-life.webp", "Residents waiting for a local bus in a planned Queenstown alpine neighbourhood", "Jacks Point and Lake Hayes trade central convenience for newer homes, space and driving.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Queenstown through five destination lenses",
    assessment_intro="Here’s how Queenstown scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current observations show the spread from a Frankton Road apartment through a Hanley's Farm home-and-income property to a Queenstown Hill new build. They are asking evidence—not valuations. Local NZD is primary; USD uses the recorded ECB cross-rate basis.",
    market_anchors_intro="These official 2024 council capital rating values are broad submarket anchors—not sale prices, floor-area comparisons or current property valuations. Commission matched completed-sales evidence and a candidate-specific valuation.",
    orientation_groups=(
        DossierOrientationGroup("Core and western slopes", (("Frankton / Remarkables Park", "Airport, hospital and daily services"), ("Frankton Road", "Lake corridor and traffic"), ("Queenstown town / Hill", "Centre and steep premium slopes"), ("Fernhill", "Western views and gradients"))),
        DossierOrientationGroup("Basin and southern communities", (("Arrowtown", "Established village centre"), ("Lake Hayes / Shotover Country", "Residential basin"), ("Jacks Point / Hanley's Farm", "Planned communities south of Frankton"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current bus, winter-road and airport service, peak traffic, the exact hospital route and property-level access.",
    country_guide_url="/countries/new-zealand-property/",
    country_guide_label="New Zealand property guide",
    rail_comparison="Compare Queenstown with the full Atlas.",
)


PHUKET_KOH_SAMUI_DOSSIER = PremiumDossierSpec(
    destination_id="phuket-koh-samui",
    title="Phuket and Koh Samui Retirement Property Dossier",
    description="Assess Phuket and Koh Samui retirement property through legal ownership, residence, healthcare, access, rental rules, hazards, value, exit liquidity, and current asking evidence.",
    h1="Phuket / Koh Samui: choose the legal product before the tropical life",
    lede=(
        "Phuket and Koh Samui can deliver an unusually rich tropical life: warm-water coast, strong food culture, international airports and established private services. They are not one property market. Phuket offers the deeper hospital, retail and condominium ecosystem; Samui offers a more intimate villa-and-island rhythm with greater operational dependence. The controlling decision is legal, not scenic: choose the ownership product, lawful use and future buyer pool before choosing the view."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is selectively positive for a well-capitalised buyer who will use independent Thai legal, tax and building professionals and who values the home even without short-stay income. A registered foreign-quota condominium is usually the clearest ownership product because the foreign buyer can hold the unit freehold when the building remains inside the statutory 49% foreign-ownership ceiling and the required remittance evidence is satisfied. A villa is different: foreigners generally cannot own Thai land, so the buyer must understand separately the land right, building ownership, lease, superficies, company, succession and resale mechanics. A brochure's word ‘freehold’ is not enough.",
        "Phuket is the stronger year-round operating base. Phuket Town and Wichit connect hospitals, government services and ordinary urban life; Rawai, Nai Harn and Chalong provide a lived-in southern coastal pattern; Choeng Thale, Laguna and Si Sunthon provide a polished international service ecosystem at a higher price and with more development exposure. Koh Samui is credible for buyers who deliberately want an island villa life around Bo Phut, Maenam or Lamai and accept narrower healthcare depth, road dependence, water and wastewater questions, storm disruption and a smaller operator and resale pool.",
        "Look elsewhere first if the plan depends on the property creating residence, direct foreign land freehold, an informal nominee company, guaranteed yield or hands-off villa ownership. A Thai home does not grant a visa. The BOI Long-Term Resident programme has separate age, passive-income and investment tests; property can be part of a qualifying investment for some applicants but does not produce automatic approval. Proceed in order: establish residence and healthcare, select the legal product, choose the daily-life zone, reconcile title and building, test hazards and services, then price the exit."
    ),
    lenses_intro="The Atlas pairs the ten decision dimensions into five practical questions. Phuket and Koh Samui share a national legal framework, but daily life, infrastructure, product type and the future buyer pool differ enough that each address needs its own conclusion.",
    lenses=(
        DossierLens(
            "Choose the daily system, not the holiday memory",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Phuket's best retirement case is ordinary life with tropical access. Phuket Town and Wichit offer supermarkets, markets, cafés, municipal services and the island's deepest concentration of hospitals and specialists. Bangkok Hospital Phuket publishes emergency and specialist contact routes, while other private and public providers expand the local network. Rawai and Chalong have a strong foreign-resident ecosystem, marinas, restaurants and south-coast access, but traffic and distance from major hospitals vary by address. Choeng Thale and Laguna add polished services and beach proximity, though the pattern can feel more resort-led and development-heavy. Test the home on a weekday in wet season, not only at sunset.",
                "Koh Samui offers a more private island rhythm. Bo Phut combines airport access, services and a broad residential base; Maenam is quieter and greener with a longer east-coast service trip; Lamai has an established town and beach pattern south of the busiest northeast corridor. The trade is operational. Samui's hospital choice and airport are useful but smaller, specialist care can require travel, and most households depend on a car, driver or motorbike on roads with variable width, drainage and lighting. Koh Samui municipality publishes water-resource and wastewater work because those systems matter. Confirm actual supply, storage, septic or sewer connection and backup arrangements for the candidate home.",
                "Retirement fit changes when heat, mobility or health changes. Walk the route to groceries, test stairs and bedroom access, time an emergency journey and ask who can manage the property during an absence. Private healthcare needs insurance or a funded self-pay plan; owning a home does not create public coverage or residence. On both islands, inspect cooling, shade, ventilation, mosquito control, mould, salt corrosion and wet-season access. The strongest home remains manageable when one household member cannot drive, when a flight is disrupted and when the pool, pump, air-conditioning or roof needs urgent work. Tropical appeal earns the destination's lifestyle score; repeatable daily life earns retirement fit.",
            ),
        ),
        DossierLens(
            "Use the airports, but price the final kilometre",
            ("global_access", "foreigner_fit"),
            (
                "Phuket International Airport gives the island a material access advantage. Airports of Thailand publishes current passenger services, transport and flight information, and the airport supports domestic and regional routes without a Bangkok road transfer. That does not make every address easy. The north-south road system can turn a modest map distance into a slow journey in peak traffic or heavy rain. Choeng Thale and the northwest sit closer to the airport than Rawai and Nai Harn; Phuket Town and Wichit are better connected to administrative and hospital functions. Time the front-door journey during a realistic arrival, including luggage, rain, taxi availability and a late flight.",
                "Samui Airport makes island living far more practical than a ferry-only destination, but route breadth, pricing and disruption tolerance differ from Phuket. The airport is close to Bo Phut and the northeast; Maenam and Lamai add road time. Ferries provide useful redundancy and vehicle access, yet port choice, queues, weather and onward travel matter. A buyer who makes frequent long-haul journeys should compare the whole chain, not the existence of an airport icon. Keep a plan for missed connections, medical transfer, storm disruption and receiving contractors or family when the owner is abroad.",
                "Both islands are internationally familiar, with English-speaking agents, private hospitals and service businesses. Familiarity reduces friction but does not change the language or authority of Land Office records, building permits, tax filings, juristic-person documents or local licences. Appoint an independent Thai lawyer who did not represent the seller or developer, a tax adviser, an engineer and a reliable local contact. Have material documents translated, identify who receives official notices and agree inspection and payment controls. Foreigner fit is strong for a buyer who builds this local operating system; it is weak for someone expecting the sales team or rental manager to substitute for independent governance.",
            ),
        ),
        DossierLens(
            "Separate land, building, title and permitted use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Start with the legal product. The Department of Lands' current foreign-condominium regulation and official transfer guidance require buyers to verify the foreign-ownership quota and qualifying foreign-currency evidence. Confirm the condominium registration, unit title, current foreign quota, remittance documentation, common-property rights, juristic-person accounts, reserve fund, insurance, arrears, litigation and rules. A resort residence can have a condominium title, a hotel operating layer, both or neither. Ask whether the unit is independently transferable and occupiable if a branded operator changes, and whether promised services are contractual, funded and lawful.",
                "A villa requires a different file. Foreign individuals generally cannot own land, and a Thai company's landholding cannot lawfully rely on nominee shareholders. A lease can grant use for its registered term but is not land freehold; renewal promises, inheritance and transfer economics need written analysis. Building ownership, superficies, usufruct, access, utilities and the land title must be reconciled. Check the Chanote or other title, survey and encumbrances at the Land Office; trace seller authority and company history; verify the construction permit, completion, lawful floor area, pool and retaining structures. The Si Sunthon observation below is marketed with company ownership. That description is a diligence warning, not an endorsed structure.",
                "Hazard and building review belong beside title. The Department of Mineral Resources publishes landslide susceptibility and geohazard maps, including Phuket tsunami material; the Meteorological Department publishes monsoon and rainfall evidence. Overlay current tsunami, flood, landslide and drainage information, then inspect the actual site after rain. Review slope cuts, retaining walls, access gradient, stormwater route, roof fixing, corrosion, water storage, electrical systems and evacuation. Koh Samui hillside villas require particular road, retaining-wall and runoff scrutiny. Obtain a property-specific insurance quotation before commitment. Being outside a mapped outline does not prove the address will drain, evacuate or insure well.",
            ),
            "monsoon-road",
        ),
        DossierLens(
            "Treat short stays as a regulated operating business",
            ("rental_profit", "capital_upside"),
            (
                "Do not underwrite nightly income from an online listing. Thailand's Hotel Act defines temporary accommodation for compensation as a hotel and creates a licence framework, subject to current exemptions and implementing rules; accommodation provided on a monthly basis or longer is treated differently in the Act's definition. The exact building, unit, room count, operator and local permission determine the answer. Verify the Hotel Act licence or exemption, building use, local registration, condominium rules, tax position and operator authority in writing. A developer pool, management contract or historic guest activity is not proof that a new owner may continue the same operation.",
                "A lawful property still needs a complete operating model. Reconcile achieved nights and rates with bank, tax and booking records, then deduct management, guest communication, cleaning, linen, platform fees, electricity, water, internet, pool and garden care, pest control, insurance, repairs, replacement reserve, tax, owner use and empty periods. Villa utilities and maintenance can be large, particularly when cooling, pumps and salt exposure combine. Phuket has a deeper management market; Samui's operator dependence and logistics can be greater. Compare the outcome with a normal monthly tenancy and with personal use only. Reject guaranteed yield unless the guarantor, security, term, exclusions and payment history survive independent review.",
                "Official REIC evidence provides scale, not a return forecast. In 2025 foreigners transferred 1,190 condominium units worth 6,087 million baht in Phuket, versus 212 units worth 552 million baht across Surat Thani Province. The latter is province-wide and is not a Samui villa series. REIC's Q1 2026 secondary asking inventory showed 2,898 Phuket listings with an average asking price of 8.3 million baht, while Surat Thani's broader inventory was larger and cheaper on average. These figures confirm activity and dispersion; they do not establish a candidate yield, lawful use or appreciation. Capital upside remains product- and structure-specific.",
            ),
            "samui-villa-life",
        ),
        DossierLens(
            "Enter through a recognisable product and preserve the exit",
            ("value_entry", "exit_liquidity"),
            (
                "The three current observations deliberately mix products. The Rawai condominium asks 14 million baht for 134 square metres of seller-stated indoor area and is marketed as foreign quota. The Si Sunthon villa asks 30.9 million baht for 534 square metres and is marketed with company ownership. The Maenam villa asks 12.9 million baht for 220 square metres on a stated 600-square-metre plot and is marketed as ‘Sale with Company’ while noting that a foreigner cannot own the land. Both company-sale descriptions are diligence warnings, not endorsed structures. Their converted area prices are not a clean index: common areas, land, age, services, fit-out and legal rights differ. They are asking evidence—not valuations or proof of availability.",
                "Value entry begins with comparability. For a condominium, compare completed transfers in the same building or immediate area, unit condition, view, floor, foreign quota, common fees, reserve and operating restrictions. For a villa, compare the lawful building and land rights, plot, internal area, age, access, drainage, water, permit and maintenance record. REIC's official inventory and foreign-transfer totals can challenge an implausible story, but a candidate needs matched completed evidence and an independent valuation. A cheap legal structure can be expensive at exit; a premium for clear foreign-quota title, ordinary access and a well-run building may be rational.",
                "Exit liquidity follows the next buyer's eligibility and confidence. A well-located foreign-quota Phuket condominium can reach a broader international pool if the building is funded and the title is clean. A practical Rawai or Choeng Thale home may attract resident and second-home demand, but competition from new supply matters. A Samui villa's pool narrows with ticket size, lease duration, company risk, steep access, specialised design and operator dependence. Before purchase, ask two independent agents how they would resell the exact legal product, which completed deals they would use and how long it could take. Model a slow sale, full selling costs and no appreciation.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Phuket combines deep services with Rawai and Choeng Thale coast life; Koh Samui offers a quieter villa rhythm around Maenam and Bo Phut.",
        "global_access": "Phuket Airport has the broader network; Samui Airport keeps island life viable but adds higher connection, road and disruption sensitivity.",
        "ownership_clarity": "Phuket and Koh Samui condominiums can offer foreign-quota freehold; villa land, building, lease and company rights require separate legal proof.",
        "regulatory_safety": "Phuket and Samui buyers must reconcile title, permits, lawful accommodation use, tsunami, flood, landslide, drainage and insurance at address level.",
        "rental_profit": "Phuket has the deeper operator market, while Koh Samui villas can carry heavier utilities, maintenance, seasonality and management dependence.",
        "capital_upside": "Phuket transaction depth supports selected products; Koh Samui scarcity can help distinctive villas, but structure and exit risk constrain broad appreciation claims.",
        "retirement_fit": "Phuket Town and Wichit provide the strongest healthcare base; Maenam, Bo Phut and Lamai require more driving and medical-transfer planning.",
        "exit_liquidity": "Foreign-quota Phuket condominiums reach a clearer buyer pool; singular Samui villas and company or lease structures can take longer to resell.",
        "foreigner_fit": "Phuket and Koh Samui are internationally familiar, yet Land Office, visa, tax, building and licensing work still needs independent Thai support.",
        "value_entry": "Rawai, Si Sunthon and Maenam asking evidence spans unlike legal and physical products, so one island-wide price cannot establish value.",
    },
    market_anchors=(
        {"location": "Phuket foreign condominium transfers", "evidence": "1,190 units / 6,087 million THB", "buyer_read": "Official REIC 2025 foreign-buyer transfers; activity evidence, not an asking-price or villa-market benchmark.", "source_label": "REIC 2025 foreign condominium report", "source_url": "https://www.reic.or.th/News/RealEstate/470678"},
        {"location": "Surat Thani foreign condominium transfers", "evidence": "212 units / 552 million THB", "buyer_read": "Official REIC 2025 province-wide evidence; not specific to Koh Samui and not a villa series.", "source_label": "REIC 2025 foreign condominium report", "source_url": "https://www.reic.or.th/News/RealEstate/470678"},
        {"location": "Phuket secondary asking inventory", "evidence": "2,898 listings / 8.3 million THB average", "buyer_read": "Official Q1 2026 asking-inventory evidence; a broad listing average, not a completed-sale median or candidate valuation.", "source_label": "REIC Q1 2026 secondary inventory", "source_url": "https://www.reic.or.th/Upload/260616-PressReleaseREIC-Q1-69-02_59769_1781663071_30035.pdf"},
    ),
    micro_locations_intro="Choose the operating pattern before the property. These four areas span urban service depth, southern resident coast, premium northwest development and Samui island life; none substitutes for address-level title, building, hazard and transport work.",
    micro_locations=(
        {"name": "Phuket Town / Wichit", "best_for": "Strongest year-round services and hospitals", "daily_life": "Urban markets, retail, administration and ordinary resident demand", "diligence": "Traffic, flood drainage, building management and coast access"},
        {"name": "Rawai / Nai Harn / Chalong", "best_for": "Lived-in southern coast and foreign-resident services", "daily_life": "Restaurants, marinas and beach access with a car-led rhythm", "diligence": "Airport and hospital time, oversupply, title, drainage and lawful rent"},
        {"name": "Choeng Thale / Laguna / Si Sunthon", "best_for": "Polished services and northwest beach access", "daily_life": "International schools, dining, clubs and expanding residential zones", "diligence": "Construction pipeline, traffic, common fees, water and villa structure"},
        {"name": "Koh Samui: Bo Phut / Maenam / Lamai", "best_for": "Deliberate island and villa lifestyle", "daily_life": "Airport-side services, quieter north coast or established southeast town", "diligence": "Roads, slope, water, wastewater, healthcare transfer, operator and exit"},
    ),
    checklist=(
        "Confirm the residence, healthcare and tax plan separately from property ownership.",
        "Obtain an independent Thai opinion on the buyer, title, land, building, lease, company and exit rights.",
        "For a condominium, verify registration, unit title, foreign quota, remittance evidence and juristic-person finances.",
        "For a villa, reconcile Chanote, survey, access, building permit, lawful area, pool, utilities and every land right.",
        "Overlay tsunami, flood, landslide and rainfall evidence; inspect drainage, slope and evacuation on site.",
        "Assume zero nightly income until the Hotel Act licence or exemption, building use and operator authority are proven.",
        "Test airport, hospital, grocery and contractor journeys in peak traffic and wet season.",
        "Model five-year cash outlay and a slow resale to the next legally eligible buyer.",
    ),
    references_intro="Ownership, residence, tax, lodging, title, hazards, healthcare, transport, market and listing claims were reviewed on 22 August 2026. Recheck no later than 22 February 2027 and immediately after any ownership, visa, tax, lodging, listing, transport, hazard or market-data change. Obtain current Thai legal, tax, immigration, building, engineering, insurance and management advice for the exact buyer and property. Listings are dated asking observations, not valuations or availability guarantees.",
    references=(
        {"label": "Department of Lands: foreign condominium ownership regulation", "url": "https://www.dol.go.th/en/dol-services/public-service-manual/land-registration/land-for-foreigners/dol-regulation-foreign-condominium-ownership-2004/"},
        {"label": "Department of Lands: foreign-buyer transfer documents", "url": "https://www.dol.go.th/question-answer/Q2601-000065"},
        {"label": "Department of Lands: English Land Code", "url": "https://www.dol.go.th/media/813280848056029184/2026/02/EBAF485hLGxjwntourvyDW2a.pdf"},
        {"label": "Department of Lands: land for foreigners", "url": "https://www.dol.go.th/dol-services/public-service-manual/land-registration/land-for-foreigners/?page=1"},
        {"label": "Department of Lands: fees and taxes", "url": "https://www.dol.go.th/en/dol-services/public-service-manual/land-registration/fees-taxes-duties/"},
        {"label": "BOI: Long-Term Resident programme", "url": "https://ltr.boi.go.th/"},
        {"label": "Department of Provincial Administration: Hotel Act", "url": "https://multi.dopa.go.th/legal/assets/modules/news/uploads/a8fec27695d5ecdb26fe0de8f70040fc5c00b4c6870cd0192022484170852251.pdf"},
        {"label": "Revenue Department: rental income", "url": "https://www.rd.go.th/english/6045.html"},
        {"label": "Revenue Department: statutory tax chapters", "url": "https://www.rd.go.th/english/37748.html"},
        {"label": "REIC: 2025 foreign condominium transfers", "url": "https://www.reic.or.th/News/RealEstate/470678"},
        {"label": "REIC: Q1 2026 secondary asking inventory", "url": "https://www.reic.or.th/Upload/260616-PressReleaseREIC-Q1-69-02_59769_1781663071_30035.pdf"},
        {"label": "Department of Mineral Resources: landslide susceptibility", "url": "https://gisportal.dmr.go.th/arcgis/rest/services/hazard/landslide_susceptibility/mapserver"},
        {"label": "Department of Mineral Resources: geohazard maps", "url": "https://www.dmr.go.th/map_service/geohazard_map/"},
        {"label": "Department of Mineral Resources: Phuket tsunami material", "url": "https://www.dmr.go.th/wp-content/uploads/2022/11/cartoontsunami.pdf"},
        {"label": "Thai Meteorological Department: monthly climate summaries", "url": "https://tmd.go.th/en/climate/summarymonthly"},
        {"label": "Phuket International Airport", "url": "https://phuket.airportthai.co.th/?lang=en"},
        {"label": "Samui Airport", "url": "https://www.samuiairport.com/en/"},
        {"label": "Bangkok Hospital Phuket: important contacts", "url": "https://www.bangkokhospital.com/en/phuket/visit/important-telephone-numbers"},
        {"label": "Koh Samui municipality: water resources", "url": "https://www.kohsamuicity.go.th/content/resource"},
        {"label": "Koh Samui municipality: wastewater", "url": "https://www.kohsamuicity.go.th/news/detail/78559/data.html"},
        {"label": "Rawai condominium asking observation", "url": "https://www.fazwaz.com/property-sales/2-bedroom-condo-for-sale-at-selina-serenity-resort-residences-in-rawai-phuket-u1944488"},
        {"label": "Si Sunthon villa asking observation", "url": "https://www.fazwaz.com/property-sales/4-bedroom-villa-for-sale-at-manor-phuket-in-si-sunthon-phuket-u6144306"},
        {"label": "Maenam villa asking observation", "url": "https://www.fazwaz.com/property-sales/3-bedroom-villa-for-sale-in-maenam-surat-thani-u6076824"},
        {"label": "European Central Bank: euro reference rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("phuket-service-base", "/assets/phuket-koh-samui-phuket-service-base.webp", "Older residents walking through a shaded Phuket neighbourhood near shops and everyday services", "Phuket's strongest case is a practical year-round base with the coast nearby.", "hero"),
        DossierImage("monsoon-road", "/assets/phuket-koh-samui-monsoon-road.webp", "Wet-season road and tropical drainage beside homes in Phuket", "Monsoon access, drainage and slope conditions belong in the property file.", "wide"),
        DossierImage("samui-villa-life", "/assets/phuket-koh-samui-samui-villa-life.webp", "Mature couple on a shaded Koh Samui terrace overlooking a tropical residential hillside", "Samui's villa life is compelling when water, roads, healthcare and management are solved.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Phuket / Koh Samui through five destination lenses",
    assessment_intro="Here’s how Phuket / Koh Samui scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current observations show a Rawai foreign-quota condominium, a Si Sunthon company-structure villa and a Maenam villa. They are asking evidence—not valuations. Local THB is primary; USD uses the recorded ECB cross-rate basis.",
    market_anchors_intro="These official REIC figures establish market scale and broad asking context. They do not price a candidate, prove lawful use or create a Koh Samui villa index.",
    orientation_groups=(
        DossierOrientationGroup("Phuket service and coast corridors", (("Phuket Town / Wichit", "Hospitals and urban services"), ("Chalong / Rawai", "Southern resident coast"), ("Nai Harn", "Beach-led south"), ("Choeng Thale / Laguna", "Northwest international services"), ("Si Sunthon", "Inland villa growth"))),
        DossierOrientationGroup("Koh Samui north, east and south", (("Maenam", "Quieter north coast"), ("Bo Phut", "Airport-side services"), ("Chaweng", "Busiest east-coast hub"), ("Lamai", "Established southeast town"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current airport and ferry schedules, wet-season roads, hospital time, water and wastewater arrangements, and property-level access.",
    country_guide_url="/countries/thailand-property/",
    country_guide_label="Thailand property guide",
    rail_comparison="Compare Phuket / Koh Samui with the full Atlas.",
)


VANCOUVER_ISLAND_VICTORIA_DOSSIER = PremiumDossierSpec(
    destination_id="vancouver-island-victoria",
    title="Vancouver Island and Victoria Property Dossier for Foreign Buyers",
    description="Assess Vancouver Island and Victoria property through purchase eligibility, census geography, B.C. taxes, residence, healthcare, rentals, hazards, access, prices and resale.",
    h1="Vancouver Island / Victoria: legal access before island life",
    lede=(
        "Vancouver Island / Victoria offers a rare combination of English-language ease, serious healthcare, mild coastal living and year-round city services. Yet for a foreign buyer, the first map is legal rather than scenic. Most non-Canadians are prohibited from buying ordinary residential property inside a census metropolitan area or census agglomeration until January 1, 2027 unless an exception applies. The practical case therefore begins by proving who can buy what, and exactly where, before comparing Victoria, Sidney, Sooke or the central island."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-22",
    date_reviewed="2026-08-22",
    verdict_paragraphs=(
        "The verdict is conditional. Vancouver Island can be an excellent long-term home for a Canadian citizen, permanent resident or other buyer who clearly falls within a statutory exception. It is not presently an open residential market for most non-Canadians. The federal Prohibition on the Purchase of Residential Property by Non-Canadians Act has been extended through 1 January 2027. It generally catches detached houses, attached homes and condominium units in a census metropolitan area or census agglomeration, while property outside those Statistics Canada geographies is excluded from the regulation’s definition. The line is technical: a postal address, tourism label or agent’s description does not establish eligibility. Obtain a written Canadian legal opinion on the buyer, beneficial owners, property type and exact census geography before making an offer or paying a deposit.",
        "Eligibility does not make the transaction inexpensive. In the Capital Regional District, a foreign national or foreign corporation can face B.C.’s 20% additional property transfer tax on top of the ordinary graduated property transfer tax, unless an exemption applies. A foreign owner may also enter the federal Underused Housing Tax regime, an annual 1% tax with its own filing and exemption tests, and B.C.’s speculation and vacancy tax can apply at a 3% foreign-owner rate for the 2026 tax year. These regimes have different definitions and declarations. They must be checked separately rather than collapsed into a single ‘foreign-buyer tax’ estimate.",
        "For an eligible buyer who accepts those costs, the strongest pattern is a year-round base chosen for ordinary life, not a seasonal income story. Victoria Core offers the deepest hospitals, culture, transit and resale pool. Sidney and the Saanich Peninsula trade some urban depth for airport, ferry and gentler small-town living. Sooke offers space and coast at a longer driving distance, while Nanaimo, Parksville and Qualicum Beach broaden the island search beyond the Victoria metropolitan market. Establish residence and healthcare separately, test access in winter, and treat short-term rental, hazard and resale diligence as address-level work."
    ),
    lenses_intro="Five paired lenses turn the island idea into a buyer sequence: qualify legally, choose a daily-life geography, cost every tax and transport dependency, and preserve a credible exit.",
    lenses=(
        DossierLens(
            "Choose a place that still works on an ordinary Tuesday",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Victoria Core is the most complete retirement proposition on Vancouver Island. Downtown, James Bay, Fairfield, Oak Bay and adjacent neighbourhoods place groceries, culture, waterfront walks, specialists and public transport within a normal urban routine. Royal Jubilee Hospital and Victoria General Hospital give the capital region medical depth that a resort market rarely matches. The city is attractive without being dependent on a short summer season, and its relatively mild coastal winters support walking through much of the year. The trade-offs are high housing costs, wet and dark winter stretches, older strata buildings and a market where a pretty harbour view can obscure noise, wind, reserve-fund or accessibility problems.",
                "Sidney and the Saanich Peninsula offer a different version of ease. Sidney has a compact centre, level streets, shops, waterfront and proximity to Victoria International Airport and the Swartz Bay ferry terminal. It can suit a buyer who values calm daily life and regional connections over nightlife. Yet the peninsula is not one continuous walkable village. North Saanich and rural pockets often require a car, septic or well diligence and longer trips to major hospitals. Sooke pushes the trade further: dramatic coast, trails and more space, but a constrained road connection toward Victoria and greater dependence on driving, local services and property-level drainage or slope conditions.",
                "Central Island changes both lifestyle and legal geography. Nanaimo is a service city with ferries, an airport, healthcare and a resident economy; Parksville and Qualicum Beach offer established retirement communities and gentler beach life. They are not substitutes for Victoria Core: specialist care, flights, ferry routes, employment and buyer pools differ. Nor should a buyer assume that ‘outside Victoria’ means outside a census agglomeration. Confirm the exact Statistics Canada boundary first. After eligibility, spend two ordinary weeks in winter, complete the grocery, pharmacy and hospital journeys, and test whether the home remains workable if one household member stops driving."
            ),
        ),
        DossierLens(
            "Measure the island from the front door, not the brochure",
            ("global_access", "foreigner_fit"),
            (
                "Vancouver Island is connected, but every connection has a last mile. Victoria International Airport sits near Sidney, not downtown Victoria, and the drive can vary with traffic. Swartz Bay provides the principal vehicle-ferry route toward Metro Vancouver, while passenger and vehicle services from Nanaimo create a different access pattern for the central island. Ferries are bookable transport with schedules, fares, weather exposure and peak-period capacity constraints—not a bridge. A household planning frequent international travel should time the complete journey with luggage, a missed sailing and a late arrival, then compare it with living on the mainland.",
                "Within Greater Victoria, buses can support an urban or peninsula routine, but outer suburbs, Sooke and many rural or coastal homes are car-led. Highway 14 is the critical corridor toward Sooke; an incident, storm or construction can change a nominal commute. Farther north, the island highway links communities efficiently by Canadian standards, yet trips between Nanaimo, Parksville and Victoria are long enough to reshape hospital, airport and family access. Ask where the backup route is, how winter wind affects power and trees, and whether charging, fuel, roadside assistance and contractor capacity fit the property.",
                "English-language administration and familiar legal institutions improve foreigner fit, but they do not soften the purchase prohibition. A sophisticated local team should include a lawyer who understands the federal Act and its regulations, a B.C. tax adviser, an independent inspector and, where relevant, a strata specialist. Residence is another file. Canada offers permanent-residence pathways for eligible immigrants, but no general visa that grants retirement residence simply because a home was purchased. The practical sequence is immigration advice, purchase-eligibility advice, tax modelling and only then property search. Ease of communication makes diligence possible; it is not evidence that the answer will be yes."
            ),
            "island-access",
        ),
        DossierLens(
            "Prove purchase eligibility, then investigate the exact asset",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Canada’s land-registration system can provide clear title, but ownership clarity for a non-Canadian is presently dominated by eligibility. The federal rule covers a non-Canadian’s direct or indirect purchase of prescribed residential property in a census metropolitan area or census agglomeration, subject to defined exceptions. The regulations exclude property outside those geographies and provide exceptions for certain temporary residents, refugees, spouses or common-law partners and other cases. Definitions, control tests and transaction structure matter. Do not rely on a seller, developer or agent to decide them; obtain written advice tied to the actual parties and parcel.",
                "If eligible, calculate tax from the deed outward. B.C.’s ordinary property transfer tax is graduated by fair market value, with an additional residential rate above CAD 3 million. The 20% additional property transfer tax applies to foreign entities and taxable trustees acquiring residential property in specified areas including the Capital Regional District, subject to exemptions and refund rules. The federal Underused Housing Tax and B.C. speculation and vacancy tax are annual regimes with distinct ownership, use, filing and exemption tests. Municipality-level vacancy taxes and normal property tax may add another layer. A home occupied personally can still create filing work even where an exemption ultimately removes tax.",
                "Property diligence then divides into strata and detached-home files. For a strata apartment or townhouse, read the depreciation report, contingency reserve, budgets, insurance, deductibles, minutes, litigation, special levies, rental bylaws, age restrictions and accessibility. For a detached or rural home, verify title charges, survey, permits, additions, septic, well, oil tank, drainage, retaining walls, trees and insurability. Coastal and low-lying property needs flood and tsunami review; the wider island adds earthquake, wildfire, wind and landslide exposure. Use current provincial and local maps, but commission property-specific inspection and insurance quotations because a map category is not a condition report."
            ),
            "coastal-risk",
        ),
        DossierLens(
            "Underwrite long-term use before tourist income",
            ("rental_profit", "capital_upside"),
            (
                "The base rental case is ordinary housing demand, not nightly tourism. CMHC’s 2025 Victoria evidence reported a 3.3% purpose-built vacancy rate and an average two-bedroom rent of CAD 2,120; the condominium rental universe was tighter at 0.3% vacancy with an average two-bedroom rent of CAD 2,688. Those are market-level observations, not a forecast for a candidate. Strata bylaws, unit condition, parking, tenant rules, management cost and provincial tenancy law determine the actual result. Model a professional long-term tenancy after property tax, strata fees, insurance, maintenance, vacancy, tax compliance and a reserve for major repairs.",
                "Short-term rental is a constrained operating case. B.C.’s principal-residence requirement applies in many island communities including Victoria, Saanich, Sidney and Sooke and generally limits an operator to the principal residence plus one secondary suite or accessory dwelling unit. Local bylaws, business licences, strata rules and platform registration can be stricter. A second home bought for visitor accommodation may therefore have no lawful nightly-rental route. Before using any tourism revenue, obtain written confirmation for the exact address and operator, then deduct management, cleaning, utilities, consumables, platform fees, tax, insurance and seasonality. Treat zero nightly income as the default until every permission is proved.",
                "Capital upside is plausible only as a property-specific scenario. Victoria has constrained geography, institutions and a broad resident base, while Sidney, Sooke and retirement-oriented central-island communities offer different demand. Yet high entry costs, policy changes, interest rates and a narrower eligible foreign-buyer pool can offset scarcity. VREB’s July 2026 benchmark of CAD 1,311,000 for a Victoria Core single-family home and CAD 548,600 for a Core condominium describe matched product categories; B.C. Assessment’s CAD 786,000 typical Sooke single-family value is an assessment anchor dated July 1, 2025. None prices a candidate or guarantees appreciation."
            ),
        ),
        DossierLens(
            "Pay for a future buyer pool, not only a view",
            ("value_entry", "exit_liquidity"),
            (
                "The three asking observations below expose the danger of one island-wide price. A renovated Downtown Victoria strata apartment asks CAD 669,000 for 986 square feet of stated finished area. A new Sidney strata townhouse asks CAD 859,800 for 1,258 square feet. A large Sooke oceanfront strata townhouse asks CAD 1,098,000 for 2,933 square feet. Converted per-square-metre figures differ because the products, land relationship, age, location, services and common obligations differ. They are asking evidence—not valuations, completed transactions or proof that a non-Canadian may purchase them.",
                "Value entry begins with a matched set. Compare a candidate apartment with completed sales in the same building or immediate micro-market, then adjust for floor, exposure, parking, condition, reserve funding and levies. Compare a Sidney townhouse with similar completed new and resale product, warranty and strata burden. Compare a Sooke coastal home with lawful internal area, site, access, foreshore exposure, insurance and maintenance—not with a Victoria Core detached benchmark. Commission an independent valuation where the price or financing warrants it, and model currency movement because the household’s liabilities and future proceeds may be in CAD while wealth is elsewhere.",
                "Exit liquidity depends on who can legally and practically buy next. Victoria Core has the broadest local owner-occupier and rental-investor pool, but an older or weakly funded strata can still be difficult. Sidney’s retirement appeal is durable when the home is accessible and near services. Sooke and remote coast assets can take longer because driving, condition, insurance and taste narrow demand. Federal rules may change after January 1, 2027, but do not underwrite an exit on an assumed policy outcome. Ask two agents who did not source the property for completed evidence, likely buyer profile and realistic sale time; model a slow resale with full costs and no appreciation."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Victoria Core combines waterfront, culture and year-round services; Sidney, Sooke and Parksville trade urban depth for quieter coastal routines.",
        "global_access": "Victoria Airport and Swartz Bay support regional travel, while Sooke and central Vancouver Island add driving, ferry and disruption sensitivity.",
        "ownership_clarity": "Victoria title can be clear, but most non-Canadians face a federal purchase prohibition whose answer depends on buyer, property and census geography.",
        "regulatory_safety": "Victoria, Sidney and Sooke restrict short stays through the provincial principal-residence rule, while hazards and strata obligations remain address-specific.",
        "rental_profit": "Victoria has credible long-term demand, but property tax, strata, insurance and tenancy costs constrain yield; second-home nightly rent may be unavailable.",
        "capital_upside": "Victoria Core scarcity supports selected assets, while Sooke and central-island appreciation depends more heavily on access, condition and the local buyer pool.",
        "retirement_fit": "Victoria offers the island’s deepest hospitals and services; Sidney is practical, while Sooke, Nanaimo and Parksville require different transport and care planning.",
        "exit_liquidity": "Victoria Core reaches the broadest resident pool; specialised Sooke waterfront and remote Vancouver Island homes can take longer to resell.",
        "foreigner_fit": "English-language ease helps administration, but Victoria-area purchase restrictions, stacked taxes and residence rules materially narrow the foreign-buyer case.",
        "value_entry": "Downtown Victoria, Sidney and Sooke asking evidence spans unlike strata products, so matched completed sales matter more than one island average.",
    },
    market_anchors=(
        {"location": "Victoria Core single-family", "evidence": "1,311,000 CAD", "buyer_read": "July 2026 VREB HPI benchmark for a matched single-family category; not an asking price or candidate valuation.", "source_label": "Victoria Real Estate Board current statistics", "source_url": "https://www.vreb.org/current-statistics"},
        {"location": "Victoria Core condominium", "evidence": "548,600 CAD", "buyer_read": "July 2026 VREB HPI benchmark for a matched condominium category; building condition and strata finances still control a candidate.", "source_label": "Victoria Real Estate Board current statistics", "source_url": "https://www.vreb.org/current-statistics"},
        {"location": "Sooke typical single-family", "evidence": "786,000 CAD", "buyer_read": "B.C. Assessment 2026 roll typical assessed value as of July 1, 2025; not a completed-sale median or candidate valuation.", "source_label": "B.C. Assessment Vancouver Island 2026", "source_url": "https://info.bcassessment.ca/news/Pages/Vancouver-Island-2026-Property-Assessments-Announced.aspx"},
    ),
    micro_locations_intro="Use these four operating patterns only after legal geography is confirmed. Victoria Core, the Saanich Peninsula, Sooke and Central Island differ in hospitals, transport, property type, hazards and the future buyer pool.",
    micro_locations=(
        {"name": "Victoria Core", "best_for": "Deepest services, hospitals and walkability", "daily_life": "Urban neighbourhoods, transit, waterfront and broad resident demand", "diligence": "Purchase eligibility, strata finances, noise, seismic work and taxes"},
        {"name": "Sidney / Saanich Peninsula", "best_for": "Calm small-town retirement near airport and ferry", "daily_life": "Walkable Sidney centre with car-led rural peninsula beyond", "diligence": "Census geography, hospital time, septic or well, strata and coastal risk"},
        {"name": "Sooke / West Shore", "best_for": "More space and dramatic southwest coast", "daily_life": "Car-led living with Highway 14 dependence and local services", "diligence": "Road resilience, drainage, slope, tsunami, insurance and resale depth"},
        {"name": "Central Island: Nanaimo / Parksville / Qualicum", "best_for": "Retirement communities with a separate service hub", "daily_life": "Nanaimo ferries and healthcare; smaller beach towns farther north", "diligence": "Exact CMA or CA boundary, specialist care, transport, wildfire and exit pool"},
    ),
    checklist=(
        "Obtain written advice on the buyer, beneficial owners, property type and exact CMA or CA geography before offering.",
        "Confirm residence, tax residence and MSP healthcare eligibility separately from ownership.",
        "Calculate ordinary property transfer tax, the 20% additional tax, UHT, speculation and vacancy tax, and annual filings separately.",
        "For strata, read depreciation reports, minutes, insurance, deductibles, levies, bylaws, litigation and accessibility.",
        "For detached or rural homes, verify permits, survey, septic, well, oil tank, drainage, trees, access and insurability.",
        "Overlay earthquake, tsunami, flood, wildfire and landslide sources; obtain property-specific inspection and insurance terms.",
        "Assume zero nightly income until provincial, municipal, strata and operator requirements are confirmed in writing.",
        "Model winter transport, five-year cash outlay, currency risk and a slow resale to the next eligible buyer.",
    ),
    references_intro="Legal, tax, residence, healthcare, rental, hazard, transport, market and listing claims were reviewed on 22 August 2026. Recheck immediately after a purchase-ban, tax, short-term rental, transport, hazard, market-data or listing change, and in all cases before a binding offer. Obtain Canadian legal, tax, immigration, inspection, insurance and strata advice for the actual buyer and property.",
    references=(
        {"label": "CMHC: Prohibition on Purchase of Residential Property by Non-Canadians", "url": "https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/consultations/prohibition-purchase-residential-property-non-canadians-act"},
        {"label": "Justice Laws: enacted extension to the fourth anniversary", "url": "https://laws-lois.justice.gc.ca/eng/AnnualStatutes/2024_17/page-15.html"},
        {"label": "Justice Laws: purchase-prohibition regulations section 3", "url": "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2022-250/section-3.html"},
        {"label": "Canada Revenue Agency: Underused Housing Tax", "url": "https://www.canada.ca/en/services/taxes/excise-taxes-duties-and-levies/underused-housing-tax.html"},
        {"label": "B.C.: additional property transfer tax", "url": "https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax/additional-property-transfer-tax"},
        {"label": "B.C.: property transfer tax rates", "url": "https://www2.gov.bc.ca/gov/content?id=B6F43B3AAE394299B03B1F777747A36F"},
        {"label": "B.C.: speculation and vacancy tax rates", "url": "https://www2.gov.bc.ca/gov/content/taxes/speculation-vacancy-tax/how-tax-works/tax-rates?keyword=2023"},
        {"label": "B.C.: short-term rental principal-residence requirement", "url": "https://www2.gov.bc.ca/gov/content/housing-tenancy/short-term-rentals/principal-residence-requirement"},
        {"label": "IRCC: immigrate to Canada", "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada.html"},
        {"label": "B.C.: MSP eligibility", "url": "https://www2.gov.bc.ca/gov/content/health/health-drug-coverage/msp/bc-residents/eligibility-and-enrolment/are-you-eligible"},
        {"label": "B.C.: MSP coverage wait period", "url": "https://www2.gov.bc.ca/gov/content/health/health-drug-coverage/msp/bc-residents/eligibility-and-enrolment/how-to-enrol/coverage-wait-period"},
        {"label": "Island Health: Royal Jubilee Hospital", "url": "https://www.islandhealth.ca/locations/hospitals-health-centre-locations/royal-jubilee-hospital-rjh"},
        {"label": "Island Health: specialized intensive-care sites", "url": "https://www.islandhealth.ca/services/hospital-services/adult-intensive-care-units-icu"},
        {"label": "PreparedBC: earthquakes and tsunamis", "url": "https://www2.gov.bc.ca/gov/content/safety/emergency-management/preparedbc/know-your-hazards/earthquakes-tsunamis/tsunami"},
        {"label": "PreparedBC: landslide preparedness", "url": "https://www2.gov.bc.ca/gov/content?id=673B4BF9FE304FA9AC218B0D30D5762B"},
        {"label": "B.C. flood hazard map", "url": "https://governmentofbc.maps.arcgis.com/apps/webappviewer/index.html?id=1a60c24b82ed41699d8a55338fb11076"},
        {"label": "BC Wildfire Service: Provincial Strategic Threat Analysis", "url": "https://www2.gov.bc.ca/gov/content/safety/wildfire-status/prevention/fire-fuel-management/psta"},
        {"label": "B.C.: Highway 14 corridor", "url": "https://www2.gov.bc.ca/gov/content/transportation-projects/other-transportation-projects/highway-14"},
        {"label": "BC Transit: Victoria schedules and route maps", "url": "https://www.bctransit.com/victoria/schedules-and-maps/"},
        {"label": "BC Ferries route map", "url": "https://www.bcferries.com/routes-fares/discover-route-map"},
        {"label": "BC Ferries fares and bookings", "url": "https://www.bcferries.com/routes-fares/ferry-fares"},
        {"label": "Victoria International Airport", "url": "https://www.victoriaairport.com/"},
        {"label": "CMHC: 2025 rental market reports", "url": "https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/market-reports/rental-market-reports-major-centres"},
        {"label": "Victoria Real Estate Board current statistics", "url": "https://www.vreb.org/current-statistics"},
        {"label": "B.C. Assessment: Vancouver Island 2026 assessments", "url": "https://info.bcassessment.ca/news/Pages/Vancouver-Island-2026-Property-Assessments-Announced.aspx"},
        {"label": "Downtown Victoria asking observation", "url": "https://www.realtor.ca/real-estate/30169955/403-1015-johnson-st-victoria-downtown"},
        {"label": "Sidney asking observation", "url": "https://www.realtor.ca/real-estate/29877007/2-2312-orchard-ave-sidney-sidney-south-east"},
        {"label": "Sooke asking observation", "url": "https://www.realtor.ca/real-estate/29896327/3-6995-nordin-rd-sooke-whiffin-spit"},
        {"label": "European Central Bank euro reference rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
    ),
    images=(
        DossierImage("victoria-daily-life", "/assets/vancouver-island-victoria-daily-life.webp", "Older couple walking beside Victoria harbour near a lived-in waterfront neighbourhood", "Victoria’s case begins with year-round city life, hospitals and a waterfront that works beyond summer.", "hero"),
        DossierImage("island-access", "/assets/vancouver-island-victoria-island-access.webp", "Coastal ferry approaching Vancouver Island through calm grey water", "Ferries and airports connect the island, but schedules and last-mile travel shape daily life.", "wide"),
        DossierImage("coastal-risk", "/assets/vancouver-island-victoria-coastal-risk.webp", "Rain-wet coastal road beside forest and homes near Sooke on Vancouver Island", "A scenic coast still needs road, drainage, wind, flood and emergency-access diligence.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Vancouver Island / Victoria through five destination lenses",
    assessment_intro="Here’s how Vancouver Island / Victoria scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three direct current observations compare a Downtown Victoria apartment, a Sidney townhouse and a Sooke oceanfront townhouse. They are asking evidence—not valuations. Finished internal area is used consistently; CAD is primary and USD uses the recorded ECB cross-rate.",
    market_anchors_intro="These official VREB and B.C. Assessment figures bound distinct matched products. They are context—not candidate valuations, listing medians or a single island price.",
    orientation_groups=(DossierOrientationGroup("South to Central Island", (("Victoria Core", "Hospitals, culture and transit"), ("Sidney / Saanich", "Airport, ferry and small-town life"), ("Sooke / West Shore", "Coast and car-led access"), ("Nanaimo", "Central-island service hub"), ("Parksville / Qualicum", "Retirement-oriented beach towns"))),),
    orientation_caption="Orientation schematic—not to scale. Confirm current census geography, ferry and airport schedules, hospital time, road resilience, hazards and property-level access.",
    country_guide_url="/countries/canada-property/",
    country_guide_label="Canada property guide",
    rail_comparison="Compare Vancouver Island / Victoria with the full Atlas.",
)


DUBAI_DOSSIER = PremiumDossierSpec(
    destination_id="dubai",
    title="Dubai Property Dossier for Foreign Buyers | Global Home Atlas",
    description="Assess Dubai property through designated freehold ownership, residence, service charges, completed-asset diligence, licensed letting, heat resilience, value and resale depth.",
    h1="Dubai: buy the finished asset, not the promise",
    lede=(
        "Dubai is one of the world’s most accessible property markets for an international buyer, but access is not the same as simplicity. Foreign nationals can own in designated freehold areas, the registration path is well defined, and resident, tenant and visitor demand is substantial. The harder decision is which completed building, service-charge burden and daily-life pattern will remain useful through summer and credible on resale. This dossier separates that durable case from the promotional one."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-23",
    date_reviewed="2026-08-23",
    verdict_paragraphs=(
        "The verdict is positive for a selective buyer, with one controlling rule: choose the completed asset and its operating record before choosing a future story. The Dubai Land Department says foreigners may own freehold property in areas designated for foreign ownership, and every sale must be registered. That is unusually clear access. It does not remove the need to verify the title, seller, developer, building-management record, service-charge statement, permitted use, parking, defects and resale comparables. Nor does a purchase itself create residence. The UAE Golden visa route for real-estate investors has a separate AED 2 million eligibility threshold and application process; a deed below or above that figure is not automatic approval. Establish the household’s lawful residence, insurance and banking route independently.",
        "Dubai best suits a buyer who values global air access, English-language professional services, strong year-round urban infrastructure and the ability to choose between dense waterfront living and newer inland neighbourhoods. It can work for an owner-occupier who accepts an air-conditioned summer routine, or for an investor who underwrites ordinary residential demand before adding licensed holiday-home income. It is weaker for anyone who needs effortless outdoor life throughout the year, assumes every new tower carries equal quality, depends on an unverified off-plan completion date, or treats a headline gross yield as spendable income. A high service charge, frequent furnishing replacement, vacancy and management can transform an attractive brochure return.",
        "Proceed in order. First choose the daily-life pattern: Downtown Dubai and Business Bay, Dubai Marina and JBR, Palm Jumeirah, or Dubai Hills Estate. Then confirm residence and health insurance, cash and financing, title and designated-freehold status. For a completed unit, read the DLD record, building accounts, RERA-approved service charge, maintenance history and recent completed transactions. For any off-plan alternative, verify the developer, project status, escrow record, payment schedule, cancellation rights and realistic handover risk through DLD data and independent counsel. Only after that should rent, appreciation or Golden visa eligibility enter the decision."
    ),
    lenses_intro=(
        "Dubai becomes easier to judge when ten factors are paired into five practical questions. The narrative below explains the trade-offs; the complete Atlas assessment appears once in the score table that follows."
    ),
    lenses=(
        DossierLens(
            "Build a life that still works in August",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Dubai’s attraction is not only spectacle. Downtown Dubai and Business Bay offer restaurants, offices, groceries, pharmacies and urban services close together; Dubai Marina and JBR combine apartment living with a promenade, beach and rail connections; Palm Jumeirah provides resort-like waterfront seclusion; Dubai Hills Estate offers newer parks, schools, clinics and family-scale housing farther inland. These are meaningfully different lives. A waterfront tower can be walkable within its immediate district but frustrating for cross-city errands. A villa can offer privacy and shade while making almost every useful trip dependent on a car. The decision should begin with an ordinary Tuesday, not a weekend view.",
                "Climate is the main lifestyle constraint. Dubai’s cooler months make outdoor exercise, terraces and beach life unusually pleasant, but summer heat changes the operating model. Dubai Health Authority guidance treats heatstroke as a serious risk and identifies older people among vulnerable groups. Test shaded access from the front door to parking, taxi or Metro; indoor walking options; cooling reliability; balcony usability; pool and common-area maintenance; and the cost of running air conditioning through the hottest period. Dubai Hills’ greenery, Marina’s promenade and Downtown’s connected buildings are not interchangeable forms of resilience. A retirement home should remain convenient when outdoor time contracts.",
                "Healthcare depth is a strength, but access is administrative and financial rather than created by property ownership. Dubai’s government portal says health insurance is mandatory, with employers responsible for employees and sponsors responsible for dependants. The emirate has a substantial public and private care network, yet provider access, policy limits, exclusions and ongoing premiums still need buyer-specific checking. Before choosing Palm Jumeirah isolation or a Dubai Hills villa, map routine and specialist care at peak traffic. If one household member stops driving, test the replacement routine. The best retirement asset is the one that preserves daily independence, not simply the one with the most dramatic address."
            ),
            "summer-shade",
        ),
        DossierLens(
            "Use global access without ignoring the last mile",
            ("global_access", "foreigner_fit"),
            (
                "Dubai International Airport is a structural advantage. Dubai Airports reported 95.2 million guests in 2025, evidence of the network’s scale rather than a promise that every itinerary is simple. Downtown Dubai and Business Bay have relatively direct airport road and Metro access. Dubai Marina and JBR sit much farther west but benefit from Metro and tram connections. Palm Jumeirah adds monorail, taxi and road dependence. Dubai Hills Estate is closer to major roads than to a walk-up rail station. Measure door-to-gate travel at the hours the household will actually fly, including luggage, interchange, parking and the return trip after a long journey.",
                "Within the city, the Metro is useful where the home, workplace and routine destinations align with it. It does not make the whole emirate car-free. A Business Bay apartment can sit an uncomfortable walk from the nearest station; a Marina tower can be close to rail yet slow to exit by road; Palm Jumeirah’s fronds magnify last-mile time; and Dubai Hills’ internal distances favour a car. Walk the route in daytime heat and after dark, not only on a map. Check taxi availability, visitor parking, delivery access, road noise and construction detours. Access scores well because Dubai offers alternatives, but address-level friction remains decisive.",
                "Foreigner fit is high because the market, banking, brokerage and professional-services ecosystem routinely serves international clients. English is widely used in commercial transactions, but the legal and administrative framework remains local. Use a DLD-registered broker, independently appointed conveyancing lawyer, qualified tax adviser and building inspector. Verify the title and seller through official channels; do not rely on a screenshot forwarded by an agent. Cross-border buyers should also plan currency transfers, sanctions and source-of-funds checks, estate planning, powers of attorney and document legalisation before the payment deadline. Operational familiarity makes Dubai approachable; it should not make the buyer casual."
            ),
            "metro-access",
        ),
        DossierLens(
            "Own in the right zone—and audit the building",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Ownership clarity begins with geography. DLD’s guidance permits foreign freehold ownership in designated areas, so a marketing name or view is not enough: confirm the exact plot, unit and title classification. DLD’s sale-registration service sets out the passport, electronic no-objection certificate and fee process and lists residency status as open to all. It also states a 2% registration fee for the seller and 2% for the buyer, plus trustee, title and map charges where applicable. Obtain a current completion statement for the actual transaction rather than applying a single percentage to every property or corporate structure.",
                "For a jointly owned building, service charges are part of the asset, not a footnote. DLD directs owners to the RERA-approved Service Charge Index and Mollak system. Request the current approved charge, unit account, arrears, reserve position, insurance, maintenance contracts, owners’ records and history of major work. Compare lifts, chilled-water arrangements, cooling allocation, façade and waterproofing, fire systems, parking, pools and common areas. In Dubai Marina and Business Bay, two similar-looking towers can have very different governance and operating costs. On Palm Jumeirah, waterfront exposure and specialist amenities increase the questions. A low asking price can be the market’s estimate of a building problem.",
                "Intended use must also be cleared. Dubai regulates holiday homes through a licensing and permitting framework; a residential title or active online listing does not itself prove that a particular unit, operator and stay pattern comply. Verify the current tourism classification, permit, building rules, management contract and tax treatment before adding short-term income. The Federal Tax Authority distinguishes residential real estate from commercial and serviced accommodation, with different VAT treatment, so obtain property-specific advice. For off-plan property, check DLD project, developer and escrow data, construction progress and contractual remedies. Regulatory safety is strongest in a completed, documented building with an ordinary-use case."
            ),
        ),
        DossierLens(
            "Underwrite resident demand before tourist demand",
            ("rental_profit", "capital_upside"),
            (
                "Dubai has genuine demand depth. DLD reported 1.38 million registered tenancy contracts in 2025 with a total value of AED 126.4 billion. That is system-wide evidence, not a forecast for a particular unit. A completed Business Bay apartment can reach office-linked residents; Dubai Marina and JBR attract tenants seeking waterfront and rail access; Dubai Hills can appeal to longer-stay households wanting newer community infrastructure. Palm Jumeirah competes in a higher-cost, more discretionary segment. Start with documented long-term asking and achieved rents in the same tower or community, then deduct vacancy, agent fees, management, maintenance, cooling, insurance, service charge and periodic refurbishment.",
                "Holiday-home demand can add flexibility, but it turns the home into a hospitality operation. Model licensing, platform fees, cleaning, linen, utilities, consumables, guest support, furnishing wear, seasonal pricing, management and neighbour or building restrictions. Ask who holds the permit and controls the listing history if an operator is involved. Compare three cases: a conventional annual tenancy, a compliant licensed holiday-home operation, and no income. If the purchase only works under the most optimistic case, it is not a resilient retirement or investment asset. A professionally staged gross-yield claim is not a substitute for bank statements, contracts and actual operating expenses.",
                "Capital upside should be treated as an asset-selection scenario. DLD’s 2025 summary recorded 147,500 units sold and 937 projects under construction, illustrating both market depth and a large supply pipeline. Population, aviation and business growth can support established districts, but new launches continually compete for attention. A buyer paying a launch premium assumes developer execution, completion, future service charges and resale demand against newer inventory. A completed unit with a proven view, sensible layout, manageable charge and broad tenant pool may be less exciting but easier to evaluate. Never use Dubai’s citywide growth as a guarantee for a compromised building or price."
            ),
        ),
        DossierLens(
            "Price the exact asset—and know the next buyer",
            ("value_entry", "exit_liquidity"),
            (
                "The official 2024 DLD report gives a useful broad baseline: average residential apartment value of 19,138 AED/m² and average villa value of 14,617 AED/m². Those figures cover broad market activity, including both ready and off-plan segments; they do not value a candidate, establish a 2026 asking price or make an apartment directly comparable with a villa. The three direct asking observations below deliberately span Business Bay, Dubai Marina and Dubai Hills Estate. Their dispersion reflects location, building, view, age, size and property type. Reconcile each candidate with recent completed transactions in the same building or tightly matched community before negotiating.",
                "Value entry comes from refusing the wrong premium. In Downtown Dubai and Business Bay, distinguish a genuinely useful location from a skyline label, and price traffic, construction, layout and service charge. In Dubai Marina and JBR, test view protection, road access, tower governance and waterfront maintenance. On Palm Jumeirah, separate beachfront scarcity from dated fit-out, exposure and high recurring costs. In Dubai Hills Estate, compare mature sections with ongoing construction and verify the exact built-up area, plot, community fee and route to daily services. A cheaper AED/m² figure can still be poor value when the operating burden and buyer pool are weak.",
                "Exit liquidity depends on the future audience. A well-managed one- or two-bedroom apartment in a recognised completed tower can appeal to residents, investors and international buyers. An unusual layout, extreme service charge, poor parking or unresolved defect narrows that pool. A large Palm or Dubai Hills home may be scarce but requires a buyer with the right budget, taste and carrying-cost tolerance. Model a five-year sale under flat, weaker and stronger market conditions, including registration, finance, maintenance, furnishing, management, vacancy and selling costs. Before committing, ask two brokers who did not source the unit for completed comparables and an evidence-based resale strategy."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Dubai combines Downtown energy, Marina waterfront life and Dubai Hills greenery, but summer moves much of daily life indoors.",
        "global_access": "DXB provides exceptional global reach; Marina, Palm Jumeirah and Dubai Hills each add distinct road, rail and last-mile trade-offs.",
        "ownership_clarity": "DLD registration and designated freehold areas provide clear access, while title, seller, service charges and project status remain asset-specific.",
        "regulatory_safety": "Dubai holiday-home permits, DLD project records, Mollak charges and building rules require written checks before income or completion assumptions.",
        "rental_profit": "Business Bay and Dubai Marina have resident demand, but service charges, vacancy, furnishing and licensed-operation costs reduce headline returns.",
        "capital_upside": "Dubai’s growth and transaction depth support selected completed assets, while 937 projects under construction keep supply and execution risk high.",
        "retirement_fit": "Dubai offers healthcare, services and security, but mandatory insurance, severe summer heat and car dependence shape long-term suitability.",
        "exit_liquidity": "Recognised completed Dubai towers reach broad buyer pools; high charges, defects, unusual layouts and promotional pricing weaken resale depth.",
        "foreigner_fit": "Dubai’s international ecosystem is accessible, yet DLD verification, local legal advice, banking and source-of-funds preparation remain essential.",
        "value_entry": "Downtown, Marina, Palm Jumeirah and Dubai Hills occupy different price bands; value depends on completed evidence and recurring cost.",
    },
    market_anchors=(
        {"location": "Dubai residential apartments", "evidence": "19,138 AED/m²", "buyer_read": "DLD’s broad 2024 apartment series includes ready and off-plan activity; it is not filtered to a matched completed candidate, 2026 valuation or building comparable.", "source_label": "Dubai Land Department 2024 annual report", "source_url": "https://backoffice.dubailand.gov.ae/en/open-data/research/annual-report-real-estate-sector-performance-2024/"},
        {"location": "Dubai residential villas", "evidence": "14,617 AED/m²", "buyer_read": "DLD’s broad 2024 villa series includes ready and off-plan activity; it is not filtered to a matched completed candidate, and area basis, community and condition still require matching.", "source_label": "Dubai Land Department 2024 annual report", "source_url": "https://backoffice.dubailand.gov.ae/en/open-data/research/annual-report-real-estate-sector-performance-2024/"},
        {"location": "Dubai registered tenancy market", "evidence": "1.38 million contracts", "buyer_read": "DLD’s 2025 registered tenancy total across the emirate; it is demand context, not rent or occupancy evidence for a candidate.", "source_label": "Dubai Land Department 2025 rental-sector release", "source_url": "https://backoffice.dubailand.gov.ae/en/news-media/dubai-s-rental-sector-records-strong-growth-in-2025-underscoring-market-stability-and-the-strength-of-the-emirate-s-real-estate-ecosystem/"},
    ),
    micro_locations_intro=(
        "Dubai is not one interchangeable freehold market. These four patterns describe daily life and diligence rather than price zones; verify the exact plot, title, building, service charge, route and nearby construction for every candidate."
    ),
    micro_locations=(
        {"name": "Downtown Dubai / Business Bay", "best_for": "Central urban life", "daily_life": "Offices, services and Metro access with traffic variation", "diligence": "Tower record, construction, layout, parking and service charge"},
        {"name": "Dubai Marina / JBR", "best_for": "Waterfront apartment living", "daily_life": "Promenade, beach, tram and Metro within a dense district", "diligence": "Road access, tower governance, view protection and cooling"},
        {"name": "Palm Jumeirah", "best_for": "Premium resort-style ownership", "daily_life": "Waterfront seclusion with higher road and operating dependence", "diligence": "Exposure, recurring costs, fit-out, access and buyer-pool depth"},
        {"name": "Dubai Hills Estate", "best_for": "Newer family-scale living", "daily_life": "Parks, schools and villas in a more car-led community", "diligence": "Built-up area, plot, construction phase, fees and daily routes"},
    ),
    checklist=(
        "Confirm the household’s residence, health-insurance, banking and estate-planning routes independently of the purchase.",
        "Verify that the exact plot and unit carry the intended designated-freehold title through DLD records.",
        "Choose the Downtown, Marina, Palm or Dubai Hills daily-life pattern before comparing finishes.",
        "For a completed asset, inspect condition, defects, cooling, parking, insurance and the building-management record.",
        "Obtain the RERA-approved service charge, unit account, reserve information and history of major work.",
        "For off-plan alternatives, verify developer, project, escrow, progress, payment, cancellation and handover evidence.",
        "Clear long-term or licensed holiday-home use, management, tax and building rules in writing before pricing income.",
        "Reconcile completed transactions and model five-year carrying and resale costs before making a binding offer.",
    ),
    references_intro=(
        "Legal, administrative, market, health, climate, transport and listing claims were reviewed on 23 August 2026. Recheck every time-sensitive source and obtain UAE legal, tax, immigration, building, insurance and finance advice for the exact buyer and asset before signing. Listing observations are dated asking evidence only; they do not verify availability, title, condition, negotiability or completed value."
    ),
    references=(
        {"label": "Dubai Land Department: foreign ownership and registration FAQ", "url": "https://dubailand.gov.ae/en/frequently-asked-questions"},
        {"label": "Dubai Land Department: property sale registration", "url": "https://dubailand.gov.ae/en/eservices/property-sale-registration/"},
        {"label": "Dubai Land Department: open real-estate data", "url": "https://dubailand.gov.ae/en/open-data/real-estate-data/"},
        {"label": "Dubai Land Department: 2024 annual real-estate report", "url": "https://backoffice.dubailand.gov.ae/en/open-data/research/annual-report-real-estate-sector-performance-2024/"},
        {"label": "Dubai Land Department: 2025 rental-sector statistics", "url": "https://backoffice.dubailand.gov.ae/en/news-media/dubai-s-rental-sector-records-strong-growth-in-2025-underscoring-market-stability-and-the-strength-of-the-emirate-s-real-estate-ecosystem/"},
        {"label": "Dubai Land Department: Service Charge Index guide", "url": "https://dubailand.gov.ae/media/vkcojy4z/service_charge_index_en.pdf"},
        {"label": "Dubai Land Department: Know Your Rights", "url": "https://dubailand.gov.ae/media/wlzmuycr/know_your_rights.pdf"},
        {"label": "UAE Government: Golden visa", "url": "https://u.ae/en/information-and-services/visa-and-emirates-id/residence-visas/golden-visa"},
        {"label": "Dubai legislation: Holiday Homes Decree 41 of 2013", "url": "https://dlp.dubai.gov.ae/Legislation%20Reference/2013/Decree%20No.%20%2841%29%20of%202013.html"},
        {"label": "Dubai legislation: Holiday Homes Administrative Resolution 1 of 2020", "url": "https://dlp.dubai.gov.ae/Legislation%20Reference/2020/Administrative%20Resolution%20No.%20%281%29%20of%202020.html"},
        {"label": "Federal Tax Authority: VAT real-estate guide", "url": "https://tax.gov.ae/DownloadOpenTextFile?fileUrl=en%2FVAT_VAT_Guides%2FReal_Estate_Guide%2FReal_Estate_Guide_VATGRE1_EN_19_04_2021_EN.pdf"},
        {"label": "Dubai Government: healthcare and mandatory insurance", "url": "https://www.dubai.ae/en/web/dubai.ae/healthcare"},
        {"label": "Dubai Health Authority: summer health guide", "url": "https://www.dha.gov.ae/uploads/072025/Summer%20guide_EN2025751189.pdf"},
        {"label": "Dubai Airports: main fact file", "url": "https://media.dubaiairports.ae/dubai-airports-main-fact-file/"},
        {"label": "Dubai RTA: Metro and tram stations map", "url": "https://www.rta.ae/wps/portal/rta/ae/public-transport/metro-stations-map"},
        {"label": "Dubai RTA: public transport overview", "url": "https://rta.ae/wps/portal/rta/ae/public-transport"},
        {"label": "Dubai Media Office: April 2024 extreme-weather response", "url": "https://www.mediaoffice.ae/en/news/2024/april/19-04/rta-and-dm"},
        {"label": "Dubai Media Office: Tasreef rainwater-drainage project", "url": "https://www.mediaoffice.ae/en/news/2024/june/24-06/mohammed-bin-rashid-approves-aed30-billion-tasreef-project"},
        {"label": "Central Bank of the UAE: domestic market operations and dirham peg", "url": "https://centralbank.ae/en/our-operations/monetary-policy-and-domestic-markets/domestic-market-operations/"},
        {"label": "Business Bay completed apartment asking observation", "url": "https://www.propertyfinder.ae/en/plp/buy/apartment-for-sale-dubai-business-bay-the-bay-128807897.html"},
        {"label": "Dubai Marina completed apartment asking observation", "url": "https://www.propertyfinder.ae/en/plp/buy/apartment-for-sale-dubai-dubai-marina-5242-5242-tower-2-129312973.html"},
        {"label": "Dubai Hills completed villa asking observation", "url": "https://www.propertyfinder.ae/en/plp/buy/villa-for-sale-dubai-dubai-hills-estate-maple-at-dubai-hills-estate-maple-at-dubai-hills-estate-2-131537797.html"},
    ),
    images=(
        DossierImage("waterfront-life", "/assets/dubai-waterfront-daily-life.webp", "Everyday waterfront life in Dubai Marina", "Dubai Marina / JBR: a waterfront routine with real transport and tower trade-offs.", "hero"),
        DossierImage("metro-access", "/assets/dubai-metro-city-access.webp", "Dubai Metro passing through the city", "Global access is excellent; the last mile still changes by address.", "wide"),
        DossierImage("summer-shade", "/assets/dubai-hills-summer-shade.webp", "Shaded pedestrian life in Dubai Hills Estate", "Summer suitability depends on shade, cooling, services and short daily routes.", "wide"),
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
    lenses_heading="Dubai through five destination lenses",
    assessment_intro="Here’s how Dubai scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three completed asking observations show the spread between Business Bay, Dubai Marina and Dubai Hills Estate. They are asking evidence—not valuations. The apartment sources label size only as Area, and the villa page conflicts on built-up area; local price is primary and USD uses the recorded CBUAE exchange basis.",
    market_anchors_intro="The official apartment, villa and tenancy figures provide broad context, not candidate pricing. Match property type, completion, district, building, size and condition before drawing a conclusion.",
    orientation_groups=(
        DossierOrientationGroup(
            "Urban waterfront to inland",
            (
                ("Downtown Dubai / Business Bay", "Central and dense"),
                ("Dubai Marina / JBR", "Waterfront and rail-linked"),
                ("Palm Jumeirah", "Premium and road-dependent"),
                ("Dubai Hills Estate", "Newer, greener and car-led"),
            ),
        ),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm the exact road, Metro, tram and walking route for every address.",
    country_guide_url="/countries/united-arab-emirates-property/",
    country_guide_label="United Arab Emirates property guide",
    rail_comparison="Compare Dubai with the full Atlas.",
)


BALI_DOSSIER = PremiumDossierSpec(
    destination_id="bali",
    title="Bali Retirement Property Dossier for Foreign Buyers",
    description="Assess Bali property through foreign land rights, leasehold, residence, villa licensing, daily life, hazards, value decay, exit and current listings.",
    h1="Bali: buy the legal interest, not the dream",
    lede=(
        "Bali can support an exceptional long-stay life, but the island’s property language is dangerously compressed. A villa advertised as ‘leasehold,’ ‘freehold’ or ‘investment ready’ may involve very different land rights, remaining terms, permits and operating permissions. Sanur, Ubud, Canggu and Uluwatu also solve different daily-life problems. This dossier starts with the legal interest and the life it must support, then tests licensing, infrastructure, hazards, cash flow and what a future buyer will actually acquire."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-23",
    date_reviewed="2026-08-23",
    verdict_paragraphs=(
        "The verdict is conditional. Bali is suitable for a buyer who accepts that Hak Milik freehold land is reserved to Indonesian citizens and who will not use an Indonesian nominee as a substitute. Government Regulation 18/2021 permits qualifying foreigners with immigration documents to own specified residential property through defined rights, including landed houses on Hak Pakai or Hak Pakai over Hak Milik under a formal deed. Yet much of the foreign-facing villa market is not that product: it is a private lease. A lease can be lawful and useful, but it is a wasting contractual asset whose value depends on the land certificate, lessor, executed term, extension formula, assignment, default remedies and treatment of the building at expiry.",
        "Property and residence must be solved separately. Immigration’s current list includes E33E five-year and E33F one-year retiree special-residency visas, but the E33F detail page currently says its data are not yet available. A seller, agent or lease cannot fill that gap. Confirm the current applicant-specific visa requirements and healthcare plan directly with immigration counsel before treating any home as a retirement base. Bali’s provincial health system lists hospitals across Denpasar, Badung and Gianyar; access is strongest around the southern service corridor, while an attractive inland or cliff address can add substantial time in traffic.",
        "Proceed only if independent Indonesian counsel can explain in plain language what is acquired, for how long and on what registered land; a planner can confirm land use and building approvals; and a licensed adviser can reconcile residence, tax and operation. A personal-use home may work without tourist income. A rental villa requires a separate lawful business route, property-level permission and conservative economics. If the deal needs an informal nominee, an assumed extension, an unfinished permit or heroic occupancy to make sense, it is not ready."
    ),
    lenses_intro="The five lenses below pair the Atlas’s ten dimensions around Bali’s real decision sequence: daily life, access, legal interest, lawful operation and the leasehold exit.",
    lenses=(
        DossierLens(
            "Choose an island routine that still works in rain",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Bali’s lifestyle case is real: strong food, culture, wellness, tropical landscapes and a large international community can make ordinary weeks rewarding. The useful retirement question is narrower. Sanur offers a relatively mature, flatter coastal routine with supermarkets, cafés and hospitals in the wider Denpasar corridor. Ubud offers culture and greenery but brings congestion, hills, damp and longer access to some specialist care. Canggu concentrates restaurants and international services yet can turn a short map distance into a tiring journey. Uluwatu offers cliffs and surf but is more fragmented and car-dependent.",
                "Healthcare depth is concentrated rather than uniform. Bali’s official health directory lists RSUP Prof. Dr. I.G.N.G. Ngoerah and multiple public and private hospitals in Denpasar, RSUD Bali Mandara near Sanur, Mangusada and Udayana facilities in Badung, and Sanjiwani plus other hospitals in Gianyar. A directory proves facilities exist, not that a preferred specialist, insurance arrangement or emergency pathway will work for the buyer. Test the exact door-to-door trip at busy hours, identify a primary doctor and emergency hospital, and arrange insurance before moving.",
                "Live in the chosen neighbourhood during the wet season before signing a long lease. Make the grocery, pharmacy, hospital and airport journeys; test drainage, mould, insects, noise, power, internet, water pressure and wastewater; and ask what happens when a driver is unavailable. A pool and open living room can be delightful, but stairs, slippery stone, humidity and constant maintenance matter over years. Bali scores highly for magnetism; retirement fit belongs to the address and household, not the island brand."
            ),
            None,
        ),
        DossierLens(
            "Measure access in traffic time, not kilometres",
            ("global_access", "foreigner_fit"),
            (
                "I Gusti Ngurah Rai is an international airport and gives Bali unusually strong regional access for an island, but every property journey crosses a constrained road system. The airport operator identifies DPS as Bali’s international airport; that establishes the gateway, not the final leg. Sanur and parts of southern Denpasar can offer a more predictable airport and hospital relationship. Canggu, Ubud and the Bukit can vary sharply by hour, ceremony, rain and construction. Record actual weekday and weekend travel rather than accepting an agent’s best-case minutes.",
                "Foreigner fit is high in service availability but lower in legal simplicity. English is common in the sales and hospitality ecosystem, yet the controlling land certificate, spatial plan, tax record, lease, corporate documents and government approvals are Indonesian instruments. Translation by the selling agent is not independent advice. Use a buyer-appointed lawyer or notary, verify identity and authority of every lessor and landholder, and retain signed bilingual documents where appropriate. Confirm who receives official notices and who can act when the owner is abroad.",
                "The island’s popularity also creates operating friction: road access can be narrow, neighbours can be affected by guest traffic, and construction can change a view or route. Inspect legal road access, parking, refuse collection, water supply, septic or sewer arrangements and the path for tradespeople. In a cliff or rural setting, test emergency response and evacuation. Global connectivity is valuable only when the last mile remains usable for the buyer, staff and eventual resale market."
            ),
            "bali-access",
        ),
        DossierLens(
            "Define the right, the term and the permitted use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Indonesia’s Basic Agrarian Law reserves Hak Milik to Indonesian citizens and identifies foreigners domiciled in Indonesia as eligible for Hak Pakai. Government Regulation 18/2021 adds the current residential framework for foreigners with immigration documents. That does not convert a vendor’s ‘freehold’ advertisement into foreign freehold. Obtain an official land search and independent written opinion covering the land right, registered holder, encumbrances, boundaries, access, disputes, building ownership and the precise route available to this buyer. Reject nominee arrangements that disguise beneficial ownership.",
                "For leasehold, read the executed instrument rather than the marketing label. Confirm start and expiry dates, prepaid rent, renewal mechanism and price, assignment and subletting, succession, landlord sale or death, taxes, insurance, repairs, reconstruction after casualty, default, dispute forum and what happens to the building and furniture at expiry. ‘Twenty-five plus twenty-five’ is not fifty years unless the later term is enforceable on intelligible economics. Compare price per remaining lease-year as well as price per portal-stated building area. Ask counsel to produce a one-page term schedule from the signed documents, then reconcile it to every date and promise in the advertisement. Record who must consent to assignment, whether the next buyer can inherit the extension right, which currency or index sets extension rent, and whether the lessee can remove or recover value from improvements at expiry. Price any unresolved consent or renewal as absent, not probable.",
                "Permitted residential use does not establish lawful hospitality use. OSS classifies villa accommodation under KBLI 55193, describing private houses rented to tourists and managed by the owner. The exact project still needs compatible zoning, building approvals, business structure, licences and local compliance. Verify PBG and SLF status, spatial designation, environmental and wastewater obligations, neighbourhood constraints and the operator’s registrations. For each claimed approval, obtain the complete document, issuing authority, parcel or building identifier, approved plans, use category, conditions and current status; match names, coordinates and floor area to the land search and physical building. A receipt, application screenshot or agent statement is not an issued approval. Have the planner identify any mismatch and the lawful remedy before deposit, because a permit ‘in process’ transfers execution, delay and refusal risk to the buyer. A platform listing, Pondok Wisata claim or management forecast is evidence to investigate, not permission."
            ),
        ),
        DossierLens(
            "Underwrite a hospitality business without borrowing hotel statistics",
            ("rental_profit", "capital_upside"),
            (
                "Bali’s tourism demand is substantial. BPS recorded 578,251 direct foreign arrivals in May 2026 and room occupancy of 61.16% for star hotels and 37.20% for non-star hotels and other accommodation. Those figures support the island-wide demand context; they do not forecast an individual villa. Location, bedroom count, design, licence, reviews, distribution, operator quality, season, road access and new supply can produce very different results. Do not apply a marketed island occupancy rate to the candidate property.",
                "Build the operating model from source documents: achieved booking statements, bank receipts, platform reports, tax filings, staffing contracts and utility bills. Model management, cleaning, linen, commissions, maintenance, pool and garden care, utilities, insurance, local taxes, replacement reserves and empty periods. Indonesia’s tax authority states that land and building lease income is generally subject to 10% final income tax on the gross rental value; hospitality, foreign ownership and corporate structures can change the analysis, so obtain a written taxpayer-specific opinion.",
                "Capital upside is also structure-dependent. Bank Indonesia’s Denpasar primary-house index provides a disciplined official context but does not price Bali leasehold villas. Appreciation in underlying land may accrue principally to the landholder, while the lessee’s remaining term declines. Renovation, brand and a favourable extension can create value, but none is automatic. Run a no-rental case, a weak-season case and an exit with five fewer lease years. If the return disappears without perpetual extension or resale at today’s multiple, the underwriting is too optimistic."
            ),
            "villa-operation",
        ),
        DossierLens(
            "Price the declining term and preserve an honest exit",
            ("value_entry", "exit_liquidity"),
            (
                "The three listing observations below are deliberately all leasehold because that is the comparison many foreign buyers actually face. They span Sanur, Canggu and Ubud, but their lease terms and legal readiness differ. The portal’s building-area field is only a denominator; it is not verified legal internal area. Price per square metre without remaining term can mislead, just as a low total price can hide a short lease, unfinished permit or expensive extension.",
                "Exit liquidity depends on what can be assigned to whom. A future buyer will examine remaining years, extension rights, landholder cooperation, permits, operating records, building condition and the same immigration or entity constraints. Sanur may attract long-stay and retirement demand; Canggu may reach a larger hospitality audience but face supply and traffic pressure; Ubud demand can be strong but access and the specific lease matter. Ask two independent brokers how they would market the exact interest today and after five years.",
                "Model acquisition through exit. Include legal and notarial work, searches, applicable BPHTB or other transaction taxes, lease-related tax, business setup, permits, insurance, furnishing, maintenance, management, currency and sale costs. The national BPHTB ceiling is 5% on the taxable base after the local non-taxable threshold, but the applicable transaction and Bali locality require a written closing statement. Do not add a generic percentage to every lease. The best entry is the clearest lawful interest at a price that recognises decay, capex and a narrower future buyer pool."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Bali combines culture, food, wellness and tropical scenery, while Sanur, Ubud, Canggu and Uluwatu produce distinctly different routines.",
        "global_access": "Bali has a major international gateway at DPS, but Canggu, Ubud and Uluwatu journeys are governed by traffic and last-mile roads.",
        "ownership_clarity": "Bali foreign buyers must distinguish Hak Pakai and other lawful rights from contractual leasehold; Hak Milik nominee arrangements are not a solution.",
        "regulatory_safety": "Bali villa operation requires property-level zoning, building and OSS licensing checks; an online rental history does not prove lawful use.",
        "rental_profit": "Bali tourism demand is deep, but BPS hotel occupancy is not a villa forecast and net profit depends on licence, operator and cost evidence.",
        "capital_upside": "Bali land and tourism demand can support selected assets, while lease decay means underlying appreciation may not accrue fully to the lessee.",
        "retirement_fit": "Sanur offers Bali’s clearest service corridor; Ubud, Canggu and Uluwatu require sharper traffic, healthcare, humidity and mobility testing.",
        "exit_liquidity": "Bali resale depth narrows with shorter lease terms, weak extensions, unclear permits and singular villas whose next buyer must accept the same structure.",
        "foreigner_fit": "Bali has a mature international service ecosystem, but title, planning, tax, lease and licence documents still require independent Indonesian advice.",
        "value_entry": "Bali leasehold asks can look inexpensive per square metre; remaining years, permit status, extension cost and terminal value determine real entry value.",
    },
    market_anchors=(
        {"location": "Denpasar small primary houses", "evidence": "RPPI 106.52", "buyer_read": "Bank Indonesia Q1 2026 index, 2018=100, based on developer primary-house prices; not a Bali villa price, leasehold benchmark or valuation.", "source_label": "Bank Indonesia Q1 2026 survey", "source_url": "https://www.bi.go.id/en/publikasi/laporan/Documents/Residential-Property-Survey-Quarter-1-2026.pdf"},
        {"location": "Denpasar medium primary houses", "evidence": "RPPI 106.70", "buyer_read": "Bank Indonesia Q1 2026 index, 2018=100, for developer primary houses; it shows price direction only and is not matched to Sanur, Ubud or Canggu villas.", "source_label": "Bank Indonesia Q1 2026 survey", "source_url": "https://www.bi.go.id/en/publikasi/laporan/Documents/Residential-Property-Survey-Quarter-1-2026.pdf"},
        {"location": "Denpasar large primary houses", "evidence": "RPPI 104.82", "buyer_read": "Bank Indonesia Q1 2026 index, 2018=100, for developer primary houses; tenure, completed sales, land value and lease years are outside its scope.", "source_label": "Bank Indonesia Q1 2026 survey", "source_url": "https://www.bi.go.id/en/publikasi/laporan/Documents/Residential-Property-Survey-Quarter-1-2026.pdf"},
    ),
    micro_locations_intro="Bali is not one property market. Sanur, Ubud, Canggu and Uluwatu support different routines, operating models and future buyer pools, with meaningful street-by-street variation in access, planning, hazards, water and construction. Use the table to choose a routine to test, not a listing. Rent nearby first; repeat essential journeys in traffic and heavy rain; then match the advertised location to the registered parcel, current spatial plan and hazard overlays before pricing personal or hospitality use.",
    micro_locations=(
        {"name": "Sanur", "best_for": "Long-stay routine", "daily_life": "Flatter coast, established services and stronger Denpasar hospital access.", "diligence": "Beachside flooding and tsunami layers, lease term, traffic, PBG/SLF and lawful rental use."},
        {"name": "Ubud", "best_for": "Culture and greenery", "daily_life": "Restaurants, wellness and inland landscapes with congestion and humidity.", "diligence": "Road access, slope and flood risk, mould, water, wastewater, licence and hospital journey."},
        {"name": "Canggu / Berawa", "best_for": "Hospitality ecosystem", "daily_life": "Dense international amenities alongside heavy traffic and construction.", "diligence": "Supply, noise, access width, drainage, permits, operator evidence and lease decay."},
        {"name": "Uluwatu / Bukit", "best_for": "Cliff and surf lifestyle", "daily_life": "Dramatic coast with fragmented services and car dependence.", "diligence": "Water, cliff stability, evacuation, road title, construction quality, wastewater and exit pool."},
    ),
    checklist=(
        "Obtain official land and encumbrance searches; identify the registered right, holder, boundaries and legal access.",
        "Have independent counsel explain the buyer’s lawful structure and reject nominee ownership.",
        "Reconcile lease commencement, expiry, extension pricing, assignment, succession, default and building ownership.",
        "Verify spatial designation, PBG, SLF, wastewater, water, environmental and neighbourhood requirements.",
        "For paid stays, confirm KBLI, business entity, licence, tax and exact property eligibility in writing.",
        "Test wet-season drainage, mould, traffic, hospital and airport travel, utilities and emergency access.",
        "Rebuild rental economics from achieved records and include 10% final income tax only where adviser-confirmed.",
        "Model the exit five years later with fewer lease years, capex, selling costs and a narrower eligible buyer pool.",
    ),
    references_intro="Legal and administrative claims use Indonesian government sources reviewed 23 August 2026. The next scheduled review is 23 November 2026. Review sooner if land, immigration, tax, licensing, planning, healthcare, transport or hazard rules change; if a listing or source becomes unavailable; or if the Atlas score changes. The E33F detail page currently provides no requirements. Recheck every linked source and obtain independent Indonesian legal, tax, immigration and planning advice for the exact buyer, parcel, interest and intended use before commitment.",
    references=(
        {"label": "ATR/BPN: Basic Agrarian Law", "url": "https://jdih.atrbpn.go.id/peraturan/download/32/Penerjemahan%20UU%20No.%205%20Tahun%201960%20%28UUPA%29.pdf"},
        {"label": "ATR/BPN: Government Regulation 18/2021", "url": "https://jdih.atrbpn.go.id/peraturan/download/946/Terjemahan%20PP%20No%2018%20Tahun%202021.pdf"},
        {"label": "ATR/BPN: Ministerial Regulation 18/2021", "url": "https://jdih.atrbpn.go.id/peraturan/download/1030/Permen%20ATR%20KBPN%20No.%2018%20Tahun%202021%20tentang%20Tata%20Cara%20Penetapan%20Hak%20Pengelolaan%20dan%20Hak%20Atas%20Tanah.pdf"},
        {"label": "Immigration: current visa list", "url": "https://kanwilpapuabarat.imigrasi.go.id/service-proxy/8"},
        {"label": "Immigration: E33F retiree page", "url": "https://kanwilpapuabarat.imigrasi.go.id/service-proxy/8?url=https%3A%2F%2Fwww.imigrasi.go.id%2Fwna%2Fdaftar-visa-indonesia%2FE33F"},
        {"label": "OSS: KBLI 55193 villa accommodation", "url": "https://oss.go.id/en/kbli/detail/2eebd4b4-1bf0-43eb-99de-fa767ea4fb18"},
        {"label": "Directorate General of Taxes: land and building lease income", "url": "https://pajak.go.id/id/pemotongan-pajak-penghasilan-pasal-4-ayat-2-1"},
        {"label": "Indonesia Law 1/2022: BPHTB ceiling", "url": "https://jdih.kemenkeu.go.id/download/770ecf1d-664b-48a1-88f4-8849b8ca7258/1TAHUN2022UU.pdf"},
        {"label": "Bank Indonesia: Q1 2026 residential survey", "url": "https://www.bi.go.id/en/publikasi/laporan/Documents/Residential-Property-Survey-Quarter-1-2026.pdf"},
        {"label": "Bank Indonesia: JISDOR", "url": "https://www.bi.go.id/en/statistik/informasi-kurs/jisdor/Default.aspx"},
        {"label": "BPS Bali: May 2026 tourism", "url": "https://bali.bps.go.id/id/pressrelease/2026/07/01/718048/perkembangan-pariwisata-provinsi-bali-mei-2026.html"},
        {"label": "Bali Province: health-facility directory", "url": "https://sik-kbs.baliprov.go.id/pencarian"},
        {"label": "Bali BPBD: provincial hazard maps", "url": "https://bpbd.baliprov.go.id/article/2888/peta-risiko-bencana-banjir-di-provinsi-bali"},
        {"label": "Bali BPBD: 2025–2029 risk study", "url": "https://bpbd.baliprov.go.id/article/3402/kajian-risiko-bencana-provinsi-bali-tahun-2023-2027"},
        {"label": "InJourney Airports: Bali I Gusti Ngurah Rai", "url": "https://www.injourneyairports.id/airport/island/Nusa%20Tenggara"},
        {"label": "Rumah123: Sanur leasehold observation", "url": "https://www.rumah123.com/properti/denpasar-sanur/beachside-leasehold-villa-in-sanur-285-years-lease-169v-hos41263870/"},
        {"label": "Rumah123: Canggu leasehold observation", "url": "https://www.rumah123.com/properti/badung-canggu/villa-leasehold-di-canggu-cocok-untuk-investasi-hos40574772/"},
        {"label": "Rumah123: Ubud leasehold observation", "url": "https://www.rumah123.com/properti/gianyar-ubud/leasehold-tropical-luxury-villa-just-10-minutes-from-ubud-centre-vls111755/"},
    ),
    images=(
        DossierImage("sanur-life", "/assets/bali-sanur-life.webp", "Older couple walking along Sanur promenade in warm morning light", "Sanur makes Bali’s strongest case for a repeatable coastal routine.", "wide"),
        DossierImage("bali-access", "/assets/bali-access-road.webp", "Ordinary Bali road linking homes, shops and scooters after tropical rain", "On Bali, the last mile often matters more than the map distance.", "wide"),
        DossierImage("villa-operation", "/assets/bali-villa-operation.webp", "Well-maintained tropical villa courtyard prepared for everyday use", "A villa is an operating asset: water, drainage, staffing and permits sit behind the image.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Bali through five destination lenses",
    assessment_intro="Here’s how Bali scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three direct seller asks illustrate very different Bali leasehold propositions. IDR is primary; USD uses Bank Indonesia JISDOR. Building area and lease terms are portal claims, not legal verification.",
    market_anchors_intro="Bank Indonesia’s official Denpasar RPPI series is the most disciplined current direction indicator available here. It covers developer primary houses and is indexed to 2018=100; it does not establish Bali villa prices, leasehold value or completed transactions.",
    orientation_groups=(
        DossierOrientationGroup("South and east", (("DPS airport", "International gateway"), ("Sanur", "Long-stay coast"), ("Ubud", "Inland cultural base"))),
        DossierOrientationGroup("West and Bukit", (("Canggu", "Hospitality and traffic"), ("Jimbaran", "Southern service link"), ("Uluwatu", "Cliff and surf base"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Travel times vary sharply by traffic, rain and exact road access.",
    country_guide_url="/countries/indonesia-property/",
    country_guide_label="Indonesia property guide",
    rail_comparison="Compare Bali with the full Atlas.",
)


DOLOMITES_SOUTH_TYROL_DOSSIER = PremiumDossierSpec(
    destination_id="dolomites-south-tyrol",
    title="Dolomites and South Tyrol Property Dossier | Global Home Atlas",
    description="Assess Dolomites and South Tyrol property through resident-housing restrictions, ownership, access, healthcare, tourist letting, hazards, value, resale, and current listings.",
    h1="Dolomites / South Tyrol: buy the valley, not the postcard",
    lede=(
        "The Dolomites can deliver one of Europe’s finest year-round mountain lives, but the address determines whether that life is practical. Ortisei and Selva put the Sella landscape close at a premium; Corvara offers a resort-led Alta Badia rhythm; Brunico and Valdaora connect skiing to rail, named provincial hospitals and ordinary services; San Candido gives the eastern Pusteria valley a smaller but complete base. Ownership eligibility, resident-housing restrictions, tourist-use rights, winter access and resale are property-specific. This dossier separates the durable valley system from the postcard premium."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-23",
    date_reviewed="2026-08-23",
    verdict_paragraphs=(
        "The verdict is positive for a lifestyle-led buyer who chooses a year-round operating base before choosing a view. South Tyrol combines exceptional landscape, food, hiking, cycling and winter sport with functioning towns, public transport and provincial healthcare. Yet the strongest retirement case is not automatically the most famous resort. Ortisei and Selva can support repeat use, but they remain bus-linked valleys with premium entry prices. Corvara is even more road- and tourism-led. Brunico, Valdaora and San Candido offer a different proposition: rail or direct valley-bus access, ordinary commerce and closer connection to hospitals listed by the provincial health authority. The right answer depends on whether the home is for weeks of intense mountain use or months of everyday life.",
        "Legal access has two layers. Italy’s Foreign Ministry says EU and EEA citizens, and specified non-EU residents with qualifying Italian permits, are exempt from a reciprocity check; other non-EU buyers require a nationality- and transaction-specific assessment by the notary. That national ownership pathway does not override South Tyrol’s use restrictions. A conventioned or resident-housing dwelling can be purchased but cannot simply become a holiday home; it must serve eligible permanent housing. The 2025 provincial reform also reserves new housing zones and new residential volume for residents. A foreign buyer therefore needs written confirmation of both the ability to acquire and the exact unit’s lawful occupancy and letting status.",
        "Property ownership does not create residence. Italy’s elective-residence route is designed for applicants who intend to settle, have adequate independent income and will not work, but requirements and consular judgment remain applicant-specific. Establish residence, tax and healthcare arrangements first. Then choose the valley, test the hospital and winter route, obtain the land-register, cadastral, planning, energy, condominium and resident-housing records, and inspect the building for roof, moisture, heating, snow and access burdens. Only after that should tourist rent, appreciation or a future foreign buyer enter the model. The Dolomites reward selectivity; they punish the assumption that beauty makes every restriction and carrying cost irrelevant."
    ),
    lenses_intro=(
        "The Atlas groups the ten decision dimensions into five practical questions. The prose explains what the evidence means for a buyer; the complete ten-dimension assessment appears once in the score table below."
    ),
    lenses=(
        DossierLens(
            "Choose the daily system that still works after ski week",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Ortisei and Selva are the most recognisable Val Gardena choices. They combine dramatic scenery, lifts, restaurants, Ladin culture and a long summer season, but their daily systems are not identical to an urban neighbourhood. Ortisei has the broader village centre and direct valley buses; Selva places the high-mountain experience closer and the international resort identity higher. Both require careful review of gradient, ice, evening transport, grocery distance and the journey to Bressanone or Bolzano for deeper services. A lift-side apartment can be outstanding for active repeat stays and still become inconvenient when walking ability changes or the car cannot reach the building easily in snow.",
                "Corvara and Alta Badia offer a polished resort environment, strong food culture and exceptional access to the Sella landscape. They are also more dependent on roads and buses for the wider life of the province. This matters in retirement and shoulder season. Test the route to Brunico hospital, the nearest pharmacy and grocery options when visitor services reduce. Ask whether a non-skiing partner has a satisfying week and whether the address works without driving after dark. The destination’s magnetism is unquestioned; retirement fit depends on how much of the household’s routine can be met inside a small tourism-led valley.",
                "Brunico, Valdaora and San Candido shift the balance. Brunico is a regional service and rail base whose official health district lists primary-care, nursing, dental and public-health services; the provincial health authority also names hospitals in Brunico and San Candido. Valdaora connects a village routine and the Pusteria rail corridor to Kronplatz, while San Candido combines a walkable centre and rail with its named hospital. These facts establish location, not comparative clinical capability or appointment access. Spend an ordinary November week before buying. Make the food, clinic, hospital and social journeys; test heating and daylight; and ask whether one household member could remain independent if the other could no longer drive."
            ),
            "village-routine",
        ),
        DossierLens(
            "Treat access as a chain, not an airport claim",
            ("global_access", "foreigner_fit"),
            (
                "South Tyrol has no single gateway that makes every Dolomites address easy. International trips normally combine an airport, mainline rail or motorway, and a final valley leg. Val Gardena connects by buses through Ponte Gardena, Chiusa, Bressanone or Bolzano. Alta Badia connects by road and valley buses toward Brunico. The Pusteria corridor is different: regional trains link Fortezza, Brunico, Valdaora, Dobbiaco and San Candido. Official 2026 timetables show this network, but they do not guarantee a simple luggage journey from a specific home. Measure the complete trip in winter, including transfers, parking, snow and late arrival.",
                "The Pusteria rail corridor can support a lower-car lifestyle if the address is genuinely walkable to a station and daily services. Valdaora and San Candido benefit from that structure; a hillside development described as near rail may still require a steep walk or local bus. Ortisei and Selva have frequent valley services but remain bus-led. Corvara’s practical range depends even more on roads, buses and season. Inspect the exact last mile in poor weather. Confirm ski storage, step-free access, snow clearance, visitor parking and whether taxis operate when needed. A good regional network cannot repair a difficult building entrance.",
                "South Tyrol’s German, Italian and Ladin environment is part of the appeal and part of the operating reality. Tourism professionals often support international clients, but the binding transaction, land-register, planning, tax and provincial-housing work remains local. Use an independent bilingual notary and lawyer, and obtain translations where necessary. A buyer who expects English to carry every administrative task will find more friction than a visitor does. Foreigner fit is strongest when the household welcomes local language and institutions, retains professional support, and chooses a community for daily belonging rather than treating it as a managed resort product."
            ),
            "pusteria-rail",
        ),
        DossierLens(
            "Clear both the national purchase and the provincial use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Nationally, the notary must establish that the buyer can complete the legal act. EU and EEA citizens do not require reciprocity verification. Certain legally resident non-EU citizens are also exempt; for other non-EU nationals, reciprocity or an applicable treaty position must be checked case by case. Do not accept a portal’s phrase such as freehold or foreign-buyer friendly as the answer. Confirm nationality, residence status, marital-property position, tax code, source of funds and signing arrangements before paying a non-refundable deposit. The purchase contract should be conditional on the documentary and legal results that matter.",
                "South Tyrol adds the controlling property-use question. The provincial housing-supervision FAQ says a conventioned dwelling may be bought but cannot be used as a holiday home; it must meet eligible permanent-housing needs. The 2025 reform moves further by reserving new housing zones and new residential volume for residents, with stronger controls against misuse. A listing advertised as new, investment-grade or ideal for a second home may therefore describe very different legal products. Obtain the exact conventioning, occupancy and land-register records, and ask the competent municipality or provincial authority to confirm lawful second-home use in writing.",
                "Tourist letting is a separate regulated activity. The province requires the certified commencement notification for private room and furnished-holiday-apartment letting, together with classification and price-notification requirements; 2025–2026 reforms add tighter operating and professional-qualification rules. National identification and safety duties may also apply. None of this proves that a particular conventioned apartment, condominium or municipality permits the intended use. Verify the unit, operator, building rules, registration, safety equipment, tax and continuity after sale. If the financial case depends on short stays before these answers exist, the buyer is underwriting a hospitality permission rather than a home."
            ),
        ),
        DossierLens(
            "Underwrite ordinary demand before the tourism premium",
            ("rental_profit", "capital_upside"),
            (
                "Rental demand is real but uneven. Ortisei, Selva and Corvara can command intense winter and summer interest, while Brunico, Valdaora and San Candido mix visitor demand with more ordinary local use. Gross rates do not reveal the result. Deduct management, cleaning, utilities, heating, condominium charges, maintenance, insurance, furnishing renewal, platform costs, vacancy and tax. Then separate a lawful private-let operation from an apartment that may only be occupied as eligible resident housing. The safest retirement model works with no tourist rent; any compliant income should improve the case rather than rescue it.",
                "Scarcity supports the long-term story, especially in established resort centres where landscape, planning and limited developable land constrain supply. The resident-housing policy can also protect local occupancy while reducing the stock legally available to second-home buyers. Scarcity is not the same as guaranteed appreciation. Premium markets can reprice when financing costs rise, winter demand changes or a building’s access and energy performance fall behind. Model a flat nominal value after five years and a material discount on sale. A beautiful but legally narrow asset may be scarce and still have a small future buyer pool.",
                "Climate and infrastructure deserve explicit capital treatment. The province’s Hazard Browser and municipal hazard-zone plans cover flood, debris flow, landslide, rockfall and avalanche information; the correct screen is address-specific, not a valley reputation. Review roof snow load, retaining walls, slope drainage, stream proximity, avalanche exposure, access closure and insurance. Also inspect energy classification, heating system, summer cooling need and the cost of upgrading older alpine construction. A property that remains reachable, efficient and insurable is more likely to preserve usefulness and buyer demand than one whose only durable feature is the view."
            ),
        ),
        DossierLens(
            "Pay for lawful use and a buyer pool you can name",
            ("value_entry", "exit_liquidity"),
            (
                "Official OMI 2025 H2 ranges show why one Dolomites average is misleading. Normal-condition apartment ranges in selected central zones were 5,100–9,700 EUR/m² in Ortisei, 3,800–7,500 in Corvara and 2,400–4,800 in San Candido, all on the OMI gross-area basis. They are broad zone opinions, not completed-sale evidence or valuations. They also do not capture every premium view, renovation or restriction. Their value is comparative: they reveal a location gradient and force the buyer to identify asset type, condition, lawful use and area basis before accepting a portal comparison.",
                "The three asking observations below add current product evidence: a 115 m² Ortisei apartment, a 110 m² tourist apartment in Selva and a 50 m² Valdaora apartment advertised for independent second-home use. All use the portal-stated surface denominator; that is not a legal or measured internal-area certificate. Their asking EUR/m² levels differ sharply, and none is a substitute for completed transactions. Reconcile cadastral and physical areas, accessories, parking, energy, conventioning, tourist status, condition and view. A smaller legal second-home unit can be better value than a larger resident-restricted bargain the buyer cannot use as intended.",
                "Acquisition cost must be property-specific. On a private residential resale, the Italian Revenue Agency’s general baseline is 9% registration tax on the applicable base absent first-home relief; developer or VAT sales, luxury categories and buyer facts can differ, so obtain a written notarial closing statement. Exit liquidity then follows the future audience. A central, lawful second-home apartment with manageable charges, parking and ordinary access can reach domestic, European and international lifestyle buyers. A conventioned apartment reaches an eligibility-defined resident market. A very expensive Selva or Ortisei home requires a narrower buyer who accepts both entry price and carrying cost. Ask two independent agents to identify the next buyer, normal marketing period and completed substitutes. Model sale tax and fees, currency movement, a weaker ski season and a ten-percent price reduction. The best entry is the one whose lawful use and future buyer remain clear without promotional assumptions."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Ortisei, Selva and Corvara deliver exceptional mountain culture; Brunico, Valdaora and San Candido make that lifestyle more repeatable beyond peak weeks.",
        "global_access": "South Tyrol combines mainline connections with valley buses; Pusteria rail helps Valdaora and San Candido, while Val Gardena and Corvara retain longer last miles.",
        "ownership_clarity": "Italy’s reciprocity framework is workable, but every South Tyrol buyer must also clear the exact unit’s conventioning and lawful occupancy status.",
        "regulatory_safety": "South Tyrol resident-housing and tourist-let rules are property-specific; conventioned homes, municipal approvals and alpine hazards require written address-level clearance.",
        "rental_profit": "Ortisei, Selva and Corvara have strong visitor demand, but lawful-use limits, seasonality, management, heating and maintenance compress the spendable return.",
        "capital_upside": "Dolomites scarcity and year-round demand support the case, while high entry prices, energy upgrades and restricted buyer pools limit easy appreciation.",
        "retirement_fit": "The provincial health authority names hospitals in Brunico and San Candido; Valdaora adds rail, while every buyer must verify the required service and real journey from the address.",
        "exit_liquidity": "Lawful second homes in recognised Dolomites centres reach broad lifestyle buyers; conventioned, inaccessible or extremely expensive stock has a narrower exit.",
        "foreigner_fit": "South Tyrol is internationally experienced, but German, Italian and Ladin administration means foreign buyers still need bilingual independent professional support.",
        "value_entry": "Official OMI ranges and current Ortisei, Selva and Valdaora asks show that lawful use, area basis and carrying cost matter more than one regional average.",
    },
    market_anchors=(
        {"location": "Ortisei · B1 central premium zone", "evidence": "5,100–9,700 EUR/m²", "buyer_read": "Agenzia Entrate OMI 2025 H2 range for normal-condition apartments on gross area in the Scurcià, Lusenberg and Via Meisules B1 zone; a zone opinion, not a sale or valuation.", "source_label": "Agenzia Entrate OMI 2025 H2", "source_url": "https://www1.agenziaentrate.gov.it/servizi/Consultazione/ricerca.htm?lingua=DE"},
        {"location": "Corvara · B1 centre", "evidence": "3,800–7,500 EUR/m²", "buyer_read": "Agenzia Entrate OMI 2025 H2 range for normal-condition apartments on gross area in the Corvara, Pescosta and Colfosco B1 zone; it does not isolate a view, restriction or completed sale.", "source_label": "Agenzia Entrate OMI 2025 H2", "source_url": "https://www1.agenziaentrate.gov.it/servizi/Consultazione/ricerca.htm?lingua=DE"},
        {"location": "San Candido · B1 centre", "evidence": "2,400–4,800 EUR/m²", "buyer_read": "Agenzia Entrate OMI 2025 H2 range for normal-condition apartments on gross area in central San Candido; it is a broad zone benchmark, not a candidate valuation.", "source_label": "Agenzia Entrate OMI 2025 H2", "source_url": "https://www1.agenziaentrate.gov.it/servizi/Consultazione/ricerca.htm?lingua=DE"},
    ),
    micro_locations_intro=(
        "Use four operating patterns, not one Dolomites average. Ortisei and Selva are the premium Val Gardena pair; Corvara and Alta Badia are resort-led and road-dependent; Brunico and Valdaora combine a service town, rail and Kronplatz; San Candido and Dobbiaco offer a smaller eastern Pusteria base. Confirm exact conventioning, second-home use, station or bus route, gradient, snow clearance, hospital journey, hazards, building costs and future eligible buyer for every address."
    ),
    micro_locations=(
        {"name": "Ortisei / Selva Val Gardena", "best_for": "Premium active mountain life", "daily_life": "Village services and buses inside a high-cost resort valley", "diligence": "Conventioning, gradient, building, parking and exit price"},
        {"name": "Corvara / Alta Badia", "best_for": "Sella access and polished resort use", "daily_life": "Tourism-led villages with road and bus dependence", "diligence": "Lawful use, winter road, hospital route and seasonality"},
        {"name": "Brunico / Valdaora", "best_for": "Services, rail and Kronplatz", "daily_life": "Resident economy, named hospital and Pusteria connections", "diligence": "Required clinical service, station walk, conventioning and exact second-home right"},
        {"name": "San Candido / Dobbiaco", "best_for": "Walkable eastern-valley base", "daily_life": "Rail, a named hospital and year-round town services", "diligence": "Clinical capability, winter access, tourist status and resale depth"},
    ),
    checklist=(
        "Confirm nationality-specific reciprocity, residence, tax and healthcare before treating the property as a retirement home.",
        "Obtain written land-register, cadastral, planning, condominium, energy and conventioning records for the exact unit.",
        "Require explicit confirmation that second-home occupancy and any tourist use are lawful and continue after sale.",
        "Travel the airport, rail or bus, grocery and hospital chain from the exact address in winter and shoulder season.",
        "Inspect roof, moisture, heating, snow load, retaining structures, access, parking and planned capital work.",
        "Screen the provincial Hazard Browser and municipal plan for flood, debris flow, landslide, rockfall and avalanche exposure.",
        "Compare portal surface, legal area and completed substitutes before relying on EUR/m² or a valuation.",
        "Model five-year carrying and a conservative resale without tourist rent, then identify the future eligible buyer.",
    ),
    references_intro=(
        "Legal, residence, tax, housing, tourism, transport, healthcare, hazard, market, FX and listing claims were reviewed on 23 August 2026. The next scheduled review is 23 February 2027, or sooner if a cited law, provincial rule, OMI release, timetable, hazard source or listing changes. Recheck every live source and obtain independent Italian and South Tyrolean legal, notarial, tax, immigration, planning, engineering and insurance advice for the exact buyer and property. Listing observations are dated asks, not proof of title, lawful use, area, condition, availability or completed value."
    ),
    references=(
        {"label": "Italian Foreign Ministry: rights and reciprocity", "url": "https://www.esteri.it/en/temi/diplomazia_giuridica/condizreciprocita/"},
        {"label": "Italian Notariat: services for foreign buyers", "url": "https://www.notariato.it/en/notaio/notarial-services-for-foreigners/"},
        {"label": "Italian Revenue Agency: buying a home and transfer taxes", "url": "https://www1.agenziaentrate.gov.it/web_app_entrate/guida_acquisto_casa.html"},
        {"label": "Italian Consulate London: elective residence", "url": "https://conslondra.esteri.it/it/servizi-consolari-e-visti/servizi-per-il-cittadino-straniero/visti/elective-residence/"},
        {"label": "South Tyrol Housing Supervision: conventioned-home FAQ", "url": "https://wohnbauaufsicht.provinz.bz.it/de/faq-frequently-asked-questions"},
        {"label": "South Tyrol: 2025 resident-housing reform", "url": "https://wohnen.provinz.bz.it/de/mehr-wohnraum"},
        {"label": "South Tyrol: private rooms and holiday-apartment letting", "url": "https://tourismus.provinz.bz.it/de/gastgewerbe-private-zimmer-ferienwohnungsvermietung"},
        {"label": "South Tyrol: 2026 private-landlord qualification", "url": "https://news.provinz.bz.it/de/news/private-vermieter-kriterien-fur-berufliche-qualifikation-beschlossen"},
        {"label": "Agenzia Entrate: OMI quotation search", "url": "https://www1.agenziaentrate.gov.it/servizi/Consultazione/ricerca.htm?lingua=DE"},
        {"label": "South Tyrol Mobility: current timetables", "url": "https://www.suedtirolmobil.info/en/my-journey/timetables"},
        {"label": "South Tyrol Mobility: regional network maps", "url": "https://www.suedtirolmobil.info/en/my-journey/network-maps"},
        {"label": "South Tyrol Health Authority: named hospital laboratories", "url": "https://www.sabes.it/it/laboratori"},
        {"label": "South Tyrol Health Authority: Brunico district services", "url": "https://www.sabes.it/it/brunico-circondario"},
        {"label": "South Tyrol natural-hazards portal", "url": "https://naturgefahren.provinz.bz.it/it/home"},
        {"label": "South Tyrol Hazard Browser", "url": "https://naturgefahren.provinz.bz.it/it/hazard-browser"},
        {"label": "European Central Bank: euro reference rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
        {"label": "Ortisei Via Minert apartment asking observation", "url": "https://www.immobiliare.it/annunci/123436481/"},
        {"label": "Selva Strada da Nives apartment asking observation", "url": "https://www.immobiliare.it/annunci/126489173/"},
        {"label": "Valdaora Residence Plunger apartment asking observation", "url": "https://www.immobiliare.it/annunci/128498934/"},
    ),
    images=(
        DossierImage("val-gardena-life", "/assets/dolomites-south-tyrol-val-gardena-life.webp", "Older couple walking through Ortisei with the Dolomites behind the village", "Val Gardena’s appeal is strongest when village life works beyond the lifts.", "hero"),
        DossierImage("pusteria-rail", "/assets/dolomites-south-tyrol-pusteria-rail.webp", "Regional train crossing the Pusteria valley near Valdaora", "Pusteria rail changes the daily-life case for Valdaora and San Candido.", "wide"),
        DossierImage("village-routine", "/assets/dolomites-south-tyrol-village-routine.webp", "Everyday South Tyrol village street with shops, bus stop and mountain backdrop", "A durable mountain home connects scenery to groceries, healthcare and winter access.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Dolomites / South Tyrol through five destination lenses",
    assessment_intro="Here’s how Dolomites / South Tyrol scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations compare premium Ortisei, tourist-use Selva and second-home Valdaora apartments. EUR is primary; USD uses the recorded ECB reference rate. Portal-stated surface is a comparison denominator, not verified legal internal area.",
    market_anchors_intro="These official Agenzia Entrate OMI 2025 H2 zone ranges cover normal-condition apartments on gross area. They are broad market opinions—not completed transactions, asking prices or valuations—and must be reconciled for legal use, exact location, condition and area.",
    orientation_groups=(
        DossierOrientationGroup("Val Gardena / Alta Badia", (("Bolzano / Bressanone", "Mainline service gateways"), ("Ortisei", "Broader Val Gardena base"), ("Selva", "High resort core"), ("Corvara", "Road-linked Alta Badia"))),
        DossierOrientationGroup("Pusteria rail corridor", (("Fortezza", "Mainline interchange"), ("Brunico", "Hospital and service town"), ("Valdaora", "Rail and Kronplatz"), ("San Candido", "Eastern valley hospital base"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Val Gardena and Alta Badia are bus- and road-led; the Pusteria corridor has rail. Confirm the exact winter route and last mile.",
    country_guide_url="/countries/italy-property/",
    country_guide_label="Italy property guide",
    rail_comparison="Compare Dolomites / South Tyrol with the full Atlas.",
)


CHAMONIX_DOSSIER = PremiumDossierSpec(
    destination_id="chamonix",
    title="Chamonix Retirement Property Dossier",
    description="Assess Chamonix retirement property through daily life, Geneva access, residence, healthcare, tourist-let rules, alpine hazards, completed-market anchors, value, and resale.",
    h1="Chamonix: buy the usable valley address, not only the Mont Blanc name",
    lede=(
        "Chamonix has a world-famous name, but retirement quality is decided at street level. Chamonix Centre offers shops, trains, buses and a hospital site within an active town. Les Praz and Les Tines trade some convenience for space and calm. Argentière and Le Tour put mountain access first, while Les Houches offers a more residential price point and an easier family buyer pool. The right purchase connects that alpine appeal to lawful use, winter access, healthcare, manageable building costs and a credible exit."
    ),
    author="Global Home Atlas Research Team",
    date_published="2026-08-23",
    date_reviewed="2026-08-23",
    verdict_paragraphs=(
        "Chamonix is a strong lifestyle-led purchase for a buyer who can afford to treat personal use as the principal return. The valley works throughout the year: climbing, hiking, skiing and trail running sit beside supermarkets, schools, restaurants, rail and an established resident economy. Yet the purchase does not create French residence. A non-EU retiree ordinarily needs an appropriate long-stay status, and France-Visas requires a visitor applicant to demonstrate resources, accommodation and medical cover while agreeing not to work. Public healthcare follows separate residence and eligibility rules. Confirm immigration, tax residence and health coverage before the property search becomes binding.",
        "The second condition is to buy an operating pattern rather than a postcard. Chamonix Centre can support more car-light daily life, but it brings crowds, noise, small apartments and older copropriété buildings. Les Praz and Les Tines can offer calm, sun and rail stops, but the exact walk, gradient and winter route matter. Argentière and Le Tour are compelling for serious mountain users, with greater exposure to snow, seasonal trade and distance from central services. Les Houches is a distinct commune and market: less globally prestigious, often better value, and potentially easier to explain to a permanent household on resale.",
        "The third condition is regulatory discipline. Since 1 May 2025, the Chamonix valley requires registration for furnished tourist accommodation and, for physical-person owners, change-of-use authorization under its local regime. The municipality also limits the number of authorized properties by commune, while national reforms expand registration, DPE and copropriété controls. A listing's rental history, platform badge or agent forecast does not prove that authorization transfers or that the building permits the use. Underwrite the home without short-stay income until the mairie, copropriété records and independent French counsel confirm the exact position in writing."
    ),
    lenses_intro=(
        "The Atlas pairs ten decision dimensions into five questions. Each lens connects the mountain proposition to the address, legal status, building and future buyer that make it usable."
    ),
    lenses=(
        DossierLens(
            "Make mountain life repeatable after the holiday week",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Chamonix's magnetism is earned. Few towns combine the Mont Blanc massif, international mountaineering culture and four-season outdoor access with a functioning urban centre. In Chamonix Centre, ordinary life can include a bakery, pharmacy, market, cinema, train, bus and restaurant without a long drive. That concentration matters more in retirement than lift proximity alone. It also brings peak-season congestion, visitor turnover, evening noise and competition for small homes. Spend ordinary weeks in November and during a busy winter period before deciding that a central address is either too intense or exactly the social energy required.",
                "Healthcare is credible but should not be overstated. Hôpitaux du Pays du Mont-Blanc states that Chamonix is a daytime non-scheduled-care centre opened only during high winter and summer seasons; for the current summer it runs from 11 July to 30 August 2026, 09:00–20:00. Sallanches provides the emergency department that is open all year, alongside the group's wider services. Call 15 before attending urgent care. Test the actual Sallanches route in winter, not the Chamonix hospital name: snow, traffic and driving ability change the answer. A buyer with an existing condition should ask the treating specialist where the required service is delivered and plan coverage outside the seasonal Chamonix opening.",
                "The micro-location changes retirement fit. Les Praz and Les Tines can combine a quieter residential rhythm with Mont-Blanc Express stops, but some homes sit on narrow roads or away from groceries. Argentière has a village core, rail and mountain identity, yet the upper valley is colder and farther from central services. Le Tour is more specialist still. Les Houches has schools, shops, rail and a broader residential texture, but it is not central Chamonix and travel between neighbourhoods remains weather-sensitive. Walk the grocery, station, doctor and waste route in snow; repeat it after dark and imagine one household member cannot drive."
            ),
        ),
        DossierLens(
            "Use Geneva access honestly—and choose the last mile",
            ("global_access", "foreigner_fit"),
            (
                "Geneva is a major strength, but it is road-led rather than a seamless airport rail link. Chamonix's official access page gives about 1 hour 15 minutes by road from Geneva and identifies regular coach and shuttle options. That is excellent for a high-alpine town, while border traffic, winter weather, flight timing and a missed transfer can materially lengthen the trip. Obtain a door-to-door plan for the exact address with luggage. A central apartment near Chamonix Sud differs from a chalet above Les Praz or a home in Le Tour even when a brochure gives each the same airport headline.",
                "Inside the valley, the Mont-Blanc Express is the structural asset. SNCF describes the year-round line between Saint-Gervais and Martigny, and the municipality states that it serves Les Houches, Chamonix, Argentière and Vallorcine. Chamonix Mobilité buses cover the valley from Servoz to Vallorcine with seasonal frequency changes. These networks can reduce car dependence, but they do not make every property transit-oriented. Check the actual timetable, climb, pavement, snow clearance and final distance. A station visible on a map may still be impractical with shopping, skis or limited mobility.",
                "Foreigner fit is strong at the service layer and more demanding in administration. Chamonix is accustomed to international residents, buyers and visitors, and English is common in the property and tourism economy. French contracts, copropriété minutes, planning documents, tax notices, insurance terms and mairie correspondence remain controlling. Use an independent notaire and, where the facts justify it, separate legal, tax and building advisers. Translation should cover the full documents, not only the agent's summary. The most internationally familiar address can still fail because the purchaser misunderstood a vote, easement, works programme or residence consequence."
            ),
            "winter-access",
        ),
        DossierLens(
            "Own the building and lawful use—not the brochure",
            ("ownership_clarity", "regulatory_safety"),
            (
                "France provides a familiar notarised ownership process, but the notaire is not a substitute for buyer-side investigation. Confirm identity, matrimonial or holding structure, title, easements, boundaries, planning, diagnostics, tax position and source of funds before the deposit becomes non-refundable. For a copropriété, read the règlement, recent meeting minutes, charges, arrears, insurance, reserve position and voted or proposed works. Older alpine buildings can concentrate roof, façade, lift, heating, insulation and water costs. A renovated apartment interior says little about the common fabric that determines comfort and future cash calls.",
                "Energy performance now has direct operating and rental consequences. Obtain the current DPE, its date, methodology and supporting bills; ask whether any studio correction or national rule change affects the displayed class. Examine heating type, ventilation, glazing, summer comfort and the feasibility of improving a unit inside a protected or jointly governed building. National reforms progressively constrain the letting of poorly performing homes, while a copropriété can limit tourist letting under defined conditions. Treat energy, building governance and intended use as one diligence stream rather than three unrelated checkboxes.",
                "Alpine hazard work must be address-specific. Géorisques identifies major risks for Chamonix-Mont-Blanc and links the municipal DICRIM, including avalanche, flood and ground-movement concerns. The current PLU became opposable in May 2026 and shapes development and permanent-housing policy. Overlay the official parcel information, planning zone and risk plans; then inspect roof shedding, drainage, retaining structures, access, tree and slope exposure, snow storage and evacuation. Obtain an insurer's written terms before signing. A home outside a dramatic-looking zone can still have access or water problems, while a mapped risk is not automatically uninsurable; the exact evidence controls."
            ),
            "building-governance",
        ),
        DossierLens(
            "Treat tourist rent as a permissioned business",
            ("rental_profit", "capital_upside"),
            (
                "Chamonix has real visitor demand, but a resort-wide yield is not decision-grade evidence. Since 1 May 2025, furnished tourist accommodation in the valley must be registered, and physical-person owners need change-of-use authorization under the local system. The municipality states a limit of one authorized property per physical person in Chamonix-Mont-Blanc and Les Houches, with different treatment elsewhere in the valley. National registration, DPE and copropriété rules also matter. Confirm the current rule, applicant, unit, commune, building and transfer position; do not assume an authorization or operating history follows the sale.",
                "If lawful use is confirmed, build a property-level account from evidence. Start with achieved bookings and bank receipts, then deduct manager commission, cleaning, linen, platform charges, utilities, heating, internet, snow clearing, insurance, taxe foncière, copropriété charges, maintenance, furniture renewal, vacancy and tax. Separate owner-use weeks from rentable inventory. Stress a poor snow period, a closed lift, access disruption and a change in local enforcement. A high gross nightly rate in February can coexist with a modest or negative owner return after a premium purchase price and year-round costs.",
                "Capital upside is supported by global recognition, limited valley land and a deep international audience, but it is not uniform. The 2026 Notaires observatory records a 9,760 EUR/m² median for old apartments in Chamonix-Mont-Blanc and a 1.776 million EUR median for old houses, while Les Houches old apartments were 7,910 EUR/m². Those completed-market medians show brand and commune differences; they do not value a particular view, building or chalet. Planning restrictions may support scarcity while also narrowing redevelopment and lawful use. Pay only for advantages that a future buyer can verify and finance."
            ),
        ),
        DossierLens(
            "Enter on completed evidence and preserve the exit",
            ("value_entry", "exit_liquidity"),
            (
                "The three current asking observations below illustrate product dispersion rather than market value. A 37 m² Savoy apartment asks 450,000 EUR and carries a DPE F. A Les Houches apartment asks 550,000 EUR; the page displays 78 m² but the seller text identifies 75 m² Loi Carrez, which is the comparison denominator used here. That source also conflicts on governance: its prose says a copropriété of 8 lots, while structured fields say the property is not subject to copropriété and separately cite 20 lots. A Les Praz chalet asks 3.2 million EUR; the seller states 342 m² total including a double garage and 290 m² habitable, so the narrower habitable figure is used here. Reconcile every denominator, title, copropriété record and accessory before comparing EUR/m².",
                "Value entry follows the next credible buyer pool. A well-run Chamonix Centre apartment near daily services can reach international, French and personal-use buyers, but small size, noise, energy class and charges can reduce the audience. Les Praz and Les Tines can attract long-hold lifestyle buyers when sun, access and building quality are real. Argentière and Le Tour appeal strongly to mountain users but form narrower submarkets. Les Houches can be less glamorous and more useful: a practical family apartment near transport may resell to permanent households as well as second-home buyers. The premium should reflect that pool, not an agent's destination average.",
                "Model the full acquisition-to-exit cash path. Ask the notaire for a written cost estimate for the exact old or new property rather than applying one universal percentage. Include financing and currency costs, diagnostics, surveys, insurance, taxes, copropriété calls, heating, energy works, snow and garden care, vacant-period management and eventual agency and tax consequences. Then model no tourist rent, flat nominal resale and a ten-percent price reduction. Before exchange, ask two agents who did not source the home which completed sales they would use, who would buy it next and how long a normal sale could take. The best Chamonix purchase is the address that remains useful without promotional assumptions."
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Chamonix combines a working alpine town with exceptional four-season mountain life; peak-season crowding and upper-valley seasonality change the experience by address.",
        "global_access": "Geneva road and coach access is unusually strong for the high Alps, while weather, borders and the property’s last mile weaken the headline journey.",
        "ownership_clarity": "France’s notarised process is familiar, but title, copropriété governance, diagnostics, planning and the buyer’s tax structure remain property-specific.",
        "regulatory_safety": "Valley registration and change-of-use rules, national DPE controls, copropriété powers and alpine hazards require written clearance for the exact unit.",
        "rental_profit": "Chamonix has deep visitor demand, but local authorization, high entry price, management, heating and seasonality prevent a credible resort-wide net yield.",
        "capital_upside": "Global brand and constrained land support selected homes, while planning, energy work and very high entry prices limit blanket appreciation claims.",
        "retirement_fit": "Chamonix Centre has daily services and a hospital site; Sallanches handles broader care, while upper-valley homes add winter and driving dependence.",
        "exit_liquidity": "Practical central and Les Houches homes reach broader pools; singular chalets and highly priced upper-valley assets need fewer, wealthier buyers.",
        "foreigner_fit": "Chamonix is internationally experienced, but French legal, tax, planning and copropriété documents still require independent professional interpretation.",
        "value_entry": "Notaires medians and current centre, Les Houches and Les Praz asks show that building, lawful use, energy and future audience matter more than one valley average.",
    },
    market_anchors=(
        {"location": "Chamonix-Mont-Blanc · old apartments", "evidence": "9,760 EUR/m²", "buyer_read": "Notaires de France 2025 completed-sale median, up 3.4% in one year. This is a commune median for old apartments, not a candidate valuation.", "source_label": "Notaires des Savoie 2026 observatory", "source_url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
        {"location": "Chamonix-Mont-Blanc · old houses", "evidence": "1,776,000 EUR", "buyer_read": "Notaires de France 2025 completed-sale median for old houses; no annual change was published. Size, land, condition and micro-location remain unseparated.", "source_label": "Notaires des Savoie 2026 observatory", "source_url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
        {"location": "Les Houches · old apartments", "evidence": "7,910 EUR/m²", "buyer_read": "Notaires de France 2025 completed-sale median, up 10.1% in one year. It is a separate commune benchmark, not a Chamonix Centre substitute.", "source_label": "Notaires des Savoie 2026 observatory", "source_url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
    ),
    micro_locations_intro=(
        "Use four operating patterns rather than a single Chamonix average. Confirm the commune, train or bus stop, winter walk, sun, noise, healthcare route, tourist-let position, DPE, copropriété, planning and hazards for the exact address."
    ),
    micro_locations=(
        {"name": "Chamonix Centre", "best_for": "Car-light daily life", "daily_life": "Shops, restaurants, buses, rail and hospital site", "diligence": "Noise, DPE, copropriété, charges and tourist-let status"},
        {"name": "Les Praz / Les Tines", "best_for": "Calmer valley living", "daily_life": "Rail stops, golf and residential streets", "diligence": "Sun, gradient, snow, station walk, planning and building work"},
        {"name": "Argentière / Le Tour", "best_for": "Mountain-first ownership", "daily_life": "Upper-valley village and specialist outdoor access", "diligence": "Winter access, services, heating, hazards and narrower exit"},
        {"name": "Les Houches", "best_for": "Residential value and family pool", "daily_life": "Separate commune with shops, schools, rail and bus", "diligence": "Exact neighbourhood, authorization, transport and completed comparables"},
    ),
    checklist=(
        "Confirm French residence, tax residence, healthcare and cross-border estate planning before purchase.",
        "Choose Chamonix Centre, Les Praz / Les Tines, Argentière / Le Tour or Les Houches by daily routine.",
        "Obtain title, easements, planning, diagnostics, DPE, copropriété minutes, charges and voted works.",
        "Clear registration, change-of-use authorization and building rules before underwriting tourist income.",
        "Travel the Geneva, station, grocery and required hospital route in winter and shoulder season.",
        "Screen Géorisques, the current PLU and parcel plans for avalanche, flood, slope, access and insurance.",
        "Reconcile portal Surface, Loi Carrez or habitable area, land, accessories and matched completed sales.",
        "Model five-year carrying and a conservative resale without tourist rent, then identify the future buyer.",
    ),
    references_intro=(
        "Legal, residence, healthcare, planning, tourist-let, transport, hazard, completed-market, FX and listing claims were reviewed on 23 August 2026. The next scheduled review is 23 February 2027, or sooner after any cited legal, municipal, PLU, DPE, transport, hospital, hazard, market or listing change. Recheck every source and obtain independent French notarial, legal, tax, immigration, planning, building, insurance and healthcare advice for the exact buyer and property. Listings are dated asking observations, not proof of availability, area, title, lawful use, condition or completed value."
    ),
    references=(
        {"label": "France-Visas: long-stay visitor route", "url": "https://france-visas.gouv.fr/en/web/france-visas/tourist-or-private-visit"},
        {"label": "Assurance Maladie: universal health protection", "url": "https://www.ameli.fr/assure/droits-demarches/principes/protection-universelle-maladie"},
        {"label": "Chamonix: furnished tourist accommodation rules", "url": "https://www.chamonix.fr/demarches/logement-jhabitat-cham/meubles-de-tourisme-2/"},
        {"label": "Chamonix: current tourist-let compliance notice", "url": "https://www.chamonix.fr/actualites/mise-en-conformite-des-meubles-de-tourisme-ne-tardez-pas/"},
        {"label": "Service Public: 2024 furnished-tourist-let reforms", "url": "https://www.service-public.fr/entreprendre/actualites/A17883"},
        {"label": "Chamonix: current PLU", "url": "https://www.chamonix.fr/demarches/urbanisme/documents-opposables/plu/"},
        {"label": "Géorisques: Chamonix-Mont-Blanc commune report", "url": "https://www.georisques.gouv.fr/mes-risques/connaitre-les-risques-pres-de-chez-moi/rapport2/74056/CHAMONIX-MONT-BLANC"},
        {"label": "Hôpitaux du Pays du Mont-Blanc", "url": "https://www.hpmb.fr/hopital/presentation/"},
        {"label": "Hôpitaux du Pays du Mont-Blanc: Chamonix urgent-care opening", "url": "https://www.hpmb.fr/poles/urgences-medecine-montagne-sport/urgences-chamonix/"},
        {"label": "Chamonix: urban transport", "url": "https://www.chamonix.fr/demarches/viacham-et-mobilite/transport-urbain/"},
        {"label": "SNCF TER: Mont-Blanc Express", "url": "https://www.ter.sncf.com/auvergne-rhone-alpes/decouvrir/trains-touristiques/mont-blanc-express"},
        {"label": "Chamonix: access to the valley", "url": "https://www.chamonix.fr/la-commune/le-territoire/acces-et-deplacement/venir-a-chamonix-mont-blanc/"},
        {"label": "Notaires des Savoie: 2026 property observatory", "url": "https://chambre-interdepartementale-de-savoie.notaires.fr/wp-content/uploads/2026/04/Observatoire-de-limmo-des-Notaires-des-Savoie-2026.pdf"},
        {"label": "Immobilier.notaires.fr: Chamonix prices", "url": "https://www.immobilier.notaires.fr/fr/prix-immobilier?codeInsee=74056&neuf=false&typeLocalisation=COMMUNE"},
        {"label": "European Central Bank: euro reference rates", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"},
        {"label": "Chamonix Savoy apartment asking observation", "url": "https://proprietes.lefigaro.fr/annonces/appartement-haute%2Bsavoie-rhone%2Balpes-france/107450633/"},
        {"label": "Les Houches apartment asking observation", "url": "https://proprietes.lefigaro.fr/annonces/appartement-haute%2Bsavoie-rhone%2Balpes-france/95388787/"},
        {"label": "Les Praz chalet asking observation", "url": "https://proprietes.lefigaro.fr/annonces/chalet-haute%2Bsavoie-rhone%2Balpes-france/97870885/"},
    ),
    images=(
        DossierImage("valley-life", "/assets/chamonix-valley-life.webp", "Older couple walking through Chamonix Centre with Mont Blanc above the town", "Chamonix works best when the mountain address also supports ordinary daily life.", "hero"),
        DossierImage("winter-access", "/assets/chamonix-winter-access.webp", "Mont-Blanc Express train serving a snowy Chamonix valley station", "The station, winter walk and last mile matter as much as the valley map.", "wide"),
        DossierImage("building-governance", "/assets/chamonix-building-governance.webp", "Residents entering a well-kept alpine apartment building in Chamonix", "Copropriété condition, energy and lawful use determine the ownership experience.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Chamonix through five destination lenses",
    assessment_intro="Here’s how Chamonix scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current asking observations compare a small central apartment, a Les Houches family apartment and a Les Praz chalet. EUR is primary; USD uses the recorded ECB reference rate. Each area basis is reproduced and qualified rather than treated as verified legal internal area.",
    market_anchors_intro="These Notaires de France 2025 completed-sale medians distinguish Chamonix apartments, Chamonix houses and Les Houches apartments. They are broad commune evidence—not current asks or valuations—and do not isolate condition, view, building, lawful use or exact micro-location.",
    orientation_groups=(
        DossierOrientationGroup("Lower valley to town", (("Les Houches", "Residential value and rail"), ("Chamonix Centre", "Services and transport core"), ("Les Praz / Les Tines", "Calmer northern neighbourhoods"))),
        DossierOrientationGroup("Upper valley", (("Argentière", "Village and Grands Montets"), ("Montroc / Le Tour", "Mountain-first outer base"), ("Vallorcine", "Separate commune toward Martigny"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm current rail and bus timetables, winter access, the commune boundary and the exact last mile.",
    country_guide_url="/countries/france-property/",
    country_guide_label="France property guide",
    rail_comparison="Compare Chamonix with the full Atlas.",
)


LAKE_TAHOE_DOSSIER = PremiumDossierSpec(
    destination_id="lake-tahoe",
    title="Lake Tahoe Retirement Property Dossier",
    description="Assess Lake Tahoe retirement property across California and Nevada through daily life, access, ownership, tax, rental permits, wildfire, insurance, value, resale, and current listings.",
    h1="Lake Tahoe: choose the jurisdiction before the view",
    lede="Lake Tahoe is not one retirement market. South Lake Tahoe offers the basin's broadest everyday service base; Tahoe City and Kings Beach anchor the north shore; Truckee adds a larger year-round town beyond the basin; Incline Village and Crystal Bay offer Nevada-side ownership and amenity structures; Stateline and Glenbrook sit under a different county permit system again. The lake-and-mountain lifestyle is exceptional, but every attractive address carries a specific combination of wildfire, insurance, snow, access, rental and resale risk. This dossier separates those choices before comparing homes.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-23",
    date_reviewed="2026-08-23",
    verdict_paragraphs=(
        "The verdict is selectively positive. Lake Tahoe suits an active buyer who values four-season mountain-and-water life, can carry a high-cost property without optimistic rent, and is willing to choose a jurisdiction before choosing the view. South Lake Tahoe provides the clearest full-service base and a deeper lower-priced segment. Tahoe City, Kings Beach and the west shore offer stronger north-shore character with more fragmented services. Truckee is not on the lake, but often provides the most complete year-round town pattern. Incline Village and Crystal Bay combine Nevada administration with resident amenities and premium pricing. Stateline and Glenbrook offer a quieter east-shore proposition under Douglas County rules.",
        "Foreign ownership does not create U.S. immigration status, health coverage or tax residence. California Civil Code section 671 allows a person to take, hold and dispose of property regardless of citizenship status; Nevada NRS 111.055 allows nonresident aliens, persons and corporations to hold real property. Those state rules do not settle federal sanctions, entity eligibility, title, financing, beneficial ownership, FIRPTA withholding, rental-income taxation or U.S. estate exposure, all of which require independent advice. California and Nevada also diverge on property-tax mechanics, state income tax and local administration. A Nevada address should never be bought as a tax slogan: residence depends on facts, while a second home can remain exposed to taxes and obligations elsewhere. Confirm the buyer, entity, intended occupancy and cross-border estate plan before signing.",
        "Proceed in order. Establish immigration, healthcare, tax, estate and financing capacity. Select South Shore, North/West Shore, Incline/Crystal Bay or Stateline/Glenbrook for ordinary life, not holiday appeal. Confirm the parcel's city, county and TRPA position; lawful use; title; HOA; access; utilities; permits; hazard maps; defensible space; evacuation route; snow systems; insurance binder and realistic recurring cost. If rent matters, verify the exact permit path and building rules in writing. Then identify the next buyer and model a slow exit. Tahoe can be a superb home, but it is a poor place to improvise operations after closing.",
    ),
    lenses_intro="The five paired lenses below turn Lake Tahoe's Atlas scores into jurisdiction and property choices. The full ten-factor assessment appears once in the score table.",
    lenses=(
        DossierLens(
            "Build a life that works beyond the holiday week",
            ("lifestyle_magnetism", "retirement_fit"),
            (
                "Lake Tahoe's lifestyle case is unusually durable: alpine water, skiing, hiking, cycling, boating and strong seasonal light all belong to the same geography. The practical version differs by address. South Lake Tahoe has supermarkets, restaurants, local government and Barton Memorial Hospital within a recognisable town. Tahoe City is compact and attractive but smaller; Kings Beach feels more everyday and reaches Truckee services by road. Incline Village has local shops, recreation and a community hospital, while Crystal Bay is quieter and thinner. Stateline adds entertainment and resort services; Glenbrook is secluded. A beautiful lake view does not establish a useful Tuesday in November.",
                "Healthcare is meaningful but regional. California's HCAI lists Barton Memorial in South Lake Tahoe as an open general acute-care hospital with basic emergency service; El Dorado County identifies it as a Level III trauma centre with 24-hour emergency care. Tahoe Forest Hospital in Truckee operates a 24/7 emergency room, and Tahoe Forest Health System maps urgent care in Truckee and Tahoe City plus emergency care in Incline Village. Those facilities strengthen the retirement case, but specialist pathways can reach Reno, Sacramento or elsewhere. Confirm network coverage, ambulance route, winter transfer conditions and the household plan if one person cannot drive.",
                "Altitude, smoke, snow and terrain should influence the floor plan. A steep driveway above Tahoe City, stairs to a Stateline condo, icy entry in Incline Village or remote west-shore house can become limiting after injury. Look for main-level living, reliable heating, cooling or filtration, backup power, safe roof-shed zones and a maintainable walk from parking. Spend ordinary weeks in May and November, buy groceries, reach appointments and return after dark. Ask who checks heat, leaks, trees and snow when the home is empty. Retirement fit comes from repeatable daily life and a credible support network, not the number of recreation options.",
            ),
            "winter-operations",
        ),
        DossierLens(
            "Measure the passes, the last mile and the state line",
            ("global_access", "foreigner_fit"),
            (
                "Reno-Tahoe International Airport is the most obvious gateway for the north and east sides, and its official ground-transport page lists taxis, private vehicles and Tahoe-oriented operators. The South Shore can also be approached from Reno or from Sacramento over U.S. 50. North and west shore buyers often use Interstate 80 and Truckee before turning toward the lake. None of those routes is a guaranteed journey time. Caltrans applies R1–R3 chain controls in mountain areas and directs drivers to QuickMap for current restrictions; check I-80 and U.S. 50 conditions before every winter journey. Test the exact door-to-airport route with luggage, a storm forecast and a missed connection.",
                "Local movement remains car-led. South Lake Tahoe has the densest errands and some transit, but residential areas spread well beyond a walkable core. Tahoe City and Kings Beach have compact centres yet daily services are separated along State Route 28. Truckee has a stronger year-round service base but sits away from the shoreline. Incline Village concentrates useful amenities; hillside and Crystal Bay properties can still be steep and vehicle-dependent. Stateline may work for a resort stay without a car, while Glenbrook usually does not. Confirm winter ploughing responsibility, private-road agreements, parking, shuttle seasonality and whether the household can function through a multi-day closure.",
                "Foreigner fit is strong in language and professional availability but weaker in cross-border simplicity. The region has brokers, lawyers, accountants, managers and insurers accustomed to second homes, yet California and Nevada documents, tax treatment, licensing and court jurisdictions differ. Federal visitor status remains separate from property ownership, and U.S. real estate can produce rental filings, FIRPTA withholding on sale and estate-tax consequences for a nonresident. Obtain independent counsel in the state of the property and coordinated home-country advice. Appoint a reliable local representative to receive notices and inspect the asset; a familiar language does not make an absentee mountain home passive.",
            ),
        ),
        DossierLens(
            "Own the parcel—and prove every layer of use",
            ("ownership_clarity", "regulatory_safety"),
            (
                "Title can be straightforward, but Lake Tahoe adds regional planning and property-specific constraints. TRPA explains that projects can require its review, local approval or both, with extra scrutiny around shorezone, land coverage and development rights. Before closing, reconcile the deed, survey, access, easements, boundaries, water, sewer or septic, permits, legal floor area, additions, retaining walls, tree work and any TRPA file. Condominiums and planned communities add declarations, budgets, reserves, insurance allocation, litigation, rental restrictions, amenity rights and special assessments. Incline Village resident amenities, Tahoe Keys waterfront systems and private-road communities each require their own governing package.",
                "Short-term use is fragmented. South Lake Tahoe regulates vacation-home rentals under Ordinance 2026-1203, effective 23 April 2026, and the City's current page directs applicants to confirm property eligibility; the exact zone, cap and permit status must be rechecked before relying on rental. Placer County requires an STR permit and transient-occupancy-tax certificate and operates a cap framework. Washoe County maintains Article 319, permits, inspections and tier procedures for Incline Village and Crystal Bay. Douglas County permits vacation rentals of 28 days or fewer in Tahoe Township, caps permits at 600 and applies neighbourhood density limits. HOA rules may be stricter than government. Verify the parcel, permit availability, transferability, inspection, local-contact, occupancy, parking and tax position in writing.",
                "Environmental regulation is part of ownership rather than a separate research task. Shoreline work, coverage, grading, trees, drainage and redevelopment may involve TRPA and the local jurisdiction. A listing's remodel, detached studio, deck or converted room is not lawful merely because it exists or appears in MLS area. Ask for approved plans, final inspections, TRPA records and a current rebuild-cost analysis. On older cabins, inspect foundation, roof, electrical, plumbing, insulation, freeze history and unpermitted space. On resort or condominium product, read master insurance exclusions and loss-assessment exposure. Regulatory safety comes from a clean documentary chain for the intended use, not from the attractiveness of the building.",
            ),
            "wildfire-diligence",
        ),
        DossierLens(
            "Underwrite wildfire, insurance and rent as one operation",
            ("rental_profit", "capital_upside"),
            (
                "There is no defensible basin-wide net-yield figure. Visitor demand can be strong in ski weeks and summer, but lawful supply, rates, occupancy and costs vary sharply by jurisdiction and building. A tourist-core South Lake Tahoe residence, a Placer County home, an Incline Village condo and a Douglas County VHR are different businesses. Start with the permit and HOA, then obtain trailing property-level statements, bank deposits, tax returns and the future management contract. Deduct management, cleaning, booking fees, utilities, hot tub, snow, defensible space, insurance, tax, repairs, furniture, HOA charges and owner blocks. Compare with long-term rent and no rental before assigning value to income.",
                "Insurance belongs in the offer contingency. CAL FIRE's current hazard maps distinguish hazard from property-specific risk and direct buyers to address-level zones. California's Department of Insurance says the FAIR Plan is an insurer of last resort with limited perils and may require a separate differences-in-conditions policy. Nevada-side availability and terms require separate quotations. Obtain a full binder—not an estimate—for the exact ownership, occupancy, rental and rebuild basis. Reconcile dwelling limits, wildfire, smoke, water, sewer backup, flood, earthquake, liability, ordinance-and-law, loss assessment and vacancy. A cheap premium inherited from a seller, an HOA master policy or a lender indication is not proof of durable coverage.",
                "Capital upside is plausible but segmented. Q2 2026 public MLS-fed reports showed very different single-family medians and transaction counts across South Shore, North/West Shore and Incline Village/Crystal Bay. Those signals demonstrate demand and dispersion, not guaranteed appreciation. Scarce lakefront, low-elevation Incline Village, Tahoe City character, South Shore entry product and Truckee year-round utility reach different buyers. Climate, insurance, permits and financing can narrow the future pool even when lifestyle demand remains strong. Buy an address that is easy to explain, insure, maintain and access. Model flat prices, higher insurance and a longer marketing period; the personal-use case should survive that scenario.",
            ),
        ),
        DossierLens(
            "Enter below the romance and preserve the exit",
            ("value_entry", "exit_liquidity"),
            (
                "Lake Tahoe's entry range is wide enough to make one average misleading. A small South Lake Tahoe townhouse may enter below a detached north-shore home; a Tahoe City architectural property can command a land-and-design premium; an Incline Village house may add amenity rights and Nevada-side demand; true lakefront can trade in another market entirely. The three listings below are direct current asks chosen to show that dispersion. Their median asking price and median asking price per square metre support the Atlas planning inputs, but neither is a valuation. Reconcile every candidate with recent completed sales of the same property type, jurisdiction, condition and access pattern.",
                "Ownership costs begin before closing. California and Nevada use different property-tax systems; California's Board of Equalization explains the one-percent base rate plus voter-approved debt and reassessment on change of ownership, while Nevada's Department of Taxation says county rates remain subject to a state-imposed cap. Neither source supplies a complete parcel bill. Add title, escrow, legal, inspections, survey, lender charges, insurance, TRPA or permit work, HOA contributions, snow, trees, utilities, repairs and tax advice. The calculator's two-percent acquisition allowance is a planning assumption, not a statutory tax rate or closing quote. Obtain a buyer-specific closing statement and five-year cash-flow model.",
                "Exit liquidity depends on the next buyer's friction. South Lake Tahoe's broader price ladder and service base can support more buyers; Tahoe City and Kings Beach retain north-shore demand but winter access and inventory vary; Incline Village attracts buyers seeking amenities and Nevada administration but often at a higher entry point; Crystal Bay and Glenbrook can be exceptionally thin. Unusual architecture, steep drives, private roads, uncertain permits, weak insurance, deferred wildfire work or heavy HOA charges reduce the pool. Before making an offer, ask two agents who did not source the property how they would resell it, to whom, and with which completed comparables. Preserve optionality at purchase rather than hoping scarcity solves every flaw.",
            ),
        ),
    ),
    score_reads={
        "lifestyle_magnetism": "Tahoe combines alpine water and four-season recreation; South Lake Tahoe and Truckee provide the strongest ordinary-life counterweight to resort seasonality.",
        "global_access": "Reno, Sacramento and Bay Area access are credible, but Tahoe's last mile crosses storm-sensitive passes and remains address- and season-dependent.",
        "ownership_clarity": "California Civil Code section 671 and Nevada NRS 111.055 support broad Tahoe property holding, while federal, entity, title, tax and estate checks still apply.",
        "regulatory_safety": "South Lake Tahoe, Placer, Washoe and Douglas apply different rental systems, while TRPA and HOA controls add parcel-level constraints.",
        "rental_profit": "Tahoe has strong peak demand where rentals are lawful, but permits, management, snow, insurance and owner use prevent a defensible basin-wide net yield.",
        "capital_upside": "South Shore, North/West Shore and Incline closed-market signals show durable demand but also large price, volume and buyer-pool differences.",
        "retirement_fit": "Barton, Tahoe Forest and Incline Village emergency facilities support Tahoe retirement, while specialist care, altitude, snow and driving remain constraints.",
        "exit_liquidity": "South Lake Tahoe reaches a broader entry pool; distinctive Tahoe City, Crystal Bay and Glenbrook assets can require a slower specialist exit.",
        "foreigner_fit": "Tahoe offers English-language professional depth, but U.S. immigration, rental tax, FIRPTA, estate exposure and absentee operations remain material.",
        "value_entry": "Tahoe asks range from South Lake Tahoe townhouses to premium Tahoe City and Incline homes; value depends on use, insurance and future buyer depth.",
    },
    market_anchors=(
        {"location": "South Shore single-family homes", "evidence": "$810,000 median", "buyer_read": "Q2 2026 closed market: 73 sales and 75 average days on market. A broad public market signal—not a valuation for a specific home.", "source_label": "Sierra Sotheby's / MLS-fed Q2 2026 report", "source_url": "https://marketupdates.sothebysrealty.com/marketupdate/sierrasir/south_shore"},
        {"location": "North/West Shore single-family homes", "evidence": "$1.23 million median", "buyer_read": "Q2 2026 closed market: 64 sales and 124 average days on market. The geography combines distinct communities and is not a valuation.", "source_label": "Sierra Sotheby's / MLS-fed Q2 2026 report", "source_url": "https://marketupdates.sothebysrealty.com/marketupdate/sierrasir/north_west_shore"},
        {"location": "Incline Village / Crystal Bay single-family homes", "evidence": "$2.5 million median", "buyer_read": "Q2 2026 closed market: 50 sales and 99 average days on market. Thin luxury submarkets can move the median; this is not a valuation.", "source_label": "Sierra Sotheby's / MLS-fed Q2 2026 report", "source_url": "https://marketupdates.sothebysrealty.com/marketupdate/sierrasir/incline_village_crystal_bay"},
    ),
    micro_locations_intro="Choose the operating system before the building. These four patterns group daily life and regulation; they are not price zones. Confirm the exact parcel's city or county, state, TRPA status, hazard layers, road, utilities, HOA, lawful use and current permit availability.",
    micro_locations=(
        {"name": "South Lake Tahoe / Meyers", "best_for": "Broadest services and entry range", "daily_life": "Barton Hospital, groceries and town services; Meyers is quieter and more car-led.", "diligence": "City versus El Dorado boundary, current VHR zone and cap, insurance, snow and traffic."},
        {"name": "Tahoe City / Kings Beach / West Shore", "best_for": "North-shore character and lake access", "daily_life": "Compact centres with Tahoe Forest urgent care in Tahoe City; Truckee supports deeper services.", "diligence": "Placer STR permit, private roads, winter access, wildfire, shoreline/TRPA and thin submarkets."},
        {"name": "Incline Village / Crystal Bay", "best_for": "Nevada-side base with resident amenities", "daily_life": "Local shops, recreation and Incline emergency care; Reno and Truckee broaden services.", "diligence": "Washoe STR tier, amenity eligibility, HOA, tax facts, insurance, steep access and resale depth."},
        {"name": "Stateline / Zephyr Cove / Glenbrook", "best_for": "East-shore and Nevada resort access", "daily_life": "Stateline is visitor-led; Glenbrook is quieter, more private and more driving-dependent.", "diligence": "Douglas VHR cap and density, private community rules, highway access, wildfire and healthcare route."},
    ),
    checklist=(
        "Confirm immigration, healthcare, U.S. tax, estate, financing and ownership structure before selecting a state.",
        "Resolve the parcel's state, city or county, TRPA jurisdiction, title, survey, access, utilities and lawful improvements.",
        "Obtain written current rental eligibility from the jurisdiction and HOA; verify permit transfer, occupancy, parking, tax and local-contact duties.",
        "Overlay current wildfire, flood and evacuation maps; inspect defensible space, trees, roof, vents, drainage and private-road access.",
        "Bind property-specific insurance for the exact occupancy, rental, rebuild, liability and HOA loss-assessment exposure before contingencies expire.",
        "Travel airport, hospital, grocery and evacuation routes in winter; confirm ploughing, chain controls, parking and backup power.",
        "Reconcile HOA budgets, reserves, master insurance, assessments, amenity rights, litigation, rental rules and snow responsibility.",
        "Compare completed like-for-like sales, model five-year cash outlay and a slow insured resale, then obtain a buyer-specific closing statement.",
    ),
    references_intro="Legal, tax, title, planning, rental, health, transport, hazard, insurance, market and listing claims were reviewed on 23 August 2026. Recheck every time-sensitive source no later than 23 February 2027 and immediately after any tax, immigration, estate, zoning, rental, TRPA, insurance, hazard, transport, healthcare, market-data or listing change. Obtain current U.S. federal, California or Nevada legal, tax, title, planning, insurance and immigration advice for the exact buyer, entity, parcel and intended use. Asking evidence and public market signals are not valuations or availability guarantees.",
    references=(
        {"label": "United States property guide", "url": "/countries/united-states-property/"},
        {"label": "U.S. Department of State: visitor visa", "url": "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html"},
        {"label": "California Civil Code section 671: property rights regardless of citizenship", "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=671."},
        {"label": "Nevada NRS 111.055: nonresident property holding", "url": "https://www.leg.state.nv.us/nrs/nrs-111.html#NRS111Sec055"},
        {"label": "IRS: FIRPTA withholding", "url": "https://www.irs.gov/individuals/international-taxpayers/firpta-withholding"},
        {"label": "IRS: nonresident U.S. real-property income", "url": "https://www.irs.gov/individuals/international-taxpayers/nonresident-aliens-real-property-located-in-the-us"},
        {"label": "IRS: nonresident estates with U.S. assets", "url": "https://www.irs.gov/individuals/international-taxpayers/some-nonresidents-with-us-assets-must-file-estate-tax-returns"},
        {"label": "South Lake Tahoe: current vacation-home-rental programme", "url": "https://www.cityofslt.us/2510/Vacation-Home-Rentals"},
        {"label": "Placer County: current short-term-rental programme", "url": "https://www.placer.ca.gov/6109/Short-Term-Rental-Program"},
        {"label": "Washoe County: current short-term-rental programme", "url": "https://www.washoecounty.gov/csd/planning_and_development/short_term_rentals/index.php"},
        {"label": "Douglas County: current vacation-home-rental programme", "url": "https://www.douglascountynv.gov/government/departments/community-development/vacation-home-rentals"},
        {"label": "Douglas County: VHR permit cap and application", "url": "https://www.douglascountynv.gov/GOVERNMENT/departments/community-development/vacation-home-rentals/apply-permitting-process-for-new-vhr/"},
        {"label": "TRPA: 2024 permitting procedure manual", "url": "https://www.trpa.gov/wp-content/uploads/documents/Permitting-Procedure-Manual.pdf"},
        {"label": "CAL FIRE: current Fire Hazard Severity Zones", "url": "https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones"},
        {"label": "California Department of Insurance: residential insurance and FAIR Plan", "url": "https://www.insurance.ca.gov/01-consumers/105-type/5-residential/"},
        {"label": "California Board of Equalization: property-tax assessment", "url": "https://www.boe.ca.gov/pdf/pub800-10.pdf"},
        {"label": "Nevada Department of Taxation: locally assessed property-tax FAQ", "url": "https://tax.nv.gov/faqs/locally-assessed-property-tax-faqs/"},
        {"label": "Barton Memorial Hospital: California HCAI profile", "url": "https://hcai.ca.gov/facility/barton-memorial-hospital/"},
        {"label": "El Dorado County EMS: Barton trauma and 24-hour emergency service", "url": "https://www.eldoradocounty.ca.gov/Public-Safety-Justice/Emergency-Medical-Services/Contractors/Base-Hospitals"},
        {"label": "Tahoe Forest Hospital: 24/7 emergency department", "url": "https://www.tfhd.com/location/tahoe-forest-hospital/"},
        {"label": "Tahoe Forest Health: North Shore urgent and emergency care map", "url": "https://www.tfhd.com/services/urgent-care/"},
        {"label": "Caltrans: current chain controls", "url": "https://dot.ca.gov/travel/winter-driving-tips/chain-controls"},
        {"label": "Reno-Tahoe Airport: current ground transportation", "url": "https://www.renoairport.com/parking-transportation/transportation/"},
        {"label": "Q2 2026 South Shore closed-market signal", "url": "https://marketupdates.sothebysrealty.com/marketupdate/sierrasir/south_shore"},
        {"label": "Q2 2026 North/West Shore closed-market signal", "url": "https://marketupdates.sothebysrealty.com/marketupdate/sierrasir/north_west_shore"},
        {"label": "Q2 2026 Incline Village / Crystal Bay closed-market signal", "url": "https://marketupdates.sothebysrealty.com/marketupdate/sierrasir/incline_village_crystal_bay"},
        {"label": "South Lake Tahoe Wildwood asking observation", "url": "https://www.chaseinternational.com/p/1200-Wildwood-Avenue-South-Lake-Tahoe-CA-96150/dmgid_186496709"},
        {"label": "Tahoe City North Lake Boulevard asking observation", "url": "https://davebest.chaseinternational.com/p/1455-North-Lake-Boulevard-Tahoe-City-CA-96145/dmgid_187698061?oid=216100012"},
        {"label": "Incline Village Dorothy Court asking observation", "url": "https://www.sereno.com/1018809/608-dorothy-court-incline-village-nevada-89451-ivmls"},
    ),
    images=(
        DossierImage("shoreline", "/assets/lake-tahoe-shoreline-hero.webp", "Mature residents walking beside Lake Tahoe on a calm alpine morning", "The strongest Tahoe purchase supports ordinary life as well as the view.", "hero"),
        DossierImage("winter-operations", "/assets/lake-tahoe-winter-operations.webp", "Resident clearing snow outside a Lake Tahoe home while a plough maintains the road", "Winter access, heat and snow service are recurring ownership systems.", "wide"),
        DossierImage("wildfire-diligence", "/assets/lake-tahoe-wildfire-diligence.webp", "Homeowner and inspector reviewing defensible space at a wooded Lake Tahoe house", "Insurance begins with the exact building, vegetation and operating plan.", "wide"),
    ),
    nav_items=(("verdict", "Verdict"), ("lenses", "Five destination lenses"), ("scores", "Atlas assessment"), ("listings", "Representative listings"), ("locations", "Where to look"), ("checklist", "Buyer checklist"), ("sources", "References")),
    lenses_heading="Lake Tahoe through five destination lenses",
    assessment_intro="Here’s how Lake Tahoe scores on the ten factors that matter most when choosing a long-term home abroad.",
    listings_intro="Three current direct asking observations compare a South Lake Tahoe townhouse, a Tahoe City architectural home and an Incline Village house. USD is both local and comparison currency; each area is converted from the MLS-stated living square feet.",
    market_anchors_intro="These are public market signals—not valuations. They cover Q2 2026 single-family closings across three different geographies and do not isolate waterfront, condition, amenities, insurance, lawful use or exact address.",
    orientation_groups=(
        DossierOrientationGroup("North and west", (("Reno-Tahoe Airport", "Regional gateway"), ("Truckee", "Year-round service town"), ("Kings Beach", "North-shore daily life"), ("Tahoe City / West Shore", "Lake communities and Placer rules"))),
        DossierOrientationGroup("Nevada east to South Shore", (("Incline Village / Crystal Bay", "Washoe County and amenities"), ("Glenbrook / Zephyr Cove", "Douglas County east shore"), ("Stateline", "Nevada resort edge"), ("South Lake Tahoe / Meyers", "Broadest basin service base"))),
    ),
    orientation_caption="Orientation schematic—not to scale. Confirm the state and jurisdiction, current road and chain controls, airport transfer, hospital route and exact last mile.",
    country_guide_url="/countries/united-states-property/",
    country_guide_label="United States property guide",
    rail_comparison="Compare Lake Tahoe with the full Atlas.",
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
    CROATIA_ISTRIA_DALMATIA_DOSSIER.destination_id: CROATIA_ISTRIA_DALMATIA_DOSSIER,
    QUEENSTOWN_DOSSIER.destination_id: QUEENSTOWN_DOSSIER,
    PHUKET_KOH_SAMUI_DOSSIER.destination_id: PHUKET_KOH_SAMUI_DOSSIER,
    VANCOUVER_ISLAND_VICTORIA_DOSSIER.destination_id: VANCOUVER_ISLAND_VICTORIA_DOSSIER,
    DUBAI_DOSSIER.destination_id: DUBAI_DOSSIER,
    BALI_DOSSIER.destination_id: BALI_DOSSIER,
    DOLOMITES_SOUTH_TYROL_DOSSIER.destination_id: DOLOMITES_SOUTH_TYROL_DOSSIER,
    CHAMONIX_DOSSIER.destination_id: CHAMONIX_DOSSIER,
    LAKE_TAHOE_DOSSIER.destination_id: LAKE_TAHOE_DOSSIER,
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

    if spec.property_anchor_indexes:
        if len(spec.property_anchor_indexes) != 3:
            raise ValueError(f"{spec.destination_id} requires three property-anchor associations")
        indexes = [index for index in spec.property_anchor_indexes if index is not None]
        if (
            len(indexes) != len(set(indexes))
            or any(index < 0 or index >= len(spec.market_anchors) for index in indexes)
        ):
            raise ValueError(f"{spec.destination_id} has invalid property-anchor associations")

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
validate_premium_dossier(CROATIA_ISTRIA_DALMATIA_DOSSIER)
validate_premium_dossier(QUEENSTOWN_DOSSIER)
validate_premium_dossier(DUBAI_DOSSIER)
validate_premium_dossier(BALI_DOSSIER)
validate_premium_dossier(DOLOMITES_SOUTH_TYROL_DOSSIER)
validate_premium_dossier(CHAMONIX_DOSSIER)
