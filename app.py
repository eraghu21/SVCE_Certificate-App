import streamlit as st
import pandas as pd
from fpdf import FPDF
import re

# Load Excel data
df = pd.read_excel("registrations.xlsx")  # Make sure columns: Name, Mail, Designation, College

st.title("🎓 Certificate Generator")

# Input fields
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
        # Search for matching row by email (case-insensitive)
        match = df[df['Mail'].str.strip().str.lower() == email_input.strip().lower()]
        
        if not match.empty:
            row = match.iloc[0]  # Get the first matched row
            name = row['Name']
            designation = row['Designation']
            college = row['College']

            # Generate PDF Certificate
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()

            # Background image (optional)
            pdf.image("certificate_bg.png", x=0, y=0, w=297, h=210)

                       
            pdf.ln(70)

            pdf.set_font("Arial", 'B', 20)
            pdf.set_x(65)
            pdf.cell(200, 12, txt=name.strip(), ln=True, align='C')
            pdf.ln(1)

            pdf.set_font("Arial", size=16)
            pdf.cell(200, 10, txt=f"{designation}, {college}", ln=True, align='C')
            pdf.ln(20)

            pdf.cell(0, 10, txt="has successfully participated in the event.", ln=True, align='C')

            # Save and show download button
            cert_filename = f"certificate_{name.strip().replace(' ', '_')}.pdf"
            pdf.output(cert_filename)

            with open(cert_filename, "rb") as f:
                st.success("✅ Certificate generated successfully!")
                st.download_button("📥 Download Certificate", f, file_name=cert_filename, mime="application/pdf")
        else:
            st.error("❌ Email not found in the records.")
