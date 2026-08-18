# Automated SEO Content Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert qualified existing-page Search Console findings into validated content overrides and one consolidated draft pull request without allowing editorial content to auto-merge.

**Architecture:** A read-only context collector converts rendered pages and analytics findings into a small typed prompt payload. The OpenAI Responses API returns strict schema-constrained proposals; deterministic validation converts accepted proposals into a machine-owned JSON override file that the static builder consumes. The existing feedback loop batches accepted changes into one draft PR, while reporting failures without interrupting monitoring.

**Tech Stack:** Python 3.11, standard-library `unittest`, OpenAI Python SDK and Responses API Structured Outputs, GitHub CLI, GitHub Actions, existing static Python site builder.

## Global Constraints

- Editorial changes always remain in a draft pull request until approved.
- Editorial pull requests must never receive `auto-merge-safe` or call `maybe_auto_merge`.
- The first release handles existing-page `query-ctr-opportunity`, `low-ctr-opportunity`, and non-deterministic `near-ranking-opportunity` findings only.
- New landing pages and all new factual research remain outside the first release.
- Generated content may not introduce unsupported legal, tax, visa, ownership, price, yield, return, or guarantee claims.
- Generate at most five editorial proposals per scheduled run.
- Apply a 28-day target-page cooldown after merge.
- Missing credentials or generation failures must not prevent monitoring, status-dashboard generation, issue updates, or report uploads.
- `OPENAI_API_KEY` is the only required new secret; `SEO_CONTENT_MODEL` defaults to `gpt-5.6`.
- Model output may influence only `data/seo_content_overrides.json`; it must never generate or edit executable code.
- Use Structured Outputs with strict JSON Schema, as documented at <https://developers.openai.com/api/docs/guides/structured-outputs>.

---

## File Map

- Create `scripts/seo_content_generator.py`: context extraction, proposal schema, OpenAI call, deterministic validation, override serialization, and batch result types.
- Create `src/seo_content_overrides.py`: strict runtime loading and application of machine-owned overrides.
- Create `data/seo_content_overrides.json`: committed empty override array.
- Create `tests/test_seo_content_generator.py`: context, schema, API, validation, batching, and store tests.
- Create `tests/fixtures/seo-content-report.json`: deterministic one-page Search Console input.
- Create `tests/fixtures/seo-content-response.json`: deterministic strict-schema model response.
- Create `tests/test_seo_content_overrides.py`: runtime loader and safe application tests.
- Modify `src/build_unified_app.py`: apply overrides to homepage, guide, country, and destination rendering.
- Modify `scripts/seo_feedback_loop.py`: candidate selection, consolidated generated-content branch/PR, summary reporting, and suppression of proposal-only PRs for eligible findings.
- Modify `tests/test_seo_feedback_loop.py`: selection, branch stability, draft PR arguments, failure reporting, and no-auto-merge tests.
- Modify `.github/workflows/seo-feedback-loop.yml`: install the OpenAI SDK and expose the two configuration values.
- Modify `docs/SEO_GROWTH_SYSTEM.md`: configuration, safety rules, review flow, and recovery.

---

### Task 1: Extract Stable Page Context

**Files:**
- Create: `scripts/seo_content_generator.py`
- Test: `tests/test_seo_content_generator.py`

**Interfaces:**
- Consumes: canonical URL, sitemap URLs, and generated files below `artifacts/`.
- Produces: `TargetPageContext`, `canonical_to_artifact_path()`, `collect_target_context()`, and `content_hash()`.

- [ ] **Step 1: Write failing context-extraction tests**

```python
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import seo_content_generator


class ContextCollectionTests(unittest.TestCase):
    def test_collect_target_context_reads_metadata_intro_and_faqs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            page = root / "countries" / "portugal-property" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<title>Portugal Guide</title>'
                '<meta name="description" content="Current description">'
                '<link rel="canonical" href="https://globalhomeatlas.com/countries/portugal-property/">'
                '<h1>Portugal Property Guide</h1>'
                '<p class="page-lede">Current intro.</p>'
                '<details class="faq-item"><summary>Question?</summary><p>Answer.</p></details>',
                encoding="utf-8",
            )

            context = seo_content_generator.collect_target_context(
                "https://globalhomeatlas.com/countries/portugal-property/",
                ["https://globalhomeatlas.com/countries/portugal-property/"],
                artifacts_root=root,
            )

        self.assertEqual("country", context.page_type)
        self.assertEqual("Portugal Guide", context.title)
        self.assertEqual("Current description", context.meta_description)
        self.assertEqual("Portugal Property Guide", context.h1)
        self.assertEqual("Current intro.", context.intro)
        self.assertEqual((("Question?", "Answer."),), context.faqs)
        self.assertEqual(64, len(context.base_content_hash))

    def test_collect_target_context_rejects_url_outside_sitemap(self) -> None:
        with self.assertRaisesRegex(ValueError, "not present in sitemap"):
            seo_content_generator.collect_target_context(
                "https://globalhomeatlas.com/not-real/",
                ["https://globalhomeatlas.com/"],
                artifacts_root=Path("artifacts"),
            )
```

- [ ] **Step 2: Run the tests and confirm the missing module failure**

Run: `python3 -m unittest tests.test_seo_content_generator -v`

Expected: FAIL because `scripts.seo_content_generator` does not exist.

- [ ] **Step 3: Implement the page-context types and HTML collector**

Create these exact public interfaces:

