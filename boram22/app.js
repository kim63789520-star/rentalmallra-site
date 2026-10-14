(() => {
  'use strict';
  const form = document.getElementById('consultForm');
  const status = document.getElementById('formStatus');
  const submit = form.querySelector('[type=submit]');
  const preview = document.body.dataset.mode !== 'live';
  if (preview) document.getElementById('previewBanner').hidden = false;
  // The form already contains direct contact links; avoid covering inputs on mobile.
  const observer = new IntersectionObserver(entries => {
    document.body.classList.toggle('consult-in-view', entries[0].intersectionRatio >= 0.15);
  }, {threshold: [0, 0.15]});
  observer.observe(document.getElementById('consult'));
  let busy = false;
  let completed = false;
  const message = (text, error = false) => {
    status.textContent = text;
    status.classList.toggle('error', error);
  };
  document.querySelectorAll('[data-topic]').forEach(button => {
    button.addEventListener('click', () => {
      [...form.elements.topic].forEach(radio => { radio.checked = radio.value === button.dataset.topic; });
      document.getElementById('consult').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
      form.elements.phone.focus({preventScroll: true});
    });
  });
  form.elements.phone.addEventListener('input', () => {
    const digits = form.elements.phone.value.replace(/\D/g, '').slice(0, 11);
    form.elements.phone.value = digits.length > 7 ? digits.replace(/^(\d{3})(\d{3,4})(\d{4})$/, '$1-$2-$3') : digits;
    form.elements.phone.removeAttribute('aria-invalid');
  });
  // Only campaign metadata, not arbitrary URL parameters or contact details.
  const source = () => {
    const params = new URLSearchParams(location.search);
    return ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'n_keyword', 'n_query'].map(key => {
      const value = params.get(key);
      return value ? `${key}=${value.replace(/[\r\n]/g, ' ').slice(0, 120)}` : '';
    }).filter(Boolean).join(' / ') || '직접 또는 미확인';
  };
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || completed) return;
    const phone = form.elements.phone.value.replace(/\D/g, '');
    if (!/^010\d{8}$/.test(phone)) {
      message('010으로 시작하는 휴대폰번호 11자리를 확인해 주세요.', true);
      form.elements.phone.setAttribute('aria-invalid', 'true');
      form.elements.phone.focus();
      return;
    }
    if (!form.elements.agree.checked) {
      message('개인정보 수집·이용 내용을 확인하고 동의해 주세요.', true);
      form.elements.agree.focus();
      return;
    }
    if (preview) {
      message('입력 확인 완료. 미리보기이므로 상담 정보는 전송하지 않았습니다.');
      return;
    }
    const relay = window.TG && window.TG.relay;
    if (!relay) {
      message('현재 온라인 접수를 이용할 수 없습니다. 전화 또는 카카오톡으로 문의해 주세요.', true);
      return;
    }
    const name = form.elements.name.value.trim().replace(/[\r\n]/g, ' ') || '(미입력)';
    const text = '[보람상조피플 / boram22] 상담 신청\n\n이름: ' + name + '\n연락처: ' + phone
      + '\n상담 주제: ' + form.elements.topic.value + '\n유입: ' + source()
      + '\n페이지: ' + location.origin + location.pathname
      + '\n개인정보 수집·이용 동의: 예 (boram22-20261014)\n시각: ' + new Date().toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'});
    busy = true;
    submit.disabled = true;
    message('상담 신청을 전달하고 있습니다. 잠시 기다려 주세요.');
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 25000);
    try {
      const response = await fetch(relay, {method: 'POST', headers: {'Content-Type': 'text/plain'}, body: JSON.stringify({type: 'lead', text}), signal: controller.signal});
      if (!response.ok) throw new Error('HTTP error');
      const result = await response.json();
      if (result.ok !== true) throw new Error('Delivery not confirmed');
      completed = true;
      form.reset();
      message('상담 신청이 접수되었습니다. 김다혜 매니저가 확인 후 연락드리겠습니다. 추가로 남길 내용은 아래 카카오톡으로 보내주세요.');
      submit.textContent = '상담 신청 접수 완료 ✓';
    } catch (_) {
      message('접수 완료 여부를 확인하지 못했습니다. 중복 신청 전 전화 또는 카카오톡으로 접수 여부를 확인해 주세요.', true);
    } finally {
      clearTimeout(timeout);
      busy = false;
      submit.disabled = completed;
    }
  });
})();
