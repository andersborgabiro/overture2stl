# Tasks:
# TODO Dotted and dashed lines for certain LineString.
# TODO What to do with Point? Without a description there's not much point showing them.

# Documentation:
# https://github.com/OvertureMaps/overturemaps-py/tree/main/overturemaps
# https://github.com/OvertureMaps/schema
# https://github.com/OvertureMaps/schema/tree/dev/schema/buildings

import geojson
from shapely.geometry import shape, box, Polygon
from shapely.ops import unary_union, transform
from shapely.validation import explain_validity
from pyproj import Transformer
from pyproj import CRS
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon
from stl import mesh
import csv
import os

transformer = None

default_types = [
    "building", 
    "building_part", 
    "infrastructure", 
    "segment", 
    "water"
]

# Widths of roads in meters
# https://github.com/OvertureMaps/schema/blob/dev/schema/transportation/segment.yaml
road_widths = {
    "motorway": 20.0,
    "primary": 12.0,
    "secondary": 8.0,
    "tertiary": 6.0,
    "residential": 4.0,
    "living_street": 4.0,
    "trunk": 2.0,
    "unclassified": 2.0,
    "service": 2.0,
    "pedestrian": 2.0,
    "footway": 2.0,
    "steps": 2.0,
    "path": 2.0,
    "track": 2.0,
    "cycleway": 2.0,
    "bridleway": 2.0,
    "unknown": 2.0
}

# Polygons to be considered flat areas
polygon_flat = [
    # Infrastructure
    # https://github.com/OvertureMaps/schema/blob/dev/schema/base/infrastructure.yaml
    "barrier",
    "pier",
    "transit",

    # Water
    # https://github.com/OvertureMaps/schema/blob/dev/schema/base/water.yaml
    "canal",
    "human_made",
    "lake",
    "ocean",
    "physical",
    "pond",
    "reservoir",
    "river",
    "spring",
    "stream",
    "wastewater",
    "water"
]

# Points that are relevant to include
point_relevant = [
    "transit/bus_stop",
    #"barrier/bollard",
    #"barrier/gate"
]

# Project geographic geometry to projected coordinate system.
def project_geom(geom):
    global transformer

    return transform(transformer.transform, geom)

# Convert a Polygon to a 3D mesh with height.
def polygon_to_extruded_mesh(polygon, height):
    projected_poly = project_geom(polygon)
    # Use trimesh's robust extrusion
    mesh_obj = trimesh.creation.extrude_polygon(projected_poly, height)
    if (mesh_obj):
        return mesh_obj.vertices, mesh_obj.faces
    else:
        return None, None

# Convert a LineString into a 3D extruded corridor mesh of width and height in meters.
def line_to_extruded_mesh(line, width, height):
    projected_line = project_geom(line)
    corridor_poly = projected_line.buffer(width / 2.0, cap_style=2, join_style=2)

    # Check for validity
    if corridor_poly.is_empty:
        print("Warning: Buffer produced an empty polygon for line:", list(line.coords))
        return None, None

    if not corridor_poly.is_valid:
        print("Warning: Buffer polygon invalid:", explain_validity(corridor_poly))
        # Try to fix with buffer(0)
        corridor_poly = corridor_poly.buffer(0)
        if corridor_poly.is_empty or not corridor_poly.is_valid:
            print("Failed to fix invalid buffer polygon.")
            return None, None

    # Extrude using trimesh
    try:
        mesh_obj = trimesh.creation.extrude_polygon(corridor_poly, height)
        if mesh_obj.vertices.shape[0] == 0 or mesh_obj.faces.shape[0] == 0:
            print("Extrusion resulted in empty mesh.")
            return None, None
        return mesh_obj.vertices, mesh_obj.faces
    except Exception as e:
        print("Extrusion failed:", e)
        return None, None

def point_to_cylinder_mesh(point, width, height, sections=24):
    projected_point = project_geom(point)
    x, y = projected_point.x, projected_point.y
    transform=trimesh.transformations.translation_matrix([x, y, height / 2.0])
    mesh_obj = trimesh.creation.cylinder(radius=width / 2.0, height=height, sections=sections, transform=transform)
    if mesh_obj:
        return mesh_obj.vertices, mesh_obj.faces
    else:
        return None, None  

def get_utm_epsg_code(minx, miny, maxx, maxy):
    avg_lon = (minx + maxx) / 2.0
    avg_lat = (miny + maxy) / 2.0
    zone_number = int((avg_lon + 180.0) / 6.0) + 1
    if avg_lat >= 0:
        epsg_code = 32600 + zone_number # Northern hemisphere
    else:
        epsg_code = 32700 + zone_number # Southern hemisphere
    return epsg_code