```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


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


def canonical_to_artifact_path(target_url: str, artifacts_root: Path = ARTIFACTS) -> Path:
    parsed = urlparse(target_url)
    if parsed.netloc != "globalhomeatlas.com":
        raise ValueError(f"Unsupported target host: {parsed.netloc}")
    relative = parsed.path.strip("/")
    return artifacts_root / relative / "index.html" if relative else artifacts_root / "index.html"


def content_hash(title: str, description: str, h1: str, intro: str, faqs: tuple[tuple[str, str], ...]) -> str:
    payload = "\n".join([title, description, h1, intro, *[f"{q}\n{a}" for q, a in faqs]])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
        elif tag == "title":
            self.capture, self.buffer = "title", []
        elif tag == "h1" and not self.values["h1"]:
            self.capture, self.buffer = "h1", []
        elif tag == "p" and ({"seo-lede", "page-lede"} & classes) and not self.values["intro"]:
            self.capture, self.buffer = "intro", []
        elif self.in_faq and tag == "summary":
            self.capture, self.buffer = "faq_question", []
        elif self.in_faq and tag == "p":
            self.capture, self.buffer = "faq_answer", []

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        closing = {"title": "title", "h1": "h1", "p": self.capture, "summary": "faq_question"}.get(tag)
        if self.capture and closing == self.capture:
            text = " ".join("".join(self.buffer).split())
            if self.capture == "faq_question":
                self.faq_question = text
            elif self.capture == "faq_answer":
                self.faqs.append((self.faq_question, text))
            else:
                self.values[self.capture] = text
            self.capture, self.buffer = None, []
        if tag == "details":
            self.in_faq = False


def page_type_for_url(target_url: str) -> str:
    path = urlparse(target_url).path
    if path == "/":
        return "homepage"
    if path.startswith("/countries/"):
        return "country"
    if path.startswith("/destinations/"):
        return "destination"
    return "guide"


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
    missing = [name for name in ("title", "description", "h1") if not parser.values[name]]
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
            parser.values["title"], parser.values["description"], parser.values["h1"], parser.values["intro"], faqs
        ),
    )
```

Preserve the focused parser behavior shown above: capture only the first `<title>`, description meta, canonical link, `<h1>`, `.seo-lede` or `.page-lede`, and `.faq-item` pairs. Do not add a general-purpose HTML dependency.

- [ ] **Step 4: Add homepage, guide, destination, escaping, and canonical-mismatch tests**

```python
def test_page_type_routes_known_paths(self) -> None:
    self.assertEqual("homepage", seo_content_generator.page_type_for_url("https://globalhomeatlas.com/"))
    self.assertEqual("country", seo_content_generator.page_type_for_url("https://globalhomeatlas.com/countries/spain-property/"))
    self.assertEqual("destination", seo_content_generator.page_type_for_url("https://globalhomeatlas.com/destinations/andermatt/"))
    self.assertEqual("guide", seo_content_generator.page_type_for_url("https://globalhomeatlas.com/buy-property-abroad/"))
```

- [ ] **Step 5: Run the focused tests**

Run: `python3 -m unittest tests.test_seo_content_generator.ContextCollectionTests -v`

Expected: PASS.

- [ ] **Step 6: Commit the context collector**

```bash
git add scripts/seo_content_generator.py tests/test_seo_content_generator.py
git commit -m "Add SEO content context collector"
```

---

### Task 2: Define and Enforce the Content Safety Contract

**Files:**
- Modify: `scripts/seo_content_generator.py`
- Modify: `tests/test_seo_content_generator.py`
- Create: `tests/fixtures/seo-content-report.json`
- Create: `tests/fixtures/seo-content-response.json`

**Interfaces:**
- Consumes: `TargetPageContext` from Task 1 and a finding mapping.
- Produces: `ContentProposal`, `PROPOSAL_JSON_SCHEMA`, `proposal_from_dict()`, `validate_proposal()`, `override_entry()`, `load_override_entries()`, and `upsert_override_entry()`.

- [ ] **Step 1: Write failing proposal and policy tests**

```python
class ProposalValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = seo_content_generator.TargetPageContext(
            target_url="https://globalhomeatlas.com/countries/portugal-property/",
            page_type="country",
            title="Portugal Property Guide",
            meta_description="Compare Portugal property markets for foreign buyers.",
            h1="Portugal Property Guide",
            intro="Portugal is a retirement and second-home benchmark.",
            faqs=(),
            sitemap_urls=(
                "https://globalhomeatlas.com/countries/portugal-property/",
                "https://globalhomeatlas.com/buy-property-abroad/",
            ),
            base_content_hash="a" * 64,
        )

    def proposal(self, **changes):
        values = {
            "finding_fingerprint": "gha-low-ctr-opportunity-abc123",
            "target_url": self.context.target_url,
            "base_content_hash": self.context.base_content_hash,
            "title": "Portugal Property Guide for Foreign Buyers",
            "meta_description": "Compare Portugal property markets for foreign buyers and retirement planning.",
            "intro": "Compare Portugal as a retirement and second-home benchmark.",
            "faq_question": None,
            "faq_answer": None,
            "internal_link_target": "https://globalhomeatlas.com/buy-property-abroad/",
            "internal_link_anchor": "buying property abroad guide",
            "rationale": "Matches the observed foreign-buyer query intent.",
            "source_fragments": ["Portugal", "retirement and second-home benchmark"],
            "policy_flags": {
                "legal": False, "tax": False, "visa": False, "ownership": False,
                "price": False, "yield": False, "return": False, "guarantee": False,
            },
        }
        values.update(changes)
        return seo_content_generator.proposal_from_dict(values)

    def test_valid_proposal_has_no_errors(self) -> None:
        self.assertEqual([], seo_content_generator.validate_proposal(self.proposal(), self.context))

    def test_rejects_new_number_and_prohibited_claim(self) -> None:
        proposal = self.proposal(intro="Portugal guarantees a 12% return.")
        errors = seo_content_generator.validate_proposal(proposal, self.context)
        self.assertTrue(any("number" in error for error in errors))
        self.assertTrue(any("guarantee" in error or "return" in error for error in errors))
```

