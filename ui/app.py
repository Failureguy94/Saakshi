import streamlit as st
import os
import sys
import pandas as pd
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from saakshi.db import get_db
from saakshi.modules.custody import verify_chain
from saakshi.modules.reporting import generate_report
import json

def compute_merkle_root():
    if not os.path.exists("out/manifest.json"):
        return "N/A"
    with open("out/manifest.json", "r") as f:
        return json.load(f).get("merkle_root", "N/A")

st.set_page_config(page_title="Saakshi Forensic Platform", layout="wide", initial_sidebar_state="expanded")
st.title("Saakshi Forensic Platform")
st.markdown("⚠️ **Note: All data shown is generated from synthetic test images.**")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Evidence", "Recovery", "Timeline", "Integrity", "Report"])

def load_table(table):
    conn = get_db()
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

with tab1:
    st.header("Evidence Acquisition")
    if os.path.exists("out/synthetic_dvr.img"):
        st.success("Image acquired: out/synthetic_dvr.img")
        st.write("Identified Profile: VendorX")
    else:
        st.error("No image found. Please run the pipeline first.")

with tab2:
    st.header("Recovered Video Segments")
    try:
        df = load_table("segments")
        st.dataframe(df)
        
        st.subheader("Disk Map")
        st.write("🟢 Indexed 🔴 Recovered/Deleted")
        
        # Simple disk map visual
        html = "<div style='display: flex; height: 30px; width: 100%; border: 1px solid #555;'>"
        for _, row in df.iterrows():
            color = "#ff4b4b" if row["is_recovered"] else "#00cc66"
            width = max(1, int((row["length"] / 50000) * 100)) # naive scaling
            html += f"<div style='background-color: {color}; width: {width}px; border-right: 1px solid #333;' title='CH{row['channel']}'></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(str(e))

with tab3:
    st.header("Timeline & Motion Events")
    try:
        events = load_table("motion_events")
        st.dataframe(events)
    except Exception as e:
        st.error(str(e))

with tab4:
    st.header("Custody & Integrity")
    try:
        custody_df = load_table("custody_log")
        st.dataframe(custody_df)
        
        st.write(f"**Merkle Root:** `{compute_merkle_root()}`")
        
        if st.button("Verify Chain"):
            is_valid, _ = verify_chain()
            if is_valid:
                st.success("Cryptographic chain verified and intact.")
            else:
                st.error("Chain verification failed! Tampering detected.")
                
        if st.button("Tamper one byte (Demo)"):
            try:
                # Corrupt the custody log slightly
                conn = get_db()
                c = conn.cursor()
                c.execute("UPDATE custody_log SET data_hash = 'TAMPERED' WHERE id = 1")
                conn.commit()
                conn.close()
                st.warning("Tampered first entry in custody log. Press 'Verify Chain' again.")
            except Exception:
                pass
    except Exception as e:
        st.error(str(e))

with tab5:
    st.header("Reporting")
    if st.button("Generate PDF Report"):
        try:
            pdf = generate_report()
            st.success(f"Report generated at {pdf}")
            with open(pdf, "rb") as f:
                st.download_button("Download PDF", f, file_name="saakshi_report.pdf")
        except Exception as e:
            st.error(str(e))
