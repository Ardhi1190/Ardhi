import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from io import StringIO

# Atur layout fullscreen
st.set_page_config(layout="wide")

# Tambahkan Judul Dashboard
st.title("📊 Dashboard Analisis Item Survey Employee Happiness & Engagement")

# URL Google Sheets dalam format CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1V_wGUbLyDn6Uo5_EyFeLRp4AgZiYB72csQQJJEg5Yn8/export?format=csv"

@st.cache_data
def load_google_sheets(url):
    response = requests.get(url, verify=False)  # Hapus verify=False untuk keamanan
    if response.status_code == 200:
        data = StringIO(response.text)
        df = pd.read_csv(data)

        # Mapping respon ke angka
        mapping = {
            'Sangat Setuju': 4,
            'Setuju': 3,
            'Tidak Setuju': 2,
            'Sangat Tidak Setuju': 1
        }

        start_col = 6  # Kolom ke-7 ke akhir berisi pertanyaan
        statement_columns = df.columns[start_col:]

        df[statement_columns] = df[statement_columns].replace(mapping)
        df[statement_columns] = df[statement_columns].apply(pd.to_numeric, errors='coerce').fillna(0)

        return df, statement_columns
    return None, None

# Ambil data
df, statement_columns = load_google_sheets(sheet_url)

if df is not None:
    jabatan_list = ["All"] + sorted(df["Posisi/Jabatan"].dropna().unique().tolist())
    selected_jabatan = st.selectbox("Pilih Jabatan:", jabatan_list)
    df_filtered = df if selected_jabatan == "All" else df[df["Posisi/Jabatan"] == selected_jabatan]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### Total Responden Berdasarkan Jabatan")
        jabatan_counts = df_filtered["Posisi/Jabatan"].value_counts()
        total_responden = jabatan_counts.sum()  # Menghitung total responden
    
        # Menampilkan total responden di Streamlit
        st.write(f"**Total Responden: {total_responden}**")

        if not jabatan_counts.empty:
            fig, ax = plt.subplots(figsize=(5, 5))  # Ukuran diperbesar

            # Warna dinamis sesuai jumlah kategori
            colors = plt.get_cmap("Set3")(np.linspace(0, 1, len(jabatan_counts)))

            # Pie chart
            wedges, texts, autotexts = ax.pie(
                jabatan_counts, 
                labels=jabatan_counts.index, 
                autopct=lambda p: f'{int(p * total_responden / 100)}' if total_responden > 0 else '',
                startangle=90, 
                colors=colors
            )

            ax.axis("equal")  # Menjaga proporsi lingkaran

            # Ubah teks autopct agar hanya menampilkan angka (bukan persen)
            for autotext, count in zip(autotexts, jabatan_counts):
                autotext.set_text(f"{count}")  # Ganti teks dengan angka responden
            
            # Perbaikan ukuran teks agar lebih terbaca
            for text in texts:
                text.set_fontsize(10)  
            for autotext in autotexts:
                autotext.set_fontsize(10)  

            st.pyplot(fig)
        else:
            st.warning("Tidak ada data responden untuk filter ini.")

    with col2:
        #st.write("### Rata-rata Nilai Berdasarkan Jabatan")

        if not df_filtered.empty:
            # Employee Happiness
            #st.subheader("Employee Happiness")
            happiness_columns = df.columns[6:22]  
            avg_happiness = df_filtered[happiness_columns].mean(numeric_only=True).round(2)

            # Tampilkan dalam bentuk tabel
            #st.dataframe(avg_happiness.to_frame(name="Rata-rata Skor"), use_container_width=True)

            # Grafik Employee Happiness (Horizontal Bar Chart)
            st.subheader("Employee Happiness")

            # Hitung rata-rata keseluruhan Employee Happiness
            overall_avg_happiness = avg_happiness.mean().round(2)

            # Menentukan pertanyaan dengan nilai terbesar & terkecil
            max_question = avg_happiness.idxmax()  # Pertanyaan dengan skor tertinggi
            max_value = avg_happiness.max()

            min_question = avg_happiness.idxmin()  # Pertanyaan dengan skor terendah
            min_value = avg_happiness.min()

            # Tampilkan rata-rata keseluruhan di Streamlit
            st.write(f"**Rata-rata Keseluruhan Employee Happiness: {overall_avg_happiness}**")
            st.write(f"📈 **Item dengan skor tertinggi**: `{max_question}` ({max_value})")
            st.write(f"📉 **Item dengan skor terendah**: `{min_question}` ({min_value})")

            fig, ax = plt.subplots(figsize=(8, 10))  # Ukuran lebih besar untuk keterbacaan
            bars = ax.barh(avg_happiness.index, avg_happiness.values, color="blue")

            # Tambahkan label nilai pada setiap batang
            for bar in bars:
                ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
                        f"{bar.get_width():.2f}", va='center', ha='left', fontsize=10, color="black")

            ax.set_xlabel("Rata-rata Skor")
            ax.set_ylabel("Kategori")
            ax.set_title("Rata-rata Employee Happiness")
            st.pyplot(fig)

            # Employee Engagement
            #st.subheader("Employee Engagement")
            engagement_columns = df.columns[22:44]  
            avg_engagement = df_filtered[engagement_columns].mean(numeric_only=True).round(2)

            # Tampilkan dalam bentuk tabel
            #st.dataframe(avg_engagement.to_frame(name="Rata-rata Skor"), use_container_width=True)

            ## Grafik Employee Engagement (Horizontal Bar Chart)
            st.subheader("Employee Engagement")

            # Hitung rata-rata keseluruhan Employee Engagement
            overall_avg_engagement = avg_engagement.mean().round(2)

            # Menentukan pertanyaan dengan nilai terbesar & terkecil
            max_question = avg_engagement.idxmax()  # Pertanyaan dengan skor tertinggi
            max_value = avg_engagement.max()

            min_question = avg_engagement.idxmin()  # Pertanyaan dengan skor terendah
            min_value = avg_engagement.min()

            # Tampilkan rata-rata keseluruhan di Streamlit
            st.write(f"**Rata-rata Keseluruhan Employee Engagement: {overall_avg_engagement}**")
            st.write(f"📈 **Item dengan skor tertinggi**: `{max_question}` ({max_value})")
            st.write(f"📉 **Item dengan skor terendah**: `{min_question}` ({min_value})")
            
            fig, ax = plt.subplots(figsize=(8, 10))  # Ukuran lebih besar agar lebih jelas
            bars = ax.barh(avg_engagement.index, avg_engagement.values, color="green")  # Warna berbeda untuk membedakan

            # Tambahkan label nilai pada setiap batang
            for bar in bars:
                ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
                        f"{bar.get_width():.2f}", va='center', ha='left', fontsize=10, color="black")

            ax.set_xlabel("Rata-rata Skor")
            ax.set_ylabel("Kategori")
            ax.set_title("Rata-rata Employee Engagement")
            st.pyplot(fig)

        else:
            st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")

            
    st.write("### 📊 Uji Validitas Employee Happiness & Engagement")

