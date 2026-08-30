from __future__ import annotations

from html import escape
from typing import Iterable


def _links_html(links: Iterable[tuple[str, str]]) -> str:
    return "\n".join(
        f'<a href="{escape(href)}">{escape(label)}</a>' for href, label in links
    )


def site_header_html(links: Iterable[tuple[str, str]]) -> str:
    link_rows = tuple(links)
    desktop_links = _links_html(link_rows)
    mobile_links = _links_html(link_rows)
    return f"""
  <header class="gha-header">
    <nav class="gha-primary-nav" aria-label="Primary">
      <div class="gha-shell gha-header__inner">
        <a class="gha-brand" href="/" aria-label="Global Home Atlas home">
          <img src="/assets/global-home-atlas-logo-compact-light.svg" alt="Global Home Atlas" width="174" height="48">
        </a>
        <div class="gha-primary-links">{desktop_links}</div>
        <details class="gha-mobile-menu">
          <summary>Menu</summary>
          <nav aria-label="Mobile primary">{mobile_links}</nav>
        </details>
      </div>
    </nav>
  </header>
"""


def site_footer_html(site_name: str, contact_email: str) -> str:
    safe_name = escape(site_name)
    safe_email = escape(contact_email)
    return f"""
  <footer class="gha-footer">
    <div class="gha-shell gha-footer__grid">
      <div>
        <strong>{safe_name}</strong>
        <p>Independent research for overseas property decisions. Research only; verify legal, tax, immigration, and property advice locally.</p>
        <nav aria-label="Footer">
          <a href="/dashboard/">Research dashboard</a>
          <a href="/country-comparison/">Compare countries</a>
          <a href="/guides/">Guides</a>
          <a href="/methodology/">Methodology</a>
          <a href="/research-standards/">Research standards</a>
          <a href="/contact/">Contact</a>
        </nav>
      </div>
      <div class="gha-footer__signup">
        <strong>Get destination updates</strong>
        <p>Ask to be notified when new destination research or country hubs are added.</p>
        <a href="mailto:{safe_email}?subject=Global%20Home%20Atlas%20updates" data-track="contact_click" data-track-label="footer updates">Email {safe_email}</a>
      </div>
    </div>
  </footer>
"""


