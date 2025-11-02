# -*- coding: utf-8 -*-


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
PASSWORD = os.getenv("MY", "test")  # fallback password if not set

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="EXPORT4PHOBS", layout="wide")

# -------------------------------
# PASSWORD LOGIN
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("## 🔒 Za dostop do aplikacije se prijavi")

    password = st.text_input("Vnesi geslo", type="password")

    if st.button("Odkleni Aplikacijo"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Access Granted!")
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")
    st.stop()

# -------------------------------
# MAIN APP (after login)
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

st.markdown("#### BAR Urejevalnik")

#Sheet URL - new tab
sheet_url = "https://docs.google.com/spreadsheets/d/15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk/edit?gid=1385640257"

st.markdown("""
    <style>
    .google-sheet-button {
        float: right;  /* Align button to the right */
        background-color: #1cb319;
        color: white;
        padding: 0px 40px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    .google-sheet-button:hover {
        background-color: #4fb34d;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <a href="{sheet_url}" target="_blank">
        <button class="google-sheet-button">
           Odpri v Google Sheet v novem oknu
        </button>
    </a>
""", unsafe_allow_html=True)

# Embed Google Sheet
st.components.v1.iframe(
    "https://docs.google.com/spreadsheets/d/15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk/edit?gid=1385640257",
    height=550,
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
    df['Yield'] = f"YIELD{los_code}"
    if 'Datum' not in df.columns:
        df['Datum'] = pd.Timestamp.today().strftime('%Y-%m-%d')
    return df[['Hotel_ID', 'Datum', 'nicla', 'BAR', 'Yield']]

def convert_df_to_csv_download(df):
    return df.to_csv(index=False, header=False).encode("utf-8")

# -------------------------------
# MAIN PHOBS CSS COLORS
# -------------------------------

st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #f6b221;
        color: white;
        cursor: pointer;
    }

    /* Hover effect */
   .stButton>button:hover {
        background-color: #f7c24f;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    /* Style all download buttons */
    .stDownloadButton>button {
        background-color: #5392ca;
        color: white;
        cursor: pointer;
    }

    /* Hover effect */
    .stDownloadButton>button:hover {
        background-color: #4184bf;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# MAIN PHOBS EXPORTER
# -------------------------------


st.markdown("#### BAR Export.csv Generator")

if st.button("🔄 Osveži podatke"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=600)  # cache for 10 minutes
def load_master_data():
    gsheet_id = "15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk"
    master_url = f"https://docs.google.com/spreadsheets/d/{gsheet_id}/gviz/tq?tqx=out:csv&sheet=PHOBS"
    master_df = pd.read_csv(master_url)
    return master_df

try:
    master_df = load_master_data()
    st.success(f"✅ Loaded master sheet — {len(master_df)} hotels found.")
except Exception as e:
    st.error(f"❌ Failed to load master sheet: {e}")
    st.stop()

# Display last refresh time
st.caption(f"Last refreshed at: {datetime.now().strftime('%H:%M:%S')}")

# -------------------------------
# Load individual hotel sheets
# -------------------------------
gsheet_id = "15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk"

col_count = 3
cols = st.columns(col_count)
hotel_buttons = []

failed = []
for idx, row in master_df.iterrows():
    hotel_name = row.get("Hotel_Name", "")
    hotel_id = row.get("Hotel_ID", "")
    los_code = row.get("YIELD_Code", "")

    try:
        sname = urllib.parse.quote(hotel_name)
        url = f"https://docs.google.com/spreadsheets/d/{gsheet_id}/gviz/tq?tqx=out:csv&sheet={sname}"
        df = pd.read_csv(url)
        df = prepare_phobs_csv(df, hotel_id, los_code)

        csv_data = convert_df_to_csv_download(df)
        with cols[idx % col_count]:
            st.download_button(
                label=f"📥 {hotel_name}.csv",
                data=csv_data,
                file_name=f"{hotel_name}-Phobs.csv",
                mime="text/csv",
                use_container_width=True,
            )
    except Exception as e:
        failed.append((hotel_name, str(e)))

if failed:
    st.warning("⚠️ Some hotels failed to load:")
    for h, e in failed:
        st.text(f"{h}: {e}")