if df is not None:
    if not df_filtered.empty:
        # Ambil kolom Employee Happiness & Employee Engagement
        happiness_columns = df.columns[6:22]  
        engagement_columns = df.columns[22:44]  

        # Hitung skor total untuk Employee Happiness & Engagement
        df_filtered["Total Happiness"] = df_filtered[happiness_columns].sum(axis=1)
        df_filtered["Total Engagement"] = df_filtered[engagement_columns].sum(axis=1)

        ### **1️⃣ Hitung Korelasi Setiap Item dengan Total Skor**
        happiness_validity = df_filtered[happiness_columns].corrwith(df_filtered["Total Happiness"])
        engagement_validity = df_filtered[engagement_columns].corrwith(df_filtered["Total Engagement"])

        ### **2️⃣ Tampilkan Hasil Validitas dalam Kolom**
        col1, col2 = st.columns([1, 1])

        with col1:
            st.write("### 🔍 Validitas Employee Happiness")
            st.dataframe(happiness_validity.to_frame(name="Korelasi dengan Total Happiness"))

        with col2:
            st.write("### 🔍 Validitas Employee Engagement")
            st.dataframe(engagement_validity.to_frame(name="Korelasi dengan Total Engagement"))

        ### **3️⃣ Kesimpulan Uji Validitas (Di Luar Layout Kolom)**
        st.write("### 📌 Kesimpulan Uji Validitas")

        def interpret_validity(correlation, label):
            invalid_questions = correlation[correlation < 0.3].index.tolist()
            if invalid_questions:
                return f"❌ Beberapa item dalam {label} tidak valid: {', '.join(invalid_questions)}"
            else:
                return f"✅ Semua item dalam {label} valid."

        st.write(interpret_validity(happiness_validity, "Employee Happiness"))
        st.write(interpret_validity(engagement_validity, "Employee Engagement"))

    else:
        st.warning("Tidak cukup data untuk melakukan uji validitas.")
        
    st.write("### 🔥 Korelasi Rata-rata Nilai Employee Happiness & Employee Engagement")

