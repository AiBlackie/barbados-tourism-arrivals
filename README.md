# ✈️ Barbados Tourism Arrivals — Airport Traffic vs. Visitor Arrivals

A Streamlit dashboard comparing three distinct measures of Barbados' tourism economy:
1. **GAIA Inc. Total Passengers** (Airport Traffic)
2. **BSS Stay-Over Arrivals** (Actual Overnight Visitors)
3. **BSS Cruise Arrivals** (Cruise Passengers)

The dashboard proves a simple but important thesis: **Airport traffic is not tourism.** The number of people passing through Grantley Adams International Airport (GAIA) is significantly higher than the number of actual stay-over tourists. The gap between these two numbers is the story.

## 📊 The Thesis

The airport counts everyone through the terminal: locals returning home, business travellers, transit passengers, crew, and tourists. The Barbados Statistical Service (BSS) counts only the stay-over visitors—the people who flew in and stayed overnight. 

In 2024, over **2.37 million** people passed through GAIA. But only **617,000** were stay-over visitors. That is a gap of nearly **1.76 million people**—more than the entire population of Barbados. 

This dashboard does not claim that either number is wrong. It shows what each source measures, and how far apart they are.

## 🏏 The 2024 World Cup Paradox

In June 2024, Barbados hosted the ICC Men's T20 World Cup Final. The airport saw a record 2.37 million passengers for the year. Yet, actual stay-over tourists fell by 3% compared to 2023 (from 636,540 to 617,314). The World Cup filled the planes and the cruise ships, but it did not fill the hotel beds for the year. Mega-events boost airport traffic; they do not automatically grow the stay-over tourism product.

## 🚀 Features

- **Overview:** The three headline numbers side-by-side, with the "Divergence Chart" showing the gap between airport traffic and actual tourists.
- **The Two Visitor Streams:** A breakdown of Stay-Over vs. Cruise passengers, including the critical distinction between "Intransit" and "Landed" cruise passengers.
- **Year-by-Year Explorer:** Select any year (2018, 2022, 2023) to see the Country Breakdown, Purpose of Visit, and Length of Stay. (2024 breakdowns are pending BSS release).
- **Country Breakdown:** A trend analysis of the major source markets (UK, USA, Canada, CARICOM, Other Europe) and a market shift comparison.
- **Cruise vs. Stay-Over:** A side-by-side comparison of the two visitor streams over time.
- **Airport Traffic vs. Visitor Arrivals:** The core divergence chart, with a year-by-year gap analysis.
- **Download:** Export the data as a CSV or download a full HTML summary report.
- **Bajan Proverbs:** Each section is anchored by a verified proverb from *"De Mortar-Pestle"* by G. Addinton Forde (1987), giving the dashboard a unique cultural identity.

## 📁 Data Sources

- **Airport Traffic:** [GAIA Inc. Passenger & Cargo Statistics](https://www.gaia.bb) (website). 
  *Note: These are operational traffic reports, not audited financial statements.*
- **Visitor Arrivals:** [Barbados Statistical Service (BSS), Visitor Arrivals Statistics](https://www.stats.gov.bb). 
  *Note: Data is revised where applicable (see 2022 and 2024 revision notes). 2019 BSS figures are Jan–Sept YTD only. 2024 breakdowns are pending BSS release.*

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.9 or higher
- pip

### Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/barbados-tourism-arrivals.git
   cd barbados-tourism-arrivals
