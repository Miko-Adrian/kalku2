import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

st.set_page_config(page_title="Spektrofotometri Sederhana", layout="wide")

st.title("📊 Analisis Spektrofotometri - Beer's Law")

st.markdown("Masukkan minimal 3 data standar (konsentrasi dan absorbansi):")

# Input data standar
num_std = st.number_input("Jumlah data standar", min_value=3, max_value=20, value=6)
std_data = []

for i in range(num_std):
    col1, col2 = st.columns(2)
    with col1:
        conc = st.number_input(f"Konsentrasi {i+1} (ppm)", key=f"c{i}", format="%.4f")
    with col2:
        absb = st.number_input(f"Absorbansi {i+1}", key=f"a{i}", format="%.4f")
    std_data.append((conc, absb))

df = pd.DataFrame(std_data, columns=["Konsentrasi", "Absorbansi"])

# Validasi input
if df["Konsentrasi"].isnull().any() or df["Absorbansi"].isnull().any():
    st.warning("Isi semua nilai terlebih dahulu.")
    st.stop()

if df["Konsentrasi"].nunique() < 2:
    st.error("Minimal dua nilai konsentrasi harus berbeda untuk menghitung regresi linier.")
    st.stop()

# Hitung regresi linier
slope, intercept, r_value, _, _ = linregress(df["Konsentrasi"], df["Absorbansi"])
r_squared = r_value**2

# Validasi slope
if abs(slope) < 1e-6:
    st.error("Slope terlalu kecil. Data mungkin tidak cukup bervariasi atau tidak linier.")
    st.stop()

# Plot kurva kalibrasi
fig, ax = plt.subplots()
x_fit = np.linspace(0, df["Konsentrasi"].max() * 1.1, 100)
y_fit = slope * x_fit + intercept

ax.scatter(df["Konsentrasi"], df["Absorbansi"], label="Data Standar", color="blue")
ax.plot(x_fit, y_fit, color="red", linestyle="--", label=f"y = {slope:.3f}x + {intercept:.3f}")
ax.set_xlabel("Konsentrasi (ppm)")
ax.set_ylabel("Absorbansi")
ax.set_title("Kurva Kalibrasi")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# Tampilkan parameter regresi
st.markdown("### 📌 Parameter Regresi")
st.write(f"- Slope (ε·l): {slope:.4f}")
st.write(f"- Intersep: {intercept:.4f}")
st.write(f"- Koefisien Korelasi (r): {r_value:.4f}")
st.write(f"- R-squared: {r_squared:.4f}")

# Input sampel
st.markdown("---")
st.markdown("### 🧪 Hitung Konsentrasi Sampel")
num_samples = st.number_input("Jumlah sampel", min_value=1, max_value=10, value=6)

sample_results = []
st.markdown("#### Hasil Perhitungan Konsentrasi:")
cols = st.columns(min(6, num_samples))

for i in range(num_samples):
    with cols[i % 6]:
        abs_val = st.number_input(
            f"Absorbansi S{i+1}", format="%.4f", key=f"s{i}"
        )
        conc_val = (abs_val - intercept) / slope if slope != 0 else 0
        conc_val = max(conc_val, 0)
        st.metric(label=f"Konsentrasi S{i+1}", value=f"{conc_val:.3f} ppm")
        sample_results.append({
            "Sampel": f"S{i+1}",
            "Absorbansi": f"{abs_val:.4f}",
            "Konsentrasi (ppm)": f"{conc_val:.3f}"
        })

# Tampilkan tabel hasil
if sample_results:
    st.markdown("#### 📋 Tabel Hasil:")
    st.table(pd.DataFrame(sample_results))

    # CV Horwitz
    st.markdown("#### 📉 Evaluasi Presisi (CV Horwitz)")
    horwitz_results = []
    horwitz_values = []

    for s in sample_results:
        ppm = float(s["Konsentrasi (ppm)"])
        C_decimal = ppm / 1_000_000
        if C_decimal > 0:
            cv_horwitz = 2 ** (1 - 0.5 * np.log10(C_decimal)) * 100
            horwitz_values.append(cv_horwitz)
        else:
            cv_horwitz = np.nan
        horwitz_results.append({
            "Sampel": s["Sampel"],
            "Konsentrasi (ppm)": f"{ppm:.3f}",
            "CV Horwitz (%)": f"{cv_horwitz:.2f}" if not np.isnan(cv_horwitz) else "NaN"
        })

    st.table(pd.DataFrame(horwitz_results))

    horwitz_values_clean = [v for v in horwitz_values if not np.isnan(v)]
    if horwitz_values_clean:
        avg_cv_horwitz = np.mean(horwitz_values_clean)
        st.markdown(f"📌 *Rata-rata CV Horwitz: {avg_cv_horwitz:.2f}%*")
