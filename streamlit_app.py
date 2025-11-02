# -------------------------------
# BUTTON TO OPEN GOOGLE SHEET IN NEW TAB
# -------------------------------
gsheet_url = "https://docs.google.com/spreadsheets/d/15HJ7wxyUmo-gcl5_y1M9gl4Ti-JSsYEJZCjoI76s-Xk/edit#gid=1385640257"
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
# HOTEL CSV DOWNLOAD BUTTONS (BLUE)
# -------------------------------
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

        # Place download button inside column
        with cols[idx % col_count]:
            st.download_button(
                label=f"📥 {hotel_name}.csv",
                data=csv_data,
                file_name=f"{hotel_name}-Phobs.csv",
                mime="text/csv",
                key=f"download_{idx}",
                help="Download CSV for this hotel",
                # custom styling via HTML wrapper
                css_class="custom-download"
            )
    except Exception as e:
        failed.append((hotel_name, str(e)))

# Show failed hotel loads
if failed:
    st.warning("⚠️ Some hotels failed to load:")
    for h, e in failed:
        st.text(f"{h}: {e}")