if df is not None:
    if not df_filtered.empty:
        # Ambil kolom Employee Happiness & Employee Engagement
        happiness_columns = df.columns[6:22]  # Employee Happiness
        engagement_columns = df.columns[22:44]  # Employee Engagement

        # Hitung rata-rata per responden
        df_avg = pd.DataFrame({
            "Employee Happiness": df_filtered[happiness_columns].mean(axis=1),
            "Employee Engagement": df_filtered[engagement_columns].mean(axis=1)
        })

        # Hitung korelasi Spearman antara rata-rata Employee Happiness & Engagement
        spearman_corr = df_avg.corr(method='spearman')

        # Membuat heatmap manual dengan Matplotlib
        fig, ax = plt.subplots(figsize=(6, 5))
        cax = ax.matshow(spearman_corr, cmap="coolwarm", vmin=-1, vmax=1)
        fig.colorbar(cax)

        # Menyesuaikan label sumbu X dan Y
        categories = ["Employee Happiness", "Employee Engagement"]
        ax.set_xticks(range(len(categories)))
        ax.set_yticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, fontsize=10, ha="right")
        ax.set_yticklabels(categories, fontsize=10)

        # Menampilkan angka korelasi dalam heatmap
        for (i, j), val in np.ndenumerate(spearman_corr.values):
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=12)

        ax.xaxis.set_ticks_position("bottom")
        ax.xaxis.set_label_position("bottom")

        st.pyplot(fig)

        ### Kesimpulan Otomatis ###
        correlation_value = spearman_corr.iloc[0, 1]  # Korelasi antara Happiness & Engagement

        st.write("### 🔍 Kesimpulan dari Korelasi")
        if correlation_value > 0.5:
            st.write(f"✅ **Employee Happiness dan Engagement memiliki korelasi positif yang kuat (r = {correlation_value:.2f})**")
        elif correlation_value < -0.5:
            st.write(f"❌ **Employee Happiness dan Engagement memiliki korelasi negatif yang kuat (r = {correlation_value:.2f})**")
        else:
            st.write(f"ℹ️ **Employee Happiness dan Engagement memiliki korelasi lemah (r = {correlation_value:.2f})**")

    else:
        st.warning("Tidak cukup data untuk menghitung korelasi.")

        

    st.write("### 🔥 Korelasi Nilai per Indikator Employee Happiness & Employee Engagement")

if df is not None:
    if not df_filtered.empty:
        # Ambil kolom Employee Happiness & Employee Engagement
        happiness_columns = df.columns[6:22]  # Employee Happiness
        engagement_columns = df.columns[22:44]  # Employee Engagement

        # Gabungkan subset data
        selected_columns = list(happiness_columns) + list(engagement_columns)
        spearman_corr = df_filtered[selected_columns].corr(method='spearman').fillna(0)

        # Membuat heatmap manual dengan Matplotlib
        fig, ax = plt.subplots(figsize=(12, 10))
        cax = ax.matshow(spearman_corr, cmap="coolwarm", vmin=-1, vmax=1)
        fig.colorbar(cax)

        # Menyesuaikan label sumbu X dan Y
        ax.set_xticks(range(len(selected_columns)))
        ax.set_yticks(range(len(selected_columns)))
        ax.set_xticklabels(selected_columns, rotation=75, fontsize=8, ha="right")
        ax.set_yticklabels(selected_columns, fontsize=8)

        # Menampilkan angka korelasi dalam heatmap
        for (i, j), val in np.ndenumerate(spearman_corr.values):
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=7)

        ax.xaxis.set_ticks_position("bottom")
        ax.xaxis.set_label_position("bottom")

        st.pyplot(fig)

        ### Kesimpulan Otomatis ###
        spearman_corr_unstacked = spearman_corr.where(np.triu(np.ones(spearman_corr.shape), k=1).astype(bool)).stack()
        strongest_positive = spearman_corr_unstacked.idxmax()
        strongest_negative = spearman_corr_unstacked.idxmin()
        max_corr_value = spearman_corr_unstacked.max()
        min_corr_value = spearman_corr_unstacked.min()

        st.write("### 🔍 Kesimpulan dari Korelasi")
        if max_corr_value > 0.5:
            st.write(f"✅ **Korelasi positif terkuat**: **{strongest_positive[0]}** & **{strongest_positive[1]}** (r = {max_corr_value:.2f})")
        else:
            st.write("ℹ️ Tidak ada korelasi positif yang kuat (r > 0.5).")

        if min_corr_value < -0.5:
            st.write(f"❌ **Korelasi negatif terkuat**: **{strongest_negative[0]}** & **{strongest_negative[1]}** (r = {min_corr_value:.2f})")
        else:
            st.write("ℹ️ Tidak ada korelasi negatif yang kuat (r < -0.5).")

    else:
        st.warning("Tidak cukup data untuk menghitung korelasi.")

else:
    st.error("Gagal mengambil data. Cek kembali URL atau izin Google Sheets.")