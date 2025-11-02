# streamlit_app.py

import os
import pandas as pd
import urllib.parse
import base64
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

# -------------------------------
# ENVIRONMENT & PASSWORD SETUP
# -------------------------------
load_dotenv()
PASSWORD = os.getenv("MY", "test")  # fallback if not set

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="EXPORT4PHOBS", layout="wide")

# -------------------------------
# LOGIN
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("## 🔒 Please log in to access the app")
    password = st.text_input("Enter Password", type="password")
    if st.button("Unlock App"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Access Granted!")
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")
    st.stop()

# -------------------------------
# HEADER
# -------------------------------
st.markdown(
    """
<div style="display:flex;justify-content:space-between;align-items:center;">
  <h2><b>EXPORT</b>4PHOBS</h2>
  <img src="https://www.adria-ankaran.si//app/uploads/2025/10/logo-Adria.jpg" width="180" alt="">
</div>
<hr>
""",
    unsafe_allow_html=True
)

# -------------------------------
# EMBED GOOGLE SHEET
# -------------------------------
gsheet_url = "https://docs.google.com/spreadsheets/d/15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk/edit#gid=1385640257"
st.markdown("### 📊 Linked Google Sheet (PHOBS Master Data)")
st.components.v1.iframe(gsheet_url, height=550)

# -------------------------------
# BUTTON TO OPEN GOOGLE SHEET IN NEW TAB
# -------------------------------
st.markdown(
    f"""
<div style="margin:10px 0;">
    <a href="{gsheet_url}" target="_blank" style="
        background-color:#5392ca;
        color:white;
        padding:8px 14px;
        border-radius:6px;
        text-decoration:none;
        font-weight:600;
        display:inline-block;
        transition:0.3s;
    ">📂 Open Google Sheet in new tab</a>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------
# CUSTOM CSS FOR DOWNLOAD BUTTONS
# -------------------------------
st.markdown(
    """
<style>
.custom-download button {
    background-color: #5392ca !important;
    color: white !important;
    border-radius: 6px !important;
    padding: 8px 14px !important;
    font-weight: 600 !important;
    transition: 0.3s !important;
    width: 100% !important;
}
.custom-download button:hover {
    background-color: #417fb4 !important;
}
</style>
""",
    unsafe_allow_html=True
)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def prepare_phobs_csv(df, hotel_id, los_code):
    if 'BAR' not in df.columns:
        df['BAR'] = 120
    df['BAR'] = df['BAR'].apply(lambda x: f"BAR{x}")
    df['Hotel_ID'] = hotel_id
    df['nicla'] = 0
    df['Yield'] = f"YIELD{los_code}" if pd.notna(los_code) else "YIELD"
    if 'Datum' not in df.columns:
        df['Datum'] = pd.Timestamp.today().strftime('%Y-%m-%d')
    return df[['Hotel_ID', 'Datum', 'nicla', 'BAR', 'Yield']]

def convert_df_to_csv_download(df):
    return df.to_csv(index=False, header=False).encode("utf-8")

# -------------------------------
# MAIN EXPORT SECTION
# -------------------------------
st.markdown("## ⚙️ PHOBS BAR Export .csv Generator")

# Orange reload button
if st.button("🔄 Reload Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=600)
def load_master_data():
    gsheet_id = "15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk"
    master_url = f"https://docs.google.com/spreadsheets/d/{gsheet_id}/gviz/tq?tqx=out:csv&sheet=PHOBS"
    return pd.read_csv(master_url)

# Load master sheet
try:
    master_df = load_master_data()
    st.success(f"✅ Loaded master sheet — {len(master_df)} hotels found.")
except Exception as e:
    st.error(f"❌ Failed to load master sheet: {e}")
    st.stop()

st.caption(f"Last refreshed at: {datetime.now().strftime('%H:%M:%S')}")

# -------------------------------
# LOAD INDIVIDUAL HOTEL SHEETS
# -------------------------------
gsheet_id = "15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk"
col_count = 3
cols = st.columns(col_count)
failed = []

for idx, row in master_df.iterrows():
    hotel_name = row.get("Hotel_Name", "").strip()
    hotel_id = row.get("Hotel_ID", "")
    los_code = row.get("YIELD_Code", "")
    try:
        sname = urllib.parse.quote(hotel_name)
        url = f"https://docs.google.com/spreadsheets/d/{gsheet_id}/gviz/tq?tqx=out:csv&sheet={sname}"
        df = pd.read_csv(url)
        df = prepare_phobs_csv(df, hotel_id, los_code)
        csv_data = convert_df_to_csv_download(df)

        with cols[idx % col_count]:
            st.markdown('<div class="custom-download">', unsafe_allow_html=True)
            st.download_button(
                label=f"📥 {hotel_name}.csv",
                data=csv_data,
                file_name=f"{hotel_name}-Phobs.csv",
                mime="text/csv",
                key=f"download_{idx}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        failed.append((hotel_name, str(e)))

if failed:
    st.warning("⚠️ Some hotels failed to load:")
    for h, e in failed:
        st.text(f"{h}: {e}")