- [ ] **Step 2: Run the policy tests and confirm missing-interface failures**

Run: `python3 -m unittest tests.test_seo_content_generator.ProposalValidationTests -v`

Expected: FAIL because `ContentProposal` and validation functions are undefined.

- [ ] **Step 3: Add the strict proposal model and JSON Schema**

```python
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


POLICY_FLAG_NAMES = ("legal", "tax", "visa", "ownership", "price", "yield", "return", "guarantee")

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
        "finding_fingerprint", "target_url", "base_content_hash", "title",
        "meta_description", "intro", "faq_question", "faq_answer",
        "internal_link_target", "internal_link_anchor", "rationale",
        "source_fragments", "policy_flags",
    ],
    "additionalProperties": False,
}
```

- [ ] **Step 4: Implement deterministic validation**

`validate_proposal(proposal, context)` must return a list of exact human-readable errors and check:

- URL, fingerprint shape, and base hash equality;
- paired FAQ and internal-link fields;
- link membership in `context.sitemap_urls` and no self-link;
- title length 30–65 characters and description length 70–165 characters when changed;
- non-empty trimmed text and at least one material change;
- FAQ changes only when `context.page_type == "guide"`; homepage, country, and destination proposals must return `null` for both FAQ fields in the first release;
- case-insensitive source-fragment presence in the original context;
- numbers, percentages, currency symbols, and capitalized entities newly introduced relative to source;
- prohibited terms and any `True` policy flag;
- repeated target query more than twice in one proposed field.

Use conservative token comparison. Do not call the model again to judge its own output.

- [ ] **Step 5: Implement override serialization and deterministic upsert**

```python
SEO_CONTENT_OVERRIDES_PATH = ROOT / "data" / "seo_content_overrides.json"


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
```

`upsert_override_entry()` replaces entries sharing either the target URL or fingerprint, sorts by target URL, and writes a trailing newline.

- [ ] **Step 6: Add boundary tests**

Add explicit tests for title/description lengths, FAQ pairing, link pairing, outside-sitemap links, stale hashes, source-fragment mismatch, unchanged output, keyword repetition, all eight policy flags, malformed JSON store data, and target/fingerprint deduplication.

- [ ] **Step 7: Run the generator test module**

Run: `python3 -m unittest tests.test_seo_content_generator -v`

Expected: PASS.

- [ ] **Step 8: Commit the safety contract**

```bash
git add scripts/seo_content_generator.py tests/test_seo_content_generator.py
git commit -m "Validate generated SEO content"
```

---

### Task 3: Call the OpenAI Responses API with Structured Outputs

**Files:**
- Modify: `scripts/seo_content_generator.py`
- Modify: `tests/test_seo_content_generator.py`

**Interfaces:**
- Consumes: a finding mapping and `TargetPageContext`.
- Produces: `build_generation_input()`, `generate_proposal()`, `GenerationFailure`, and `BatchGenerationResult`.

- [ ] **Step 1: Write failing mocked-client tests**

```python
class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.status = "completed"
        self.output = []
        self.output_text = json.dumps(payload)


class FakeResponses:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeClient:
    def __init__(self, response):
        self.responses = FakeResponses(response)


def test_generate_proposal_uses_strict_schema(self) -> None:
    client = FakeClient(FakeResponse(self.valid_proposal))
    proposal = seo_content_generator.generate_proposal(self.finding, self.context, client=client, model="test-model")
    request = client.responses.calls[0]
    self.assertEqual("test-model", request["model"])
    self.assertTrue(request["text"]["format"]["strict"])
    self.assertEqual(seo_content_generator.PROPOSAL_JSON_SCHEMA, request["text"]["format"]["schema"])
    self.assertEqual(self.context.target_url, proposal.target_url)
```

Use `json.dumps(valid_proposal_dict)` in the real test; do not leave the ellipsis shown above.

- [ ] **Step 2: Run the mocked-client test and verify failure**

Run: `python3 -m unittest tests.test_seo_content_generator.OpenAIGenerationTests -v`

Expected: FAIL because `generate_proposal()` is undefined.

- [ ] **Step 3: Implement a dependency-injected Responses API call**

```python
DEFAULT_MODEL = "gpt-5.6"


class GenerationFailure(RuntimeError):
    pass


def openai_client():
    from openai import OpenAI
    return OpenAI()


def generate_proposal(finding: dict, context: TargetPageContext, *, client=None, model: str | None = None) -> ContentProposal:
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
    if response.status != "completed":
        raise GenerationFailure(f"OpenAI response status: {response.status}")
    return proposal_from_dict(json.loads(response.output_text))
```

