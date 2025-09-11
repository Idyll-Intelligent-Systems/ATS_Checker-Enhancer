document.addEventListener('DOMContentLoaded', () => {
  const baseUrl = document.body.dataset.baseUrl || '';
  document.querySelectorAll('a[data-path]').forEach((element) => {
    element.href = `${baseUrl}${element.dataset.path}`;
  });
});

