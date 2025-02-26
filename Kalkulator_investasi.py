import streamlit as st
import numpy_financial as npf
import pandas as pd
from fpdf import FPDF

# Konfigurasi Layout Wide
st.set_page_config(page_title="Kalkulator Investasi", layout="wide")

# Desain Header
st.markdown(
    "<h1 style='text-align: center; color: #007BFF;'>💰 Kalkulator Investasi 💰</h1>",
    unsafe_allow_html=True
)
st.write("🔹 Hitung angsuran pinjaman dan analisis arus kas investasi.")

# Input Nama Proyek
project_name = st.text_input("🏢 Nama Proyek Investasi", "")

# Layout Input Diperkecil
col_input, col_result = st.columns([1, 3])  # Kolom input lebih kecil, tabel lebih lebar

with col_input:
    st.markdown("### 📝 Input Data")
    principal_input = st.text_input("💵 Jumlah Pinjaman", "0")
    annual_rate = st.number_input("📊 Suku Bunga Tahunan (%)", min_value=0.0, value=0.0, step=0.1)
    num_periods = st.number_input("⏳ Jangka Waktu (Tahun)", min_value=1, value=1, step=1)

    # Convert input principal menjadi format dengan pemisah ribuan
    if principal_input != "":
        try:
            principal = float(principal_input.replace(",", "").replace(".", ""))  # Hapus koma atau titik jika ada
        except ValueError:
            principal = 0
    else:
        principal = 0

st.markdown("<hr>", unsafe_allow_html=True)  # Garis pemisah

# Kolom Pendapatan Muncul Sebelum Generate
pendapatan_list = []
col_input_small, col_table_wide = st.columns([1, 3])  # Kolom input kecil, tabel lebih lebar

with col_input_small:
    st.markdown("### 💰 Masukkan Pendapatan")
    for i in range(1, num_periods + 1):
        pendapatan_input = st.text_input(f"Pendapatan Tahun {i}", "0")
        try:
            pendapatan = float(pendapatan_input.replace(",", "").replace(".", ""))
        except ValueError:
            pendapatan = 0
        pendapatan_list.append(pendapatan)
st.markdown("<hr>", unsafe_allow_html=True)  # Garis pemisah

# Tombol Generate (Tetap Tampil)
generate_clicked = st.button("🔍 Generate Perhitungan", key="generate_btn")