`build_generation_input()` must use one developer message and one user message. The developer message must say: rewrite only supplied content, return `null` when a field should not change, never add facts, preserve research caveats, and flag prohibited categories. The user payload must contain only the finding and `TargetPageContext` fields—not repository secrets or unrelated report data.

- [ ] **Step 4: Add refusal, incomplete, invalid JSON, and retry tests**

Inspect `response.output` for refusal items before parsing. Add `generate_proposal_with_retry(finding, context, client, model, attempts=3, sleep_fn=time.sleep)` that retries only timeout, connection, 429, and 5xx-style exceptions; schema, refusal, and policy errors do not retry.

- [ ] **Step 5: Add batch result types and independent failure behavior**

```python
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
```

Implement `generate_batch()` so one rejected proposal never prevents later proposals. When `OPENAI_API_KEY` is missing and no client is injected, return an empty result with `skipped_reason="OPENAI_API_KEY is not configured"` without importing the SDK.

- [ ] **Step 6: Run all generator tests**

Before running the module, add a fixture test that loads both committed JSON fixtures, injects `FakeClient`, and asserts one accepted override for `https://globalhomeatlas.com/countries/portugal-property/`. The report fixture must contain that URL in `sitemap.urls` and `search_console.low_ctr_pages`; the response fixture must contain every required schema field, preserve the fixture context hash, and use only phrases copied from the fixture page context.

Use this report fixture structure:

```json
{
  "sitemap": {
    "urls": [
      "https://globalhomeatlas.com/countries/portugal-property/",
      "https://globalhomeatlas.com/buy-property-abroad/"
    ]
  },
  "search_console": {
    "low_ctr_pages": [
      {
        "page": "https://globalhomeatlas.com/countries/portugal-property/",
        "clicks": 0,
        "impressions": 40,
        "ctr": 0.0,
        "position": 8.0
      }
    ]
  }
}
```

Build the response fixture inside the test from the collected context so the real SHA-256 hash is used, then compare it with the committed response fixture after replacing the sentinel string `__BASE_CONTENT_HASH__`. This keeps the fixture readable without weakening the production hash check.

Run: `python3 -m unittest tests.test_seo_content_generator -v`

Expected: PASS with no real network calls.

- [ ] **Step 7: Commit the structured generator**

```bash
git add scripts/seo_content_generator.py tests/test_seo_content_generator.py tests/fixtures/seo-content-report.json tests/fixtures/seo-content-response.json
git commit -m "Generate structured SEO content proposals"
```

---

### Task 4: Apply Overrides Safely in the Static Builder

**Files:**
- Create: `src/seo_content_overrides.py`
- Create: `data/seo_content_overrides.json`
- Create: `tests/test_seo_content_overrides.py`
- Modify: `src/build_unified_app.py:13-17`
- Modify: `src/build_unified_app.py:946-963`
- Modify: `src/build_unified_app.py:2784-3276`
- Modify: `src/build_unified_app.py:3861-4002`
- Modify: `src/build_unified_app.py:4005-4260`
- Modify: `src/build_unified_app.py:5002-5380`
- Modify: `src/build_unified_app.py:7235-7320`
- Modify: `tests/test_seo_ctr_content.py`

**Interfaces:**
- Consumes: validated entries in `data/seo_content_overrides.json`.
- Produces: `load_content_overrides()`, `apply_content_override()`, `render_generated_internal_link()`, and override-aware page builders.

- [ ] **Step 1: Write failing runtime-loader tests**

```python
from src import seo_content_overrides


class ContentOverrideRuntimeTests(unittest.TestCase):
    def test_apply_content_override_maps_only_recognized_fields(self) -> None:
        base = {"title": "Old", "description": "Old description", "faqs": [("Old?", "Old answer.")]}
        entries = [{
            "target_url": "https://globalhomeatlas.com/example/",
            "finding_fingerprint": "gha-low-ctr-opportunity-abc123",
            "base_content_hash": "a" * 64,
            "generated_at": "2026-08-12T00:00:00Z",
            "model": "test-model",
            "signal": {},
            "lifecycle": "proposed",
            "cooldown_until": "2026-09-09T00:00:00Z",
            "content": {
                "title": "New title",
                "meta_description": "New description",
                "intro": "New intro",
                "faq_question": "New?",
                "faq_answer": "New answer.",
                "internal_link_target": "https://globalhomeatlas.com/guides/",
                "internal_link_anchor": "property buying guides",
            },
        }]
        result = seo_content_overrides.apply_content_override(base, "https://globalhomeatlas.com/example/", entries)
        self.assertEqual("New title", result["title"])
        self.assertEqual("New description", result["description"])
        self.assertEqual("New intro", result["generated_intro"])
        self.assertEqual(("New?", "New answer."), result["faqs"][-1])
        self.assertEqual("property buying guides", result["generated_internal_link"]["anchor"])
```

- [ ] **Step 2: Run the runtime test and verify the missing module failure**

Run: `python3 -m unittest tests.test_seo_content_overrides -v`

Expected: FAIL because `src.seo_content_overrides` does not exist.

- [ ] **Step 3: Implement strict runtime loading and copying**

