import streamlit as st
import mysql.connector
import pandas as pd
from fpdf import FPDF

# ==========================
# 🔗 Koneksi Database
# ==========================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="office_finance"
    )

# ==========================
# 📊 Laporan Otomatis
# ==========================
def laporan_neraca_saldo():
    st.header("📊 Neraca Saldo Bulanan")
    try:
        db = get_db()
        query = """
            SELECT DATE_FORMAT(tanggal, '%Y-%m') AS bulan,
                   SUM(CASE WHEN tipe='pemasukan' THEN jumlah ELSE 0 END) AS total_pemasukan,
                   SUM(CASE WHEN tipe='pengeluaran' THEN jumlah ELSE 0 END) AS total_pengeluaran,
                   SUM(CASE WHEN tipe='pemasukan' THEN jumlah ELSE 0 END) -
                   SUM(CASE WHEN tipe='pengeluaran' THEN jumlah ELSE 0 END) AS saldo_bulan
            FROM Transaksi
            GROUP BY DATE_FORMAT(tanggal, '%Y-%m')
            ORDER BY bulan;
        """
        df = pd.read_sql(query, db)
        st.dataframe(df)

        if st.button("Unduh Excel Neraca"):
            df.to_excel("neraca_saldo.xlsx", index=False)
            st.success("File neraca_saldo.xlsx berhasil dibuat!")

        if st.button("Unduh PDF Neraca"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, "Neraca Saldo Bulanan", ln=True, align='C')
            for _, row in df.iterrows():
                pdf.cell(200, 10, f"{row['bulan']} | Pemasukan: {row['total_pemasukan']} | Pengeluaran: {row['total_pengeluaran']} | Saldo: {row['saldo_bulan']}", ln=True)
            pdf.output("neraca_saldo.pdf")
            st.success("File neraca_saldo.pdf berhasil dibuat!")
    except mysql.connector.Error as e:
        st.error(f"Gagal koneksi ke database: {e}")
    except Exception as e:
        st.error(f"Terjadi error: {e}")

def laporan_rekap_absensi():
    st.header("👥 Rekap Absensi per Karyawan")
    try:
        db = get_db()
        query = """
            SELECT u.nama AS nama_karyawan,
                   DATE_FORMAT(a.tanggal, '%Y-%m') AS bulan,
                   COUNT(*) AS total_hadir
            FROM Absensi a
            JOIN User u ON a.user_id = u.user_id
            WHERE a.status = 'hadir'
            GROUP BY u.nama, DATE_FORMAT(a.tanggal, '%Y-%m')
            ORDER BY bulan, nama_karyawan;
        """
        df = pd.read_sql(query, db)
        st.dataframe(df)

        if st.button("Unduh Excel Absensi"):
            df.to_excel("rekap_absensi.xlsx", index=False)
            st.success("File rekap_absensi.xlsx berhasil dibuat!")
    except Exception as e:
        st.error(f"Terjadi error: {e}")

def laporan_kasbon():
    st.header("💵 Daftar Kasbon Aktif")
    try:
        db = get_db()
        query = """
            SELECT u.nama AS nama_karyawan,
                   k.tanggal,
                   k.jumlah,
                   k.status
            FROM Kasbon k
            JOIN User u ON k.user_id = u.user_id
            WHERE k.status = 'aktif'
            ORDER BY k.tanggal DESC;
        """
        df = pd.read_sql(query, db)
        st.dataframe(df)

        if st.button("Unduh Excel Kasbon"):
            df.to_excel("kasbon_aktif.xlsx", index=False)
            st.success("File kasbon_aktif.xlsx berhasil dibuat!")
    except Exception as e:
        st.error(f"Terjadi error: {e}")

# ==========================
# 🚀 Main App
# ==========================
st.set_page_config(page_title="Office Finance Reports", layout="wide")

menu = st.sidebar.selectbox("Menu Laporan", ["Neraca Saldo Bulanan", "Rekap Absensi", "Kasbon Aktif"])

if menu == "Neraca Saldo Bulanan":
    laporan_neraca_saldo()
elif menu == "Rekap Absensi":
    laporan_rekap_absensi()
elif menu == "Kasbon Aktif":
    laporan_kasbon()
