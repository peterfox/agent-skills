# SerpAPI Amazon Product API Reference

Source: https://serpapi.com/amazon-product-api

Retrieves detailed product information for a specific Amazon product by ASIN.

---

## Required Parameters

| Parameter | Value |
|-----------|-------|
| `engine` | `amazon_product` |
| `api_key` | Your SerpApi private key |

---

## Search Parameters

| Parameter | Description |
|-----------|-------------|
| `asin` | Amazon Standard Identification Number for the product to look up |

---

## Localization Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `amazon_domain` | `amazon.com` | Amazon domain to use. See [Supported Domains](#supported-domains). |
| `language` | — | Locale in `<language>_<REGION>` format (e.g., `en_US`, `es_US`, `ja_JP`) |

---

## Filter Parameters

| Parameter | Description |
|-----------|-------------|
| `delivery_zip` | ZIP/postal code to filter shipping options by area |
| `shipping_location` | Country code to filter shipping by region |
| `other_sellers` | Include marketplace results from alternative vendors |

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
| `product_results` | Core product data (see below) |
| `purchase_options` | Pricing variants (one-time purchase, Subscribe & Save) |
| `item_ingredients` | Ingredient list array |
| `item_specifications` | Dynamic product attribute key-value pairs |
| `about_item` | Feature descriptions array |
| `product_description` | Rich marketing content with images and features |
| `product_details` | Manufacturer info, dimensions, UPC, bestseller rank |
| `bought_together` | Frequently purchased bundle items |
| `related_products` | Similar/recommended products |
| `sustainability_features` | Certifications and eco info |
| `reviews_information` | Review summary and individual reviews |
| `sponsored_brands` | Brand advertising sections |
| `other_sellers` | Marketplace alternatives with pricing |

---

### `product_results` Fields

| Field | Type | Description |
|-------|------|-------------|
| `asin` | string | Product identifier |
| `title` | string | Product name |
| `description` | string | Short description |
| `tags` | string[] | Product tags |
| `badges` | string[] | Labels (e.g., `"Amazon's Choice"`) |
| `brand` | string | Brand name |
| `link` | string | Product page URL |
| `link_clean` | string | URL without tracking parameters |
| `thumbnails` | string[] | Product image URLs |
| `rating` | float | Average rating (0–5) |
| `reviews` | integer | Review count |
| `bought_last_month` | string | e.g., `"1K+ bought in past month"` |
| `price` | string | Current price |
| `extracted_price` | float | Numeric price |
| `old_price` | string | Pre-discount price |
| `extracted_old_price` | float | Numeric original price |
| `discount` | string | Discount percentage |
| `price_unit` | string | Per-unit price |
| `extracted_price_unit` | float | Numeric per-unit price |
| `snap_ebt_eligible` | boolean | SNAP/EBT payment accepted |
| `delivery` | string[] | Delivery option descriptions |
| `stock` | string | Availability status |
| `variants` | object[] | Product variants (see below) |

---

### `variants[]`

```json
{
  "title": "Variant group name (e.g., 'Flavor', 'Size')",
  "items": [
    {
      "position": 1,
      "asin": "B000000000",
      "name": "Option name",
      "selected": true,
      "serpapi_link": "https://serpapi.com/search?..."
    }
  ]
}
```

---

### `purchase_options`

| Field | Description |
|-------|-------------|
| `buy_new` | One-time purchase: `caption`, `price`, `extracted_price`, `price_unit`, `delivery[]`, `stock` |
| `subscribe_and_save` | Subscription option with same fields plus subscription discount details |

---

### `product_details`

| Field | Type | Description |
|-------|------|-------------|
| `asin` | string | Product identifier |
| `upc` | string | Universal Product Code |
| `manufacturer` | string | Manufacturer name |
| `brand` | string | Brand name |
| `item_form` | string | Format (e.g., `"Ground"`) |
| `units` | string | Size measurement |
| `product_dimensions` | string | Physical dimensions |
| `best_sellers_rank` | object[] | `{ text, extracted_rank, link, link_text }` |
| `rating` | float | Average rating |
| `review` | integer | Review count |

---

### `item_specifications`

Dynamic key-value object. Keys vary by product category. Example fields:

