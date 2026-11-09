# findr. — AI-Powered Personal Finance Advisor

> **Your money, decided.** A personal finance advisor that consolidates multiple credit-card statements, reconciles them, finds money leaks, and answers questions with an AI assistant that is grounded on the user's own numbers.

**🔗 Live Demo:** https://shohan96s.github.io/FinTech/

![findr dashboard](docs/screenshot.png) <!-- Add a screenshot of the dashboard here -->

---

## 📌 Problem

People with several credit cards see their spending one statement at a time. None of those statements shows:
- total spend across all cards
- where the money actually goes, by category
- fees, interest and duplicate charges that bought nothing
- subscriptions that quietly pile up

**findr** combines all the statements into one reconciled view and turns it into clear, actionable advice.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Multi-card consolidation** | Merges statements from multiple cards into one monthly spend view |
| **Statement reconciliation** | Checks consolidated totals against each source statement ✓ |
| **Data-quality checks** | Flags missing or inconsistent inputs (e.g. an expected card with no statement) before any advice is shown |
| **Category analysis** | Share of total spend by category, plus month-on-month trends and spike explanations |
| **Money-leak detection** | Finds avoidable fees, interest charges and likely billing errors |
| **Subscription stack** | Lists recurring subscriptions and their combined cost |
| **AI Advisor (Claude)** | Answers natural-language questions, grounded strictly on the reconciled data |
| **Deterministic mode** | Toggles AI phrasing off so answers are instant and guaranteed to match the data exactly |

---

## 🧠 AI Design: Grounded and Trustworthy

An LLM should never invent financial figures, so findr is built around that rule:

1. **Numbers first.** All totals, categories and flags are calculated deterministically from the statements.
2. **LLM for phrasing only.** Claude receives the computed figures as context and turns them into natural-language answers. It does not calculate.
3. **Fallback switch.** With AI turned off, answers come from deterministic templates, so every figure matches the source data.
4. **Data checks before advice.** If the input data is incomplete, the user is warned before any insight is shown.

---

## 🛠️ Tech Stack

<!-- ⚠️ Update this section with the actual tools used -->
| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript `<!-- confirm / add framework, e.g. React, Chart.js -->` |
| Data processing | `<!-- e.g. Python / JavaScript — statement parsing, categorisation, reconciliation -->` |
| AI | Claude API (Anthropic) `<!-- confirm model and how it is called -->` |
| Hosting | GitHub Pages |

---

## 📂 Project Structure

<!-- ⚠️ Replace with the actual folder layout -->
```
FinTech/
├── index.html          # Dashboard UI
├── assets/             # Styles, scripts, charts
├── data/               # Anonymised sample statements
├── docs/               # Screenshots
└── README.md
```

---

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/shohan96s/FinTech.git
cd FinTech

# 2. Open locally
#    Open index.html in a browser, or run a simple server:
python -m http.server 8000
#    Then visit http://localhost:8000
```

<!-- ⚠️ If the AI advisor needs an API key, explain how to set it up — never commit keys to the repo -->

---

## 🔒 Data Privacy

- The demo uses an **anonymised test user** (Jordan T. Reeves) and **sample statements** (Jun–Aug 2026).
- No real customer or card data is stored in this repository.

---

## 📈 Sample Insights (Demo Data)

- Consolidated spend across **3 cards** for **June–August 2026**
- The August spending spike is traced to a single trip
- Avoidable fees and interest for the quarter are quantified
- A likely billing error is flagged for action

---

## 🔮 Future Enhancements

- [ ] Upload statements directly as PDF or CSV
- [ ] Budget alerts and goal tracking
- [ ] Workflow automation (e.g. n8n) for monthly report emails
- [ ] Multi-currency support (AED / INR)

---

## 👤 Author

**Shohan S** — UiPath RPA & AI Automation Developer
📧 shohan96@gmail.com · 🔗 [LinkedIn](https://linkedin.com/in/your-profile) <!-- update -->
