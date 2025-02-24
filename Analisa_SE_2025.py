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
st.markdown("---")

# URL Google Sheets dalam format CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1V_wGUbLyDn6Uo5_EyFeLRp4AgZiYB72csQQJJEg5Yn8/export?format=csv"
if st.button("🔄 Perbarui Data"):
    st.cache_data.clear()
    st.rerun()
@st.cache_data(ttl=30)  # Cache berlaku selama 30 Detik

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
    # 🎯 **Filter Data**
    st.markdown("## 🎯 **Filter Data**", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        jabatan_list = ["All"] + sorted(df["Posisi/Jabatan"].dropna().unique().tolist())
        selected_jabatan = st.selectbox("📌 Pilih Jabatan:", jabatan_list)
    with col2:
        masa_kerja_list = ["All"] + sorted(df["Masa Kerja"].dropna().unique().tolist())
        selected_masa_kerja = st.selectbox("📌 Pilih Masa Kerja:", masa_kerja_list)
    with col3:
        usia_list = ["All"] + sorted(df["Usia"].dropna().unique().tolist())
        selected_usia = st.selectbox("📌 Pilih Usia:", usia_list)

    df_filtered = df
    if selected_jabatan != "All":
        df_filtered = df_filtered[df_filtered["Posisi/Jabatan"] == selected_jabatan]
    if selected_masa_kerja != "All":
        df_filtered = df_filtered[df_filtered["Masa Kerja"] == selected_masa_kerja]
    if selected_usia != "All":
        df_filtered = df_filtered[df_filtered["Usia"] == selected_usia]

    st.divider()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### 📌 Total Responden Berdasarkan Jabatan")
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

            # Menampilkan daftar nama responden sesuai filter dengan tampilan scroll
            st.write("📌 Daftar Nama Responden:")
            if not df_filtered.empty and "Isikan Nama Anda" in df_filtered.columns:
                names = df_filtered["Isikan Nama Anda"].dropna().tolist()

                # Gunakan markdown dengan bullet points agar lebih rapi
                st.markdown(
                    '<div style="max-height: 300px; width: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 9px; border-radius: 4px;">' +
                    "".join(f"<p>• {name}</p>" for name in names) +
                    '</div>',
                    unsafe_allow_html=True
                )
            
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
            st.subheader("📌 Employee Happiness")
            st.subheader("(Skala 1 s.d 4)")

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
            st.subheader("📌 Employee Engagement")

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
        
    st.divider()       
    # Judul
    st.write("### 📊 Uji Validitas Employee Happiness & Engagement")
    st.write("### (Standard Nilai ≥ 0.3 = Valid)")

if df is not None:
    df_filtered = df.copy()  # Salin data untuk menghindari modifikasi langsung
    
    if not df_filtered.empty:
        # Ambil kolom Employee Happiness & Employee Engagement
        happiness_columns = df.columns[6:22]  
        engagement_columns = df.columns[22:44]  

        # Pastikan hanya kolom numerik yang diproses
        df_filtered[happiness_columns] = df_filtered[happiness_columns].apply(pd.to_numeric, errors="coerce")
        df_filtered[engagement_columns] = df_filtered[engagement_columns].apply(pd.to_numeric, errors="coerce")

        # Hapus baris yang seluruhnya NaN setelah konversi
        df_filtered.dropna(subset=list(happiness_columns) + list(engagement_columns), how="all", inplace=True)

        # Cek jumlah baris setelah filtering
        if df_filtered.shape[0] < 2:
            st.warning("Data terlalu sedikit untuk menghitung korelasi!")
            st.stop()

        # Hitung skor total
        df_filtered["Total Happiness"] = df_filtered[happiness_columns].sum(axis=1, skipna=True)
        df_filtered["Total Engagement"] = df_filtered[engagement_columns].sum(axis=1, skipna=True)

        # Cek apakah Total Happiness & Engagement memiliki variasi nilai
        if df_filtered["Total Happiness"].nunique() < 2 or df_filtered["Total Engagement"].nunique() < 2:
            st.warning("Total Happiness atau Total Engagement memiliki nilai yang sama di semua baris. Korelasi tidak bisa dihitung!")
            st.stop()

        # Hitung korelasi
        happiness_validity = df_filtered[happiness_columns].corrwith(df_filtered["Total Happiness"])
        engagement_validity = df_filtered[engagement_columns].corrwith(df_filtered["Total Engagement"])

        # Konversi ke DataFrame
        happiness_validity_df = happiness_validity.to_frame(name="Korelasi dengan Total Happiness")
        engagement_validity_df = engagement_validity.to_frame(name="Korelasi dengan Total Engagement")

        # Cek apakah ada kolom dengan semua NaN dalam hasil korelasi
        if happiness_validity_df.isna().all().values[0] or engagement_validity_df.isna().all().values[0]:
            st.warning("Korelasi tidak dapat dihitung karena semua nilai NaN atau hanya memiliki satu nilai unik.")
            st.stop()

        # **Tampilkan DataFrame tanpa Styling**
        col1, col2 = st.columns([1, 1])

        with col1:
            st.write("### 🔍 Validitas Employee Happiness")
            st.dataframe(happiness_validity_df)

        with col2:
            st.write("### 🔍 Validitas Employee Engagement")
            st.dataframe(engagement_validity_df)

        # **Kesimpulan Uji Validitas**
        st.write("### 📌 Kesimpulan Uji Validitas")

        def interpret_validity(correlation_series, label):
            invalid_questions = correlation_series[correlation_series < 0.3].index.tolist()
            if invalid_questions:
                return f"❌ **Beberapa item dalam {label} tidak valid:**\n- " + "\n- ".join(invalid_questions)
            else:
                return f"✅ **Semua item dalam {label} valid.**"

        st.markdown(interpret_validity(happiness_validity, "Employee Happiness"))
        st.markdown(interpret_validity(engagement_validity, "Employee Engagement"))

    else:
        st.warning("Tidak ada data yang sesuai filter!")
        st.stop()

    st.divider()
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

    st.divider()
    st.write("### 🔥 Korelasi antara Employee Happiness & Employee Engagement")
    
if df is not None:
    if not df_filtered.empty:
        # Ambil kolom Employee Happiness & Employee Engagement
        happiness_columns = df.columns[6:22]  # Employee Happiness
        engagement_columns = df.columns[22:44]  # Employee Engagement

        # Hitung korelasi Spearman secara manual tanpa scipy
        rank_df = df_filtered.rank(method="average")  # Ranking untuk korelasi Spearman
        happiness_engagement_corr = rank_df.corr(method="pearson").loc[happiness_columns, engagement_columns]

         # **HEATMAP KORELASI**
        fig, ax = plt.subplots(figsize=(12, 8))

        # Tampilkan matriks korelasi sebagai heatmap
        cax = ax.matshow(happiness_engagement_corr, cmap="coolwarm", vmin=-1, vmax=1)
        fig.colorbar(cax)

        # Atur label sumbu
        ax.set_xticks(range(len(engagement_columns)))
        ax.set_yticks(range(len(happiness_columns)))
        ax.set_xticklabels(engagement_columns, rotation=75, fontsize=8, ha="right")
        ax.set_yticklabels(happiness_columns, fontsize=8)

        # Tambahkan nilai korelasi di dalam heatmap
        for (i, j), val in np.ndenumerate(happiness_engagement_corr.values):
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', color=color, fontsize=7)

        # Atur posisi label sumbu x agar di bawah heatmap
        ax.xaxis.set_ticks_position("bottom")
        ax.xaxis.set_label_position("bottom")

        ax.set_title("Heatmap Korelasi Employee Happiness & Employee Engagement", fontsize=12)

        st.pyplot(fig)  # **Tampilkan heatmap di Streamlit**

        # **MENCARI KORELASI POSITIF KUAT TANPA PENGULANGAN**
        correlation_pairs = happiness_engagement_corr.unstack().reset_index()

        # Tukar urutan kolom agar sesuai dengan matriks korelasi
        correlation_pairs.columns = ["Employee Engagement", "Employee Happiness", "Correlation"]

        # Urutkan dari korelasi tertinggi
        correlation_pairs = correlation_pairs.sort_values("Correlation", ascending=False).reset_index(drop=True)

        # Klasifikasi korelasi (hanya yang positif kuat)
        strong_positive_correlation = correlation_pairs[correlation_pairs["Correlation"] > 0.7]

        # Hilangkan duplikasi Employee Happiness, simpan hanya korelasi tertinggi per item
        unique_strong_positive = strong_positive_correlation.drop_duplicates(subset=["Employee Happiness"], keep="first")

        # Hitung jumlah unik Employee Happiness yang memiliki korelasi positif kuat
        unique_happiness_strong_positive = unique_strong_positive["Employee Happiness"].nunique()

        # Hitung ulang persentase hanya untuk korelasi positif kuat
        total_happiness_items = len(happiness_columns)
        strong_positive_percentage = (unique_happiness_strong_positive / total_happiness_items) * 100 if total_happiness_items > 0 else 0

        # **Menampilkan daftar korelasi positif kuat tanpa pengulangan**
        st.write("### 📌 Daftar Item dengan Korelasi Positif Kuat (Tanpa Pengulangan)")
        if not unique_strong_positive.empty:
            st.write(f"#### 🔴 Korelasi Positif Kuat (r > 0.7) - **{unique_happiness_strong_positive} item**")
            st.dataframe(unique_strong_positive[["Employee Happiness", "Employee Engagement", "Correlation"]])  
        else:
            st.write("ℹ️ **Tidak ada korelasi positif kuat antara Employee Happiness & Employee Engagement.**")

        # **Perhitungan ulang tampilan Latex**
        st.write("## 📊 Perhitungan")
        st.latex(r"""
        \text{Persentase Korelasi Positif Kuat} = \left(\frac{%d}{%d}\right) \times 100\%% = %.2f\%%
        """ % (unique_happiness_strong_positive, total_happiness_items, strong_positive_percentage))

        # **Kesimpulan hanya untuk korelasi positif kuat**
        st.write("## 📊 Kesimpulan")
        if strong_positive_percentage > 70:
            st.success("✅ **Karena %.2f%% dari item Employee Happiness memiliki korelasi positif kuat (lebih dari 70%%), maka Employee Happiness dapat direpresentasikan oleh Employee Engagement. 🚀**" % strong_positive_percentage)
        elif strong_positive_percentage > 50:
            st.warning("⚠️ **Sebagian item Employee Happiness dapat direpresentasikan oleh Employee Engagement, tetapi tidak semuanya.**")
        else:
            st.error("❌ **Employee Happiness tidak dapat sepenuhnya diwakili oleh Employee Engagement.**")

    else:
        st.warning("Tidak cukup data untuk menghitung korelasi.")

else:
    st.error("Gagal mengambil data. Cek kembali URL atau izin Google Sheets.")
