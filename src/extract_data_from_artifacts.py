from bs4 import BeautifulSoup
from pathlib import Path
import json, re, runpy
ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)

def slug(s):
    return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

# Extract destination cards from dashboard HTML
html = (ART / 'dashboard_mobile_first_v10.html').read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')
dests=[]
for card in soup.select('details.dest'):
    name = card.get('data-dest') or card.select_one('h2').get_text(' ', strip=True)
    rank_text = card.select_one('.rank').get_text(strip=True) if card.select_one('.rank') else ''
    rank = int(re.sub(r'\D','',rank_text) or 0)
    scores = {}
    for row in card.select('.score-row'):
        label = row.select_one('.score-top span').get_text(' ', strip=True)
        score = float(row.select_one('.score-top b').get_text(strip=True))
        weight_text = row.select_one('.weight').get_text(' ', strip=True) if row.select_one('.weight') else ''
        m = re.search(r'(\d+(?:\.\d+)?)%', weight_text)
        weight = float(m.group(1))/100 if m else None
        scores[slug(label).replace('-','_')] = {'label': label, 'score': score, 'weight': weight}
    qmetrics = card.select('.quick-metrics div')
    qm={}
    for div in qmetrics:
        k=div.select_one('small').get_text(' ', strip=True) if div.select_one('small') else ''
        v=div.select_one('b').get_text(' ', strip=True) if div.select_one('b') else ''
        qm[slug(k).replace('-','_')] = v
    # panel section
    panel = card.select_one('section.judge')
    panel_summary = ''
    pros = ''
    cons = ''
    if panel:
        ps = panel.find_all('p', recursive=False)
        panel_summary = ps[0].get_text(' ', strip=True) if ps else ''
        boxes = panel.select('.proscons > div')
        if len(boxes)>0: pros = boxes[0].select_one('p').get_text(' ', strip=True) if boxes[0].select_one('p') else ''
        if len(boxes)>1: cons = boxes[1].select_one('p').get_text(' ', strip=True) if boxes[1].select_one('p') else ''
    verdict = card.select_one('summary .verdict').get_text(' ', strip=True) if card.select_one('summary .verdict') else ''
    info_sections = card.select('.info-grid > div')
    ownership_notes = red_flags = price_basis = price_confidence = profit_driver = ''
    rental={}
    for div in info_sections:
        h3 = div.select_one('h3').get_text(' ', strip=True) if div.select_one('h3') else ''
        if h3 == 'Ownership':
            ps=div.find_all('p')
            ownership_notes = ps[0].get_text(' ', strip=True) if ps else ''
            red_flags = ps[1].get_text(' ', strip=True) if len(ps)>1 else ''
        elif h3 == 'Rental / yield':
            dts=div.find_all('dt'); dds=div.find_all('dd')
            rental={slug(dt.get_text(' ', strip=True)).replace('-','_'): dd.get_text(' ', strip=True) for dt,dd in zip(dts,dds)}
        elif h3 == 'Price basis':
            ps=div.find_all('p')
            price_basis = ps[1].get_text(' ', strip=True) if len(ps)>1 else ''
            price_confidence = ps[2].get_text(' ', strip=True).replace('Confidence: ','') if len(ps)>2 else ''
        elif h3 == 'Profit driver':
            p=div.select_one('p')
            profit_driver = p.get_text(' ', strip=True) if p else ''
    dests.append({
        'id': slug(name), 'name': name, 'rank': rank,
        'country': card.get('data-country'), 'category': card.get('data-group'),
        'overall_score': float(card.get('data-score') or 0),
        'usd_per_m2': float(card.get('data-price') or 0),
        'net_yield_estimate': card.get('data-yield'),
        'quick_metrics': qm,
        'panel_summary': panel_summary,
        'pros': [x.strip() for x in pros.split(';') if x.strip()],
        'cons': [x.strip() for x in cons.split(';') if x.strip()],
        'panel_verdict': verdict,
        'scores': scores,
        'ownership_notes': ownership_notes,
        'red_flags': red_flags,
        'rental': rental,
        'price_basis': price_basis,
        'price_confidence': price_confidence,
        'profit_driver': profit_driver
    })
(DATA / 'destinations.json').write_text(json.dumps(dests, ensure_ascii=False, indent=2), encoding='utf-8')

# Extract listing rows from source script context
ctx = runpy.run_path(str(ROOT / 'src' / 'create_listings_appendix.py'))
rows = ctx['rows']
FX = ctx['FX']
listings=[]
for r in rows:
    listings.append({
        'destination_id': slug(r['dest']),
        'destination_name': r['dest'],
        'property_type': r['ptype'],
        'listing_name': r['name'],
        'usd_price': r.get('usd'),
        'local_currency': r.get('curr'),
        'local_price': r.get('price'),
        'size_m2': r.get('size'),
        'usd_per_m2': r.get('usd_m2'),
        'source_name': r.get('source'),
        'source_url': r.get('url'),
        'note': r.get('note'),
        'confidence': 'Medium',
        'captured_date': '2026-06-21'
    })
(DATA / 'listings.json').write_text(json.dumps(listings, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Extracted {len(dests)} destinations and {len(listings)} listings')