def landing_design_css() -> str:
    return r"""
    :root {
      --gha-ink: #24312d;
      --gha-paper: #f4efe4;
      --gha-surface: #fffdf7;
      --gha-muted: #646e69;
      --gha-rule: rgba(36, 49, 45, .24);
      --gha-accent: #a44e2f;
      --gha-link: #41665a;
      --gha-brass: #a98a4b;
      --gha-display-serif: "Iowan Old Style", Baskerville, "Palatino Linotype", Palatino, Georgia, serif;
      --gha-reading-sans: "Avenir Next", Avenir, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    html { scroll-behavior: smooth; overflow-x: hidden; }
    .gha-mode-landing { margin: 0; overflow-x: hidden; background: var(--gha-paper); color: var(--gha-ink); font-family: var(--gha-reading-sans); font-weight: 400; }
    .gha-mode-landing *, .gha-mode-landing *::before, .gha-mode-landing *::after { box-sizing: border-box; }
    .gha-mode-landing a { color: var(--gha-link); text-underline-offset: .18em; text-decoration-thickness: 1px; }
    .gha-mode-landing p { line-height: 1.62; }
    .gha-mode-landing :focus-visible { outline: 2px solid var(--gha-accent); outline-offset: 4px; }
    .gha-shell, .gha-mode-landing .shell { width: min(1220px, calc(100% - 48px)); margin-inline: auto; }

    .gha-header { position: absolute; inset: 0 0 auto; z-index: 20; color: var(--gha-ink); }
    .gha-header__inner { min-height: 86px; display: flex; align-items: center; justify-content: space-between; gap: 24px; border-bottom: 3px solid var(--gha-ink); }
    .gha-brand { display: flex; align-items: center; text-decoration: none; }
    .gha-brand img { display: block; width: 150px; height: auto; }
    .gha-primary-nav { display: block; }
    .gha-primary-links { display: flex; align-items: center; gap: 28px; }
    .gha-primary-links a { font-weight: 500; color: var(--gha-ink); font-size: 12px; letter-spacing: .075em; text-decoration: none; text-transform: uppercase; }
    .gha-primary-links a:hover { color: var(--gha-accent); }
    .gha-mobile-menu { display: none; position: relative; }
    .gha-mobile-menu summary { min-height: 44px; display: inline-flex; align-items: center; padding: 0 4px; color: var(--gha-ink); font-size: 14px; font-weight: 500; list-style: none; cursor: pointer; }
    .gha-mobile-menu summary::-webkit-details-marker { display: none; }
    .gha-mobile-menu nav { position: absolute; top: calc(100% + 8px); right: 0; width: min(82vw, 300px); display: grid; padding: 8px 16px; border: 1px solid var(--gha-rule); background: var(--gha-surface); box-shadow: 0 18px 44px rgba(36, 49, 45, .14); }
    .gha-mobile-menu nav a { min-height: 44px; display: flex; align-items: center; border-bottom: 1px solid var(--gha-rule); color: var(--gha-ink); font-size: 14px; font-weight: 500; text-decoration: none; }
    .gha-mobile-menu nav a:last-child { border-bottom: 0; }

    .gha-mode-landing .hero { min-height: 760px; display: grid; align-items: center; padding: 128px 0 92px; background: linear-gradient(90deg, rgba(244, 239, 228, .99) 0 43%, rgba(244, 239, 228, .78) 64%, rgba(244, 239, 228, .28)), url("/assets/atlas-map-coastal-sage.jpg") center / cover; }
    .gha-mode-landing .hero-grid { width: min(790px, calc(100% - 48px)); max-width: none; margin: 0 auto 0 max(24px, calc((100% - 1220px) / 2)); display: grid; padding-top: 42px; }
    .gha-mode-landing h1 { max-width: 780px; font-family: var(--gha-display-serif); font-size: clamp(54px, 5.5vw, 78px); font-weight: 500; line-height: .96; letter-spacing: -.035em; }
    .gha-mode-landing .lede { max-width: 670px; margin-top: 28px; color: #46524d; font-family: var(--gha-display-serif); font-size: clamp(20px, 2vw, 25px); line-height: 1.42; }
    .gha-mode-landing .hero-actions { display: flex; flex-wrap: wrap; align-items: center; margin-top: 32px; gap: 8px 22px; }
    .gha-mode-landing .hero-actions .text-action { flex-basis: 100%; }
    .gha-mode-landing .hero-secondary-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 24px; }
    .gha-mode-landing .primary-action { font-weight: 500; }
    .gha-mode-landing .primary-action { min-height: 46px; display: inline-flex; align-items: center; justify-content: center; padding: 0 18px; border: 1px solid var(--gha-ink); border-radius: 0; background: var(--gha-ink); color: var(--gha-paper); font-size: 12px; font-weight: 500; letter-spacing: .055em; text-decoration: none; text-transform: uppercase; box-shadow: none; }
    .gha-mode-landing .secondary-action { min-height: 44px; display: inline-flex; align-items: center; padding: 0; border: 0; border-radius: 0; background: transparent; color: var(--gha-ink); font-size: 14px; font-weight: 500; text-decoration: underline; text-underline-offset: .2em; }
    .gha-mode-landing .text-action { min-height: 44px; display: inline-flex; align-items: center; color: var(--gha-ink); font-size: 14px; font-weight: 500; text-decoration: none; }
    .gha-mode-landing .text-action::after, .gha-mode-landing .card-link::after { content: " →"; }
    .gha-mode-landing .primary-action:hover { background: var(--gha-accent); color: var(--gha-paper); }
    .gha-mode-landing .secondary-action:hover, .gha-mode-landing .text-action:hover { color: var(--gha-accent); }
    .gha-mode-landing main { position: relative; z-index: 1; margin: 0; }
    .gha-mode-landing .section { margin: 0; padding: 64px 0; border: 0; border-top: 1px solid var(--gha-rule); border-radius: 0; background: transparent; box-shadow: none; }
    .gha-mode-landing main > .shell > .section:first-child { border-top: 0; }
    .gha-mode-landing .section-header { display: flex; justify-content: space-between; gap: 24px; margin-bottom: 28px; align-items: end; }
    .gha-mode-landing .section-header h2, .gha-mode-landing .method-compact h2 { font-family: var(--gha-display-serif); font-size: clamp(38px, 4.2vw, 54px); font-weight: 500; line-height: 1; letter-spacing: -.025em; }
    .gha-mode-landing .section-header p, .gha-mode-landing .method-compact p { color: #47534e; font-size: 16px; line-height: 1.65; }

    .gha-mode-landing .atlas-tool-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 28px; }
    .gha-mode-landing .atlas-tool { min-height: 100%; display: grid; align-content: start; gap: 12px; padding: 20px 0 0; border-top: 3px solid var(--gha-ink); }
    .gha-mode-landing .atlas-tool h3 { margin: 0; font-family: var(--gha-display-serif); font-size: 27px; font-weight: 500; line-height: 1.08; }
    .gha-mode-landing .atlas-tool p { margin: 0; color: var(--gha-muted); font-size: 14px; }
    .gha-mode-landing .atlas-tool__link { min-height: 44px; display: inline-flex; align-items: center; margin-top: 4px; font-weight: 500; }
    .gha-mode-landing .atlas-tool__link::after { content: " →"; }
    .gha-mode-landing .atlas-support { margin: 24px 0 0; color: var(--gha-muted); font-size: 14px; }
    .gha-mode-landing .atlas-support a { font-weight: 500; }

    .gha-mode-landing .intent-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 42px; }
    .gha-mode-landing .intent-item { padding: 20px 0; border-top: 1px solid var(--gha-rule); }
    .gha-mode-landing .intent-item h3 { margin: 0; font-family: var(--gha-display-serif); font-size: 25px; font-weight: 500; }
    .gha-mode-landing .intent-item h3 a { color: var(--gha-ink); }
    .gha-mode-landing .intent-item p { margin: 8px 0 0; color: var(--gha-muted); font-size: 14px; }

    .gha-mode-landing .section--finder { margin: 72px 0; padding: 40px; border: 1px solid var(--gha-rule); background: rgba(255, 253, 247, .62); }
    .gha-mode-landing .finder-map-cue { display: none; }
    .gha-mode-landing .finder-grid { display: grid; grid-template-columns: minmax(250px, 300px) minmax(0, 1fr); gap: 38px; align-items: start; }
    .gha-mode-landing .finder-panel, .gha-mode-landing .finder-output { display: grid; align-content: start; gap: 14px; }
    .gha-mode-landing .finder-panel label { display: grid; gap: 9px; }
    .gha-mode-landing .finder-panel select { width: 100%; min-height: 48px; padding: 0 14px; border: 1px solid var(--gha-rule); border-radius: 0; background: var(--gha-surface); color: var(--gha-ink); font: inherit; font-weight: 400; }
    .gha-mode-landing .finder-step, .gha-mode-landing .finder-panel label, .gha-mode-landing .finder-result span, .gha-mode-landing .finder-result dt { color: var(--gha-accent); font-weight: 500; }
    .gha-mode-landing .finder-results { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
    .gha-mode-landing .finder-result { min-width: 0; display: grid; align-content: start; padding: 0 0 18px; border: 0; border-bottom: 1px solid var(--gha-rule); border-radius: 0; background: transparent; box-shadow: none; }
    .gha-mode-landing .finder-result__thumb { height: 112px; margin: 0 0 14px; border-radius: 0; }
    .gha-mode-landing .finder-result__thumb { overflow: hidden; background: #e8ede7; }
    .gha-mode-landing .finder-result__thumb img { width: 100%; height: 100%; display: block; object-fit: cover; }
    .gha-mode-landing .finder-result h3 { margin: 8px 0 4px; font-family: var(--gha-display-serif); font-size: 24px; font-weight: 500; line-height: 1.1; }
    .gha-mode-landing .finder-result h3 a { color: var(--gha-ink); }
    .gha-mode-landing .finder-result p { margin: 0 0 10px; color: var(--gha-muted); font-size: 14px; }
    .gha-mode-landing .finder-note { color: var(--gha-muted); font-size: 13px; }
    .gha-mode-landing .finder-signal strong { color: var(--gha-accent); font-size: 10px; font-weight: 600; letter-spacing: .07em; text-transform: uppercase; }
    .gha-mode-landing .card-link { font-weight: 500; }

    .gha-mode-landing .research-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 42px; }
    .gha-mode-landing .research-link { padding: 18px 0; border-top: 1px solid var(--gha-rule); }
    .gha-mode-landing .research-link h3 { margin: 0; font-family: var(--gha-display-serif); font-size: 24px; font-weight: 500; line-height: 1.15; }
    .gha-mode-landing .research-link a { min-height: 44px; display: inline-flex; align-items: center; color: var(--gha-ink); }
    .gha-mode-landing .research-link p { margin: 6px 0 0; color: var(--gha-muted); font-size: 14px; }

    .gha-mode-landing .browse-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 56px; }
    .gha-mode-landing .browse-column h3 { margin: 0 0 14px; font-family: var(--gha-display-serif); font-size: 27px; font-weight: 500; }
    .gha-mode-landing .browse-column ul { columns: 2; column-gap: 24px; margin: 0; padding: 0; list-style: none; }
    .gha-mode-landing .browse-column li { break-inside: avoid; margin: 0; }
    .gha-mode-landing .browse-column li a { min-height: 44px; display: flex; align-items: center; font-size: 14px; font-weight: 500; }
    .gha-mode-landing .browse-all { min-height: 44px; display: inline-flex; align-items: center; margin-top: 12px; font-weight: 500; }

    .gha-mode-landing .latest-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 28px; }
    .gha-mode-landing .latest-item { padding-top: 18px; border-top: 1px solid var(--gha-rule); }
    .gha-mode-landing .latest-item time { color: var(--gha-accent); font-size: 12px; font-weight: 500; }
    .gha-mode-landing .latest-item h3 { margin: 10px 0 6px; font-family: var(--gha-display-serif); font-size: 24px; font-weight: 500; line-height: 1.14; }
    .gha-mode-landing .latest-item h3 a { color: var(--gha-ink); }
    .gha-mode-landing .latest-item p { margin: 0; color: var(--gha-muted); font-size: 14px; }

    .gha-mode-landing .method-compact { display: flex; align-items: end; justify-content: space-between; gap: 32px; }
    .gha-mode-landing .coverage-line { color: var(--gha-ink); font-family: var(--gha-display-serif); font-size: 19px; }
    .gha-mode-landing .method-links { flex: none; display: grid; gap: 10px; }
    .gha-mode-landing .method-links a { font-weight: 500; }
    .gha-footer { font-weight: 400; }
    .gha-footer { padding: 54px 0; background: var(--gha-ink); color: var(--gha-paper); }
    .gha-footer__grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, 340px); gap: 48px; }
    .gha-footer strong { font-family: var(--gha-display-serif); font-size: 25px; font-weight: 500; }
    .gha-footer p { max-width: 54ch; color: rgba(244, 239, 228, .72); font-size: 13px; line-height: 1.6; }
    .gha-footer nav { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 24px; }
    .gha-footer a { color: var(--gha-paper); font-size: 13px; font-weight: 500; }
    .gha-footer__signup { display: grid; align-content: start; gap: 10px; }

    @media (max-width: 860px) {
      .gha-shell, .gha-mode-landing .shell { width: min(100% - 32px, 1220px); }
      .gha-header__inner { min-height: 74px; }
      .gha-primary-links { display: none; }
      .gha-mobile-menu { display: block; }
      .gha-mode-landing .hero { min-height: 680px; padding: 106px 0 72px; background-position: 62% center; }
      .gha-mode-landing .hero-grid { width: min(790px, calc(100% - 32px)); margin-left: 16px; padding-top: 28px; }
      .gha-mode-landing .atlas-tool-grid, .gha-mode-landing .latest-grid { grid-template-columns: 1fr; gap: 28px; }
      .gha-mode-landing .section--finder { margin: 48px 0; padding: 28px; }
      .gha-mode-landing .finder-grid { grid-template-columns: 1fr; gap: 22px; }
      .gha-mode-landing .finder-results { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .gha-footer__grid { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 620px) {
      .gha-mode-landing .hero { min-height: 620px; padding: 96px 0 60px; background: linear-gradient(180deg, rgba(244, 239, 228, .98) 0 58%, rgba(244, 239, 228, .72)), url("/assets/atlas-map-coastal-sage.jpg") 67% center / cover; }
      .gha-mode-landing h1 { font-size: clamp(52px, 16vw, 72px); }
      .gha-mode-landing .hero-secondary-actions { display: grid; gap: 2px; }
      .gha-mode-landing .hero-secondary-actions a { min-height: 44px; }
      .gha-mode-landing .section { padding: 48px 0; }
      .gha-mode-landing .section--finder { padding: 22px 18px; }
      .gha-mode-landing .section-header, .gha-mode-landing .method-compact { display: grid; grid-template-columns: 1fr; align-items: start; }
      .gha-mode-landing .intent-grid, .gha-mode-landing .research-grid, .gha-mode-landing .browse-grid, .gha-mode-landing .finder-results { grid-template-columns: 1fr; }
      .gha-mode-landing .finder-result { display: grid; grid-template-columns: 112px 1fr; column-gap: 14px; }
      .gha-mode-landing .finder-result__thumb { grid-row: 1 / span 6; height: 112px; }
      .gha-mode-landing .browse-grid { gap: 36px; }
      .gha-mode-landing .browse-column ul { columns: 1; }
      .gha-footer__grid, .gha-footer nav { grid-template-columns: 1fr; }
      .gha-footer__grid { gap: 32px; }
    }
    """


