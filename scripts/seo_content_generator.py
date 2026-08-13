from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SEO_CONTENT_OVERRIDES_PATH = ROOT / "data" / "seo_content_overrides.json"
POLICY_FLAG_NAMES = ("legal", "tax", "visa", "ownership", "price", "yield", "return", "guarantee")
DEFAULT_MODEL = "gpt-5.6"
SUPPORTED_GUIDE_SLUGS = {
    "best-places-to-buy-property-abroad-for-retirement",
    "best-places-to-buy-vacation-home-abroad",
    "best-countries-for-expats-to-buy-property",
    "best-countries-to-buy-property-as-a-foreigner",
    "buy-property-abroad",
    "buying-property-abroad-for-retirement",
    "best-places-to-buy-a-second-home-abroad",
    "overseas-property-investment",
    "foreign-property-investment-risks",
    "portugal-vs-spain-retirement-property",
    "greece-vs-portugal-retirement-property",
    "japan-retirement-property-foreign-buyers",
    "thailand-villa-ownership-foreigners",
    "best-places-to-buy-property-in-europe",
    "where-can-foreigners-buy-property",
}
PROHIBITED_CLAIM_TERMS = {
    "legal": ("legal", "lawful", "legally"),
    "tax": ("tax", "taxes", "taxation"),
    "visa": ("visa", "residency", "immigration"),
    "ownership": ("ownership", "own", "owns", "owned", "freehold", "leasehold"),
    "price": ("price", "priced", "cost", "affordable", "expensive"),
    "yield": ("yield", "yields"),
    "return": ("return", "returns", "profit", "appreciation"),
    "guarantee": ("guarantee", "guaranteed", "certain", "risk-free"),
}

