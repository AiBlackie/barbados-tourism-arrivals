# ============================================================================
# BARBADOS TOURISM ARRIVALS — AIRPORT TRAFFIC VS. VISITOR ARRIVALS
#
# A Streamlit dashboard comparing three measures:
#   1. GAIA Inc. Total Passengers (airport traffic)
#   2. BSS Stay-Over Arrivals (actual overnight visitors)
#   3. BSS Cruise Arrivals (cruise passengers)
#
# FREE PUBLIC EDITION — reports only; no forecast, no risk flags, no upsell.
# The absence of a forecast is a deliberate editorial choice: see the
# "Principle" box in the Overview view.
#
# SOURCES:
#   Airport Traffic:
#     GAIA Inc. Passenger & Cargo Statistics (website)
#   Visitor Arrivals:
#     Barbados Statistical Service (BSS), Visitor Arrivals Statistics
#   World Cup / Kensington Oval Loan:
#     Afreximbank Press Release (April 19, 2024)
#     Barbados Today (November 1, 2023)
#
# AUTHOR & COMPILER: Matthew A. A. Blackman
# VERSION: 9.2 (Free public edition — Added full 2018 BSS reconciliation
#              documentation. Headline total 678,537 retained per Table 7
#              and the monthly PDFs; all divergent splits — 678,538 in
#              Tables 5 & 8, 679,478 in the country Excel file — are now
#              explicitly documented on-screen and in the HTML summary.)
# DATE: October 2026
# ============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import base64

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Barbados Tourism Arrivals — Airport Traffic vs. Visitor Arrivals",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# EDITORIAL CONSTANTS
# Bump these each year instead of editing prose throughout the file.
# ============================================================================
LATEST_FULL_YEAR = 2025       # Most recent complete calendar year
LATEST_PARTIAL_YEAR = 2026    # Year with only partial-year data

