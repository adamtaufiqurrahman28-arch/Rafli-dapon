document.addEventListener('DOMContentLoaded', () => {
  const copyBtn = document.querySelector('[data-copy-target]');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      const target = document.getElementById(copyBtn.dataset.copyTarget);
      if (!target) return;
      await navigator.clipboard.writeText(target.value || target.textContent || '');
      const original = copyBtn.textContent;
      copyBtn.textContent = 'Tersalin ✓';
      setTimeout(() => copyBtn.textContent = original, 1600);
    });
  }

  const search = document.getElementById('menuSearch');
  if (search) {
    search.addEventListener('input', () => {
      const q = search.value.toLowerCase().trim();
      document.querySelectorAll('.menu-search-item').forEach((item) => {
        item.style.display = item.dataset.name.includes(q) ? '' : 'none';
      });
    });
  }
});
