# SerpAPI eBay Search API Reference

Source: https://serpapi.com/ebay-search-api

---

## Required Parameters

| Parameter | Value |
|-----------|-------|
| `engine` | `ebay` |
| `api_key` | Your SerpApi private key |

---

## Search Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `_nkw` | Optional* | Search query. Supports standard eBay search syntax. *Required unless `category_id` is specified. |
| `category_id` | Optional* | Numeric eBay category ID. Can be used without `_nkw`. Category IDs are found in the `categories` array of API responses. |

---

## Localization Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ebay_domain` | `ebay.com` | eBay domain to search. See [Supported Domains](#supported-domains). |
| `_salic` | — | Country code for location-based filtering. |

---

## Pagination Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `_pgn` | `1` | Any integer | Page number |
| `_ipg` | `50` | `25`, `50`, `100`, `200` | Results per page |

---

## Filters

### `show_only` — Listing Filters (case-sensitive, comma-separated)

| Value | Description |
|-------|-------------|
| `Complete` | Completed listings |
| `Sold` | Sold items only |
| `FR` | Free returns |
| `RPA` | Returns accepted |
| `AS` | Authorized seller |
| `Savings` | Deals and savings |
| `SaleItems` | Sale items |
| `Lots` | Listed as lots |
| `Charity` | Benefits charity |
| `AV` | Authenticity Guarantee |
| `FS` | Free shipping |
| `LPickup` | Local pickup |

Multiple values: `show_only=Sold,FS`

---

### `buying_format` — Listing Format (case-sensitive)

| Value | Description |
|-------|-------------|
| `Auction` | Auction listings only |
| `BIN` | Buy It Now only |
| `BO` | Best Offer accepted |

---

### `LH_ItemCondition` — Item Condition (join multiple with `|`)

| Value | Condition |
|-------|-----------|
| `1000` | New |
| `3000` | Used |
| `10` | Not Specified |

Example: `LH_ItemCondition=1000|3000`

---

### `LH_PrefLoc` — Preferred Location

| Value | Description |
|-------|-------------|
| `Domestic` | Items within same country |
| `Regional` | Regional items |
| `Worldwide` | All locations |

---

## Price Parameters

| Parameter | Description |
|-----------|-------------|
| `_udlo` | Minimum price (items priced above this value) |
| `_udhi` | Maximum price (items priced below this value) |

---

## Sort Options (`_sop`)

| `_sop` | Sort Order | Notes |
|--------|-----------|-------|
| `12` | Best Match (default) | |
| `1` | Time: ending soonest | |
| `10` | Time: newly listed | |
| `15` | Price + Shipping: lowest first | |
| `16` | Price + Shipping: highest first | |
| `7` | Distance: nearest first | |
| `2` | Price: lowest first | Not available on ebay.com |
| `3` | Price: highest first | Not available on ebay.com |
| `18` | Condition: new first | Not available on ebay.com, ebay.ca, ebay.de, others |
| `19` | Condition: used first | Not available on ebay.com, ebay.ca, ebay.de, others |

---

## Display Parameters

| Parameter | Options | Description |
|-----------|---------|-------------|
| `_dmd` | `Grid`, `List` | Results display layout |
| `_blrs` | `spell_auto_correct` | Disable query auto-correction |
| `_stpos` | ZIP/postal code | Filter shipping by geographic area |

---

## Output & Caching Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `output` | `json` | Response format: `json` or `html` |
| `no_cache` | `false` | `true` to bypass cache. Cannot combine with `async`. |
| `async` | `false` | `true` for async submission. Cannot combine with `no_cache`. Not on Ludicrous Speed accounts. |
| `json_restrictor` | — | Limit response fields for smaller payloads |
| `zero_trace` | `false` | Enterprise only. Prevents storing search data on SerpApi servers. |

---

## Supported Domains (`ebay_domain`)

| Domain | Country |
|--------|---------|
| `ebay.com` | United States (default) |
| `ebay.co.uk` | United Kingdom |
| `ebay.de` | Germany |
| `ebay.fr` | France |
| `ebay.it` | Italy |
| `ebay.es` | Spain |
| `ebay.ca` | Canada |
| `ebay.com.au` | Australia |
| `ebay.at` | Austria |
| `ebay.com.hk` | Hong Kong |
| `ebay.ie` | Ireland |
| `ebay.com.my` | Malaysia |
| `ebay.nl` | Netherlands |
| `ebay.pl` | Poland |
| `ebay.com.sg` | Singapore |
| `ebay.ch` | Switzerland |

---

## Response Structure

### Root-Level Fields

| Field | Description |
|-------|-------------|
| `search_metadata` | Request tracking: `id`, `status`, `json_endpoint`, `created_at`, `processed_at`, `ebay_url`, `raw_html_file`, `total_time_taken` |
| `search_parameters` | Echo of submitted parameters |
| `search_information` | `organic_results_state`, `total_results`, `query_displayed` |
| `organic_results` | Array of listing objects |
| `categories` | Subcategory options with names and IDs |
| `related_searches` | Suggested alternative queries with links |
| `pagination` | eBay and SerpApi pagination with next/previous links |
| `deals` | Curated deal listings |
| `best_selling` | Best-selling product listings |

### `organic_results` Item Fields

| Field | Type | Description |
|-------|------|-------------|
| `sponsored` | boolean | Whether listing is promoted |
| `title` | string | Item name |
| `link` | string | Product URL |
| `product_id` | string | eBay item ID |
| `condition` | string | e.g. "Brand New", "Pre-Owned" |
| `price` | object | `raw` (string) and `extracted` (number) |
| `shipping` | string | Delivery information |
| `returns` | string | Return policy |
| `thumbnail` | string | Image URL |
| `seller` | object | `username`, `reviews` count, `positive_feedback` percentage |
| `promotion` | string | Discount messaging |
| `rating` | number | Customer rating (when available) |
| `reviews` | number | Review count (when available) |
| `top_rated` | boolean | Top-rated seller/listing indicator |
| `watchers` | number | Number of watchers |
