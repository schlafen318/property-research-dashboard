from math import isnan
from html import escape
FX={'JPY':1/161.305,'EUR':1.14784,'CAD':0.70609,'NZD':0.57370,'CHF':1.24288,'THB':0.0303905,'IDR':0.000056243,'VND':0.0000380084,'USD':1}
# url refs are public listing/portal pages gathered in research
rows=[]
def add(dest,ptype,name,price,curr,size,source,url,note=''):
    usd=price*FX[curr] if price and curr in FX else None
    usd_m2=usd/size if usd and size else None
    rows.append(dict(dest=dest,ptype=ptype,name=name,price=price,curr=curr,size=size,usd=usd,usd_m2=usd_m2,source=source,url=url,note=note))
# Japan
add('Fukuoka / Itoshima','Holiday house','Shima Nogita 2SLDK holiday house',180000000,'JPY',291.28,'RealEstate.co.jp','https://realestate.co.jp/en/forsale/fukuoka/itoshima-shi','Large coastal holiday-house example; high-end for Itoshima.')
add('Fukuoka / Itoshima','House','Shima Keya 5LDK new house',34900000,'JPY',85.70,'RealEstate.co.jp','https://realestate.co.jp/en/forsale/fukuoka/itoshima-shi','Affordable new-build style detached home.')
add('Fukuoka / Itoshima','Apartment','Itoshima 2LDK apartment',20900000,'JPY',92.0,'Akiya Japan','https://www.akiyajapan.com/city/itoshima','Lower-cost local-living example; verify current status.')
add('Hakone / Izu','House','Izu house, 116.76 m²',7800000,'JPY',116.76,'Akiya Japan','https://www.akiyajapan.com/city/izu-7','Very low-entry older-stock example; renovation risk likely.')
add('Hakone / Izu','Apartment','Izu apartment, 89.42 m²',3430000,'JPY',89.42,'Akiya Japan','https://www.akiyajapan.com/city/izu-7','Illustrates how cheap non-prime Izu stock can be.')
add('Hakone / Izu','House','Izu house, 142.31 m²',8990000,'JPY',142.31,'Akiya Japan','https://www.akiyajapan.com/city/izu-7','Older-stock value example; inspect condition carefully.')
add('Hakuba','Luxury house','Hakuba 5-bed / 5-bath house',1814372,'USD',293.1,'JamesEdition','https://www.jamesedition.com/real_estate/hakuba-japan','Prime/luxury western-buyer chalet benchmark.')
add('Hakuba','House','Hakuba 4-bed house',1251291,'USD',199.7,'JamesEdition','https://www.jamesedition.com/real_estate/hakuba-japan','Mid-luxury chalet example.')
add('Hakuba','Hotel / ryokan','Hokujo hotel / ryokan',250000000,'JPY',512.52,'RealEstate.co.jp','https://realestate.co.jp/en/forsale?prefecture=JP-20&station=1140930&trainline=11409','Operating-property example rather than pure second home.')
add('Niseko','Condo','Youtei Tracks 206, Upper Hirafu',90000000,'JPY',83.96,'Niseko Real Estate','https://nisekorealestate.com/properties/upper-hirafu','Entry/mid Hirafu condo example.')
add('Niseko','Ski-in/out condo','Aya Niseko 207, 2-bed',185000000,'JPY',85.9,'Niseko Real Estate','https://nisekorealestate.com/properties/upper-hirafu','Prime ski-in/ski-out condo example.')
add('Niseko','House / chalet','Kita House, Kutchan',60000000,'JPY',102.22,'Niseko Realty','https://www.nisekorealty.com/property-search?type=Land','Local-house/chalet example outside core Hirafu pricing.')
# Europe/Portugal/Spain/Italy/France/Austria/Switzerland
add('Valencia','Apartment','Valencia City 5-bed buy-to-let apartment',225000,'EUR',67,'HomeEspaña','https://www.homeespana.com/property-for-sale/valencia/','Low-ticket city buy-to-let example.')
add('Valencia','Villa','Alzira 5-bed villa',399000,'EUR',185,'HomeEspaña','https://www.homeespana.com/property-for-sale/valencia/','Inland/suburban villa showing value outside city core.')
add('Valencia','Villa','Torrent 3-bed detached villa',420000,'EUR',174,'HomeEspaña','https://www.homeespana.com/property-for-sale/valencia/','Detached family villa example near Valencia.')
add('Algarve / Cascais','Villa','Algarve T5 villa near Alvor',915000,'EUR',410,'Idealista','https://www.idealista.pt/en/geo/comprar-casas/algarve/','Large Algarve villa with pool/annex; yield depends on licence/operator.')
add('Algarve / Cascais','Villa','Cascais centre 4-bed villa',2900000,'EUR',298,'Idealista','https://www.idealista.pt/en/comprar-casas/cascais-e-estoril/cascais/','Prime Cascais is a very different price regime from Algarve.')
add('Algarve / Cascais','Apartment','Cascais Rosário T3 apartment',990000,'EUR',123,'Idealista','https://www.idealista.pt/en/comprar-casas/cascais-e-estoril/cascais/','High-quality apartment example; liquidity better than yield.')
add('Málaga / Costa del Sol','Apartment','Manilva 2-bed apartment',265000,'EUR',87.08,'Spain-Real.Estate','https://spain-real.estate/','Lower-cost Costa del Sol apartment example.')
add('Málaga / Costa del Sol','Semi-detached villa','Estepona Serene Atalaya villas from',600000,'EUR',124,'Cadena SER / Metrovacesa','https://cadenaser.com/andalucia/2026/01/27/metrovacesa-vende-una-promocion-de-50-villas-pareadas-en-estepona-ser-malaga/','New-build villa development example; many units sold.')
add('Málaga / Costa del Sol','Ultra-luxury villa','Villa Orquídea, Benahavís',19800000,'EUR',1696,'El País','https://elpais.com/economia/negocios/2026-05-01/las-tres-casas-de-la-semana-el-super-lujo-de-la-costa-del-sol-cuesta-20-millones-de-euros.html','Shows top-end price ceiling; not a yield asset.')
add('Lake Como','Villa','Pianello del Lario detached villa',495000,'EUR',141,'Idealista','https://www.idealista.it/en/geo/vendita-case/lago-di-como/','Relatively accessible lake-view villa example.')
add('Lake Como','Villa','Blevio 6-bed villa',4100000,'EUR',503,'Gate-away','https://www.gate-away.com/properties/lake-como','Prime luxury Lake Como villa example.')
add('Lake Como','Apartment','Menaggio 3-room apartment',520000,'EUR',70,'Lake Como Properties','https://lake-como-properties.com/','Town/lake-access apartment example.')
add('Madeira','Villa','Funchal 3-bed sea-view villa',700000,'EUR',255.2,'Mer et Demeures','https://www.meretdemeures.com/en/property/europe/portugal/madeira/sea%2Bview-property-for%2Bsale-funchal/','Good representative sea-view villa.')
add('Madeira','Apartment','Câmara de Lobos 2-bed apartment',505000,'EUR',131,'realestate.com.au International','https://www.realestate.com.au/international/pt/madeira/','Modern apartment example; check exact fees and tenure.')
add('Madeira','Luxury villa','Funchal modern pool villa',1400000,'EUR',243,'Le Figaro Properties','https://properties.lefigaro.com/announces/luxury-real%2Bestate-madeira-portugal/','Luxury Funchal villa price band; source gives USD headline and area.')
add('Costa Brava / Girona','Villa','S’Agaró 4-bed villa',1570000,'EUR',359,'Lucas Fox','https://www.lucasfox.com/property/spain/costa-brava/s-agaro.html','High-quality Costa Brava villa example.')
add('Costa Brava / Girona','Villa','Begur Sa Riera new-build villa',2200000,'EUR',260,'Costa Brava House','https://www.costabravahouse.com/en/buy-house-costa-brava','Sea-view villa with tourist-location appeal.')
add('Costa Brava / Girona','Country house','Forallac / Baix Empordà country house',1591780,'USD',900,'JamesEdition','https://www.jamesedition.com/real_estate/forallac-spain','Rural-luxury alternative to beachfront villas.')
add('Crete','Village house','Stylos / Apokoronas 2-bed village house',132000,'EUR',81.5,'Crete Island Real Estate','https://crete-island.net/','Low-entry authentic village-house example.')
add('Crete','Villa project','Agios Onoufrios modern villa',1470000,'EUR',250,'Crete Island Real Estate','https://crete-island.net/','Sea-view luxury villa development example.')
add('Crete','Hotel','Kato Gouves hotel',2200000,'EUR',970,'A Place in the Sun','https://www.aplaceinthesun.com/property/greece/crete','Operating/hospitality property example.')
add('Annecy','Apartment','Annecy new-build 3-bed apartment',428000,'EUR',80,'French-Property.com','https://www.french-property.com/properties-for-sale?location=annecy%2Chaute-savoie','City/lake access apartment; size estimated from property type if exact not shown.')
add('Annecy','House','Annecy-le-Vieux 4-bed house',749000,'EUR',188,'realestate.com.au International','https://www.realestate.com.au/international/fr/annecy-le-vieux-rhone/','Family-house example below prime lakefront pricing.')
add('Annecy','Lake-area house','Veyrier-du-Lac / Lake Annecy house',1890000,'EUR',223,'Prestige Property','https://www.prestigeproperty.co.uk/lake-annecy-property-137/','Premium lake-adjacent house example.')
add('Mallorca','Apartment benchmark','Mallorca apartment benchmark',1026957,'EUR',205,'Charlesdel / market listing sample','https://charlesdel.com/spain/mallorca/property-for-sale/','Average apartment listing price; not a single unit.')
add('Mallorca','Villa / house benchmark','Mallorca house/villa benchmark',2684381,'EUR',537,'Charlesdel / market listing sample','https://charlesdel.com/spain/mallorca/property-for-sale/','Average villa/house listing price; wide dispersion by location.')
add('Mallorca','Luxury villa','Santa Ponça Villa Goya',25000000,'EUR',900,'El País','https://elpais.com/economia/negocios/2026-02-06/las-tres-casas-de-la-semana-lujo-en-venta-en-mallorca-por-25-millones-de-euros.html','Top-end luxury example; build size approximate from public description.')
add('Croatia / Istria-Dalmatia','Villa','Trogir/Ciovo sea-view villa',475000,'EUR',180,'Croatia Property Sales','https://www.croatiapropertysales.com/property-for-sale-dalmatia/','Good mid-market Dalmatian villa example.')
add('Croatia / Istria-Dalmatia','Apartment','Čiovo duplex apartment',295000,'EUR',84,'Croatia Property Sales','https://www.croatiapropertysales.com/property-for-sale-dalmatia/','Lower-ticket coastal apartment example.')
add('Croatia / Istria-Dalmatia','Waterfront villa','Zadar beachfront villa',3250000,'EUR',310,'Croatia Property Sales','https://www.croatiapropertysales.com/property-for-sale-dalmatia/','Prime waterfront villa; closer to trophy/liquidity test.')
add('Dolomites / South Tyrol','Apartment','Valdaora / Kronplatz 1-bed apartment',428000,'EUR',50,'Overseas Residence','https://overseasresidence.com/properties-dolomites/','Freehold apartment in ski area; compact but expensive per m².')
add('Dolomites / South Tyrol','Apartment','Valdaora / Kronplatz 2-bed apartment',598000,'EUR',72,'Overseas Residence','https://overseasresidence.com/properties-dolomites/','Ski-area apartment benchmark.')
add('Dolomites / South Tyrol','Chalet','Chalet Piccolino, Dolomites',1450000,'EUR',180,'Country Life / Savills','https://www.countrylife.co.uk/property/international-property-guides/the-dream-ski-chalet-for-sale-plan-world-domination-and-ski-japow-at-the-same-time','Curated chalet example; size approximate if not listed in snippet.')
add('Bali','Leasehold villa','Bingin / Uluwatu 3-bed rooftop BBQ villa',8820000000,'IDR',280,'The Bali Homes','https://www.thebalihomes.com/properties','Leasehold, ready villa example.')
add('Bali','Freehold villa','Berawa / Canggu 5-bed freehold villa',14000000000,'IDR',254,'The Bali Homes','https://www.thebalihomes.com/properties','Rare freehold-style higher-price example; legal structuring crucial.')
add('Bali','Leasehold villa','Balangan 3-bed modern villa',4370000000,'IDR',156,'FazWaz Indonesia','https://www.fazwaz.id/property-for-sale/indonesia/bali','28-year lease example; terminal value matters.')
add('Chamonix','Apartment','Chamonix garden-level 159 m² apartment',1500000,'EUR',159,'SeeChamonix','https://www.seechamonix.com/property-for-sale/','High-quality apartment in core Chamonix.')
add('Chamonix','Apartment / penthouse','Argentière penthouse',1500000,'EUR',145.3,'Savills','https://search.savills.com/list/property-for-sale/54237%2C47320','Mont Blanc-view penthouse benchmark.')
add('Chamonix','Chalet','Chalet Mica, Chamonix',2520000,'EUR',160,'Chamonix Sotheby’s','https://www.chamonixsothebysrealty.com/en/mountain-view/%26new_research%3D1','Prime chalet example; very expensive per m².')
add('Da Nang / Hoi An','Apartment','Hoa Hai 1-bed apartment',15000000,'VND',40,'FazWaz Vietnam','https://www.fazwaz.vn/property-for-sale/vietnam/da-nang','Extremely low snippet price looks anomalous; verify before relying.')
add('Da Nang / Hoi An','Condo median','Da Nang condo median listing',3894000000,'VND',58.5,'DotProperty Vietnam','https://www.dotproperty.com.vn/en/properties-for-sale/%C4%91%C3%A0-n%E1%BA%B5ng','Uses median price and median VND/m² to infer size.')
add('Da Nang / Hoi An','Apartment benchmark','70 m² Vietnam big-city apartment',3500000000,'VND',70,'Global Property Guide','https://www.globalpropertyguide.com/asia/vietnam/price-history','Market benchmark rather than destination-specific listing.')
add('Queenstown','Apartment','Sawmill Road 2-bed apartment from',780000,'NZD',75,'Ray White Queenstown','https://rwqueenstown.co.nz/properties/for-sale?category=&suburbPostCode=','Entry apartment/new-development example; size estimated.')
add('Queenstown','Apartment','Queenstown apartment, Frankton',990000,'NZD',90,'realestate.co.nz','https://www.realestate.co.nz/residential/sale/central-otago-lakes-district/queenstown/apartment','Frankton apartment example; exact size not exposed in snippet.')
add('Queenstown','Luxury / development','Queenstown Hill development/home opportunity',2500000,'NZD',250,'Le Figaro Properties','https://properties.lefigaro.com/announces/luxury-real%2Bestate-otago-new%2Bzealand/?ville=queenstown','Representative higher-end Queenstown Hill opportunity; verify details.')
add('Phuket / Koh Samui','Condo','Rawai condo from',107000,'USD',44,'Tranio','https://tranio.com/articles/phuket-property-prices/','Small Phuket condo entry example.')
add('Phuket / Koh Samui','Villa','Rawai / Phuket villa from',479000,'USD',440,'Tranio','https://tranio.com/articles/phuket-property-prices/','Large villa benchmark, likely outside prime west-coast pricing.')
add('Phuket / Koh Samui','Villa','Maret, Koh Samui 4-bed pool villa',16900000,'THB',220,'FazWaz Thailand','https://www.fazwaz.com/property-for-sale/thailand/surat-thani/koh-samui','Samui villa example; land/title structure to verify.')
add('Whistler','House','Emerald Drive 3-bed house',1999000,'CAD',146.5,'Zillow','https://www.zillow.com/whistler-bc/','Lower-end detached-house example by Whistler standards.')
add('Whistler','Townhouse','Eagle Drive 2-bed townhouse',1699000,'CAD',110.7,'Zillow','https://www.zillow.com/whistler-bc/','Townhouse example; liquidity may be better than chalets.')
add('Whistler','Luxury condo','Tapley Place 5-bed condo',14995000,'CAD',464.1,'Zillow','https://www.zillow.com/whistler-bc/','Trophy segment; yield likely weak.')
add('Innsbruck / Tyrol','Apartment','Innsbruck 36 m² apartment',299000,'EUR',36,'realestate.com.au International','https://www.realestate.com.au/international/at/innsbruck-tyrol/','Compact urban alpine apartment.')
add('Innsbruck / Tyrol','Apartment','Innsbruck 68 m² apartment',319000,'EUR',68,'realestate.com.au International','https://www.realestate.com.au/international/at/innsbruck-tyrol/','Practical city apartment example.')
add('Innsbruck / Tyrol','Luxury chalet','Kitzbühel chalet',14900000,'EUR',240,'Muhr Immobilien','https://www.muhr-immobilien.com/en/properties/tyrol/','Top-end Tyrol trophy chalet; restrictive market.')
add('Andermatt','Condo','Andermatt 2-bed condo',3780706,'USD',149.0,'JamesEdition','https://www.jamesedition.com/real_estate/andermatt-switzerland','Foreign-buyer-friendly Swiss exception, but very expensive.')
add('Andermatt','Apartment','Andermatt 1-bed apartment',3395692,'USD',79.0,'JamesEdition','https://www.jamesedition.com/real_estate/andermatt-switzerland','Small luxury unit with very high USD/m².')
add('Andermatt','Market apartment benchmark','Andermatt median apartment',1439190,'CHF',88.0,'RealAdvisor','https://realadvisor.ch/en/property-prices/town-andermatt','Market benchmark from June 2026 pricing data.')
add('Ticino / Lake Lugano','Apartment','Lugano 50 m² apartment',400000,'CHF',50,'realestate.com.au International','https://www.realestate.com.au/international/ch/lugano-ticino/','Lower-ticket Lugano apartment example.')
add('Ticino / Lake Lugano','Luxury villa','Lugano lake/mountain-view house',5453678,'USD',771,'Le Figaro Properties','https://properties.lefigaro.com/announces/luxury-real%2Bestate-ticino-switzerland/?ville=lugano','Large luxury villa example.')
add('Ticino / Lake Lugano','Market benchmark','Lugano average luxury home',2569999,'USD',245,'JamesEdition','https://www.jamesedition.com/real_estate/lugano-switzerland','Luxury-market benchmark; exact unit not specified.')
add('Swiss Valais / Vaud Alps','Chalet','Villars-sur-Ollon Chalet Bayrou',5300000,'CHF',350,'Knight Frank','https://www.knightfrank.com/property-for-sale/switzerland/swiss-alps','Representative high-end Vaud alpine chalet; size estimated.')
add('Swiss Valais / Vaud Alps','Penthouse','Nendaz ski-in/ski-out penthouse',3500000,'CHF',209.96,'Savills','https://search.savills.com/list/property-for-sale/switzerland/swiss-alps','Prime Swiss alpine apartment example.')
add('Swiss Valais / Vaud Alps','Market benchmark','Verbier premium resort price/m² benchmark',22100,'CHF',1,'Capiwell / UBS summary','https://capiwell.ch/swiss-alps-winter-2025-2026-holiday-homes-soar-in-demand/','Per-m² benchmark, not a specific listing.')
# HTML
from collections import defaultdict
by=defaultdict(list)
for r in rows: by[r['dest']].append(r)

