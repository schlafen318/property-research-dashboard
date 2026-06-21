import runpy
from html import escape
from pathlib import Path
from collections import defaultdict
ctx = runpy.run_path('/mnt/data/create_listings_appendix.py')
rows = ctx['rows']
FX = ctx['FX']
by = defaultdict(list)
for r in rows:
    by[r['dest']].append(r)

fx_line = 'FX used: JPY/USD 161.305, EUR/USD 1.14784, CAD/USD 0.70609, NZD/USD 0.57370, CHF/USD 1.24288, THB/USD 0.0303905, IDR/USD 0.000056243, VND/USD 0.0000380084. USD listings are unchanged. All headline prices below are converted to USD; original local listing price is retained underneath.'

def usd_price(x):
    if x is None: return 'POA'
    if x >= 10_000_000:
        return '$' + format(x/1e6, ',.1f') + 'm'
    if x >= 1_000_000:
        return '$' + format(x/1e6, ',.2f') + 'm'
    if x >= 1000:
        return '$' + format(x/1000, ',.0f') + 'k'
    return '$' + format(x, ',.0f')

def usd_m2(x):
    if x is None: return '—'
    return '$' + format(x, ',.0f') + '/m²'

def local_price(r):
    if not r['price']: return 'POA'
    return f"{r['curr']} {r['price']:,.0f}"

def m2fmt(x): return '—' if x is None else f"{x:,.0f} m²"

css = '''
:root{--bg:#f6f7fb;--card:#fff;--ink:#172033;--muted:#667085;--line:#e4e7ec;--blue:#0B2E6D;--gold:#B78300;--soft:#eef3fb;--green:#0f766e}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}header{background:linear-gradient(135deg,#0B2E6D,#16498f);color:#fff;padding:28px 18px}header h1{margin:0 0 8px;font-size:26px}header p{margin:4px 0;color:#dbe6ff}.wrap{max-width:1180px;margin:auto;padding:18px}.controls{position:sticky;top:0;background:rgba(246,247,251,.96);backdrop-filter:blur(8px);padding:10px 0;z-index:5}.controls input,.controls select{width:100%;padding:12px;border:1px solid var(--line);border-radius:12px;margin:4px 0;font-size:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;box-shadow:0 2px 10px rgba(16,24,40,.04)}h2{font-size:20px;margin:0 0 8px;color:var(--blue)}.tag{display:inline-block;background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:4px 9px;font-size:12px;color:var(--blue);margin-bottom:8px}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:#475467;font-size:12px}.usd{font-weight:700;color:var(--green);font-size:14px}.local{color:var(--muted);font-size:12px;margin-top:2px}a{color:var(--blue);word-break:break-word}.note{color:var(--muted);font-size:12px}.mini{font-size:12px;color:var(--muted)}header .mini{color:#dbe6ff}.stat{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}.pill{background:#fff7e0;border:1px solid #ead393;color:#684c00;border-radius:10px;padding:5px 8px;font-size:12px}.fxbox{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px;margin:0 0 14px;font-size:13px;color:#344054}.fxbox b{color:var(--blue)}@media(max-width:720px){header{padding:22px 12px}header h1{font-size:21px}.wrap{padding:12px}.grid{display:block}.card{margin-bottom:12px;padding:12px}table,thead,tbody,tr,th,td{display:block}thead{display:none}tr{padding:10px 0;border-top:1px solid var(--line)}td{border:0;padding:4px 0}td::before{content:attr(data-label);display:block;font-size:11px;color:#667085;text-transform:uppercase;letter-spacing:.03em}.usd{font-size:16px}}'''
html=['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Property Listing Appendix — USD Prices</title><style>'+css+'</style></head><body>']
html.append('<header><div class="wrap"><h1>Representative Real Listings Appendix — USD Prices</h1><p>Three listing snapshots per destination to show what the property stock actually looks like.</p><p class="mini">All headline prices are converted to USD. Original local listing price is shown below the USD figure for auditability.</p></div></header>')
html.append('<div class="wrap"><div class="fxbox"><b>Conversion basis:</b> '+escape(fx_line)+'</div><div class="controls"><input id="q" placeholder="Search destination, source, property type..."><select id="sort"><option value="order">Original order</option><option value="cheap">Lowest median USD/m² first</option><option value="expensive">Highest median USD/m² first</option><option value="lowprice">Lowest median USD price first</option><option value="highprice">Highest median USD price first</option></select></div><div class="grid" id="grid">')
order=list(by.keys())
for dest in order:
    items=by[dest]
    vals=[r['usd_m2'] for r in items if r['usd_m2']]
    prices=[r['usd'] for r in items if r['usd']]
    med_m2=sorted(vals)[len(vals)//2] if vals else None
    med_price=sorted(prices)[len(prices)//2] if prices else None
    html.append(f'<section class="card" data-dest="{escape(dest).lower()}" data-med="{med_m2 or 0}" data-price="{med_price or 0}"><h2>{escape(dest)}</h2><div class="stat"><span class="pill">3 examples</span><span class="pill">Median sample price: {usd_price(med_price)}</span><span class="pill">Median sample: {usd_m2(med_m2)}</span></div><table><thead><tr><th>Type / listing</th><th>USD price</th><th>Size</th><th>USD/m²</th><th>Source</th><th>Read</th></tr></thead><tbody>')
    for r in items:
        html.append('<tr>'+''.join([
            f'<td data-label="Listing"><b>{escape(r["ptype"])}</b><br>{escape(r["name"])}</td>',
            f'<td data-label="USD price"><div class="usd">{usd_price(r["usd"])}</div><div class="local">Original: {escape(local_price(r))}</div></td>',
            f'<td data-label="Size">{m2fmt(r["size"])}</td>',
            f'<td data-label="USD/m²"><div class="usd">{usd_m2(r["usd_m2"])}</div></td>',
            f'<td data-label="Source"><a href="{escape(r["url"])}" target="_blank">{escape(r["source"])}</a></td>',
            f'<td data-label="Read" class="note">{escape(r["note"])}</td>'
        ])+'</tr>')
    html.append('</tbody></table></section>')
html.append('</div></div><script>const q=document.getElementById("q"),sort=document.getElementById("sort"),grid=document.getElementById("grid"),orig=[...grid.children];function apply(){let cards=[...grid.children];let query=q.value.toLowerCase();cards.forEach(c=>c.style.display=c.textContent.toLowerCase().includes(query)?"":"none");let vis=cards.filter(c=>c.style.display!=="none");if(sort.value==="cheap")vis.sort((a,b)=>+a.dataset.med-+b.dataset.med);if(sort.value==="expensive")vis.sort((a,b)=>+b.dataset.med-+a.dataset.med);if(sort.value==="lowprice")vis.sort((a,b)=>+a.dataset.price-+b.dataset.price);if(sort.value==="highprice")vis.sort((a,b)=>+b.dataset.price-+a.dataset.price);if(sort.value==="order")vis.sort((a,b)=>orig.indexOf(a)-orig.indexOf(b));vis.forEach(c=>grid.appendChild(c));}q.oninput=apply;sort.onchange=apply;</script></body></html>')
out='/mnt/data/property_destination_real_listings_appendix_usd.html'
Path(out).write_text('\n'.join(html), encoding='utf-8')
print(out, len(rows), 'rows', len(by), 'destinations')
