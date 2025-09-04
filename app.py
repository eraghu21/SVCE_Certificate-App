import streamlit as st
import pandas as pd
from fpdf import FPDF
import re
import pyAesCrypt
import requests
import os
import base64
from PIL import Image

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="SVCE FDP Certificate Generator", layout="centered")

# ====================== VISIT COUNTER ======================
def update_visit_count():
    count_file = "counter.txt"
    if not os.path.exists(count_file):
        with open(count_file, "w") as f:
            f.write("0")

    with open(count_file, "r") as f:
        count = int(f.read())

    # Count only new session
    if "counted" not in st.session_state:
        count += 1
        with open(count_file, "w") as f:
            f.write(str(count))
        st.session_state.counted = True

    return count

visit_count = update_visit_count()

# ====================== LOGO (Top-Right Floating) ======================
st.markdown(
    """
    <style>
        .logo-container {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 100px;
            z-index: 100;
        }
        .stApp {
            background-color: #f9f9f9;
        }
    </style>
    <div class="logo-container">
        <img src="data:image/png;base64,%s" width="100">
    </div>
    """ % base64.b64encode(open("logo.png", "rb").read()).decode(),
    unsafe_allow_html=True
)

# ====================== HEADER ======================
st.title("🎓 SVCE FDP Certificate Generator")

# FDP Banner Image (resized)
banner = Image.open("brochure.png")
banner = banner.resize((900, 300))
st.image(banner)

# Visit Counter Display
st.markdown(f"<div style='text-align:right; color:gray;'>👁️ Total Visits: {visit_count}</div>", unsafe_allow_html=True)

# ====================== CERTIFICATE VALIDATION ======================
# Parameters
buffer_size = 64 * 1024
password = st.secrets["excel_password"]
encrypted_url = "https://raw.githubusercontent.com/eraghu21/certificate-app/main/registrations.xlsx.aes"

# Temp files
enc_file = "registrations.xlsx.aes"
dec_file = "registrations.xlsx"

# Load & decrypt
try:
    with open(enc_file, "wb") as f:
        f.write(requests.get(encrypted_url).content)

    pyAesCrypt.decryptFile(enc_file, dec_file, password, buffer_size)
    df = pd.read_excel(dec_file)

    os.remove(enc_file)
    os.remove(dec_file)
except Exception as e:
    st.error(f"❌ Error loading participant data: {e}")
    st.stop()

# ====================== EMAIL INPUT ======================
email_input = st.text_input("📧 Enter your registered Email")

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

if st.button("Generate Certificate"):
    if not is_valid_email(email_input):
        st.warning("⚠️ Please enter a valid email address.")
    else:
        match = df[df['Mail'].str.strip().str.lower() == email_input.strip().lower()]

        if not match.empty:
            row = match.iloc[0]
            attendance = row['Attendance']

            if attendance >= 3:
                name = row['Name']
                designation_raw = row['Designation'].strip().lower()
                college = row['College Name']

                # Shorten designation
                if "assistant" in designation_raw:
                    designation = "Assistant Professor"
                elif "associate" in designation_raw:
                    designation = "Associate Professor"
                elif "professor" in designation_raw:
                    designation = "Professor"
                else:
                    designation = row['Designation'].strip()

                # Generate certificate
                pdf = FPDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                pdf.image("certificate_bg.png", x=0, y=0, w=297, h=210)

                pdf.ln(62)
                pdf.set_font("Arial", 'B', 20)
                pdf.set_x(95)
                pdf.cell(240, 12, txt=f"{name.strip().upper()} - {designation.strip().upper()}", ln=True, align='C')

                pdf.ln(2)
                pdf.set_font("Arial", size=16)
                pdf.cell(0, 10, txt=college.strip().upper(), ln=True, align='C')

                cert_filename = f"certificate_{name.strip().replace(' ', '_')}.pdf"
                pdf.output(cert_filename)

                with open(cert_filename, "rb") as f:
                    st.success("✅ Certificate generated successfully!")
                    st.download_button("📥 Download Certificate", f, file_name=cert_filename, mime="application/pdf")

                os.remove(cert_filename)
            else:
                st.warning("⚠️ You must have attended at least 3 sessions and submitted feedback to receive a certificate.")
        else:
            st.error("❌ Email not found in the Registration records.")

# ====================== FOOTER ======================
st.markdown("""---""")
st.markdown(
    f"""
    <div style='text-align: center; font-size: 14px; color: gray;'>
        Developed with ❤️ by <b>Raghuvaran E</b><br>
        Sri Venkateswara College of Engineering - Dept. of CSE<br>
        <i>Quantum AI FDP 2025</i><br>
        📧 <a href="mailto:eraghu21@gmail.com">eraghu21@gmail.com</a><br>
        👁️ <b>Total Visits:</b> {visit_count}
    </div>
    """,
    unsafe_allow_html=True
)
