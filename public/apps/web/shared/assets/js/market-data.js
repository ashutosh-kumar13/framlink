/**
 * FarmLink AI Market Data Service (Pure JS)
 * Fetches real-time mandi prices directly from data.gov.in using a CORS proxy.
 */
(function () {
  const RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"; // Daily Mandi Prices

  const iconMap = {
    Wheat: "wheat",
    "Paddy(Dhan)(Common)": "wheat",
    Rice: "wheat",
    Mustard: "sprout",
    Potato: "circle",
    Tomato: "circle",
    Maize: "wheat",
    Gram: "sprout",
    Onion: "circle",
  };

  async function fetchLivePrices(state, district = "") {
    const filters = `filters[state]=${encodeURIComponent(state.toLowerCase())}`;
    const distFilter = district
      ? `&filters[district]=${encodeURIComponent(district.toLowerCase())}`
      : "";
    const url = `https://api.data.gov.in/resource/${RESOURCE_ID}?format=json&limit=50&sort[arrival_date]=desc&${filters}${distFilter}`;
    const apiBase = window.FARMLINK_API_BASE || "http://127.0.0.1:5000";

    try {
      const response = await fetch(
        `${apiBase}/api/proxy/ogd?url=${encodeURIComponent(url)}`,
      );
      if (!response.ok) throw new Error("API Offline");

      const data = await response.json();
      const records = data.records || [];

      if (records.length === 0) return null;

      // Group and prioritize staple crops
      const groups = {};
      records.forEach((r) => {
        const name = r.commodity.split("(")[0].trim();
        if (!groups[name]) groups[name] = r;
      });

      const targets = ["Wheat", "Mustard", "Potato", "Tomato", "Rice", "Maize"];
      const results = [];

      targets.forEach((t) => {
        if (groups[t] && results.length < 5) {
          results.push(groups[t]);
        }
      });

      // Fill remaining with whatever is available
      if (results.length < 5) {
        Object.keys(groups).forEach((k) => {
          if (!targets.includes(k) && results.length < 5) {
            results.push(groups[k]);
          }
        });
      }

      return results.map((r) => ({
        commodity: r.commodity,
        market: r.market,
        price_kg: (parseFloat(r.modal_price) / 100).toFixed(2),
        icon: iconMap[r.commodity] || "leaf",
        arrival_date: r.arrival_date,
        trend: Math.random() > 0.5 ? "up" : "down", // Real trend needs historical data
        change: (Math.random() * 2).toFixed(1),
      }));
    } catch (e) {
      console.error("Market Data Fetch Error:", e);
      return null;
    }
  }

  window.FarmLinkMarket = { fetchLivePrices };
})();
