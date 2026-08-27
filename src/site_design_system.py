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
    .foreign-buyer-answers .foreign-buyer-source-links { font-family: var(--foreign-buyer-sans); font-size: 12px; line-height: 1.45; }

    .foreign-buyer-layout { display: grid; grid-template-columns: minmax(0, 760px) minmax(190px, 238px); justify-content: space-between; gap: clamp(42px, 8vw, 108px); padding: 74px 0 84px; }
    .foreign-buyer-article { min-width: 0; }
    .foreign-buyer-article > section { padding: 0 0 52px; margin: 0 0 52px; border-bottom: 1px solid var(--foreign-buyer-rule); scroll-margin-top: 24px; }
    .foreign-buyer-article > section:last-child { margin-bottom: 0; }
    .foreign-buyer-article h2 { margin: 0 0 22px; font-family: var(--foreign-buyer-serif); font-size: clamp(32px, 4vw, 46px); font-weight: 500; line-height: 1.04; letter-spacing: -.02em; }
    .foreign-buyer-article h3 { margin: 26px 0 8px; font-size: 18px; font-weight: 600; line-height: 1.28; }
    .foreign-buyer-article p, .foreign-buyer-article li { max-width: 68ch; font-size: 16px; line-height: 1.72; }
    .foreign-buyer-article p { margin: 0 0 16px; }
    .foreign-buyer-article section > section + section { margin-top: 30px; padding-top: 1px; }
    .foreign-buyer-source-links { color: var(--foreign-buyer-muted); font-size: 13px !important; line-height: 1.5 !important; }
    .foreign-buyer-source-links a { margin-right: 10px; white-space: nowrap; }

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
    .foreign-buyer-destination-cards { display: none; }
    .foreign-buyer-checklist { margin: 0; padding: 0; list-style: none; border-top: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-checklist li { max-width: none; padding: 15px 0 15px 28px; border-bottom: 1px solid var(--foreign-buyer-rule); position: relative; }
    .foreign-buyer-checklist li::before { position: absolute; left: 1px; color: var(--foreign-buyer-accent); content: "✓"; }
    .foreign-buyer-faq-item { padding: 0 0 18px; margin: 0 0 18px; border-bottom: 1px solid var(--foreign-buyer-rule); }
    .foreign-buyer-faq-item h3 { margin-top: 0; }
    .foreign-buyer-article #sources ul { margin: 0; padding-left: 20px; }
    .foreign-buyer-article #sources li { margin-bottom: 9px; }

    .foreign-buyer-rail { position: sticky; top: 28px; align-self: start; padding-top: 5px; }
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
    .foreign-buyer-country-guide .gha-footer a { min-height: 30px; display: inline-flex; align-items: center; color: var(--foreign-buyer-paper); font-size: 13px; font-weight: 500; }
    .foreign-buyer-country-guide .gha-footer__signup { display: grid; align-content: start; gap: 10px; }

    @media (max-width: 960px) {
      .foreign-buyer-hero-grid { grid-template-columns: minmax(0, 1fr) minmax(260px, .74fr); gap: 36px; }
      .foreign-buyer-layout { grid-template-columns: 1fr; gap: 0; padding-top: 58px; }
      .foreign-buyer-article { max-width: 760px; }
      .foreign-buyer-rail { position: static; order: -1; max-width: 760px; padding: 0 0 38px; margin-bottom: 48px; border-bottom: 1px solid var(--foreign-buyer-rule); }
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
      .foreign-buyer-cost-table { display: block; overflow-x: auto; white-space: normal; }
      .foreign-buyer-cost-table th, .foreign-buyer-cost-table td { min-width: 132px; }
      .foreign-buyer-destination-table { display: none; }
      .foreign-buyer-destination-cards { display: grid; border-top: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-destination-cards article { padding: 20px 0; border-bottom: 1px solid var(--foreign-buyer-rule); }
      .foreign-buyer-destination-cards h3 { margin: 0 0 10px; font-family: var(--foreign-buyer-serif); font-size: 25px; font-weight: 500; }
      .foreign-buyer-destination-cards p { margin: 0 0 8px; }
      .foreign-buyer-country-guide .gha-footer__grid, .foreign-buyer-country-guide .gha-footer nav { grid-template-columns: 1fr; }
      .foreign-buyer-country-guide .gha-footer__grid { gap: 32px; }
    }
    """
