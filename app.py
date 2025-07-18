import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

st.set_page_config(page_title="Spektrofotometri Sederhana", layout="wide")
st.title("📊 Analisis Spektrofotometri - Beer's Law")

st.markdown("Masukkan minimal 6 data standar (konsentrasi dan absorbansi):")

# Input data standar
num_std = st.number_input("Jumlah data standar", min_value=6, max_value=20, value=6)
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

# Plot kurva kalibrasi
fig, ax = plt.subplots()
x_fit = np.linspace(0, df["Konsentrasi"].max()*1.1, 100)
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

cols = st.columns(min(6, num_samples))  # Maks. 6 kolom per baris

for i in range(num_samples):
    with cols[i % 6]:
        abs_val = st.number_input(
            f"Absorbansi S{i+1}", min_value=0.0, max_value=3.0, format="%.4f", key=f"s{i}"
        )
        conc_val = (abs_val - intercept) / slope if slope != 0 else 0
        conc_val = max(conc_val, 0)
        st.metric(label=f"Konsentrasi S{i+1}", value=f"{conc_val:.3f} ppm")
        sample_results.append({
            "Sampel": f"S{i+1}",
            "Absorbansi": abs_val,
            "Konsentrasi (ppm)": conc_val
        })

# Tampilkan tabel hasil
if sample_results:
    st.markdown("#### 📋 Tabel Hasil:")
    res_df = pd.DataFrame(sample_results)
    st.dataframe(res_df.style.format({
        "Absorbansi": "%.4f",
        "Konsentrasi (ppm)": "%.3f"
    }), hide_index=True)

    # =========================
    # 🔸 %RPD (akurasi duplikat)
    # =========================
    if num_samples >= 2 and num_samples % 2 == 0:
        st.markdown("#### 🎯 Evaluasi Akurasi (%RPD untuk Duplikat)")

        rpd_results = []
        rpd_values = []
        for i in range(0, num_samples, 2):
            c1 = sample_results[i]["Konsentrasi (ppm)"]
            c2 = sample_results[i+1]["Konsentrasi (ppm)"]
            avg = (c1 + c2) / 2
            rpd = abs(c1 - c2) / avg * 100 if avg != 0 else 0
            rpd_values.append(rpd)
            rpd_results.append({
                "Pasangan": f"S{i+1} & S{i+2}",
                "%RPD": rpd
            })

        rpd_df = pd.DataFrame(rpd_results)
        st.dataframe(rpd_df.style.format({"%RPD": "%.2f"}), hide_index=True)

        # Tampilkan nilai rata-rata %RPD
        avg_rpd = np.mean(rpd_values)
        st.markdown(f"📌 *Nilai Akurasi (%RPD rata-rata): {avg_rpd:.2f}%*")

    # =========================
    # 🔸 CV Horwitz (presisi)
    # =========================
    st.markdown("#### 📉 Evaluasi Presisi (CV Horwitz)")
    horwitz_results = []
    horwitz_values = []

    for s in sample_results:
        ppm = s["Konsentrasi (ppm)"]
        C_decimal = ppm / 1_000_000  # ppm ke proporsi
        if C_decimal > 0:
            cv_horwitz = 2 ** (1 - 0.5 * np.log10(C_decimal)) * 100
            horwitz_values.append(cv_horwitz)
        else:
            cv_horwitz = np.nan
        horwitz_results.append({
            "Sampel": s["Sampel"],
            "Konsentrasi (ppm)": ppm,
            "CV Horwitz (%)": cv_horwitz
        })

    cv_df = pd.DataFrame(horwitz_results)
    st.dataframe(cv_df.style.format({
        "Konsentrasi (ppm)": "%.3f",
        "CV Horwitz (%)": "%.2f"
    }), hide_index=True)

    # Tampilkan nilai rata-rata CV Horwitz
    horwitz_values_clean = [v for v in horwitz_values if not np.isnan(v)]
    if horwitz_values_clean:
        avg_cv_horwitz = np.mean(horwitz_values_clean)
        st.markdown(f"📌 *Rata-rata CV Horwitz: {avg_cv_horwitz:.2f}%*")
