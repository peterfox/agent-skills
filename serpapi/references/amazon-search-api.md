# SerpAPI Amazon Search API Reference

Source: https://serpapi.com/amazon-search-api

Searches Amazon and returns product listings, ads, filters, categories, and pagination.

---

## Required Parameters

| Parameter | Value |
|-----------|-------|
| `engine` | `amazon` |
| `api_key` | Your SerpApi private key |

---

## Search Parameters

| Parameter | Description |
|-----------|-------------|
| `k` | Search query — anything you'd type into Amazon's search box |
| `i` | Store/department for category-specific searches (e.g., `fashion`) |
| `node` | Category node ID for filtered results. Extract node IDs from Amazon category URLs. |

---

## Localization Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `amazon_domain` | `amazon.com` | Amazon domain to use. 22 domains supported — see [amazon-product-api.md](amazon-product-api.md#supported-domains). |
| `language` | — | Locale in `<language>_<REGION>` format (e.g., `en_US`, `es_US`, `ja_JP`) |

---

## Shipping Parameters

| Parameter | Description |
|-----------|-------------|
| `delivery_zip` | ZIP/postal code to filter shipping options by area |
| `shipping_location` | Country code to filter shipping by region |

---

## Filter Parameters

### `s` — Sort Order

| Value | Description |
|-------|-------------|
| `relevanceblender` | Featured (default) |
| `price-asc-rank` | Price: Low to High |
| `price-desc-rank` | Price: High to Low |
| `review-rank` | Avg. Customer Review |
| `date-desc-rank` | Newest Arrivals |
| `exact-aware-popularity-rank` | Best Sellers |

### `rh` — Attribute Filtering

Comma-separated `key:value` pairs. Values come from `filters[].options[].rh` in the response — never construct them manually.

Structure: `n:16318031,p_72:1248897011`

| Prefix | Meaning |
|--------|---------|
| `n:` | Category node |
| `p_72:` | Customer review rating |
| `p_n_cpf_eligible:` | Certification filter |
| *(additional `p_` keys)* | Product attribute filters |

### `dc`

Set to `true` to disable spelling auto-correction.

---

## Pagination

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | `1` | Page number |

---

## Device & Output Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `device` | `desktop` | `desktop`, `tablet`, `mobile` | Browser device type |
| `output` | `json` | `json`, `html` | Response format |
| `no_cache` | `false` | `true`/`false` | Bypass 1-hour cache. Cached searches are free. Cannot combine with `async`. |
| `async` | `false` | `true`/`false` | Async submission; retrieve via Search Archive API. Cannot combine with `no_cache`. |
| `json_restrictor` | — | — | Limit response fields for smaller payloads |
| `zero_trace` | `false` | `true`/`false` | Enterprise only. Prevents storing search data on SerpApi servers. |

---

## Response Structure

### Root-Level Fields

| Field | Description |
|-------|-------------|
| `search_metadata` | `id`, `status`, `json_endpoint`, `created_at`, `processed_at`, `raw_html_file`, `total_time_taken` |
| `search_parameters` | Echo of all submitted parameters |
| `search_information` | `total_results`, `query_displayed`, `store`, `page` |
| `organic_results` | Main product listings array |
| `product_ads` | Sponsored product listings with brand information |
| `featured_products` | "Recently bought and rated" sections |
| `sponsored_brands` | Brand showcase sections |
| `video_results` | Video content with associated products |
| `categories` | Browsable category navigation |
| `filters` | Refinement options |
| `related_searches` | Suggested alternative queries |
| `pagination` | Page navigation links |

---

