import streamlit as st
import pandas as pd
from fpdf import FPDF

# Load Excel data
@st.cache_data
def load_data():
    return pd.read_excel("registrations.xlsx")

df = load_data()

# UI
st.title("🎓 Certificate Generator")

name = st.text_input("Enter your Name")
designation = st.text_input("Enter your Designation")
college = st.text_input("Enter your College Name")

# Validate and generate
if st.button("Generate Certificate"):
    match = df[
        (df['Name'].str.strip().str.lower() == name.strip().lower()) &
        (df['Designation'].str.strip().str.lower() == designation.strip().lower()) &
        (df['College Name'].str.strip().str.lower() == college.strip().lower())
    ]

    if not match.empty:
        # Create PDF
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.image("certificate_bg.jpg", x=0, y=0, w=297, h=210)
        //pdf.set_font("Arial", size=24)
       // pdf.cell(200, 10, txt="Certificate of Participation", ln=True, align='C')
        pdf.ln(20)
        //pdf.set_font("Arial", size=16)
        //pdf.cell(200, 10, txt="This is to certify that", ln=True, align='C')
        //pdf.ln(10)
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(200, 10, txt=name, ln=True, align='C')
        pdf.set_font("Arial", size=16)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"{designation}, {college}", ln=True, align='C')
        //pdf.ln(20)
        //pdf.cell(200, 10, txt="has successfully participated in the event.", ln=True, align='C')

        file_name = f"{name}_certificate.pdf"
        pdf.output(file_name)

        with open(file_name, "rb") as f:
            st.download_button(
                label="📥 Download Your Certificate",
                data=f,
                file_name=file_name,
                mime="application/pdf"
            )
    else:
        st.error("🚫 Not registered! Please check your details.")
