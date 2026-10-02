
import streamlit as st
import numpy_financial as npf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# 1. KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Kalkulator Pinjaman",
    layout="wide"
)

st.markdown(
    """
    <h1 style='text-align: center; color: #007BFF;'>
        💰 Kalkulator Pinjaman 💰
    </h1>
    """,
    unsafe_allow_html=True
)

st.write(
    "🔹 Hitung angsuran pinjaman."
)

# =========================================================
# 2. FUNGSI BANTUAN
# =========================================================
def parse_rupiah(value):
    """Mengubah input Rupiah format Indonesia menjadi angka."""
    try:
        cleaned = str(value).strip().replace("Rp", "").replace(" ", "")
        if not cleaned:
            return 0.0

        if "," in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(".", "")

        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def format_rupiah(value):
    return f"Rp {value:,.0f}"


# =========================================================
# 3. INPUT NAMA PROYEK
# =========================================================
project_name = st.text_input(
    "🏢 Nama Proyek",
    ""
)

# =========================================================
# 4. INPUT DATA PINJAMAN
# =========================================================
col_input, col_ang = st.columns([1, 2])

with col_input:
    st.markdown("### 📝 Input Data")

    principal_input = st.text_input(
        "💵 Jumlah Pinjaman",
        "30.299.999.996"
    )

    annual_rate = st.number_input(
        "📊 Suku Bunga Tahunan (%)",
        min_value=0.0,
        value=8.0,
        step=0.1,
        format="%.2f"
    )

    num_periods = st.number_input(
        "⏳ Jangka Waktu (Tahun)",
        min_value=1,
        value=15,
        step=1
    )

    principal = parse_rupiah(principal_input)

# =========================================================
# 5. PERHITUNGAN ANGSURAN BULANAN
# =========================================================
rate = annual_rate / 100
periods = int(num_periods)
monthly_periods = periods * 12
monthly_rate = rate / 12

if principal > 0:
    if monthly_rate > 0:
        pmt_monthly = npf.pmt(
            monthly_rate,
            monthly_periods,
            -principal
        )
    else:
        pmt_monthly = principal / monthly_periods
else:
    pmt_monthly = 0.0

# =========================================================
# 6. GENERATE TABEL ANGSURAN BULANAN
# =========================================================
balance = principal
data_monthly = []

for i in range(1, monthly_periods + 1):
    year = (i - 1) // 12 + 1
    month = (i - 1) % 12 + 1

    saldo_awal = balance
    interest = saldo_awal * monthly_rate

    if i == monthly_periods:
        # Pelunasan seluruh sisa pokok pada bulan terakhir
        principal_payment = saldo_awal
        total_payment = principal_payment + interest
        balance = 0.0
    else:
        total_payment = pmt_monthly
        principal_payment = total_payment - interest
        balance = max(0.0, saldo_awal - principal_payment)

    data_monthly.append([
        i,
        year,
        month,
        saldo_awal,
        principal_payment,
        interest,
        total_payment,
        balance
    ])

df_ang_bulanan = pd.DataFrame(
    data_monthly,
    columns=[
        "Bulan Ke",
        "Tahun",
        "Bulan",
        "Saldo Awal",
        "Angsuran Pokok",
        "Bunga",
        "Total Cicilan",
        "Sisa Pinjaman"
    ]
)

# =========================================================
# 7. RINGKASAN ANGSURAN TAHUNAN
# =========================================================
df_ang_tahunan = (
    df_ang_bulanan
    .groupby("Tahun", as_index=False)
    .agg({
        "Saldo Awal": "first",
        "Angsuran Pokok": "sum",
        "Bunga": "sum",
        "Total Cicilan": "sum",
        "Sisa Pinjaman": "last"
    })
)

total_cicilan = df_ang_bulanan["Total Cicilan"].sum()

# =========================================================
# 8. TAMPILAN TABEL ANGSURAN
# =========================================================
with col_ang:
    st.subheader(
        "📌 Perhitungan Angsuran Menggunakan Formula PMT"
    )

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "💳 Angsuran per Bulan",
            format_rupiah(pmt_monthly)
        )

    with metric2:
        st.metric(
            "📅 Angsuran per Tahun",
            format_rupiah(
                df_ang_tahunan["Total Cicilan"].iloc[0]
            )
        )

    st.markdown(
        f"### 📜 Tabel Angsuran Pinjaman: {project_name}"
    )

    tab_tahunan, tab_bulanan = st.tabs([
        "📅 Angsuran Tahunan",
        "📆 Angsuran Bulanan"
    ])

    # -----------------------------------------------------
    # TABEL ANGSURAN TAHUNAN
    # -----------------------------------------------------
    with tab_tahunan:
        st.caption(
            "Ringkasan angsuran tahunan berdasarkan akumulasi "
            "12 bulan angsuran."
        )

        st.dataframe(
            df_ang_tahunan.style.format({
                "Saldo Awal": "Rp {:,.0f}",
                "Angsuran Pokok": "Rp {:,.0f}",
                "Bunga": "Rp {:,.0f}",
                "Total Cicilan": "Rp {:,.0f}",
                "Sisa Pinjaman": "Rp {:,.0f}"
            }),
            height=390,
            use_container_width=True,
            hide_index=True
        )

        csv_loan_annual = df_ang_tahunan.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="⬇️ Download Angsuran Tahunan",
            data=csv_loan_annual,
            file_name="angsuran_tahunan.csv",
            mime="text/csv",
            key="download_loan_annual"
        )

    # -----------------------------------------------------
    # TABEL ANGSURAN BULANAN - SELURUH PERIODE
    # -----------------------------------------------------
    with tab_bulanan:
        st.caption(
            "Seluruh periode angsuran ditampilkan sekaligus. "
            "Scroll tabel untuk melihat bulan berikutnya."
        )

        # Tidak menampilkan kolom Bulan Ke
        df_loan_display = df_ang_bulanan[[
            "Tahun",
            "Bulan",
            "Saldo Awal",
            "Angsuran Pokok",
            "Bunga",
            "Total Cicilan",
            "Sisa Pinjaman"
        ]].copy()

        st.dataframe(
            df_loan_display.style.format({
                "Saldo Awal": "Rp {:,.0f}",
                "Angsuran Pokok": "Rp {:,.0f}",
                "Bunga": "Rp {:,.0f}",
                "Total Cicilan": "Rp {:,.0f}",
                "Sisa Pinjaman": "Rp {:,.0f}"
            }),
            height=450,
            use_container_width=True,
            hide_index=True
        )

        csv_loan_monthly = df_loan_display.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="⬇️ Download Angsuran Bulanan",
            data=csv_loan_monthly,
            file_name="angsuran_bulanan.csv",
            mime="text/csv",
            key="download_loan_monthly"
        )

