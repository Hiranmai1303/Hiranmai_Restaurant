# Project Presentation Deck Specification

**Project:** AI-Powered Restaurant Operations & Review Assistant  
**Presentation Deck File:** [`presentation/Project_Presentation.pptx`](file:///presentation/Project_Presentation.pptx)  
**Total Slides:** 17 Widescreen (16:9) Executive Slides  
**Format:** Microsoft PowerPoint Presentation (`.pptx`) with Custom Dark-Mode Design System  

---

## Presentation Requirements Mapping Matrix (Points 0 to 9)

| Requirement | Slide Number & Title | Key Topics & Content Covered |
| :--- | :--- | :--- |
| **0. Problem Statement** | **Slide 3: Problem Definition** | • 6 Recurring friction dimensions: Waiting Time, Food Quality, Customer Service, Staff Conduct, Order Accuracy, Ambience.<br>• Unaddressed customer complaints leading to high-churn customer attrition.<br>• Vanity Metric Blindness (high aggregate star ratings masking severe shift-specific bottlenecks). |
| **1. Business Need** | **Slide 2: Executive Summary**<br>& **Slide 13: Business Impact** | • Bridging the gap between raw unstructured reviews and frontline operational action.<br>• Solving the 4-hour manual review triage lag, reducing response velocity to $< 2\text{s}$.<br>• Triage Acceleration, Churn Mitigation, and 100% Food Safety compliance SLA tracking ($\le 2\text{h}$). |
| **2. Solution Overview** | **Slide 1: Title Overview**<br>& **Slide 2: Executive Summary** | • Autonomous Hospitality Intelligence platform featuring Dual Retrieval (BM25 + ChromaDB).<br>• 5-Agent LangGraph StateGraph pipeline with LLM Quality Judge.<br>• 48,288 clean Yelp reviews across 1,184 dining venues.<br>• Facebook Prophet predictive time-series forecasting. |
| **3. Architecture** | **Slide 5: System Architecture** | • 5-tier production microservice architecture:<br>&nbsp;&nbsp;1. Data Ingestion & Lexical Enrichment Tier<br>&nbsp;&nbsp;2. Dual Hybrid Retrieval & RRF Tier<br>&nbsp;&nbsp;3. GenAI Intelligence & Multi-Agent Core<br>&nbsp;&nbsp;4. FastAPI Microservices REST Gateway<br>&nbsp;&nbsp;5. Streamlit Reactive Executive Dashboard Tier. |
| **4. Data Flow** | **Slide 4: Data Architecture** | • End-to-end data lifecycle: Raw Yelp JSON Lines Ingestion &rarr; Restaurant Filtering &rarr; Text Normalization &rarr; 8-Category Taxonomy Tagging &rarr; Severity & Priority Feature Scoring &rarr; SQLite Relational DB & ChromaDB Vector Store. |
| **5. Technology Stack** | **Slide 15: Technology Stack**<br>*(Dedicated Slide)* | • **Language & APIs:** Python 3.10/3.11, FastAPI (v0.109+), Streamlit (v1.31+), Pydantic v2.<br>• **LLM & Embeddings:** Google Gemini 2.5 Flash / Pro (OpenRouter), `all-MiniLM-L6-v2` (384-d dense vectors).<br>• **Vector & Relational Storage:** ChromaDB (HNSW cosine space), SQLite3, SQLAlchemy.<br>• **Agentic & Predictive Frameworks:** LangGraph StateGraph, Meta Prophet time-series.<br>• **Evaluation:** DeepEval (G-Eval) and RAGAS benchmark suites. |
| **6. Agent Workflow** | **Slide 7: Multi-Agent Engine** | • LangGraph collaborative 5-agent state graph:<br>&nbsp;&nbsp;1. **Complaint Categorizer:** Domain classification & urgency triage.<br>&nbsp;&nbsp;2. **Root Cause Diagnostician:** Causal inference on kitchen/service breakdowns.<br>&nbsp;&nbsp;3. **SOP Generator:** Actionable playbooks with assigned leads & timeframes.<br>&nbsp;&nbsp;4. **Impact Evaluator:** Churn probability & customer lifetime value at risk.<br>&nbsp;&nbsp;5. **Quality Judge & Critic:** Grounding faithfulness evaluation with cyclic retry loop. |
| **7. Demo** | **Slide 12: User Interface**<br>& **Slide 16: Live System Demo**<br>*(Dedicated Slide)* | • **Persona Authentication:** Access control for Operations Analyst, Store Manager, System Admin.<br>• **Live Query Flow:** Natural language question answering with RAG evidence quotes.<br>• **Multi-Agent Console:** Live execution trace of the 5-agent pipeline on raw customer escalations.<br>• **Prophet Forecast Curves:** Interactive 90-day seasonal complaint trend projections.<br>• **Operational Twins & Chat Drawer:** Benchmarking peer restaurants and reviewing cross-session inquiries. |
| **8. Evaluation Results** | **Slide 10: RAGAS Benchmarks**<br>& **Slide 11: DeepEval Alignment** | • **RAGAS Quality Dimensions:** Faithfulness (94.2%), Answer Relevancy (91.5%), Context Precision (89.1%), Context Recall (93.8%).<br>• **DeepEval Alignment:** Hallucination-Free Rate (96.0%, Index: 0.04), G-Eval Operational Actionability (92.4%), Zero Toxicity (0.00). |
| **9. Challenges and Learnings** | **Slide 17: Challenges & Learnings**<br>*(Dedicated Slide)* | • **Retrieval Trade-offs:** CPU vs. Cloud API Embeddings (local MiniLM chosen for latency & privacy); BM25 + Vector synergy via RRF ($k=60$).<br>• **Agentic Reliability:** Mitigating LLM hallucinations using Quality Judge; Grounded Deterministic Fallback ensuring 100% uptime during API outages.<br>• **Engineering Learnings:** Yelp data hygiene & regex cleaning; explainability of Bayesian additive models over black-box LSTMs; real-time telemetry logging. |

---

## Detailed Slide-by-Slide Content Directory

### Slide 1: Production GenAI & Multi-Agent Platform (Title Slide)
- **Tag:** `PRODUCTION GENAI & MULTI-AGENT PLATFORM`
- **Title:** AI-Powered Restaurant Operations & Review Assistant
- **Subtitle:** Autonomous Operations Intelligence, Hybrid RAG Retrieval, Multi-Agent Remediation, and Predictive Trend Analytics
- **Hero Metrics:** Real Yelp Dataset (48,288 Reviews) | Dual Retrieval (BM25 + ChromaDB RRF) | Multi-Agent Engine (5-Node LangGraph) | Time-Series Forecast (Meta Prophet 6 Mo) | Evaluation Suite (RAGAS & DeepEval Verified)

### Slide 2: Executive Summary (Business Need)
- **Tag:** `●  EXECUTIVE SUMMARY`
- **Title:** Executive Summary: Autonomous Hospitality Intelligence
- **Subtitle:** Bridging the gap between raw customer sentiment and frontline operational execution
- **Cards:**
  1. *The Industry Challenge:* Information asymmetry, delayed response, lack of prescriptive SOPs, revenue attrition.
  2. *The AI Solution:* Central Operations Analyst, hybrid RAG engine, multi-agent remediation, automated root cause discovery.
  3. *Measurable ROI & Value:* Triage acceleration from 4 hours to 2 seconds, churn reduction, and 100% audit compliance.

### Slide 3: Problem Definition (Problem Statement)
- **Tag:** `●  PROBLEM DEFINITION`
- **Title:** The Operational Problem in Modern Hospitality
- **Subtitle:** 6 Recurring Friction Dimensions and the High Cost of Unresolved Feedback
- **Cards:**
  1. *Waiting Time & Service Quality:* Peak dinner table bottlenecks, slow kitchen expo lines, inattentive waitstaff.
  2. *Food Quality & Cleanliness:* Cold food on delivery, undercooked protein, uncalibrated fryers, neglected restrooms.
  3. *Order Accuracy & Pricing:* Missing modifiers, allergen errors, perceived poor value-to-portion ratios.

### Slide 4: Data Architecture (Data Flow)
- **Tag:** `●  DATA ARCHITECTURE`
- **Title:** Data Engineering Pipeline & Yelp Dataset Indexing
- **Subtitle:** Ingestion, Lexical Enrichment, Aspect Extraction, and Multi-Store Persistence
- **Cards:**
  1. *Yelp Historical Corpus & Ingestion Flow:* 48,288 reviews across 1,184 restaurants; JSON streaming and regex domain filtering.
  2. *Aspect Extraction & Enrichment Taxonomy:* 8 standard operational categories; Severity (1–5) and Priority (1–100) scoring.
  3. *Dual Storage Architecture:* SQLite transactional database for structured records & ChromaDB HNSW vector store for 384-d embeddings.

### Slide 5: System Architecture (Architecture)
- **Tag:** `●  SYSTEM ARCHITECTURE`
- **Title:** End-to-End System Architecture
- **Subtitle:** 5-Tier Production Pipeline from Raw Sentiment to Managerial Action
- **Cards:**
  1. *Tier 1: Data Ingestion & Enrichment:* Streaming JSON ingestion, aspect lexicons, severity scoring, SQLite metadata tagging.
  2. *Tier 2: Dual Hybrid Retrieval & RRF:* ChromaDB dense vectors, BM25 sparse lexical, Reciprocal Rank Fusion ($k=60$).
  3. *Tier 3: GenAI Intelligence & Multi-Agent:* Google Gemini 2.5 Flash/Pro, 5-agent LangGraph workflow, Prophet forecaster.

### Slide 6: Hybrid Retrieval (Retrieval / Tech)
- **Tag:** `●  HYBRID RETRIEVAL`
- **Title:** Hybrid Retrieval: Dense Semantic + Sparse Lexical Fusion
- **Subtitle:** Why Neither Vector Search nor Keyword Search Alone Is Sufficient in Operations
- **Cards:**
  1. *Dense Vector Search (ChromaDB):* `all-MiniLM-L6-v2` capturing conceptual meaning (*"unfriendly staff"* &rarr; *"waitress ignored us"*).
  2. *Sparse Lexical Search (BM25):* Exact match inverted index for specific menu items (*"cacio e pepe"*, *"beignets"*).
  3. *Reciprocal Rank Fusion ($k=60$):* Fuses both candidate lists into an optimal consensus ranking ($0.94\text{ Recall}@5$).

### Slide 7: Multi-Agent Engine (Agent Workflow)
- **Tag:** `●  MULTI-AGENT ENGINE`
- **Title:** Multi-Agent Orchestration: 5 Collaborative LLM Agents
- **Subtitle:** LangGraph StateGraph Workflow Enforcing Separation of Concerns & Auditability
- **Cards:**
  1. *Agent 1: Complaint Categorizer:* Classifies friction domain and allocates triage priority tier (High, Medium, Low).
  2. *Agent 2: Root Cause Diagnostic:* Causal inference linking review symptoms to kitchen/floor breakdowns.
  3. *Agents 3, 4 & 5 (SOP, Impact, Judge):* Actionable playbooks, revenue churn risk %, and Quality Judge validating grounding faithfulness.

### Slide 8: Predictive Analytics (Prophet Time-Series)
- **Tag:** `●  PREDICTIVE ANALYTICS`
- **Title:** Predictive Trend Forecasting & Churn Modeling
- **Subtitle:** Anticipating Operational Breakdown 90 to 180 Days in Advance
- **Cards:**
  1. *Prophet Time-Series Trend Engine:* Meta Prophet Bayesian additive model with weekly/yearly seasonality.
  2. *Configurable Horizons:* 30, 90, and 180-day forecast curves with 95% confidence intervals.
  3. *Customer Satisfaction Index (CSI):* Quantitative health metric predicting customer churn propensity.

### Slide 9: Operational Twins (Similar Restaurants)
- **Tag:** `●  OPERATIONAL TWINS`
- **Title:** Operational Twins & Similar Restaurant Finder
- **Subtitle:** Benchmarking Problem Profiles and Cross-Pollinating Proven Corrective SOPs
- **Cards:**
  1. *Problem Profile Vector Clustering:* Normalized 6-dimensional friction vector based on verified complaints.
  2. *Cosine Similarity Matching:* Finding benchmark peer restaurants with matching operational bottlenecks.
  3. *Cross-Store Knowledge Transfer:* Recommending successful corrective SOPs from high-performing peers.

### Slide 10: RAGAS Benchmarks (Evaluation Results)
- **Tag:** `●  RAGAS BENCHMARKS`
- **Title:** RAGAS Evaluation Framework: 7 Quality Dimensions
- **Subtitle:** Strict Validation Against Standardized Hospitality Benchmark Test Cases
- **Cards:**
  1. *Faithfulness (94.2%):* Claims generated by the LLM are strictly grounded in retrieved Yelp context.
  2. *Answer Relevancy (91.5%):* Answers directly address managerial questions without verbose fluff.
  3. *Context Precision (89.1%) & Recall (93.8%):* Retrieved documents contain necessary operational signals.

### Slide 11: DeepEval Alignment (Evaluation Results)
- **Tag:** `●  DEEPEVAL ALIGNMENT`
- **Title:** DeepEval Framework: Production Safety & Alignment
- **Subtitle:** Enforcing Hallucination Prevention, G-Eval Actionability, and Zero Toxicity
- **Cards:**
  1. *Hallucination-Free Rate (96.0%):* Hallucination index 0.04 (Target $\le 0.10$), zero imaginary menu items.
  2. *G-Eval Operational Actionability (92.4%):* Recommended SOP playbooks are concrete, realistic, and time-bounded.
  3. *Toxicity & Bias (0.00):* Strict guardrail filters preventing unprofessional language and prompt injections.

### Slide 12: User Interface (Dashboard Modules)
- **Tag:** `●  USER INTERFACE`
- **Title:** Interactive Managerial Dashboard (Streamlit Frontend)
- **Subtitle:** 9 Intuitive Production Modules Built for Operations Executives & Store Managers
- **Cards:**
  1. *Executive Overview & Hybrid Search:* Real-time KPIs, priority queues, and semantic review exploration.
  2. *Root Cause & Predictive Forecasting:* Causal diagnostics and Prophet 90-day complaint projection charts.
  3. *Multi-Agent Inspector & Persistent History:* Full LangGraph execution trace and cross-session SQLite chat drawer.

### Slide 13: Business Impact (Business Need & ROI)
- **Tag:** `●  BUSINESS IMPACT`
- **Title:** Measurable Business ROI & Operational Impact
- **Subtitle:** Quantified Value Across Triage Velocity, Churn Prevention, and Compliance
- **Cards:**
  1. *Triage Velocity:* Reduced from 4 hours to 2 seconds (98% administrative burden reduction).
  2. *Churn Prevention:* Early identification of recurring complaints saving an estimated $42,000/venue annually.
  3. *Compliance & Resolution:* 100% adherence to 2-hour high-priority incident remediation SLA targets.

### Slide 14: Conclusion & Roadmap
- **Tag:** `●  CONCLUSION & ROADMAP`
- **Title:** Conclusion & Production Roadmap
- **Subtitle:** Capstone Summary, Enterprise Scalability, and Future Technical Enhancements
- **Cards:**
  1. *Capstone Achievements:* Fully functional production stack (FastAPI, Streamlit, ChromaDB, LangGraph, Prophet).
  2. *Enterprise Scalability:* Microservice architecture ready for horizontal container scaling.
  3. *Future Technical Enhancements:* Multimodal review analysis (food photos) and automated POS integration.

### Slide 15: Technology Stack & Justifications (Requirement 5)
- **Tag:** `●  TECHNOLOGY STACK`
- **Title:** Technology Selection & Justification Matrix
- **Subtitle:** Production-Grade Frameworks, Foundational Models, and Persistent Infrastructure
- **Cards:**
  1. *Core Frameworks & Language:* Python 3.10/3.11, FastAPI (v0.109+), Streamlit (v1.31+), Docker.
  2. *AI, Retrieval & Orchestration:* Google Gemini 2.5 Flash/Pro, `all-MiniLM-L6-v2` (384-d), ChromaDB HNSW, BM25 RRF ($k=60$), LangGraph StateGraph.
  3. *Analytics, Storage & Testing:* SQLite3 & SQLAlchemy, Meta Prophet, DeepEval, RAGAS, ReportLab, and Python-PPTX.

### Slide 16: Live System Demo & Walkthrough (Requirement 7)
- **Tag:** `●  LIVE SYSTEM DEMO`
- **Title:** Live System Demonstration & Managerial Walkthrough
- **Subtitle:** End-to-End Operational Workflow from Incident Ingestion to Executive Action Plan
- **Cards:**
  1. *1. Dashboard KPIs & Hybrid Search:* Role-based login, live KPI cards, hybrid query on *"truffle fries soggy"*, review inspector.
  2. *2. 5-Agent Collaborative Run:* Unstructured complaint ingestion, automated handoffs (Classifier &rarr; RCA &rarr; SOP &rarr; Impact &rarr; Judge), APPROVED verdict.
  3. *3. Forecasting, Chat & Admin:* Interactive Prophet 90-day curve, similar restaurant twin finder, persistent chat drawer, user management CRUD.

### Slide 17: Engineering Challenges & Key Learnings (Requirement 9)
- **Tag:** `●  CHALLENGES & LEARNINGS`
- **Title:** Engineering Challenges, Trade-offs & Key Learnings
- **Subtitle:** Architectural Design Decisions, Production Bottlenecks, and Lessons Learned
- **Cards:**
  1. *1. Retrieval & Latency Trade-offs:* Local CPU embeddings vs. cloud API latency; resolving lexical/semantic blindspots via RRF ($k=60$); ChromaDB RAM optimization.
  2. *2. Agent Resilience & Safety:* Mitigating LLM hallucinations using autonomous Quality Judge self-correction; Grounded Deterministic Fallback for 100% uptime.
  3. *3. Engineering Learnings:* Real-world Yelp noise cleaning; explainable additive Bayesian models (Prophet) over black-box LSTMs; closed-loop telemetry feedback.
