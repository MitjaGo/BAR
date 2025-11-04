# -*- coding: utf-8 -*-
#psswd .secrets on app UI streamlit#

import os
import pandas as pd
import urllib.parse
import base64
import streamlit as st

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="EXPORT4PHOBS", layout="wide")

# -------------------------------
# PASSWORD LOGIN
# -------------------------------

# Get password from Streamlit Secrets
PASSWORD = st.secrets.get("MY_PASSWORD", "")

if not PASSWORD:
    st.error("❌ MY_PASSWORD secret is missing in .streamlit/secrets.toml!")
    st.stop()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

# Header with logo (always visible)
st.markdown(
    """
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    ">
        <h2 style="margin: 0;"><b>EXPORT</b>4PHOBS</h2>
        <img src="https://www.adria-ankaran.si//app/uploads/2025/10/logo-Adria.jpg" width="180" alt="Logo">
    </div>
    <hr style="border: 1px solid #ddd;">
    """,
    unsafe_allow_html=True
)

# Login screen
if not st.session_state.authenticated:    
    st.markdown("## 🔒 Za dostop do aplikacije se prijavi")

    password = st.text_input("Vnesi geslo", type="password")

    st.markdown("""
        <style>
        div.stButton>button {
            background-color: #1cb319;
            color: white;
            cursor: pointer;
        }
        div.stButton>button:hover {
            background-color: #4fb34d;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("Odkleni Aplikacijo"):
        st.session_state.login_attempted = True
        if password == PASSWORD:
            st.session_state.authenticated = True
        else:
            st.error("❌ Geslo ni pravilno. Prosim za ponoven vnos.")

    st.stop()

# -------------------------------
# MAIN APP (after login)
# -------------------------------

st.write("✅ Uspešno ste prijavljeni! Dobrodošli v aplikaciji.")
st.markdown('<span style="color:green;font-size:30px; font-weight:bold;">BAR Urejevalnik</span>', unsafe_allow_html=True)

# -------------------------------
# LOAD GOOGLE SHEET ID FROM SECRETS
# -------------------------------
sheet_id = st.secrets.get("sheet", {}).get("spreadsheet_id", "")

if not sheet_id:
    st.error("❌ Spreadsheet ID is missing in .streamlit/secrets.toml!")
    st.stop()

# Construct the full sheet URL
sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?rm=demo"

#BUTTON STYLING CSS#

# Button styling
st.markdown("""
    <style>
    .google-sheet-button {
        float: right;
        background-color: #1cb319;
        color: white;
        padding: 0px 25px;
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

#-------------------------

# Open Sheet button
st.markdown(f"""
    <a href="{sheet_url}" target="_blank">
        <button class="google-sheet-button">
           Odpri v Google Sheet v novem oknu
        </button>
    </a>
""", unsafe_allow_html=True)

# Embed the sheet
st.components.v1.iframe(sheet_url, height=550)

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
        #df['Datum'] = pd.Timestamp.today().strftime('%Y-%m-%d')
        df['Datum'] = pd.Timestamp.now(tz='Europe/Belgrade').strftime('%Y-%m-%d')

    return df[['Hotel_ID', 'Datum', 'nicla', 'BAR', 'Yield']]

def convert_df_to_csv_download(df):
    return df.to_csv(index=False, header=False).encode("utf-8")

# -------------------------------
# PHOBS EXPORTER
# -------------------------------
st.markdown('<hr style="border: 1px solid #ddd;">', unsafe_allow_html=True)
st.markdown('<span style="color:green;font-size:25px; font-weight:bold;">BAR Export.csv Generator</span>', unsafe_allow_html=True)

if st.button("🔄 Osveži podatke"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=600)
def load_master_data(sheet_id: str):
    master_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=PHOBS"
    return pd.read_csv(master_url)

try:
    master_df = load_master_data(sheet_id)
    st.success(f"✅ Loaded master sheet — {len(master_df)} hotels found.")
except Exception as e:
    st.error(f"❌ Failed to load master sheet: {e}")
    st.stop()

#st.caption(f"Last refreshed at: {datetime.now().strftime('%H:%M:%S')}")
time_str = pd.Timestamp.now(tz='Europe/Belgrade').strftime('%H:%M:%S')

st.markdown(
    f"<p style='color:gray; font-weight:bold;'>Last refreshed at: {time_str}</p>",
    unsafe_allow_html=True
)


# -------------------------------
# Load individual hotel sheets
# -------------------------------
col_count = 3
cols = st.columns(col_count)
failed = []

for idx, row in master_df.iterrows():
    hotel_name = row.get("Hotel_Name", "")
    hotel_id = row.get("Hotel_ID", "")
    los_code = row.get("YIELD_Code", "")

    try:
        sname = urllib.parse.quote(hotel_name)
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sname}"
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






