# Return the longitude of the central meridian for a given UTM EPSG code.
def get_utm_central_meridian(epsg_code):
    if 32601 <= epsg_code <= 32660:
        zone = epsg_code - 32600
    elif 32701 <= epsg_code <= 32760:
        zone = epsg_code - 32700
    else:
        raise ValueError("EPSG code is not a valid UTM zone.")
    return -183 + 6 * zone # degrees

# Helper to get grid convergence angle at a point
def get_convergence_angle(lon, lat, epsg_code):
    # Returns the grid convergence angle (in degrees) at (lon, lat) for the given UTM EPSG code.
    lon0 = get_utm_central_meridian(epsg_code)
    # Convert degrees to radians
    lon_rad = np.deg2rad(lon)
    lat_rad = np.deg2rad(lat)
    lon0_rad = np.deg2rad(lon0)
    # Compute convergence angle in radians
    gamma = np.arctan(np.tan(lon_rad - lon0_rad) * np.sin(lat_rad))
    return np.rad2deg(gamma)

# Helper to rotate vertices around Z axis
def rotate_vertices(vertices, angle_deg):
    angle_rad = np.deg2rad(angle_deg)
    R = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad), 0],
        [np.sin(angle_rad),  np.cos(angle_rad), 0],
        [0, 0, 1]
    ])
    return vertices @ R.T

# Download Overture data for a given type and bbox, save to file if not cached
def get_overture_geojson(type_name, bbox, cache_prefix):
    filename = f"{cache_prefix} - {type_name}.geojson"

    # Use cached GeoJSON if exists
    if os.path.exists(filename):
        print(f"Using cached '{filename}'")
        return filename

    # Fetch GeoJSON, assuming OvertureMaps is installed
    print(f"Fetching '{filename}'")
    command = f'overturemaps download --bbox={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]} -f geojson --type="{type_name}" -o "{filename}"'
    os.system(command)
    
    return filename