### `organic_results` Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Result position |
| `asin` | string | Amazon product identifier |
| `sponsored` | boolean | Sponsored/promoted listing |
| `amazon_brand` | boolean | Amazon own-brand product |
| `brand` | string | Manufacturer/brand name |
| `title` | string | Product name |
| `link` | string | Full Amazon product URL |
| `link_clean` | string | Simplified product URL |
| `serpapi_link` | string | SerpApi endpoint for this product (use with `amazon_product` engine) |
| `thumbnail` | string | Product image URL |
| `rating` | float | Average rating (0–5) |
| `reviews` | integer | Review count |
| `bought_last_month` | string | e.g., `"1K+ bought in past month"` |
| `price` | string | Current price |
| `extracted_price` | float | Numeric price |
| `price_unit` | string | Per-unit price display |
| `extracted_price_unit` | float | Numeric per-unit price |
| `old_price` | string | Pre-discount price |
| `extracted_old_price` | float | Numeric original price |
| `save_with_coupon` | string | Coupon savings messaging |
| `snap_ebt_eligible` | boolean | SNAP/EBT eligible |
| `prime` | boolean | Prime shipping eligible |
| `amazon_fresh` | boolean | Available via Amazon Fresh |
| `whole_foods_market` | boolean | Available via Whole Foods |
| `shipping` | string | General shipping description |
| `delivery` | string[] | Delivery option descriptions |
| `stock` | string | Availability status |
| `offers` | string[] | Promotions, subscription discounts, seller info |
| `more_buying_choices` | string | Alternative seller pricing summary |
| `more_buying_choices_link` | string | Link to alternative sellers page |
| `tags` | string[] | Size/quantity descriptors |
| `badges` | string[] | e.g., `"Best Seller in Household"` |
| `customizable` | boolean | Supports personalisation options |
| `small_business` | boolean | Small business seller |
| `works_with_alexa` | boolean | Alexa compatible |
| `age_rating` | string | Recommended age range |
| `options` | string | Variant choices description |
| `options_link` | string | URL to variant selection page |
| `climate_pledge_friendly` | boolean | Climate Pledge Friendly certified |
| `top_rated` | boolean | Top-rated product indicator |

#### `variants` (nested)

```json
{
  "options": [
    { "position": 1, "asin": "B000000000", "title": "Option name", "link": "https://..." }
  ],
  "more_variants": "12",
  "more_variants_link": "https://..."
}
```

#### `specs` (nested)

Dynamic key-value object of technical specs. Example keys: `display_size`, `disk_size`, `connectivity`, `brand`.

#### `sustainability_features[]` (nested)

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Display order |
| `name` | string | Feature category |
| `snippet` | string | Brief description |
| `thumbnail` | string | Certification logo URL |
| `certified_by` | string | Certifying organisation name |
| `certified_info` | string | Detailed certification explanation |

#### `origin_country` (nested)

```json
{ "name": "Country name", "link": "https://...", "thumbnail": "https://..." }
```

---

### `filters` Structure

Used to discover `rh` tokens and other refinements. Always read from response.

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Display order |
| `name` | string | Filter label (e.g., `"Free Shipping by Amazon"`) |
| `description` | string | Optional explanation |
| `rh` | string | Refinement hash — pass as `rh` parameter |
| `url` | string | Direct Amazon filtered URL |
| `serpapi_url` | string | SerpApi equivalent URL |
| `used` | boolean | Whether this filter is currently active |

Common filter categories: `eligible_for_free_shipping`, `delivery_day`, `brands`, `customer_reviews`, price ranges.

---

### `categories[]`

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Display order |
| `name` | string | Category name |
| `link` | string | Amazon category URL |
| `node` | string | Category node ID (use as `node` parameter) |
| `serpapi_api` | string | Direct SerpApi endpoint for this category |

---

### `pagination`

| Field | Description |
|-------|-------------|
| `current` | Current page number |
| `next` | Next page URL |
| `other_pages` | Object mapping page numbers to URLs |

SerpApi provides a parallel `serpapi_pagination` object with identical structure using SerpApi endpoints.

---

## Notes

- **`rh` tokens**: Always obtain from `filters[].options[].rh` in the response — never construct manually.
- **`node` IDs**: Extract from Amazon category URLs or from `categories[].node` in the response.
- **`serpapi_link`** on organic results: Use this directly with the `amazon_product` engine to fetch full product details.
