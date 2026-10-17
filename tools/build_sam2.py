# /sam2/ = /sam/ 복제 + '골라서 공유' 기능 (상품 골라 고객에게 링크로 보내기)
# 사용: python3 tools/build_sam2.py   (/sam/ 을 고친 뒤 다시 실행하면 /sam2/ 에 반영)
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'sam/index.html'), encoding='utf-8').read()

def rep(s, old, new, count=1):
    assert s.count(old) >= 1, 'not found: ' + old[:60]
    return s.replace(old, new, count)

CSS = r"""
/* ---- sam2: 골라서 공유 ---- */
.pick-toggle{background:var(--tap);color:var(--tap-ink);border:0;border-radius:10px;padding:8px 14px;font:inherit;font-size:14px;font-weight:800;cursor:pointer;white-space:nowrap}
.pick-toggle.on{background:#fff;color:var(--nv)}
.pick-guide{background:var(--nv2);color:#fff;border-radius:12px;padding:12px 14px;margin:0 0 14px;font-size:14px;line-height:1.55}
.pick-guide b{color:var(--tap)}
.pick-fields{display:grid;grid-template-columns:1fr;gap:8px;margin-top:10px}
.pick-preview{margin-top:8px;font-size:13px;color:#c3cde0;line-height:1.5}
.pick-preview b{color:#fff}
.pick-fields input{width:100%;border:0;border-radius:8px;padding:10px 12px;font:inherit;font-size:14px;background:#fff;color:var(--ink)}
@media(max-width:720px){.pick-fields{grid-template-columns:1fr}}
.pcard{position:relative}
.pcard .pk{display:none}
body.picking .pcard .pk{display:flex;position:absolute;top:10px;right:10px;z-index:2;width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.95);border:2px solid #cbd5e1;align-items:center;justify-content:center;font-weight:800;color:transparent;font-size:15px}
body.picking .pcard.picked{box-shadow:0 0 0 3px var(--tap),0 4px 14px rgba(0,0,0,.18)}
body.picking .pcard.picked .pk{background:var(--tap);border-color:var(--tap);color:var(--tap-ink)}
body.picking .pcard .go{visibility:hidden}
.pickbar{position:fixed;left:0;right:0;bottom:0;z-index:90;background:var(--nv2);border-top:2px solid var(--tap);padding:10px 0 calc(10px + env(safe-area-inset-bottom,0px))}
.pickbar .wrap{display:flex;gap:8px;align-items:center}
.pickbar .pinfo{color:#fff;font-size:14px;flex:1;min-width:0}
.pickbar .pinfo b{color:var(--tap)}
.pickbar .pinfo a{color:#c3cde0;text-decoration:underline;cursor:pointer;margin-left:4px}
.pickbar button{border:0;border-radius:10px;padding:11px 14px;font:inherit;font-size:14px;font-weight:800;cursor:pointer;white-space:nowrap}
.pickbar .pb-all{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.4)}
.pickbar .pb-send{background:var(--tap);color:var(--tap-ink)}
.pickbar button:disabled{opacity:.45;cursor:default}
.pick-link{margin-top:10px;font-size:13px;color:#c3cde0;word-break:break-all}
.pick-head{background:#fff;border-radius:16px;padding:20px 20px 18px;margin:0 0 18px;box-shadow:0 4px 14px rgba(0,0,0,.18)}
.pick-head .ph-k{font-size:13px;font-weight:800;color:var(--sand)}
.pick-head h2{margin:4px 0 6px;font-size:clamp(20px,3vw,26px);font-weight:800;color:var(--nv);letter-spacing:-.02em}
.pick-head p{margin:0;color:var(--muted);font-size:14.5px;white-space:pre-line}
.pick-head .ph-all{display:inline-block;margin-top:12px;font-size:13.5px;font-weight:700;color:var(--nv);text-decoration:underline}
body.custom .sf,body.custom .sf-tags,body.custom .sf-bar .right,body.custom .sam-cos{display:none}
.ptoast{position:fixed;left:50%;bottom:150px;transform:translateX(-50%);background:rgba(0,0,0,.85);color:#fff;padding:10px 18px;border-radius:999px;font-size:14px;z-index:120;opacity:0;transition:opacity .2s;pointer-events:none;white-space:nowrap}
.ptoast.on{opacity:1}
"""

