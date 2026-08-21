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
    description="A foreign-buyer dossier for comparing retirement property in Fukuoka and Itoshima.",
    h1="Fukuoka / Itoshima: city ease, coast within reach",
    lede="A practical base for buyers who want Japanese city services without giving up access to the coast.",
    author="Global Home Atlas Research Team",
    date_published="2026-08-21",
    date_reviewed="2026-08-21",
    verdict_paragraphs=(
        "Fukuoka and Itoshima suit buyers who put year-round daily life before a speculative rental story.",
    ),
    lenses_intro="Five paired lenses connect the Atlas score to the life and property decision.",
    lenses=(
        DossierLens(
            "Live well between city and coast",
            ("lifestyle_magnetism", "retirement_fit"),
            ("Fukuoka supplies the daily-life infrastructure; Itoshima supplies the coastal release.",),
            "city-access",
        ),
        DossierLens(
            "Reach Fukuoka easily—and integrate beyond the airport",
            ("global_access", "foreigner_fit"),
            ("Airport proximity does not remove the language and last-mile work of settling locally.",),
        ),
        DossierLens(
            "Own clearly, then operate locally",
            ("ownership_clarity", "regulatory_safety"),
            ("Clear ownership rules still leave building, hazard, management and use checks to the buyer.",),
        ),
        DossierLens(
            "Separate ordinary demand from a rental story",
            ("rental_profit", "capital_upside"),
            ("Underwrite residential demand separately from seasonal visitor demand.",),
            "seaside-life",
        ),
        DossierLens(
            "Enter with discipline and preserve the exit",
            ("value_entry", "exit_liquidity"),
            ("The right entry price depends on condition, access and the depth of the eventual buyer pool.",),
        ),
    ),
    micro_locations_intro="Choose the daily-life pattern before choosing the property.",
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
    references_intro="Rules and market evidence must be rechecked before a transaction.",
    references=(
        {"label": "Japan retirement property guide", "url": "/japan-retirement-property-foreign-buyers/"},
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
