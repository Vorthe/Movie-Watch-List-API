# Phase 4 — Production-Grade Features

## What

Add three features that turn the project from "works" to "production-ready":

1. Real email sending (SendGrid)
2. Admin panel in frontend (RBAC)
3. Content-based movie recommendations

Plus optional ideas borrowed from Letterboxd / Trakt / Simkl if time allows.

## Why

The project already covers the happy path: users browse movies, mark
them, get in-app notifications. What it does not show yet:

- Real third-party API integration (SendGrid) with retries and errors
- Full RBAC flow (backend + frontend), not just backend checks
- Product thinking (recommendations turn a list into a personal service)

These three are what separates a "portfolio project" from "a product".

## Decisions

- **SendGrid over AWS SES**: simpler setup, free 100 emails/day, one API key
- **Admin panel as a route in the same app**, not a separate SPA.
  Vue Router `meta: { requiresAdmin: true }`. One build, one deploy.

## Tasks (in order)

### 4.1 — SendGrid

- [ ] Add `sendgrid` to requirements
- [ ] Get SendGrid API key
- [ ] Update `App/tasks.py::send_welcome_notification` to send email
- [ ] Add `autoretry_for` with exponential backoff
- [ ] Add `SENDGRID_API_KEY`, `EMAIL_FROM` to env vars
- [ ] Test locally
- [ ] Deploy and test on production

### 4.2 — Admin panel

- [ ] Add `meta: { requiresAdmin: true }` to router
- [ ] Decode `role` from JWT in auth store
- [ ] Add API client `api/admin.js`
- [ ] Create `AdminView.vue` (list, create, delete catalog movies)
- [ ] Guard in `router.beforeEach` (redirect non-admin)
- [ ] Test local
- [ ] Deploy

### 4.3 — Recommendations

- [ ] Add `GET /recommendations` endpoint
      (based on user's top genres + high external_rating unseen movies)
- [ ] Add `api/recommendations.js`
- [ ] Create `RecommendationsView.vue`
- [ ] Add to navbar
- [ ] Test local
- [ ] Deploy

### 4.4 — Optional (only if time allows)

- [ ] `watched_at` column on `user_movie_status` (from Letterboxd idea)
- [ ] Advanced stats (genre distribution, monthly trend — from Trakt)
- [ ] Import from Letterboxd CSV (from Simkl)

## Files

**Backend:**

- `App/tasks.py` (SendGrid in welcome task)
- `App/routers/recommendations.py` (new)
- `App/main.py` (include router)
- `requirements.txt` (sendgrid)

**Frontend:**

- `frontend/src/views/AdminView.vue` (new)
- `frontend/src/views/RecommendationsView.vue` (new)
- `frontend/src/api/admin.js` (new)
- `frontend/src/api/recommendations.js` (new)
- `frontend/src/router/index.js` (routes + guards)
- `frontend/src/stores/auth.js` (decode role)

**Docs:**

- `docs/PHASE-4.md` (this file)
- `docs/adr/ADR-004-sendgrid.md` (during 4.1)

## Done when

- Signup sends a real email (check inbox)
- Admin sees admin panel; non-admin redirected
- User sees "Recommended for you" with real suggestions
- 55+ tests still pass
- All deployed to production
