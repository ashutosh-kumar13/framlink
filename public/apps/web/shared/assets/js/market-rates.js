/**
 * FarmLink Pure JavaScript Market Rates Service
 * Fetches real-time mandi prices using the local Python proxy for reliability.
 */
(function () {
  const MAIN_RESOURCE = "35985678-0d79-46b4-9ed6-6f13308a1d24"; // Historical Resource (More Reliable)
  const LOCAL_PROXY = "http://127.0.0.1:5000/api/proxy/ogd?url=";

  function normalize(str) {
    if (!str) return "";
    const acronyms = ["APMC", "MSP", "FAQ"];
    return str
      .toLowerCase()
      .split(" ")
      .map((word) => {
        const upper = word.toUpperCase();
        return acronyms.includes(upper)
          ? upper
          : word.charAt(0).toUpperCase() + word.slice(1);
      })
      .join(" ");
  }

  async function fetchWithRetry(apiTarget) {
    try {
      const url = `${LOCAL_PROXY}${encodeURIComponent(apiTarget)}`;
      const response = await fetch(url);
      if (response.ok) return await response.json();
    } catch (e) {
      console.warn(`[MarketJS] Proxy fetch failed:`, e);
    }
    return null;
  }

  async function fetchLiveMandiRates(state, district = "") {
    console.log(`[MarketJS] Syncing market data for ${state}, ${district}...`);

    // 3-Stage Greedy Strategy
    const strategies = [
      {
        name: "Mandi Match",
        filters: `&filters[State]=${encodeURIComponent(normalize(state))}&filters[District]=${encodeURIComponent(normalize(district))}`,
      },
      {
        name: "State Match",
        filters: `&filters[State]=${encodeURIComponent(normalize(state))}`,
      },
      { name: "National Match", filters: "" },
    ];

    for (let strategy of strategies) {
      try {
        // Historical resource uses Uppercase field names
        const apiTarget = `https://api.data.gov.in/resource/${MAIN_RESOURCE}?format=json&limit=50&sort[Arrival_Date]=desc${strategy.filters}`;
        const data = await fetchWithRetry(apiTarget);

        if (data && data.records && data.records.length > 0) {
          console.log(`[MarketJS] Data found via ${strategy.name}`);

          const groups = {};
          data.records.forEach((r) => {
            const commName = r.Commodity || r.commodity || "Unknown";
            const key =
              commName.charAt(0).toUpperCase() +
              commName.slice(1).toLowerCase();
            if (!groups[key]) groups[key] = [];
            groups[key].push(r);
          });
          return groups;
        }
      } catch (error) {
        console.error(`[MarketJS] ${strategy.name} failed:`, error);
      }
    }
    return null;
  }

  window.FarmLinkMarket = {
    fetchLiveMandiRates,
    iconMap: {
      Wheat: "wheat",
      Rice: "wheat",
      Paddy: "wheat",
      Maize: "wheat",
      Gram: "sprout",
      Mustard: "sprout",
      Potato: "circle",
      Tomato: "circle",
      Onion: "circle",
    },
  };
})();
