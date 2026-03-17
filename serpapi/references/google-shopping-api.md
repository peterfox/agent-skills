# SerpAPI Google Shopping API Reference

Source: https://serpapi.com/google-shopping-api

---

## Required Parameters

| Parameter | Value |
|-----------|-------|
| `engine` | `google_shopping` |
| `q` | Search query |
| `api_key` | Your SerpApi private key |

---

## Search Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `q` | — | Search query |
| `shoprs` | — | Encoded filter metadata string. Multiple filters joined with `||`. Overrides `q` for filter-only requests. Obtain values from `filters[].options[].shoprs` or `carousel_filters[].shoprs` in API responses. |

---

## Geographic & Localization Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `location` | — | Search origin location (city-level recommended). Mutually exclusive with `uule`. |
| `uule` | — | Google-encoded location. Mutually exclusive with `location`. |
| `google_domain` | `google.com` | Google domain to use. 184 domains supported (see https://serpapi.com/google-domains). |
| `gl` | — | Two-letter country code (e.g., `us`, `uk`, `fr`) |
| `hl` | — | Two-letter language code (e.g., `en`, `es`, `fr`) |

---

## Filter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_price` | number | Minimum price. Overrides any price filter in `shoprs`. |
| `max_price` | number | Maximum price. Overrides any price filter in `shoprs`. |
| `sort_by` | integer | Sort order (see below). Overrides `shoprs` sorting. |
| `free_shipping` | boolean | Filter to free shipping items only. |
| `on_sale` | boolean | Filter to sale items only. |
| `small_business` | boolean | Filter to small business products only. |

### `sort_by` Values

| Value | Description |
|-------|-------------|
| `1` | Price: low to high |
| `2` | Price: high to low |

---

## Pagination Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `start` | `0` | Result offset. `0` = page 1, `60` = page 2, `120` = page 3. **Not recommended for new layout** — use `serpapi_pagination.next` from the response instead. |

---

## Device & Output Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `device` | `desktop` | `desktop`, `tablet`, `mobile` | Browser device type |
| `output` | `json` | `json`, `html` | Response format |
| `no_cache` | `false` | `true`/`false` | Bypass cache (1-hour TTL). Cannot combine with `async`. |
| `async` | `false` | `true`/`false` | Async submission; retrieve via Search Archive API. Cannot combine with `no_cache`. |
| `json_restrictor` | — | — | Limit response fields for smaller payloads |
| `zero_trace` | `false` | `true`/`false` | Enterprise only. Prevents storing search data on SerpApi servers. |

---

## Response Structure

### Root-Level Fields

| Field | Description |
|-------|-------------|
| `search_metadata` | `id`, `status`, `json_endpoint`, `created_at`, `processed_at`, `google_shopping_url`, `raw_html_file`, `total_time_taken` |
| `search_parameters` | Echo of all submitted parameters |
| `search_information` | `query_displayed`, `shopping_results_state` |
| `filters` | Refinement options (see below) |
| `carousel_filters` | Horizontal quick-filter chips |
| `inline_shopping_results` | Top-positioned sponsored product cards |
| `shopping_results` | Main product listing array |
| `categorized_shopping_results` | Products grouped by category |
| `serpapi_pagination` | `next` link for next page |

---

### `shopping_results` Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Result position |
| `title` | string | Product name |
| `product_id` | string | Google product ID |
| `product_link` | string | Google Shopping product page URL |
| `immersive_product_page_token` | string | Token for immersive product page |
| `serpapi_immersive_product_api` | string | SerpApi link for immersive product data |
| `source` | string | Retailer name |
| `source_icon` | string | Retailer logo URL |
| `multiple_sources` | boolean | Whether multiple sellers offer this product |
| `price` | string | Formatted price string |
| `extracted_price` | number | Numeric price value |
| `old_price` | string | Original price before discount (optional) |
| `extracted_old_price` | number | Numeric original price (optional) |
| `rating` | number | Average rating (decimal) |
| `reviews` | integer | Number of reviews |
| `snippet` | string | Product description snippet (optional) |
| `extensions` | string[] | Additional attributes (e.g. "Free shipping", "Sale") |
| `thumbnail` | string | Primary image URL |
| `thumbnails` | string[] | Additional image URLs |
| `serpapi_thumbnails` | string[] | SerpApi-hosted thumbnail URLs |
| `delivery` | string | Shipping/availability info |

---

### `inline_shopping_results` Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Result position |
| `block_position` | string | Position within block |
| `title` | string | Product name |
| `price` | string | Formatted price |
| `extracted_price` | number | Numeric price |
| `link` | string | Product URL |
| `tracking_link` | string | Tracking URL |
| `source` | string | Retailer name |
| `rating` | number | Average rating |
| `reviews` | integer | Review count |
| `thumbnail` | string | Image URL |
| `serpapi_thumbnail` | string | SerpApi-hosted thumbnail |

---

### `categorized_shopping_results` Structure

```json
{
  "title": "Category Name",
  "shopping_results": [
    { "...same fields as shopping_results...", "tag": "string", "delivery": "string" }
  ]
}
```

---

### `filters` Structure

Used to discover available refinements and their `shoprs` tokens for follow-up requests.

```json
{
  "type": "filter type label",
  "input_type": "select|range|...",
  "options": [
    {
      "text": "Option Label",
      "shoprs": "<encoded filter token>",
      "serpapi_link": "https://serpapi.com/search?..."
    }
  ]
}
```

---

### `carousel_filters` Structure

Horizontal scrollable filter chips.

```json
{
  "text": "Filter Label",
  "shoprs": "<encoded filter token>",
  "serpapi_link": "https://serpapi.com/search?...",
  "input_type": "carousel"
}
```

---

## Notes

- **Dynamic filters**: Available `filters` and `carousel_filters` vary per query. Always read them from the response to discover applicable refinements for a given search.
- **`shoprs` tokens**: The primary mechanism for applying category-specific filters (brand, size, colour, etc.). Extract from response filters and pass back as `shoprs` parameter.
- **Pagination**: Prefer `serpapi_pagination.next` over manual `start` offsets for reliability with the new layout.
