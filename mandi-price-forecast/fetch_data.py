import os
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import API_KEY, DAILY_RESOURCE_ID, RESOURCE_ID, RAW_DATA_PATH, MAX_RECORDS

def title_case(value: str) -> str:
    if not value: return ""
    acronyms = {"APMC", "MSP", "FAQ"}
    words = value.strip().split()
    result = []
    for word in words:
        if "(" in word and ")" in word:
            parts = word.replace("(", " (").replace(")", ") ").split()
            formatted_parts = []
            for p in parts:
                if p.startswith("("):
                    formatted_parts.append(f"({p[1:-1].capitalize()})")
                else:
                    formatted_parts.append(p.capitalize())
            result.append("".join(formatted_parts))
        elif word.upper() in acronyms:
            result.append(word.upper())
        else:
            result.append(word.capitalize())
    return " ".join(result)

def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    })
    session.mount("https://", HTTPAdapter(max_retries=Retry(
        total=5,
        backoff_factor=3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )))
    return session

def fetch_mandi_data(state, district, market, commodity, variety=None, limit=None):
    """
    Enhanced fetcher with optional limit for quick updates.
    """
    api_key = os.getenv("DATA_GOV_API_KEY", API_KEY)
    if not api_key:
        return False, "DATA_GOV_API_KEY is not configured."
    session = get_session()

    resources = [RESOURCE_ID, DAILY_RESOURCE_ID]
    fetch_limit = max(1, limit or MAX_RECORDS)

    # Handle market name variants (bare name vs APMC)
    market_variants = [market]
    if "APMC" in market:
        market_variants.append(market.replace("APMC", "").strip())
    elif "APMC" not in market:
        market_variants.append(f"{market} APMC")

    # Deduplicate variants
    market_variants = list(dict.fromkeys(market_variants))

    all_raw_records = []

    for rid in resources:
        for m_variant in market_variants:
            print(f"Checking Resource {rid} for Market variant: '{m_variant}'...")
            offset = 0
            page_size = 50
            source_count = 0

            is_historical = rid.startswith("3598")
            s_key = "filters[State]" if is_historical else "filters[state]"
            m_key = "filters[Market]" if is_historical else "filters[market]"
            c_key = "filters[Commodity]" if is_historical else "filters[commodity]"
            v_key = "filters[Variety]" if is_historical else "filters[variety]"
            d_key = "sort[Arrival_Date]" if is_historical else "sort[arrival_date]"

            params = {
                "api-key": api_key, "format": "json", "limit": page_size,
                d_key: "desc",
                s_key: title_case(state),
                m_key: title_case(m_variant),
                c_key: title_case(commodity),
            }
            if variety: params[v_key] = title_case(variety)

            try:
                while source_count < fetch_limit:
                    params["offset"] = offset
                    # Increased timeout for potentially slow gov server
                    response = session.get(f"https://api.data.gov.in/resource/{rid}", params=params, timeout=120)

                    if response.status_code == 200:
                        data = response.json()
                        records = data.get("records", [])
                        if not records:
                            break

                        all_raw_records.extend(records)
                        source_count += len(records)
                        offset += page_size
                        if len(records) < page_size:
                            break
                        time.sleep(0.2)
                    else:
                        break

                print(f"  Done: Fetched {source_count} records from this variant.")
            except Exception as e:
                print(f"  Warning: Resource {rid} failed for variant {m_variant}: {e}")
                continue

    if all_raw_records:
        df = pd.DataFrame(all_raw_records)
        df.columns = [c.lower() for c in df.columns]
        required_columns = {"arrival_date", "market", "commodity", "variety"}
        if not required_columns.issubset(df.columns):
            missing = ", ".join(sorted(required_columns - set(df.columns)))
            return False, f"API response is missing columns: {missing}"

        # Deduplicate across variants and resources
        initial_len = len(df)
        df = df.drop_duplicates(subset=['arrival_date', 'market', 'commodity', 'variety']).reset_index(drop=True)
        print(f"MERGE COMPLETE: Final dataset has {len(df)} unique records (Removed {initial_len - len(df)} duplicates).")

        os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
        df.to_csv(RAW_DATA_PATH, index=False)
        return True, f"Success: {len(df)} records merged."

    return False, "No data found for this selection or its variants."

if __name__ == "__main__":
    from config import STATE, DISTRICT, MANDI, COMMODITY
    success, msg = fetch_mandi_data(STATE, DISTRICT, MANDI, COMMODITY)
    print(msg)
