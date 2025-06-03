# TODO Separate bounding box for STL from bounding box for map (completely separate)

import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

from libs.Overture2STL import (
    bbox_string,
    bbox_size_meters,
    map_types_default,
    map_types_all,
    overture_to_stl,
)

# Must be called first
st.set_page_config(page_title="Overture to STL", page_icon="🗺", layout="centered", initial_sidebar_state="collapsed")

st.title("🗺 Overture to STL Generator")

# Styling got fixing height issue with Folium
custom_css = """
<style>
.map-container {
    height: 500px !important;
    width: 100%;
    overflow: hidden;
}
.map-container > * {
    height: 100% !important;
}
iframe {
    height: 500px !important;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Bounding Box
st.header("Bounding Box")

st.write(
    "Draw a rectangle on the map to select the area. You can zoom and pan as needed. Only one rectangle is allowed at a time."
)

# Initialize session state for bbox
if "bbox" not in st.session_state:
    bbox = [13.133869, 55.675416, 13.267422, 55.744661]  # Lund, Sweden
    st.session_state["bbox"] = bbox
else:
    bbox = st.session_state["bbox"]

# Center map on current bbox
center_lat = (bbox[1] + bbox[3]) / 2
center_lon = (bbox[0] + bbox[2]) / 2

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=14,
    tiles="OpenStreetMap",
    width="100%",
    height=500,
)

Draw(
    export=False,
    draw_options={
        "polyline": False,
        "polygon": False,
        "circle": False,
        "marker": False,
        "circlemarker": False,
        "rectangle": True,
    },
    edit_options={"edit": True, "remove": True},
).add_to(m)

map_data = st_folium(m, height=500, width="100%")

#st.write(map_data)

# If a rectangle was drawn, use that as a bounding box
if map_data and map_data.get("last_active_drawing"):
    coords = map_data["last_active_drawing"]["geometry"]["coordinates"][0]
    lons = [pt[0] for pt in coords]
    lats = [pt[1] for pt in coords]
    bbox = [min(lons), min(lats), max(lons), max(lats)]
    st.session_state["bbox"] = bbox

bbox_csv = bbox_string(bbox)
width_m, height_m = bbox_size_meters(bbox)
st.info(
    f"Bounding box: {bbox_csv}  \n"
    f"The dimensions of the area are roughly {round(width_m, 0)} m wide and {round(height_m, 0)} m high. Take this into account when editing object dimensions and scaling."
)

# Map Types
st.header("Map Types")
selected_types = []
cols = st.columns(3)
for i, t in enumerate(map_types_all):
    checked = t in map_types_default
    with cols[i % 3]:
        if st.checkbox(t, value=checked, key=f"maptype_{t}"):
            selected_types.append(t)

# Height Mode
st.header("Height Mode")
height_mode = st.selectbox(
    "Mode for use of the height settings below:",
    [
        ("f", "Fixed"),
        ("l", "Lowest allowed, otherwise explicit"),
        ("h", "Highest allowed, otherwise explicit"),
        ("e", "Explicit"),
    ],
    format_func=lambda x: x[1],
    index=3,
)
polygon_height_mode = height_mode[0]

# --- Numerical Parameters ---
st.header("Model Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    polygon_height = st.number_input(
        "Default/limit height for buildings (m)",
        min_value=0.0,
        value=3.0,
        step=0.1,
    )
    polygon_height_flat = st.number_input(
        "Default/limit height for flat areas (m)",
        min_value=0.0,
        value=1.0,
        step=0.1,
    )
    line_width = st.number_input(
        "Default/limit width for lines (m)",
        min_value=0.0,
        value=3.0,
        step=0.1,
    )
with col2:
    line_height = st.number_input(
        "Default/limit height for lines (m)",
        min_value=0.0,
        value=2.0,
        step=0.1,
    )
    point_width = st.number_input(
        "Default width for points (m)",
        min_value=0.0,
        value=4.0,
        step=0.1,
    )
    point_height = st.number_input(
        "Default height for points (m)",
        min_value=0.0,
        value=4.0,
        step=0.1,
    )
with col3:
    scale_percent = st.number_input(
        "Scaling factor (%)",
        min_value=0.1,
        value=100.0,
        step=1.0,
    )
    base_height = st.number_input(
        "Base height (mm)",
        min_value=0.0,
        value=2.0,
        step=0.1,
    )
    base_margin = st.number_input(
        "Base margin (mm)",
        min_value=0.0,
        value=5.0,
        step=0.1,
    )

# --- Output File ---
st.header("Output")
outputfile = st.text_input(
    "File name for generated files (without extension)", value=""
)

if "perform" in st.session_state and st.session_state["perform"]:   
    with st.spinner("Generating STL...", show_time=True):
        try:
            overture_to_stl(
                bbox,
                selected_types,
                polygon_height_mode,
                polygon_height,
                polygon_height_flat,
                line_width,
                line_height,
                point_width,
                point_height,
                scale_percent,
                base_margin,
                base_height,
                outputfile,
            )

            st.success(f"'{outputfile}.stl' was generated successfully.")
            st.info("Check your working directory for the file.")
        except Exception as e:
            st.error(f"Something went wrong when generating the STL file: {e}")

        st.session_state["perform"] = False 

# --- Generate STL Button ---
if st.button("Generate STL"):
    if not outputfile.strip():
        st.error("Please enter a file name for the output.")
    elif not bbox or len(bbox) != 4:
        st.error("Please select a bounding box on the map.")
    elif not selected_types:
        st.error("Please select at least one map type.")
    else:
        st.session_state["perform"] = True     

st.caption("Powered by Overture2STL by Abiro 2025, licensed under the MIT License.")
