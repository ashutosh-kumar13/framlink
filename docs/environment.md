# Environment configuration

The forecast service reads runtime configuration from `mandi-price-forecast/.env`.

Create that file locally from `.env.example` and set the real `DATA_GOV_API_KEY` value. The `.env` file is ignored and must never be committed.

## GitHub deployment

For GitHub Actions or a hosted deployment, add these as repository or environment secrets/variables instead of committing `.env`:

- Secret: `DATA_GOV_API_KEY`
- Variables: `DATA_GOV_RESOURCE_ID`, `DATA_GOV_DAILY_RESOURCE_ID`, `DATA_GOV_PINCODE_RESOURCE_ID`
- Variables: `DEFAULT_STATE`, `DEFAULT_DISTRICT`, `DEFAULT_MANDI`, `DEFAULT_COMMODITY`, `DEFAULT_VARIETY`
- Variables: `MAX_RECORDS`, `HISTORY_YEARS`, `FLASK_HOST`, `FLASK_PORT`, `FLASK_DEBUG`

Firebase browser configuration is public client configuration. Protect the Firebase project with Authentication, Firestore, and Storage security rules; do not place server credentials in frontend files.
