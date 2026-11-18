// 보람상조피플 상담폼 → 구글 앱스스크립트 → 텔레그램
// 봇 토큰은 앱스스크립트에만 있다. 이 파일엔 절대 넣지 않는다(공개 파일).
window.TG = {
  relay: "https://script.google.com/macros/s/AKfycbw0JSTa9jIlbXOcCOSBpz0nLMMAcb-5_vas_Flbu1kb2SA0FzTjWLPyDO5ytSI-3gan/exec"
};

// 방문 기록(부정클릭 확인) — 같은 앱스스크립트 주소
window.VISITLOG = "https://script.google.com/macros/s/AKfycbw0JSTa9jIlbXOcCOSBpz0nLMMAcb-5_vas_Flbu1kb2SA0FzTjWLPyDO5ytSI-3gan/exec";

// 상담 버튼 클릭 기록 (10-28 대표님 "사람을 더 끌어오게" — 클릭 뒤 측정). IP 없이 페이지·유입만.
// 같은 방문기록 시트에 page = "클릭:<버튼> <경로>" 로 쌓인다. 분석은 scripts/ads/visit_log.py
(function(){
  var u=window.VISITLOG; if(!u || /^\/(bohum|boram22)\//.test(location.pathname)) return;  // 보험·boram22는 처리방침에 없어 제외
  function src(){ try{ return sessionStorage.getItem("src")||""; }catch(e){ return ""; } }
  function log(what){
    var body=JSON.stringify({site:location.host, page:("클릭:"+what+" "+location.pathname).slice(0,120),
      q:("유입="+src()+" "+location.search).slice(0,400), ref:(document.referrer||"").slice(0,300), ad:0, ip:"",
      ua:navigator.userAgent.slice(0,200)});
    try{ if(navigator.sendBeacon && navigator.sendBeacon(u,new Blob([body],{type:"text/plain"}))) return; }catch(e){}
    try{ fetch(u,{method:"POST",mode:"no-cors",keepalive:true,headers:{"Content-Type":"text/plain"},body:body}); }catch(e){}
  }
  document.addEventListener("click",function(e){
    var a=e.target.closest&&e.target.closest("a,button"); if(!a) return;
    var h=a.getAttribute("href")||"", t=(a.textContent||"").replace(/\s+/g," ").trim().slice(0,20);
    if(/kakao/i.test(h)) log("카톡");
    else if(/^tel:/i.test(h)) log("전화");
    // 10-30: <button> 기본 type이 submit이라 '냉장가전'·'2구좌'·'더 보기' 탭까지 신청으로 잡히던 것 — 폼 안 버튼만
    else if((a.type==="submit"&&a.form)||/^ap(Send|Next)$|^goApply$/.test(a.id)||/상담 신청|신청하기|번호 남기기/.test(t)) log("신청 "+t);
  },true);
  // 10-30 대표님 "왜 접수 안 했는지" — 폼 제출 시도와 막힌 이유(번호·동의)를 남긴다. 번호 자체는 안 남긴다.
  document.addEventListener("submit",function(e){
    var f=e.target, p=f.elements&&f.elements["phone"], g=f.elements&&f.elements["agree"];
    var d=p?(p.value||"").replace(/[^0-9]/g,""):"";
    var why=!p?"번호칸없음":(d.length<10||d.length>11)?"번호오류("+d.length+"자리)":(g&&!g.checked)?"동의안함":"통과";
    log("제출 "+why);
  },true);
})();

/* 즐겨찾기 안내 (11-18 대표님) — 같은 브라우저로 광고 타고 3번째 들어오면 "즐겨찾기 해두고 바로 들어오세요" 안내.
 * 상담 버튼(아래 고정 바)을 가리지 않게 화면 위쪽에 띄운다. 하루 1번만, 닫기 가능. 저장은 이 브라우저 localStorage만. */
(function () {
  try {
    var q = location.search, ref = document.referrer || "";
    var ad = /NaPm=|n_media=|n_query=|n_keyword=/.test(q) || /adcr\.naver|ad\.search\.naver/.test(ref);
    if (!ad) return;
    var ls = window.localStorage, n = (parseInt(ls.getItem("fav_adn") || "0", 10) || 0) + 1;
    ls.setItem("fav_adn", String(n));
    var today = new Date().toISOString().slice(0, 10);
    if (n < 3 || ls.getItem("fav_day") === today) return;
    ls.setItem("fav_day", today);
    var show = function () {
      var b = document.createElement("div");
      b.setAttribute("role", "status");
      b.style.cssText = "position:fixed;left:50%;top:12px;transform:translateX(-50%);z-index:2147483000;max-width:calc(100% - 32px);" +
        "box-sizing:border-box;background:#fff;color:#222;border:1px solid #d9dde3;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,.12);" +
        "padding:10px 40px 10px 14px;font:14px/1.45 -apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;";
      b.textContent = "자주 찾아주셔서 감사해요 😊 즐겨찾기(★) 해두시면 다음엔 검색 없이 바로 들어오실 수 있어요.";
      var x = document.createElement("button");
      x.type = "button"; x.setAttribute("aria-label", "닫기"); x.textContent = "×";
      x.style.cssText = "position:absolute;right:6px;top:50%;transform:translateY(-50%);border:0;background:none;font-size:20px;color:#888;padding:4px 8px;cursor:pointer;";
      x.onclick = function () { b.remove(); };
      b.appendChild(x);
      document.body.appendChild(b);
      setTimeout(function () { if (b.parentNode) b.remove(); }, 12000);
    };
    if (document.body) show(); else document.addEventListener("DOMContentLoaded", show);
  } catch (e) {}
})();
