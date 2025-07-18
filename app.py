import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

st.set_page_config(page_title="Spektrofotometri Sederhana", layout="wide")
st.title("📊 Analisis Spektrofotometri - Hukum Beer")

st.markdown("Masukkan minimal 3 data standar (konsentrasi dan absorbansi):")

# Input data standar
num_std = st.number_input("Jumlah data standar", min_value=3, value=3, step=1)
std_data = []
col1, col2 = st.columns(2)
with col1:
    for i in range(num_std):
        konsentrasi = st.number_input(f"Konsentrasi Standar {i+1} (ppm)", key=f"k{i}")
        std_data.append({"Konsentrasi (ppm)": konsentrasi})

with col2:
    for i in range(num_std):
        absorbansi = st.number_input(f"Absorbansi Standar {i+1}", key=f"a{i}")
        std_data[i]["Absorbansi"] = absorbansi

df_std = pd.DataFrame(std_data)

# Perhitungan regresi linier
x = df_std["Konsentrasi (ppm)"]
y = df_std["Absorbansi"]
slope, intercept, r_value, _, _ = linregress(x, y)

# Plot kalibrasi
fig, ax = plt.subplots()
ax.scatter(x, y, color='blue', label='Data Standar')
ax.plot(x, slope * x + intercept, color='red', label='Garis Kalibrasi')
ax.set_xlabel("Konsentrasi (ppm)")
ax.set_ylabel("Absorbansi")
ax.set_title("Kurva Kalibrasi")
ax.legend()
st.pyplot(fig)

st.markdown(f"""
**Persamaan regresi:** y = {slope:.4f}x + {intercept:.4f}  
**Koefisien korelasi (R²):** {r_value**2:.4f}
""")

# Input data sampel
st.markdown("---")
st.markdown("### 📌 Data Sampel")
num_samples = st.number_input("Jumlah data sampel", min_value=1, value=2, step=1)
sample_data = []
for i in range(num_samples):
    absorbansi = st.number_input(f"Absorbansi Sampel {i+1}", key=f"sampel{i}")
    konsentrasi = (absorbansi - intercept) / slope if slope != 0 else 0
    sample_data.append({
        "Sampel": f"S{i+1}",
        "Absorbansi": absorbansi,
        "Konsentrasi (ppm)": konsentrasi
    })

sample_results = pd.DataFrame(sample_data)
st.markdown("### 📄 Hasil Perhitungan Konsentrasi:")
st.dataframe(sample_results.style.format({"Absorbansi": "%.4f", "Konsentrasi (ppm)": "%.3f"}), hide_index=True)

# =========================
# 🔸 %RPD (akurasi duplikat)
# =========================
if num_samples >= 2 and num_samples % 2 == 0:
    st.markdown("#### 🎯 Evaluasi Akurasi (%RPD untuk Duplikat)")

    rpd_results = []
    rpd_texts = []
    for i in range(0, num_samples, 2):
        c1 = sample_results.iloc[i]["Konsentrasi (ppm)"]
        c2 = sample_results.iloc[i+1]["Konsentrasi (ppm)"]
        avg = (c1 + c2) / 2
        rpd = abs(c1 - c2) / avg * 100 if avg != 0 else 0
        rpd_results.append({
            "Pasangan": f"S{i+1} & S{i+2}",
            "%RPD": rpd
        })
        rpd_texts.append(f"- Pasangan S{i+1} & S{i+2}: **{rpd:.2f}%**")

    rpd_df = pd.DataFrame(rpd_results)
    st.dataframe(rpd_df.style.format({"%RPD": "%.2f"}), hide_index=True)

    st.markdown("##### Hasil %RPD:")
    for text in rpd_texts:
        st.markdown(text)

    # Menghitung rata-rata akurasi
    avg_accuracy = np.mean([r["%RPD"] for r in rpd_results])
    st.markdown(f"**Akurasi rata-rata (%RPD): {avg_accuracy:.2f}%**")

# =========================
# 🔸 CV Horwitz (presisi)
# =========================
st.markdown("#### 📉 Evaluasi Presisi (CV Horwitz)")
horwitz_results = []
horwitz_texts = []

for s in sample_results.itertuples():
    ppm = s._3
    C_decimal = ppm / 1_000_000  # ppm ke proporsi
    if C_decimal > 0:
        cv_horwitz = 2 ** (1 - 0.5 * np.log10(C_decimal)) * 100
    else:
        cv_horwitz = np.nan
    horwitz_results.append({
        "Sampel": s._1,
        "Konsentrasi (ppm)": ppm,
        "CV Horwitz (%)": cv_horwitz
    })
    if not np.isnan(cv_horwitz):
        horwitz_texts.append(f"- {s._1}: **{cv_horwitz:.2f}%**")

cv_df = pd.DataFrame(horwitz_results)
st.dataframe(cv_df.style.format({
    "Konsentrasi (ppm)": "%.3f",
    "CV Horwitz (%)": "%.2f"
}), hide_index=True)

st.markdown("##### Hasil CV Horwitz:")
for text in horwitz_texts:
    st.markdown(text)
