from libs.Overture2STL import (
    bbox_size_meters,
    map_types_default,
    map_types_all,
    overture_to_stl,
)

if __name__ == "__main__":
    # Bounding box
    input_bbox = input(
        "Enter bounding box (long west, lat south, long east, lat north): "
    ).strip()
    bbox = [round(float(x.strip()), 6) for x in input_bbox.split(",")]

    width_m, height_m = bbox_size_meters(bbox)
    print(
        f"Given the provided bounding box, the dimensions of the area are roughly {round(width_m, 0)} m wide and {round(height_m, 0)} m high. Take this into account when editing object dimensions and scaling."
    )

    # Overture types
    types_list = ", ".join(map_types_default)
    overture_types_input = input(
        f"Comma-separated Overture map types to download ({types_list}): "
    ).strip()
    if overture_types_input != "":
        overture_types = [
            t.strip()
            for t in overture_types_input.split(",")
            if t.strip() and t.strip() in map_types_all
        ]
    else:
        overture_types = map_types_default

    # Polygon height mode
    polygon_height_mode_default = "e"
    input_height_mode = input(
        "Mode for use of the height settings below: f(ixed), l(owest), h(ighest), e(xplicit) (e): "
    ).strip()
    polygon_height_mode = (
        input_height_mode.strip().lower()[0]
        if len(input_height_mode) > 0
        else polygon_height_mode_default
    )
    if polygon_height_mode not in ["f", "l", "h", "e"]:
        polygon_height_mode = polygon_height_mode_default

    # Polygon height for generic use
    polygon_height_default = 3.0
    input_height = input(
        f"Default or limit height for buildings ({polygon_height_default} m): "
    ).strip()
    polygon_height = (
        float(input_height) if input_height != "" else polygon_height_default
    )

    # Polygon height for flat surfaces
    polygon_height_flat_default = 1.0
    input_height_flat = input(
        f"Default or limit height for flat areas ({polygon_height_flat_default} m): "
    ).strip()
    polygon_height_flat = (
        float(input_height_flat)
        if input_height_flat != ""
        else polygon_height_flat_default
    )

    # Line width
    line_width_default = 3.0
    input_line_width = input(
        f"Default or limit width for lines ({line_width_default} m): "
    ).strip()
    line_width = (
        float(input_line_width) if input_line_width != "" else line_width_default
    )

    # Line height
    line_height_default = 2.0
    input_line_height = input(
        f"Default or limit height for lines ({line_height_default} m): "
    ).strip()
    line_height = (
        float(input_line_height) if input_line_height != "" else line_height_default
    )

    # Point width/diameter
    point_width_default = 4.0
    input_point_width = input(
        f"Default width for points ({point_width_default} m): "
    ).strip()
    point_width = (
        float(input_point_width) if input_point_width != "" else point_width_default
    )

    # Point height
    point_height_default = 4.0
    input_point_height = input(
        f"Default height for points ({point_height_default} m): "
    ).strip()
    point_height = (
        float(input_point_height) if input_point_height != "" else point_height_default
    )

    # Scaling factor
    scale_percent_default = 100.0
    input_scale_percent = input(
        f"Scaling factor in percent ({scale_percent_default}%): "
    ).strip()
    scale_percent = (
        float(input_scale_percent)
        if input_scale_percent != ""
        else scale_percent_default
    )

    # Base height
    base_height_default = 2.0
    input_base_height = input(f"Base height ({base_height_default} mm): ").strip()
    base_height = (
        float(input_base_height) if input_base_height != "" else base_height_default
    )

    # Base margin
    base_margin_default = 5.0
    input_base_margin = input(f"Base margin ({base_margin_default} mm): ").strip()
    base_margin = (
        float(input_base_margin) if input_base_margin != "" else base_margin_default
    )

    # File name for STL and GeoJSON files
    input_outputfile = input(
        "File name for generated files without extension: "
    ).strip()

    if input_outputfile != "":
        overture_to_stl(
            bbox,
            overture_types,
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
            input_outputfile,
        )
    else:
        print("Missing a file path!")