s = src
s = rep(s, '</style>', CSS + '</style>')
s = rep(s, '<meta name="viewport"', '<meta name="robots" content="noindex,nofollow">\n<meta name="viewport"')
s = rep(s, '    <div class="sf-bar">',
'''    <div class="pick-head" id="pickHead" hidden>
      <div class="ph-k">상담사가 골라드린 상품</div>
      <h2 id="phTitle"></h2>
      <p id="phMemo"></p>
      <a class="ph-all" href="./">전체 상품 보러가기 ›</a>
    </div>
    <div class="pick-guide" id="pickGuide" hidden>
      <b>골라서 공유</b> · 상품을 눌러 체크한 뒤 아래 <b>선택한 것 보내기</b>를 누르면, 고른 상품만 보이는 링크가 만들어져요.
      <div class="pick-fields">
        <input id="pkName" placeholder="고객 이름 (예: 홍길동)" aria-label="고객 이름" autocomplete="off">
      </div>
      <div class="pick-preview" id="pkPreview"></div>
      <div class="pick-link" id="pickLink" hidden></div>
    </div>
    <div class="sf-bar">''')
s = rep(s, '        <div class="sort" id="sort">',
        '        <button type="button" class="pick-toggle" id="pickToggle">골라서 공유</button>\n        <div class="sort" id="sort">')
s = rep(s, '<div class="leadbar">',
'''<div class="pickbar" id="pickbar" hidden><div class="wrap">
  <div class="pinfo">선택 <b id="pkCount">0</b>개<a id="pkClear">비우기</a></div>
  <button type="button" class="pb-all" id="pkAll">검색결과 전체</button>
  <button type="button" class="pb-send" id="pkSend" disabled>선택한 것 보내기</button>
</div></div>
<div class="ptoast" id="ptoast" role="status"></div>
<div class="leadbar">''')

# 고객 링크(?ids= / ?q=)와 고르기 모드
s = rep(s, 'let sel={co:[],cat:[],brand:[],gj:[],price:[]}, q="", sort="def", shown=0;',
'''let sel={co:[],cat:[],brand:[],gj:[],price:[]}, q="", sort="def", shown=0;
var UP=new URLSearchParams(location.search);
var IDS=UP.get("ids")?UP.get("ids").split(",").filter(Boolean):null;
var CUSTOM=!!(IDS||UP.get("q"));
var picking=false, picked=[];
if(UP.get("q")) q=UP.get("q").trim().toLowerCase();
if(UP.get("sort")) sort=UP.get("sort");''')
s = rep(s, '  if(q){ var hay=',
        '  if(IDS && IDS.indexOf(p.id)<0) return false;\n  if(q){ var hay=')
s = rep(s, '''  return '<a class="pcard" href="'+p.url+'">'
    +'<div class="imgbox">''',
'''  return '<a class="pcard'+(picked.indexOf(p.id)>=0?' picked':'')+'" data-id="'+p.id+'" href="'+p.url+'">'
    +'<span class="pk" aria-hidden="true">✓</span><div class="imgbox">''')
s = rep(s, '''  else if(sort==="high") cur=cur.slice().sort(function(a,b){return b.m-a.m;});''',
'''  else if(sort==="high") cur=cur.slice().sort(function(a,b){return b.m-a.m;});
  if(IDS && sort==="def") cur=cur.slice().sort(function(a,b){return IDS.indexOf(a.id)-IDS.indexOf(b.id);});''')

