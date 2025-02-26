import streamlit as st
import numpy_financial as npf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    st.markdown("### 📜 Tabel Angsuran Pinjaman")
    st.dataframe(df_ang.style.format({
        "Saldo Awal": "Rp {:,.0f}",
        "Total Cicilan": "Rp {:,.0f}",
        "Angsuran Pokok": "Rp {:,.0f}",
        "Bunga": "Rp {:,.0f}",
        "Sisa Pinjaman": "Rp {:,.0f}",
    }), height=390, use_container_width=True)


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
        cumulative_cashflow = principal - df_ang["Angsuran Pokok"].cumsum()

        # Hitung Total
        total_pendapatan = sum(pendapatan_list)
        total_cicilan = sum(df_ang["Total Cicilan"])
        total_cashflow = sum(cashflow[1:])

        # Buat DataFrame Cashflow
        df_cashflow = pd.DataFrame({
            "Tahun": list(range(1, periods + 1)) + ["Total"],
            "Pendapatan": pendapatan_list + [total_pendapatan],
            "Total Cicilan": list(df_ang["Total Cicilan"]) + [total_cicilan],
            "Cashflow": cashflow[1:] + [total_cashflow],
        })

        risk_ratio = total_pendapatan / total_cicilan if total_cicilan > 0 else None

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
            }), height=420, use_container_width=True)

        # Tampilkan Grafik Cashflow
        #st.markdown("### 📈 Grafik Tren Arus Kas")

        # Atur ukuran font untuk seluruh elemen grafik
        plt.rcParams.update({'font.size': 7})  # Ukuran font kecil untuk semua elemen

        # Buat figure dengan ukuran lebih kecil
        fig, ax = plt.subplots(figsize=(6, 1.5))  # Lebar 6 inci, tinggi 3 inci
        ax.plot(range(1, num_periods + 1), cashflow[1:num_periods + 1], marker='o', linestyle='-', color='b', label="Cashflow")

        # Label dan Tampilan
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Cashflow (Rp)")
        ax.set_title("Tren Arus Kas")
        ax.legend(fontsize=8)
        ax.grid(True)

        # Sesuaikan sumbu X agar hanya menampilkan tahun yang relevan
        ax.set_xticks(range(1, num_periods + 1))

        # Tampilkan grafik di Streamlit
        with col_cashflow:
            st.pyplot(fig)

        # Analisis Risiko & IRR
        st.markdown("### 🔍 Analisis Risiko & Profitabilitas")
        
        st.markdown("#### 📊 Internal Rate of Return (IRR)")
        st.latex(r"IRR = \text{Tingkat Diskonto yang membuat } NPV = 0")
        st.write("**Interpretasi:** IRR menunjukkan tingkat pengembalian dari investasi ini. Jika IRR lebih besar dari suku bunga pinjaman, maka proyek ini menguntungkan.")
        if np.isnan(irr) or irr < 0:
            st.error(f"❌ **IRR Tidak Valid:** {irr_display}. Artinya, investasi ini tidak memberikan pengembalian yang cukup.")
        else:
            st.success(f"✅ **IRR:** {irr_display}. Jika lebih besar dari suku bunga pinjaman ({annual_rate:.2f}%), maka investasi ini menjanjikan.")
        
        st.markdown("#### ⚖️ Rasio Risiko")
        st.latex(r"Rasio\ Risiko = \frac{Total\ Pendapatan}{Total\ Cicilan}")
        st.write("**Interpretasi:** Rasio risiko membandingkan total pendapatan dengan total cicilan. Jika rasio lebih besar dari 1, pendapatan cukup untuk membayar cicilan.")
        if risk_ratio:
            if risk_ratio > 1:
                st.success(f"✅ **Rasio Risiko:** {risk_ratio:.2f} (Pendapatan cukup untuk menutup cicilan).")
            else:
                st.error(f"❌ **Rasio Risiko:** {risk_ratio:.2f} (Pendapatan tidak cukup, risiko tinggi).")
        else:
            st.warning("⚠️ Tidak dapat menghitung rasio risiko.")

        # Kesimpulan Analisa
        st.markdown("### 📌 Kesimpulan Analisa")
        kesimpulan = ""

        if np.isnan(irr) or irr < annual_rate / 100:
            kesimpulan += "❌ **Hasil Analisa:** IRR berada di bawah suku bunga pinjaman, yang berarti investasi ini perlu dipertimbangkan karena tingkat pengembaliannya tidak cukup tinggi.\n\n"
        elif irr >= annual_rate / 100 and irr < 0.15:  # IRR antara suku bunga dan 15% dianggap "Perlu dipertimbangkan"
            kesimpulan += f"⚖️ **Hasil Analisa:** IRR sebesar {irr_display}. Proyek ini memiliki potensi yang cukup baik, namun tetap perlu dianalisis lebih lanjut sebelum keputusan investasi diambil.\n\n"
        else:  # IRR di atas 15% dianggap "Sangat baik untuk investasi"
            kesimpulan += f"✅ **Hasil Analisa:** IRR sebesar {irr_display}. Proyek ini sangat baik untuk investasi karena tingkat pengembaliannya lebih tinggi dari suku bunga pinjaman dan cukup menarik.\n\n"

        if risk_ratio:
            if risk_ratio > 1.5:
                kesimpulan += f"✅ **Rasio Risiko:** {risk_ratio:.2f}, menandakan proyek ini memiliki pendapatan yang sangat cukup untuk menutup cicilan, sehingga aman untuk investasi.\n\n"
            elif risk_ratio > 1:
                kesimpulan += f"⚖️ **Rasio Risiko:** {risk_ratio:.2f}, menunjukkan bahwa pendapatan cukup untuk membayar cicilan, namun tetap perlu perhitungan lebih lanjut.\n\n"
            else:
                kesimpulan += f"❌ **Rasio Risiko:** {risk_ratio:.2f}, menunjukkan bahwa pendapatan tidak cukup untuk membayar cicilan, sehingga investasi ini memiliki risiko tinggi.\n\n"

        # Tentukan Sentimen Investasi
        sentimen = "🔵 Netral"
        if irr >= 0.15 and risk_ratio > 1.5:
            sentimen = "🟢 Positif (Investasi Menguntungkan)"
        elif irr < annual_rate / 100 or risk_ratio < 1:
            sentimen = "🔴 Negatif (Risiko Tinggi)"

        # Tambahkan ke Kesimpulan
        kesimpulan += f"**📌 Sentimen Investasi: {sentimen}**\n\n"

        st.info(kesimpulan)
  
      


