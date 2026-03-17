# Packagist API Reference

Base URL: `https://packagist.org`

Always set: `User-Agent: your-app-name (mailto=you@example.com)`

## Authentication

Only needed for write operations. Two methods:
- Header: `Authorization: Bearer [username]:[apiToken]`
- Query params: `?username=...&apiToken=...`

SAFE tokens: read-only. MAIN tokens: also allow write operations.

## Search

```
GET /search.json?q={query}
GET /search.json?q={query}&type={type}
GET /search.json?tags={tag}
GET /search.json?q={query}&per_page=15&page=2
```

Response:
```json
{
  "results": [
    {
      "name": "vendor/package",
      "description": "...",
      "url": "https://packagist.org/packages/vendor/package",
      "repository": "https://github.com/vendor/package",
      "downloads": 123456,
      "favers": 789
    }
  ],
  "total": 42,
  "next": "https://packagist.org/search.json?q=...&page=2"
}
```

## Package Listing

```
GET /packages/list.json                               # all packages
GET /packages/list.json?vendor={vendor}               # by vendor
GET /packages/list.json?type={type}                   # by type
GET /packages/list.json?vendor={vendor}&fields[]=type&fields[]=repository&fields[]=abandoned
```

Supported extra fields: `repository`, `type`, `abandoned`

Response (simple): `{ "packageNames": ["vendor/package", ...] }`
Response (with fields): `{ "packages": { "vendor/package": { "type": "...", "repository": "..." } } }`

## Package Details

```
GET /packages/{vendor}/{package}.json
```

Cached for 12 hours. Response includes:
- `package.name`, `package.description`, `package.time`, `package.maintainers`
- `package.versions` — keyed by version string, each has `require`, `require-dev`, `license`, `homepage`, `source`
- `package.downloads` — `{ total, monthly, daily }`
- `package.favers`
- `package.repository`, `package.github_stars`, `package.github_watchers`, `package.github_forks`, `package.github_open_issues`
- `package.abandoned` — false or replacement package name

## Download Statistics

```
GET /packages/{vendor}/{package}/stats.json
```

Response:
```json
{
  "package": {
    "downloads": {
      "total": 1234567,
      "monthly": 45678,
      "daily": 1234
    },
    "versions": {
      "v1.0.0": { "downloads": 10000 },
      "v2.0.0": { "downloads": 20000 }
    },
    "date": "2013-01-01"
  }
}
```

## Popular Packages

```
GET /explore/popular.json?per_page=100
```

Sorted by downloads over the last week (not all-time). Paginated with `next` link.

## Security Advisories

```
GET /api/security-advisories/?packages[]={vendor}/{package}
GET /api/security-advisories/?packages[]={vendor}/{pkg1}&packages[]={vendor}/{pkg2}
GET /api/security-advisories/?updatedSince={timestamp}
```

Also accepts PURL format: `packages[]=pkg:composer/vendor/package`

Response:
```json
{
  "advisories": {
    "vendor/package": [
      {
        "advisoryId": "PKSA-...",
        "packageName": "vendor/package",
        "remoteId": "...",
        "title": "...",
        "link": "https://...",
        "cve": "CVE-2023-XXXXX",
        "affectedVersions": ">=1.0,<1.2.5",
        "sources": [...],
        "reportedAt": "2023-01-01T00:00:00+00:00",
        "composerRepository": "https://packagist.org",
        "severity": "high"
      }
    ]
  }
}
```

Severity values: `low`, `medium`, `high`, `critical`

## Composer v2 Metadata (efficient batch lookup)

```
GET https://repo.packagist.org/p2/{vendor}/{package}.json
GET https://repo.packagist.org/p2/{vendor}/{package}~dev.json   # dev versions
```

Static files — supports `If-Modified-Since`. Requires `composer/metadata-minifier` to expand the compressed format. Use this for automated tools; prefer `/packages/{vendor}/{package}.json` for human-readable lookups.

## Track Package Updates

```
GET /metadata/changes.json                      # initial timestamp
GET /metadata/changes.json?since={timestamp}    # poll for changes
```

Changes log kept for up to 24h. Actions: `update`, `delete`, `resync`. Useful for mirroring.

## Platform Statistics

```
GET /statistics.json
```

Returns overall platform download totals.

## Write Operations (authenticated)

```
POST /api/create-package          body: {"repository":"https://..."}   # MAIN token
PUT  /api/packages/{vendor}/{pkg} body: {"repository":"https://..."}   # MAIN token
POST /api/update-package          body: {"repository":"https://..."}   # SAFE token
```

## Rate Limiting

- Max 10 concurrent requests (20 for static files only)
- Avoid scheduled requests at predictable times (XX:00, midnight)
- Use HTTP/2-capable clients
- Use `If-Modified-Since` for caching