def main(
        bbox=None,
        overture_types=None, 
        polygon_height_mode='f', 
        polygon_height_default=3.0, 
        polygon_height_flat_default=1.0, 
        line_width_default=3.0, 
        line_height_default=2.0, 
        point_width_default=4.0, 
        point_height_default=4.0, 
        base_margin=10.0,
        base_height=2.0,
        output_stl_path=""        
        ):

    global transformer
    global default_types

    # Default Overture types
    if overture_types is None:
        overture_types = default_types

    # Log of geometries
    csv_file = open(output_stl_path + ".csv", mode='w', newline='')
    csv_writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
    csv_writer.writerow(["type", "subtype", "class", "poly_height", "line_width", "line_height", "point_width", "point_height"])

    # Use manual bounding box
    if bbox is None:
        raise ValueError("Manual bounding box must be provided.")

    bbox_poly = box(*bbox)

    # Get the EPSG code
    epsg_code = get_utm_epsg_code(*bbox)
    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg_code}", always_xy=True)

    # Get the convergence angle
    minx, miny, maxx, maxy = bbox
    center_lon = (minx + maxx) / 2.0
    center_lat = (miny + maxy) / 2.0
    convergence_angle = get_convergence_angle(center_lon, center_lat, epsg_code)

    all_vertices = []
    all_faces = []
    vertex_offset = 0

    # Download or load cached geojson for each type
    geojson_files = []
    for type_name in overture_types:
        geojson_file = get_overture_geojson(type_name, bbox, output_stl_path)
        geojson_files.append(geojson_file)

    for input_geojson_path in geojson_files:
        print("Processing " + input_geojson_path)
        with open(input_geojson_path, 'r') as f:
            gj = geojson.load(f)

        # Process each feature
        for feature in gj['features']:
            # Shape
            geom = shape(feature['geometry'])

            # Clip geometry to bounding box
            clipped_geom = geom.intersection(bbox_poly)
            if clipped_geom.is_empty:
                continue  # Skip features outside the area

            # Properties
            props = feature.get('properties', {})
            props_subtype = props.get('subtype', '').lower()
            props_class = props.get('class', '').lower()

            # Start and compare values for polygon dimensions
            if props_subtype in polygon_flat:
                polygon_height = polygon_height_flat_default
                polygon_height_compare = polygon_height_flat_default
            else:
                polygon_height = polygon_height_default   
                polygon_height_compare = polygon_height_default

            # Height mode other than 'f': explicit height if it exists
            if polygon_height_mode != 'f':
                height_gen = props.get('height')
                height_m = props.get('height_m')
                height_ft = props.get('height_ft')
                height_floors = props.get('num_floors')
                if height_gen is not None:
                    polygon_height = float(height_gen)
                elif height_m is not None:
                    polygon_height = float(height_m)
                elif height_ft is not None:
                    polygon_height = float(height_ft) * 0.3048
                elif height_floors is not None:
                    polygon_height = float(height_floors) * 3.0 + 3.0

                # Height mode 'l': adjust if explicit height too low
                if polygon_height_mode == 'l':
                    if polygon_height < polygon_height_compare:
                        polygon_height = polygon_height_compare

                # Height mode 'h': adjust if explicit height too high
                if polygon_height_mode == 'h':
                    if polygon_height > polygon_height_compare:
                        polygon_height = polygon_height_compare                        

            polygon_height = polygon_height_flat_default if polygon_height < polygon_height_flat_default else polygon_height

            # Start values for line dimensions
            line_height = line_height_default
            if props_subtype == "road" and props_class in road_widths:
                line_width = road_widths[props_class]
                if line_width < line_width_default:
                    line_width = line_width_default
            else:
                line_width = line_width_default

            # Start values for point dimensions
            if f"{props_subtype}/{props_class}" in point_relevant:
                point_width = point_width_default
                point_height = point_height_default
            else:
                point_width = 0.0
                point_height = 0.0

            csv_writer.writerow([clipped_geom.geom_type, props_subtype, props_class, polygon_height, line_width, line_height, point_width, point_height])

            # Use clipped geometry for further processing
            type = clipped_geom.geom_type
            match type:
                # Polygon
                case 'Polygon' | 'MultiPolygon':
                    if polygon_height > 0.0:
                        if type == 'Polygon':
                            geoms = [clipped_geom]
                        else:
                            geoms = clipped_geom.geoms

                        for poly in geoms:
                            vertices, faces = polygon_to_extruded_mesh(poly, polygon_height)
                            if vertices is not None and faces is not None:                            
                                faces += vertex_offset
                                all_vertices.append(vertices)
                                all_faces.append(faces)
                                vertex_offset += len(vertices)

                # Line string
                case 'LineString' | 'MultiLineString':
                    if line_width > 0.0 and line_height > 0.0:
                        if type == 'LineString':
                            geoms = [clipped_geom]
                        else:
                            geoms = clipped_geom.geoms

                        for line in geoms:
                            vertices, faces = line_to_extruded_mesh(line, line_width, line_height)
                            if vertices is not None and faces is not None:
                                faces += vertex_offset
                                all_vertices.append(vertices)
                                all_faces.append(faces)
                                vertex_offset += len(vertices)

                # Point
                case 'Point' | 'MultiPoint':
                    if point_width > 0.0 and point_height > 0.0:
                        if type == 'Point':
                            geoms = [clipped_geom]
                        else:
                            geoms = clipped_geom.geoms

                        for point in geoms:
                            vertices, faces = point_to_cylinder_mesh(point, point_width, point_height)
                            if vertices is not None and faces is not None:
                                faces += vertex_offset
                                all_vertices.append(vertices)
                                all_faces.append(faces)
                                vertex_offset += len(vertices)                                

                case 'Point':
                    # TODO TBA
                    pass

                case 'GeometryCollection':
                    # TODO TBA
                    pass

                case _:
                    print(f"Skipping unsupported geometry type: " + clipped_geom.geom_type)

    csv_file.close()

    if not all_vertices:
        raise ValueError("No polygon features found in the GeoJSON.")

    # Concatenate all vertices and faces
    vertices = np.vstack(all_vertices)
    faces = np.vstack(all_faces)

    # Rotate mesh so that north is up in STL
    print(f"Rotating mesh by {-convergence_angle:.6f} degrees to align north-up.")
    vertices = rotate_vertices(vertices, -convergence_angle)

    # Add base under the map
    # TODO Doesn't work: can't concatenate with previous data
    if base_margin >= 0 and base_height > 0:
        # Project bbox corners to projected coordinates
        bbox_poly_proj = project_geom(bbox_poly)
        minx, miny, maxx, maxy = bbox_poly_proj.bounds

        # Expand bounds by margin
        minx -= base_margin
        miny -= base_margin
        maxx += base_margin
        maxy += base_margin

        # Create base polygon in projected coordinates
        base_poly = box(minx, miny, maxx, maxy)

        # Extrude base polygon to base_height
        mesh_obj_base = trimesh.creation.extrude_polygon(base_poly, base_height)
        base_vertices = mesh_obj_base.vertices
        base_faces = mesh_obj_base.faces

        # Shift base so its top is at Z=0 (so map sits on top)
        if base_vertices is not None and base_faces is not None and base_vertices.shape[0] > 0 and base_faces.shape[0] > 0:
            base_vertices[:, 2] -= base_height
            base_faces += vertices.shape[0]
            vertices = np.vstack([vertices, base_vertices])
            faces = np.vstack([faces, base_faces])
        else:
            print("Base mesh is invalid or empty, skipping.") 

    print(f"Total vertices: {vertices.shape[0]}, Total faces: {faces.shape[0]}")
    if vertices.shape[0] == 0 or faces.shape[0] == 0:
        raise RuntimeError("No geometry generated for STL export.")

    # Create mesh
    mesh_obj = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

    # Validate mesh
    print("Checking if mesh is watertight...")
    if not mesh_obj.is_watertight:
        print("Mesh is not watertight. Attempting to fill holes...")
        mesh_obj.fill_holes()
        if not mesh_obj.is_watertight:
            print("Failed to make mesh watertight. Proceeding with current mesh.")
        else:
            print("Mesh successfully filled to be watertight.")
    else:
        print("Mesh is watertight.")

    # Check and fix normals
    if not mesh_obj.is_winding_consistent:
        print("Fixing mesh normals for consistency...")
        mesh_obj.fix_normals()

    # Export to STL
    print(f"Exporting mesh...")
    mesh_obj.export(output_stl_path + ".stl")
    print("Done.")

