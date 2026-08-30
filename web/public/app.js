const $=s=>document.querySelector(s);
let evidence=[], institutions=[];
const techLabel={llm:'LLM',agent:'Agent',rag:'RAG',mcp:'MCP',copilot:'Copilot',model_name:'Model'};

async function load(){
  const [manifest, inst, idx] = await Promise.all([
    fetch('/data/manifest.json').then(r=>r.json()),
    fetch('/data/institutions.json').then(r=>r.json()),
    fetch('/data/search-index.json').then(r=>r.json())
  ]);
  evidence=idx; institutions=inst;
  $('#stats').innerHTML=[
    ['机构',manifest.institution_count],['报告',manifest.report_count],['证据',manifest.evidence_count]
  ].map(([k,v])=>`<div class="stat"><b>${v}</b><span>${k}</span></div>`).join('');
  $('#institution').insertAdjacentHTML('beforeend',institutions.map(x=>`<option value="${esc(x.institution_id)}">${esc(x.name)}${x.ticker?' · '+esc(x.ticker):''}</option>`).join(''));
  render();
}
function esc(v=''){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function render(){
  const iid=$('#institution').value, tech=$('#technology').value, q=$('#query').value.trim().toLowerCase();
  const rows=evidence.filter(x=>{
    if(iid && x.institution_id!==iid)return false;
    if(tech && !(x.technology_groups||[]).includes(tech))return false;
    if(q){const hay=[x.institution_name,x.ticker,x.section_title,x.text,...(x.technology_groups||[]),...(x.deployment_hits||[]),...(x.finance_hits||[])].join(' ').toLowerCase(); if(!hay.includes(q))return false;}
    return true;
  }).sort((a,b)=>(b.score||0)-(a.score||0)||a.institution_name.localeCompare(b.institution_name,'zh-CN')||a.page_no-b.page_no);
  $('#result-count').textContent=`${rows.length} 条`;
  $('#results').innerHTML=rows.length?rows.map(card).join(''):'<div class="empty">没有符合当前筛选条件的证据。</div>';
}
function card(x){
  const badges=(x.technology_groups||[]).map(t=>`<span class="badge">${esc(techLabel[t]||t)}</span>`).join('');
  return `<article class="card">
    <div class="card-top"><div><div class="institution-name">${esc(x.institution_name)}</div><div class="meta">${esc(x.ticker||'')} · PDF 第 ${x.page_no} 页</div></div><div class="score">证据评分 ${x.score==null?'—':Number(x.score).toFixed(2)}</div></div>
    <div class="badges">${badges}</div>
    <div class="quote">${esc(x.text)}</div>
    ${x.section_title?`<div class="section">解析章节：${esc(x.section_title)}</div>`:''}
    <div style="margin-top:12px"><a href="${esc(x.source_url)}" target="_blank" rel="noopener noreferrer">查看原始报告 ↗</a></div>
  </article>`;
}
['institution','technology'].forEach(id=>$('#'+id).addEventListener('change',render));
$('#query').addEventListener('input',render);
$('#reset').addEventListener('click',()=>{$('#institution').value='';$('#technology').value='';$('#query').value='';render();});
load().catch(err=>{$('#results').innerHTML=`<div class="empty">数据加载失败：${esc(err.message)}</div>`;console.error(err);});
