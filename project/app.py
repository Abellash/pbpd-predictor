import streamlit as st
import numpy as np
import joblib

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

st.header("Powder Properties")

col1, col2 = st.columns(2)

with col1:
    d10 = st.number_input("D10 (µm)", value=15.0)
    d50 = st.number_input("D50 (µm)", value=35.0)
    d90 = st.number_input("D90 (µm)", value=55.0)
    span = st.number_input("Span", value=1.2)
    tap_density = st.number_input("Tap Density (g/cm³)", value=5.0)

with col2:
    hr = st.number_input("Hausner Ratio (HR)", min_value=1.0, value=1.2)
    d23 = st.number_input("D[2,3] (µm)", value=30.0)
    d34 = st.number_input("D[3,4] (µm)", value=42.0)
    layer_thickness = st.number_input("Effective Layer Thickness (µm)", min_value=0.1, value=60.0)

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

for w in warnings:
    st.warning(w)

if st.button("Predict PBPD"):
    try:
        model = joblib.load(f"model_{material_group}.pkl")
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

    except FileNotFoundError:
        st.error(f"Model for '{material_group.upper()}' not found. Make sure the model file exists.")
