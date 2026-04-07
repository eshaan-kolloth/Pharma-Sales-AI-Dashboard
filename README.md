<div align="center">

<!-- HEADER BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2d5a27,30:4a7c3f,60:7ab648,100:c5e86c&height=250&section=header&text=🥦%20VeggieDash&fontSize=90&fontColor=ffffff&fontAlignY=50&desc=Your%20Vegetable%20Shop%20Analytics%20%7C%20From%20Farm%20to%20Figures!&descSize=16&descAlignY=72&descFontColor=e8f5d0&animation=fadeIn" width="100%"/>

<br/>

<!-- ANIMATED TAGLINE -->
<img src="https://readme-typing-svg.demolab.com?font=Fredoka+One&size=22&duration=2000&pause=700&color=4a7c3f&center=true&vCenter=true&multiline=false&width=700&lines=🥕+Track+your+carrots...+and+your+cash!;🍅+See+what's+selling+%26+what's+rotting;🧅+Profit+insights+fresher+than+your+stock;🥬+3+pages+%C2%B7+8+charts+%C2%B7+zero+confusion;🫛+Built+with+Streamlit+%C2%B7+Plotly+%C2%B7+Python" alt="Typing SVG" />

<br/><br/>

<!-- BADGES -->
[![Python](https://img.shields.io/badge/Python_3.9+-3d7a2a?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-3f4f75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/License-MIT-7ab648?style=for-the-badge)](LICENSE)

<br/>

```
🌱 ─────── FRESH ─────── FAST ─────── INSIGHTFUL 🌱
```

</div>

---

## 🥦 What Is This?

> *"Ever stared at a pile of wilting spinach and wondered — where did it all go wrong?"*

**VeggieDash** is a **Streamlit analytics dashboard** built for vegetable shop owners (or data nerds who love vegetables 🥕). Upload your shop's CSV data and instantly get beautiful charts, profit insights, and waste breakdowns — no spreadsheet headaches required.

Whether you're running a corner sabzi shop or tracking a dozen items across weeks, this dashboard turns your raw numbers into **crispy, clean insights** — just like fresh veggies! 🌿

---

## ✨ Features at a Glance

```
🥗 THE VEGGIE DASHBOARD MENU
════════════════════════════════════════════════════════════
  📊  DASHBOARD     →   Your daily stats, served fresh
  📋  SUMMARY       →   The full nutritional breakdown
  📁  RAW DATA      →   All ingredients, uncooked
════════════════════════════════════════════════════════════
```

### 🌽 Page 1 — Dashboard
The big picture. Eight charts, four KPI cards, zero confusion.

| Chart | What it tells you |
|-------|-----------------|
| 📊 Sales by Vegetable | Which veggie is the crowd favourite? |
| 📈 Sales Over Time | Spotting your busiest days |
| 🗑️ Waste Breakdown | Which item is silently eating your profits? |
| 💰 Revenue by Vegetable | Follow the money, not just the kilos |
| 📈 Profit Over Time | Is the shop going up or down? |
| ⚖️ Bought vs Sold vs Wasted | The holy trinity of shop math |
| 📅 Weekend vs Weekday | Do Sundays actually pay off? |
| 💹 Average Sell Price | Spot price spikes at a glance |

### 🍆 Page 2 — Summary
Your **smart report card** — best sellers, worst wasters, and profit champions, all ranked and colour-coded.

- 🏆 **Best Seller** — the vegetable your customers can't get enough of
- 🗑️ **Most Wasted** — the one quietly rotting in the corner
- 💰 **Most Profitable** — not always the same as best seller (plot twist! 🎭)
- 📅 Sales heatmap by day of week — plan your restocking smarter

### 🥔 Page 3 — Raw Data
- 🔍 Search & filter your records in real time
- 📥 Download filtered data as CSV — take it anywhere

---

## 🌿 Sidebar Controls

> *Filters so intuitive even your accountant uncle will figure it out*

```
🥕 Filter by Vegetable    →  Any combo you like
📅 Filter by Day          →  Monday blues? Filter 'em out
🗓️ Filter by Date Range   →  Zoom into any period instantly
```

All three filters update **every single chart and table simultaneously** — no refresh needed. 🪄

---

## 🚀 Quick Start

Three steps. That's it.

```bash
# 1️⃣  Clone the repo
git clone https://github.com/your-username/veggie-dashboard.git
cd veggie-dashboard

# 2️⃣  Install dependencies (only 4, we promise 🌱)
pip install -r requirements.txt

# 3️⃣  Drop your CSV in the data folder & launch!
streamlit run app.py
```

Then open **http://localhost:8501** and watch your veggie data bloom 🌸

---

## 📁 Project Structure

```
veggie-dashboard/
│
├── 🐍 app.py                 ←  The whole app lives here
├── 📦 requirements.txt       ←  4 dependencies, nothing more
├── 📂 data/
│   └── 🥦 vegetable_shop.csv ←  Your shop's data goes here
└── 📖 README.md              ←  You're reading this!
```

---

## 📊 CSV Format

Your data file should look like this:

| Column | Type | Description |
|--------|------|-------------|
| `Date` | date | The transaction date |
| `Day` | string | Monday, Tuesday... |
| `Item` | string | Vegetable name |
| `Bought_kg` | float | How much you bought |
| `Buy_Price` | float | Price you paid per kg (₹) |
| `Sold_kg` | float | How much you sold |
| `Sell_Price` | float | Price you charged per kg (₹) |
| `Wasted_kg` | float | How much went to waste |

> 💡 The app auto-calculates **Revenue**, **Cost**, and **Profit** for you — no formulas needed!

---

## 📦 Requirements

```txt
pandas      # Chop, slice, and dice your data 🔪
numpy       # The math behind the magic 🔢
streamlit   # Your app's fresh coat of paint 🎨
plotly      # Charts so pretty they belong in a museum 🖼️
```

---

## 🗺️ Roadmap — What's Growing Next?

```
 🌱 PHASE 1 — PLANTED (DONE ✅)
 ├─ ✅  8-chart dashboard with live filters
 ├─ ✅  Best seller / waste / profit summary page
 ├─ ✅  Raw data viewer with search & CSV export
 ├─ ✅  Vegetable, Day & Date range filters
 └─ ✅  Auto-calculated Revenue, Cost, Profit

 🌿 PHASE 2 — SPROUTING (COMING SOON 🔜)
 ├─ ⬜  Stock alerts — "You're running low on tomatoes!" 🍅
 ├─ ⬜  Restock recommendation engine
 ├─ ⬜  Weekly PDF report export
 └─ ⬜  Multi-shop / multi-location support

 🍅 PHASE 3 — RIPE (FUTURE 🌟)
 ├─ ⬜  Seasonal price trend predictions
 ├─ ⬜  WhatsApp daily report bot 📲
 ├─ ⬜  Hindi / regional language support 🇮🇳
 └─ ⬜  AI-powered waste reduction tips 🤖
```

---

## 🤝 Contributing

Found a bug? Have a feature idea? Contributions are as welcome as fresh coriander on a curry! 🌿

```bash
git checkout -b feat/your-awesome-idea
git commit -m "feat: added something crunchy 🥕"
git push origin feat/your-awesome-idea
# → Open a Pull Request!
```

---

## 📄 License

**MIT** — free to use, fork, and sell more vegetables with. 🥦

---

<div align="center">

```
🥕 ─────────────────────────────────────────────── 🍅
     Built with 🐍 Python · 📊 Streamlit · ❤️ 
         For every sabzi shop that deserves
              better than a notebook.
🥬 ─────────────────────────────────────────────── 🌽
```

*Fresh data. Fresh decisions. Fresh profits.* 🌿

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:c5e86c,50:7ab648,100:2d5a27&height=120&section=footer&animation=fadeIn" width="100%"/>

</div>
