# Organizer Challenge Card

**Name:** The Hidden Test Case  
**Category:** Web / SQL Injection  
**Difficulty:** Medium  
**Points:** 134 (suggested)  
**Flag:** `SECE{legacy_search_leaks_internal_notes}`

## Player-facing description
LeetVault's old problem search has been acting strangely. Some records appear to be missing, and the database team insists everything is normal. Investigate the site and recover the hidden verification value.

## Hints (optional, release progressively)
1. The problem list is loaded from an API. Inspect the request made by the search bar.
2. Compare `ORDER BY` values and count how many columns the original query returns.
3. SQLite keeps table definitions in `sqlite_master`. A legacy note may be more interesting than the public problem list.

## Intended solution
Use SQL injection in `/api/problems?search=`. Discover four columns with `ORDER BY`, enumerate `sqlite_master`, find `internal_notes`, then retrieve its rows with a four-column `UNION SELECT`.

## Learning objectives
- Recognize SQL injection in a search parameter.
- Infer the number of result columns.
- Enumerate SQLite schema metadata.
- Extract a record through `UNION SELECT`.
- Understand why parameterized queries are essential.
