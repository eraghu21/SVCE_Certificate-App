import streamlit as st
import pandas as pd
from fpdf import FPDF
import re
import pyAesCrypt
import requests
import os
from PIL import Image


# Load the image from a file
image = Image.open('svce_logo.jpg')

# Display the image using st.image()
st.image(image)
st.title("🎓 SVCE FDP(Sep 8 to Sep 12) Certificate Generator")
# Parameters
buffer_size = 64 * 1024
password = st.secrets["excel_password"]
encrypted_url = "https://raw.githubusercontent.com/eraghu21/certificate-app/main/registrations.xlsx.aes"

# Download and decrypt encrypted Excel
enc_file = "registrations.xlsx.aes"
dec_file = "registrations.xlsx"

try:
    with open(enc_file, "wb") as f:
        f.write(requests.get(encrypted_url).content)

    pyAesCrypt.decryptFile(enc_file, dec_file, password, buffer_size)
    df = pd.read_excel(dec_file)
    os.remove(dec_file)  # optional cleanup

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Input field
email_input = st.text_input("Enter your registered Email")

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
            name = row['Name']
            designation = row['Designation']
            college = row['College Name']

            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.image("certificate_bg.png", x=0, y=0, w=297, h=210)
            pdf.ln(62)
            pdf.set_font("Arial", 'B', 20)
            pdf.set_x(90)
            pdf.cell(200, 12, txt=name.strip(), ln=True, align='C')
            pdf.ln(1)
            pdf.set_x(40)
            pdf.set_font("Arial", size=16)
            pdf.cell(200, 10, txt=f"{college}", ln=True, align='C')

            cert_filename = f"certificate_{name.strip().replace(' ', '_')}.pdf"
            pdf.output(cert_filename)

            with open(cert_filename, "rb") as f:
                st.success("✅ Certificate generated successfully!")
                st.download_button("📥 Download Certificate", f, file_name=cert_filename, mime="application/pdf")
        else:
            st.error("❌ Participant Email not found in the Registration record.")
