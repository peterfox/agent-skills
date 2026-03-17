---
name: packagist
description: Look up PHP packages on Packagist using the API. Use when the user wants to search for packages, get package details or metadata, check download statistics, look up security advisories, list packages by vendor or type, or find popular PHP packages. Triggers on phrases like "find a package for...", "look up packagist", "search for a composer package", "check package stats", "packagist security advisories", "what packages does vendor X have".
---

# Packagist

Use the Packagist API (via WebFetch) to look up PHP packages. Always include a `User-Agent` with `mailto=` when making requests.

See [references/api.md](references/api.md) for all endpoints and response formats.

## Common Tasks

### Search for packages
```
GET https://packagist.org/search.json?q={query}&per_page=15
```
Filter by type: `&type=symfony-bundle`
Filter by tag: `&tags=psr-3`

### Get package details
```
GET https://packagist.org/packages/{vendor}/{package}.json
```
Returns maintainers, all versions, dependencies, downloads, favers, GitHub info.

### Get download stats
```
GET https://packagist.org/packages/{vendor}/{package}/stats.json
```

### Check security advisories
```
GET https://packagist.org/api/security-advisories/?packages[]={vendor}/{package}
```
Multiple packages: repeat `packages[]=` for each.

### List a vendor's packages
```
GET https://packagist.org/packages/list.json?vendor={vendor}
```

## Presenting Results

- For search results: show name, description, downloads, and favers
- For package details: show latest stable version, description, license, homepage, and key dependencies
- For stats: show total downloads and monthly trend
- For security advisories: show CVE, severity, affected versions, and title — flag any unpatched advisories clearly