```python
ALLOWED_CONTENT_FIELDS = {
    "title", "meta_description", "intro", "faq_question", "faq_answer",
    "internal_link_target", "internal_link_anchor",
}


def load_content_overrides(path: Path = DEFAULT_PATH) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("SEO content overrides must be a list")
    seen: set[str] = set()
    for row in rows:
        if set(row) != REQUIRED_TOP_LEVEL_FIELDS:
            raise ValueError("SEO content override has unknown or missing top-level fields")
        target = row["target_url"]
        if target in seen:
            raise ValueError(f"Duplicate SEO content target: {target}")
        seen.add(target)
        if set(row["content"]) != ALLOWED_CONTENT_FIELDS:
            raise ValueError(f"SEO content override has unknown or missing content fields: {target}")
        validate_runtime_entry(row)
    return rows


def apply_content_override(base: dict, canonical: str, entries: list[dict]) -> dict:
    result = deepcopy(base)
    entry = next((row for row in entries if row["target_url"] == canonical), None)
    if not entry:
        return result
    content = entry["content"]
    if content["title"] is not None:
        result["title"] = content["title"]
    if content["meta_description"] is not None:
        result["description"] = content["meta_description"]
    if content["intro"] is not None:
        result["generated_intro"] = content["intro"]
    if content["faq_question"] is not None:
        result.setdefault("faqs", []).append((content["faq_question"], content["faq_answer"]))
    if content["internal_link_target"] is not None:
        result["generated_internal_link"] = {
            "target": content["internal_link_target"],
            "anchor": content["internal_link_anchor"],
        }
    return result
```

Define `REQUIRED_TOP_LEVEL_FIELDS`, `DEFAULT_PATH`, and `validate_runtime_entry()` immediately above these functions. The validator must reject duplicate target URLs, unknown keys, malformed hashes, unknown lifecycle values, unpaired FAQ/link fields, and non-HTTPS Global Home Atlas links. `apply_content_override()` must deep-copy the base mapping and never mutate constants in `build_unified_app.py`.

Initialize `data/seo_content_overrides.json` as:

```json
[]
```

- [ ] **Step 4: Add builder tests before modifying rendering**

Add tests to `tests/test_seo_ctr_content.py` that pass an in-memory override list into each builder:

```python
def test_seo_page_override_updates_visible_and_schema_faq(self) -> None:
    page = seo_page("best-places-to-buy-property-in-europe")
    canonical = build_unified_app.page_url(page["slug"])
    overrides = [content_override(canonical, title="Europe Property Guide 2026", faq=("Compare Europe?", "Compare access and resale depth."))]
    html = build_unified_app.build_seo_page(page, sample_destinations(), build_unified_app.SEO_PAGES, content_overrides=overrides)
    self.assertIn("<title>Europe Property Guide 2026</title>", html)
    self.assertIn("Compare Europe?", html)
    self.assertIn('"@type":"FAQPage"', html)
```

Add equivalent focused assertions for homepage meta/intro, country title/meta/intro, destination title/meta/intro, and a generated internal link. Use the smallest valid destination fixtures required by each builder.

- [ ] **Step 5: Make page builders override-aware**

Add optional `content_overrides: list[dict] | None = None` parameters to:

```python
build_landing_page(destinations, pages, listings, countries, content_overrides=None)
build_country_hub_page(hub, destinations, pages, content_overrides=None)
build_seo_page(page, destinations, pages, auto_links=None, content_overrides=None)
build_destination_page(dest, listings, destinations, pages, content_overrides=None)
```

At the top of each function, construct a base content mapping, call `apply_content_override()`, and use only the returned values for title, description, intro, FAQ, and link rendering. Add a single escaped helper:

```python
def generated_internal_link_html(content: dict) -> str:
    link = content.get("generated_internal_link")
    if not link:
        return ""
    return (
        '<p class="generated-seo-link">Continue with '
        f'<a href="{escape(urlparse(link["target"]).path)}">{escape(link["anchor"])}</a>.</p>'
    )
```

Render it once near the hero/intro area. The visible FAQ list and JSON-LD schema must receive the same effective page mapping.

- [ ] **Step 6: Load overrides once during `build()`**

```python
content_overrides = load_content_overrides()
landing_html = clean_generated_html(
    build_landing_page(destinations, SEO_PAGES, listings, countries, content_overrides=content_overrides)
)
```

Pass the same list to every guide, country, and destination call. Do not reread the file for each page.

- [ ] **Step 7: Run runtime, builder, and static verification tests**

Run:

```bash
python3 -m unittest tests.test_seo_content_overrides tests.test_seo_ctr_content -v
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
```

Expected: all commands pass; the empty override file leaves existing content unchanged.

- [ ] **Step 8: Commit the override runtime**

```bash
git add src/seo_content_overrides.py data/seo_content_overrides.json tests/test_seo_content_overrides.py tests/test_seo_ctr_content.py src/build_unified_app.py artifacts
git commit -m "Render validated SEO content overrides"
```

---

### Task 5: Select Findings and Open One Consolidated Draft PR

**Files:**
- Modify: `scripts/seo_feedback_loop.py:17-45`
- Modify: `scripts/seo_feedback_loop.py:682-716`
- Modify: `scripts/seo_feedback_loop.py:784-1120`
- Modify: `scripts/seo_feedback_loop.py:1206-1290`
- Modify: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: `(Finding, issue_url)` pairs, issue labels, open generated PR metadata, sitemap URLs, and `generate_batch()` from Task 3.
- Produces: `list_generated_content_prs()`, `reconcile_merged_generated_content_prs()`, `select_generated_content_candidates()`, `generated_content_branch()`, `generated_content_pr_create_args()`, `build_generated_content_pr_body()`, and `scaffold_generated_content_pr()`.

- [ ] **Step 1: Write failing selection tests**

