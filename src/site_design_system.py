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
      --gha-muted: #68726d;
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
    .gha-mode-landing .browse-column li { break-inside: avoid; margin: 0 0 10px; }
    .gha-mode-landing .browse-column li a { font-size: 14px; font-weight: 500; }
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
