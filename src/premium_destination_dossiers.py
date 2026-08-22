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


PREMIUM_DESTINATION_DOSSIERS = {
    FUKUOKA_ITOSHIMA_DOSSIER.destination_id: FUKUOKA_ITOSHIMA_DOSSIER,
    ALGARVE_CASCAIS_DOSSIER.destination_id: ALGARVE_CASCAIS_DOSSIER,
    MADEIRA_DOSSIER.destination_id: MADEIRA_DOSSIER,
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
