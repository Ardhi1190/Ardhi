import streamlit as st
import numpy_financial as npf
import pandas as pd
import numpy as np

# Konfigurasi Layout Wide
st.set_page_config(page_title="Kalkulator Investasi", layout="wide")

# Header
st.markdown("<h1 style='text-align: center; color: #007BFF;'>💰 Kalkulator Investasi 💰</h1>", unsafe_allow_html=True)
st.write("🔹 Hitung angsuran pinjaman dan analisis arus kas investasi.")

# Input Nama Proyek
project_name = st.text_input("🏢 Nama Proyek Investasi", "")

# Layout Input dan Tabel Angsuran
col_input, col_ang = st.columns([1, 2])
with col_input:
    st.markdown("### 📝 Input Data")
    principal_input = st.text_input("💵 Jumlah Pinjaman", "0")
    annual_rate = st.number_input("📊 Suku Bunga Tahunan (%)", min_value=0.0, value=0.0, step=0.1)
    num_periods = st.number_input("⏳ Jangka Waktu (Tahun)", min_value=1, value=1, step=1)

    # Konversi input jumlah pinjaman ke float
    try:
        principal = float(principal_input.replace(",", "").replace(".", ""))
    except ValueError:
        principal = 0

# Hitung Angsuran
rate = annual_rate / 100
periods = num_periods

if rate > 0:
    pmt = npf.pmt(rate, periods, -principal)
else:
    pmt = principal / periods

balance = principal
data = []
for i in range(1, periods + 1):
    saldo_awal = balance
    interest = balance * rate
    principal_payment = pmt - interest
    balance -= principal_payment
    data.append([i, saldo_awal, pmt, principal_payment, interest, max(0, balance)])

df_ang = pd.DataFrame(data, columns=["Tahun", "Saldo Awal", "Total Cicilan", "Angsuran Pokok", "Bunga", "Sisa Pinjaman"])
total_cicilan = sum(df_ang["Total Cicilan"])

# Tampilkan Tabel Angsuran
with col_ang:
    st.markdown(f"### 📊 Tabel Angsuran untuk Proyek: {project_name}")
    st.dataframe(df_ang.style.format({
        "Saldo Awal": "Rp {:,.0f}",
        "Total Cicilan": "Rp {:,.0f}",
        "Angsuran Pokok": "Rp {:,.0f}",
        "Bunga": "Rp {:,.0f}",
        "Sisa Pinjaman": "Rp {:,.0f}"
    }), use_container_width=True)

# Layout Input Pendapatan dan Tabel Cashflow
col_pendapatan, col_cashflow = st.columns([1, 2])
pendapatan_list = []
with col_pendapatan:
    st.markdown("### 💰 Masukkan Pendapatan")
    for i in range(1, num_periods + 1):
        pendapatan_input = st.text_input(f"Pendapatan Tahun {i}", "0")
        try:
            pendapatan = float(pendapatan_input.replace(",", "").replace(".", ""))
        except ValueError:
            pendapatan = 0
        pendapatan_list.append(pendapatan)

# Tombol Generate Perhitungan
generate_clicked = st.button("🔍 Generate Perhitungan", key="generate_btn")

# Jalankan perhitungan hanya setelah tombol ditekan
if generate_clicked:
    if not all(p > 0 for p in pendapatan_list) or principal <= 0:
        st.warning("⚠️ Harap masukkan semua pendapatan dan jumlah pinjaman sebelum melakukan perhitungan.")
    else:
        # Hitung Cashflow
        cashflow = [-principal] + [p - c for p, c in zip(pendapatan_list, df_ang["Total Cicilan"])]
        cumulative_cashflow = np.cumsum(cashflow)

        df_cashflow = pd.DataFrame({
            "Tahun": range(1, periods + 1),
            "Pendapatan": pendapatan_list,
            "Total Cicilan": df_ang["Total Cicilan"],
            "Cashflow": cashflow[1:],
            "Cumulative Cashflow": cumulative_cashflow[1:]
        })

        total_pendapatan = sum(pendapatan_list)
        risk_ratio = total_pendapatan / total_cicilan if total_cicilan > 0 else None

        # Perhitungan Payback Period
        payback_period = next((i+1 for i, c in enumerate(cumulative_cashflow[1:]) if c >= 0), None)

        # Perhitungan IRR
        irr = npf.irr(cashflow)
        irr_display = f"{irr*100:.2f}%" if not np.isnan(irr) else "Tidak dapat dihitung"

        # Tampilkan Tabel Cashflow
        with col_cashflow:
            st.markdown(f"### 📊 Tabel Arus Kas untuk Proyek: {project_name}")
            st.dataframe(df_cashflow.style.format({
                "Pendapatan": "Rp {:,.0f}",
                "Total Cicilan": "Rp {:,.0f}",
                "Cashflow": "Rp {:,.0f}",
                "Cumulative Cashflow": "Rp {:,.0f}"
            }), use_container_width=True)

        # Analisis Balik Modal & Risiko
        st.markdown("### 🔍 Analisis Balik Modal & Risiko")

        st.markdown("#### 📌 Payback Period")
        st.latex(r"Payback\ Period = \sum_{t=0}^{n} Cashflow_t \geq 0")
        st.write("**Dasar Perhitungan:** Payback period dihitung dengan mencari tahun pertama di mana arus kas kumulatif menjadi positif atau nol.")
        if payback_period is not None:
            st.success(f"✅ Proyek akan balik modal pada tahun ke-{payback_period}.")
        else:
            st.error("❌ Investasi belum balik modal dalam periode yang ditentukan.")

        st.markdown("---")  # Pembatas
        st.markdown("#### 📊 Internal Rate of Return (IRR)")
        st.latex(r"IRR = \text{Tingkat Diskonto yang membuat } NPV = 0")
        st.write("**Dasar Perhitungan:** IRR adalah tingkat pengembalian yang membuat Net Present Value (NPV) menjadi nol.")
        if np.isnan(irr) or irr < 0:
            st.error(f"❌ **IRR Tidak Valid:** {irr_display}. Jika negatif atau tidak dapat dihitung, maka investasi tidak menguntungkan.")
        else:
            st.success(f"✅ **IRR:** {irr_display}. Jika lebih besar dari suku bunga pinjaman ({annual_rate:.2f}%), maka investasi layak.")

        st.markdown("---")  # Pembatas
        st.markdown("#### ⚖️ Rasio Risiko")
        st.latex(r"Rasio\ Risiko = \frac{Total\ Pendapatan}{Total\ Cicilan}")
        st.write("**Dasar Perhitungan:** Rasio ini mengukur seberapa besar pendapatan dibandingkan dengan total cicilan.")
        if risk_ratio:
            if risk_ratio > 1:
                st.success(f"✅ **Rasio Risiko:** {risk_ratio:.2f} (Pendapatan cukup untuk menutup cicilan).")
            else:
                st.error(f"❌ **Rasio Risiko:** {risk_ratio:.2f} (Pendapatan tidak cukup, risiko tinggi).")
        else:
            st.warning("⚠️ Tidak dapat menghitung rasio risiko.")