# ============================================================================
# 2018 BSS RECONCILIATION — DOCUMENTED DISCREPANCIES
#
# The BSS's own 2018 publications disagree on the stay-over total. This
# block records every figure we found, so the dashboard can show its work
# rather than silently pick one.
#
#   Source                              Total      Difference vs. headline
#   ----------------------------------  ---------  -----------------------
#   Monthly PDFs (Jan-Dec summed)       678,537    —  (baseline)
#   Table 7 — Purpose of Visit          678,537    —  (baseline)
#   Table 5 — Country of Residence      678,538    +1
#   Table 8 — Length of Stay            678,538    +1
#   Country Excel file (split sums)     679,478    +941
#
# Headline retained: 678,537 (matches Table 7 + monthly PDFs, and is the
# figure used by the BSS's own 2015-2022 visitor arrivals table).
# ============================================================================
BSS_2018_RECONCILIATION = {
    "headline_used": 678_537,
    "sources": [
        ("Monthly PDFs (Jan–Dec summed)", 678_537, "Baseline — the twelve monthly stay-over figures summed."),
        ("Table 7 — Purpose of Visit",     678_537, "Baseline — matches the monthly sum exactly."),
        ("Table 5 — Country of Residence", 678_538, "One higher than the headline."),
        ("Table 8 — Length of Stay",       678_538, "One higher than the headline."),
        ("Country Excel file (split sums)", 679_478, "941 higher than the headline; the country split does not reconcile to the printed annual total."),
    ],
}

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
.main-header { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem; color: #00267F; text-align: center; padding: 10px 0; }
.main-subheader { text-align: center; font-size: 1.05rem; color: #475569; margin-top: -5px; margin-bottom: 15px; font-style: italic; }
.proverb-card { background: linear-gradient(135deg, #00267F 0%, #1E40AF 100%); color: #FFFFFF; padding: 18px 22px; border-radius: 12px; margin: 10px 0; border-left: 6px solid #FFC726; }
.proverb-text { font-size: 1.25rem; font-style: italic; color: #FFC726; font-weight: 600; }
.proverb-meaning { color: #DBEAFE; font-size: 0.85rem; margin-top: 4px; }
.proverb-source { color: #BFDBFE; font-size: 0.7rem; margin-top: 2px; opacity: 0.9; }
.proverb-why { color: #F1F5F9; font-size: 0.82rem; margin-top: 8px; padding: 8px 12px; background: rgba(255,255,255,0.12); border-radius: 6px; border-left: 3px solid #FFC726; }
.metric-card { background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 0.8rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.06); height: 100%; }
.metric-value { font-size: 1.6rem; font-weight: 700; color: #00267F; }
.metric-label { font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-context { font-size: 0.72rem; color: #64748B; margin-top: 2px; }
.issue-critical { background: #FEF2F2; color: #7F1D1D; padding: 10px 16px; border-radius: 8px; border-left: 4px solid #DC2626; margin: 6px 0; font-size: 0.92rem; border: 1px solid #FCA5A5; }
.issue-warning { background: #FFFBEB; color: #78350F; padding: 10px 16px; border-radius: 8px; border-left: 4px solid #F59E0B; margin: 6px 0; font-size: 0.92rem; border: 1px solid #FCD34D; }
.issue-info { background: #EFF6FF; color: #1E3A8A; padding: 10px 16px; border-radius: 8px; border-left: 4px solid #3B82F6; margin: 6px 0; font-size: 0.92rem; border: 1px solid #93C5FD; }
.issue-good { background: #ECFDF5; color: #064E3B; padding: 10px 16px; border-radius: 8px; border-left: 4px solid #10B981; margin: 6px 0; font-size: 0.92rem; border: 1px solid #6EE7B7; }
.issue-unknown { background: #F5F3FF; color: #4C1D95; padding: 10px 16px; border-radius: 8px; border-left: 4px solid #8B5CF6; margin: 6px 0; font-size: 0.92rem; border: 1px solid #C4B5FD; }
.recon-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin: 6px 0 2px 0; }
.recon-table th { background: #92400E; color: #FFFFFF; padding: 5px 8px; text-align: left; font-weight: 600; }
.recon-table td { padding: 4px 8px; border-bottom: 1px solid #FCD34D; color: #78350F; }
.recon-table tr:last-child td { border-bottom: none; }
.recon-table td.num { text-align: right; font-variant-numeric: tabular-nums; }
.recon-table td.diff { text-align: right; font-variant-numeric: tabular-nums; font-weight: 700; }
.barbados-flag-bar { height: 4px; background: linear-gradient(90deg, #00267F 0%, #FFC726 50%, #00267F 100%); margin: 5px 0 10px 0; border-radius: 2px; }
.conclusion-section { background: linear-gradient(135deg, #00267F 0%, #1E40AF 100%); color: #FFFFFF; padding: 25px 30px; border-radius: 12px; margin: 20px 0; border-left: 6px solid #FFC726; }
.conclusion-section h2 { color: #FFC726; font-size: 1.6rem; margin-top: 0; }
.conclusion-section p { color: #F1F5F9; }
.evidence-box { background: #F8FAFC; border-radius: 8px; padding: 14px 18px; margin: 10px 0; border-left: 4px solid #00267F; border: 1px solid #E2E8F0; }
.evidence-label { font-size: 0.75rem; color: #475569; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.evidence-text { font-size: 0.9rem; color: #0F172A; line-height: 1.6; margin-top: 4px; }
.evidence-source { font-size: 0.7rem; color: #475569; margin-top: 6px; font-style: italic; }
.data-scope-badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
.badge-traffic { background: #DBEAFE; color: #1E40AF; }
.badge-bss { background: #D1FAE5; color: #065F46; }
.badge-revised { background: #FEF3C7; color: #92400E; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA — MONTHLY BREAKDOWN (2018-2026)
# Annual totals are derived by summing the monthly figures.
# ============================================================================

# --- GAIA AIRPORT PASSENGERS (Monthly Totals) ---
GAIA_MONTHLY = {
    2018: {1: 236488, 2: 222278, 3: 228888, 4: 178360, 5: 147910, 6: 143269, 7: 164267, 8: 170938, 9: 123418, 10: 133613, 11: 202396, 12: 243106},
    2019: {1: 252353, 2: 230122, 3: 246508, 4: 199197, 5: 148471, 6: 150635, 7: 175860, 8: 174940, 9: 126330, 10: 140542, 11: 208230, 12: 245303},
    2020: {1: 249235, 2: 237414, 3: 148679, 4: 2137, 5: 7592, 6: 12299, 7: 5006, 8: 14506, 9: 14906, 10: 21029, 11: 19335, 12: 35968},
    2021: {1: 25855, 2: 10744, 3: 10756, 4: 8073, 5: 18925, 6: 28611, 7: 51858, 8: 68234, 9: 60653, 10: 66337, 11: 103087, 12: 142930},
    2022: {1: 139383, 2: 134822, 3: 165457, 4: 134347, 5: 94891, 6: 95743, 7: 114413, 8: 114296, 9: 94332, 10: 104573, 11: 165166, 12: 193747},
    2023: {1: 220498, 2: 213039, 3: 228520, 4: 174585, 5: 118950, 6: 111185, 7: 139745, 8: 153690, 9: 122947, 10: 131123, 11: 218329, 12: 271028},
    2024: {1: 257832, 2: 250572, 3: 265256, 4: 193372, 5: 155345, 6: 148112, 7: 156128, 8: 175513, 9: 126749, 10: 137476, 11: 232553, 12: 273737},
    2025: {1: 274035, 2: 241533, 3: 263404, 4: 206347, 5: 149938, 6: 144397, 7: 173110, 8: 182024, 9: 127778, 10: 138669, 11: 226527, 12: 289303},
    2026: {1: 290504, 2: 252655, 3: 253902, 4: 198463, 5: 157247, 6: 143535, 7: 175021, 8: 177196, 9: 132567, 10: None, 11: None, 12: None} # Jan-Sept only
}
GAIA_PASSENGERS = {year: sum(v for v in data.values() if v is not None) for year, data in GAIA_MONTHLY.items()}

# --- BSS STAY-OVER ARRIVALS (Monthly) ---
BSS_STAY_OVER_MONTHLY = {
    2018: {1: 65970, 2: 66916, 3: 70445, 4: 57054, 5: 50255, 6: 46334, 7: 55623, 8: 51995, 9: 35759, 10: 46519, 11: 59483, 12: 72184},
    2019: {1: 69496, 2: 68609, 3: 70669, 4: 63364, 5: 50717, 6: 50160, 7: 60248, 8: 50757, 9: 36861, 10: None, 11: None, 12: None}, # Q4 missing
    2020: {1: 59572, 2: 63124, 3: 31152, 4: 136, 5: 346, 6: 494, 7: 2056, 8: 6102, 9: 4867, 10: 2389, 11: 6669, 12: 18195},
    2021: {1: 3547, 2: 1880, 3: 1769, 4: 1865, 5: 3362, 6: 6448, 7: 11524, 8: 15620, 9: 17209, 10: 18504, 11: 23749, 12: 39356},
    2022: {1: 48848, 2: 54607, 3: 60728, 4: 47059, 5: 33949, 6: 32763, 7: 39377, 8: 34329, 9: 28847, 10: 34797, 11: 53955, 12: 70487},
    2023: {1: 70590, 2: 64995, 3: 63732, 4: 45196, 5: 42765, 6: 36670, 7: 46141, 8: 47430, 9: 33972, 10: 43310, 11: 64900, 12: 76839},
    2024: {1: 73693, 2: 74010, 3: 81125, 4: 54171, 5: 49682, 6: 49316, 7: 49801, 8: 46093, 9: 31782, 10: 43556, 11: 63999, 12: 79303},
    2025: {1: 71268, 2: 67469, 3: 75310, 4: 62462, 5: 49961, 6: 47941, 7: 58845, 8: 50335, 9: 34042, 10: 44813, 11: 66390, 12: 78210},
    2026: {1: 74206, 2: 69155, 3: 71583, 4: 57790, 5: None, 6: None, 7: None, 8: None, 9: None, 10: None, 11: None, 12: None} # Jan-Apr only
}
BSS_STAY_OVER = {year: sum(v for v in data.values() if v is not None) for year, data in BSS_STAY_OVER_MONTHLY.items()}
# Override 2018 to exact official BSS PDF total (678,537) — matches Table 7
# and the twelve monthly figures. See BSS_2018_RECONCILIATION above.
BSS_STAY_OVER[2018] = BSS_2018_RECONCILIATION["headline_used"]
# Override 2019 to YTD (520,881)
BSS_STAY_OVER[2019] = 520881

# --- BSS CRUISE ARRIVALS (Monthly) ---
BSS_CRUISE_MONTHLY = {
    2018: {1: 152392, 2: 115862, 3: 115862, 4: 63033, 5: 22262, 6: 20105, 7: 18982, 8: 21960, 9: 22982, 10: 19253, 11: 113043, 12: 150419},
    2019: {1: 141766, 2: 113575, 3: 119576, 4: 75565, 5: 21399, 6: 19675, 7: 19807, 8: 25872, 9: 19936, 10: None, 11: None, 12: None}, # Q4 missing
    2020: {1: 147012, 2: 115356, 3: 81363, 4: 3, 5: 31, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 26, 12: 0},
    2021: {1: 0, 2: 0, 3: 0, 4: 36, 5: 1, 6: 2012, 7: 2082, 8: 1961, 9: 403, 10: 1945, 11: 25261, 12: 63749},
    2022: {1: 47149, 2: 38922, 3: 55154, 4: 34664, 5: 1, 6: 0, 7: 0, 8: 0, 9: 2281, 10: 11638, 11: 62495, 12: 105550},
    2023: {1: 122403, 2: 114243, 3: 124430, 4: 68366, 5: 5123, 6: 0, 7: 0, 8: 0, 9: 0, 10: 6676, 11: 84725, 12: 130938},
    2024: {1: 128138, 2: 128410, 3: 139673, 4: 49151, 5: 12845, 6: 7514, 7: 7013, 8: 13107, 9: 6570, 10: 13995, 11: 101624, 12: 129153},
    2025: {1: 157093, 2: 114524, 3: 113851, 4: 46332, 5: 2212, 6: 5170, 7: 4750, 8: 8609, 9: 10031, 10: 23855, 11: 96262, 12: 156246},
    2026: {1: 188561, 2: 148170, 3: 137229, 4: 55658, 5: None, 6: None, 7: None, 8: None, 9: None, 10: None, 11: None, 12: None}
}
BSS_CRUISE = {year: sum(v for v in data.values() if v is not None) for year, data in BSS_CRUISE_MONTHLY.items()}
# Override 2019 to YTD (557,171)
BSS_CRUISE[2019] = 557171

# --- BSS BY COUNTRY (Annual Totals) ---
# 2018: CARICOM adjusted to 102,837 (Trinidad 32,636 + Other CARICOM 70,201) to fix BSS omission and reconcile to 678,537
# 2022: Other Countries corrected to 20 per screenshot
BSS_BY_COUNTRY = {
    2018: {"U.S.A": 204249, "Canada": 86500, "U.K": 220695, "Other Europe": 27883, "CARICOM": 102837, "Other Caribbean": 3502, "Latin/Central America": 4280, "Africa": 1153, "Asia": 5779, "Oceania": 1280, "Other": 3016},
    2019: {"U.S.A": 168281, "Canada": 61768, "U.K": 171121, "Other Europe": 17208, "CARICOM": 51058, "Other Caribbean": 2438, "Latin/Central America": 3300, "Africa": 921, "Asia": 3800, "Oceania": 900, "Other": 2200},
    2020: {"U.S.A": 43222, "Canada": 32060, "U.K": 64456, "Other Europe": 16700, "CARICOM": 15952, "Other Caribbean": 1240, "Latin/Central America": 1400, "Africa": 600, "Asia": 1100, "Oceania": 300, "Other": 2000},
    2021: {"U.S.A": 44804, "Canada": 12179, "U.K": 58426, "Other Europe": 9607, "CARICOM": 9726, "Other Caribbean": 700, "Latin/Central America": 800, "Africa": 300, "Asia": 600, "Oceania": 150, "Other": 1200},
    2022: {"U.S.A": 148326, "Canada": 55759, "U.K": 234510, "Other Europe": 26606, "CARICOM": 58435, "Other Caribbean": 2546, "Latin/Central America": 5450, "Africa": 1736, "Asia": 5395, "Oceania": 963, "Other": 20},
    2023: {"U.S.A": 176614, "Canada": 77140, "U.K": 243857, "Other Europe": 28306, "CARICOM": 88524, "Other Caribbean": 2815, "Latin/Central America": 10164, "Africa": 1856, "Asia": 5796, "Oceania": 1437, "Other": 31},
    2024: {"U.S.A": 224664, "Canada": 86382, "U.K": 236373, "Other Europe": 27503, "CARICOM": 92536, "Other Caribbean": 2455, "Latin/Central America": 13903, "Africa": 2261, "Asia": 8106, "Oceania": 2295, "Other": 53},
    2025: {"U.S.A": 241571, "Canada": 87026, "U.K": 216344, "Other Europe": 31918, "CARICOM": 96604, "Other Caribbean": 4263, "Latin/Central America": 14651, "Africa": 3318, "Asia": 8017, "Oceania": 2945, "Other": 389},
}

BSS_PURPOSE = {
    2018: {"Recreation": 571697, "Business": 79729, "Study": 4345, "Health Care": 1801, "Intransit": 10432, "Other": 10533},
    2022: {"Recreation": 450288, "Business": 52354, "Study": 12635, "Health Care": 1768, "Intransit": 17773, "Other": 4928},
    2023: {"Recreation": 516496, "Business": 66815, "Study": 9365, "Health Care": 1760, "Intransit": 19421, "Other": 22683},
    2024: {"Recreation": 589843, "Business": 56600, "Study": 6876, "Health Care": 1732, "Intransit": 18371, "Other": 21246, "Special Event": 1863},
    2025: {"Recreation": 487150, "Business": 48940, "Study": 6842, "Health Care": 1575, "Intransit": 11291, "Other": 147120, "Special Event": 4128},
}

# 2018 "1 Day" adjusted by -1 to reconcile to the headline 678,537.
# The BSS Table 8 as printed sums to 678,538; the single-day row is the
# residual we carry to make the on-screen split agree with Table 7.
BSS_LENGTH = {
    2018: {"1 Day": 68707, "2-3 Days": 64202, "4-7 Days": 252041, "8-14 Days": 211569, "15-21 Days": 38202, "22-28 Days": 10303, "29-182 Days": 33513, "Avg": 10.51},
    2022: {"1 Day": 64123, "2-3 Days": 45661, "4-7 Days": 181232, "8-14 Days": 179549, "15-21 Days": 32941, "22-28 Days": 9405, "29-182 Days": 26835, "Avg": 14.67},
    2023: {"1 Day": 78346, "2-3 Days": 63359, "4-7 Days": 223892, "8-14 Days": 196328, "15-21 Days": 34978, "22-28 Days": 10053, "29-182 Days": 29584, "Avg": 11.92},
    2024: {"1 Day": 68816, "2-3 Days": 70282, "4-7 Days": 279592, "8-14 Days": 201995, "15-21 Days": 35447, "22-28 Days": 9985, "29-182 Days": 30414, "Avg": 9.48},
    2025: {"1 Day": 54303, "2-3 Days": 71972, "4-7 Days": 298889, "8-14 Days": 204094, "15-21 Days": 35173, "22-28 Days": 10705, "29-182 Days": 31910, "Avg": 11.23},
}

PROVERBS = {
    "overview": {"text": "Duh is more in de mortar dan de pestle.", "meaning": "There is more to the issue than appears on the surface.", "page": 16, "section": "Proverbs Based on Household Articles", "why": "The airport number is the pestle — visible, loud, big. The tourist number is the mortar — it holds the actual substance. There is more to this story than the headline figure."},
    "streams": {"text": "De hen dat cackle lay de egg.", "meaning": "The person who has made the outcry is the one responsible.", "page": 2, "section": "Proverbs Based on Animals", "why": "Cruise lines make the loudest noise — big ships, big passenger counts. But the stay-over visitor is the one laying the egg — staying overnight, spending in hotels, restaurants, and shops."},
    "year": {"text": "Mek-sure better dan cock-sure.", "meaning": "It is better to make absolutely sure that everything is alright, than to assume that all is well.", "page": 29, "section": "Proverbs Based on Human Relationships", "why": "Verify every figure. The 2022 and 2024 BSS revisions prove why this matters — preliminary numbers were revised upward and downward. Do not assume; check."},
    "country": {"text": "When yuh neighbour beard ketch fire, wet yuh own.", "meaning": "Take warning from the misfortune of others.", "page": 31, "section": "Proverbs Based on Nature", "why": "Watch the source market shifts. The UK remains dominant, but the USA and CARICOM are growing. Watch what is happening in other markets and prepare your own."},
    "cruise": {"text": "De sea en' got nuh back door.", "meaning": "The sea is not a safe place, as there is no guarantee that you will get back out.", "page": 32, "section": "Proverbs Based on Nature", "why": "Both visitor streams matter. Neither is an exit from the other. The cruise passenger and the stay-over visitor are two parts of the same tourism economy — and both must be counted and understood."},
    "divergence": {"text": "Cockroach en' had no right at hen party.", "meaning": "It is foolish to get oneself into situations with which one cannot cope.", "page": 1, "section": "Proverbs Based on Animals", "why": "The airport is not the tourist industry. It is the gate. Do not confuse the two. The airport counts everyone through the terminal; the BSS counts only the tourists. Each has its place — but they are not the same."},
    "conclusion": {"text": "Wha' do in de dark does come out in de light.", "meaning": "It is impossible to hide all of one's actions.", "page": 33, "section": "Proverbs Based on Nature", "why": "The numbers are public. The gap is visible. The truth will be seen. This dashboard simply puts the two sources side by side — and lets the reader see what they measure."},
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def format_number(n):
    if n is None:
        return "N/A"
    return f"{n:,.0f}"

def get_badge(source):
    if source == "traffic":
        return '<span class="data-scope-badge badge-traffic">📊 GAIA Inc. Traffic Statistics</span>'
    elif source == "bss":
        return '<span class="data-scope-badge badge-bss">📋 BSS Visitor Arrivals</span>'
    elif source == "revised":
        return '<span class="data-scope-badge badge-revised">📝 BSS Revised</span>'
    return ""

def render_proverb(key):
    p = PROVERBS[key]
    st.markdown(f"""
    <div class="proverb-card">
        <div style="color:#BFDBFE;font-size:0.75rem;">📖 Bajan Proverb · {p['section']}</div>
        <div class="proverb-text">"{p['text']}"</div>
        <div class="proverb-meaning">— {p['meaning']}</div>
        <div class="proverb-source">Source: "De Mortar-Pestle" by G. Addinton Forde (1987), p. {p['page']}</div>
        <div class="proverb-why">💡 <strong style="color:#FFC726;">Why this proverb fits:</strong> {p['why']}</div>
    </div>
    """, unsafe_allow_html=True)

def render_2018_reconciliation_note(compact=False):
    """Render the 2018 BSS reconciliation note.

    compact=True is used where a full table would crowd the view (e.g. the
    Monthly Data Explorer); it keeps the headline explanation and drops
    the per-source table.
    """
    headline = BSS_2018_RECONCILIATION["headline_used"]

    if compact:
        st.markdown(f"""
        <div class="issue-warning">
            <strong>⚠️ 2018 reconciliation note:</strong> BSS's 2018 publications
            disagree internally. Table 7 (Purpose of Visit) and the twelve monthly
            PDFs both give <strong>{headline:,.0f}</strong>; Table 5 (Country of
            Residence) and Table 8 (Length of Stay) both give <strong>678,538</strong>;
            the country Excel file sums to <strong>679,478</strong>. This dashboard
            uses the headline <strong>{headline:,.0f}</strong> throughout. The
            Country and Length-of-Stay splits shown elsewhere are BSS's as-printed
            figures and may differ by 1–941 from the headline.
        </div>
        """, unsafe_allow_html=True)
        return

    rows = ""
    for label, total, note in BSS_2018_RECONCILIATION["sources"]:
        diff = total - headline
        diff_txt = "—" if diff == 0 else f"{diff:+,.0f}"
        rows += f"""
        <tr>
            <td>{label}</td>
            <td class="num">{total:,.0f}</td>
            <td class="diff">{diff_txt}</td>
            <td>{note}</td>
        </tr>
        """

    st.markdown(f"""
    <div class="issue-warning">
        <strong>⚠️ 2018 BSS Reconciliation — Documented Discrepancy</strong><br>
        The Barbados Statistical Service's own 2018 publications disagree on the
        stay-over total. The dashboard uses the <strong>official headline of
        {headline:,.0f}</strong> — the figure printed in Table 7 (Purpose of Visit)
        and obtained by summing the twelve monthly PDFs, and the figure adopted in
        the BSS's 2015–2022 visitor arrivals table. Other 2018 splits are printed
        as BSS published them and do not reconcile exactly:
        <table class="recon-table" style="margin-top:8px;">
            <thead>
                <tr>
                    <th>Source</th>
                    <th style="text-align:right;">Printed Total</th>
                    <th style="text-align:right;">Difference</th>
                    <th>Note</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <div style="margin-top:6px; font-size:0.82rem;">
            <strong>How the dashboard handles it:</strong> the 2018 headline, the
            conversion rate, and every year-over-year comparison use
            <strong>{headline:,.0f}</strong>. The country and length-of-stay
            breakdowns use BSS's printed figures; where a split sums to 678,538 we
            carry the one-visitor difference on the "1 Day" length-of-stay row so
            the on-screen split still adds to the headline. The country Excel file
            (679,478) is flagged but not used — its sum is 941 above the printed
            annual total.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# VIEW: OVERVIEW
# ============================================================================
def render_overview():
    st.markdown(f"""
    <div class="main-header">✈️ Barbados Tourism Arrivals</div>
    <div class="main-subheader">Airport Traffic vs. Visitor Arrivals · 2018–{LATEST_PARTIAL_YEAR}</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#EFF6FF; color:#1E3A8A; padding:16px 20px; border-radius:10px; border-left:5px solid #00267F; margin:15px 0; border-top:1px solid #93C5FD; border-right:1px solid #93C5FD; border-bottom:1px solid #93C5FD;">
        <p style="margin:0; font-size:0.95rem; color:#1E3A8A; line-height:1.7;">
        <strong style="color:#1E3A8A;">The airport counts everyone through the terminal.</strong>
        The Barbados Statistical Service counts only the stay-over visitors.
        <strong style="color:#1E3A8A;">These are not the same number</strong> — and the gap between them is the story.
        </p>
        <p style="margin:8px 0 0 0; font-size:0.9rem; color:#1E3A8A; line-height:1.7; font-style:italic;">
        This dashboard does not claim that either number is wrong. It shows what each source measures, and how far apart they are.
        </p>
    </div>
    """, unsafe_allow_html=True)

    render_proverb("overview")

    # --- No-forecast principle box ---
    st.markdown("""
    <div class="issue-info" style="margin-top:10px;">
        <strong>🧭 A note on forecasting:</strong> This dashboard <em>reports</em> what has been published. It does <strong>not</strong> forecast.
        Forecasting arrivals from this data would require assumptions the data cannot support — monthly country splits, forward bookings, and visitor spend are not in these series.
        The value of what is shown here depends on not overclaiming what it can tell you. Every figure is traceable to a published source; see the captions and the <em>Monthly Data Explorer</em>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 📊 The Three Numbers — {LATEST_FULL_YEAR}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #3B82F6;">
            <div class="metric-label">GAIA Total Passengers</div>
            <div class="metric-value" style="color:#1D4ED8;">{format_number(GAIA_PASSENGERS[LATEST_FULL_YEAR])}</div>
            <div class="metric-context">{get_badge('traffic')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #10B981;">
            <div class="metric-label">BSS Stay-Over Arrivals</div>
            <div class="metric-value" style="color:#059669;">{format_number(BSS_STAY_OVER[LATEST_FULL_YEAR])}</div>
            <div class="metric-context">{get_badge('revised')} Full Year</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #F59E0B;">
            <div class="metric-label">BSS Cruise Arrivals</div>
            <div class="metric-value" style="color:#B45309;">{format_number(BSS_CRUISE[LATEST_FULL_YEAR])}</div>
            <div class="metric-context">{get_badge('bss')} Full Year</div>
        </div>
        """, unsafe_allow_html=True)

    gap = GAIA_PASSENGERS[LATEST_FULL_YEAR] - BSS_STAY_OVER[LATEST_FULL_YEAR]
    st.markdown(f"""
    <div class="issue-critical" style="margin-top:14px;">
        <strong>🔍 The Gap in {LATEST_FULL_YEAR}:</strong> {format_number(gap)} passengers passed through GAIA who were not stay-over visitors.
        That is more than the entire population of Barbados. The gap is the story.
    </div>
    """, unsafe_allow_html=True)

    # Conversion rate calculation
    pct_full = (BSS_STAY_OVER[LATEST_FULL_YEAR] / GAIA_PASSENGERS[LATEST_FULL_YEAR]) * 100
    pct_2018 = (BSS_STAY_OVER[2018] / GAIA_PASSENGERS[2018]) * 100
    pct_2022 = (BSS_STAY_OVER[2022] / GAIA_PASSENGERS[2022]) * 100
    pct_2023 = (BSS_STAY_OVER[2023] / GAIA_PASSENGERS[2023]) * 100
    pct_2024 = (BSS_STAY_OVER[2024] / GAIA_PASSENGERS[2024]) * 100

    yoy_delta = pct_full - pct_2024
    vs_2018_delta = pct_full - pct_2018

    if yoy_delta > 0:
        yoy_text = f"a marginal <strong>improvement</strong> of +{yoy_delta:.1f} pp over 2024"
    elif yoy_delta < 0:
        yoy_text = f"a marginal <strong>decline</strong> of {yoy_delta:.1f} pp versus 2024"
    else:
        yoy_text = "unchanged versus 2024"

    if vs_2018_delta < 0:
        vs_2018_text = f"{abs(vs_2018_delta):.1f} pp below the 2018 pre-COVID level ({pct_2018:.1f}%)"
    elif vs_2018_delta > 0:
        vs_2018_text = f"{vs_2018_delta:.1f} pp above the 2018 pre-COVID level ({pct_2018:.1f}%)"
    else:
        vs_2018_text = f"exactly at the 2018 pre-COVID level ({pct_2018:.1f}%)"

    st.markdown(f"""
    <div class="issue-warning" style="margin-top:10px;">
        <strong>📉 The Conversion Rate Story:</strong> Despite record-breaking airport traffic in {LATEST_FULL_YEAR} ({format_number(GAIA_PASSENGERS[LATEST_FULL_YEAR])}), the <em>percentage</em> of those passengers who were actual stay-over tourists was <strong>{pct_full:.1f}%</strong> — {yoy_text}, and {vs_2018_text}.<br><br>
        <strong>2018:</strong> {pct_2018:.1f}% | <strong>2022:</strong> {pct_2022:.1f}% | <strong>2023:</strong> {pct_2023:.1f}% | <strong>2024:</strong> {pct_2024:.1f}% | <strong>{LATEST_FULL_YEAR}:</strong> {pct_full:.1f}%
    </div>
    """, unsafe_allow_html=True)

    # Live 2026 YTD figures from dictionaries
    ytd_bss = BSS_STAY_OVER[LATEST_PARTIAL_YEAR]
    ytd_gaia = GAIA_PASSENGERS[LATEST_PARTIAL_YEAR]

    st.markdown(f"""
    <div class="issue-unknown" style="margin-top:10px;">
        <strong>📝 {LATEST_PARTIAL_YEAR} Data Note:</strong> The Barbados Statistical Service has published data for <strong>January to April {LATEST_PARTIAL_YEAR}</strong> ({format_number(ytd_bss)} stay-over arrivals). GAIA has published data for <strong>January to September {LATEST_PARTIAL_YEAR}</strong> ({format_number(ytd_gaia)} total passengers). The full {LATEST_PARTIAL_YEAR} analysis will be updated as more data becomes available.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 📈 The Divergence — 2018–{LATEST_FULL_YEAR}")
    # NOTE: Chart intentionally stops at the latest FULL year. 2026 is a partial
    # year in both series (GAIA Jan-Sept, BSS Jan-Apr) and plotting it alongside
    # full-year points would show a fake conversion collapse. See the callout above.
    years = [y for y in sorted(GAIA_PASSENGERS.keys()) if y <= LATEST_FULL_YEAR]
    gaia_vals = [GAIA_PASSENGERS[y] for y in years]
    bss_vals = [BSS_STAY_OVER[y] for y in years]
    cruise_vals = [BSS_CRUISE[y] for y in years]

    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(go.Scatter(x=years, y=gaia_vals, name="GAIA Total Passengers", line=dict(color="#3B82F6", width=3), mode="lines+markers", marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=years, y=bss_vals, name="BSS Stay-Over Arrivals", line=dict(color="#10B981", width=3), mode="lines+markers", marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=years, y=cruise_vals, name="BSS Cruise Arrivals", line=dict(color="#F59E0B", width=2, dash="dash"), mode="lines+markers", marker=dict(size=6)))
    fig.update_layout(
        height=420, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x unified", margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        title=f"Airport Traffic vs. Visitor Arrivals (2018–{LATEST_FULL_YEAR})",
    )
    fig.update_yaxes(title_text="Number of People", tickformat=",")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Note: 2019 BSS figures are Jan–Sept YTD only. 2022, 2023, 2024, and {LATEST_FULL_YEAR} BSS figures are revised. {LATEST_PARTIAL_YEAR} is partial-year data (BSS Jan–Apr, GAIA Jan–Sept) and is shown in the callout above, not on the chart.")

# ============================================================================
# VIEW: TWO VISITOR STREAMS
# ============================================================================
def render_streams():
    st.markdown("""
    <div class="main-header">🏝️ The Two Visitor Streams</div>
    <div class="main-subheader">Stay-Over vs. Cruise — two parts of the same tourism economy</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    render_proverb("streams")

    st.markdown("""
    <div class="issue-info">
        <strong>📌 The distinction:</strong> A <strong>stay-over visitor</strong> flies in, stays overnight, and spends money in hotels, restaurants, and shops. A <strong>cruise passenger</strong> arrives by ship — often for just a day — and may spend very little ashore. Both are counted by the BSS, but they are not the same visitor.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #10B981;">
            <div class="metric-label">Stay-Over Arrivals ({LATEST_FULL_YEAR})</div>
            <div class="metric-value" style="color:#059669;">{format_number(BSS_STAY_OVER[LATEST_FULL_YEAR])}</div>
            <div class="metric-context">Actual overnight visitors (full year, revised)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #F59E0B;">
            <div class="metric-label">Cruise Arrivals ({LATEST_FULL_YEAR})</div>
            <div class="metric-value" style="color:#B45309;">{format_number(BSS_CRUISE[LATEST_FULL_YEAR])}</div>
            <div class="metric-context">Cruise passengers (full year)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🚢 Intransit vs. Landed — 2024 vs. 2025")
    st.markdown("""
    <div style="background:#F8FAFC; padding:14px 18px; border-radius:10px; border:1px solid #E2E8F0;">
        <p style="margin:0; font-size:0.9rem; color:#1E293B; line-height:1.7;">
        <strong>Intransit passengers</strong> stay on the ship or pass through the terminal without formally entering the country.
        <strong>Landed passengers</strong> disembark and may spend time ashore.
        Both are counted in BSS cruise arrivals — but only landed passengers are potential spenders.
        </p>
    </div>
    """, unsafe_allow_html=True)

    cruise_data = [
        {"Year": "2024", "Type": "Intransit", "Passengers": 492725},
        {"Year": "2024", "Type": "Landed", "Passengers": 156400},
        {"Year": "2025", "Type": "Intransit", "Passengers": 546393},
        {"Year": "2025", "Type": "Landed", "Passengers": 192542},
    ]
    df_cruise = pd.DataFrame(cruise_data)

    fig = px.bar(
        df_cruise, x="Year", y="Passengers", color="Type", barmode="group",
        title="Cruise Arrivals: Intransit vs. Landed (2024 vs 2025)",
        color_discrete_map={"Intransit": "#3B82F6", "Landed": "#F59E0B"}
    )
    fig.update_layout(
        height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Passengers", yaxis_tickformat=",",
        legend_title_text="Passenger Type",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    fig.update_traces(
        hovertemplate="<b>Year: %{x}</b><br>Type: %{fullData.name}<br>Passengers: %{y:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# VIEW: YEAR-BY-YEAR EXPLORER
# ============================================================================
def render_year_explorer():
    st.markdown("""
    <div class="main-header">📅 Year-by-Year Explorer</div>
    <div class="main-subheader">Select a year to see the full picture</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    render_proverb("year")

    years = [2018, 2019, 2022, 2023, 2024, 2025, 2026]
    year = st.selectbox("Select Year", years, index=len(years)-2) # Default to latest full year

    st.markdown(f"## {year}")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #3B82F6;">
            <div class="metric-label">GAIA Total Passengers</div>
            <div class="metric-value" style="color:#1D4ED8;">{format_number(GAIA_PASSENGERS[year])}</div>
            <div class="metric-context">{get_badge('traffic')} {'(Jan-Sept YTD)' if year == 2026 else ''}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #10B981;">
            <div class="metric-label">BSS Stay-Over Arrivals</div>
            <div class="metric-value" style="color:#059669;">{format_number(BSS_STAY_OVER[year])}</div>
            <div class="metric-context">{get_badge('revised' if year in [2022, 2023, 2024, 2025] else 'bss')} {'(Jan-Apr YTD)' if year == 2026 else '(Jan-Sept YTD)' if year == 2019 else ''}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #F59E0B;">
            <div class="metric-label">BSS Cruise Arrivals</div>
            <div class="metric-value" style="color:#B45309;">{format_number(BSS_CRUISE[year])}</div>
            <div class="metric-context">{get_badge('bss')} {'(Jan-Apr YTD)' if year == 2026 else '(Jan-Sept YTD)' if year == 2019 else ''}</div>
        </div>
        """, unsafe_allow_html=True)

    if year == 2018:
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        render_2018_reconciliation_note()

    if year == 2019:
        st.markdown("""
        <div class="issue-warning" style="margin-top:20px;">
            <strong>⚠️ 2019 Data Note:</strong> The BSS bulletins for October, November, and December 2019 were not provided. The totals shown here reflect only the <strong>January to September</strong> period (520,881 stay-over and 557,171 cruise arrivals).
        </div>
        """, unsafe_allow_html=True)
    elif year == 2026:
        st.markdown(f"""
        <div class="issue-info" style="margin-top:20px;">
            <strong>📅 2026 Partial Year:</strong> The BSS has published data for <strong>January to April 2026</strong> ({format_number(BSS_STAY_OVER[2026])} stay-over arrivals). GAIA has published data for <strong>January to September 2026</strong> ({format_number(GAIA_PASSENGERS[2026])} passengers). Full sub-category breakdowns are pending BSS release.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 🌍 Stay-Over Arrivals by Country of Residence")
        if year == 2018:
            st.markdown("""
            <div class="issue-warning" style="margin-bottom:10px; font-size:0.85rem;">
                <strong>2018 split caveat:</strong> BSS Table 5 as printed sums to
                <strong>678,538</strong> (one more than the headline). The country
                Excel file sums to <strong>679,478</strong>. The chart below shows
                BSS's as-printed country rows — the headline used everywhere else
                in this dashboard is <strong>678,537</strong>.
            </div>
            """, unsafe_allow_html=True)
        country_data = BSS_BY_COUNTRY.get(year, {})
        if country_data:
            df_country = pd.DataFrame(list(country_data.items()), columns=["Country", "Arrivals"])
            df_country = df_country.sort_values("Arrivals", ascending=True)

            fig = px.bar(df_country, x="Arrivals", y="Country", orientation="h",
                         color="Arrivals", color_continuous_scale="Blues",
                         title=f"Stay-Over Arrivals by Country ({year})",
                         hover_data={"Arrivals": ":,.0f"},
                         text_auto='.0f')

            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              showlegend=False, coloraxis_showscale=False,
                              xaxis_tickformat=",")

            fig.update_traces(textfont_size=10, textangle=0, textposition="outside", cliponaxis=False)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Source: Barbados Statistical Service, Visitor Arrivals Statistics ({year})")

        st.markdown("### 🎯 Purpose of Visit")
        purpose_data = BSS_PURPOSE.get(year, {})
        if purpose_data:
            df_purpose = pd.DataFrame(list(purpose_data.items()), columns=["Purpose", "Arrivals"])
            df_purpose = df_purpose.sort_values("Arrivals", ascending=False)
            fig = px.pie(df_purpose, values="Arrivals", names="Purpose", hole=0.4,
                         title=f"Stay-Over Arrivals by Purpose of Visit ({year})",
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10,
                              hovertemplate="<b>%{label}</b><br>Arrivals: %{value:,.0f}<extra></extra>")
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Source: Barbados Statistical Service, Visitor Arrivals Statistics ({year})")

        st.markdown("### 📅 Length of Stay")
        length_data = BSS_LENGTH.get(year, {})
        if length_data:
            avg = length_data.pop("Avg", None)
            df_length = pd.DataFrame(list(length_data.items()), columns=["Category", "Arrivals"])

            if year == 2018:
                st.markdown("""
                <div class="issue-warning" style="margin-bottom:10px; font-size:0.85rem;">
                    <strong>2018 split caveat:</strong> BSS Table 8 as printed sums to
                    <strong>678,538</strong>. The "1 Day" row here carries the
                    one-visitor residual so this on-screen split reconciles to the
                    headline <strong>678,537</strong> used elsewhere.
                </div>
                """, unsafe_allow_html=True)

            fig = px.bar(df_length, x="Category", y="Arrivals",
                         title=f"Stay-Over Arrivals by Length of Stay ({year})",
                         color_discrete_sequence=["#00267F"],
                         hover_data={"Arrivals": ":,.0f"},
                         text_auto='.0f')

            fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              showlegend=False, yaxis_tickformat=",")

            fig.update_traces(textfont_size=10, textangle=0, textposition="outside", cliponaxis=False)
            st.plotly_chart(fig, use_container_width=True)

            if avg:
                st.markdown(f"""
                <div class="metric-card" style="border-left:4px solid #8B5CF6; max-width:280px;">
                    <div class="metric-label">Average Length of Stay</div>
                    <div class="metric-value" style="color:#6D28D9;">{avg:.1f} days</div>
                    <div class="metric-context">Per stay-over visitor</div>
                </div>
                """, unsafe_allow_html=True)
            st.caption(f"Source: Barbados Statistical Service, Visitor Arrivals Statistics ({year})")

# ============================================================================
# VIEW: COUNTRY BREAKDOWN
# ============================================================================
def render_country():
    st.markdown("""
    <div class="main-header">🌍 Country Breakdown</div>
    <div class="main-subheader">Where do Barbados' stay-over visitors come from?</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    render_proverb("country")

    st.markdown("""
    <div class="issue-info">
        <strong>📌 The dominant markets:</strong> The U.K., U.S.A., and Canada have consistently been the top three source markets. But CARICOM has grown significantly, and Other Europe and Latin/Central America are shifting. Watch the trends, not just the totals.
    </div>
    """, unsafe_allow_html=True)

    render_2018_reconciliation_note(compact=True)

    years = [2018, 2022, 2023, 2024, 2025]
    countries = ["U.K", "U.S.A", "Canada", "CARICOM", "Other Europe"]

    fig = go.Figure()
    colors = {"U.K": "#00267F", "U.S.A": "#3B82F6", "Canada": "#F59E0B", "CARICOM": "#10B981", "Other Europe": "#8B5CF6"}
    for country in countries:
        vals = [BSS_BY_COUNTRY[y].get(country, 0) for y in years]
        fig.add_trace(go.Scatter(x=years, y=vals, name=country,
                                 line=dict(color=colors[country], width=3), mode="lines+markers",
                                 hovertemplate=f"{country}: %{{y:,.0f}}<extra></extra>"))
    fig.update_layout(
        height=420, title="Stay-Over Arrivals by Major Source Market",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Arrivals", yaxis_tickformat=",",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Source: Barbados Statistical Service, Visitor Arrivals Statistics. 2019, 2020, and 2021 omitted because full-year breakdowns are not available or are pandemic-affected.")

    st.markdown(f"### 📊 {LATEST_FULL_YEAR} vs. 2018 — Market Shift")
    st.markdown("""
    <div class="issue-warning" style="font-size:0.85rem;">
        <strong>2018 baseline note:</strong> the 2018 column uses BSS Table 5's
        printed country rows (sum 678,538). The annual headline used elsewhere is
        678,537 — a one-visitor difference. Shares below are computed against each
        year's own printed total so the 2018 shares still sum to 100%.
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for c in countries:
        v2018 = BSS_BY_COUNTRY[2018].get(c, 0)
        v_latest = BSS_BY_COUNTRY[LATEST_FULL_YEAR].get(c, 0)
        change = v_latest - v2018
        pct = (change / v2018 * 100) if v2018 > 0 else 0

        total_2018 = sum(BSS_BY_COUNTRY[2018].values())
        total_latest = sum(BSS_BY_COUNTRY[LATEST_FULL_YEAR].values())
        pct_2018 = (v2018 / total_2018 * 100) if total_2018 > 0 else 0
        pct_latest = (v_latest / total_latest * 100) if total_latest > 0 else 0

        rows.append({
            "Market": c,
            "2018 Arrivals": f"{v2018:,.0f}",
            "2018 Share": f"{pct_2018:.1f}%",
            f"{LATEST_FULL_YEAR} Arrivals": f"{v_latest:,.0f}",
            f"{LATEST_FULL_YEAR} Share": f"{pct_latest:.1f}%",
            "Change": f"{change:+,.0f}",
            "% Change": f"{pct:+.1f}%"
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="issue-info">
        <strong>📌 Reading the table:</strong> The <strong>Share</strong> columns show the percentage of total stay-over arrivals that each market represented in that year. This shows how the market mix has shifted. For example, if the U.K.'s share dropped, but its absolute number grew, it means the other markets grew faster.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# VIEW: CRUISE VS. STAY-OVER
# ============================================================================
def render_cruise():
    st.markdown("""
    <div class="main-header">🛳️ Cruise vs. Stay-Over</div>
    <div class="main-subheader">The two visitor streams compared</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    render_proverb("cruise")

    # NOTE: Chart intentionally stops at the latest FULL year. 2026 is partial-year
    # in both series (BSS Jan-Apr) and would distort the grouped comparison.
    years = [y for y in sorted(BSS_STAY_OVER.keys()) if y <= LATEST_FULL_YEAR]
    stay_vals = [BSS_STAY_OVER[y] for y in years]
    cruise_vals = [BSS_CRUISE[y] for y in years]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=stay_vals, name="Stay-Over Arrivals", marker_color="#10B981", hovertemplate="Year: %{x}<br>Stay-Over: %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Bar(x=years, y=cruise_vals, name="Cruise Arrivals", marker_color="#F59E0B", hovertemplate="Year: %{x}<br>Cruise: %{y:,.0f}<extra></extra>"))
    fig.update_layout(
        barmode="group", height=420,
        title=f"Stay-Over vs. Cruise Arrivals (2018–{LATEST_FULL_YEAR})",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Arrivals", yaxis_tickformat=",",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Source: Barbados Statistical Service. 2019 is Jan–Sept YTD. 2023 and 2024 revised; 2026 is shown in the callout on the Overview, not on this chart.")

    st.markdown("### 📊 The Numbers Side by Side")
    rows = []
    for y in years:
        rows.append({
            "Year": y,
            "Stay-Over": f"{BSS_STAY_OVER[y]:,.0f}",
            "Cruise": f"{BSS_CRUISE[y]:,.0f}",
            "Total Visitors": f"{(BSS_STAY_OVER[y] + BSS_CRUISE[y]):,.0f}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="issue-warning">
        <strong>⚠️ The 2020–2021 collapse:</strong> Both streams collapsed in 2020 and 2021 due to COVID-19. Cruise was essentially zero in 2021. Both recovered strongly by 2025. The two streams move together — but they are not interchangeable.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# VIEW: AIRPORT TRAFFIC VS. VISITOR ARRIVALS
# ============================================================================
def render_divergence():
    st.markdown("""
    <div class="main-header">✈️ Airport Traffic vs. Visitor Arrivals</div>
    <div class="main-subheader">The gap that tells the story</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    render_proverb("divergence")

    # NOTE: Chart intentionally stops at the latest FULL year. 2026 is a partial
    # year in both series (GAIA Jan-Sept, BSS Jan-Apr) and would show a fake gap.
    years = [y for y in sorted(GAIA_PASSENGERS.keys()) if y <= LATEST_FULL_YEAR]
    gaia_vals = [GAIA_PASSENGERS[y] for y in years]
    bss_vals = [BSS_STAY_OVER[y] for y in years]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=gaia_vals, name="GAIA Total Passengers",
        line=dict(color="#3B82F6", width=3), mode="lines+markers",
        fill=None,
        hovertemplate="Year: %{x}<br>GAIA Passengers: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=years, y=bss_vals, name="BSS Stay-Over Arrivals",
        line=dict(color="#10B981", width=3), mode="lines+markers",
        fill="tonexty", fillcolor="rgba(245, 158, 11, 0.15)",
        hovertemplate="Year: %{x}<br>Stay-Over: %{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        height=450,
        title=f"Airport Traffic vs. Actual Tourists — The Divergence (2018–{LATEST_FULL_YEAR})",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Number of People", yaxis_tickformat=",",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div style="text-align:center; margin:10px 0 20px 0;">
        <span style="background:#FEF3C7; padding:6px 16px; border-radius:16px; font-size:0.85rem; font-weight:600; color:#92400E;">
        🟡 Shaded Area = Non-Tourist Passengers (locals, business travellers, transit, crew)
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 The Gap, Year by Year")
    rows = []
    for y in years:
        gap = GAIA_PASSENGERS[y] - BSS_STAY_OVER[y]
        pct = (BSS_STAY_OVER[y] / GAIA_PASSENGERS[y] * 100) if GAIA_PASSENGERS[y] > 0 else 0
        rows.append({
            "Year": y,
            "GAIA Passengers": f"{GAIA_PASSENGERS[y]:,.0f}",
            "BSS Stay-Over": f"{BSS_STAY_OVER[y]:,.0f}",
            "Gap (Non-Tourists)": f"{gap:,.0f}",
            "Stay-Over % of Airport Traffic": f"{pct:.1f}%"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="issue-info">
        <strong>📌 What this means:</strong> In every year shown, the GAIA total is significantly larger than the BSS stay-over total. The gap is not a flaw in either source — it is a reflection of what each source measures. GAIA counts everyone through the terminal. BSS counts only the overnight visitors. The difference is locals, business travellers, transit passengers, and crew.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="evidence-box">
        <div class="evidence-label">Sources</div>
        <div class="evidence-text">
        <strong>Airport Traffic:</strong> GAIA Inc. Passenger &amp; Cargo Statistics (website). Operational traffic reports, not audited financial statements.<br>
        <strong>Visitor Arrivals:</strong> Barbados Statistical Service, Visitor Arrivals Statistics (revised where applicable).<br><br>
        <em>This dashboard does not claim that either number is wrong. It shows what each source measures, and how far apart they are.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# VIEW: THE WORLD CUP CONTEXT
# ============================================================================
def render_worldcup():
    st.markdown("""
    <div class="main-header">🏏 The World Cup Context</div>
    <div class="main-subheader">A major event, a USD 25M loan, and the arrival numbers</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    render_proverb("year")

    st.markdown(f"""
    <div class="issue-info">
        <strong>📌 The context:</strong> In November 2023, the African Export-Import Bank
        (Afreximbank) extended a <strong>USD 25 million (BDS$50 million)</strong> term loan
        facility to <strong>Kensington Oval Management Inc. (KOMI)</strong>, backed by a
        <strong>guarantee from the Government of Barbados</strong>. The facility was used to
        rehabilitate and upgrade Kensington Oval ahead of the 2024 ICC Men's T20 World Cup
        (June 4–30, 2024). Barbados hosted the Final.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="evidence-box">
        <div class="evidence-label">Loan Terms — Verified</div>
        <div class="evidence-text">
        <strong>Lender:</strong> African Export-Import Bank (Afreximbank)<br>
        <strong>Borrower:</strong> Kensington Oval Management Inc. (KOMI)<br>
        <strong>Guarantor:</strong> Government of Barbados<br>
        <strong>Amount:</strong> USD 25,000,000 (BDS$50,000,000)<br>
        <strong>Signed:</strong> November 1, 2023, at ACTIF23, Georgetown, Guyana<br>
        <strong>Purpose:</strong> Rehabilitation and upgrade — Garfield Sobers Players' Pavilion,
        A/V and electrical systems, temporary stands — ahead of the 2024 ICC T20 World Cup<br>
        <strong>Interest:</strong> Concessionary rates
        </div>
        <div class="evidence-source">
        Sources: Afreximbank press release, 19 April 2024; Barbados Today, 1 November 2023.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 What Did the Arrival Numbers Actually Do?")

    world_cup_baseline = {
        2018: {"context": "Last normal pre-COVID year — no World Cup, no loan"},
        2023: {"context": "Year before the World Cup — loan signed in November"},
        2024: {"context": "World Cup year — Barbados hosted the Final"},
    }

    rows = []
    baseline_2018 = BSS_STAY_OVER[2018]
    for y in [2018, 2023, 2024]:
        arr = BSS_STAY_OVER[y]
        change = arr - baseline_2018
        pct = (change / baseline_2018 * 100) if baseline_2018 > 0 else 0
        if y == 2018:
            change_str = "—"
            pct_str = "—"
        else:
            change_str = f"{change:+,.0f}"
            pct_str = f"{pct:+.1f}%"
        rows.append({
            "Year": y,
            "Stay-Over Arrivals": f"{arr:,.0f}",
            "Change vs 2018": change_str,
            "% Change vs 2018": pct_str,
            "Context": world_cup_baseline[y]["context"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    delta_vs_2023 = BSS_STAY_OVER[2024] - BSS_STAY_OVER[2023]
    pct_vs_2023 = delta_vs_2023 / BSS_STAY_OVER[2023] * 100
    delta_vs_2018 = BSS_STAY_OVER[2024] - BSS_STAY_OVER[2018]
    pct_vs_2018 = delta_vs_2018 / BSS_STAY_OVER[2018] * 100

    st.markdown(f"""
    <div class="issue-warning" style="margin-top:14px;">
        <strong>⚠️ Two baselines, two sets of numbers:</strong><br>
        Against <strong>2023</strong> (the year before the World Cup), 2024 rose by
        <strong>{delta_vs_2023:+,.0f} visitors ({pct_vs_2023:+.1f}%)</strong>.<br>
        Against <strong>2018</strong> (the last normal pre-COVID year — no World Cup, no loan),
        2024 rose by <strong>{delta_vs_2018:+,.0f} visitors ({pct_vs_2018:+.1f}%)</strong>.<br>
        Both are accurate depending on the baseline chosen.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="issue-info" style="margin-top:10px;">
        <strong>📌 Update:</strong> Since the World Cup year, arrivals have continued to grow.
        In {LATEST_FULL_YEAR} — the latest full year in this dashboard — stay-over arrivals reached
        <strong>{BSS_STAY_OVER[LATEST_FULL_YEAR]:,.0f}</strong>, and GAIA total passengers reached <strong>{GAIA_PASSENGERS[LATEST_FULL_YEAR]:,.0f}</strong>.
        The full series is on the <em>Overview</em> page.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 What This Data Cannot Tell You")

    st.markdown("""
    <div class="issue-unknown">
        <strong>1. Arrivals are not impact.</strong> A stay-over visitor's spend varies enormously
        by length of stay, purpose, and source market. This dashboard counts heads, not dollars.
        A World Cup visitor may spend more per day than a winter sun-seeker — or less.
    </div>
    <div class="issue-unknown">
        <strong>2. Causation is not established.</strong> Airlift, source-market economics, cruise
        deployment, hotel capacity, and global travel demand all move arrivals. No single cause
        — not the World Cup, not the loan — can be isolated from this data.
    </div>
    <div class="issue-unknown">
        <strong>3. Some benefits don't show up in arrivals at all.</strong> Global broadcast
        exposure, future bookings, cruise calls, and the legacy use of a renovated venue
        are not captured by a stay-over headcount.
    </div>
    <div class="issue-unknown">
        <strong>4. The loan is a liability, not a cost.</strong> The USD 25M is a term loan
        (concessionary rate), not a grant. The Government of Barbados guaranteed it. Whether
        the guarantee is ever called, and whether the venue's future revenue services the loan,
        are questions for the fiscal accounts — not the arrivals statistics.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="evidence-box">
        <div class="evidence-label">Sources</div>
        <div class="evidence-text">
        <strong>Loan:</strong> Afreximbank press release, 19 April 2024 — "Afreximbank Supports
        Rehabilitation of Sporting Facility in Barbados Ahead of the 2024 Cricket World Cup."<br>
        <strong>Loan (signing):</strong> Barbados Today, 1 November 2023 — "Loan signed for
        Kensington Oval upgrade."<br>
        <strong>Arrivals:</strong> Barbados Statistical Service, Visitor Arrivals Statistics
        (2018, 2023, 2024; 2024 revised per BSS revision note).<br><br>
        <em>This section presents factual context and arrival figures. It does not assess the return on investment or the success of the event.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# VIEW: MONTHLY DATA EXPLORER
# ============================================================================
def render_monthly():
    st.markdown("""
    <div class="main-header">🗓️ Monthly Data Explorer</div>
    <div class="main-subheader">Month-by-month validation of annual totals</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="issue-info">
        <strong>📌 Data Integrity:</strong> This view displays the raw monthly figures used to calculate the annual totals. Where months are missing (e.g., 2019 Q4, 2026 partial year), it is explicitly noted. This allows you to verify that the annual sums are correct.
    </div>
    """, unsafe_allow_html=True)

    render_2018_reconciliation_note(compact=True)

    data_type = st.radio("Select Data Source", ["GAIA Passengers", "BSS Stay-Over Arrivals", "BSS Cruise Arrivals"], horizontal=True)

    if data_type == "GAIA Passengers":
        df = pd.DataFrame(GAIA_MONTHLY).T
        title = "GAIA Monthly Passenger Totals"
    elif data_type == "BSS Stay-Over Arrivals":
        df = pd.DataFrame(BSS_STAY_OVER_MONTHLY).T
        title = "BSS Monthly Stay-Over Arrivals"
    else:
        df = pd.DataFrame(BSS_CRUISE_MONTHLY).T
        title = "BSS Monthly Cruise Arrivals"

    df.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    df["Annual Total"] = df.sum(axis=1, min_count=1)
    df_formatted = df.apply(lambda col: col.map(lambda x: f"{x:,.0f}" if pd.notnull(x) else "—"))

    st.markdown(f"### {title}")
    st.dataframe(df_formatted, use_container_width=True)

    if data_type == "BSS Stay-Over Arrivals":
        st.markdown("""
        <div class="issue-warning">
            <strong>⚠️ Note on missing data:</strong> 2019 only has Jan–Sept data. 2026 only has Jan–Apr data.
            <br><br>
            <strong>⚠️ 2018 note:</strong> the twelve monthly stay-over figures sum to
            <strong>678,537</strong>, which is the headline used throughout this
            dashboard. The BSS's 2018 country and length-of-stay tables print
            <strong>678,538</strong> and the country Excel file sums to
            <strong>679,478</strong> — see the reconciliation note above.
        </div>
        """, unsafe_allow_html=True)
    elif data_type == "BSS Cruise Arrivals":
        st.markdown("""
        <div class="issue-warning">
            <strong>⚠️ Note on missing data:</strong> 2019 only has Jan–Sept data. 2026 only has Jan–Apr data.
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# VIEW: CONCLUSION
# ============================================================================
def render_conclusion():
    st.markdown("""
    <div class="main-header">📖 Conclusion</div>
    <div class="barbados-flag-bar"></div>
    """, unsafe_allow_html=True)

    render_proverb("conclusion")

    st.markdown(f"""
    <div class="conclusion-section">
        <h2>The Numbers Tell a Story</h2>
        <p style="font-size:1.05rem; color:#DBEAFE;">
        The GAIA total passenger count is not the same as the BSS stay-over arrival count. 
        They never have been. And they never will be.
        </p>
        <p style="color:#F1F5F9;">
        The airport counts everyone through the terminal — locals, business travellers, transit passengers, crew, and tourists. 
        The BSS counts only the stay-over visitors — the people who flew in and stayed overnight.
        </p>
        <p style="color:#F1F5F9;">
        In {LATEST_FULL_YEAR}, over <strong>{GAIA_PASSENGERS[LATEST_FULL_YEAR]/1e6:.2f} million</strong> people passed through GAIA. But only <strong>{BSS_STAY_OVER[LATEST_FULL_YEAR]:,.0f}</strong> were stay-over visitors. 
        The gap is more than the entire population of Barbados.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #00267F 0%, #1E40AF 100%); 
                padding: 20px 25px; border-radius: 12px; border-left: 6px solid #FFC726; 
                margin: 15px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="color: #FFC726; margin-top: 0; font-size: 1.3rem;">🏏 The 2024 World Cup Year</h3>
        <p style="color: #F1F5F9; font-size: 0.95rem; line-height: 1.6;">
        In June 2024, Barbados hosted the ICC Men's T20 World Cup Final. The airport saw a record 2.37 million passengers for the year. 
        Stay-over tourism also grew: arrivals rose to <strong>696,531</strong>, a <strong>+9.4% increase</strong> over 2023 (636,540), once the revised December 2024 figure is included.
        <br><br>
        In November 2023, Afreximbank extended a <strong>USD 25 million loan</strong> to Kensington Oval Management Inc. — guaranteed by the Government of Barbados — to prepare the venue. Against 2018, the last normal pre-COVID year, 2024's arrivals were <strong>+2.7% higher</strong>. 
        See <em>The World Cup Context</em> for the specific arrival numbers across these baselines.
        <br><br>
        Since then, {LATEST_FULL_YEAR} arrivals reached <strong>{BSS_STAY_OVER[LATEST_FULL_YEAR]:,.0f}</strong> against GAIA total passengers of <strong>{GAIA_PASSENGERS[LATEST_FULL_YEAR]:,.0f}</strong> — a conversion rate of {(BSS_STAY_OVER[LATEST_FULL_YEAR]/GAIA_PASSENGERS[LATEST_FULL_YEAR]*100):.1f}%.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="conclusion-section" style="margin-top: 0; border-top-left-radius: 0; border-top-right-radius: 0;">
        <p style="color:#FFC726; font-weight:700; font-size:1.15rem; line-height:1.5; margin-bottom: 0;">
        This is not a criticism of either source.<br>
        It is simply what happens when you measure two different things.<br>
        The airport measures traffic. The BSS measures tourism.<br>
        Both are true. They are just not the same.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="evidence-box">
        <div class="evidence-label">Data Sources</div>
        <div class="evidence-text">
        <strong>GAIA Total Passengers:</strong> GAIA Inc. Passenger &amp; Cargo Statistics (website). Operational traffic reports, not audited financial statements.<br>
        <strong>BSS Stay-Over and Cruise Arrivals:</strong> Barbados Statistical Service, Visitor Arrivals Statistics (revised where applicable — see 2022, 2023, 2024, and 2025 revision notes).<br>
        <strong>2018 reconciliation:</strong> Headline 678,537 taken from Table 7 (Purpose of Visit) and the monthly PDFs. Table 5 (Country) and Table 8 (Length of Stay) print 678,538; the country Excel file sums to 679,478. See the reconciliation note on the Year-by-Year Explorer.<br>
        <strong>2019:</strong> BSS figures are Jan–Sept YTD only. October–December 2019 bulletins were not available.<br>
        <strong>2026:</strong> BSS data is Jan–Apr YTD. GAIA data is Jan–Sept YTD. Full sub-category breakdowns are pending release.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F8F5F0; padding:20px 24px; border-radius:10px; border:2px solid #00267F; margin:20px 0;">
        <h4 style="color:#00267F; margin-bottom:8px;">📖 About This Dashboard</h4>
        <p style="color:#1E293B; margin-bottom:8px;"><strong>Author &amp; Compiler:</strong> Matthew A. A. Blackman</p>
        <p style="color:#1E293B; margin-bottom:8px;"><strong>Data Sources:</strong> GAIA Inc. Passenger &amp; Cargo Statistics (website); Barbados Statistical Service, Visitor Arrivals Statistics.</p>
        <p style="color:#1E293B; margin-bottom:8px;"><strong>Proverbs:</strong> "De Mortar-Pestle" by G. Addinton Forde (1987). All page numbers verified against source.</p>
        <p style="color:#1E293B; margin-bottom:0;"><strong>Dedication:</strong> To the people of Barbados — who deserve to see the numbers clearly, and understand what they measure.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# DOWNLOAD FUNCTIONS
# ============================================================================
def generate_csv():
    rows = []
    for year in sorted(GAIA_MONTHLY.keys()):
        for month in range(1, 13):
            month_name = datetime(2000, month, 1).strftime('%b')
            gaia_val = GAIA_MONTHLY.get(year, {}).get(month, None)
            stay_val = BSS_STAY_OVER_MONTHLY.get(year, {}).get(month, None)
            cruise_val = BSS_CRUISE_MONTHLY.get(year, {}).get(month, None)
            rows.append({
                "Year": year,
                "Month": month_name,
                "Month_Num": month,
                "GAIA_Total_Passengers": gaia_val,
                "BSS_StayOver_Arrivals": stay_val,
                "BSS_Cruise_Arrivals": cruise_val
            })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def generate_html_summary():
    years = sorted(GAIA_PASSENGERS.keys())
    rows_main = ""
    for y in years:
        gap = GAIA_PASSENGERS[y] - BSS_STAY_OVER[y]
        pct = (BSS_STAY_OVER[y] / GAIA_PASSENGERS[y] * 100) if GAIA_PASSENGERS[y] > 0 else 0
        rows_main += f"""
        <tr>
            <td>{y}</td>
            <td>{GAIA_PASSENGERS[y]:,.0f}</td>
            <td>{BSS_STAY_OVER[y]:,.0f}</td>
            <td>{BSS_CRUISE[y]:,.0f}</td>
            <td>{gap:,.0f}</td>
            <td>{pct:.1f}%</td>
        </tr>
        """

    country_years = [2018, 2022, 2023, 2024, 2025]
    countries = ["U.K", "U.S.A", "Canada", "CARICOM", "Other Europe", "Other Caribbean", "Latin/Central America", "Africa", "Asia", "Oceania", "Other"]
    country_header = "<tr><th>Country</th>"
    for y in country_years:
        country_header += f"<th>{y} Arrivals</th><th>{y} %</th>"
    country_header += "</tr>"
    country_body = ""
    for c in countries:
        country_body += f"<tr><td>{c}</td>"
        for y in country_years:
            val = BSS_BY_COUNTRY.get(y, {}).get(c, 0)
            total = sum(BSS_BY_COUNTRY.get(y, {}).values())
            pct = (val / total * 100) if total > 0 else 0
            country_body += f"<td>{val:,.0f}</td><td>{pct:.1f}%</td>"
        country_body += "</tr>"

    # Dynamically build purpose table to handle BSS schema changes
    purpose_years = [2018, 2022, 2023, 2024, 2025]
    all_purposes = set()
    for y in purpose_years:
        if y in BSS_PURPOSE:
            all_purposes.update(BSS_PURPOSE[y].keys())
    purposes = sorted(list(all_purposes))
    
    purpose_header = "<tr><th>Purpose</th>"
    for y in purpose_years:
        purpose_header += f"<th>{y} Arrivals</th><th>{y} %</th>"
    purpose_header += "</tr>"
    purpose_body = ""
    for p in purposes:
        purpose_body += f"<tr><td>{p}</td>"
        for y in purpose_years:
            val = BSS_PURPOSE.get(y, {}).get(p, 0)
            total = sum(BSS_PURPOSE.get(y, {}).values())
            pct = (val / total * 100) if total > 0 else 0
            purpose_body += f"<td>{val:,.0f}</td><td>{pct:.1f}%</td>"
        purpose_body += "</tr>"

    # Dynamically build length of stay table
    length_years = [2018, 2022, 2023, 2024, 2025]
    all_lengths = set()
    for y in length_years:
        if y in BSS_LENGTH:
            all_lengths.update(k for k in BSS_LENGTH[y].keys() if k != "Avg")
    
    # Sort lengths chronologically
    def length_sort_key(val):
        if val == "1 Day": return 1
        if val == "2-3 Days": return 2
        if val == "4-7 Days": return 3
        if val == "8-14 Days": return 4
        if val == "15-21 Days": return 5
        if val == "22-28 Days": return 6
        if val == "29-182 Days": return 7
        return 8

    lengths = sorted(list(all_lengths), key=length_sort_key)
    
    length_header = "<tr><th>Category</th>"
    for y in length_years:
        length_header += f"<th>{y} Arrivals</th><th>{y} %</th>"
    length_header += "</tr>"
    length_body = ""
    for l in lengths:
        length_body += f"<tr><td>{l}</td>"
        for y in length_years:
            val = BSS_LENGTH.get(y, {}).get(l, 0)
            total = sum(v for k, v in BSS_LENGTH.get(y, {}).items() if k != "Avg")
            pct = (val / total * 100) if total > 0 else 0
            length_body += f"<td>{val:,.0f}</td><td>{pct:.1f}%</td>"
        length_body += "</tr>"
    length_body += "<tr style='font-weight:bold;'><td>Average (days)</td>"
    for y in length_years:
        avg = BSS_LENGTH.get(y, {}).get("Avg", 0)
        length_body += f"<td>{avg:.1f}</td><td>-</td>"
    length_body += "</tr>"

    pct_2018 = (BSS_STAY_OVER[2018] / GAIA_PASSENGERS[2018]) * 100
    pct_2022 = (BSS_STAY_OVER[2022] / GAIA_PASSENGERS[2022]) * 100
    pct_2023 = (BSS_STAY_OVER[2023] / GAIA_PASSENGERS[2023]) * 100
    pct_2024 = (BSS_STAY_OVER[2024] / GAIA_PASSENGERS[2024]) * 100
    pct_2025 = (BSS_STAY_OVER[2025] / GAIA_PASSENGERS[2025]) * 100

    yoy_delta = pct_2025 - pct_2024
    if yoy_delta > 0:
        yoy_word = "improvement"
    elif yoy_delta < 0:
        yoy_word = "decline"
    else:
        yoy_word = "no change"
    vs_2018_delta = pct_2025 - pct_2018
    vs_2018_word = "below" if vs_2018_delta < 0 else ("above" if vs_2018_delta > 0 else "at")

    # Methodology note for Purpose of Visit
    methodology_note = """
    <div style="background-color: #F8FAFC; border-left: 4px solid #64748B; padding: 10px 14px; margin-bottom: 12px; font-size: 0.8rem; color: #475569;">
        <strong>📌 Note on Purpose of Visit:</strong> The BSS changed its reporting methodology over time. For consistency, this table applies the consolidated methodology used in <strong>2023, 2024, and 2025</strong> (grouping sub-categories into a single "Recreation" total) to the data for <strong>2018 and 2022</strong>. This allows for a direct year-over-year comparison across all years.
    </div>
    """

    # 2018 reconciliation block (HTML)
    recon_rows = ""
    for label, total, note in BSS_2018_RECONCILIATION["sources"]:
        diff = total - BSS_2018_RECONCILIATION["headline_used"]
        diff_txt = "—" if diff == 0 else f"{diff:+,.0f}"
        recon_rows += f"<tr><td>{label}</td><td style='text-align:right;'>{total:,.0f}</td><td style='text-align:right; font-weight:bold;'>{diff_txt}</td><td>{note}</td></tr>"

    recon_block = f"""
    <h2>0. Data Reconciliation — 2018</h2>
    <div class="recon">
        <strong>⚠️ 2018 BSS Reconciliation — Documented Discrepancy</strong><br>
        The Barbados Statistical Service's own 2018 publications disagree on the stay-over total.
        This summary uses the <strong>official headline of {BSS_2018_RECONCILIATION['headline_used']:,}</strong>
        — the figure printed in Table 7 (Purpose of Visit) and obtained by summing the twelve
        monthly PDFs, and the figure adopted in the BSS's 2015–2022 visitor arrivals table.
        Other 2018 splits are printed as BSS published them and do not reconcile exactly:
        <table style="margin-top:8px;">
            <thead><tr><th>Source</th><th style="text-align:right;">Printed Total</th><th style="text-align:right;">Difference</th><th>Note</th></tr></thead>
            <tbody>{recon_rows}</tbody>
        </table>
        <div style="margin-top:8px; font-size:0.82rem;">
            <strong>How this summary handles it:</strong> the 2018 headline, the conversion rate, and every
            year-over-year comparison use <strong>{BSS_2018_RECONCILIATION['headline_used']:,}</strong>.
            The country and length-of-stay breakdowns below use BSS's printed figures; where a split
            sums to 678,538 the one-visitor difference is carried on the "1 Day" length-of-stay row so
            the split still adds to the headline. The country Excel file (679,478) is flagged but not
            used — its sum is 941 above the printed annual total.
        </div>
    </div>
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Barbados Tourism Arrivals Summary</title>
    <style>
        body {{ font-family: Georgia, serif; background: #F5F0E8; color: #0F172A; line-height: 1.6; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 30px; background: #FFFCF7; }}
        h1 {{ color: #00267F; text-align: center; }}
        h2 {{ color: #00267F; border-bottom: 2px solid #FFC726; padding-bottom: 4px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.82rem; }}
        th {{ background: #00267F; color: white; padding: 8px 10px; text-align: left; }}
        td {{ padding: 6px 10px; border-bottom: 1px solid #E0D6C8; }}
        tr:nth-child(even) {{ background: #F8F5F0; }}
        .proverb {{ background: #00267F; color: white; padding: 16px 20px; border-radius: 10px; border-left: 5px solid #FFC726; margin: 16px 0; }}
        .proverb-text {{ font-size: 1.1rem; font-style: italic; color: #FFC726; font-weight: 600; }}
        .proverb-meaning {{ color: #DBEAFE; font-size: 0.85rem; }}
        .proverb-source {{ color: #BFDBFE; font-size: 0.7rem; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 3px solid #00267F; text-align: center; font-size: 0.8rem; color: #475569; }}
        .note {{ background: #FEF3C7; color: #78350F; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #F59E0B; margin: 16px 0; font-size: 0.85rem; }}
        .growth {{ background: #ECFDF5; color: #064E3B; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #10B981; margin: 16px 0; font-size: 0.85rem; border: 1px solid #6EE7B7; }}
        .conversion {{ background: #FFFBEB; color: #78350F; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #F59E0B; margin: 16px 0; font-size: 0.85rem; border: 1px solid #FCD34D; }}
        .principle {{ background: #EFF6FF; color: #1E3A8A; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #3B82F6; margin: 16px 0; font-size: 0.85rem; border: 1px solid #93C5FD; }}
        .worldcup {{ background: #EFF6FF; color: #1E3A8A; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #3B82F6; margin: 16px 0; font-size: 0.85rem; border: 1px solid #93C5FD; }}
        .recon {{ background: #FEF3C7; color: #78350F; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #F59E0B; margin: 16px 0; font-size: 0.85rem; border: 1px solid #FCD34D; }}
        .recon table th {{ background: #92400E; }}
        .dedication {{ margin-top: 20px; padding: 15px; background: #F8F5F0; border-radius: 8px; text-align: center; font-style: italic; color: #00267F; font-weight: bold; }}
    </style></head>
    <body><div class="container">
        <h1>✈️ Barbados Tourism Arrivals</h1>
        <p style="text-align:center; font-style:italic; color:#475569;">Airport Traffic vs. Visitor Arrivals · 2018–2026</p>
        <div class="proverb">
            <div class="proverb-text">"Duh is more in de mortar dan de pestle."</div>
            <div class="proverb-meaning">— There is more to the issue than appears on the surface.</div>
            <div class="proverb-source">Source: "De Mortar-Pestle" by G. Addinton Forde (1987), p. 16</div>
        </div>

        <div class="principle">
            <strong>🧭 This summary reports; it does not forecast.</strong> The figures below are drawn from published GAIA and BSS data and are labelled with their scope (full year / YTD / revised). No projection is included, because arrivals cannot be forecast reliably from these series alone — monthly country splits, forward bookings, and visitor spend are not in the data.
        </div>

        {recon_block}

        <h2>1. GAIA vs. BSS — The Main Numbers</h2>
        <table>
            <thead><tr><th>Year</th><th>GAIA Passengers</th><th>BSS Stay-Over</th><th>BSS Cruise</th><th>Gap (Non-Tourists)</th><th>Stay-Over %</th></tr></thead>
            <tbody>{rows_main}</tbody>
        </table>

        <div class="growth">
            <strong>✅ 2025 Was a Year of Growth:</strong> Stay-over arrivals rose to <strong>707,046</strong>, a <strong>+1.5% increase</strong> over 2024 (696,531). The airport also saw a record 2.41 million passengers.
        </div>

        <div class="conversion">
            <strong>📉 The Conversion Rate Story:</strong> Despite record-breaking airport traffic in 2025, the percentage of airport passengers who were actual stay-over tourists was <strong>{pct_2025:.1f}%</strong> — a marginal <strong>{yoy_word}</strong> versus 2024 ({pct_2024:.1f}%), and {abs(vs_2018_delta):.1f} pp {vs_2018_word} the 2018 pre-COVID level ({pct_2018:.1f}%).<br><br>
            <strong>2018:</strong> {pct_2018:.1f}% | <strong>2022:</strong> {pct_2022:.1f}% | <strong>2023:</strong> {pct_2023:.1f}% | <strong>2024:</strong> {pct_2024:.1f}% | <strong>2025:</strong> {pct_2025:.1f}%
        </div>

        <div class="note">
            <strong>📝 2026 Data Note:</strong> The Barbados Statistical Service has published data for <strong>January to April 2026</strong> ({BSS_STAY_OVER[2026]:,.0f} stay-over arrivals). GAIA has published data for <strong>January to September 2026</strong> ({GAIA_PASSENGERS[2026]:,.0f} total passengers). The full 2026 analysis will be updated as more data becomes available.
        </div>

        <div class="worldcup">
            <strong>🏏 The 2024 World Cup Context:</strong> In June 2024, Barbados hosted the ICC Men's T20 World Cup Final. The airport saw a record 2.37 million passengers for the year. Stay-over tourism also grew: arrivals rose to <strong>696,531</strong>, a <strong>+9.4% increase</strong> over 2023 (636,540), once the revised December 2024 figure is included.
            <br><br>
            In November 2023, Afreximbank extended a <strong>USD 25 million loan</strong> (BDS$50 million) to Kensington Oval Management Inc. (KOMI), guaranteed by the Government of Barbados, to rehabilitate the venue ahead of the event. Signed 1 November 2023. Against 2018 — the last normal pre-COVID year, with no World Cup and no loan — 2024's arrivals were <strong>+2.7% higher</strong> (+17,993 visitors). Against 2023, they were <strong>+9.4% higher</strong>. Both are accurate depending on the baseline chosen.
        </div>

        <h2>2. Stay-Over Arrivals by Country of Residence</h2>
        <div class="note" style="font-size:0.8rem;">
            <strong>2018 split caveat:</strong> BSS Table 5 as printed sums to <strong>678,538</strong>
            (one more than the headline); the country Excel file sums to <strong>679,478</strong>.
            Shares below are computed against each year's own printed total so each column sums to 100%.
        </div>
        <table>
            <thead>{country_header}</thead>
            <tbody>{country_body}</tbody>
        </table>

        <h2>3. Stay-Over Arrivals by Purpose of Visit</h2>
        {methodology_note}
        <div class="note" style="font-size:0.8rem;">
            <strong>2018 purpose split:</strong> BSS Table 7 as printed sums to <strong>678,537</strong> — this matches the headline used throughout the summary.
        </div>
        <table>
            <thead>{purpose_header}</thead>
            <tbody>{purpose_body}</tbody>
        </table>

        <h2>4. Stay-Over Arrivals by Length of Stay</h2>
        <div class="note" style="font-size:0.8rem;">
            <strong>2018 length-of-stay caveat:</strong> BSS Table 8 as printed sums to <strong>678,538</strong>.
            The "1 Day" row in the table below carries the one-visitor difference so the split reconciles
            to the headline <strong>678,537</strong> used elsewhere.
        </div>
        <table>
            <thead>{length_header}</thead>
            <tbody>{length_body}</tbody>
        </table>

        <h2>5. Sources</h2>
        <p><strong>GAIA Total Passengers:</strong> GAIA Inc. Passenger &amp; Cargo Statistics (website). Operational traffic reports, not audited financial statements.</p>
        <p><strong>BSS Stay-Over and Cruise Arrivals:</strong> Barbados Statistical Service, Visitor Arrivals Statistics (revised where applicable).</p>
        <p><strong>2018 reconciliation:</strong> Headline 678,537 taken from Table 7 (Purpose of Visit) and the monthly PDFs. Table 5 (Country) and Table 8 (Length of Stay) print 678,538; the country Excel file sums to 679,478.</p>
        <p><strong>Kensington Oval Loan:</strong> Afreximbank press release, 19 April 2024; Barbados Today, 1 November 2023 — USD 25M (BDS$50M) term loan from Afreximbank to KOMI, guaranteed by the Government of Barbados.</p>
        <p><strong>2019:</strong> BSS figures are Jan–Sept YTD only.</p>
        <p><strong>2026:</strong> BSS data is Jan–Apr YTD. GAIA data is Jan–Sept YTD. Full sub-category breakdowns pending BSS release.</p>

        <div class="footer">
            <p><strong>Barbados Tourism Arrivals — Airport Traffic vs. Visitor Arrivals</strong></p>
            <p>Author &amp; Compiler: Matthew A. A. Blackman</p>
            <p>Proverbs from "De Mortar-Pestle" by G. Addinton Forde (1987)</p>
            <p style="font-size:0.7rem; color:#64748B; font-style:italic;">
                This summary reports what has been published. It does not forecast. It shows what each source measures, and how far apart they are.
            </p>
            <div class="dedication">
                Dedication: To the people of Barbados — who deserve to see the numbers clearly, and understand what they measure.
            </div>
        </div>
    </div></body></html>
    """
    return html

def render_download():
    st.markdown("---")
    st.markdown("### 📥 Download")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Download Summary (HTML)", use_container_width=True):
            html = generate_html_summary()
            b64 = base64.b64encode(html.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="barbados_tourism_arrivals_summary.html" style="display:block; background:#059669; color:#FFFFFF; text-align:center; padding:10px; border-radius:6px; text-decoration:none; font-weight:600;">✅ Click to Download Summary</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Summary ready! Click the green button above to download.")
    with col2:
        if st.button("📊 Download Data (CSV)", use_container_width=True):
            csv = generate_csv()
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="barbados_tourism_arrivals_data.csv" style="display:block; background:#059669; color:#FFFFFF; text-align:center; padding:10px; border-radius:6px; text-decoration:none; font-weight:600;">✅ Click to Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Data ready! Click the green button above to download.")

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("## ✈️ Barbados Tourism Arrivals")
    st.markdown("### Navigation")
    views = [
        "📊 Overview",
        "🏝️ The Two Visitor Streams",
        "📅 Year-by-Year Explorer",
        "🌍 Country Breakdown",
        "🛳️ Cruise vs. Stay-Over",
        "✈️ Airport Traffic vs. Visitor Arrivals",
        "🏏 The World Cup Context",
        "🗓️ Monthly Data Explorer",
        "📖 Conclusion",
    ]
    view = st.selectbox("Select View", views, index=0)
    st.markdown("---")
    render_download()
    st.markdown("---")
    st.markdown("""
    <div style="background:#F8F5F0; padding:12px 14px; border-radius:8px; border:1px solid #00267F;">
        <div style="font-size:0.75rem; color:#00267F; font-weight:700;">📖 About</div>
        <div style="font-size:0.75rem; color:#1E293B; margin-top:4px;">
            Author &amp; Compiler: Matthew A. A. Blackman<br>
            Sources: GAIA Inc. Passenger &amp; Cargo Statistics; BSS Visitor Arrivals Statistics<br>
            Proverbs: "De Mortar-Pestle" by G. Addinton Forde (1987)
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT ROUTING
# ============================================================================
if view == "📊 Overview":
    render_overview()
elif view == "🏝️ The Two Visitor Streams":
    render_streams()
elif view == "📅 Year-by-Year Explorer":
    render_year_explorer()
elif view == "🌍 Country Breakdown":
    render_country()
elif view == "🛳️ Cruise vs. Stay-Over":
    render_cruise()
elif view == "✈️ Airport Traffic vs. Visitor Arrivals":
    render_divergence()
elif view == "🏏 The World Cup Context":
    render_worldcup()
elif view == "🗓️ Monthly Data Explorer":
    render_monthly()
elif view == "📖 Conclusion":
    render_conclusion()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"""
**Barbados Tourism Arrivals — Airport Traffic vs. Visitor Arrivals (Free Public Edition — no forecast)**
**Airport Traffic Source:** GAIA Inc. Passenger & Cargo Statistics (website). Operational traffic reports, not audited financial statements.
**Visitor Arrivals Source:** Barbados Statistical Service, Visitor Arrivals Statistics (revised where applicable — see 2022, 2023, 2024, and 2025 revision notes). 2019 BSS figures are Jan–Sept YTD only. 2026 BSS data is Jan–Apr YTD. GAIA 2026 data is Jan–Sept YTD.
**2018 Reconciliation:** Headline 678,537 (Table 7 + monthly PDFs). Table 5 (Country) and Table 8 (Length of Stay) print 678,538; the country Excel file sums to 679,478. Documented on the Year-by-Year Explorer, Country Breakdown, Monthly Data Explorer, and HTML summary.
**Proverbs:** "De Mortar-Pestle" by G. Addinton Forde (1987). Page numbers verified against source.
**Author & Compiler:** Matthew A. A. Blackman
**Generated:** {datetime.now().strftime('%B %d, %Y %I:%M %p')}
""")