# SerpAPI Google Search API Reference

Source: https://serpapi.com/search-api

---

## Required Parameters

| Parameter | Description |
|-----------|-------------|
| `engine` | `google` |
| `q` | Search query. Supports Google operators: `site:`, `inurl:`, `intitle:`, etc. |
| `api_key` | Your SerpApi private key |

---

## Geographic Location Parameters

All location methods are mutually exclusive — use only one.

| Parameter | Cannot combine with | Description |
|-----------|---------------------|-------------|
| `location` | `uule`, `lat`, `lon` | Human-readable location (city-level recommended) |
| `uule` | `location`, `lat`, `lon`, `radius` | Google-encoded location string |
| `lat` + `lon` | `location`, `uule` | GPS coordinates (both required together). May need matching `gl`. |
| `radius` | — | Distance bias in meters. Desktop: 1–199m. Tablet/Mobile: 1–1000m. Works with `location` or `lat`/`lon`. |

---

## Advanced Geographic Parameters

| Parameter | Description |
|-----------|-------------|
| `ludocid` | Google CID for a specific place (found in local results as `place_id` or `data_cid`) |
| `lsig` | Forces knowledge graph map view. Sourced from Local Pack or Google Local APIs. |
| `kgmid` | Google Knowledge Graph entity ID. May override other params except `start`. |
| `si` | Cached encrypted search parameters. Overrides most params except `start`. |
| `ibp` | Controls layout rendering (e.g., expanded knowledge graphs) |
| `uds` | Filter string provided by Google (found in `filters` section of response) |

---

## Localization Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `google_domain` | `google.com` | Google domain to use. 184 domains supported (see https://serpapi.com/google-domains). |
| `gl` | — | Two-letter country code (e.g., `us`, `uk`, `fr`). Recommended alongside `location`. |
| `hl` | — | Two-letter language code (e.g., `en`, `es`, `fr`). Controls UI language. |
| `cr` | — | Country restriction. Format: `countryFR\|countryDE` |
| `lr` | — | Language restriction. Format: `lang_fr\|lang_de` |

---

## Search Type (`tbm`)

| Value | Search Type |
|-------|-------------|
| *(blank)* | Standard web search |
| `isch` | Images |
| `lcl` | Local |
| `vid` | Videos |
| `nws` | News |
| `shop` | Shopping |
| `pts` | Patents |

---

## Advanced Filter Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tbs` | — | "To be searched" — advanced filters not available in the query string. Enables filtering by date, patents, news, videos, images, apps, text content. See https://serpapi.com/advanced-google-query-parameters for full list of values. |
| `safe` | blur | Adult content filter: `active` (strict) or `off` |
| `nfpr` | `0` | Auto-correction: `1` = exclude corrected results, `0` = include |
| `filter` | `1` | Similar/omitted results toggle: `1` = on (default), `0` = off |

---

## Pagination Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `start` | `0` | Result offset. `0` = page 1, `10` = page 2, `20` = page 3, etc. |

---

## Device & Output Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `device` | `desktop` | `desktop`, `tablet`, `mobile` | Controls user-agent and rendering |
| `output` | `json` | `json`, `html` | Response format. `html` is useful for debugging unsupported features. |
| `no_cache` | `false` | `true`/`false` | Bypass 1-hour cache. Cached searches are free and don't count against quota. Cannot combine with `async`. |
| `async` | `false` | `true`/`false` | Async submission; retrieve via Search Archive API. Cannot combine with `no_cache`. Not on Ludicrous Speed plan. |
| `json_restrictor` | — | — | Limit response fields for smaller payloads |
| `zero_trace` | `false` | `true`/`false` | Enterprise only. Prevents storing search data on SerpApi servers. |

---

## Response Structure

### Root-Level Fields

| Field | Description |
|-------|-------------|
| `search_metadata` | `id`, `status`, `json_endpoint`, `created_at`, `processed_at`, `google_url`, `raw_html_file`, `total_time_taken` |
| `search_parameters` | Echo of all submitted parameters |
| `search_information` | `organic_results_state`, `query_displayed`, `total_results`, `time_taken_displayed` |
| `knowledge_graph` | Entity panel (when applicable) |
| `answer_box` | Direct answer/featured snippet (when applicable) |
| `organic_results` | Main search results array |
| `local_results` | Local business results (when applicable) |
| `images_results` | Image results (when applicable) |
| `news_results` | News results (when applicable) |
| `shopping_results` | Shopping results (when applicable) |
| `video_results` | Video results (when applicable) |
| `recipes_results` | Recipe results (when applicable) |
| `related_searches` | Suggested alternative queries |
| `pagination` | Both Google and SerpApi pagination with next/previous links |

---

### `organic_results` Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Ranking position |
| `title` | string | Result headline |
| `link` | string | Destination URL |
| `redirect_link` | string | Google's redirect wrapper URL |
| `displayed_link` | string | Formatted URL shown in search results |
| `snippet` | string | Preview text excerpt |
| `date` | string | Publication/update timestamp (optional) |
| `thumbnail` | string | Associated image URL (optional) |
| `sitelinks` | object | Inline navigation links to subpages (optional) |
| `rich_snippet` | object | Enhanced data: ratings, extensions, structured snippets (optional) |
| `about_this_result` | object | Source metadata, keywords, languages, regions (optional) |
| `cached_page_link` | string | Google's cached version URL (optional) |
| `related_pages_link` | string | Similar content discovery URL (optional) |

---

### `knowledge_graph` Fields

| Field | Description |
|-------|-------------|
| `title` | Entity name |
| `type` | Entity type/category |
| `description` | Summary text |
| `images` | Array of image URLs |
| `books` | Related books (when applicable) |
| `related_searches` | Related entity queries |
| *(additional fields vary by entity type)* | Nutritional data, species info, etc. |

---

### `local_results` Item Fields

| Field | Description |
|-------|-------------|
| `title` | Business name |
| `rating` | Average rating |
| `reviews` | Review count |
| `price` | Price level indicator |
| `address` | Street address |
| `gps_coordinates` | `{ lat, lon }` |
| `place_id` | Google place identifier |

---

## Notes

- **`tbs` values**: See https://serpapi.com/advanced-google-query-parameters for the full list of date, type, and content filters.
- **`cr` / `lr` formatting**: Multiple values use pipe separator, e.g., `countryFR|countryDE`, `lang_fr|lang_de`.
- **`kgmid` / `si`**: These can override most other parameters; use carefully when combining with other filters.
- **Cached results**: Free and do not count against your API quota.
- **Status flow**: `Processing` → `Success` or `Error`. Error details appear in the `error` field.