PROPOSAL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "finding_fingerprint": {"type": "string"},
        "target_url": {"type": "string"},
        "base_content_hash": {"type": "string"},
        "title": {"type": ["string", "null"]},
        "meta_description": {"type": ["string", "null"]},
        "intro": {"type": ["string", "null"]},
        "faq_question": {"type": ["string", "null"]},
        "faq_answer": {"type": ["string", "null"]},
        "internal_link_target": {"type": ["string", "null"]},
        "internal_link_anchor": {"type": ["string", "null"]},
        "rationale": {"type": "string"},
        "source_fragments": {"type": "array", "items": {"type": "string"}},
        "policy_flags": {
            "type": "object",
            "properties": {name: {"type": "boolean"} for name in POLICY_FLAG_NAMES},
            "required": list(POLICY_FLAG_NAMES),
            "additionalProperties": False,
        },
    },
    "required": [
        "finding_fingerprint",
        "target_url",
        "base_content_hash",
        "title",
        "meta_description",
        "intro",
        "faq_question",
        "faq_answer",
        "internal_link_target",
        "internal_link_anchor",
        "rationale",
        "source_fragments",
        "policy_flags",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class TargetPageContext:
    target_url: str
    page_type: str
    title: str
    meta_description: str
    h1: str
    intro: str
    faqs: tuple[tuple[str, str], ...]
    sitemap_urls: tuple[str, ...]
    base_content_hash: str


@dataclass(frozen=True)
class ContentProposal:
    finding_fingerprint: str
    target_url: str
    base_content_hash: str
    title: str | None
    meta_description: str | None
    intro: str | None
    faq_question: str | None
    faq_answer: str | None
    internal_link_target: str | None
    internal_link_anchor: str | None
    rationale: str
    source_fragments: tuple[str, ...]
    policy_flags: dict[str, bool]


@dataclass(frozen=True)
class RejectedProposal:
    fingerprint: str
    target_url: str
    reason: str


@dataclass(frozen=True)
class BatchGenerationResult:
    accepted: tuple[dict, ...]
    rejected: tuple[RejectedProposal, ...]
    skipped_reason: str | None


class GenerationFailure(RuntimeError):
    pass


class PageContextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values = {"title": "", "description": "", "canonical": "", "h1": "", "intro": ""}
        self.faqs: list[tuple[str, str]] = []
        self.capture: str | None = None
        self.buffer: list[str] = []
        self.in_faq = False
        self.faq_question = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "meta" and values.get("name") == "description":
            self.values["description"] = values.get("content") or ""
        elif tag == "link" and values.get("rel") == "canonical":
            self.values["canonical"] = values.get("href") or ""
        elif tag == "details" and "faq-item" in classes:
            self.in_faq = True
        elif tag == "title" and not self.values["title"]:
            self.capture, self.buffer = "title", []
        elif tag == "h1" and not self.values["h1"]:
            self.capture, self.buffer = "h1", []
        elif tag == "p" and ({"seo-lede", "page-lede", "lede"} & classes) and not self.values["intro"]:
            self.capture, self.buffer = "intro", []
        elif self.in_faq and tag == "summary":
            self.capture, self.buffer = "faq_question", []
        elif self.in_faq and tag == "p":
            self.capture, self.buffer = "faq_answer", []

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        expected = {
            "title": "title",
            "h1": "h1",
            "summary": "faq_question",
            "p": self.capture if self.capture in {"intro", "faq_answer"} else None,
        }.get(tag)
        if self.capture and expected == self.capture:
            value = " ".join("".join(self.buffer).split())
            if self.capture == "faq_question":
                self.faq_question = value
            elif self.capture == "faq_answer":
                self.faqs.append((self.faq_question, value))
            else:
                self.values[self.capture] = value
            self.capture, self.buffer = None, []
        if tag == "details":
            self.in_faq = False


def canonical_to_artifact_path(target_url: str, artifacts_root: Path = ARTIFACTS) -> Path:
    parsed = urlparse(target_url)
    if parsed.scheme != "https" or parsed.netloc != "globalhomeatlas.com":
        raise ValueError(f"Unsupported target URL: {target_url}")
    relative = parsed.path.strip("/")
    return artifacts_root / relative / "index.html" if relative else artifacts_root / "index.html"


def content_hash(
    title: str,
    description: str,
    h1: str,
    intro: str,
    faqs: tuple[tuple[str, str], ...],
) -> str:
    payload = "\n".join([title, description, h1, intro, *[f"{q}\n{a}" for q, a in faqs]])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def page_type_for_url(target_url: str) -> str:
    parsed = urlparse(target_url)
    if parsed.scheme != "https" or parsed.netloc != "globalhomeatlas.com":
        raise ValueError(f"Unsupported target URL: {target_url}")
    if parsed.path == "/":
        return "homepage"
    if parsed.path.startswith("/countries/"):
        return "country"
    if parsed.path.startswith("/destinations/"):
        return "destination"
    slug = parsed.path.strip("/")
    if slug in SUPPORTED_GUIDE_SLUGS:
        return "guide"
    raise ValueError(f"Target URL is not supported by the content renderer: {target_url}")


def collect_target_context(
    target_url: str,
    sitemap_urls: list[str] | tuple[str, ...],
    artifacts_root: Path = ARTIFACTS,
) -> TargetPageContext:
    known_urls = tuple(sitemap_urls)
    if target_url not in known_urls:
        raise ValueError(f"Target URL is not present in sitemap: {target_url}")
    path = canonical_to_artifact_path(target_url, artifacts_root)
    if not path.exists():
        raise ValueError(f"Target artifact does not exist: {path}")
    parser = PageContextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if parser.values["canonical"] != target_url:
        raise ValueError(f"Canonical mismatch for {target_url}")
    missing = [field for field in ("title", "description", "h1") if not parser.values[field]]
    if missing:
        raise ValueError(f"Missing required page context: {', '.join(missing)}")
    faqs = tuple(parser.faqs)
    return TargetPageContext(
        target_url=target_url,
        page_type=page_type_for_url(target_url),
        title=parser.values["title"],
        meta_description=parser.values["description"],
        h1=parser.values["h1"],
        intro=parser.values["intro"],
        faqs=faqs,
        sitemap_urls=known_urls,
        base_content_hash=content_hash(
            parser.values["title"],
            parser.values["description"],
            parser.values["h1"],
            parser.values["intro"],
            faqs,
        ),
    )


def proposal_from_dict(payload: dict) -> ContentProposal:
    required = set(PROPOSAL_JSON_SCHEMA["required"])
    if set(payload) != required:
        missing = sorted(required - set(payload))
        extra = sorted(set(payload) - required)
        raise ValueError(f"Invalid proposal fields; missing={missing}, extra={extra}")
    flags = payload.get("policy_flags")
    if not isinstance(flags, dict) or set(flags) != set(POLICY_FLAG_NAMES):
        raise ValueError("Invalid proposal policy flags")
    if not all(isinstance(flags[name], bool) for name in POLICY_FLAG_NAMES):
        raise ValueError("Proposal policy flags must be booleans")
    fragments = payload.get("source_fragments")
    if not isinstance(fragments, list) or not all(isinstance(item, str) for item in fragments):
        raise ValueError("Proposal source_fragments must be strings")
    nullable_fields = (
        "title",
        "meta_description",
        "intro",
        "faq_question",
        "faq_answer",
        "internal_link_target",
        "internal_link_anchor",
    )
    if any(payload[field] is not None and not isinstance(payload[field], str) for field in nullable_fields):
        raise ValueError("Proposal content fields must be strings or null")
    return ContentProposal(
        finding_fingerprint=str(payload["finding_fingerprint"]),
        target_url=str(payload["target_url"]),
        base_content_hash=str(payload["base_content_hash"]),
        title=payload["title"],
        meta_description=payload["meta_description"],
        intro=payload["intro"],
        faq_question=payload["faq_question"],
        faq_answer=payload["faq_answer"],
        internal_link_target=payload["internal_link_target"],
        internal_link_anchor=payload["internal_link_anchor"],
        rationale=str(payload["rationale"]),
        source_fragments=tuple(fragments),
        policy_flags=dict(flags),
    )


def _source_text(context: TargetPageContext) -> str:
    return "\n".join(
        [
            context.title,
            context.meta_description,
            context.h1,
            context.intro,
            *[f"{question}\n{answer}" for question, answer in context.faqs],
        ]
    )


def _proposal_text(proposal: ContentProposal) -> str:
    return "\n".join(
        value
        for value in (
            proposal.title,
            proposal.meta_description,
            proposal.intro,
            proposal.faq_question,
            proposal.faq_answer,
            proposal.internal_link_anchor,
        )
        if value
    )


_ENTITY_TITLE_TOKEN = r"(?:[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\-]{2,}|[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]{0,3}\.)"
_ENTITY_CONNECTOR = r"(?:da|das|de|del|di|do|dos|du|la|le|van|von)"


def _capitalized_entity_phrases(text: str) -> set[str]:
    separator = rf"(?:[ \t]+(?:{_ENTITY_CONNECTOR}[ \t]+)?|[ \t]+[dl]['’])"
    pattern = rf"(?<!\w){_ENTITY_TITLE_TOKEN}(?:{separator}{_ENTITY_TITLE_TOKEN})+"
    return set(re.findall(pattern, text))


def _entity_is_supported(entity: str, source_lower: str) -> bool:
    if entity.lower() in source_lower:
        return True

    title_tokens = list(re.finditer(_ENTITY_TITLE_TOKEN, entity))
    return any(
        entity[token.start():].lower() in source_lower
        for token in title_tokens[1:-1]
    )


def validate_proposal(proposal: ContentProposal, context: TargetPageContext) -> list[str]:
    errors: list[str] = []
    if proposal.target_url != context.target_url:
        errors.append("Target URL does not match page context")
    if proposal.base_content_hash != context.base_content_hash:
        errors.append("Base content hash is stale")
    if not re.fullmatch(r"gha-[a-z0-9-]+", proposal.finding_fingerprint):
        errors.append("Finding fingerprint is invalid")
    if (proposal.faq_question is None) != (proposal.faq_answer is None):
        errors.append("FAQ question and answer must be paired")
    if context.page_type != "guide" and proposal.faq_question is not None:
        errors.append("FAQ changes are limited to guide pages")
    if (proposal.internal_link_target is None) != (proposal.internal_link_anchor is None):
        errors.append("Internal link target and anchor must be paired")
    if proposal.internal_link_target:
        if proposal.internal_link_target not in context.sitemap_urls:
            errors.append("Internal link target is not present in sitemap")
        if proposal.internal_link_target == context.target_url:
            errors.append("Internal link target cannot be the current page")
    if proposal.title is not None and not 30 <= len(proposal.title.strip()) <= 65:
        errors.append("Title must contain 30 to 65 characters")
    if proposal.meta_description is not None and not 70 <= len(proposal.meta_description.strip()) <= 165:
        errors.append("Meta description must contain 70 to 165 characters")
    content_values = [
        proposal.title,
        proposal.meta_description,
        proposal.intro,
        proposal.faq_question,
        proposal.faq_answer,
        proposal.internal_link_anchor,
    ]
    if any(value is not None and not value.strip() for value in content_values):
        errors.append("Proposed content fields cannot be blank")
    original_values = {
        context.title,
        context.meta_description,
        context.intro,
        *[item for pair in context.faqs for item in pair],
    }
    if all(value is None or value.strip() in original_values for value in content_values):
        errors.append("Proposal does not make a material content change")
    source_text = _source_text(context)
    source_lower = source_text.lower()
    if not proposal.source_fragments:
        errors.append("Proposal must cite at least one source fragment")
    for fragment in proposal.source_fragments:
        if not fragment.strip() or fragment.lower() not in source_lower:
            errors.append(f"Source fragment is not present in page context: {fragment}")
    proposed_text = _proposal_text(proposal)
    source_numbers = set(re.findall(r"(?:[$€£¥]\s*)?\d+(?:[.,]\d+)?%?", source_text))
    proposed_numbers = set(re.findall(r"(?:[$€£¥]\s*)?\d+(?:[.,]\d+)?%?", proposed_text))
    if proposed_numbers - source_numbers:
        errors.append("Proposal introduces a number absent from source context")
    for name, flagged in proposal.policy_flags.items():
        if flagged:
            errors.append(f"Proposal policy flag is set: {name}")
    proposed_lower = proposed_text.lower()
    for category, terms in PROHIBITED_CLAIM_TERMS.items():
        introduced = [term for term in terms if re.search(rf"\b{re.escape(term)}\b", proposed_lower)]
        if introduced:
            errors.append(f"Proposal introduces prohibited {category} claim language: {introduced[0]}")

    new_entities = sorted(
        entity for entity in _capitalized_entity_phrases(proposed_text)
        if not _entity_is_supported(entity, source_lower)
    )
    if new_entities:
        errors.append(f"Proposal introduces capitalized entities absent from source context: {', '.join(new_entities)}")

    words = re.findall(r"[a-z0-9]+", proposed_lower)
    repeated = {
        " ".join(words[index:index + 3])
        for index in range(max(0, len(words) - 2))
        if words.count(words[index]) >= 4
        and sum(1 for offset in range(max(0, len(words) - 2)) if words[offset:offset + 3] == words[index:index + 3]) >= 4
    }
    if repeated:
        errors.append("Proposal repeats the same query phrase excessively")
    return errors


def override_entry(
    proposal: ContentProposal,
    finding: dict,
    *,
    generated_at: str,
    model: str,
    cooldown_until: str,
) -> dict:
    return {
        "target_url": proposal.target_url,
        "finding_fingerprint": proposal.finding_fingerprint,
        "base_content_hash": proposal.base_content_hash,
        "generated_at": generated_at,
        "model": model,
        "signal": finding,
        "lifecycle": "proposed",
        "cooldown_until": cooldown_until,
        "content": {
            "title": proposal.title,
            "meta_description": proposal.meta_description,
            "intro": proposal.intro,
            "faq_question": proposal.faq_question,
            "faq_answer": proposal.faq_answer,
            "internal_link_target": proposal.internal_link_target,
            "internal_link_anchor": proposal.internal_link_anchor,
        },
    }


def load_override_entries(path: Path = SEO_CONTENT_OVERRIDES_PATH) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("SEO content overrides must be a list")
    return [item for item in payload if isinstance(item, dict)]


def upsert_override_entry(entry: dict, path: Path = SEO_CONTENT_OVERRIDES_PATH) -> None:
    rows = load_override_entries(path)
    rows = [
        row
        for row in rows
        if row.get("target_url") != entry.get("target_url")
        and row.get("finding_fingerprint") != entry.get("finding_fingerprint")
    ]
    rows.append(entry)
    rows.sort(key=lambda row: str(row.get("target_url") or ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_generation_input(finding: dict, context: TargetPageContext) -> list[dict]:
    page_rules = (
        f"This is a {context.page_type} page. "
        + ("FAQ fields may be proposed when supported. " if context.page_type == "guide" else "FAQ fields must be null. ")
        + "A proposed title must contain 30 to 65 characters. "
        + "A proposed meta description must contain 70 to 165 characters. "
        + "Any content field that would introduce protected-topic language must be null. "
    )
    developer = (
        "Revise only the supplied page content to improve match with the supplied Search Console signal. "
        + page_rules
        + "Return null for fields that should remain unchanged. Never add facts, numbers, legal, tax, visa, "
        "ownership, price, yield, return, or guarantee claims. Preserve research caveats. Set every policy "
        "flag truthfully when the requested wording touches a prohibited category. Use source_fragments to "
        "identify exact phrases in the supplied page context that support the rewrite."
    )
    context_payload = asdict(context)
    context_payload["faqs"] = [list(pair) for pair in context.faqs]
    context_payload["sitemap_urls"] = list(context.sitemap_urls)
    user_payload = {"finding": finding, "page_context": context_payload}
    return [
        {"role": "developer", "content": developer},
        {"role": "user", "content": json.dumps(user_payload, sort_keys=True)},
    ]


def openai_client():
    from openai import OpenAI

    return OpenAI()


def _refusal_text(response) -> str | None:
    for item in getattr(response, "output", []) or []:
        contents = item.get("content", []) if isinstance(item, dict) else getattr(item, "content", [])
        for content in contents or []:
            content_type = content.get("type") if isinstance(content, dict) else getattr(content, "type", None)
            if content_type == "refusal":
                return content.get("refusal") if isinstance(content, dict) else getattr(content, "refusal", "refused")
    return None


def generate_proposal(
    finding: dict,
    context: TargetPageContext,
    *,
    client=None,
    model: str | None = None,
) -> ContentProposal:
    active_client = client or openai_client()
    active_model = model or os.environ.get("SEO_CONTENT_MODEL", DEFAULT_MODEL)
    response = active_client.responses.create(
        model=active_model,
        input=build_generation_input(finding, context),
        text={
            "format": {
                "type": "json_schema",
                "name": "seo_content_proposal",
                "strict": True,
                "schema": PROPOSAL_JSON_SCHEMA,
            }
        },
    )
    refusal = _refusal_text(response)
    if refusal:
        raise GenerationFailure(f"OpenAI response was refused: {refusal}")
    status = getattr(response, "status", None)
    if status != "completed":
        raise GenerationFailure(f"OpenAI response status: {status or 'unknown'}")
    try:
        payload = json.loads(response.output_text)
    except (AttributeError, TypeError, json.JSONDecodeError) as exc:
        raise GenerationFailure("OpenAI response was not valid structured JSON") from exc
    try:
        return proposal_from_dict(payload)
    except ValueError as exc:
        raise GenerationFailure(f"OpenAI response failed schema validation: {exc}") from exc


def _transient_api_error(exc: Exception) -> bool:
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    if exc.__class__.__name__ in {"APIConnectionError", "APITimeoutError"}:
        return True
    status_code = getattr(exc, "status_code", None)
    return status_code == 429 or (isinstance(status_code, int) and status_code >= 500)


def generate_proposal_with_retry(
    finding: dict,
    context: TargetPageContext,
    *,
    client=None,
    model: str | None = None,
    attempts: int = 3,
    sleep_fn=time.sleep,
) -> ContentProposal:
    if attempts < 1:
        raise ValueError("attempts must be positive")
    for attempt in range(1, attempts + 1):
        try:
            return generate_proposal(finding, context, client=client, model=model)
        except Exception as exc:
            if attempt == attempts or not _transient_api_error(exc):
                raise
            sleep_fn(attempt)
    raise GenerationFailure("OpenAI generation attempts exhausted")


def generate_batch(
    candidates: list[tuple[dict, TargetPageContext]],
    *,
    client=None,
    model: str | None = None,
    generated_at: str | None = None,
) -> BatchGenerationResult:
    if client is None and not os.environ.get("OPENAI_API_KEY"):
        return BatchGenerationResult(accepted=(), rejected=(), skipped_reason="OPENAI_API_KEY is not configured")
    active_model = model or os.environ.get("SEO_CONTENT_MODEL", DEFAULT_MODEL)
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    generated_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    cooldown_until = (generated_dt + timedelta(days=28)).isoformat()
    accepted: list[dict] = []
    rejected: list[RejectedProposal] = []
    for finding, context in candidates:
        fingerprint = str(finding.get("fingerprint") or "")
        try:
            proposal = generate_proposal_with_retry(
                finding,
                context,
                client=client,
                model=active_model,
            )
            errors = validate_proposal(proposal, context)
            if proposal.finding_fingerprint != fingerprint:
                errors.append("Finding fingerprint does not match generation request")
            if errors:
                raise ValueError("; ".join(errors))
            accepted.append(
                override_entry(
                    proposal,
                    finding.get("payload") or {},
                    generated_at=timestamp,
                    model=active_model,
                    cooldown_until=cooldown_until,
                )
            )
        except Exception as exc:
            rejected.append(
                RejectedProposal(
                    fingerprint=fingerprint,
                    target_url=context.target_url,
                    reason=str(exc),
                )
            )
    return BatchGenerationResult(accepted=tuple(accepted), rejected=tuple(rejected), skipped_reason=None)
