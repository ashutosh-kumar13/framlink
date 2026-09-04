const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;
const RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070";
const DATA_GOV_URL = `https://api.data.gov.in/resource/${RESOURCE_ID}`;

app.use(express.json());
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", process.env.CORS_ORIGIN || "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

function input(req, name) {
  return String(req.body?.[name] ?? req.query[name] ?? "").trim();
}

app.get("/", (req, res) => {
  res.json({
    ok: true,
    service: "FarmLink Retell API",
    endpoint: "/api/get-mandi-price",
  });
});

app.get("/health", (req, res) => {
  res.json({ ok: true, service: "FarmLink Retell API" });
});

async function getMandiPrice(req, res) {
  const apiKey = process.env.DATA_GOV_API_KEY;
  if (!apiKey) {
    return res
      .status(503)
      .json({ ok: false, message: "DATA_GOV_API_KEY is not configured." });
  }

  const params = new URLSearchParams({
    "api-key": apiKey,
    format: "json",
    limit: "20",
  });
  for (const field of ["state", "district", "market", "commodity"]) {
    const value = input(req, field);
    if (value) params.set(`filters[${field}]`, value);
  }

  try {
    const upstream = await fetch(`${DATA_GOV_URL}?${params}`);
    if (!upstream.ok) {
      return res
        .status(502)
        .json({ ok: false, message: "Mandi data is temporarily unavailable." });
    }

    const payload = await upstream.json();
    const records = (payload.records || []).map((record) => ({
      state: record.state || "",
      district: record.district || "",
      market: record.market || "",
      commodity: record.commodity || "",
      variety: record.variety || "",
      arrival_date: record.arrival_date || "",
      modal_price: record.modal_price || "",
      min_price: record.min_price || "",
      max_price: record.max_price || "",
    }));

    return res.json({
      ok: true,
      message: records.length
        ? `Latest mandi prices found for ${input(req, "commodity") || "the requested crop"}.`
        : "No mandi prices found for the requested filters.",
      records,
      total: records.length,
    });
  } catch (error) {
    console.error("Mandi API error:", error);
    return res
      .status(502)
      .json({
        ok: false,
        message: "Could not connect to the mandi price service.",
      });
  }
}

app.get("/api/get-mandi-price", getMandiPrice);
app.post("/api/get-mandi-price", getMandiPrice);

module.exports = app;

if (process.env.NODE_ENV !== "production") {
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}
