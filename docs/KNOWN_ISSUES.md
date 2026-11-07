# Known Issues

Last updated: 2026-11-07 (end of Phase 1).

## Fixed in Phase 1

| #   | Issue                                                         | How it was fixed                       |
| --- | ------------------------------------------------------------- | -------------------------------------- |
| 1   | Movie creation was under `/movies/movie` (users could create) | Moved all CRUD to `/admin/movies`      |
| 2   | RBAC inconsistent: users created, admins could not            | Admin-only CRUD, users only own status |
| 3   | `title` was limited to 20 chars                               | Expanded to 200                        |
| 5   | `average_rating` only counted watched movies                  | Now computed from `user_movie_status`  |
| 7   | `/admin/*` returned 401 instead of 403                        | Returns 403 with clear message         |
| 15  | No automated tests                                            | 37 tests                               |
| 16  | No CI pipeline                                                | GitHub Actions CI                      |

## Still open

| #   | Issue                                                   | Severity | Notes                                                         |
| --- | ------------------------------------------------------- | -------- | ------------------------------------------------------------- |
| 4   | Seed data will use real TMDB data (Phase 2)             | Low      | In progress                                                   |
| 6   | Root `/` redirects to non-existent `/movies/movie-page` | Low      | Harmless in API-only mode                                     |
| 8   | **SECURITY: `role` accepted from client on signup**     | **HIGH** | Strip `role` from `CreateUserRequest`, always assign `"user"` |
| 9   | No password strength validation on backend              | Medium   | Add via Pydantic                                              |
| 10  | No email format validation on backend                   | Low      | Use `pydantic.EmailStr`                                       |
| 11  | Signup form still sends `role: 'user'`                  | Low      | Depends on fix #8                                             |
| 12  | No loading skeleton on initial fetch                    | Low      | Optional                                                      |
| 14  | Dockerfile has regional PyPI mirror arg                 | Low      | Already conditional via ARG                                   |
