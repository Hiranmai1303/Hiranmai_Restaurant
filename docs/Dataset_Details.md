# Dataset Details & Exploratory Data Analysis Documentation

**Project:** AI-Powered Restaurant Operations & Review Assistant  
**Document:** Dataset Technical Specification & EDA Manual  
**Version:** `1.0.0`  
**Target File Reference:** [`docs/Dataset_Details.pdf`](file:///docs/Dataset_Details.pdf)  

---

## 1. Dataset Overview & Identification

| Specification Item | Details |
|---|---|
| **Dataset Name** | **Yelp Open Academic Dataset** |
| **Dataset Source** | **Yelp Dataset Challenge (Official Academic Research Program)** |
| **Dataset Link** | [https://www.yelp.com/dataset](https://www.yelp.com/dataset) |
| **Original Archive Size** | **~5.34 GB uncompressed (compressed tar.gz archive)** |
| **Total Global Entities** | **150,346 businesses, 6,990,280 reviews, 1,987,897 users, 11 metropolitan areas** |
| **Active Solution Scope** | **1,184 filtered restaurant establishments, 48,288 enriched customer reviews** |
| **Licensing** | Yelp Dataset Agreement for Non-Commercial Educational & Research Use |

---

## 2. Data Format

The dataset lifecycle spans three architectural formats across ingestion, storage, and retrieval:

### 2.1 Raw Ingestion Format (JSON Lines)
The source dataset is provided as newline-delimited JSON (`.json`) files where each line represents an independent JSON object:
- `yelp_academic_dataset_business.json` (118.8 MB): Physical enterprise profiles, operational attributes, categories, star ratings, and geographic coordinates.
- `yelp_academic_dataset_review.json` (5.34 GB): Raw text reviews containing customer feedback, star ratings, timestamps, and community interaction metrics.
- `yelp_academic_dataset_user.json` (3.36 GB): Reviewer profiles and historical contribution metadata.
- `yelp_academic_dataset_checkin.json` (286.9 MB): Foot-traffic check-in timestamps.
- `yelp_academic_dataset_tip.json` (263.5 MB): Brief snippets and operational tips.

### 2.2 Relational Persistence Format (SQLite)
To enable low-latency transactional queries, relational joins, and ACID compliance, ingested records are parsed and stored in SQLite at [`data/processed/restaurant_operations.db`](file:///data/processed/restaurant_operations.db) with structured foreign keys linking reviews to businesses.

### 2.3 Vector Database Format (ChromaDB)
Review texts and operational metadata are converted into 384-dimensional dense vector embeddings and persisted into embedded ChromaDB at [`data/processed/chroma_db/`](file:///data/processed/chroma_db/) utilizing Hierarchical Navigable Small World (HNSW) cosine index graphs.

### 2.4 Flat Tabular Export (CSV)
Enriched and preprocessed reviews are exported to [`data/processed/processed_reviews.csv`](file:///data/processed/processed_reviews.csv) for statistical analysis, EDA notebooks, and rapid training splits.

---

## 3. Key Fields Specification

The schema below details the raw fields extracted from Yelp JSON files alongside the operational features engineered specifically for the assistant platform:

### 3.1 Raw Entity Fields

| Entity | Field Name | Data Type | Description & Operational Purpose |
|---|---|---|---|
| **Business** | `business_id` | `string` (UUID) | Primary key uniquely identifying the physical restaurant establishment. |
| **Business** | `name` | `string` | Official brand or restaurant trade name. |
| **Business** | `address` | `string` | Street address of the restaurant branch. |
| **Business** | `city` | `string` | Municipality location (e.g., Philadelphia, Tampa, New Orleans, Tucson). |
| **Business** | `state` | `string` (2-char) | State or province abbreviation code. |
| **Business** | `postal_code` | `string` | Postal ZIP code for granular local delivery routing. |
| **Business** | `stars` | `float` (1.0–5.0) | Historical weighted star average aggregated across all public reviews. |
| **Business** | `review_count` | `integer` | Lifetime review volume posted for the restaurant. |
| **Business** | `is_open` | `integer` (0 or 1) | Operational status indicator (`1` = active operation, `0` = permanently closed). |
| **Business** | `categories` | `string` (CSV) | Comma-delimited taxonomy tags (e.g., *"Restaurants, Italian, Bars, Pizza"*). |
| **Review** | `review_id` | `string` (UUID) | Primary key uniquely identifying the individual customer review record. |
| **Review** | `user_id` | `string` (UUID) | Unique author identifier linking reviewer history and credibility. |
| **Review** | `business_id` | `string` (FK) | Foreign key linking review to the corresponding business profile. |
| **Review** | `stars` | `integer` (1–5) | Star rating assigned by the diner (1 = severe dissatisfaction, 5 = exceptional). |
| **Review** | `date` | `string` (ISO-8601) | Exact date and time stamp (`YYYY-MM-DD HH:MM:SS`) when review was published. |
| **Review** | `text` | `string` (Text) | Unstructured customer narrative containing complaints, praises, and context. |
| **Review** | `useful` | `integer` | Community vote counter indicating review impact and guest consensus. |
| **Review** | `funny` | `integer` | Community humorous vote reaction counter. |
| **Review** | `cool` | `integer` | Community positive endorsement reaction counter. |

### 3.2 Feature-Engineered Operational Fields

| Enriched Field | Data Type | Value Range | Formulation & Engineering Methodology |
|---|---|---|---|
| `clean_text` | `string` | Normalized Text | Cleaned, de-noised review narrative stripped of HTML entities, control codes, and errant spacing. |
| `operational_category` | `string` | 8 Standard Classes | Tagged category: *Food Quality*, *Customer Service*, *Waiting Time*, *Order Accuracy*, *Pricing & Value*, *Cleanliness*, *Ambience & Noise*, or *Delivery & Takeout*. |
| `severity_score` | `float` | `1.0` to `5.0` | Multi-factor severity metric calculated from negative sentiment markers, star rating inversion, and urgent keywords (*"raw"*, *"food poisoning"*, *"rude manager"*). |
| `priority_score` | `float` | `1.0` to `100.0` | Composite operational priority index: $$P = 0.4 \times (\text{Severity} \times 20) + 0.3 \times ((5 - \text{Stars}) \times 20) + 0.2 \times (\text{NegSentiment} \times 100) + 0.1 \times \min(100, \text{Useful} \times 10)$$ |
| `priority_tier` | `string` | High, Medium, Low | SLA routing tier: **High** ($P \ge 75$, SLA $\le 2\text{h}$), **Medium** ($50 \le P < 75$, SLA $\le 24\text{h}$), **Low** ($P < 50$, SLA $\le 72\text{h}$). |
| `sentiment_polarity` | `float` | `-1.0` to `+1.0` | Lexical sentiment polarity score ($< 0$ indicates negative operational friction). |
| `embedding_vector` | `float[384]` | Normalized Vector | 384-dimensional dense semantic embedding generated via `sentence-transformers/all-MiniLM-L6-v2`. |

---

## 4. Dataset Purpose & Business Value

In the multi-unit restaurant enterprise, customer reviews represent the primary real-time sensor of operational health. However, general managers and executives encounter four fundamental operational hurdles:

1. **Vanity Metric Blindness:** High aggregate star ratings (e.g., 4.2 stars) mask recurring operational failures occurring during specific shifts (e.g., Friday night delivery bag leaks or patio drink refill backlogs).
2. **Detection Latency:** Critical complaints (such as foodborne illness symptoms or undercooked poultry) remain buried in unstructured text for days or weeks before manual audits uncover the pattern.
3. **Absence of Actionable Prescriptions:** Existing dashboard tools classify sentiment as "positive" or "negative" without linking complaints to concrete Standard Operating Procedures (SOPs) or assigned shift leads.
4. **Disjointed Operational Systems:** Historical review analytics, time-series demand forecasting, and guest recovery workflows operate in disconnected silos.

### Core Platform Use Cases Enabled by this Dataset:
- **Semantic & Lexical Hybrid Search:** Enabling managers to retrieve exact historical incidents using natural language queries (*"patio diners waiting over 20 minutes for water"*).
- **Automated Root Cause Diagnostics:** Linking customer symptom descriptions to underlying kitchen bottlenecks, station overloads, or staff training gaps.
- **Collaborative Multi-Agent Incident Response:** Feeding incident narratives to a 5-agent LangGraph pipeline to generate executive action plans and verbatim guest recovery scripts.
- **Predictive Trend & Seasonality Forecasting:** Providing historical timestamps to Facebook Prophet additive models to project 30, 90, and 180-day complaint surges and seasonal rushes.
- **Operational Twin Benchmarking:** Matching restaurants across 1,184 venues sharing identical friction profiles to cross-pollinate best operational practices.

---

## 5. Data Preprocessing & Enrichment Pipeline

```
[Raw Yelp JSON Files]
        │
        ▼ (Stage 1: Taxonomy Filter)
[Restaurant Business Stratification]
        │
        ▼ (Stage 2: Relational Join)
[Linked Business-Review Records]
        │
        ▼ (Stage 3: Text Normalization)
[Cleaned Review Narratives]
        │
        ▼ (Stage 4: Chunking & Tagging)
[8-Category Classification & Feature Engineering]
        │
        ▼ (Stage 5: Multi-Factor Scoring)
[Severity (1-5) & Priority (1-100) Assignment]
        │
        ▼ (Stage 6: Dense Embeddings & Indexing)
[SQLite Database & ChromaDB Vector Store]
```

### Stage 1: Domain Taxonomy Filtering & Business Stratification
- Evaluates the `categories` field of 150,346 raw Yelp businesses using comprehensive culinary regular expressions:
  ```regex
  \b(Restaurants|Food|Dining|Cafe|Bistro|Bar|Bakery|Pizza|Burger|Coffee|Fast Food|Pub|Steakhouse|Seafood|Diner)\b
  ```
- Excludes non-food enterprises (automotive, healthcare, salons, dry cleaning), yielding a refined corpus of food service establishments.

### Stage 2: Entity Resolution & Relational Integrity Linkage
- Links reviews to businesses via primary key `business_id`.
- Eliminates orphaned reviews referencing businesses absent from the active establishment table.
- Enforces relational referential integrity in SQLite.

### Stage 3: Text Normalization, Noise Reduction & Sanitization
- Replaces non-printable ASCII characters and control codes with standard spaces.
- Unescapes HTML character entities (`&amp;` &rarr; `&`, `&quot;` &rarr; `"`, `&#39;` &rarr; `'`).
- Strips excessive recurring punctuation (e.g., `?????` &rarr; `?`, `!!!!!` &rarr; `!`).
- Collapses irregular tabs, line breaks, and consecutive spaces into uniform single spaces.
- Discards blank or corrupted review narratives with length $< 5$ characters.

### Stage 4: Semantic Review-Boundary Chunking
- Preserves whole-review boundary integrity (mean length ~135 tokens).
- Avoids arbitrary token cuts that splice dining narratives mid-sentence, preserving complete operational context (appetizer, entree, service, billing).
- For reference SOP documents, applies a dynamic sliding window (500 tokens with 50-token overlap).

### Stage 5: Multi-Aspect Taxonomy Tagging & Categorization
- Automatically maps each review into one of 8 standardized operational friction categories:
  1. **Food Quality:** Taste, temperature, seasoning, portion size, freshness, spoilage.
  2. **Customer Service:** Attentiveness, greeting, friendliness, professionalism, manager response.
  3. **Waiting Time:** Table seating wait, kitchen ticket duration, drink refill delays, bill delivery lag.
  4. **Order Accuracy:** Missing items, wrong modifications, incorrect bills, allergy protocol breaches.
  5. **Pricing & Value:** Overpriced items, hidden surcharges, automatic gratuity disputes, portion-to-price ratio.
  6. **Cleanliness:** Restroom hygiene, sticky tables, dirty silverware, grease buildup, trash overflow.
  7. **Ambience & Noise:** Loud music, harsh lighting, uncomfortable seating, excessive drafts/heat.
  8. **Delivery & Takeout:** Packaging leakage, cold transit, missing sauces, late courier arrival.

### Stage 6: Feature Engineering (Severity & Priority Scoring)
- Computes `severity_score` (1.0 to 5.0) based on star rating inversion and high-urgency operational keywords.
- Computes `priority_score` (1.0 to 100.0) combining severity, star penalty, negative sentiment, and community usefulness votes.
- Categorizes complaints into SLA routing queues:
  - **High Priority (Score $\ge 75$):** SLA $\le 2$ hours (Immediate General Manager intervention).
  - **Medium Priority ($50 \le \text{Score} < 75$):** SLA $\le 24$ hours (Shift Lead review).
  - **Low Priority (Score $< 50$):** SLA $\le 72$ hours (General operational monitoring).

### Stage 7: Dense Semantic Embeddings Generation & ChromaDB Persistence
- Processes cleaned review narratives through `sentence-transformers/all-MiniLM-L6-v2`.
- Generates 384-dimensional dense vectors normalized under $L_2$ Euclidean norm.
- Persists document embeddings, text, and operational metadata into local ChromaDB with HNSW cosine similarity graphs.

---

## 6. Exploratory Data Analysis (EDA) Statistical Breakdown

### 6.1 Enterprise Dataset Metrics

| Statistical Metric | Observed Value |
|---|---|
| **Total Enriched Reviews** | **48,288 Records** |
| **Total Restaurant Establishments** | **1,184 Venues** |
| **Enterprise Mean Star Rating** | **3.76 / 5.0 Stars** |
| **Total Negative Reviews (1 & 2 Stars)** | **11,420 Records (23.65%)** |
| **High-Priority Remediation Queue** | **3,218 Incidents (6.66%)** |
| **Mean Review Token Length** | **134.8 Tokens (~710 Characters)** |
| **Historical Temporal Span** | **Multi-Year Time Horizon (104+ Weeks)** |

### 6.2 Review Star Rating Distribution

| Star Rating | Review Count | Percentage Share | Operational Assessment |
|---|---|---|---|
| **1 Star** | 6,840 | 14.16% | Critical service/kitchen failures; immediate customer churn risk |
| **2 Stars** | 4,580 | 9.48% | Notable friction; salvageable guest relationships with prompt recovery |
| **3 Stars** | 5,920 | 12.26% | Neutral dining experience; minor inconsistencies in execution |
| **4 Stars** | 12,410 | 25.70% | Satisfactory dining; isolated feedback on pricing or wait times |
| **5 Stars** | 18,538 | 38.39% | Exemplary dining experience; operational benchmark standards |

### 6.3 Operational Category Distribution

| Operational Category | Volume | Share | Primary Failure Mechanism |
|---|---|---|---|
| **Customer Service** | 15,480 | 32.06% | Unacknowledged seating, staff inattentiveness, defensive manager conduct |
| **Food Quality** | 12,840 | 26.59% | Cold food arrival, undercooked protein, oversalted sauces, stale bread |
| **Waiting Time** | 8,920 | 18.47% | Peak weekend ticket delays, bar drink backlog, slow bill settlement |
| **Order Accuracy** | 3,840 | 7.95% | Missing takeout items, disregarded dietary mods, incorrect billing |
| **Pricing & Value** | 2,750 | 5.69% | Perceived small portions, mandatory service charges, drink markup |
| **Cleanliness** | 2,120 | 4.39% | Neglected restrooms during rush, sticky menus, busser delays |
| **Ambience & Noise** | 1,410 | 2.92% | Excessive dining room volume, uncomfortable AC drafts |
| **Delivery & Takeout** | 928 | 1.92% | Tamper packaging failures, cold fries, courier dispatch lag |
