# Firebase setup

FarmLink uses Firebase Authentication, Cloud Firestore and Firebase Storage.
The application configuration is already present in
`apps/web/shared/assets/js/firebase.js`.

## Console steps

1. Open the Firebase project `test-8703f`.
2. In **Build > Authentication > Sign-in method**, enable **Phone** and keep
   the configured test phone number and its test OTP available for development.
3. In **Build > Firestore Database**, create a Firestore database.
4. In **Build > Storage**, create the default Storage bucket.
5. For the prototype, publish the following temporary Firestore rules:

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

6. For uploads, publish these temporary Storage rules:

```text
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

These rules are appropriate only for an authenticated prototype. Before public
launch, restrict each collection and file path to its owning user.

## Firestore indexes

Seller pages filter listings by `farmer_id` and show newest listings first.
Create this composite index in **Build > Firestore Database > Indexes** (or open
the index-creation link shown in the browser error):

| Collection | Field | Direction |
| --- | --- | --- |
| `listings` | `farmer_id` | Ascending |
| `listings` | `created_at` | Descending |

The same definition is stored in `firestore.indexes.json` for Firebase CLI
deployments. The app falls back to sorting the seller's already-filtered
listings in the browser until the index has finished building.

## Firestore collections

- `users`
- `farmer_profiles`
- `buyer_profiles`
- `listings`
- `orders`
- `order_items`
- `seller_order_status` (seller-specific fulfilment state for orders containing multiple sellers)
- `kyc_verifications`
- `bank_verifications`

Documents are created by the existing UI flows; no SQL migration is required.
