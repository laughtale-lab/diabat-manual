(function () {
  'use strict';

  const GOATCOUNTER_ENDPOINT =
    'https://diabat-manual.goatcounter.com/count';

  /*
   * Statistics used for the public Manual access counter.
   *
   * /manual-home
   *     Visits to the HTML Manual landing page.
   *
   * readme-pdf
   *     PDF accesses initiated from the GitHub repository README.
   */
  const HOME_PATH = '/manual-home';
  const README_PDF_EVENT = 'readme-pdf';

  const COUNTER_BASE =
    'https://diabat-manual.goatcounter.com/counter/';

  const COUNTER_ELEMENT_ID = 'manual-access-count';


  /*
   * Track the HTML landing page only on the production GitHub Pages site.
   * Local previews therefore do not pollute the statistics.
   */
  const isProductionSite =
    window.location.hostname === 'laughtale-lab.github.io' &&
    window.location.pathname.startsWith('/diabat-manual');

  if (isProductionSite) {
    window.goatcounter = {
      path: HOME_PATH
    };

    const script = document.createElement('script');

    script.async = true;
    script.src = 'https://gc.zgo.at/count.js';
    script.setAttribute(
      'data-goatcounter',
      GOATCOUNTER_ENDPOINT
    );

    document.head.appendChild(script);
  }


  /*
   * Read a public GoatCounter count.
   *
   * GoatCounter returns the count as a formatted string, for example
   * "1,234". Convert it to an integer before adding the two counters.
   *
   * A path that has not yet been recorded may return 404. In that case
   * its count is treated as zero.
   */
  async function getPublicCount(path) {
    const url =
      COUNTER_BASE +
      encodeURIComponent(path) +
      '.json';

    const response = await fetch(url, {
      cache: 'no-store'
    });

    if (response.status === 404) {
      return 0;
    }

    if (!response.ok) {
      throw new Error(
        'Unable to retrieve GoatCounter statistics.'
      );
    }

    const data = await response.json();

    const numericCount =
      String(data.count).replace(/[^\d]/g, '');

    return numericCount
      ? Number.parseInt(numericCount, 10)
      : 0;
  }


  /*
   * Display:
   *
   *   HTML landing-page visits
   * + README-to-PDF accesses
   * --------------------------------
   *   total Manual accesses
   */
  async function displayManualAccessCount() {
    const element =
      document.getElementById(COUNTER_ELEMENT_ID);

    if (!element) {
      return;
    }

    try {
      const [homeVisits, readmePdfVisits] =
        await Promise.all([
          getPublicCount(HOME_PATH),
          getPublicCount(README_PDF_EVENT)
        ]);

      const total =
        homeVisits + readmePdfVisits;

      element.textContent =
        total.toLocaleString('en-US');
    } catch (error) {
      console.warn(
        'Unable to display the Manual access count:',
        error
      );

      element.textContent = '—';
    }
  }


  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      displayManualAccessCount
    );
  } else {
    displayManualAccessCount();
  }
})();