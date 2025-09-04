import streamlit as st
import pandas as pd
from fpdf import FPDF
import re
import pyAesCrypt
import requests
import os

st.title("🎓 SVCE FDP Certificate Generator")

# Parameters
buffer_size = 64 * 1024
password = st.secrets["excel_password"]
encrypted_url = "https://raw.githubusercontent.com/eraghu21/certificate-app/main/registrations.xlsx.aes"

# Temporary filenames
enc_file = "registrations.xlsx.aes"
dec_file = "registrations.xlsx"

# Download & decrypt Excel
try:
    with open(enc_file, "wb") as f:
        f.write(requests.get(encrypted_url).content)

    pyAesCrypt.decryptFile(enc_file, dec_file, password, buffer_size)
    df = pd.read_excel(dec_file)
    
    os.remove(enc_file)  # optional
    os.remove(dec_file)  # optional
except Exception as e:
    st.error(f"❌ Error loading participant data: {e}")
    st.stop()

# Email input
email_input = st.text_input("Enter your registered Email")

# Email validation
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# On button click
if st.button("Generate Certificate"):
    if not is_valid_email(email_input):
        st.warning("⚠️ Please enter a valid email address.")
    else:
        # Match user
        match = df[df['Mail'].str.strip().str.lower() == email_input.strip().lower()]

        if not match.empty:
            row = match.iloc[0]
            attendance = row['Attendance']

            if attendance >= 3:
                name = row['Name']
                designation = row['Designation']
                college = row['College Name']

                # Generate certificate
                pdf = FPDF(orientation='L', unit='mm', format='A4')
                pdf.add_page()
                pdf.image("certificate_bg.png", x=0, y=0, w=297, h=210)

                # Move to Y position
                pdf.ln(62)

              
               # Name + Designation (uppercase + centered)
                pdf.set_font("Arial", 'B', 20)
                pdf.set_x(95)
                pdf.cell(240, 12, txt=f"{name.strip().upper()} - {designation.strip().upper()}", ln=True, align='C')

                # College (uppercase + centered)
                pdf.ln(2)
                pdf.set_font("Arial", size=16)
                pdf.cell(0, 10, txt=college.strip().upper(), ln=True, align='C')


                # Save PDF
                cert_filename = f"certificate_{name.strip().replace(' ', '_')}.pdf"
                pdf.output(cert_filename)

                with open(cert_filename, "rb") as f:
                    st.success("✅ Certificate generated successfully!")
                    st.download_button("📥 Download Certificate", f, file_name=cert_filename, mime="application/pdf")
                
                os.remove(cert_filename)  # Clean up
            else:
                st.warning("⚠️ You must have attended at least 3 sessions and feedback mandatory to receive a certificate.")
        else:
            st.error("❌ Email not found in the Registration records.")
