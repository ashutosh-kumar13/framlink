# FarmLink AI

## Project layout

```text
apps/
  web/                 Static web application
    index.html          Web entry point
    pages/
      auth/             Login and OTP
      onboarding/       Registration and KYC
      seller/           Seller workspace routes
      buyer/            Reserved for buyer workspace routes
      driver/           Reserved for driver workspace routes
    shared/assets/      Web-only CSS and JavaScript
  api/                  Future backend service
  driver/               Future standalone driver application
packages/
  ui/                   Future reusable UI components
  config/               Future shared configuration
infra/                  Deployment and infrastructure configuration
docs/                   Product and technical documentation
```

## Naming rules

- Use lowercase kebab-case for files and folders.
- Keep a page inside the user feature it belongs to, for example `pages/seller/seller-orders.html`.
- Put web-only assets under `apps/web/shared/assets`.
- Put reusable code shared by web, API, or future apps under `packages`.
- Do not place backend, database, driver, or buyer source files in seller folders.

## Current entry point

Open `apps/web/index.html` to start the existing static web experience.