def utility_design_css() -> str:
    return r"""
    :root {
      --gha-ink: #24312d;
      --gha-paper: #f4efe4;
      --gha-surface: #fffdf7;
      --gha-muted: #646e69;
      --gha-rule: rgba(36, 49, 45, .24);
      --gha-accent: #a44e2f;
      --gha-link: #41665a;
      --gha-brass: #a98a4b;
      --gha-display-serif: "Iowan Old Style", Baskerville, "Palatino Linotype", Palatino, Georgia, serif;
      --gha-reading-sans: "Avenir Next", Avenir, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    html { scroll-behavior: smooth; overflow-x: hidden; }
    .gha-mode-utility {
      min-width: 320px;
      margin: 0;
      overflow-x: hidden;
      background: var(--gha-paper);
      color: var(--gha-ink);
      font-family: var(--gha-reading-sans);
      font-weight: 400;
    }
    .gha-mode-utility *, .gha-mode-utility *::before, .gha-mode-utility *::after { box-sizing: border-box; }
    .gha-mode-utility a { color: var(--gha-link); text-decoration-thickness: 1px; text-underline-offset: .18em; }
    .gha-mode-utility p { line-height: 1.62; }
    .gha-mode-utility :focus-visible { outline: 2px solid var(--gha-accent); outline-offset: 3px; }
    .gha-mode-utility .gha-shell, .gha-mode-utility .calc-shell { width: min(1180px, calc(100% - 48px)); margin-inline: auto; }

    .gha-mode-utility .gha-header { position: relative; z-index: 20; color: var(--gha-ink); }
    .gha-mode-utility .gha-primary-nav { display: block; }
    .gha-mode-utility .gha-header__inner { min-height: 86px; display: flex; align-items: center; justify-content: space-between; gap: 24px; border-bottom: 3px solid var(--gha-ink); }
    .gha-mode-utility .gha-brand { display: flex; align-items: center; text-decoration: none; }
    .gha-mode-utility .gha-brand img { display: block; width: 150px; height: auto; }
    .gha-mode-utility .gha-primary-links { display: flex; align-items: center; gap: 28px; }
    .gha-mode-utility .gha-primary-links a { color: var(--gha-ink); font-size: 12px; font-weight: 500; letter-spacing: .075em; text-decoration: none; text-transform: uppercase; }
    .gha-mode-utility .gha-primary-links a:hover { color: var(--gha-accent); }
    .gha-mode-utility .gha-mobile-menu { display: none; position: relative; }
    .gha-mode-utility .gha-mobile-menu summary { min-height: 44px; display: inline-flex; align-items: center; padding: 0 4px; color: var(--gha-ink); font-size: 14px; font-weight: 500; list-style: none; cursor: pointer; }
    .gha-mode-utility .gha-mobile-menu summary::-webkit-details-marker { display: none; }
    .gha-mode-utility .gha-mobile-menu nav { position: absolute; top: calc(100% + 8px); right: 0; z-index: 3; width: min(82vw, 300px); display: grid; padding: 8px 16px; border: 1px solid var(--gha-rule); background: var(--gha-surface); box-shadow: 0 18px 44px rgba(36, 49, 45, .14); }
    .gha-mode-utility .gha-mobile-menu nav a { min-height: 44px; display: flex; align-items: center; border-bottom: 1px solid var(--gha-rule); color: var(--gha-ink); font-size: 14px; font-weight: 500; text-decoration: none; }
    .gha-mode-utility .gha-mobile-menu nav a:last-child { border-bottom: 0; }

    .gha-mode-utility .calc-hero { padding: 0; border-bottom: 1px solid var(--gha-rule); background: var(--gha-paper); color: var(--gha-ink); }
    .gha-mode-utility .calc-hero > .calc-shell { padding: 52px 0 48px; }
    .gha-mode-utility .eyebrow { margin: 0 0 18px; color: var(--gha-accent); font-size: 12px; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; }
    .gha-mode-utility h1, .gha-mode-utility h2, .gha-mode-utility legend, .gha-mode-utility .result-decision, .gha-mode-utility .result-total, .gha-mode-utility .key-figures strong, .gha-mode-utility .result-period h3, .gha-mode-utility .result-comparison h3, .gha-mode-utility .result-comparison summary, .gha-mode-utility .current-cost-summary, .gha-mode-utility .target-figures strong {
      font-family: var(--gha-display-serif);
      font-weight: 500;
    }
    .gha-mode-utility h1 { max-width: 900px; margin: 0; font-size: clamp(48px, 6.2vw, 78px); line-height: .98; letter-spacing: -.035em; }
    .gha-mode-utility h2 { font-size: clamp(34px, 4vw, 48px); line-height: 1.03; letter-spacing: -.025em; }
    .gha-mode-utility .calc-hero .lede { max-width: 760px; margin: 26px 0 0; color: #46524d; font-family: var(--gha-display-serif); font-size: clamp(20px, 2vw, 24px); line-height: 1.42; }
    .gha-mode-utility .calc-hero .hint { color: var(--gha-muted); }
    .gha-mode-utility .calc-modes, .gha-mode-utility .finder-modes { display: flex; flex-wrap: wrap; gap: 0 24px; margin-top: 26px; border-bottom: 1px solid var(--gha-rule); font-weight: 500; }
    .gha-mode-utility .calc-modes a, .gha-mode-utility .finder-modes a { min-height: 44px; display: inline-flex; align-items: center; border: 0; color: var(--gha-ink); font-size: 14px; font-weight: 500; text-decoration: none; }
    .gha-mode-utility .calc-modes a[aria-current], .gha-mode-utility .finder-modes a[aria-current] { color: var(--gha-accent); box-shadow: inset 0 -2px 0 var(--gha-accent); }

    .gha-mode-utility main { padding: 0 0 76px; }
    .gha-mode-utility .quick-answer { padding: 56px 0; border-bottom: 1px solid var(--gha-rule); }
    .gha-mode-utility .quick-answer h2 { max-width: 780px; margin: 0 0 18px; }
    .gha-mode-utility .quick-answer > p { max-width: 820px; }
    .gha-mode-utility .quick-benchmark { background: transparent; }
    .gha-mode-utility .quick-benchmark caption { padding-left: 0; color: var(--gha-accent); font-size: 12px; font-weight: 500; letter-spacing: .07em; text-transform: uppercase; }
    .gha-mode-utility .quick-benchmark th, .gha-mode-utility .quick-benchmark td { padding-inline: 0 20px; border-color: var(--gha-rule); }
    .gha-mode-utility .calculator-layout { margin-top: 56px; gap: 32px; }
    .gha-mode-utility .calc-panel { border: 1px solid var(--gha-rule); border-radius: 4px; background: rgba(255, 253, 247, .72); box-shadow: none; }
    .gha-mode-utility label, .gha-mode-utility .field-label { font-weight: 500; }
    .gha-mode-utility legend { font-size: 24px; }
    .gha-mode-utility input, .gha-mode-utility select, .gha-mode-utility button { border-color: var(--gha-rule); border-radius: 0; font-family: var(--gha-reading-sans); font-weight: 400; }
    .gha-mode-utility input, .gha-mode-utility select { background: var(--gha-surface); }
    .gha-mode-utility .primary { border-radius: 0; background: var(--gha-ink); color: var(--gha-paper); font-size: 12px; font-weight: 500; letter-spacing: .055em; text-transform: uppercase; }
    .gha-mode-utility .primary:hover { background: var(--gha-accent); }
    .gha-mode-utility .text-button { color: var(--gha-link); font-weight: 500; }
    .gha-mode-utility .hint { color: var(--gha-muted); }
    .gha-mode-utility .result-decision { font-size: 22px; }
    .gha-mode-utility .content-section { padding: 52px 0; border-color: var(--gha-rule); }
    .gha-mode-utility .content-section > h2 { margin-top: 0; }
    .gha-mode-utility table { background: transparent; }
    .gha-mode-utility th, .gha-mode-utility td { border-color: var(--gha-rule); }

    .gha-mode-utility .gha-footer { padding: 54px 0; background: var(--gha-ink); color: var(--gha-paper); }
    .gha-mode-utility .gha-footer__grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, 340px); gap: 48px; }
    .gha-mode-utility .gha-footer strong { font-family: var(--gha-display-serif); font-size: 25px; font-weight: 500; }
    .gha-mode-utility .gha-footer p { max-width: 54ch; color: rgba(244, 239, 228, .72); font-size: 13px; line-height: 1.6; }
    .gha-mode-utility .gha-footer nav { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 24px; }
    .gha-mode-utility .gha-footer a { color: var(--gha-paper); font-size: 13px; font-weight: 500; }
    .gha-mode-utility .gha-footer__signup { display: grid; align-content: start; gap: 10px; }

    @media (max-width: 860px) {
      .gha-mode-utility .gha-shell, .gha-mode-utility .calc-shell { width: min(100% - 32px, 1180px); }
      .gha-mode-utility .gha-header__inner { min-height: 74px; }
      .gha-mode-utility .gha-primary-links { display: none; }
      .gha-mode-utility .gha-mobile-menu { display: block; }
      .gha-mode-utility .gha-footer__grid { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 620px) {
      .gha-mode-utility .calc-hero > .calc-shell { padding: 38px 0 36px; }
      .gha-mode-utility h1 { font-size: clamp(46px, 14vw, 64px); }
      .gha-mode-utility .quick-answer { padding: 42px 0; }
      .gha-mode-utility .calculator-layout { margin-top: 42px; }
      .gha-mode-utility .gha-footer__grid, .gha-mode-utility .gha-footer nav { grid-template-columns: 1fr; }
      .gha-mode-utility .gha-footer__grid { gap: 32px; }
    }
    """


