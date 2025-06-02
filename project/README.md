# PBPD Prediction Tool

A machine learning-powered tool to predict **Powder Bed Packing Density (PBPD)** for metallic powders used in **Additive Manufacturing** processes such as Laser Powder Bed Fusion.

Supports separate, optimized models for:
- Titanium (Ti)
- Stainless Steel (SS)
- Aluminum (Al)

Built with [Streamlit](https://streamlit.io/) for a clean and interactive web interface.

---

## Features

✅ Dynamic model loading per material group  
✅ Input validation with predictive range warnings  
✅ CSV upload for batch predictions  
✅ Downloadable prediction reports  
✅ SHAP-based feature explanations (optional)  
✅ Ready for deployment on Streamlit Cloud

---

## 🛠 Installation

```bash
git clone https://github.com/your-username/pbpd-predictor.git
cd pbpd-predictor
pip install -r requirements.txt
```

Ensure you have the following model files in the root or `models/` directory:
- `model_ti.pkl`
- `model_ss.pkl`
- `model_al.pkl`

---

## Running the App

```bash
streamlit run app.py
```

---

## Input Parameters

| Feature         | Description                                 |
|------------------|---------------------------------------------|
| `D10`, `D50`, `D90` | Particle size distribution metrics (μm)      |
| `Span`            | Distribution width: `(D90 - D10) / D50`     |
| `Tap Density`     | Density after compaction (g/cm³)           |
| `True Density`    | Actual material density (g/cm³)            |
| `D[2,3]`, `D[3,4]`| Sauter & De Brouckere mean diameters (μm)  |

---

## Model Selection

The app automatically selects the correct model based on your chosen material:
- **Ti** → `model_ti.pkl`
- **SS** → `model_ss.pkl`
- **Al** → `model_al.pkl`

Each model was trained with material-specific feature optimization.


## Output and Explainability

- **Predicted PBPD** shown directly in the interface
- **SHAP plots** (if enabled) to explain prediction logic
- **Range warnings** for out-of-sample predictions


## Author

Developed by Abellash C Mathew

