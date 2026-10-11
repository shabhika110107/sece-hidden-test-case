# LeetVault: The Hidden Test Case (SECE CTF)

A deliberately vulnerable, self-contained Flask + SQLite web challenge for a controlled CTF.

## Challenge details
- **Category:** Web / SQL Injection
- **Difficulty:** Medium
- **Flag:** `SECE{legacy_search_leaks_internal_notes}`
- **Vulnerable endpoint:** `GET /api/problems?search=...`
- **Intended solve:** identify the four-column query, use a `UNION SELECT` against SQLite metadata, discover `internal_notes`, then extract the verification record.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visit http://127.0.0.1:5000

## Host on Render (Docker)
1. Create a new GitHub repository and upload the contents of this folder.
2. In Render, create **New → Web Service** and connect the repository.
3. Choose **Docker** as the runtime.
4. Add environment variable `CTF_FLAG` with your final flag value.
5. Deploy and test `/`, `/problems`, `/challenge`, and `/api/problems`.

Do not commit a real flag if the repository is public. Prefer a private repository and set `CTF_FLAG` in the host's environment settings.

## CTF operator safety
This app intentionally uses unsafe SQL string interpolation. Deploy it only as an isolated CTF target:
- use a dedicated challenge instance, not a production database;
- don't store real user data, credentials, or secrets;
- use a disposable container/database and limit access to the challenge;
- set resource limits and monitor the instance;
- reset/redeploy after the event.

## Intended solution (organizer copy)
1. Visit `/problems`; note the search API is `/api/problems?search=...`.
2. The query can be tested for SQL injection using a quote and boolean condition.
3. `ORDER BY 4` works while `ORDER BY 5` fails, indicating four selected columns.
4. A four-column `UNION SELECT` can add a synthetic row.
5. Enumerate SQLite tables via `sqlite_master`; note `internal_notes`.
6. Query `internal_notes` using four compatible expressions, for example:
   `' UNION SELECT id,note_type,content,created_at FROM internal_notes--`
7. Read the `content` field in the returned JSON; the verification flag is `SECE{legacy_search_leaks_internal_notes}`.

## Defensive lesson
Use parameterized SQL queries (`?` placeholders) and strict allow-listed query behavior. Never concatenate user input into SQL.
