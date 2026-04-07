<div align="center">

# 💊 Curewell Business Dashboard

### *AI-Powered Pharma Intelligence at Your Fingertips*

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Groq](https://img.shields.io/badge/Groq_AI-LLaMA_3.3_70B-F55036?style=for-the-badge)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

---

**A full-stack, AI-enhanced business intelligence dashboard built for pharmaceutical sales analytics — featuring real-time KPI tracking, interactive charts, regional breakdowns, and a Groq-powered AI analyst (ARIA) that talks to your data.**

[🚀 Live Demo](#) · [📸 Screenshots](#-screenshots) · [⚡ Quick Start](#-quick-start) · [🤖 Meet ARIA](#-meet-aria--your-ai-analyst)

</div>

---

## ✨ What Makes This Special?

> This isn't just another chart dashboard. Curewell combines **beautiful UI design**, **deep business analytics**, and **a conversational AI layer** that turns raw pharma sales data into actionable strategy — all in one Streamlit app.

---

## 🗂️ Dashboard Pages

| Page | Description |
|------|-------------|
| 📊 **Overview** | High-level KPIs — revenue, profit, units sold, customer count, order health |
| 🏷️ **Brand & Product** | Brand-level revenue share, top products, profit margins by brand |
| 🌍 **Region Analysis** | Geographic revenue breakdown, regional profitability heat maps |
| 📞 **Sales & Leads** | Call outcome distributions, lead source performance tracking |
| 💰 **Profit Analysis** | Profit vs. loss deep dives, margin analysis, vendor profitability |
| 📁 **Raw Data** | Filterable, exportable full dataset view |
| 🤖 **AI Insights** | ARIA — your on-demand AI business analyst powered by Groq |

---

## 📸 Screenshots

> *Coming soon — add your screenshots here!*

```
screenshots/
├── overview.png
├── brand_product.png
├── region_analysis.png
└── ai_insights.png
```

---

## 🤖 Meet ARIA — Your AI Analyst

**ARIA** (Advanced Revenue & Insights Analyst) is the AI brain of this dashboard. Powered by **Groq's LLaMA-3.3 70B** model, ARIA:

- 🔍 **Reads your filtered data** — not generic responses, but answers grounded in your actual numbers
- 💬 **Has a full chat interface** — ask anything, get strategic insights
- 📄 **Generates full HTML reports** — downloadable, offline-ready intelligence reports with KPI cards, tables, and AI-written analysis sections
- 🧠 **Covers all angles** — revenue, brand performance, regional trends, lead sources, product mix, and profit health

**Example questions to ask ARIA:**
```
"Which brand has the best profit margin and why?"
"What regions are underperforming and what could be causing it?"
"Give me a strategic summary of this quarter's sales data."
"Which products should we prioritize for the next sales push?"
```

---

## 📊 Key Features

- **8 KPI Banner Cards** with gradient designs across the Overview page
- **15+ Interactive Plotly Charts** — pie charts, bar charts, horizontal rankings, scatter plots
- **Expandable Data Tables** below every chart — see the numbers behind the visuals
- **Sidebar Filters** — slice by Brand, Region, Product, Vendor, and Lead Source simultaneously
- **Downloadable HTML Reports** — beautifully styled, print-ready, works offline
- **Smart Scroll Behavior** — auto-scrolls to top on page navigation
- **Dark-themed UI** with custom CSS, DM Sans font, and gradient banners

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/curewell-dashboard.git
cd curewell-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_key_here
```

> Get your **free** API key at [console.groq.com](https://console.groq.com)

### 4. Add your data

Place your CSV file at:

```
Data/curewell_business_full_dataset.csv
```

Your CSV should include these columns:

| Column | Description |
|--------|-------------|
| `Revenue_INR` | Order revenue in Indian Rupees |
| `Estimated_Profit_INR` | Estimated profit per order |
| `Units_Sold` | Number of units in the order |
| `Customer_ID` | Unique customer identifier |
| `Brand` | Product brand name |
| `Product` | Product name |
| `Region` | Sales region |
| `Vendor` | Vendor/distributor name |
| `Lead_Source` | How the lead was acquired |
| `Product_Size` | Size category of the product |
| `Call_Outcome` | Result of the sales call |

### 5. Launch the dashboard

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. 🎉

---

## 🗃️ Project Structure

```
curewell-dashboard/
│
├── app.py                    # Main Streamlit application (all pages + AI)
├── requirements.txt          # Python dependencies
├── .env                      # Your API keys (not committed to git)
├── .gitignore
│
└── Data/
    └── curewell_business_full_dataset.csv   # Your pharma sales data
```

---

## 📦 Dependencies

```txt
streamlit      # Web app framework
pandas         # Data manipulation
numpy          # Numerical operations
plotly         # Interactive charts
requests       # Groq API calls
python-dotenv  # Environment variable management
markdown       # HTML report generation
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Optional* | Enables ARIA AI Insights & report generation |

*The dashboard runs fully without a Groq key — AI features are simply disabled until a key is provided (can also be entered directly in the sidebar).

---

## 🛣️ Roadmap

- [ ] Date range filter for time-series analysis
- [ ] Multi-file CSV upload support
- [ ] ARIA memory — persistent chat across sessions
- [ ] Export charts as PNG
- [ ] Role-based view (Sales Rep vs. Manager vs. Executive)
- [ ] Email report delivery

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Built with ❤️ for smarter pharma sales decisions**

*If this project helped you, consider giving it a ⭐ on GitHub!*

</div>