# Perhitungan Hanya Jika Semua Input Terisi
if generate_clicked:
    # Validasi input
    missing_input = []
    if not project_name:
        missing_input.append("Nama Proyek")
    if principal <= 0:
        missing_input.append("Jumlah Pinjaman")
    if annual_rate <= 0:
        missing_input.append("Suku Bunga Tahunan")
    if num_periods <= 0:
        missing_input.append("Jangka Waktu (Tahun)")
    if any(p <= 0 for p in pendapatan_list):
        missing_input.append("Pendapatan")

    # Jika ada input yang hilang, beri peringatan
    if missing_input:
        st.warning(f"⚠️ Harap isi data berikut: {', '.join(missing_input)}")
    else:
        rate = (annual_rate / 100)
        periods = num_periods
        period_label = "Tahun"

        if rate > 0:
            pmt = npf.pmt(rate, periods, -principal)
        else:
            pmt = principal / periods

        # Perhitungan Tabel Angsuran
        balance = principal
        data = []

        for i in range(1, periods + 1):
            saldo_awal = balance
            interest = balance * rate
            principal_payment = pmt - interest
            balance -= principal_payment
            data.append([i, saldo_awal, pmt, principal_payment, interest, max(0, balance)])

        df_ang = pd.DataFrame(data, columns=[period_label, "Saldo Awal", "Total Cicilan", "Angsuran Pokok", "Bunga", "Sisa Pinjaman"])

        # Tampilkan Tabel Angsuran di Kolom Lebar
        with col_result:
            st.markdown(f"### 📊 Tabel Angsuran untuk Proyek: {project_name}")
            st.dataframe(df_ang.style.format({
                "Saldo Awal": "Rp {:,.0f}",
                "Total Cicilan": "Rp {:,.0f}",
                "Angsuran Pokok": "Rp {:,.0f}",
                "Bunga": "Rp {:,.0f}",
                "Sisa Pinjaman": "Rp {:,.0f}"
            }))

        # Hitung Cashflow & IRR
        df_pendapatan = pd.DataFrame({period_label: range(1, periods + 1), "Pendapatan": pendapatan_list})
        cashflow = [-principal] + [p - c for p, c in zip(pendapatan_list, df_ang["Total Cicilan"])]
        irr_value = npf.irr(cashflow)

        # Tampilkan Tabel Arus Kas Lebih Lebar
        with col_table_wide:
            st.markdown(f"### 📊 Tabel Arus Kas untuk Proyek: {project_name}")
            df_cashflow = pd.DataFrame({
                period_label: range(1, periods + 1),
                "Pendapatan": pendapatan_list,
                "Total Cicilan": df_ang["Total Cicilan"],
                "Cashflow": [p - c for p, c in zip(pendapatan_list, df_ang["Total Cicilan"])]
            })
            st.dataframe(df_cashflow.style.format({
                "Pendapatan": "Rp {:,.0f}",
                "Total Cicilan": "Rp {:,.0f}",
                "Cashflow": "Rp {:,.0f}"
            }))

        # Pindahkan IRR setelah tabel cashflow
        st.subheader(f"📈 Internal Rate of Return (IRR): {irr_value:.2%}")

        # Kesimpulan Otomatis
        if irr_value > 0.1:
            st.markdown("### 🔹 Kesimpulan: Investasi Menguntungkan")
            st.write(
                f"📊 IRR yang dihitung sebesar **{irr_value*100:.2f}%** menunjukkan bahwa investasi ini memberikan return yang positif. Jika Anda mencari investasi yang menghasilkan return lebih dari 10%, maka ini adalah pilihan yang tepat!"
            )
        else:
            st.markdown("### 🔹 Kesimpulan: Investasi Kurang Menguntungkan")
            st.write(
                f"📉 IRR yang dihitung sebesar **{irr_value*100:.2f}%** menunjukkan bahwa investasi ini menghasilkan return yang rendah. Mungkin Anda ingin mempertimbangkan kembali keputusan investasi ini."
            )

        # Tombol Print untuk mengunduh data dalam format PDF
        print_pdf = st.button("🖨️ Cetak Data sebagai PDF")
        if print_pdf:
            try:
                # Membuat PDF
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                pdf.cell(200, 10, txt="Kalkulator Investasi", ln=True, align="C")
                pdf.cell(200, 10, txt=f"Nama Proyek: {project_name}", ln=True)

                # Menambahkan tabel Cashflow
                pdf.cell(200, 10, txt="Tabel Arus Kas:", ln=True)
                for i in range(len(df_cashflow)):
                    pdf.cell(40, 10, txt=str(df_cashflow.iloc[i][period_label]), border=1, align="C")
                    pdf.cell(60, 10, txt=f"Rp {df_cashflow.iloc[i]['Pendapatan']:,}", border=1, align="C")
                    pdf.cell(60, 10, txt=f"Rp {df_cashflow.iloc[i]['Total Cicilan']:,}", border=1, align="C")
                    pdf.cell(60, 10, txt=f"Rp {df_cashflow.iloc[i]['Cashflow']:,}", border=1, align="C")
                    pdf.ln()

                # Menyimpan PDF ke file dan memberikan link download
                pdf_output = pdf.output(dest='S').encode('utf-8')

                # Menggunakan Streamlit untuk mendownload PDF
                st.download_button(
                    label="Unduh PDF",
                    data=pdf_output,
                    file_name=f"{project_name}_cashflow.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Gagal membuat PDF: {e}")
