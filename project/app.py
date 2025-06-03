import streamlit as st
import numpy as np
import pandas as pd
import joblib
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="PBPD Predictor", layout="wide")

st.title("Powder Bed Packing Density (PBPD) Predictor")

st.markdown("""
This tool estimates **Powder Bed Packing Density (%)** for metal powders used in Laser Powder Bed Fusion (PBF-LB/M)  
based on powder characteristics and layer thickness.  
You may select a material or let the app detect it from bulk density.
""")

st.sidebar.header("Material Info")
material_options = ["Auto (via density)", "Ti", "SS", "Al"]
material_choice = st.sidebar.selectbox("Select Material Group", material_options)
bulk_density = st.sidebar.number_input("Bulk Density (g/cm³)", min_value=0.0, value=4.5)

if material_choice == "Auto (via density)":
    if bulk_density < 3.5:
        material_group = "al"
    elif 3.5 <= bulk_density < 6:
        material_group = "ti"
    else:
        material_group = "ss"
else:
    material_group = material_choice.lower()
    material_group = material_group.lower()

st.header("Powder Properties")
col1, col2 = st.columns(2)

with col1:
    d10 = st.number_input("D10 (µm)", value=15.0)
    d50 = st.number_input("D50 (µm)", value=35.0)
    d90 = st.number_input("D90 (µm)", value=55.0)
    tap_density = st.number_input("Tap Density (g/cm³)", value=5.0)

with col2:
    hr = st.number_input("Hausner Ratio (HR)", min_value=1.0, value=1.2)
    d23 = st.number_input("D[2,3] (µm)", value=30.0)
    d34 = st.number_input("D[3,4] (µm)", value=42.0)
    layer_thickness = st.number_input("Effective Layer Thickness (µm)", min_value=0.1, value=60.0)

span = (d90 - d10) / d50
r23 = d23 / layer_thickness
r34 = d34 / layer_thickness

st.subheader("Input Check")
warnings = []

if span < 0.8 or span > 2.0:
    warnings.append("Span is outside typical range (0.8–2.0).")
if r23 < 0.05 or r23 > 1.2:
    warnings.append("R23 is outside expected range.")
if r34 < 0.05 or r34 > 1.5:
    warnings.append("R34 is outside expected range.")
if d23 > layer_thickness:
    warnings.append("D[2,3] is greater than layer thickness — may cause bridging.")
if hr > 1.4:
    warnings.append("HR is high — flowability may be poor.")

for w in warnings:
    st.warning(w)

if st.button("Predict PBPD"):
    try:
        model = joblib.load(f"model_{material_group.lower()}.pkl")
        if material_group == "ti":
            features = [r23, span, tap_density]
        elif material_group == "ss":
            features = [r23, r34, span, tap_density, hr]
        elif material_group == "al":
            features = [r34, span, tap_density]
        else:
            st.error("Material model not found.")
            st.stop()

        input_data = np.array([features])
        prediction = model.predict(input_data)[0]

        st.success(f"Predicted PBPD: **{prediction:.2f}%**")

        confidence = {
            "ti": "High",
            "ss": "Moderate",
            "al": "Low"
        }.get(material_group, "Unknown")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="PBPD Prediction Report", ln=True, align="C")
        pdf.ln(5)
        pdf.cell(200, 10, txt=f"Material Group: {material_group.upper()}", ln=True)
        pdf.cell(200, 10, txt=f"Confidence Level: {confidence}", ln=True)
        pdf.cell(200, 10, txt=f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(5)
        pdf.cell(200, 10, txt="Inputs:", ln=True)
        pdf.cell(200, 10, txt=f"D10: {d10} µm", ln=True)
        pdf.cell(200, 10, txt=f"D50: {d50} µm", ln=True)
        pdf.cell(200, 10, txt=f"D90: {d90} µm", ln=True)
        pdf.cell(200, 10, txt=f"Span: {span:.3f}", ln=True)
        pdf.cell(200, 10, txt=f"D[2,3]: {d23} µm", ln=True)
        pdf.cell(200, 10, txt=f"D[3,4]: {d34} µm", ln=True)
        pdf.cell(200, 10, txt=f"R23: {r23:.3f}", ln=True)
        pdf.cell(200, 10, txt=f"R34: {r34:.3f}", ln=True)
        pdf.cell(200, 10, txt=f"Tap Density: {tap_density} g/cm³", ln=True)
        pdf.cell(200, 10, txt=f"Hausner Ratio: {hr}", ln=True)
        pdf.cell(200, 10, txt=f"Layer Thickness: {layer_thickness} µm", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt=f"Predicted PBPD: {prediction:.2f}%", ln=True)

        pdf_output = pdf.output(dest="S").encode("latin1")
        st.download_button(
            label="Download PDF Report",
            data=pdf_output,
            file_name="pbpd_prediction_report.pdf",
            mime="application/pdf"
        )

    except FileNotFoundError:
        st.error(f"Model for '{material_group.upper()}' not found. Make sure the model file exists.")

st.markdown("---")
st.subheader("Batch Prediction via CSV")

csv_file = st.file_uploader("Upload a CSV file for batch prediction", type=["csv"])

if csv_file:
    df_csv = pd.read_csv(csv_file)
    required_cols = [
        'D10_µm', 'D50_µm', 'D90_µm',
        'D[2,3]', 'D[3,4]', 'Tap_Density_g/cm³',
        'HR', 'Effective_Layer_Thickness_µm', 'Material'
    ]

    if not all(col in df_csv.columns for col in required_cols):
        st.error("Missing required columns in CSV.")
    else:
        df = df_csv.copy()
        df['Span'] = (df['D90_µm'] - df['D10_µm']) / df['D50_µm']
        df['R23'] = df['D[2,3]'] / df['Effective_Layer_Thickness_µm']
        df['R34'] = df['D[3,4]'] / df['Effective_Layer_Thickness_µm']

        predictions = []
        for _, row in df.iterrows():
            mat = str(row['Material']).lower()
            model_used = None

            if 'ti' in mat:
                model_used = "ti"
                features = [row['R23'], row['Span'], row['Tap_Density_g/cm³']]
            elif 'ss' in mat or '316' in mat:
                model_used = "ss"
                features = [row['R23'], row['R34'], row['Span'], row['Tap_Density_g/cm³'], row['HR']]
            elif 'al' in mat:
                model_used = "al"
                features = [row['R34'], row['Span'], row['Tap_Density_g/cm³']]

            if model_used:
                model = joblib.load(f"model_{model_used}.pkl")
                pred = model.predict([features])[0]
                predictions.append(pred)
            else:
                predictions.append(np.nan)
                continue
            pred = model.predict([features])[0]
            predictions.append(pred)

        df['Predicted_PBPD_%'] = predictions
        st.success("Batch prediction complete.")
        st.dataframe(df[['Material', 'Predicted_PBPD_%']].head())

        csv_download = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Results as CSV",
            data=csv_download,
            file_name="pbpd_predictions.csv",
            mime="text/csv"
        )
