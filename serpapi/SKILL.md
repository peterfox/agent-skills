---
name: serpapi
description: Search the web and e-commerce platforms using the SerpApi API. Use when the user wants to search Google, Google Shopping, Google Jobs, eBay, or Amazon via SerpApi. Triggers on phrases like "search Google for...", "find products on eBay", "search Amazon for...", "find jobs on Google", "Google Shopping results for...", "use SerpApi to...", "search with SerpApi", "look up a product on Amazon", "find eBay listings for...", "search Amazon listings for...".
---

# SerpApi

Use the SerpApi REST API (via WebFetch) to retrieve structured search results from Google, Google Shopping, Google Jobs, eBay, and Amazon.

**Base endpoint**: `https://serpapi.com/search`
**Authentication**: Pass `api_key` as a query parameter on every request.

## Engines

| Engine | `engine` value | Reference |
|--------|---------------|-----------|
| Google Search | `google` | [references/google-search-api.md](references/google-search-api.md) |
| Google Shopping | `google_shopping` | [references/google-shopping-api.md](references/google-shopping-api.md) |
| Google Jobs | `google_jobs` | [references/google-jobs-api.md](references/google-jobs-api.md) |
| Google Immersive Product | `google_immersive_product` | [references/google-immersive-product-api.md](references/google-immersive-product-api.md) |
| eBay | `ebay` | [references/ebay-api.md](references/ebay-api.md) |
| Amazon Search | `amazon` | [references/amazon-search-api.md](references/amazon-search-api.md) |
| Amazon Product | `amazon_product` | [references/amazon-product-api.md](references/amazon-product-api.md) |

Read the relevant reference file before constructing any request.

## Key Patterns

### Chaining APIs
- **Google Shopping → Immersive Product**: A `shopping_results` item's `immersive_product_page_token` is the `page_token` for `google_immersive_product`.
- **Amazon search → Product detail**: A `organic_results` item's `serpapi_link` links directly to `amazon_product` for full product details, or use the `asin` manually.

### Filters from responses
- **Google Shopping**: `shoprs` tokens for category-specific filters (brand, colour, size, etc.) come from `filters[].options[].shoprs` or `carousel_filters[].shoprs` in the response — never construct them manually.
- **Google Jobs**: `uds` filter tokens come from `filters` in the response. `chips` and `ltype` are deprecated; use `uds` instead.
- **Google Jobs pagination**: `start` is discontinued — use `next_page_token` from `serpapi_pagination`.

### Presenting results
- Always show prices with currency and `extracted_price` for computation.
- For job listings: show `title`, `company_name`, `location`, `via`, and key `detected_extensions` fields (schedule type, remote, salary).
- For product results: show `title`, `price`, `rating`, `reviews`, and `source`/`seller`.
- For eBay: distinguish `sponsored` listings clearly.
