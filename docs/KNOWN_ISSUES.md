# Known Issues

Discovered while building the UI (Oct-Nov 2026). Priorities to be addressed in Week 3 refactor.

## Backend / API

| #   | Issue                                                                                         | Severity | Notes                                                                                                    |
| --- | --------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------- |
| 1   | Movie creation is at `POST /movies/movie` while admin only has read/delete at `/admin/movie`. | Medium   | Move creation to admin-only, or add ownership checks.                                                    |
| 2   | RBAC is inconsistent: regular users can create movies, admins cannot.                         | Medium   | Redesign RBAC around admin-only write endpoints.                                                         |
| 3   | `MovieRequest.title` has `max_length=20` — 27/100 seed movies failed to insert.               | Low      | Increase to 200.                                                                                         |
| 4   | Seed data has only `genre=Drama`.                                                             | Low      | Diversify seed genres for testing filters.                                                               |
| 5   | `average_rating` only computes watched movies — misleading field name.                        | Low      | Rename to `average_rating_watched` or add a separate field.                                              |
| 6   | Root `/` redirects to `/movies/movie-page` which does not exist (route commented out).        | Low      | Remove redirect or restore page.                                                                         |
| 7   | `/admin/movie` returns `401` (not `403`) for authenticated non-admin users.                   | Low      | Return `403` for authenticated-but-forbidden.                                                            |
| 8   | **SECURITY: `role` is accepted from client on signup — anyone can register as `admin`.**      | **HIGH** | Strip `role` from `CreateUserRequest`; assign `"user"` always; promote via separate admin-only endpoint. |
| 9   | No password strength validation on backend.                                                   | Medium   | Add min length / complexity via Pydantic.                                                                |
| 10  | No email format validation on backend.                                                        | Low      | Use `pydantic.EmailStr`.                                                                                 |

## Frontend

| #   | Issue                                                                         | Severity | Notes                                                                 |
| --- | ----------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------- |
| 11  | Signup form hardcodes `role: 'user'` on the client.                           | Low      | Depends on fix #8 — once backend strips role, remove from client too. |
| 12  | No loading skeleton on initial `movies` fetch — brief flash of empty state.   | Low      | Add skeleton components.                                              |
| 13  | Stats endpoint's `average_rating` label is ambiguous in UI ("Avg (watched)"). | Low      | Resolve after backend fix #5.                                         |

## CI/CD / Infra

| #   | Issue                                                             | Severity | Notes                                  |
| --- | ----------------------------------------------------------------- | -------- | -------------------------------------- |
| 14  | Dockerfile uses `mirror-pypi.runflare.com` (regional workaround). | Low      | Move to build-arg or CI-only override. |
| 15  | No automated tests yet.                                           | High     | Week 1 Day 2 (pytest).                 |
| 16  | No CI pipeline yet.                                               | High     | Week 1 Day 3 (GitHub Actions).         |