```python
def test_select_generated_content_candidates_prioritizes_and_caps_five(self) -> None:
    pairs = [make_editorial_pair(impressions=value, position=position) for value, position in [
        (10, 8), (80, 12), (30, 5), (60, 9), (50, 7), (40, 6),
    ]]
    selected = seo_feedback_loop.select_generated_content_candidates(
        pairs,
        issues=[],
        open_targets=set(),
        override_entries=[],
        now=datetime(2026, 8, 12, tzinfo=timezone.utc),
        limit=5,
    )
    self.assertEqual(5, len(selected))
    self.assertEqual(80, selected[0][0].payload["impressions"])

def test_selection_skips_auto_links_open_prs_implemented_and_cooldown(self) -> None:
    eligible = make_editorial_pair(impressions=25, position=8, target="https://globalhomeatlas.com/eligible/")
    auto_link = make_editorial_pair(
        impressions=60, position=6, target="https://globalhomeatlas.com/auto/", auto_implementation_safe=True
    )
    open_pr = make_editorial_pair(impressions=55, position=6, target="https://globalhomeatlas.com/open/")
    implemented = make_editorial_pair(impressions=50, position=6, target="https://globalhomeatlas.com/implemented/")
    cooldown = make_editorial_pair(impressions=45, position=6, target="https://globalhomeatlas.com/cooldown/")
    issues = [{
        "body": f"Fingerprint `{implemented[0].fingerprint}`",
        "labels": [{"name": "implemented-awaiting-google"}],
    }]
    override_entries = [{
        "target_url": "https://globalhomeatlas.com/cooldown/",
        "cooldown_until": "2026-09-01T00:00:00+00:00",
    }]
    selected = seo_feedback_loop.select_generated_content_candidates(
        [eligible, auto_link, open_pr, implemented, cooldown],
        issues=issues,
        open_targets={"https://globalhomeatlas.com/open/"},
        override_entries=override_entries,
        now=datetime(2026, 8, 12, tzinfo=timezone.utc),
        limit=5,
    )
    self.assertEqual([eligible], selected)
```

- [ ] **Step 2: Run the selection tests and verify failure**

Run: `python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests.test_select_generated_content_candidates_prioritizes_and_caps_five -v`

Expected: FAIL because the selector is undefined.

- [ ] **Step 3: Implement candidate selection**

Eligible kinds are exactly `IMPLEMENTATION_PR_KINDS`. Exclude `auto_implementation_safe`, `implemented-awaiting-google`, target URLs present in open generated-content PR bodies, and override entries whose `cooldown_until` is later than `now`. Sort by descending impressions, ascending position, then fingerprint; return at most five.

Add `list_generated_content_prs(state)` using `gh pr list --label generated-content --state {state} --json url,body,mergedAt`. Parse target URLs and fingerprints only from explicit fenced sections created by this automation; never treat arbitrary PR prose as executable input.

- [ ] **Step 4: Write failing branch and PR-argument tests**

```python
def test_generated_content_pr_is_draft_and_never_auto_merge_safe(self) -> None:
    args = seo_feedback_loop.generated_content_pr_create_args(
        branch="analytics/generated-content-2-abc123",
        base="main",
        title="Generate SEO content for 2 pages",
        body="body",
    )
    self.assertIn("--draft", args)
    labels = args[args.index("--label") + 1]
    self.assertIn("generated-content", labels)
    self.assertIn("needs-human-review", labels)
    self.assertNotIn("auto-merge-safe", labels)
```

- [ ] **Step 5: Implement stable batching and the before/after PR body**

`generated_content_branch()` hashes sorted fingerprints and returns `analytics/generated-content-{count}-{12_char_sha1}`. The PR body must list source issue, target URL, Search Console signal, before/after fields, validator outcome, model, and the exact verification commands. Escape or fence generated text so it cannot alter the PR body's structure.

- [ ] **Step 6: Implement `scaffold_generated_content_pr()`**

The function must:

1. return a stable dry-run marker without calling OpenAI;
2. call `generate_batch()` on the base branch;
3. return structured accepted/rejected/skipped details when no proposal is accepted;
4. create or reuse one deterministic branch;
5. upsert accepted entries into `data/seo_content_overrides.json`;
6. rebuild the site;
7. run `python3 -m unittest discover tests`, Python compilation, static verification, and tracking verification;
8. commit and push only after all checks pass;
9. open one draft PR with the required labels;
10. switch back to the base branch in `finally`.

Return a dataclass instead of a bare URL:

```python
@dataclass(frozen=True)
class GeneratedContentRun:
    pr_url: str | None
    accepted_count: int
    rejected: tuple[RejectedProposal, ...]
    skipped_reason: str | None
```

- [ ] **Step 7: Integrate the batch into `main()`**

Collect eligible pairs during the existing finding loop. Keep deterministic internal-link behavior unchanged. Do not call `scaffold_implementation_pr()` for a finding sent to generated content. Keep proposal-only landing-page candidates unchanged. Add these summary fields:

```python
"generated_content": {
    "accepted_count": generated_run.accepted_count,
    "rejected": [asdict(item) for item in generated_run.rejected],
    "skipped_reason": generated_run.skipped_reason,
    "pr": generated_run.pr_url,
    "reconciled_issue_count": reconciled_issue_count,
}
```

Add the generated draft URL to `pr_links` when present. Never pass it to `maybe_auto_merge()`.

