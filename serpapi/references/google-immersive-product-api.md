# SerpAPI Google Immersive Product API Reference

Source: https://serpapi.com/google-immersive-product-api

Retrieves detailed product information from Google's immersive product popup — pricing, store listings, reviews, critic ratings, insights, videos, and discussions.

> **Entry point**: `page_token` values are found in `shopping_results[].immersive_product_page_token` from the Google Shopping API, or in `serpapi_immersive_product_api` links.

---

## Required Parameters

| Parameter | Value |
|-----------|-------|
| `engine` | `google_immersive_product` |
| `page_token` | Encoded token from a Shopping API result's `immersive_product_page_token` field |
| `api_key` | Your SerpApi private key |

---

## Optional Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `more_stores` | disabled | `1` or `true` to return up to 13 stores (default returns 3–5) |
| `next_page_token` | — | Pagination token for additional store results. Obtained from `stores_next_page_token` in the response. |
| `no_cache` | `false` | Bypass 1-hour cache. Cached searches are free. Cannot combine with `async`. |
| `async` | `false` | Async submission; retrieve via Search Archive API. Cannot combine with `no_cache`. |
| `json_restrictor` | — | Limit response fields for smaller payloads |
| `zero_trace` | `false` | Enterprise only. Prevents storing search data on SerpApi servers. |
| `output` | `json` | `json` or `html`. HTML response includes a `prettify_html_file` link. |

---

## Response Structure

### Root-Level Fields

| Field | Description |
|-------|-------------|
| `search_metadata` | `id`, `status`, `json_endpoint`, `created_at`, `processed_at`, `google_immersive_product_url`, `raw_html_file`, `prettify_html_file`, `total_time_taken` |
| `search_parameters` | Echo of submitted parameters |
| `product_results` | Main product data container (see below) |
| `related_searches` | Array of suggested follow-up queries |

---

### `product_results` Fields

#### Basic Info

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Product name |
| `brand` | string | Manufacturer name |
| `rating` | float | Average rating (0–5) |
| `reviews` | integer | Total review count |
| `price_range` | string | e.g., `"$1,797–$2,200"` |
| `thumbnails` | string[] | Product image URLs |

---

#### `critic_ratings[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Publication name |
| `rating` | string | e.g., `"5/5"` |
| `link` | string | URL to review |

---

#### `stores[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Retailer name |
| `logo` | string | Favicon URL |
| `link` | string | Product purchase URL |
| `title` | string | Product title at this retailer |
| `rating` | float | Store rating |
| `reviews` | integer | Store review count |
| `tag` | string | e.g., `"Best price"` |
| `payment_methods` | string | e.g., `"PayPal, Google Pay, Affirm accepted"` |
| `details_and_offers` | string[] | Shipping/return terms |
| `coupon` | string | Discount code (optional) |
| `discount` | string | Discount amount/percentage (optional) |
| `price` | string | Current price |
| `extracted_price` | number | Numeric price |
| `original_price` | string | Pre-discount price (optional) |
| `extracted_original_price` | number | Numeric original price (optional) |
| `shipping` | string | Shipping cost or `"Free"` |
| `shipping_extracted` | number | Numeric shipping cost |
| `estimated_tax` | string | Tax amount |
| `extracted_estimated_tax` | number | Numeric tax |
| `total` | string | Final amount due |
| `extracted_total` | number | Numeric total |
| `monthly_payment_duration` | integer | Instalment months (optional) |
| `installments_description` | string | Payment plan text (optional) |
| `down_payment` | string | Upfront amount (optional) |

`stores_next_page_token` — pagination token for fetching more stores (pass as `next_page_token`).

---

#### `about_the_product`

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Manufacturer's product name |
| `link` | string | Manufacturer URL |
| `displayed_link` | string | e.g., `"lg.com"` |
| `icon` | string | Favicon URL |
| `description` | string | Full product description |
| `features[]` | object[] | `{ title, value }` — spec name/value pairs |

---

#### `top_insights[]`

Aggregated editorial content from reviews, forums, and video sources.

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Section heading |
| `subtitle` | string | Optional subheading |
| `items[]` | object[] | See below |

Each `items[]` entry:

| Field | Type | Description |
|-------|------|-------------|
| `key_point` | string | Summary sentence |
| `snippet` | string | Extracted quote |
| `pros` | string[] | Benefits list |
| `cons` | string[] | Limitations list |
| `source` | string | Origin (e.g., `"RTINGS.com"`) |
| `title` | string | Source article title |
| `link` | string | Source URL |
| `icon` | string | Source icon URL |
| `thumbnail` | string | Image URL |
| `timestamp` | string | Video position in `HH:MM` format |
| `user` | string | Commenter name (forum sources) |
| `date` | string | Posting date |

---

#### `ratings[]` — Star Distribution

| Field | Type | Description |
|-------|------|-------------|
| `stars` | integer | Star level (1–5) |
| `amount` | integer | Number of ratings at this level |

---

#### `user_reviews[]`

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Review headline |
| `text` | string | Full review body |
| `user_name` | string | Reviewer username |
| `source` | string | Review platform |
| `rating` | float | Review rating |
| `date` | string | Posting date |
| `icon` | string | User avatar URL |
| `incentivized` | boolean | `true` if sponsored review |
| `images` | string[] | Review photo URLs |

`reviews_images[]` — array of customer photo URLs across all reviews.

---

#### `videos[]`

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Video name |
| `link` | string | Video URL |
| `source` | string | Platform (e.g., `"YouTube"`) |
| `channel` | string | Creator/channel name |
| `duration` | string | Length in `MM:SS` |
| `thumbnail` | string | Preview image URL |
| `preview` | string | Video preview clip URL |

---

#### `discussions_and_forums[]`

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Thread topic |
| `link` | string | Forum URL |
| `source` | string | Platform (e.g., `"Reddit"`) |
| `icon` | string | Site favicon |
| `date` | string | Thread creation date |
| `comments` | integer | Reply count |
| `items[]` | object[] | Individual posts/comments |

Each `items[]` entry:

| Field | Type | Description |
|-------|------|-------------|
| `snippet` | string | Excerpt from post |
| `link` | string | Direct comment URL |
| `top_answer` | boolean | Featured response indicator |
| `votes` | integer | Upvote count |

---

#### `variants[]` — Product Options

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Variant category (e.g., `"Screen Size"`) |
| `items[]` | object[] | See below |

Each `items[]` entry:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Option value (e.g., `"55″"`) |
| `selected` | boolean | Currently selected variant |
| `available` | boolean | In-stock status |
| `serpapi_link` | string | API endpoint to fetch this variant |

---

#### `more_options[]` — Related Product Variants

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Product variant name |
| `thumbnail` | string | Image URL |
| `price` | string | Current price |
| `extracted_price` | number | Numeric price |
| `original_price` | string | List price |
| `extracted_original_price` | number | Numeric list price |
| `rating` | float | Product rating |
| `reviews` | integer | Review count |
| `serpapi_link` | string | API endpoint for this variant |

---

## Notes

- **Token source**: `page_token` comes from `immersive_product_page_token` in Google Shopping API results.
- **Store pagination**: Use `stores_next_page_token` → `next_page_token` to get additional store listings beyond the default 3–5 (up to 13 with `more_stores=1`).
- **`top_insights`**: Content is aggregated from multiple source types (editorial reviews, forum posts, YouTube videos) — check `timestamp` to identify video-sourced items.
