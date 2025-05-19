import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Datos base
center_lat = 7.11935
center_lon = -73.12274
area_bucaramanga_km2 = 165.0
km_to_deg = 0.009

energy_data = {
    "Solar Fotovoltaica ☀️": {"area": 8.58, "color": "orange"},
    "Eólica 🌬️": {"area": 21.55, "color": "green"},
    "Hidroeléctrica 💧": {"area": 15.03, "color": "blue"},
    "Carbón 🪨": {"area": 1.98, "color": "gray"},
    "Gas Natural 🔥": {"area": 1.5, "color": "red"},
    "Diésel 🛢️": {"area": 1.5, "color": "purple"},
    "Nuclear ☢️": {"area": 2.02, "color": "black"}
}

def crear_hexagono(lat, lon, area_km2):
    radio_km = math.sqrt((2 * area_km2) / (3 * math.sqrt(3)))
    radio_deg = radio_km * km_to_deg
    puntos = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        punto_lat = lat + radio_deg * math.cos(angle_rad)
        punto_lon = lon + radio_deg * math.sin(angle_rad)
        puntos.append([punto_lat, punto_lon])
    return puntos

st.title("🌎 Comparación de Fuentes de Energía en Bucaramanga")
st.markdown("Selecciona múltiples fuentes para visualizar su área proporcional sobre el mapa y su ranking comparativo:")

seleccionadas = []
cols = st.columns(3)
for i, fuente in enumerate(energy_data.keys()):
    if cols[i % 3].checkbox(fuente, value=False):
        seleccionadas.append(fuente)

tiles_esri = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
attr_esri = "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles=tiles_esri, attr=attr_esri)

ranking_data = []

for fuente in seleccionadas:
    datos = energy_data[fuente]
    coords = crear_hexagono(center_lat, center_lon, datos["area"])
    porcentaje = (datos["area"] / area_bucaramanga_km2) * 100
    folium.Polygon(
        locations=coords,
        color=datos["color"],
        fill=True,
        fill_color=datos["color"],
        fill_opacity=0.6,
        tooltip=f"{fuente} – {datos['area']:.2f} km² ({porcentaje:.2f}% de Bucaramanga)"
    ).add_to(m)
    ranking_data.append((fuente, datos["area"], datos["color"]))

# Mostrar mapa
st_folium(m, width=1100, height=650)

# Gráfico de barras de ranking
if ranking_data:
    ranking_data.sort(key=lambda x: x[1], reverse=True)
    fuentes = [x[0] for x in ranking_data]
    areas = [x[1] for x in ranking_data]
    colores = [x[2] for x in ranking_data]

    st.markdown("### 📊 Ranking por Área Requerida")
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(fuentes, areas, color=colores)
    ax.set_xlabel("Área requerida (km²)")
    ax.invert_yaxis()
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, f"{width:.2f}", va='center')
    st.pyplot(fig)