Before candidate selection, call `reconcile_merged_generated_content_prs()`. It must inspect merged `generated-content` PRs, find each source issue by fingerprint, and idempotently add `implemented-awaiting-google` while removing `implementation-queued`. Add `reconciled_issue_count` to the generated-content summary. A reconciliation failure is reported and must not stop monitoring.

- [ ] **Step 8: Add orchestration regression tests**

Mock `generate_batch`, branch commands, and GitHub commands. Assert:

- two findings produce one PR;
- one rejected finding does not block one accepted finding;
- no accepted entries produce no branch or PR;
- missing key appears in the summary;
- a build/test failure causes no push and no PR;
- a merged generated-content PR marks its source issue `implemented-awaiting-google` exactly once;
- the generated PR URL is never provided to `maybe_auto_merge()`;
- deterministic internal-link PRs still use the existing auto-merge path;
- proposal-only Markdown PRs are not created for generated existing-page findings.

- [ ] **Step 9: Run feedback-loop tests**

Run: `python3 -m unittest tests.test_seo_feedback_loop -v`

Expected: PASS.

- [ ] **Step 10: Commit the consolidated PR orchestration**

```bash
git add scripts/seo_feedback_loop.py tests/test_seo_feedback_loop.py
git commit -m "Open generated SEO content draft PRs"
```

---

### Task 6: Report Generation Status Without Breaking Monitoring

**Files:**
- Modify: `scripts/seo_feedback_loop.py:501-680`
- Modify: `scripts/seo_email_notification.py:80-220`
- Modify: `tests/test_seo_feedback_loop.py`
- Modify: `tests/test_seo_email_notification.py`

**Interfaces:**
- Consumes: the `generated_content` summary from Task 5.
- Produces: control-issue, GitHub-comment, email, and Telegram status text.

- [ ] **Step 1: Write failing reporting tests**

```python
def test_control_issue_reports_generated_content_outcome(self) -> None:
    body = seo_feedback_loop.control_issue_body(
        report=minimal_report(), findings=[], issue_links=[], pr_links=[], auto_merged=[], indexnow={},
        generated_content={
            "accepted_count": 2,
            "rejected": [{"fingerprint": "gha-x", "target_url": "https://globalhomeatlas.com/x/", "reason": "new number"}],
            "skipped_reason": None,
            "pr": "https://github.com/schlafen318/property-research-dashboard/pull/101",
        },
    )
    self.assertIn("Generated content accepted: `2`", body)
    self.assertIn("new number", body)
    self.assertIn("pull/101", body)
```

- [ ] **Step 2: Run reporting tests and verify signature failures**

Run: `python3 -m unittest tests.test_seo_feedback_loop tests.test_seo_email_notification -v`

Expected: FAIL until reporting functions accept the new summary.

- [ ] **Step 3: Add concise generation sections to every channel**

Report accepted count, rejection count and reasons, missing-key/configuration status, and draft PR URL. Do not include prompts, full model responses, the API key, or raw exceptions that may contain request headers.

- [ ] **Step 4: Preserve notification fallback behavior**

Ensure SMTP/Telegram absence remains non-fatal and generation failure does not change notification exit codes. Add tests for missing `generated_content` so older fixture summaries remain valid.

- [ ] **Step 5: Run notification and feedback-loop tests**

Run: `python3 -m unittest tests.test_seo_feedback_loop tests.test_seo_email_notification -v`

Expected: PASS.

- [ ] **Step 6: Commit reporting support**

```bash
git add scripts/seo_feedback_loop.py scripts/seo_email_notification.py tests/test_seo_feedback_loop.py tests/test_seo_email_notification.py
git commit -m "Report SEO content generation outcomes"
```

---

### Task 7: Configure GitHub Actions and Document Operations

**Files:**
- Modify: `.github/workflows/seo-feedback-loop.yml`
- Modify: `docs/SEO_GROWTH_SYSTEM.md`
- Test: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: GitHub secret `OPENAI_API_KEY` and optional variable `SEO_CONTENT_MODEL`.
- Produces: a daily non-blocking generation attempt and documented operator workflow.

- [ ] **Step 1: Write a workflow-contract test**

Add a text-level test that reads the workflow and asserts:

```python
workflow = Path(".github/workflows/seo-feedback-loop.yml").read_text(encoding="utf-8")
self.assertIn("openai", workflow)
self.assertIn("OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}", workflow)
self.assertIn("SEO_CONTENT_MODEL: ${{ vars.SEO_CONTENT_MODEL || 'gpt-5.6' }}", workflow)
```

- [ ] **Step 2: Run the contract test and verify failure**

Run: `python3 -m unittest tests.test_seo_feedback_loop -v`

Expected: FAIL because the workflow does not yet install or expose OpenAI configuration.

- [ ] **Step 3: Update the workflow**

Change the dependency step to install the pinned major ranges used by the implementation:

```yaml
- name: Install API dependencies
  run: |
    python -m pip install --upgrade pip
    python -m pip install "google-api-python-client>=2,<3" "google-auth>=2,<3" "google-auth-httplib2>=0.2,<1" "openai>=2,<3"
```

Expose values only on the feedback-loop step:

```yaml
- name: Run feedback loop
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    SEO_CONTENT_MODEL: ${{ vars.SEO_CONTENT_MODEL || 'gpt-5.6' }}
  run: python3 scripts/seo_feedback_loop.py --apply --notify-user schlafen318 --summary-output output/seo/feedback-loop-summary.json
```