def top_level_page_design_css() -> str:
    return utility_design_css() + r"""
    .gha-top-level .gha-shell, .gha-top-level .page-shell, .gha-top-level .shell, .gha-top-level .calc-shell { width: min(1220px, calc(100% - 48px)); margin-inline: auto; }
    .gha-top-level .page-hero, .gha-top-level .compact-hero { min-height: 0; padding: 0; border-bottom: 1px solid var(--gha-rule); background: var(--gha-paper); color: var(--gha-ink); }
    .gha-top-level .page-hero > .page-shell, .gha-top-level .compact-hero__content { padding: 52px 0 48px; }
    .gha-top-level .page-hero-grid { display: block; }
    .gha-top-level .page-eyebrow, .gha-top-level .eyebrow { margin: 0 0 18px; color: var(--gha-accent); font-size: 12px; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; }
    .gha-top-level h1, .gha-top-level h2, .gha-top-level h3 { font-family: var(--gha-display-serif); font-weight: 500; }
    .gha-top-level .page-hero h1, .gha-top-level .compact-hero h1 { max-width: 900px; margin: 0; font-size: clamp(48px, 6.2vw, 78px); line-height: .98; letter-spacing: -.035em; }
    .gha-top-level .page-lede, .gha-top-level .compact-hero .lede { max-width: 780px; margin: 26px 0 0; color: #46524d; font-family: var(--gha-display-serif); font-size: clamp(20px, 2vw, 24px); line-height: 1.42; }
    .gha-top-level .guide-page-hero { background-image: none; }
    .gha-top-level .guide-page-layout { margin-left: 0; }
    .gha-top-level .countries-hero { padding-bottom: 0; }
    @media (max-width: 860px) {
      .gha-top-level .gha-shell, .gha-top-level .page-shell, .gha-top-level .shell, .gha-top-level .calc-shell { width: min(100% - 32px, 1220px); }
    }
    @media (max-width: 620px) {
      .gha-top-level .page-hero > .page-shell, .gha-top-level .compact-hero__content { padding: 38px 0 36px; }
    }
    """