JS = r"""
(function(){
  var $=function(id){return document.getElementById(id);};
  var MEMO="가전결합 담당 김다혜입니다 😊\n모두 새 제품이고, 상품을 누르면 월 납입금·만기 환급 조건을 자세히 보실 수 있어요.\n마음에 드는 제품을 알려주시면 1:1로 꼼꼼하게 안내해 드릴게요!";
  function toast(t){var e=$("ptoast");e.textContent=t;e.classList.add("on");clearTimeout(toast.h);toast.h=setTimeout(function(){e.classList.remove("on");},2200);}
  // 고객이 받은 화면
  if(CUSTOM){
    document.body.classList.add("custom");
    var t=UP.get("t")||(UP.get("q")?"고객님께 추천드리는 "+UP.get("q"):"고객님께 추천드리는 상품");
    $("phTitle").textContent=t; $("phMemo").textContent=UP.get("memo")||MEMO;
    $("pickHead").hidden=false; document.title=t+" | 상조 가전결합 통합관";
    var names=cur.slice(0,10).map(function(p){return p.full;}).join(", ");
    if(names){ window.__PRODUCT__="[추천목록] "+names; }
    function go(){ window.scrollTo(0, $("pickHead").getBoundingClientRect().top + window.pageYOffset - 80); }
    setTimeout(go,0); window.addEventListener("load",go);
    return;
  }
  function what(){
    var v=$("q").value.trim(); if(v) return v;
    if(sel.cat.length===1) return sel.cat[0];
    if(sel.brand.length===1) return sel.brand[0]+" 가전";
    return "가전";
  }
  window.title=function(){
    var n=$("pkName").value.trim().replace(/\s*(고객)?님$/,"");
    return (n?n+" 고객님":"고객님")+"께 추천드리는 "+what();
  };
  function bar(){
    $("pkCount").textContent=picked.length; $("pkSend").disabled=!picked.length;
    $("pkClear").style.display=picked.length?"":"none";
  }
  function setPicking(on){
    picking=on; document.body.classList.toggle("picking",on);
    $("pickToggle").classList.toggle("on",on); $("pickToggle").textContent=on?"공유 끝내기":"골라서 공유";
    $("pickGuide").hidden=!on; $("pickbar").hidden=!on; bar();
  }
  $("pickToggle").addEventListener("click",function(){ setPicking(!picking); if(picking) $("catalog").scrollIntoView({behavior:"smooth"}); });
  grid.addEventListener("click",function(e){
    if(!picking) return;
    var a=e.target.closest(".pcard"); if(!a) return;
    e.preventDefault();
    var id=a.dataset.id, i=picked.indexOf(id);
    if(i<0) picked.push(id); else picked.splice(i,1);
    a.classList.toggle("picked",i<0); bar();
  });
  $("pkClear").addEventListener("click",function(){ picked=[]; paint(); bar(); });
  function link(all){
    var u=new URL(location.pathname,location.origin);
    if(all){ var qq=$("q").value.trim(); if(qq) u.searchParams.set("q",qq); if(sort!=="def") u.searchParams.set("sort",sort);
      if(!qq){ u.searchParams.set("ids",cur.map(function(p){return p.id;}).join(",")); } }
    else u.searchParams.set("ids",picked.join(","));
    u.searchParams.set("t",title());
    return u.toString();
  }
  function share(url){
    var box=$("pickLink"); box.hidden=false; box.textContent="✅ 「"+window.title()+"」 링크를 만들었어요. 카톡에 붙여넣어 보내세요!";
    var title=window.title();
    function copy(){
      var done=function(){toast("링크를 복사했어요. 카톡에 붙여넣어 보내세요");};
      if(navigator.clipboard&&window.isSecureContext){ navigator.clipboard.writeText(url).then(done,function(){fb();done();}); } else { fb(); done(); }
      function fb(){ var ta=document.createElement("textarea"); ta.value=url; ta.style.position="fixed"; ta.style.opacity="0"; document.body.appendChild(ta); ta.select(); try{document.execCommand("copy");}catch(e){} document.body.removeChild(ta); }
    }
    if(navigator.share) navigator.share({title:title,text:title,url:url}).catch(function(){}); else copy();
  }
  $("pkSend").addEventListener("click",function(){ if(picked.length) share(link(false)); });
  $("pkAll").addEventListener("click",function(){
    if(!cur.length){ toast("보낼 상품이 없어요"); return; }
    if(!$("q").value.trim() && cur.length===P.length){ toast("검색어나 필터로 상품을 먼저 좁혀 주세요"); return; }
    share(link(true));
  });
  function preview(){ $("pkPreview").innerHTML="제목: <b>"+esc(title())+"</b><br>안내: "+esc(MEMO.split("\n")[0]); }
  ["pkName","q"].forEach(function(id){ $(id).addEventListener("input",preview); });
  document.getElementById("sfRows").addEventListener("click",function(){ setTimeout(preview,0); });
  preview();
})();
"""
s = rep(s, 'render();\n</script>', 'render();\n' + JS + '</script>')
s = rep(s, '[통합관 /sam]', '[통합관 /sam2]')
s = rep(s, "gcount.innerHTML='전체 <b>'+cur.length+'</b>개';", "gcount.innerHTML=(CUSTOM?'추천 상품 ':'전체 ')+'<b>'+cur.length+'</b>개';")

# 상담사 전용 페이지라 상담 접수(폼·하단 바)는 뺌. 문의는 카카오톡으로
s, n1 = re.subn(r'<section class="consult" id="consult">.*?</section>\n', '', s, flags=re.S)
s, n2 = re.subn(r'<div class="leadbar">.*?</form>\s*</div>\s*</div>\n', '', s, flags=re.S)
assert n1 == 1 and n2 == 1, (n1, n2)
s = s.replace('href="#consult"', 'href="http://pf.kakao.com/_xowzxhX/chat" target="_blank" rel="noopener"').replace('>상담 신청</a></div>', '>카톡 상담</a></div>')
s = rep(s, 'body{margin:0;', 'body.custom,body:not(.picking){padding-bottom:20px!important}\nbody{margin:0;')

os.makedirs(os.path.join(ROOT, 'sam2'), exist_ok=True)
open(os.path.join(ROOT, 'sam2/index.html'), 'w', encoding='utf-8').write(s)
print('sam2/index.html', len(s))
