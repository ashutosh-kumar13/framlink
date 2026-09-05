# FarmLink data status

FarmLink uses Firebase Authentication, Cloud Firestore and Firebase Storage
through `apps/web/shared/assets/js/firebase.js`.

| Area | Prototype status |
| --- | --- |
| Phone sign-in | Ready after enabling Phone Authentication in Firebase Console |
| Profiles and listings | Stored in Firestore |
| Cart | Browser-local state |
| Orders and checkout | Firestore-ready prototype flow |
| KYC and bank files | Firebase Storage upload path ready |
| Live listeners | Not yet enabled in the UI |

See `docs/firebase-setup.md` for Firebase Console setup and temporary prototype
Security Rules.