def money(r):
    if not r['price']: return 'POA'
    return f"{r['curr']} {r['price']:,.0f}"
def usdfmt(x): return '—' if x is None else ('$'+format(x/1e6,'.2f')+'m' if x>=1e6 else '$'+format(x/1000,'.0f')+'k')
def m2fmt(x): return '—' if x is None else f"{x:,.0f}"
css='''
:root{--bg:#f6f7fb;--card:#fff;--ink:#172033;--muted:#667085;--line:#e4e7ec;--blue:#0B2E6D;--gold:#B78300;--soft:#eef3fb}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}header{background:linear-gradient(135deg,#0B2E6D,#16498f);color:#fff;padding:28px 18px}header h1{margin:0 0 8px;font-size:26px}header p{margin:4px 0;color:#dbe6ff}.wrap{max-width:1180px;margin:auto;padding:18px}.controls{position:sticky;top:0;background:rgba(246,247,251,.96);backdrop-filter:blur(8px);padding:10px 0;z-index:5}.controls input,.controls select{width:100%;padding:12px;border:1px solid var(--line);border-radius:12px;margin:4px 0;font-size:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;box-shadow:0 2px 10px rgba(16,24,40,.04)}h2{font-size:20px;margin:0 0 8px;color:var(--blue)}.tag{display:inline-block;background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:4px 9px;font-size:12px;color:var(--blue);margin-bottom:8px}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:#475467;font-size:12px}a{color:var(--blue);word-break:break-word}.note{color:var(--muted);font-size:12px}.mini{font-size:12px;color:var(--muted)}.stat{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}.pill{background:#fff7e0;border:1px solid #ead393;color:#684c00;border-radius:10px;padding:5px 8px;font-size:12px}@media(max-width:720px){header h1{font-size:22px}.wrap{padding:12px}.grid{display:block}.card{margin-bottom:12px}table,thead,tbody,tr,th,td{display:block}thead{display:none}tr{padding:8px 0;border-top:1px solid var(--line)}td{border:0;padding:3px 0}td::before{content:attr(data-label);display:block;font-size:11px;color:#667085;text-transform:uppercase;letter-spacing:.03em}}'''
html=['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Property Listing Appendix</title><style>'+css+'</style></head><body>']
html.append('<header><div class="wrap"><h1>Representative Real Listings Appendix</h1><p>Three listing snapshots per destination to show what the property stock actually looks like.</p><p class="mini">FX used: JPY/USD 161.305, EUR/USD 1.14784, CAD/USD 0.70609, NZD/USD 0.57370, CHF/USD 1.24288, THB/USD 0.0303905, IDR/USD 0.000056243, VND/USD 0.0000380084. Listings change quickly; verify availability, fees, title and rental permission before underwriting.</p></div></header>')
html.append('<div class="wrap"><div class="controls"><input id="q" placeholder="Search destination, source, property type..."><select id="sort"><option value="order">Original order</option><option value="cheap">Lowest median USD/m² first</option><option value="expensive">Highest median USD/m² first</option></select></div><div class="grid" id="grid">')
order=list(by.keys())
for dest in order:
    items=by[dest]
    vals=[r['usd_m2'] for r in items if r['usd_m2']]
    med=sorted(vals)[len(vals)//2] if vals else None
    html.append(f'<section class="card" data-dest="{escape(dest).lower()}" data-med="{med or 0}"><h2>{escape(dest)}</h2><div class="stat"><span class="pill">3 examples</span><span class="pill">Median sample: {usdfmt(med)}/m²</span></div><table><thead><tr><th>Type / listing</th><th>Local price</th><th>Size</th><th>USD/m²</th><th>Source</th><th>Read</th></tr></thead><tbody>')
    for r in items:
        html.append('<tr>'+''.join([
            f'<td data-label="Listing"><b>{escape(r["ptype"])}</b><br>{escape(r["name"])}</td>',
            f'<td data-label="Local price">{money(r)}<br><span class="note">{usdfmt(r["usd"])}</span></td>',
            f'<td data-label="Size">{m2fmt(r["size"])} m²</td>',
            f'<td data-label="USD/m²">{usdfmt(r["usd_m2"])}</td>',
            f'<td data-label="Source"><a href="{escape(r["url"])}" target="_blank">{escape(r["source"])}</a></td>',
            f'<td data-label="Read" class="note">{escape(r["note"])}</td>'
        ])+'</tr>')
    html.append('</tbody></table></section>')
html.append('</div></div><script>const q=document.getElementById("q"),sort=document.getElementById("sort"),grid=document.getElementById("grid");function apply(){let cards=[...grid.children];let query=q.value.toLowerCase();cards.forEach(c=>c.style.display=c.textContent.toLowerCase().includes(query)?"":"none");let vis=cards.filter(c=>c.style.display!=="none");if(sort.value==="cheap")vis.sort((a,b)=>+a.dataset.med-+b.dataset.med);if(sort.value==="expensive")vis.sort((a,b)=>+b.dataset.med-+a.dataset.med);if(sort.value==="order")vis.sort((a,b)=>cards.indexOf(a)-cards.indexOf(b));vis.forEach(c=>grid.appendChild(c));}q.oninput=apply;sort.onchange=apply;</script></body></html>')
open('/mnt/data/property_destination_real_listings_appendix.html','w').write('\n'.join(html))
print(len(rows), 'rows', len(by),'destinations')
