import streamlit as st
import pandas as pd


# Dibuat per halaman dengan pertanyaan acak
def main():
    logo_url = "https://www.agungtoyota.co.id/app/sam/assets/addons/sam/sam/samcgi-theme/resources/img/favicons/apple-touch-icon.png?v=1740058172"
    st.set_page_config(page_title="Employee Engagement Survey", page_icon=logo_url, layout="wide")
    logo_url2 = "https://www.agungtoyota.co.id/app/sam/assets/logo/logo-baru-1.png"
    logo_url1 = "https://agungconcern.co.id/wp-content/uploads/2024/08/Logo-Agung-Concern-2024.svg"
# Tambahkan CSS untuk tampilan yang lebih rapi
    st.markdown(
    f"""
    <style>
        .header-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 50px;
            background-color: rgba(240, 240, 255, 0.6);
            border-radius: 10px;
        }}
        .header-logo {{
            width: 150px;
        }}
        h1 {{ font-size: 40px !important; text-align: center; color: black !important; }}
        h2 {{ font-size: 34px !important; text-align: center; color: black !important; }}
        p, label {{ font-size: 20px !important; color: black !important; }}
        .stButton button {{ width: 100%; font-size: 22px !important; padding: 10px; background: rgba(162, 155, 254, 0.8); color: white; border-radius: 10px; border: none; }}
        .stProgress > div > div > div {{ background-color: rgba(162, 155, 254, 0.8); }}
        .stRadio > label {{ font-size: 20px !important; color: black !important; }}

         /* Styling untuk tombol agar terlihat soft 3D */
        .stButton button {{
            width: 100%;
            font-size: 20px !important;
            padding: 12px;
            background: linear-gradient(to bottom, #d8bfff, #a0c4ff); /* Soft gradient (lavender ke sky blue) */
            color: black;
            border-radius: 12px;
            border: 2px solid #cdb4db;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.15); /* Bayangan lebih lembut */
            transition: all 0.2s ease-in-out;
        }}
        .stButton button:hover {{
            background: linear-gradient(to bottom, #a0c4ff, #d8bfff);
            box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
        }}
        .stButton button:active {{
            box-shadow: 1px 1px 4px rgba(0, 0, 0, 0.1);
            transform: translateY(2px);
        }}



        /* Footer */
        .footer-container {{
            position: fixed;
            bottom: 0;
            width: 90%;
            background-color: rgba(240, 240, 255, 0.6);
            text-align: right;
            padding: 10px;
            font-size: 14px;
            border-radius: 10px;
        }}
    </style>
    <div class="header-container">
        <img src="{logo_url1}" class="header-logo">
        <h1>Employee Engagement Survey</h1>
        <img src="{logo_url2}" class="header-logo">
    </div>

    <div class="footer-container">
        <p>© 2025 Agung Toyota - All Rights Reserved | Employee Engagement Survey</p>
    </div>
    """,
    unsafe_allow_html=True
)
    
    #st.title("📋 Employee Engagement Survey")
    
    if "page" not in st.session_state:
        st.session_state.page = 0

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    categories = {
        "Pendahuluan": "",
        "1": "",
        "2": "",
        "3": "",
        "4": "",
        "Pertanyaan Terbuka": "📈",
        "Selesai": "✅"
    }

    likert_scale = ["1 - Sangat Tidak Setuju", "2 - Tidak Setuju", "3 - Setuju", "4 - Sangat Setuju"]
    
    questions = {
        "1": [
            "Perusahaan memberikan fasilitas dan alat kerja yang saya butuhkan untuk mendukung kelancaran penyelesaian tugas",
            "Atasan melakukan pembagian beban kerja sesuai dengan kapasitas dan kapabilitas yang saya miliki",
            "Rekan kerja di lingkungan kerja saya berdedikasi untuk menghasilkan pekerjaan yang berkualitas",
            "Lingkungan di tempat kerja saya mendorong untuk pengembangan diri saya"
        ],
        "2": [
            "Atasan saya mendorong saya untuk ikut berpartisipasi memberikan ide yang baik, dan menerapkannya di pekerjaan",
            "Saya memiliki teman baik di tempat kerja",
            "Saya menerima penghasilan yang sesuai dengan apa yang saya kerjakan",
            "Saya memiliki kesempatan untuk dapat melakukan yang terbaik dalam pekerjaan saya setiap hari",
        ],
        "3": [
            "Atasan dan lingkungan sekitar saya di tempat kerja peduli terhadap saya",
            "Jam kerja di perusahaan (Termasuk cuti & izin tidak masuk kerja) memenuhi kebutuhan bisnis & kebutuhan pribadi karyawan",
            "Saya mendapatkan kesempatan untuk menyampaikan pendapat di tempat kerja",
            "Atasan saya dan lingkungan kerja saya memastikan progress pekerjaan saya dalam 6 bulan terakhir"
            
        ],
        "4": [
            "Atasan saya menghargai saya di tempat kerja",
            "Perusahaan memberikan kesempatan saya untuk dapat belajar dan berkembang",
            "Saya mendapatkan pelatihan yang sesuai untuk kelancaran pekerjaan dalam setahun terakhir",
            "Saya memiliki kesempatan berdiskusi dengan atasan mengenai jenjang karir dan program pengembangan diri saya"            
        ]
       
    }
    
    total_pages = len(categories)
    st.progress(int(st.session_state.page) / (total_pages - 1))
    #page = int(st.session_state.page) if "page" in st.session_state and st.session_state.page.isdigit() else 0
    #st.progress(page / (total_pages - 1))
    
    category = list(categories.keys())[st.session_state.page]
    
    if category == "Pendahuluan":
        st.subheader(f"{categories[category]} Selamat Datang di Employee Engagement Survey")
        st.write("""
            Survei ini dilakukan untuk mengumpulkan opini atau pendapat karyawan di lingkungan Agung Concern Group mengenai pengelolaan SDM dan Organisasi.

            **Sebagai informasi, survei ini:**
            - Bersifat rahasia, positif, dan membangun ✅
            - Tidak ada jawaban benar/salah dan tidak mempengaruhi evaluasi kinerja 📊
            - Seluruh kuesioner harus diisi dan dilengkapi ✍️
            - Seluruh hasil pengisian survei akan langsung diterima, disimpan, dan diolah oleh tim HC Agung Toyota 📂
            - Setelah mengisi survei, dimohon untuk mengisi Form Absensi melalui link yang tersedia di pemberitahuan survei. 📑
            
            **Selamat mengisi survei,**
            
            **Tim HRD Agung Toyota**
        """)

        if st.button("🚀 Mulai"):
            st.session_state.page += 1
            st.rerun()


     #elif category == "Pertanyaan Terbuka":
        #st.subheader(f"{categories[category]}")
        #feedback = st.text_area("**Apa harapan anda terhadap perusahaan agar anda bisa lebih merasa bahagia:**", value=st.session_state.get("feedback", ""))
            
  
    #elif category == "Selesai":
        #st.subheader(f"{categories[category]} Terima kasih telah mengisi survei!")
       # feedback = st.text_area("💡 Masukan atau saran untuk kami:", value=st.session_state.get("feedback", ""))


    elif category == "Pertanyaan Terbuka":    
        if "submitted" not in st.session_state:
            st.session_state.submitted = False  # Tambahkan state untuk tracking pengiriman jawaban

        if "responses" not in st.session_state:
            st.session_state.responses = {}  # Inisialisasi jika belum ada

        if st.session_state.submitted:
            st.title("✅ Terima Kasih!")
            st.write("""
                Terima kasih telah mengisi survei ini.  
                Jawaban Anda telah berhasil disimpan.  
                Kami sangat menghargai partisipasi Anda!  
            """)

            if st.button("🏠 Kembali ke Halaman Awal"):
                st.session_state.page = 0
                st.session_state.responses = {} 
                st.session_state.submitted = False  # Kembali ke survei
                st.rerun()

        else:
            feedback = st.text_area("**Apa harapan Anda terhadap perusahaan agar Anda bisa lebih merasa bahagia?**", value="")

            if st.button("📩 Kirim Jawaban"):
                if feedback.strip():  # Cek apakah feedback tidak kosong atau hanya spasi
                    st.session_state.responses["Harapan Untuk Lebih Bahagia"] = feedback
                    df = pd.DataFrame([st.session_state.responses])

                    # Simpan ke file CSV
                    #df.to_csv("survey_results.csv", index=False)

                    st.session_state.submitted = True  # Ubah state ke submitted
                    st.rerun()
                else:
                    st.warning("Silakan mengisikan pertanyaan di atas sebelum mengirimkan jawaban.")

        #if st.button("📥 Download Hasil Survei"):
            #try:
                #df = pd.read_csv("survey_results.csv")
                #st.download_button(label="📊 Unduh sebagai Excel",
                                   #data=save_to_excel(df),
                                   #file_name="survey_results.xlsx",
                                   #mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            #except FileNotFoundError:
                #st.error("Belum ada data survei yang tersimpan.")
    
    else:
        st.subheader(f"{categories[category]} Halaman: {category}")
        all_answered = True
        for question in questions.get(category, []):
            default_value = st.session_state.responses.get(question, None)
            response = st.radio(question, options=likert_scale, index=likert_scale.index(default_value) if default_value in likert_scale else None)
    
            if response is None:
                all_answered = False
    
            st.session_state.responses[question] = response
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.session_state.page > 0:
                if st.button("⬅️ Kembali"):
                    st.session_state.page -= 1
                    st.rerun()
        
        with col2:
            if all_answered:
                if st.button("➡️ **Lanjut**"):
                    st.session_state.page += 1
                    st.rerun()

if __name__ == "__main__":
    main()