def retirement_finder_design_css() -> str:
    return utility_design_css() + r"""
    .retirement-finder-page .gha-shell, .retirement-finder-page .page-shell { width: min(1220px, calc(100% - 48px)); margin-inline: auto; }
    .retirement-finder-page .finder-form, .retirement-finder-page .finder-results, .retirement-finder-page .finder-editorial { max-width: 960px; }
    .retirement-finder-page .finder-hero { padding: 0; border-bottom: 1px solid var(--gha-rule); background: var(--gha-paper); }
    .retirement-finder-page .finder-hero .page-shell { padding: 52px 0 48px; }
    .retirement-finder-page .finder-eyebrow { margin: 0 0 18px; color: var(--gha-accent); font-size: 12px; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; }
    .retirement-finder-page h1, .retirement-finder-page h2, .retirement-finder-page h3, .retirement-finder-page legend, .retirement-finder-page .finder-summary strong {
      font-family: var(--gha-display-serif);
      font-weight: 500;
    }
    .retirement-finder-page h1 { max-width: 850px; margin: 0; font-size: clamp(48px, 6.2vw, 76px); line-height: .98; letter-spacing: -.035em; }
    .retirement-finder-page .finder-hero .lede { max-width: 760px; margin: 26px 0 0; color: #46524d; font-family: var(--gha-display-serif); font-size: clamp(20px, 2vw, 24px); line-height: 1.42; }
    .retirement-finder-page main { padding: 52px 0 76px; }
    .retirement-finder-page .finder-form { gap: 0; }
    .retirement-finder-page .finder-wizard-progress, .retirement-finder-page .finder-wizard-actions, .retirement-finder-page .finder-adjust-plan { display: none; }
    .retirement-finder-page .finder-section { padding: 30px 0 34px; border: 0; border-bottom: 1px solid var(--gha-rule); border-radius: 0; background: transparent; box-shadow: none; }
    .retirement-finder-page .finder-section:first-child { padding-top: 0; }
    .retirement-finder-page .finder-step.finder-step-mobile, .retirement-finder-page .finder-mobile-only { display: none; }
    .retirement-finder-page .finder-profile { padding-bottom: 16px; border-bottom: 0; }
    .retirement-finder-page .finder-section-split { padding-top: 0; }
    .retirement-finder-page .finder-plan-summary { margin-top: 18px; padding: 8px 0; border-top: 1px solid var(--gha-rule); border-bottom: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-plan-summary > summary { min-height: 44px; display: flex; align-items: center; font-weight: 400; cursor: pointer; }
    .retirement-finder-page .finder-review-summary { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0; margin: 24px 0; border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-review-summary div { padding: 16px 0; border-bottom: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-review-summary dt { color: var(--gha-muted); font-size: 12px; }
    .retirement-finder-page .finder-review-summary dd { margin: 4px 0 0; font-family: var(--gha-display-serif); font-size: 20px; }
    .retirement-finder-page .finder-step { display: block; margin-bottom: 10px; color: var(--gha-accent); font-size: 11px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; }
    .retirement-finder-page legend, .retirement-finder-page .finder-results h2 { margin: 0 0 8px; font-size: clamp(29px, 3vw, 38px); line-height: 1.05; }
    .retirement-finder-page .section-help, .retirement-finder-page .hint { color: var(--gha-muted); }
    .retirement-finder-page .field label { font-weight: 500; }
    .retirement-finder-page .finder-setting-options { display: flex; flex-wrap: wrap; gap: 4px 20px; margin-top: 7px; }
    .retirement-finder-page .finder-setting-options .check { min-height: 44px; margin: 0; }
    .retirement-finder-page .finder-section-conditional > [data-finder-group] { margin-top: 0; padding-top: 0; border-top: 0; }
    .retirement-finder-page input, .retirement-finder-page select { border: 1px solid var(--gha-rule); border-radius: 0; background: var(--gha-surface); font-family: var(--gha-reading-sans); font-weight: 400; }
    .retirement-finder-page .finder-submit { width: fit-content; min-height: 48px; padding: 0 18px; border: 1px solid var(--gha-ink); border-radius: 0; background: var(--gha-ink); color: var(--gha-paper); font-family: var(--gha-reading-sans); font-size: 12px; font-weight: 500; letter-spacing: .055em; text-transform: uppercase; }
    .retirement-finder-page .finder-submit:hover { background: var(--gha-accent); }
    .retirement-finder-page .privacy-note { margin-top: 12px; }
    .retirement-finder-page .finder-results { margin-top: 64px; padding: 42px 0 0; border: 0; border-top: 3px solid var(--gha-ink); border-radius: 0; background: transparent; }
    .retirement-finder-page .finder-results > * { min-width: 0; }
    .retirement-finder-page .finder-results-intro { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(280px, .85fr); gap: 48px; align-items: end; }
    .retirement-finder-page .finder-active-filters { margin: 10px 0 0; color: var(--gha-muted); font-size: 14px; }
    .retirement-finder-page .finder-result-read { margin: 0; font-family: var(--gha-display-serif); font-size: 21px; line-height: 1.45; }
    .retirement-finder-page .finder-summary { grid-template-columns: repeat(4, minmax(0, 1fr)); margin: 28px 0 36px; border: 0; border-top: 1px solid var(--gha-rule); border-bottom: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-summary div { padding: 16px 16px 18px 0; }
    .retirement-finder-page .finder-summary div + div { border: 0; }
    .retirement-finder-page .finder-summary span { color: var(--gha-accent); font-weight: 500; letter-spacing: .035em; text-transform: uppercase; }
    .retirement-finder-page .finder-summary strong { font-size: clamp(23px, 2.6vw, 31px); }
    .retirement-finder-page .finder-landscape { margin: 0 0 44px; padding: 26px 0 30px; border-top: 1px solid var(--gha-rule); border-bottom: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-landscape-head { display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 18px; }
    .retirement-finder-page .finder-landscape h3, .retirement-finder-page .finder-matches-section > h3, .retirement-finder-page .finder-projection-section > h3 { margin: 0; font-size: clamp(28px, 3vw, 38px); }
    .retirement-finder-page .finder-landscape-kicker { margin: 0 0 7px; color: var(--gha-accent); font-size: 11px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; }
    .retirement-finder-page .finder-landscape-key { display: flex; flex-wrap: wrap; gap: 10px 18px; margin: 0; color: var(--gha-muted); font-size: 12px; }
    .retirement-finder-page .finder-landscape-key span::before { width: 10px; height: 10px; display: inline-block; margin-right: 7px; border-radius: 50%; content: ""; }
    .retirement-finder-page .finder-key-match::before { border: 2px solid var(--gha-accent); background: var(--gha-paper); }
    .retirement-finder-page .finder-landscape-projection { display: flex; justify-content: space-between; gap: 18px; align-items: baseline; margin: 0 0 18px; padding: 11px 0; border-top: 1px solid var(--gha-brass); border-bottom: 1px solid var(--gha-brass); color: var(--gha-brass); }
    .retirement-finder-page .finder-landscape-projection strong { font-family: var(--gha-display-serif); font-size: clamp(22px, 2.6vw, 29px); font-weight: 500; }
    .retirement-finder-page .finder-landscape-axis, .retirement-finder-page .finder-landscape-row { display: grid; grid-template-columns: minmax(190px, 1.15fr) minmax(360px, 3fr) auto; column-gap: 18px; }
    .retirement-finder-page .finder-landscape-axis { min-height: 24px; align-items: end; color: var(--gha-muted); font-size: 10px; }
    .retirement-finder-page .finder-landscape-axis > :last-child { text-align: right; }
    .retirement-finder-page .finder-landscape-row { min-height: 64px; align-items: center; color: var(--gha-ink); text-decoration: none; }
    .retirement-finder-page .finder-landscape-name { min-width: 0; font-family: var(--gha-display-serif); font-size: 18px; line-height: 1.1; }
    .retirement-finder-page .finder-landscape-name small { display: block; margin-top: 2px; color: var(--gha-muted); font-family: var(--gha-reading-sans); font-size: 10px; }
    .retirement-finder-page .finder-landscape-track { position: relative; height: 38px; border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-landscape-fill { position: absolute; top: -1px; left: 0; width: var(--target-position); height: 2px; background: var(--gha-link); }
    .retirement-finder-page .finder-landscape-row.is-within .finder-landscape-fill { background: var(--gha-link); }
    .retirement-finder-page .finder-landscape-row.is-over .finder-landscape-fill { background: var(--gha-accent); }
    .retirement-finder-page .finder-landscape-row.is-on-target .finder-landscape-fill { background: var(--gha-brass); }
    .retirement-finder-page .finder-landscape-cost-dot { position: absolute; z-index: 2; top: 0; left: var(--target-position); width: 10px; height: 10px; border-radius: 50%; background: var(--gha-link); transform: translate(-50%, -50%); }
    .retirement-finder-page .finder-landscape-row.is-over .finder-landscape-cost-dot { background: var(--gha-accent); }
    .retirement-finder-page .finder-landscape-row.is-on-target .finder-landscape-cost-dot { background: var(--gha-brass); }
    .retirement-finder-page .finder-landscape-row.is-match .finder-landscape-cost-dot { width: 13px; height: 13px; border: 2px solid var(--gha-accent); background: var(--gha-paper); }
    .retirement-finder-page .finder-landscape-plan-marker { position: absolute; z-index: 1; top: -6px; left: var(--capital-position); width: 2px; height: 13px; background: var(--gha-brass); transform: translateX(-50%); }
    .retirement-finder-page .finder-landscape-scale-zero, .retirement-finder-page .finder-landscape-scale-plan { position: absolute; top: 9px; color: var(--gha-muted); font-size: 9px; line-height: 1; white-space: nowrap; }
    .retirement-finder-page .finder-landscape-scale-zero { left: 0; }
    .retirement-finder-page .finder-landscape-scale-plan { left: clamp(24px, var(--capital-position), calc(100% - 24px)); color: var(--gha-brass); transform: translateX(-50%); }
    .retirement-finder-page .finder-landscape-rank { color: var(--gha-accent); font-size: 10px; letter-spacing: .06em; }
    .retirement-finder-page .finder-landscape-value { min-width: 150px; text-align: right; }
    .retirement-finder-page .finder-landscape-required { display: block; font-family: var(--gha-display-serif); font-size: 17px; line-height: 1.15; }
    .retirement-finder-page .finder-landscape-buffer { display: block; margin-top: 3px; color: var(--gha-muted); font-size: 10px; line-height: 1.2; }
    .retirement-finder-page .finder-landscape-row.is-within .finder-landscape-buffer { color: var(--gha-link); }
    .retirement-finder-page .finder-landscape-row.is-over .finder-landscape-buffer { color: var(--gha-accent); }
    .retirement-finder-page .finder-landscape figcaption { margin: 18px 0 0; }
    .retirement-finder-page .finder-landscape-toggle { display: none; }
    .retirement-finder-page .finder-matches-section { margin-bottom: 46px; }
    .retirement-finder-page .finder-list { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 28px; margin-top: 24px; }
    .retirement-finder-page .finder-comparison-section { margin: 8px 0 46px; padding: 32px 0; border-top: 3px solid var(--gha-ink); border-bottom: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-comparison-heading h3 { margin: 0 0 22px; font-size: clamp(28px, 3vw, 38px); }
    .retirement-finder-page .finder-comparison-scroll { overflow-x: auto; }
    .retirement-finder-page .finder-comparison-table { width: 100%; min-width: 680px; border-collapse: collapse; text-align: left; }
    .retirement-finder-page .finder-comparison-table caption { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
    .retirement-finder-page .finder-comparison-table th, .retirement-finder-page .finder-comparison-table td { padding: 12px 14px 12px 0; border-top: 1px solid var(--gha-rule); vertical-align: top; font-weight: 400; }
    .retirement-finder-page .finder-comparison-table thead th { border-top: 0; font-family: var(--gha-display-serif); font-size: 20px; }
    .retirement-finder-page .finder-comparison-table tbody th { width: 190px; color: var(--gha-muted); }
    .retirement-finder-page .finder-comparison-table select { min-width: 0; margin-top: 8px; font-size: 13px; }
    .retirement-finder-page .finder-comparison-links { display: grid; gap: 5px; }
    .retirement-finder-page .finder-comparison-mobile { display: none; }
    .retirement-finder-page .finder-comparison-mobile article { padding: 20px 0; border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-comparison-mobile h4 { margin: 0 0 10px; font-family: var(--gha-display-serif); font-size: 25px; font-weight: 500; }
    .retirement-finder-page .finder-comparison-mobile dl { display: grid; gap: 12px; margin: 18px 0 0; }
    .retirement-finder-page .finder-comparison-mobile dt { color: var(--gha-muted); font-size: 12px; }
    .retirement-finder-page .finder-comparison-mobile dd { margin: 2px 0 0; }
    .retirement-finder-page .finder-comparison-status { min-height: 1.5em; color: var(--gha-muted); font-size: 13px; }
    .retirement-finder-page .finder-share-section { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 8px 18px; align-items: center; margin: 0 0 46px; padding: 24px 0; border-top: 1px solid var(--gha-rule); border-bottom: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-share-section button { min-height: 44px; padding: 0 16px; border: 1px solid var(--gha-ink); border-radius: 0; background: var(--gha-ink); color: var(--gha-paper); font: 500 12px var(--gha-reading-sans); letter-spacing: .05em; text-transform: uppercase; }
    .retirement-finder-page .finder-share-section p { margin: 0; color: var(--gha-muted); font-size: 13px; }
    .retirement-finder-page #finder-share-status, .retirement-finder-page #finder-share-url { grid-column: 1 / -1; }
    .retirement-finder-page #finder-shared-error { max-width: 960px; margin: 0 0 28px; padding: 14px 0; border-top: 1px solid var(--gha-accent); border-bottom: 1px solid var(--gha-accent); }
    .retirement-finder-page .finder-projection-section { padding-top: 38px; border-top: 3px solid var(--gha-ink); }
    .retirement-finder-page .finder-projection-wrap { position: relative; margin-bottom: 36px; padding: 18px 0 32px; border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-projection-wrap h4 { margin: 0 0 12px; font-family: var(--gha-display-serif); font-size: 24px; font-weight: 500; }
    .retirement-finder-page .finder-projection-scroll { overflow-x: auto; overscroll-behavior-inline: contain; }
    .retirement-finder-page .finder-projection-chart { display: block; width: 100%; min-width: 640px; height: auto; overflow: visible; }
    .retirement-finder-page .finder-chart-axis { stroke: var(--gha-rule); stroke-width: 1; }
    .retirement-finder-page .finder-chart-target { stroke: #9b6a33; stroke-width: 1.5; stroke-dasharray: 5 4; }
    .retirement-finder-page .finder-chart-target-label { fill: #7a5227; font-size: 11px; font-weight: 500; }
    .retirement-finder-page .finder-chart-axis-label { fill: var(--gha-muted); font-size: 10px; }
    .retirement-finder-page .finder-chart-bar { fill: #315e50; }
    .retirement-finder-page .finder-chart-year { opacity: 0; transform: translateY(8px); animation: finder-year-in .35s ease forwards; animation-delay: var(--year-delay); cursor: pointer; outline: none; }
    .retirement-finder-page .finder-chart-year.is-active .finder-chart-bar, .retirement-finder-page .finder-chart-year:focus-visible .finder-chart-bar { stroke: var(--gha-ink); stroke-width: 2px; }
    .retirement-finder-page .finder-chart-tooltip { top: 62px; border: 0; border-radius: 0; background: var(--gha-ink); color: var(--gha-paper); }
    .retirement-finder-page .finder-chart-tooltip span { color: #dfe7e3; }
    .retirement-finder-page .finder-result { min-width: 0; padding: 16px 0 22px; border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-result:first-child { border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-tier { color: var(--gha-accent); font-weight: 500; }
    .retirement-finder-page .finder-result h3 { margin: 3px 0; font-size: clamp(27px, 3vw, 35px); }
    .retirement-finder-page .finder-result h3 a { color: var(--gha-ink); white-space: normal; overflow-wrap: anywhere; }
    .retirement-finder-page .finder-result dl { grid-template-columns: 1fr; margin-top: 18px; }
    .retirement-finder-page .finder-result dt { color: var(--gha-muted); }
    .retirement-finder-page .finder-result dd { font-family: var(--gha-display-serif); font-size: 21px; font-weight: 500; }
    .retirement-finder-page .finder-rationale { margin: 16px 0 0; color: var(--gha-muted); font-size: 14px; line-height: 1.55; }
    .retirement-finder-page .finder-result-actions { display: flex; flex-wrap: wrap; gap: 6px 22px; margin-top: 20px; }
    .retirement-finder-page .finder-result-actions a { min-height: 44px; display: inline-flex; align-items: center; font-weight: 500; }
    .retirement-finder-page .finder-evidence { border-color: var(--gha-rule); }
    .retirement-finder-page .finder-evidence summary { min-height: 44px; display: flex; align-items: center; font-weight: 500; }
    .retirement-finder-page .finder-editorial { margin-top: 72px; border-top: 3px solid var(--gha-ink); }
    .retirement-finder-page .finder-editorial section { padding: 42px 0; border-bottom: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-editorial h2 { max-width: 780px; margin: 0 0 18px; font-size: clamp(34px, 4vw, 48px); line-height: 1.03; }
    .retirement-finder-page .finder-editorial p, .retirement-finder-page .finder-editorial ul { max-width: 760px; }
    .retirement-finder-page .finder-comparison { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 32px; }
    .retirement-finder-page .finder-comparison article { padding-top: 18px; border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-comparison h3 { margin: 0; font-size: 26px; }
    .retirement-finder-page .finder-faq details { max-width: 820px; padding: 16px 0; border-top: 1px solid var(--gha-rule); }
    .retirement-finder-page .finder-faq summary { min-height: 44px; display: flex; align-items: center; font-weight: 500; cursor: pointer; }
    .retirement-finder-page .finder-capital-scenarios nav { display: flex; flex-wrap: wrap; gap: 10px 24px; }
    .retirement-finder-page .finder-capital-scenarios a { font-weight: 400; }
    @media (max-width: 860px) {
      .retirement-finder-page .gha-shell, .retirement-finder-page .page-shell { width: min(100% - 32px, 1220px); }
      .retirement-finder-page .finder-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .retirement-finder-page .finder-results-intro { grid-template-columns: 1fr; gap: 14px; }
      .retirement-finder-page .finder-list { grid-template-columns: 1fr; }
    }
    @media (max-width: 820px) {
      .retirement-finder-page .finder-landscape-axis { display: none; }
      .retirement-finder-page .finder-landscape-row { grid-template-columns: minmax(0, 1fr) minmax(120px, auto); gap: 4px 14px; padding: 9px 0; }
      .retirement-finder-page .finder-landscape-track { grid-column: 1 / -1; grid-row: 2; height: 30px; margin-top: 7px; }
      .retirement-finder-page .finder-landscape-value { min-width: 0; grid-column: 2; grid-row: 1; }
    }
    @media (max-width: 760px) {
      .retirement-finder-page.finder-wizard-editing { height: 100vh; height: 100svh; overflow: hidden; }
      .retirement-finder-page.finder-wizard-editing .gha-header__inner { min-height: 56px; padding: 0 16px; border-bottom-width: 1px; }
      .retirement-finder-page.finder-wizard-editing .gha-brand img { width: 112px; }
      .retirement-finder-page.finder-wizard-editing .gha-primary-links { display: none; }
      .retirement-finder-page.finder-wizard-editing .finder-hero, .retirement-finder-page.finder-wizard-editing .context-link, .retirement-finder-page.finder-wizard-editing .finder-editorial, .retirement-finder-page.finder-wizard-editing .gha-footer { display: none; }
      .retirement-finder-page.finder-wizard-editing main { height: calc(100svh - 56px); padding: 0; overflow: hidden; }
      .retirement-finder-page.finder-wizard-editing #retirement-destination-finder > .page-shell { width: 100%; height: 100%; }
      .retirement-finder-page.finder-wizard-editing .finder-form { display: flex; height: 100%; min-height: 0; flex-direction: column; padding: 0; }
      .retirement-finder-page.finder-wizard-editing .finder-form-privacy { display: none; }
      .retirement-finder-page.finder-wizard-editing .finder-wizard-progress { flex: none; margin: 0; padding: 14px 16px 10px; }
      .retirement-finder-page.finder-wizard-editing .finder-errors { flex: none; margin: 0 16px 8px; padding: 10px 12px; font-size: 13px; }
      .retirement-finder-page.finder-wizard-editing .finder-section { display: block; min-height: 0; flex: 1 1 auto; overflow-y: auto; overscroll-behavior: contain; padding: 18px 16px calc(92px + env(safe-area-inset-bottom)); border: 0; }
      .retirement-finder-page.finder-wizard-editing .finder-step-desktop, .retirement-finder-page.finder-wizard-editing .finder-desktop-only { display: none; }
      .retirement-finder-page.finder-wizard-editing .finder-step-mobile { display: block; }
      .retirement-finder-page.finder-wizard-editing .finder-mobile-only { display: block; }
      .retirement-finder-page .finder-form { padding-bottom: 84px; }
      .retirement-finder-page .finder-wizard-progress { display: block; margin: 0 0 18px; }
      .retirement-finder-page .finder-wizard-progress p { margin: 0 0 8px; color: var(--gha-accent); font-size: 11px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; }
      .retirement-finder-page .finder-wizard-progressbar { position: relative; height: 2px; overflow: hidden; background: var(--gha-rule); }
      .retirement-finder-page .finder-wizard-progressbar::after { position: absolute; inset: 0 auto 0 0; width: var(--finder-progress, 16.6667%); background: var(--gha-accent); content: ""; transition: width .2s ease; }
      .retirement-finder-page .finder-section[tabindex="-1"]:focus { outline: 0; }
      .retirement-finder-page .finder-section .finder-step { display: none; }
      .retirement-finder-page .finder-wizard-actions { display: grid; position: fixed; z-index: 20; right: 0; bottom: 0; left: 0; grid-template-columns: auto minmax(0, 1fr); gap: 10px; padding: 10px 16px calc(10px + env(safe-area-inset-bottom)); border-top: 1px solid var(--gha-rule); background: rgba(245, 241, 232, .97); }
      .retirement-finder-page .finder-wizard-actions button { min-height: 48px; padding: 0 18px; border-radius: 0; font: 500 12px var(--gha-reading-sans); letter-spacing: .045em; text-transform: uppercase; }
      .retirement-finder-page .finder-wizard-back { border: 1px solid var(--gha-rule); background: transparent; color: var(--gha-ink); }
      .retirement-finder-page .finder-wizard-next { border: 1px solid var(--gha-ink); background: var(--gha-ink); color: var(--gha-paper); }
      .retirement-finder-page .finder-wizard-next:disabled { opacity: .45; }
      .retirement-finder-page.finder-wizard-editing .finder-form > .finder-submit { display: none; }
      .retirement-finder-page .finder-adjust-plan { min-height: 44px; display: inline-flex; align-items: center; justify-content: center; padding: 0; border: 0; background: transparent; color: var(--gha-link); font: 400 14px var(--gha-reading-sans); text-decoration: underline; text-underline-offset: .18em; }
      .retirement-finder-page .finder-comparison-scroll { display: none; }
      .retirement-finder-page .finder-comparison-mobile { display: block; }
      .retirement-finder-page .finder-landscape-head { display: block; }
      .retirement-finder-page .finder-landscape-key { margin-top: 12px; }
      .retirement-finder-page .finder-landscape-axis { display: none; }
      .retirement-finder-page .finder-landscape-row { grid-template-columns: minmax(0, 1fr) auto; gap: 4px 14px; padding: 9px 0; }
      .retirement-finder-page .finder-landscape-track { grid-column: 1 / -1; grid-row: 2; height: 30px; margin-top: 7px; }
      .retirement-finder-page .finder-landscape-value { min-width: 0; grid-column: 2; grid-row: 1; }
      .retirement-finder-page .finder-landscape-rows:not(.is-expanded) > .finder-landscape-item:nth-child(n + 6) { display: none; }
      .retirement-finder-page .finder-landscape-toggle { min-height: 44px; display: inline-flex; align-items: center; margin-top: 14px; padding: 0; border: 0; background: transparent; color: var(--gha-link); font-size: 14px; text-decoration: underline; text-underline-offset: .18em; cursor: pointer; }
    }
    @media (max-width: 620px) {
      .retirement-finder-page .finder-hero .page-shell { padding: 24px 0 26px; }
      .retirement-finder-page h1 { font-size: clamp(38px, 11vw, 52px); }
      .retirement-finder-page .finder-hero .lede { margin-top: 18px; font-size: 19px; }
      .retirement-finder-page .finder-modes { margin-top: 18px; }
      .retirement-finder-page main { padding-top: 38px; }
      .retirement-finder-page .field-grid, .retirement-finder-page .finder-summary, .retirement-finder-page .finder-result dl, .retirement-finder-page .finder-comparison { grid-template-columns: 1fr; }
      .retirement-finder-page.finder-wizard-editing #finder-profile .field-grid, .retirement-finder-page.finder-wizard-editing #finder-current-resources .field-grid, .retirement-finder-page.finder-wizard-editing #finder-retirement-income .field-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .retirement-finder-page.finder-wizard-editing #finder-financing .field-grid, .retirement-finder-page.finder-wizard-editing #finder-before-retirement [data-finder-group="rental"] .field-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .retirement-finder-page.finder-wizard-editing #finder-profile .planning-currency, .retirement-finder-page.finder-wizard-editing #finder-current-resources .field:last-child { grid-column: 1 / -1; }
      .retirement-finder-page.finder-wizard-editing #finder-before-retirement [data-finder-group="buyNow"] .field, .retirement-finder-page.finder-wizard-editing #finder-before-retirement [data-finder-group="rental"] .field:last-child { grid-column: 1 / -1; }
      .retirement-finder-page.finder-wizard-editing .finder-section { padding-bottom: calc(76px + env(safe-area-inset-bottom)); }
      .retirement-finder-page.finder-wizard-editing #finder-preferences .field-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .retirement-finder-page.finder-wizard-editing #finder-preferences .field:nth-child(1) { grid-column: 1; grid-row: 1; }
      .retirement-finder-page.finder-wizard-editing #finder-preferences .field:nth-child(2) { grid-column: 1 / -1; grid-row: 2; }
      .retirement-finder-page.finder-wizard-editing #finder-preferences .field:nth-child(3) { grid-column: 2; grid-row: 1; }
      .retirement-finder-page.finder-wizard-editing #finder-preferences .finder-setting-options { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 12px; }
      .retirement-finder-page.finder-wizard-editing #finder-preferences .finder-setting-options .check { min-height: 38px; }
      .retirement-finder-page .finder-summary div { padding-right: 0; }
      .retirement-finder-page .finder-submit { width: 100%; }
      .retirement-finder-page .finder-share-section { grid-template-columns: 1fr; }
    }
    @media (max-width: 620px) and (max-height: 600px) {
      .retirement-finder-page.finder-wizard-editing .finder-wizard-progress { padding: 8px 16px 6px; }
      .retirement-finder-page.finder-wizard-editing .finder-section { padding-top: 12px; }
      .retirement-finder-page.finder-wizard-editing #finder-profile #finder-currency-note { display: none; }
    }
    @media (prefers-reduced-motion: reduce) {
      .retirement-finder-page .finder-chart-year { animation: none; opacity: 1; transform: none; }
    }
    """