Do not add `OPENAI_API_KEY` to global job environment or shell output.

- [ ] **Step 4: Document setup and recovery**

Update `docs/SEO_GROWTH_SYSTEM.md` to explain:

- how to create `OPENAI_API_KEY` in repository Actions secrets;
- optional `SEO_CONTENT_MODEL` repository variable and default;
- eligible finding kinds and five-proposal cap;
- override-file architecture and prohibited claims;
- consolidated draft review and merge flow;
- 28-day cooldown and `implemented-awaiting-google` lifecycle;
- missing-key, API-failure, validation-rejection, stale-hash, and build-failure behavior;
- manual dry run and manual live run commands;
- how to revert a bad merged override by removing its JSON entry and rebuilding.

- [ ] **Step 5: Run workflow and documentation checks**

Run:

```bash
python3 -m unittest tests.test_seo_feedback_loop -v
python3 -m py_compile scripts/seo_content_generator.py scripts/seo_feedback_loop.py src/seo_content_overrides.py src/build_unified_app.py
git diff --check
```

Expected: PASS.

- [ ] **Step 6: Commit workflow and documentation**

```bash
git add .github/workflows/seo-feedback-loop.yml docs/SEO_GROWTH_SYSTEM.md tests/test_seo_feedback_loop.py
git commit -m "Configure automated SEO content generation"
```

---

### Task 8: End-to-End Verification and Controlled Rollout

**Files:**
- Modify if failures reveal omissions: files from Tasks 1–7 only.
- Verify: `artifacts/`, `output/seo/`, and GitHub Actions manual run.

**Interfaces:**
- Consumes: completed implementation and fixture reports.
- Produces: a verified local build and one controlled draft PR from a manual workflow run.

- [ ] **Step 1: Run the full unit suite**

Run: `python3 -m unittest discover tests -v`

Expected: PASS with no real OpenAI or GitHub calls from tests.

- [ ] **Step 2: Run compilation and static-site verification**

Run:

```bash
python3 -m py_compile src/build_unified_app.py src/seo_content_overrides.py scripts/seo_content_generator.py scripts/seo_feedback_loop.py scripts/seo_email_notification.py scripts/seo_monitor.py
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
```

Expected: all commands pass.

- [ ] **Step 3: Run the feedback loop in dry-run mode**

Run:

```bash
python3 scripts/seo_feedback_loop.py --dry-run --report tests/fixtures/seo-content-report.json --summary-output output/seo/feedback-loop-summary.json
```

Expected: output reports which findings would be selected, uses a stable generated-content branch marker, performs no API call, and makes no git or GitHub mutation.

- [ ] **Step 4: Inspect the generated diff contract with the fixture proposal**

Run:

```bash
python3 -m unittest tests.test_seo_content_generator.OpenAIGenerationTests.test_fixture_response_produces_one_override -v
```

Expected: PASS; accepted count is `1`, rejected count is `0`, and the override contains only the seven allowed content fields.

- [ ] **Step 5: Verify no editorial auto-merge path exists**

Run:

```bash
rg -n "generated-content|maybe_auto_merge|auto-merge-safe" scripts/seo_feedback_loop.py .github/workflows/seo-feedback-loop.yml
```

Expected: generated-content PR creation includes `--draft` and `needs-human-review`; only deterministic internal-link findings reach `maybe_auto_merge()`.

- [ ] **Step 6: Review repository state before the live run**

Run:

```bash
git status --short
git log --oneline -8
git diff --check
```

Expected: clean worktree and the seven implementation commits from Tasks 1–7.

- [ ] **Step 7: Configure the secret and perform one manual live run**

In GitHub repository settings, create the Actions secret `OPENAI_API_KEY`. Optionally create `SEO_CONTENT_MODEL`; otherwise use `gpt-5.6`. Trigger `SEO feedback loop` manually.

Expected:

- monitoring and issue #1 update succeed;
- at most one generated proposal is enabled for the first live rollout;
- one consolidated pull request opens as a draft;
- the PR includes before/after text and validation results;
- no editorial PR is merged automatically.

- [ ] **Step 8: Review the first two draft PRs before scheduled expansion**

Confirm rendered metadata, visible intro, FAQ/schema parity, internal-link target, absence of unsupported claims, and passing checks. After two successful reviewed drafts, change the rollout cap from one manual proposal to five scheduled proposals and rerun the full suite.

- [ ] **Step 9: Commit any verification-only corrections**

```bash
git add scripts src tests data .github/workflows/seo-feedback-loop.yml docs/SEO_GROWTH_SYSTEM.md artifacts
git commit -m "Verify automated SEO content rollout"
```

Skip this commit when verification produces no corrections.

---

## Completion Criteria

- Qualified existing-page findings produce actual override diffs, not proposal-only Markdown.
- OpenAI output is strict-schema JSON and is independently validated.
- The model cannot edit Python, workflows, or generated HTML directly.
- Homepage, guide, country, and destination pages render allowed overrides safely.
- Visible FAQs and FAQ schema remain identical.
- One daily batch creates no more than one draft PR and five proposals.
- Editorial content cannot auto-merge.
- Missing keys, API failures, refusals, stale hashes, policy failures, and build failures are reported without breaking monitoring.
- Open PR, implemented label, target URL, base hash, and cooldown suppress duplicates.
- Full unit, compilation, static-site, sitemap, and tracking checks pass.
- The first controlled live run opens a draft PR and leaves deployment pending review.
