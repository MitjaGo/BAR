import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from st_excel_table import Table

# ------------------------------
# Google Sheets setup
# ------------------------------
SERVICE_ACCOUNT_FILE = "vital-range-477116-f5-2c147eedcefb.json"  # <-- replace with your JSON file path
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
gc = gspread.authorize(credentials)

# Spreadsheet ID
SPREADSHEET_ID = "1uLyYdoiNIymsuuiorgxtlg4ISqYkYZ2rs19-OytbN0c"

# Sheet names
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
# Streamlit app
# ------------------------------
st.title("Google Sheets Editable Tables")

# Iterate over sheets
for sheet_name in SHEET_NAMES:
    st.header(f"Sheet: {sheet_name}")

    # Load sheet
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Display editable table
    Table(df.to_dict('records'), df.columns.tolist(), key=sheet_name)

    # Save button for this sheet
    if st.button(f"Save changes to {sheet_name}", key=f"save_{sheet_name}"):
        # Get edited data from session_state
        edited_data = st.session_state.get(f"st_excel_table_data_{sheet_name}", df.to_dict('records'))
        edited_df = pd.DataFrame(edited_data)

        # Clear existing sheet and update with new data
        sheet.clear()
        sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())

        st.success(f"Data successfully updated to sheet: {sheet_name}!")


