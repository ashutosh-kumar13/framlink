# Architecture boundaries

## Web

`apps/web` contains static HTML routes and web-only assets. Routes are grouped by feature, not by implementation type.

## API

`apps/api` is reserved for authentication, listings, orders, payment, KYC, notifications, and future database integrations. Keep its source code isolated from browser UI files.

## Future buyer and driver products

Buyer routes belong in `apps/web/pages/buyer`. A separate driver experience belongs in `apps/driver`; this permits it to become a mobile app later without disturbing seller code.

## Shared packages

Place cross-application UI, types, validation, API clients, and configuration in `packages` once JavaScript modules are introduced.
