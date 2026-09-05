# Plan - Dynamic Commodity Menu (API-based)

The user wants to replace the static/manual commodity input fields with a dynamic menu (dropdown/datalist) that fetches available commodities from an API. This will improve user experience by showing valid options directly.

## User Review Required

> [!IMPORTANT]
> - I will implement a **Datalist** approach. This allows users to see a dropdown of available commodities while still being able to type for quick searching.
> - The commodity list will be fetched from a new backend endpoint `/api/market/commodities`.
> - The list will initially include common crops defined in the system and can be extended to include others found in recent data.

## Proposed Changes

### Backend - API Support

#### [MODIFY] [app.py](file:///C:/Users/PC/Videos/v1/mandi-price-forecast/app.py)
- Add a new route `/api/market/commodities`.
- This route will return a JSON list of available commodities, sourced from `config.py` and potentially augmented by unique values found in the data directory.

### Frontend - Mandi AI Dashboard

#### [MODIFY] [index.html](file:///C:/Users/PC/Videos/v1/mandi-price-forecast/templates/index.html)
- Add a `<datalist id="commodity-list">` element.
- Link the `#commodity` input to this datalist using the `list` attribute.

#### [MODIFY] [script.js](file:///C:/Users/PC/Videos/v1/mandi-price-forecast/static/script.js)
- Add logic to fetch commodities from `/api/market/commodities` on page load.
- Populate the `#commodity-list` datalist with the fetched options.

### Frontend - Seller AI Insights

#### [MODIFY] [seller-ai-insights.html](file:///C:/Users/PC/Videos/v1/public/apps/web/pages/seller/seller-ai-insights.html)
- Add a `<datalist id="commodity-list">` element.
- Link the `#input-commodity` input to this datalist.
- Add JavaScript logic (similar to `script.js`) to fetch and populate the datalist on load.

## Verification Plan

### Manual Verification
1. Open the **Mandi AI Forecasting** dashboard.
2. Click on the "फसल (Commodity)" input field. Verify a dropdown appears with options like Wheat, Rice, Mustard, etc.
3. Start typing "P" and verify "Potato" and "Paddy" appear in the filtered list.
4. Repeat the same for the **Seller AI Insights** page.
5. Check the network tab to ensure `/api/market/commodities` is called exactly once per page load.
