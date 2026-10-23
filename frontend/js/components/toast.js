/**
 * toast.js — Toast notification component
 */
const Toast = (() => {
  let handle = null;
  const el = () => document.getElementById('toast');

  function show(msg) {
    const t = el();
    if (!t) return;
    t.textContent = msg;
    t.classList.add('on');
    clearTimeout(handle);
    handle = setTimeout(() => t.classList.remove('on'), CONFIG.TOAST_DURATION);
  }

  return { show };
})();
