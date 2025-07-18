import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Konfigurasi halaman
st.set_page_config(page_title="Spektrofotometri Sederhana", layout="wide")
st.title("📊 Analisis Spektrofotometri - Beer's Law")

st.markdown("Masukkan minimal 3 data standar (konsentrasi dan absorbansi):")

# Input data standar
num_std = st.number_input("Jumlah data standar:", min_value=3, max_value=10, value=3, step=1)
std_data = []

for i in range(num_std):
    col1, col2 = st.columns(2)
    with col1:
        conc = st.number_input(f"Konsentrasi Standar {i+1} (ppm):", key=f"conc_{i}")
    with col2:
        absorb = st.number_input(f"Absorbansi Standar {i+1}:", key=f"abs_{i}")
    std_data.append((conc, absorb))

# Hitung regresi jika data lengkap
if all(c > 0 and a > 0 for c, a in std_data):
    concentrations, absorbances = zip(*std_data)
    slope, intercept, r_value, _, _ = linregress(concentrations, absorbances)

    st.markdown("### 📈 Grafik Kalibrasi")
    fig, ax = plt.subplots()
    ax.scatter(concentrations, absorbances, color='blue', label='Data Standar')
    x_vals = np.array(concentrations)
    y_vals = slope * x_vals + intercept
    ax.plot(x_vals, y_vals, color='red', label=f'y = {slope:.4f}x + {intercept:.4f}')
    ax.set_xlabel("Konsentrasi (ppm)")
    ax.set_ylabel("Absorbansi")
    ax.legend()
    st.pyplot(fig)

    st.markdown(f"**Persamaan Regresi:** y = {slope:.4f}x + {intercept:.4f}")
    st.markdown(f"**R² (Koefisien Determinasi):** {r_value**2:.4f}")

    # Input data sampel
    st.markdown("---")
    st.markdown("### 🧪 Data Sampel")
    num_samples = st.number_input("Jumlah sampel:", min_value=1, max_value=10, value=2, step=1)
    sample_results = []

    for i in range(num_samples):
        absorb = st.number_input(f"Absorbansi Sampel S{i+1}:", key=f"samp_abs_{i}")
        concentration = (absorb - intercept) / slope if slope != 0 else 0
        sample_results.append({
            "Sampel": f"S{i+1}",
            "Absorbansi": absorb,
            "Konsentrasi (ppm)": concentration
        })
        st.write(f"**S{i+1} → Konsentrasi: {concentration:.3f} ppm**")

    # Evaluasi Akurasi (%RPD) jika ada pasangan duplikat
    if num_samples >= 2 and num_samples % 2 == 0:
        st.markdown("### 🎯 Evaluasi Akurasi (%RPD)")
        for i in range(0, num_samples, 2):
            c1 = sample_results[i]["Konsentrasi (ppm)"]
            c2 = sample_results[i+1]["Konsentrasi (ppm)"]
            avg = (c1 + c2) / 2
            rpd = abs(c1 - c2) / avg * 100 if avg != 0 else 0
            status = "✅ Akurasi Baik" if rpd <= 10 else "❌ Akurasi Buruk"
            st.write(f"Pasangan S{i+1} & S{i+2}: %RPD = {rpd:.2f}% — {status}")

    # Evaluasi Presisi (CV Horwitz)
    st.markdown("### 📉 Evaluasi Presisi (CV Horwitz)")
    for s in sample_results:
        ppm = s["Konsentrasi (ppm)"]
        C_decimal = ppm / 1_000_000  # ppm ke proporsi
        if C_decimal > 0:
            cv_horwitz = 2 ** (1 - 0.5 * np.log10(C_decimal)) * 100
            status = "✅ Presisi Baik" if cv_horwitz <= 22 else "❌ Presisi Buruk"
            st.write(f"{s['Sampel']}: CV Horwitz = {cv_horwitz:.2f}% — {status}")
        else:
            st.write(f"{s['Sampel']}: CV Horwitz tidak dapat dihitung (konsentrasi = 0)")
else:
    st.warning("Mohon isi semua data standar dengan benar (tidak boleh nol).")
