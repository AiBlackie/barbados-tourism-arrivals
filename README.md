# ✈️ Barbados Tourism Arrivals — Airport Traffic vs. Visitor Arrivals

A Streamlit dashboard comparing three distinct measures of Barbados' tourism economy:
1. **GAIA Inc. Total Passengers** (Airport Traffic)
2. **BSS Stay-Over Arrivals** (Actual Overnight Visitors)
3. **BSS Cruise Arrivals** (Cruise Passengers)

The dashboard highlights a simple but important distinction: **Airport traffic is not the same as tourism.** The number of people passing through Grantley Adams International Airport (GAIA) is significantly higher than the number of actual stay-over tourists. The gap between these two numbers is the story.

## 📊 The Thesis

The airport counts everyone through the terminal: locals returning home, business travellers, transit passengers, crew, and tourists. The Barbados Statistical Service (BSS) counts only the stay-over visitors—the people who flew in and stayed overnight. 

In 2024, over **2.37 million** people passed through GAIA. However, **696,531** were stay-over visitors (incorporating the BSS revised December figures). This leaves a gap of over **1.67 million people**—more than the entire population of Barbados. 

This dashboard does not claim that either number is wrong. It shows what each source measures, and how far apart they are.

## 🏏 The 2024 World Cup Context

In June 2024, Barbados hosted the ICC Men's T20 World Cup Final. Ahead of the event, the African Export-Import Bank (Afreximbank) extended a **USD 25 million (BDS$50 million)** term loan to Kensington Oval Management Inc. (KOMI), guaranteed by the Government of Barbados, to rehabilitate the venue. 

The dashboard presents the factual arrival data surrounding this event:
*   **2023:** 636,540 stay-over arrivals (the year prior to the World Cup).
*   **2024:** 696,531 stay-over arrivals (a **+9.4% increase** year-over-year).
*   **2018:** 678,538 stay-over arrivals (the last normal pre-COVID baseline).

The data shows that while airport traffic hit a record high in 2024, the year-over-year growth in stay-over arrivals (+9.4%) was larger than the growth when compared to the pre-COVID 2018 baseline (+2.7%). The dashboard presents these baselines objectively without assessing the return on investment. 

## 🚀 Features

- **Overview:** The three headline numbers side-by-side, with the "Divergence Chart" showing the gap between airport traffic and actual tourists.
- **The Two Visitor Streams:** A breakdown of Stay-Over vs. Cruise passengers, including the critical distinction between "Intransit" and "Landed" cruise passengers.
- **Year-by-Year Explorer:** Select a year (2018, 2022, 2023) to see the Country Breakdown, Purpose of Visit, and Length of Stay. (2024 sub-category breakdowns are pending BSS release).
- **Country Breakdown:** A trend analysis of the major source markets (UK, USA, Canada, CARICOM, Other Europe) and a market shift comparison.
- **Cruise vs. Stay-Over:** A side-by-side comparison of the two visitor streams over time.
- **Airport Traffic vs. Visitor Arrivals:** The core divergence chart, with a year-by-year gap analysis.
- **The World Cup Context:** A factual breakdown of the 2023 Kensington Oval loan and the resulting arrival numbers across different baselines (2018, 2023, 2024).
- **Download:** Export the data as a CSV or download a full HTML summary report.
- **Bajan Proverbs:** Each section is anchored by a verified proverb from *"De Mortar-Pestle"* by G. Addinton Forde (1987), giving the dashboard a unique cultural identity.

## 📁 Data Sources

- **Airport Traffic:** [GAIA Inc. Passenger & Cargo Statistics](https://www.gaia.bb) (website). 
  *Note: These are operational traffic reports, not audited financial statements.*
- **Visitor Arrivals:** [Barbados Statistical Service (BSS), Visitor Arrivals Statistics](https://www.stats.gov.bb). 
  *Note: Data is revised where applicable. The 2024 stay-over total (696,531) incorporates the revised December figure (79,303) plus the Jan–Nov YTD total (617,228). 2019 BSS figures are Jan–Sept YTD only.*
- **Loan Context:** Afreximbank Press Release (April 19, 2024) and Barbados Today (November 1, 2023).

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.9 or higher
- pip

### Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/barbados-tourism-arrivals.git
   cd barbados-tourism-arrivals
