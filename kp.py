import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.spatial import cKDTree
import math
import random
from geopy.distance import geodesic
from streamlit.components.v1 import html

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard ODP Telkom Witel Lampung",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #f1f1f1 !important;
    }

    .stApp {
        background: linear-gradient(135deg, #3e4c59, #606f7b) !important;
        padding: 1rem;
    }

    .block-container {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 0 12px rgba(0,0,0,0.2);
    }

    .main-header {
        background: linear-gradient(to right, #ff4d4d, #ff7f50);
        padding: 1.3rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        font-size: 2.4rem;
        letter-spacing: -1px;
        color: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    h2, h3, h4 {
        color: #f8f9fa !important;
        font-weight: 600 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 6px;
        margin-top: 1.5rem !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #343a40, #495057) !important;
        border-right: none !important;
        color: white !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }

    .metric-card, .status-card {
        background: rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.2);
        transition: transform 0.2s;
        color: white;
    }

    .metric-card:hover, .status-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }

    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
    }

    .metric-label {
        font-size: 1rem;
        color: #ced4da;
    }

    .status-green { border-left: 5px solid #28a745; }
    .status-yellow { border-left: 5px solid #ffc107; }
    .status-orange { border-left: 5px solid #fd7e14; }
    .status-red { border-left: 5px solid #dc3545; }
    .status-black { border-left: 5px solid #6c757d; }

    .stDataFrame {
        background-color: rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #f1f1f1 !important;
    }

    footer {
        background-color: #212529;
        color: white !important;
        padding: 1rem;
        font-size: 0.9rem;
        text-align: center;
        border-radius: 0 0 10px 10px;
        margin-top: 2rem;
    }

    footer a {
        color: #ffc107 !important;
    }

    input[type="checkbox"], input[type="radio"], select {
        filter: brightness(1.2);
    }
</style>
""", unsafe_allow_html=True)



# Header
st.markdown('<h1 class="main-header">📡 DASHBOARD MONITORING ODP TELKOM WITEL LAMPUNG</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Kontrol Dashboard")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Data ODP (CSV/Excel)",
        type=['csv', 'xlsx', 'xls'],
        help="Upload file CSV atau Excel dengan kolom: LATITUDE, LONGITUDE, OCC 2, Validasi Provinsi, Validasi Kabupaten Kota, Validasi Kecamatan, Validasi Kelurahan"
    )
    
    # Info sidebar
    st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
    st.markdown("### 📊 Status ODP")
    st.markdown("⚫ **Black**: Belum Teranalisis/Kapasitas Tidak Tersedia")
    st.markdown("🟢 **Green**: Kapasitas Aman")
    st.markdown("🟡 **Yellow**: Kapasitas Menengah")
    st.markdown("🟠 **Orange**: Hampir Penuh")
    st.markdown("🔴 **Red**: Penuh")
    st.markdown('</div>', unsafe_allow_html=True)


# Fungsi untuk membuat data dummy jika tidak ada upload
def create_dummy_data():
    np.random.seed(42)
    
    # Koordinat area Lampung (rough boundaries)
    lat_min, lat_max = -6.5, -3.5
    lon_min, lon_max = 103.5, 106.0
    
    # Kabupaten/Kota di Lampung
    kabupaten = [
        "Bandar Lampung", "Metro", "Lampung Selatan", "Lampung Tengah",
        "Lampung Utara", "Lampung Barat", "Lampung Timur", "Way Kanan",
        "Tulang Bawang", "Pesawaran", "Pringsewu", "Mesuji", "Tulang Bawang Barat",
        "Pesisir Barat", "Tanggamus"
    ]
    
    kecamatan = [
        "Tanjung Karang Pusat", "Kedaton", "Rajabasa", "Tanjung Senang",
        "Kemiling", "Langkapura", "Enggal", "Teluk Betung", "Panjang",
        "Sukabumi", "Sukarame", "Bumi Waras", "Metro Pusat", "Metro Utara"
    ]
    
    kelurahan = [
        "Gotong Royong", "Pahoman", "Rawa Laut", "Sukadana Ham",
        "Campang Raya", "Kupang Kota", "Teluk Betung", "Kota Karang",
        "Sumur Batu", "Labuhan Ratu", "Way Halim", "Kedamaian"
    ]
    
    n_points = 500
    data = []
    
    for i in range(n_points):
        lat = np.random.uniform(lat_min, lat_max)
        lon = np.random.uniform(lon_min, lon_max)
        
        # Distribusi status dengan probabilitas yang realistis
        status_prob = np.random.random()
        if status_prob < 0.3:
            status = 'green'
        elif status_prob < 0.6:
            status = 'yellow'
        elif status_prob < 0.8:
            status = 'orange'
        elif status_prob < 0.95:
            status = 'red'
        else:
            status = 'black'  # Belum teranalisis
        
        data.append({
            'LATITUDE': lat,
            'LONGITUDE': lon,
            'OCC 2': status,
            'Validasi Provinsi': 'Lampung',
            'Validasi Kabupaten Kota': np.random.choice(kabupaten),
            'Validasi Kecamatan': np.random.choice(kecamatan),
            'Validasi Kelurahan': np.random.choice(kelurahan)
        })
    
    return pd.DataFrame(data)

# Load data
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validasi Provinsi: hanya Lampung yang diproses
        if 'Validasi Provinsi' in df.columns:
            # Normalisasi nama provinsi
            df['Validasi Provinsi'] = df['Validasi Provinsi'].astype(str).str.strip().str.lower()
            
            # Filter hanya data Lampung
            df = df[df['Validasi Provinsi'] == 'lampung']
            
            if len(df) == 0:
                st.warning("⚠️ Tidak ada data dengan Validasi Provinsi = 'Lampung'. Menggunakan data dummy.")
                df = create_dummy_data()
            else:
                st.success(f"✅ Data berhasil dimuat: {len(df)} titik ODP (hanya Provinsi Lampung)")
        else:
            st.warning("⚠️ Kolom 'Validasi Provinsi' tidak ditemukan. Menggunakan data dummy.")
            df = create_dummy_data()
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        df = create_dummy_data()
        st.info("🔄 Menggunakan data dummy untuk demo")
else:
    df = create_dummy_data()
    st.info("📝 Menggunakan data dummy untuk demo. Upload file CSV/Excel untuk data real.")

# Validasi kolom
required_columns = ['LATITUDE', 'LONGITUDE', 'OCC 2', 'Validasi Provinsi', 
                   'Validasi Kabupaten Kota', 'Validasi Kecamatan', 'Validasi Kelurahan']

if not all(col in df.columns for col in required_columns):
    st.error("❌ File tidak memiliki kolom yang diperlukan!")
    st.stop()

# Cleaning data
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
# Handle missing status by filling with 'black'
if 'OCC 2' in df.columns:
    df['OCC 2'] = df['OCC 2'].fillna('black').str.lower().str.strip()
else:
    df['OCC 2'] = 'black'

# Clean data administratif - hilangkan NaN dan konversi ke string
administrative_cols = ['Validasi Provinsi', 'Validasi Kabupaten Kota', 'Validasi Kecamatan', 'Validasi Kelurahan']
for col in administrative_cols:
    if col in df.columns:
        # Ganti NaN dengan string kosong, lalu strip whitespace
        df[col] = df[col].fillna('').astype(str).str.strip()
        # Hapus baris dengan nilai kosong
        df = df[df[col] != '']

# Filter di sidebar
with st.sidebar:
    st.markdown("### 🔍 Filter Data")
    
    # Filter Kabupaten
    try:
        kabupaten_unique = df['Validasi Kabupaten Kota'].unique()
        # Filter hanya nilai yang valid (bukan string kosong)
        kabupaten_clean = [x for x in kabupaten_unique if x and str(x).strip()]
        kabupaten_list = ['Semua'] + sorted(kabupaten_clean)
    except Exception as e:
        st.error(f"Error processing kabupaten data: {str(e)}")
        kabupaten_list = ['Semua']
    selected_kabupaten = st.selectbox("Pilih Kabupaten/Kota:", kabupaten_list)
    
    # Filter berdasarkan kabupaten
    if selected_kabupaten != 'Semua':
        df_filtered = df[df['Validasi Kabupaten Kota'] == selected_kabupaten]
        
        # Filter Kecamatan
        try:
            kecamatan_unique = df_filtered['Validasi Kecamatan'].unique()
            kecamatan_clean = [x for x in kecamatan_unique if x and str(x).strip()]
            kecamatan_list = ['Semua'] + sorted(kecamatan_clean)
        except Exception as e:
            st.error(f"Error processing kecamatan data: {str(e)}")
            kecamatan_list = ['Semua']
            
        selected_kecamatan = st.selectbox("Pilih Kecamatan:", kecamatan_list)
        
        if selected_kecamatan != 'Semua':
            df_filtered = df_filtered[df_filtered['Validasi Kecamatan'] == selected_kecamatan]
    else:
        df_filtered = df.copy()
        selected_kecamatan = 'Semua'
    
    # Filter Status
    try:
        status_unique = df['OCC 2'].unique()
        status_clean = [x for x in status_unique if x and str(x).strip()]
        status_list = ['Semua'] + sorted(status_clean)
    except Exception as e:
        st.error(f"Error processing status data: {str(e)}")
        status_list = ['Semua']
        
    selected_status = st.multiselect("Pilih Status ODP:", status_list, default=['Semua'])
    
    if 'Semua' not in selected_status and selected_status:
        df_filtered = df_filtered[df_filtered['OCC 2'].isin(selected_status)]

# Metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_odp = len(df_filtered)
status_counts = df_filtered['OCC 2'].value_counts()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{total_odp}</p>
        <p class="metric-label">Total ODP</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    green_count = status_counts.get('green', 0)
    st.markdown(f"""
    <div class="status-card status-green">
        <p class="metric-value">{green_count}</p>
        <p class="metric-label">Green</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    yellow_count = status_counts.get('yellow', 0)
    st.markdown(f"""
    <div class="status-card status-yellow">
        <p class="metric-value">{yellow_count}</p>
        <p class="metric-label">Yellow</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    orange_count = status_counts.get('orange', 0)
    st.markdown(f"""
    <div class="status-card status-orange">
        <p class="metric-value">{orange_count}</p>
        <p class="metric-label">Orange</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    red_count = status_counts.get('red', 0)
    st.markdown(f"""
    <div class="status-card status-red">
        <p class="metric-value">{red_count}</p>
        <p class="metric-label">Red</p>
    </div>
    """, unsafe_allow_html=True)

with col6:
    black_count = status_counts.get('black', 0)
    st.markdown(f"""
    <div class="status-card status-black">
        <p class="metric-value">{black_count}</p>
        <p class="metric-label">Black</p>
    </div>
    """, unsafe_allow_html=True)


# Main content - Modified layout
st.markdown("### 🗺️ PETA SEBARAN ODP")
# Peta dengan Plotly - full width
    # Peta dengan Plotly
color_map = {
        'green': '#4CAF50',
        'yellow': '#FFFF00', 
        'orange': '#FF9800',
        'red': '#f44336',
        'black': '#333333'  # Warna untuk status black
    }
fig_map = px.scatter_mapbox(
    df_filtered,
    lat="LATITUDE",
    lon="LONGITUDE",
    color="OCC 2",
    color_discrete_map=color_map,
    hover_data={
        'Validasi Kabupaten Kota': True,
        'Validasi Kecamatan': True,
        'Validasi Kelurahan': True,
        'LATITUDE': ':.4f',
        'LONGITUDE': ':.4f',
        'OCC 2': True
    },
    zoom=8,
    height=600,
    title=""
)
fig_map.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)
st.plotly_chart(fig_map, use_container_width=True)

# Three visualization cards in one row
st.markdown("### 📊 ANALISIS DISTRIBUSI ODP")
col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        st.markdown("#### 📈 DISTRIBUSI STATUS")
        # Pie chart
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_map=color_map,
            title=""
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 STATUS PER KABUPATEN")
        try:
            kabupaten_status = df_filtered.groupby(['Validasi Kabupaten Kota', 'OCC 2']).size().unstack(fill_value=0)
            statuses = ['green', 'yellow', 'orange', 'red', 'black']
            for status in statuses:
                if status not in kabupaten_status.columns:
                    kabupaten_status[status] = 0
            
            fig_bar = px.bar(
                kabupaten_status.reset_index(),
                x='Validasi Kabupaten Kota',
                y=statuses,
                color_discrete_map=color_map,
                title=""
            )
            fig_bar.update_layout(
                height=300,
                xaxis_tickangle=-45,
                legend_title="Status ODP",
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating bar chart: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        st.markdown("#### 📉 STATUS PER KECAMATAN")
        try:
            kecamatan_status = df_filtered.groupby(['Validasi Kecamatan', 'OCC 2']).size().unstack(fill_value=0).head(10)
            statuses = ['green', 'yellow', 'orange', 'red', 'black']
            for status in statuses:
                if status not in kecamatan_status.columns:
                    kecamatan_status[status] = 0
            
            fig_bar = px.bar(
                kecamatan_status.reset_index(),
                x='Validasi Kecamatan',
                y=statuses,
                color_discrete_map=color_map,
                title=""
            )
            fig_bar.update_layout(
                height=300,
                xaxis_tickangle=-45,
                legend_title="Status ODP",
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating kecamatan chart: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

# Tabel detail - MODIFIKASI
st.markdown("### 📋 Detail Data ODP")
# Filter jumlah data yang ditampilkan
show_count = st.number_input("Jumlah data yang ditampilkan:", min_value=10, max_value=1000, value=100)

# Apply filter untuk tabel
df_table = df_filtered.copy()
df_display = df_table.head(show_count)

# Mapping status to icons
status_icon_map = {
    'green': '🟢',
    'yellow': '🟡',
    'orange': '🟠',
    'red': '🔴',
    'black': '⚫'
}

# Apply icon mapping
df_display['Status'] = df_display['OCC 2'].map(status_icon_map)

# Style tabel dengan border bawah
def style_table(row):
    styles = ['border-bottom: 1px solid #e0e0e0' for _ in row]
    return styles

# Tampilkan tabel dengan styling
st.dataframe(
    df_display[['Status', 'LATITUDE', 'LONGITUDE', 
               'Validasi Kabupaten Kota', 'Validasi Kecamatan', 'Validasi Kelurahan']]
    .style.apply(style_table, axis=1),
    use_container_width=True,
    height=400
)




# Summary statistik - MODIFIKASI
st.markdown("### 📈 Ringkasan Statistik")
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Top 5 Kecamatan Terbanyak ODP")
    try:
        kecamatan_counts = df_filtered['Validasi Kecamatan'].value_counts()
        top_kecamatan = kecamatan_counts.head(5)
        
        if not top_kecamatan.empty:
            st.dataframe(
                pd.DataFrame({
                    'Kecamatan': top_kecamatan.index,
                    'Jumlah ODP': top_kecamatan.values
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Tidak ada data kecamatan untuk ditampilkan")
            
        st.markdown("#### 5 Kecamatan Terendah ODP")
        bottom_kecamatan = kecamatan_counts.sort_values(ascending=True).head(5)
        if not bottom_kecamatan.empty:
            st.dataframe(
                pd.DataFrame({
                    'Kecamatan': bottom_kecamatan.index,
                    'Jumlah ODP': bottom_kecamatan.values
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Tidak ada data kecamatan untuk ditampilkan")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
with col2:
    st.markdown("#### Top 5 Kabupaten Terbanyak ODP")
    try:
        kabupaten_counts = df_filtered['Validasi Kabupaten Kota'].value_counts()
        top_kabupaten = kabupaten_counts.head(5)       
        if not top_kabupaten.empty:
            st.dataframe(
                pd.DataFrame({
                    'Kabupaten/Kota': top_kabupaten.index,
                    'Jumlah ODP': top_kabupaten.values
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Tidak ada data kabupaten untuk ditampilkan")           
        st.markdown("#### 5 Kabupaten Terendah ODP")
        bottom_kabupaten = kabupaten_counts.sort_values(ascending=True).head(5)
        if not bottom_kabupaten.empty:
            st.dataframe(
                pd.DataFrame({
                    'Kabupaten/Kota': bottom_kabupaten.index,
                    'Jumlah ODP': bottom_kabupaten.values
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Tidak ada data kabupaten untuk ditampilkan")          
    except Exception as e:
        st.error(f"Error: {str(e)}")