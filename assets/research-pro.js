/* Streams Into Wealth Research Pro — additive, no API keys required */
(()=>{'use strict';
const $=(s,r=document)=>r.querySelector(s);
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=n=>Number.isFinite(n)?new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n):'—';
const number=n=>Number.isFinite(n)?new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(n):'—';
const key='siw-research-notes-v2';
const ticker=()=>new URLSearchParams(location.search).get('ticker')?.toUpperCase()||'NVDA';
const panel=()=>$('#pro-panel');
const n=(id)=>{let v=Number($('#'+id)?.value);return Number.isFinite(v)?v:NaN};
const stored=()=>{try{return JSON.parse(localStorage.getItem(key)||'{}')}catch{return {}}};
const save=o=>{try{localStorage.setItem(key,JSON.stringify(o));return true}catch{return false}};
function calculate(){
const f=n('pro-fcf'),growth=n('pro-growth')/100,discount=n('pro-discount')/100,terminal=n('pro-terminal')/100,shares=n('pro-shares'),debt=n('pro-debt'),cash=n('pro-cash'),years=5;
const out=$('#pro-dcf-output');if(!out)return;
if(![f,growth,discount,terminal,shares,debt,cash].every(Number.isFinite)||shares<=0||discount<=terminal||discount<=-1||growth<=-1){out.textContent='Enter valid inputs. Shares must be positive and discount rate must exceed terminal growth.';return}
let pv=0,cf=f;for(let i=1;i<=years;i++){cf*=1+growth;pv+=cf/Math.pow(1+discount,i)}
let tv=cf*(1+terminal)/(discount-terminal);let equity=pv+tv/Math.pow(1+discount,years)-debt+cash;
out.innerHTML='<div class="pro-results"><div><small>Estimated equity value</small><strong>'+money(equity*1e9)+'</strong></div><div><small>Illustrative value per share</small><strong>'+money(equity/shares)+'</strong></div></div><p class="pro-small">All financial inputs are in billions of USD; shares outstanding in billions. Five-year simplified free-cash-flow DCF. This is a scenario, not a price target. Verify debt, cash, dilution, and forecasts.</p>';
}
async function compare(){
const input=$('#pro-compare-input'),out=$('#pro-compare-results');if(!out)return;
let names=[...new Set(input.value.toUpperCase().split(/[\s,;]+/).map(s=>s.trim()).filter(s=>/^[A-Z0-9.-]{1,12}$/.test(s)))].slice(0,5);
if(!names.length){out.textContent='Enter one to five tickers.';return}
out.textContent='Loading available SEC snapshots…';
const rows=await Promise.all(names.map(async t=>{try{let res=await fetch('data/stocks/'+encodeURIComponent(t)+'.json',{cache:'no-store'});if(!res.ok)throw Error();return {ticker:t,data:await res.json()}}catch{return {ticker:t,data:null}}}));
const fields=[['Revenue','Revenue'],['NetIncome','Net income'],['Assets','Assets'],['Liabilities','Liabilities'],['OperatingCashFlow','Operating cash flow']];
out.innerHTML='<div class="tablewrap"><table><thead><tr><th>Metric</th>'+rows.map(r=>'<th>'+safe(r.ticker)+'</th>').join('')+'</tr></thead><tbody>'+fields.map(([k,label])=>'<tr><td>'+label+'</td>'+rows.map(r=>{let d=r.data?.financials?.[k];return '<td title="'+safe(d?.end?'Period end: '+d.end:'Snapshot unavailable')+'">'+(d?money(Number(d.value)):'Not available')+'</td>'}).join('')+'</tr>').join('')+'</tbody></table></div><p class="pro-small">SEC company facts are reported figures, not live quotes. Periods may differ across companies; hover values for period ends. Missing data is never estimated.</p>';
}
function exportNotes(){const t=ticker(),d=stored()[t]||{};const lines=[['Ticker','Thesis','Risks','Catalysts','Updated'],[t,d.thesis||'',d.risks||'',d.catalysts||'',d.updated||'']];const csv=lines.map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.download=t+'-research-notes.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
function render(){
const root=panel();if(!root)return;const t=ticker(),notes=stored()[t]||{};
root.innerHTML='<div class="pro-heading"><div><div class="eyebrow">Research Pro · v2</div><h2>Build your investment thesis</h2><p class="muted">Compare verified SEC snapshots, model scenarios, and save your own research. No paid account required.</p></div><span class="pill">Research tools</span></div>'+
'<div class="pro-grid"><section class="card"><h3>Compare up to five stocks</h3><label class="pro-label" for="pro-compare-input">Tickers separated by commas</label><input id="pro-compare-input" class="field" value="'+safe(t)+',GOOGL,MSFT" maxlength="100" placeholder="NVDA, GOOGL, MSFT"><button id="pro-compare" class="button">Compare reported financials</button><div id="pro-compare-results" aria-live="polite"></div></section>'+
'<section class="card"><h3>Intrinsic value scenario</h3><p class="pro-small">Enter your assumptions. Values are not populated from an unverified quote feed.</p><div class="pro-fields">'+[['pro-fcf','Starting annual FCF ($B)',10],['pro-growth','Annual FCF growth (%)',8],['pro-discount','Discount rate (%)',10],['pro-terminal','Terminal growth (%)',2.5],['pro-shares','Shares outstanding (B)',1],['pro-debt','Total debt ($B)',0],['pro-cash','Cash ($B)',0]].map(([id,label,v])=>'<label>'+label+'<input id="'+id+'" type="number" step="any" value="'+v+'"></label>').join('')+'</div><div id="pro-dcf-output" aria-live="polite"></div></section></div>'+
'<section class="card pro-notes"><div class="pro-heading"><div><h3>My research journal · '+safe(t)+'</h3><p class="pro-small">Saved in this browser only. Export a CSV to keep a backup.</p></div><div class="pro-actions"><button class="button alt" id="pro-export">Export CSV</button><button class="button" id="pro-save">Save notes</button></div></div><div class="pro-grid">'+[['thesis','Investment thesis'],['risks','Risks and invalidation'],['catalysts','Upcoming catalysts']].map(([id,label])=>'<label class="pro-label">'+label+'<textarea id="pro-'+id+'" rows="4" maxlength="4000" placeholder="Write your own analysis…">'+safe(notes[id]||'')+'</textarea></label>').join('')+'</div><p class="pro-small" id="pro-note-status" aria-live="polite">'+(notes.updated?'Last saved: '+safe(notes.updated):'No notes saved for this ticker.')+'</p></section>';
$('#pro-compare').addEventListener('click',compare);$('#pro-save').addEventListener('click',()=>{let all=stored();all[t]={thesis:$('#pro-thesis').value,risks:$('#pro-risks').value,catalysts:$('#pro-catalysts').value,updated:new Date().toISOString()};$('#pro-note-status').textContent=save(all)?'Saved locally: '+all[t].updated:'Browser storage unavailable. Export your notes instead.'});$('#pro-export').addEventListener('click',exportNotes);
root.querySelectorAll('.pro-fields input').forEach(el=>el.addEventListener('input',calculate));calculate();
}
function init(){if(document.body.dataset.page!=='research')return;let host=$('#page');if(!host)return;let root=document.createElement('section');root.id='pro-panel';root.className='section';host.after(root);render()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();