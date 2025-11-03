import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from st_excel_table import Table

# ------------------------------
# Streamlit Cloud Secrets Setup
# ------------------------------
# Make sure your secrets.toml has:
# SPREADSHEET, PRIVATE_KEY, CLIENT_EMAIL

SPREADSHEET_ID = st.secrets["SPREADSHEET"]

# List of sheet names
SHEET_NAMES = [
    "🟠 APP_ADRIA",
    "🟡 PREMIUM_MOBHOMES",
    "🟢 OLIVE_SUITES",
    "🟤 H_CONVENT",
    "🔵 VILE_Z_BLK",
    "🟣 VILE_BREZ_BLK",
    "🔴 STD_MOBHOMES",
    "PHOBS"
]

# ------------------------------
# Google Sheets Authentication
# ------------------------------
creds = Credentials.from_service_account_info(
    {
        "type": "service_account",
        "private_key": st.secrets["PRIVATE_KEY"],
        "client_email": st.secrets["CLIENT_EMAIL"],
        "token_uri": "https://oauth2.googleapis.com/token"
    }
)

gc = gspread.authorize(creds)

# ------------------------------
# Streamlit App
# ------------------------------
st.title("Google Sheets Editable Tables")

for sheet_name in SHEET_NAMES:
    st.header(f"Sheet: {sheet_name}")

    try:
        # Load the sheet
        sheet = gc.open_by_url(st.secrets["SPREADSHEET"]).worksheet(sheet_name)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Display editable table
        Table(df.to_dict('records'), df.columns.tolist(), key=sheet_name)

        # Save button for this sheet
        if st.button(f"Save changes to {sheet_name}", key=f"save_{sheet_name}"):
            # Get edited data from session_state
            edited_data = st.session_state.get(
                f"st_excel_table_data_{sheet_name}",
                df.to_dict('records')
            )
            edited_df = pd.DataFrame(edited_data)

            # Clear existing sheet and update with new data
            sheet.clear()
            sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())

            st.success(f"Data successfully updated to sheet: {sheet_name}!")

    except gspread.WorksheetNotFound:
        st.warning(f"Sheet '{sheet_name}' not found in this spreadsheet.")
    except Exception as e:
        st.error(f"Error loading or updating sheet '{sheet_name}': {e}")



