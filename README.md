# From Text to Trust
### Interactive Information Retrieval for Structured Financial Data Using Large Language Models

**Master's Thesis — M.Sc. Artificial Intelligence**

**Author:** Fadi N. R. Sultan  
**Institution:** Technical University of Applied Sciences Würzburg-Schweinfurt (THWS), Germany  
**Submitted:** February 2026  
**Supervisors:** Prof. Dr. Andreas Lehrmann and Prof. Dr. Dominik Seuß

---

## Overview

Financial disclosures published through the U.S. Securities and Exchange Commission (SEC) contain valuable information, but extracting reliable answers from their structured tables can be challenging.

Large Language Models (LLMs) provide powerful natural-language capabilities. However, they still face limitations in numerical reasoning, processing tabular structures, and generating factually grounded answers.

This Master's thesis investigates a **Retrieval-Augmented Generation (RAG) based question-answering system** designed to retrieve and reason over structured financial data from SEC filings.

The central contribution is **Dynamic Query-Based Table Reasoning (DQTR)**, an approach that combines query classification with deterministic table-operation sequences to improve the interpretability and control of financial question answering.
## 🌐 Live Deployment

The developed AI-powered financial question-answering system is deployed online and can be accessed through the following link:

**🚀 [Explore the Live Application](https://landing4.project3.fadiprojects.online)**

The web application provides an interactive interface for submitting natural-language financial queries and demonstrates the integration of structured financial data retrieval with Dynamic Query-Based Table Reasoning (DQTR).

**Deployment URL:** https://landing4.project3.fadiprojects.online

**Research objective:** Develop a system that enables users to interact with complex financial data using natural language while maintaining transparent, evidence-based reasoning.

---

## Key Contributions

- **Dynamic Query-Based Table Reasoning (DQTR):** A reasoning framework that classifies natural-language queries and applies predefined sequences of table operations.
- **Structured financial dataset:** Financial disclosures collected from SEC EDGAR, covering a selected universe of 100 NASDAQ companies and fiscal years 2016–2025.
- **Taxonomy-aware financial extraction:** Processing financial metrics using US GAAP and XBRL taxonomy concepts.
- **Interactive web application:** A browser-based interface that supports natural-language questions and conversational interaction.
- **Comparative evaluation:** Assessment against Chain-of-Table and OpenTab using answer-correctness and evidence-quality metrics.

---

## System Architecture

The proposed system consists of three main components:

1. **Web Interface:** Allows users to submit financial questions using natural language.
2. **Retrieval and Reasoning Backend:** Processes requests, retrieves relevant financial information, and applies DQTR.
3. **Structured Financial Data:** Contains financial metrics extracted and normalized from SEC filings.

The conceptual workflow is:

**User Question → Web Interface → Retrieval Backend → Question Classification → Deterministic Table Operations → Answer Generation → User Response**

This modular architecture separates the user-facing application from financial data processing and reasoning.

---

## Dynamic Query-Based Table Reasoning (DQTR)

DQTR is the main methodological contribution of this thesis.

It builds on the Chain-of-Table approach by introducing a controlled operation-selection mechanism.

Instead of allowing unrestricted operation sequences, DQTR uses a **question gate** to identify the reasoning type and selects a predefined sequence of operations.

### DQTR Workflow

**Step 1 — Query Classification**

The user submits a question about financial data. The question gate determines the appropriate reasoning category, such as simple cell lookup, filtering, aggregation, or comparison.

**Step 2 — Operation Selection**

Based on the identified reasoning type, a deterministic policy selects a sequence of supported table operations.

**Step 3 — Table Reasoning**

The system executes the selected operations over structured financial tables.

**Step 4 — Answer Generation**

The resulting evidence is used to construct an answer to the user's question.

### Example: Simple Cell Lookup

**Question:** What was the company's net income in a specific fiscal year?

The execution follows:

`Question → Simple Cell Lookup → Select Column → Select Row → Retrieve Cell Value → Answer`

This approach aims to make table reasoning more interpretable and reduce unnecessary operation branching. However, it does not guarantee that every generated answer is correct or fully grounded.

---

## Dataset

The financial dataset was constructed using information retrieved from the **SEC EDGAR system**, particularly structured XBRL financial facts.

| Property | Description |
|---|---|
| Data source | SEC EDGAR |
| Company universe | 100 selected NASDAQ companies |
| Period | Fiscal years 2016–2025 |
| Financial metrics | 20 financial measures |
| Data representation | Structured financial tables |
| Financial taxonomy | US GAAP / XBRL |
| Processed data | CSV |
| Evaluation examples | JSONL |
| Question types | WikiTableQuestions-style and TabFact-style |

The extraction pipeline includes identifying relevant XBRL concepts, filtering financial facts, normalizing the information, and preparing structured tables for question answering.

The dataset also considers missing financial values and the use of alternative XBRL concepts when primary financial tags are unavailable.

**Data source:** [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

---

## Evaluation Results

DQTR was evaluated against two table-reasoning approaches:

- **Chain-of-Table**
- **OpenTab**

The evaluation considered both answer correctness and the quality of the evidence used in generating responses.

### Performance Comparison

| Metric | DQTR | Chain-of-Table | OpenTab |
|---|---:|---:|---:|
| Binary Accuracy | 0.600 | **0.650** | 0.580 |
| Precision | 1.000 | 1.000 | 1.000 |
| Recall | 0.600 | **0.650** | 0.580 |
| F1-Score | 0.780 | **0.920** | 0.880 |
| Faithfulness | 0.510 | **0.525** | 0.512 |
| Contextual Precision | 0.900 | **1.000** | 0.950 |
| Contextual Recall | 0.900 | **0.950** | 0.900 |
| Response Groundedness | 0.180 | **0.225** | 0.200 |
| Answer Accuracy | 0.480 | **0.550** | 0.520 |
| Exact Match | 0.480 | **0.550** | 0.500 |

*Results reported in Table 4.1 of the Master's thesis.*

### Key Findings

- DQTR achieved a binary accuracy of **60%**.
- The approach achieved **90% contextual precision and recall**.
- Chain-of-Table performed better on most reported quantitative evaluation metrics.
- DQTR's main contribution lies in its controlled and interpretable reasoning workflow rather than demonstrating superior overall answer accuracy.
- The results indicate opportunities to improve numerical correctness, evidence attribution, and answer groundedness.

---

## Technical Implementation

The research system uses a modular architecture for natural-language interaction, financial data retrieval, and structured table reasoning.

### Backend

The backend handles user requests, retrieves relevant financial data, performs query classification, applies table operations, and generates responses.

### Frontend

The interactive web application provides a natural-language search interface and a chat-style panel for displaying answers.

Communication between frontend and backend uses HTTP requests and JSON responses.

### Deployment

The thesis describes an AWS-hosted deployment using an Nginx web server and reverse proxy.

Detailed installation steps and executable reproduction commands should be documented after verifying the corresponding repository source files.

---

## Example Research Questions

The system is designed to address questions such as:

- What was a company's total revenue in 2022?
- Which fiscal year had the highest operating income?
- How many years did net income exceed a specified threshold?
- What was the average revenue over a selected period?
- Does a financial statement match the information recorded in the underlying table?

These examples illustrate the supported research problem and are not live benchmark outputs.

---

## Limitations and Future Work

The study identifies several opportunities for future improvements.

**Improving Groundedness**

Strengthening the relationship between generated answers and specific source-table cells could make the results more verifiable.

**Extending Query Classification**

Supporting additional reasoning categories could improve the system's ability to answer complex financial questions.

**Improving Operation Selection**

Future approaches could investigate more flexible selection mechanisms while preserving controlled and interpretable operations.

**Handling XBRL Taxonomy Changes**

Financial concepts evolve across reporting periods, making robust taxonomy mapping an important future research direction.

**Expanding Retrieval Capabilities**

Extending the system to additional financial documents and more complex analytical queries could improve real-world applicability.

---

## Academic Information

**Thesis Title:** From Text to Trust: Interactive Information Retrieval for Structured Financial Data using Large Language Models

**Degree:** Master of Science in Artificial Intelligence

**University:** Technical University of Applied Sciences Würzburg-Schweinfurt (THWS)

**Submission Date:** February 9, 2026

**Author:** Fadi N. R. Sultan

**Primary Supervisor:** Prof. Dr. Andreas Lehrmann

**Second Supervisor:** Prof. Dr. Dominik Seuß

---

## References

- [U.S. Securities and Exchange Commission (SEC)](https://www.sec.gov/)
- [SEC EDGAR Application Programming Interfaces](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [XBRL International](https://www.xbrl.org/)
- [Chain-of-Table: Evolving Tables in the Reasoning Chain for Table Understanding](https://arxiv.org/search/?query=Chain-of-Table%3A+Evolving+Tables+in+the+Reasoning+Chain+for+Table+Understanding&searchtype=all)

---

## Author

**Fadi N. R. Sultan**

M.Sc. Artificial Intelligence  
Technical University of Applied Sciences Würzburg-Schweinfurt (THWS), Germany

---

## Disclaimer

This repository documents academic research and is not intended to provide financial or investment advice. Financial results should be verified against original SEC disclosures before being used in consequential decisions.
