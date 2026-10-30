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
