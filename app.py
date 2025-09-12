import streamlit as st
import pandas as pd
from fpdf import FPDF
import re
import pyAesCrypt
import requests
import os

# ====================== CONFIG ======================
st.set_page_config(page_title="SVCE FDP Certificate Generator", layout="centered")

# ====================== COUNTERS ======================
def update_visit_count():
    count_file = "counter.txt"
    if not os.path.exists(count_file):
        with open(count_file, "w") as f:
            f.write("0")
    with open(count_file, "r") as f:
        count = int(f.read())
    if "counted" not in st.session_state:
        count += 1
        with open(count_file, "w") as f:
            f.write(str(count))
        st.session_state.counted = True
    return count

def update_download_count():
    count_file = "downloads.txt"
    if not os.path.exists(count_file):
        with open(count_file, "w") as f:
            f.write("0")
    with open(count_file, "r") as f:
        count = int(f.read())
    count += 1
    with open(count_file, "w") as f:
        f.write(str(count))
    return count

def get_download_count():
    count_file = "downloads.txt"
    if not os.path.exists(count_file):
        return 0
    with open(count_file, "r") as f:
        return int(f.read())

visit_count = update_visit_count()
download_total = get_download_count()

# ====================== HEADER ======================
st.title("Quantum AI: Educating the Next Generation of Professionals - FDP Certificate Generator")

st.markdown(f"<div style='text-align:right; color:gray;'>👁️ Day Visits: {visit_count}</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:right; color:gray;'>📥 Day Downloads: {download_total}</div>", unsafe_allow_html=True)

# ====================== LOAD & DECRYPT EXCEL ======================
buffer_size = 64 * 1024
password = st.secrets["excel_password"]
encrypted_url = "https://raw.githubusercontent.com/eraghu21/certificate-app/main/registrations.xlsx.aes"

enc_file = "registrations.xlsx.aes"
dec_file = "registrations.xlsx"

try:
    resp = requests.get(encrypted_url)
    if resp.status_code != 200 or len(resp.content) == 0:
        st.error("❌ Failed to download encrypted Excel file from GitHub.")
        st.stop()

    with open(enc_file, "wb") as f:
        f.write(resp.content)

    pyAesCrypt.decryptFile(enc_file, dec_file, password, buffer_size)
    df = pd.read_excel(dec_file)

    os.remove(enc_file)
    os.remove(dec_file)

except Exception as e:
    st.error("❌ Error loading participant data. Please try again later.")
    st.stop()

# ====================== CLEAN COLUMN NAMES ======================
df.columns = df.columns.str.strip().str.lower()

# ====================== EMAIL INPUT ======================
email_input = st.text_input("📧 Enter your registered Email")

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# ====================== GENERATE CERTIFICATE ======================
if st.button("Generate Certificate"):
    if not is_valid_email(email_input):
        st.warning("⚠️ Please enter a valid email address.")
    else:
        match = df[df['email'].str.strip().str.lower() == email_input.strip().lower()]
        if not match.empty:
            row = match.iloc[0]
            attendance = row['attendance']
            if attendance >= 3:
                name = row['name']
                designation_raw = row['designation'].strip().lower()
                college = row['college_name']

                if "assistant" in designation_raw:
                    designation = "Assistant Professor"
                elif "associate" in designation_raw:
                    designation = "Associate Professor"
                elif "professor" in designation_raw:
                    designation = "Professor"
                else:
                    designation = row['designation'].strip().title()

                # Generate PDF
                pdf = FPDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                pdf.image("QuantumAIFDPCertificat.jpeg", x=0, y=0, w=297, h=210)

                pdf.ln(65)
                pdf.set_font("Arial", 'B', 20)
                pdf.set_x(10)
                pdf.cell(0, 12, txt=name.strip().upper(), ln=True, align='C')

                pdf.ln(1)
                pdf.set_font("Arial", size=16)
                pdf.set_x(15)
                pdf.cell(0, 10, designation.strip().title(), ln=True, align='C')

                pdf.ln(1)
                pdf.set_font("Arial", size=16)
                pdf.cell(0, 10, txt=college.strip().upper(), ln=True, align='C')

                cert_filename = f"certificate_{name.strip().replace(' ', '_')}.pdf"
                pdf.output(cert_filename)

                with open(cert_filename, "rb") as f:
                    st.success("✅ Certificate generated successfully!")
                    st.download_button("📥 Download Certificate", f, file_name=cert_filename, mime="application/pdf")
                    update_download_count()

                os.remove(cert_filename)
            else:
                st.warning("⚠️ Your attendance is less than required.")
        else:
            st.error("❌ Email not found in the registration records.")
