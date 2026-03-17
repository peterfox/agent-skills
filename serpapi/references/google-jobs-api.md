# SerpAPI Google Jobs API Reference

Source: https://serpapi.com/google-jobs-api

---

## Required Parameters

| Parameter | Value |
|-----------|-------|
| `engine` | `google_jobs` |
| `q` | Job search query (e.g., `"barista new york"`, `"Java Developer"`) |
| `api_key` | Your SerpApi private key |

---

## Geographic Parameters

| Parameter | Cannot combine with | Description |
|-----------|---------------------|-------------|
| `location` | `uule` | Human-readable location (city-level recommended). If omitted, proxy location is used. |
| `uule` | `location` | Google-encoded location string |
| `lrad` | — | Search radius in kilometres. Does not strictly limit results. |

---

## Localization Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `google_domain` | `google.com` | Google domain to use (see https://serpapi.com/google-domains) |
| `gl` | — | Two-letter country code (e.g., `us`, `uk`, `fr`) |
| `hl` | — | Two-letter language code (e.g., `en`, `es`, `fr`) |

---

## Pagination

| Parameter | Description |
|-----------|-------------|
| `next_page_token` | Token for retrieving the next page of results (up to 10 results per page). Obtained from `serpapi_pagination.next_page_token` in the response. |

> **Note**: The `start` offset parameter has been discontinued by Google. Always use `next_page_token` for pagination.

---

## Filter Parameters

| Parameter | Description |
|-----------|-------------|
| `uds` | Google-provided encoded filter string. Obtain values from the `filters` array in the response. Multiple filters from the same category can be combined. |
| `chips` | Additional query conditions from job search page elements. **Deprecated by Google.** |
| `ltype` | Filter for work-from-home positions. **Deprecated by Google.** Use `uds` filters instead. |

### Using `uds` Filters

`uds` values are opaque encoded strings. Always read them from the `filters` array in a prior API response — do not construct them manually.

Available filter categories (vary by query):
- **Date posted** — Yesterday, Last 3 days, Last week, etc.
- **Job type** — Full time, Part time, Contract
- **Remote** — Work from home

---

## Output & Caching Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `output` | `json` | `json`, `html` | Response format. `html` useful for debugging. |
| `no_cache` | `false` | `true`/`false` | Bypass 1-hour cache. Cached searches are free and don't count against quota. Cannot combine with `async`. |
| `async` | `false` | `true`/`false` | Async submission; retrieve via Search Archive API. Cannot combine with `no_cache`. |
| `json_restrictor` | — | — | Limit response fields for smaller payloads |
| `zero_trace` | `false` | `true`/`false` | Enterprise only. Prevents storing search data on SerpApi servers. |

---

## Response Structure

### Root-Level Fields

| Field | Description |
|-------|-------------|
| `search_metadata` | `id`, `status`, `json_endpoint`, `created_at`, `processed_at`, `google_jobs_url`, `total_time_taken` |
| `search_parameters` | Echo of all submitted parameters |
| `filters` | Available refinement options (see below) |
| `jobs_results` | Main array of job listings |
| `serpapi_pagination` | Contains `next_page_token` for subsequent pages |

---

### `filters` Structure

Filters are dynamic — always read from the response to discover available refinements.

```json
{
  "name": "Filter Category",
  "options": [
    {
      "name": "Option Label",
      "link": "https://www.google.com/search?...",
      "serpapi_link": "https://serpapi.com/search?...",
      "uds": "<encoded filter token>",
      "q": "modified query string"
    }
  ]
}
```

Single-option filters omit the `options` array and include `uds`, `link`, `serpapi_link`, and `q` directly on the filter object.

---

### `jobs_results` Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Job title |
| `company_name` | string | Employer name |
| `location` | string | Job location |
| `via` | string | Job board source (e.g., "via LinkedIn") |
| `share_link` | string | Google Jobs URL for this listing |
| `thumbnail` | string | Company logo image URL |
| `description` | string | Full job description text |
| `job_id` | string | Encoded job identifier |
| `extensions` | string[] | Raw metadata badges (e.g., salary, schedule type, benefits) |
| `detected_extensions` | object | Parsed structured metadata (see below) |
| `job_highlights` | object[] | Categorised job details (see below) |
| `apply_options` | object[] | Application portals with links (see below) |

---

### `detected_extensions` Fields

| Field | Type | Description |
|-------|------|-------------|
| `posted_at` | string | When posted (e.g., `"25 days ago"`) |
| `schedule_type` | string | e.g., `"Full-time"`, `"Part-time"`, `"Contractor"` |
| `work_from_home` | boolean | Remote work available |
| `qualifications` | string | e.g., `"No degree mentioned"` |
| `paid_time_off` | boolean | PTO offered |
| `health_insurance` | boolean | Health insurance offered |
| `dental_coverage` | boolean | Dental coverage offered |

> Fields present vary by listing.

---

### `job_highlights` Structure

```json
[
  {
    "title": "Qualifications",
    "items": ["Requirement 1", "Requirement 2"]
  },
  {
    "title": "Responsibilities",
    "items": ["Duty 1", "Duty 2"]
  },
  {
    "title": "Benefits",
    "items": ["Benefit 1", "Benefit 2"]
  }
]
```

---

### `apply_options` Structure

```json
[
  {
    "title": "Job Board Name",
    "link": "https://..."
  }
]
```

---

## Notes

- **Pagination**: `start` is discontinued — always use `next_page_token`.
- **`chips` / `ltype`**: Both deprecated by Google; use `uds` from response filters instead.
- **`lrad`**: Radius is advisory, not a hard limit.
- **`uds` tokens**: Opaque — always obtain from `filters` in the response, never construct manually.
