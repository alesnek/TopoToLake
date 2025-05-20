# Name: CreateLakePolygons.py
#
# Purpose: This python script tool will create polygons for all areas identified as water in the ISO
# Cluster Unsupervised Classification output rasters. The tool loops through the geodatabase 
# where the classified rasters are saved while pulling "water_class" values from the "reclassified_rasters"
# csv file completed in the previous step.
# 
# Outputs: The tool will output simplified polygons of lakes present on the topographic maps. Polygons
# are added to a user-specified geodatabase location but are not automatically added to the map.
#
# Next steps: Add polygons to your map. Check polygons for accuracy and manually delete features as needed.
#
# Notes: Ensure you have a completed "classified_rasters.csv"  file before you run this tool, as the tool
# will read classified raster names and water_class values from this csv. In this tool, the raster is clipped
# to a shoreline polygon, but this step can be changed or omitted if working in inland regions.
#
# Author: Dr. Alia Lesnek
# School of Earth and Environmental Sciences, Queens College
# Created: 05/19/2025
# Copyright: (c) Alia Lesnek 2025
#
#---------------------------------------------------------------

# import libraries, set overwrite
import arcpy
import os
import csv
import re

arcpy.env.overwriteOutput = True

# === Parameters ===
input_gdb = arcpy.GetParameterAsText(0)  # GDB containing classified rasters
csv_file = arcpy.GetParameterAsText(1)   # CSV with classified_raster,water_class
coastline = arcpy.GetParameterAsText(2)  # Coastline polygon
area_threshold = float(arcpy.GetParameterAsText(3))  # e.g., 200
output_gdb = arcpy.GetParameterAsText(4)  # GDB to store output lake polygons

# define function to create output name in format "state_location_year_Lakes" from classified_raster name
def raster_to_lake_name(raster_name):
    base = raster_name.rsplit("_", 1)[0]  # strip "_6class", "_8class", etc. from name
    return f"{base}_Lakes"

# === Set environment ===
arcpy.env.workspace = input_gdb
arcpy.env.scratchWorkspace = arcpy.env.scratchGDB

# === Read the CSV and process each raster ===
with open(csv_file, newline="") as csvfile:
    reader = list(csv.DictReader(csvfile))
    total = len(reader)

    for idx, row in enumerate(reader, start=1):
        raster_name = row["classified_raster"]
        water_class = row["water_class"]

        # Skip if water class is blank
        if not water_class.strip():
            arcpy.AddWarning(f"Skipping {raster_name}: No water_class value specified.")
            continue

        water_class = int(water_class)
        output_name = raster_to_lake_name(raster_name)

        full_raster_path = os.path.join(input_gdb, raster_name)
        base_name = os.path.splitext(raster_name)[0]

        # === In-memory names ===
        reclass = f"in_memory/{base_name}_reclass"
        majority = f"in_memory/{base_name}_majority"
        filled = f"in_memory/{base_name}_filled"
        lake_raster = f"in_memory/{base_name}_finalRC"
        polygons = f"in_memory/{base_name}_poly"
        clipped_polygons = f"in_memory/{base_name}_clipped"

        arcpy.AddMessage(f"Processing {idx} of {total}: {raster_name}")

        # 1. Reclassify water vs non-water
        class_values = set()
        with arcpy.da.SearchCursor(full_raster_path, ["Value"]) as cursor:
            for row in cursor:
                class_values.add(row[0])
        non_water = [val for val in class_values if val != water_class]
        remap = [[water_class, 1]] + [[val, 0] for val in non_water]
        reclass = arcpy.sa.Reclassify(full_raster_path, "Value", arcpy.sa.RemapValue(remap))

        # 2. Majority Filter
        majority = arcpy.sa.MajorityFilter(reclass, "EIGHT", "HALF")

        # 3. Fill
        filled = arcpy.sa.Fill(arcpy.sa.Raster(majority))

        # 4. Final reclass to remove 0s
        lake_raster = arcpy.sa.Reclassify(filled, "Value", arcpy.sa.RemapValue([[0, "NODATA"], [1, 1]]))

        # 5. Raster to Polygon
        polygons = arcpy.conversion.RasterToPolygon(lake_raster, polygons, "SIMPLIFY", "Value")

        # 6. Clip to coastline
        arcpy.analysis.Clip(polygons, coastline, clipped_polygons)

        # 7. Area filter (add area field first)
        arcpy.management.MakeFeatureLayer(clipped_polygons, "temp_lyr")
        arcpy.management.AddField("temp_lyr", "poly_area", "DOUBLE")
        arcpy.management.CalculateGeometryAttributes("temp_lyr", [["poly_area", "AREA_GEODESIC"]], area_unit="SQUARE_METERS")
        arcpy.management.SelectLayerByAttribute("temp_lyr", "NEW_SELECTION", f"poly_area > {area_threshold}")

        # 8. Save output
        final_output = os.path.join(output_gdb, arcpy.ValidateTableName(output_name, output_gdb))
        arcpy.management.CopyFeatures("temp_lyr", final_output)

        arcpy.AddMessage(f"--> Saved: {output_name}")