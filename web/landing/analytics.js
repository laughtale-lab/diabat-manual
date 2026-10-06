(function () {
  'use strict';

  const GOATCOUNTER_ENDPOINT =
    'https://diabat-manual.goatcounter.com/count';

  const GOATCOUNTER_TOTAL =
    'https://diabat-manual.goatcounter.com/counter/TOTAL.json';

  const COUNTER_ELEMENT_ID =
    'manual-access-count';


  /*
   * Only track visits on the production GitHub Pages site.
   * Local previews will not be sent to GoatCounter.
   */
  const isProductionSite =
    window.location.hostname === 'laughtale-lab.github.io' &&
    window.location.pathname.startsWith('/diabat-manual');


  /*
   * Record a visit to the HTML Manual page as /manual-home.
   */
  if (isProductionSite) {
    window.goatcounter = {
      path: '/manual-home'
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
   * Display the total number of Manual visits.
   *
   * At present GoatCounter records only:
   *
   *   /manual-home
   *       visits to the HTML Manual page
   *
   *   readme-pdf
   *       PDF accesses from the GitHub repository README
   *
   * Therefore:
   *
   *   GoatCounter TOTAL
   *     = HTML Manual visits
   *     + README-to-PDF visits
   */
  async function displayManualVisitCount() {
    const element =
      document.getElementById(COUNTER_ELEMENT_ID);

    if (!element) {
      return;
    }

    try {
      const response = await fetch(
        GOATCOUNTER_TOTAL,
        {
          cache: 'no-store'
        }
      );

      if (!response.ok) {
        throw new Error(
          'Unable to retrieve GoatCounter statistics.'
        );
      }

      const data = await response.json();

      element.textContent = data.count;

    } catch (error) {
      console.warn(
        'Unable to display the Manual visit count:',
        error
      );

      element.textContent = '—';
    }
  }


  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded',
      displayManualVisitCount
    );
  } else {
    displayManualVisitCount();
  }
})();