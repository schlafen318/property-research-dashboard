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


PREMIUM_DESTINATION_DOSSIERS = {
    FUKUOKA_ITOSHIMA_DOSSIER.destination_id: FUKUOKA_ITOSHIMA_DOSSIER,
    ALGARVE_CASCAIS_DOSSIER.destination_id: ALGARVE_CASCAIS_DOSSIER,
    MADEIRA_DOSSIER.destination_id: MADEIRA_DOSSIER,
    MALAGA_COSTA_DEL_SOL_DOSSIER.destination_id: MALAGA_COSTA_DEL_SOL_DOSSIER,
    LAKE_COMO_DOSSIER.destination_id: LAKE_COMO_DOSSIER,
    HAKONE_IZU_DOSSIER.destination_id: HAKONE_IZU_DOSSIER,
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
