// Dynamically set anchor hrefs using a configurable base URL
(function () {
  const getEnvBaseUrl = () => {
    if (typeof window !== 'undefined' && window.BASE_URL) {
      return window.BASE_URL;
    }
    if (typeof process !== 'undefined' && process.env && process.env.BASE_URL) {
      return process.env.BASE_URL;
    }
    return undefined;
  };

  const baseUrl = (document.body && document.body.dataset
    ? document.body.dataset.baseUrl
    : undefined) || getEnvBaseUrl();

  if (!baseUrl) {
    console.warn('Base URL is not defined. Anchor links may be incorrect.');
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!baseUrl) {
      return;
    }
    const anchors = document.querySelectorAll('a[data-path]');
    anchors.forEach((anchor) => {
      anchor.href = baseUrl + anchor.dataset.path;
    });
  });
})();