# User interface

if __name__ == "__main__":
    input_bbox = input("Enter bounding box (long west, lat south, long east, lat north): ")
    bbox = [float(x.strip()) for x in input_bbox.split(",")]

    # Overture types
    types_list = ', '.join(default_types)
    overture_types_input = input(f"Comma-separated Overture types to download ({types_list}): ").strip()
    if overture_types_input != "":
        overture_types = [t.strip() for t in overture_types_input.split(",") if t.strip()]
    else:
        overture_types = None

    # Polygon height mode
    polygon_height_mode_default = 'e'
    input_height_mode = input("Mode for use of the height settings below: f(ixed), l(owest), h(ighest), e(xplicit) (e): ")
    polygon_height_mode = input_height_mode.strip().lower()[0] if len(input_height_mode) > 0 else polygon_height_mode_default
    if polygon_height_mode not in ['f', 'l', 'h', 'e']:
        polygon_height_mode = polygon_height_mode_default

    # Polygon height for generic use
    polygon_height_default = 3.0
    input_height = input(f"Default or limit height for buildings ({polygon_height_default} m): ")
    polygon_height = float(input_height) if input_height != "" else polygon_height_default

    # Polygon height for flat surfaces
    polygon_height_flat_default = 1.0
    input_height_flat = input(f"Default or limit height for flat areas ({polygon_height_flat_default} m): ")
    polygon_height_flat = float(input_height_flat) if input_height_flat != "" else polygon_height_flat_default

    # Line width
    line_width_default = 3.0
    input_line_width = input(f"Default or limit width for lines ({line_width_default} m): ")
    line_width = float(input_line_width) if input_line_width != "" else line_width_default

    # Line height
    line_height_default = 2.0
    input_line_height = input(f"Default or limit height for lines ({line_height_default} m): ")
    line_height = float(input_line_height) if input_line_height != "" else line_height_default

    # Point width/diameter
    point_width_default = 4.0
    input_point_width = input(f"Default width for points ({point_width_default} m): ")
    point_width = float(input_point_width) if input_point_width != "" else point_width_default

    # Point height
    point_height_default = 4.0
    input_point_height = input(f"Default height for points ({point_height_default} m): ")
    point_height = float(input_point_height) if input_point_height != "" else point_height_default

    # Base margin
    #base_margin_default = 10.0
    #input_base_margin = input(f"Base margin ({base_margin_default} m): ").strip()
    #base_margin = float(input_base_margin) if input_base_margin != "" else base_margin_default
    base_margin = 0.0

    # Base height
    #base_height_default = 2.0
    #input_base_height = input(f"Base height ({base_height_default} m): ").strip()
    #base_height = float(input_base_height) if input_base_height != "" else base_height_default
    base_height = 0.0

    # File name for STL and GeoJSON files
    input_outputfile = input("File name for generated files without extension: ")

    if input_outputfile != "":
        main(bbox, overture_types, polygon_height_mode, polygon_height, polygon_height_flat, line_width, line_height, point_width, point_height, base_margin, base_height, input_outputfile)
    else:
        print("Missing a file path!")
  