def foreign_buyer_country_guide_css() -> str:
    return r"""
    :root {
      --foreign-buyer-ink: #202825;
      --foreign-buyer-paper: #f3efe5;
      --foreign-buyer-surface: #fbf8f0;
      --foreign-buyer-muted: #646e69;
      --foreign-buyer-accent: #a44e2f;
      --foreign-buyer-rule: rgba(32, 40, 37, .22);
      --foreign-buyer-serif: "Iowan Old Style", Baskerville, "Palatino Linotype", Palatino, Georgia, serif;
      --foreign-buyer-sans: "Avenir Next", Avenir, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    html { scroll-behavior: smooth; overflow-x: hidden; }
    body.foreign-buyer-country-guide {
      min-width: 320px;
      margin: 0;
      overflow-x: hidden;
      background: var(--foreign-buyer-paper);
      color: var(--foreign-buyer-ink);
      font-family: var(--foreign-buyer-sans);
      font-weight: 400;
    }
    .foreign-buyer-country-guide *, .foreign-buyer-country-guide *::before, .foreign-buyer-country-guide *::after { box-sizing: border-box; }
    .foreign-buyer-country-guide a { color: #365d50; text-decoration-thickness: 1px; text-underline-offset: .18em; overflow-wrap: anywhere; }
    .foreign-buyer-country-guide :focus-visible { outline: 2px solid var(--foreign-buyer-accent); outline-offset: 4px; }
    .foreign-buyer-shell, .foreign-buyer-country-guide .gha-shell { width: min(1180px, calc(100% - 48px)); margin-inline: auto; }

    .foreign-buyer-country-guide .gha-header { position: relative; z-index: 2; }
    .foreign-buyer-country-guide .gha-header__inner { min-height: 86px; display: flex; align-items: center; justify-content: space-between; gap: 24px; border-bottom: 3px solid var(--foreign-buyer-ink); }
    .foreign-buyer-country-guide .gha-brand { display: flex; align-items: center; }
    .foreign-buyer-country-guide .gha-brand img { display: block; width: 150px; height: auto; }
    .foreign-buyer-country-guide .gha-primary-links { display: flex; align-items: center; gap: 28px; }
    .foreign-buyer-country-guide .gha-primary-links a { min-height: 44px; display: inline-flex; align-items: center; color: var(--foreign-buyer-ink); font-size: 12px; font-weight: 500; letter-spacing: .075em; text-decoration: none; text-transform: uppercase; }
    .foreign-buyer-country-guide .gha-primary-links a:hover { color: var(--foreign-buyer-accent); }
    .foreign-buyer-country-guide .gha-mobile-menu { display: none; position: relative; }
    .foreign-buyer-country-guide .gha-mobile-menu summary { min-height: 44px; display: inline-flex; align-items: center; color: var(--foreign-buyer-ink); font-size: 14px; font-weight: 500; list-style: none; cursor: pointer; }
    .foreign-buyer-country-guide .gha-mobile-menu summary::-webkit-details-marker { display: none; }
    .foreign-buyer-country-guide .gha-mobile-menu nav { position: absolute; top: calc(100% + 8px); right: 0; z-index: 3; width: min(82vw, 300px); display: grid; padding: 8px 16px; border: 1px solid var(--foreign-buyer-rule); background: var(--foreign-buyer-surface); box-shadow: 0 18px 44px rgba(32, 40, 37, .14); }
    .foreign-buyer-country-guide .gha-mobile-menu nav a { min-height: 44px; display: flex; align-items: center; border-bottom: 1px solid var(--foreign-buyer-rule); color: var(--foreign-buyer-ink); font-size: 14px; font-weight: 500; text-decoration: none; }
    .foreign-buyer-country-guide .gha-mobile-menu nav a:last-child { border-bottom: 0; }

    .foreign-buyer-hero { padding: 58px 0 0; border-bottom: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-hero-grid { display: grid; grid-template-columns: minmax(0, 1.08fr) minmax(300px, .92fr); align-items: end; gap: clamp(36px, 6vw, 84px); padding-bottom: 58px; }
    .foreign-buyer-hero-grid > *, .foreign-buyer-layout > * { min-width: 0; }
    .foreign-buyer-hero h1 { max-width: 700px; margin: 0; font-family: var(--foreign-buyer-serif); font-size: clamp(48px, 6.1vw, 78px); font-weight: 500; line-height: .98; letter-spacing: -.035em; }
    .foreign-buyer-hero h1 + p { max-width: 650px; margin: 26px 0 0; color: #46524d; font-family: var(--foreign-buyer-serif); font-size: clamp(19px, 2vw, 25px); line-height: 1.42; }
    .foreign-buyer-byline { margin: 20px 0 0; color: var(--foreign-buyer-muted); font-size: 13px; line-height: 1.5; }
    .foreign-buyer-hero figure { margin: 0; }
    .foreign-buyer-hero img { display: block; width: 100%; aspect-ratio: 4 / 3; object-fit: cover; }
    .foreign-buyer-hero figcaption { margin-top: 10px; color: var(--foreign-buyer-muted); font-size: 13px; }

    .foreign-buyer-answers { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-top: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-answers article { min-width: 0; padding: 24px 22px 26px 0; border-right: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-answers article + article { padding-left: 22px; }
    .foreign-buyer-answers article:last-child { border-right: 0; }
    .foreign-buyer-answers h2 { margin: 0; font-size: 12px; font-weight: 600; letter-spacing: .07em; text-transform: uppercase; }
    .foreign-buyer-answers p { margin: 11px 0 0; font-family: var(--foreign-buyer-serif); font-size: 18px; line-height: 1.34; }
    .foreign-buyer-contextual-source { overflow-wrap: anywhere; }

    .foreign-buyer-layout { display: grid; grid-template-columns: minmax(0, 760px) minmax(190px, 238px); justify-content: space-between; gap: clamp(42px, 8vw, 108px); padding: 74px 0 84px; }
    .foreign-buyer-article { grid-column: 1; grid-row: 1; min-width: 0; }
    .foreign-buyer-article > section { padding: 0 0 52px; margin: 0 0 52px; border-bottom: 1px solid var(--foreign-buyer-rule); scroll-margin-top: 24px; }
    .foreign-buyer-article > section:last-child { margin-bottom: 0; }
    .foreign-buyer-article h2 { margin: 0 0 22px; font-family: var(--foreign-buyer-serif); font-size: clamp(32px, 4vw, 46px); font-weight: 500; line-height: 1.04; letter-spacing: -.02em; }
    .foreign-buyer-article h3 { margin: 26px 0 8px; font-size: 18px; font-weight: 600; line-height: 1.28; }
    .foreign-buyer-article p, .foreign-buyer-article li { max-width: 68ch; font-size: 16px; line-height: 1.72; }
    .foreign-buyer-article p { margin: 0 0 16px; }
    .foreign-buyer-article section > section + section { margin-top: 30px; padding-top: 1px; }
    .foreign-buyer-steps { display: grid; gap: 0; margin: 0; padding: 0; list-style: none; counter-reset: foreign-buyer-step; }
    .foreign-buyer-steps li { display: grid; grid-template-columns: 38px minmax(0, 1fr); gap: 18px; max-width: none; padding: 22px 0; border-top: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-steps li:last-child { border-bottom: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-steps li > span { display: block; padding-top: 1px; color: var(--foreign-buyer-accent); font-family: var(--foreign-buyer-serif); font-size: 27px; line-height: 1; }
    .foreign-buyer-steps h3 { margin: 0 0 7px; }
    .foreign-buyer-steps p { margin-bottom: 8px; }

    .foreign-buyer-cost-table, .foreign-buyer-destination-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .foreign-buyer-cost-table th, .foreign-buyer-cost-table td, .foreign-buyer-destination-table th, .foreign-buyer-destination-table td { padding: 15px 12px; border-top: 1px solid var(--foreign-buyer-rule); vertical-align: top; text-align: left; line-height: 1.52; }
    .foreign-buyer-cost-table thead th, .foreign-buyer-destination-table thead th { color: var(--foreign-buyer-muted); font-size: 12px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }
    .foreign-buyer-cost-table tbody tr:last-child th, .foreign-buyer-cost-table tbody tr:last-child td, .foreign-buyer-destination-table tbody tr:last-child th, .foreign-buyer-destination-table tbody tr:last-child td { border-bottom: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-cost-table th[scope="row"], .foreign-buyer-destination-table th[scope="row"] { font-weight: 600; }
    .foreign-buyer-mobile-label { display: none; }
    .foreign-buyer-destination-cards { display: none; }
    .foreign-buyer-acquisition-example { margin-top: 34px; padding: 26px 28px; border: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-acquisition-example h3 { margin-top: 0; }
    .foreign-buyer-acquisition-example dl { margin: 22px 0 18px; }
    .foreign-buyer-acquisition-example dl > div { display: grid; grid-template-columns: minmax(0, 1fr) minmax(190px, .9fr); gap: 24px; padding: 12px 0; border-top: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-acquisition-example dt { font-weight: 600; }
    .foreign-buyer-acquisition-example dd { margin: 0; }
    .foreign-buyer-acquisition-example dd strong, .foreign-buyer-acquisition-example dd span { display: block; }
    .foreign-buyer-acquisition-example dd span, .foreign-buyer-acquisition-caveat, .foreign-buyer-price-note { color: var(--foreign-buyer-muted); font-size: 13px; }
    .foreign-buyer-acquisition-total { padding-top: 16px; border-top: 1px solid var(--foreign-buyer-ink); }
    .foreign-buyer-reader-tools { display: flex; flex-wrap: wrap; gap: 8px 28px; margin-top: 18px; }
    .foreign-buyer-reader-tools a { min-height: 44px; display: inline-flex; align-items: center; font-weight: 600; }
    .foreign-buyer-checklist { margin: 0; padding: 0; list-style: none; border-top: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-checklist li { max-width: none; padding: 15px 0 15px 28px; border-bottom: 1px solid var(--foreign-buyer-rule); position: relative; }
    .foreign-buyer-checklist li::before { position: absolute; left: 1px; color: var(--foreign-buyer-accent); content: "✓"; }
    .foreign-buyer-faq-item { padding: 0 0 18px; margin: 0 0 18px; border-bottom: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-faq-item h3 { margin-top: 0; }
    .foreign-buyer-article #sources ul { margin: 0; padding-left: 20px; }
    .foreign-buyer-article #sources li { margin-bottom: 9px; }

    .foreign-buyer-rail { position: sticky; grid-column: 2; grid-row: 1; top: 28px; align-self: start; padding-top: 5px; }
    .foreign-buyer-rail > p { margin: 0 0 10px; color: var(--foreign-buyer-muted); font-size: 12px; font-weight: 600; letter-spacing: .07em; text-transform: uppercase; }
    .foreign-buyer-rail nav { border-top: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-rail a { min-height: 44px; display: flex; align-items: center; border-bottom: 1px solid var(--foreign-buyer-rule); color: var(--foreign-buyer-ink); font-size: 14px; font-weight: 500; text-decoration: none; }
    .foreign-buyer-rail a:hover { color: var(--foreign-buyer-accent); }
    .foreign-buyer-rail .foreign-buyer-atlas-link { margin-top: 20px; color: #365d50; }

    .foreign-buyer-country-guide .gha-footer { padding: 54px 0; background: var(--foreign-buyer-ink); color: var(--foreign-buyer-paper); }
    .foreign-buyer-country-guide .gha-footer__grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, 340px); gap: 48px; }
    .foreign-buyer-country-guide .gha-footer strong { font-family: var(--foreign-buyer-serif); font-size: 25px; font-weight: 500; }
    .foreign-buyer-country-guide .gha-footer p { max-width: 54ch; color: rgba(243, 239, 229, .74); font-size: 13px; line-height: 1.6; }
    .foreign-buyer-country-guide .gha-footer nav { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 24px; }
    .foreign-buyer-country-guide .gha-footer a { min-height: 44px; display: inline-flex; align-items: center; color: var(--foreign-buyer-paper); font-size: 13px; font-weight: 500; }
    .foreign-buyer-country-guide .gha-footer__signup { display: grid; align-content: start; gap: 10px; }

    @media (max-width: 960px) {
      .foreign-buyer-hero-grid { grid-template-columns: minmax(0, 1fr) minmax(260px, .74fr); gap: 36px; }
      .foreign-buyer-layout { grid-template-columns: 1fr; gap: 0; padding-top: 58px; }
      .foreign-buyer-article { grid-column: 1; grid-row: 2; max-width: 760px; }
      .foreign-buyer-rail { grid-column: 1; grid-row: 1; position: static; max-width: 760px; padding: 0 0 38px; margin-bottom: 48px; border-bottom: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-rail nav { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 22px; }
      .foreign-buyer-rail .foreign-buyer-atlas-link { display: inline-flex; width: fit-content; }
    }
    @media (max-width: 720px) {
      .foreign-buyer-shell, .foreign-buyer-country-guide .gha-shell { width: min(100% - 32px, 1180px); }
      .foreign-buyer-country-guide .gha-header__inner { min-height: 74px; }
      .foreign-buyer-country-guide .gha-primary-links { display: none; }
      .foreign-buyer-country-guide .gha-mobile-menu { display: block; }
      .foreign-buyer-hero { padding-top: 34px; }
      .foreign-buyer-hero-grid { grid-template-columns: 1fr; gap: 30px; padding-bottom: 42px; }
      .foreign-buyer-hero h1 { font-size: clamp(44px, 14vw, 64px); }
      .foreign-buyer-hero h1 + p { margin-top: 20px; font-size: 20px; }
      .foreign-buyer-hero img { aspect-ratio: 16 / 10; }
      .foreign-buyer-answers { grid-template-columns: 1fr; }
      .foreign-buyer-answers article, .foreign-buyer-answers article + article { padding: 19px 0; border-right: 0; border-bottom: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-answers article:last-child { border-bottom: 0; }
      .foreign-buyer-layout { padding: 42px 0 62px; }
      .foreign-buyer-article > section { padding-bottom: 42px; margin-bottom: 42px; }
      .foreign-buyer-article h2 { font-size: 35px; }
      .foreign-buyer-article p, .foreign-buyer-article li { font-size: 16px; }
      .foreign-buyer-rail { padding-bottom: 28px; margin-bottom: 40px; }
      .foreign-buyer-rail nav { grid-template-columns: 1fr; }
      .foreign-buyer-cost-table, .foreign-buyer-cost-table tbody, .foreign-buyer-cost-table tr, .foreign-buyer-cost-table th, .foreign-buyer-cost-table td { display: block; width: 100%; }
      .foreign-buyer-cost-table thead { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; }
      .foreign-buyer-cost-table tr { padding: 17px 0; border-top: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-cost-table th, .foreign-buyer-cost-table td { padding: 0; border: 0; }
      .foreign-buyer-cost-table th { margin-bottom: 8px; font-size: 18px; }
      .foreign-buyer-cost-table td + td { margin-top: 10px; }
      .foreign-buyer-mobile-label { display: block; margin-bottom: 3px; color: var(--foreign-buyer-muted); font-size: 12px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }
      .foreign-buyer-cost-table tbody tr:last-child th, .foreign-buyer-cost-table tbody tr:last-child td { border-bottom: 0; }
      .foreign-buyer-destination-table { display: none; }
      .foreign-buyer-destination-cards { display: grid; border-top: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-destination-cards article { padding: 20px 0; border-bottom: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-destination-cards h3 { margin: 0 0 10px; font-family: var(--foreign-buyer-serif); font-size: 25px; font-weight: 500; }
      .foreign-buyer-destination-cards h3 a { min-height: 44px; display: inline-flex; align-items: center; }
      .foreign-buyer-destination-cards p { margin: 0 0 8px; }
      .foreign-buyer-acquisition-example { padding: 22px 20px; }
      .foreign-buyer-acquisition-example dl > div { grid-template-columns: 1fr; gap: 4px; }
      .foreign-buyer-reader-tools { display: grid; gap: 0; }
      .foreign-buyer-reader-tools a { border-top: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-country-guide .gha-footer__grid, .foreign-buyer-country-guide .gha-footer nav { grid-template-columns: 1fr; }
      .foreign-buyer-country-guide .gha-footer__grid { gap: 32px; }
    }
    """