| Field | Description |
|-------|-------------|
| `brand` | Brand name |
| `item_form` | Product form |
| `flavor` | Flavour variant |
| `caffeine_content_description` | Caffeine info |
| `roast_level` | Roast level |
| *(additional category-specific keys)* | Varies by product |

---

### `sustainability_features`

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Overview statement |
| `climate_pledge_friendly` | boolean | Climate Pledge Friendly certified |
| `learn_more_link` | string | Info URL |
| `features[]` | object[] | See below |

Each `features[]` entry:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Feature category |
| `text` | string | Feature description |
| `certified_by[]` | object[] | `{ name, logo, description, link }` |

---

### `other_sellers[]`

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Result position |
| `link` | string | Seller info URL |
| `price` | string | Formatted price |
| `extracted_price` | float | Numeric price |
| `price_unit` | string | Per-unit price |
| `extracted_price_unit` | float | Numeric per-unit price |
| `old_price` | string | Pre-discount price |
| `extracted_old_price` | float | Numeric original price |
| `discount` | string | Discount percentage |
| `rating` | float | Seller rating |
| `reviews` | integer | Seller review count |
| `delivery` | string[] | Delivery options |
| `notes` | string[] | Additional seller info |

---

### `related_products[]` / `bought_together[]`

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Result position |
| `asin` | string | Product identifier |
| `title` | string | Product name |
| `description` | string | Product summary |
| `link` | string | Product page URL |
| `link_clean` | string | URL without tracking |
| `serpapi_link` | string | SerpApi search URL |
| `thumbnail` | string | Image URL |
| `rating` | float | Star rating |
| `reviews` | integer | Review count |
| `price` | string | Current price |
| `extracted_price` | float | Numeric price |
| `price_unit` | string | Per-unit price |
| `extracted_price_unit` | float | Numeric per-unit price |
| `delivery` | string[] | Delivery options |
| `stock` | string | Availability (`bought_together` only) |
| `sponsored` | boolean | Sponsored listing (`related_products` only) |
| `prime` | boolean | Prime eligible (`related_products` only) |
| `badges` | string[] | Labels (`related_products` only) |
| `climate_pledge_friendly` | boolean | Eco cert flag (`related_products` only) |

---

### `reviews_information`

| Field | Description |
|-------|-------------|
| `summary` | Aggregated review text and sentiment insights by topic |
| `histogram` | Star rating distribution (5/4/3/2/1 star counts) |
| `authors_reviews[]` | Individual review objects (see below) |

Each `authors_reviews[]` entry:

| Field | Type | Description |
|-------|------|-------------|
| `position` | integer | Display order |
| `title` | string | Review headline |
| `text` | string | Full review body |
| `rating` | float | Star score |
| `date` | string | Publication date |
| `author` | string | Reviewer name |
| `author_link` | string | Reviewer profile URL |
| `author_image` | string | Reviewer avatar URL |
| `helpful_votes` | string | e.g., `"42 people found this helpful"` |
| `verified_purchase` | boolean | Verified purchase badge |
| `product` | object | `{ flavor_name, size, title, link }` — variant purchased |
| `images` | string[] | Review photo URLs |
| `video` | object | `{ link, thumbnail }` |

---

## Supported Domains (`amazon_domain`)

| Domain | Country |
|--------|---------|
| `amazon.com` | United States (default) |
| `amazon.co.uk` | United Kingdom |
| `amazon.de` | Germany |
| `amazon.fr` | France |
| `amazon.it` | Italy |
| `amazon.es` | Spain |
| `amazon.ca` | Canada |
| `amazon.co.jp` | Japan |
| `amazon.com.au` | Australia |
| `amazon.com.br` | Brazil |
| `amazon.in` | India |
| `amazon.nl` | Netherlands |
| `amazon.pl` | Poland |
| `amazon.se` | Sweden |
| `amazon.com.mx` | Mexico |
| `amazon.com.be` | Belgium |
| `amazon.cn` | China |
| `amazon.eg` | Egypt |
| `amazon.sa` | Saudi Arabia |
| `amazon.sg` | Singapore |
| `amazon.com.tr` | Turkey |
| `amazon.ae` | United Arab Emirates |
