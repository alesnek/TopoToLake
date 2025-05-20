# Name: IsoClass.py
#
# Purpose: This python script tool is designed for use with a geodatabase populated with USGS
# topographic map rasters. The tool searches the geodatabase, resamples the rasters to a user-
# specified cell size, and runs ISO Cluster Unsupervised Classification on the resampled
# rasters using a user-specified number of classes.
# 
# Outputs: The tool will output classified rasters, which can then be used as inputs for the
# Create Lake  Polygons tool. The tool also creates a csv file called "classified_rasters"
# that includes:
# (1) a "classified_raster" field that is auto-populated with output file names, and
# (2) an empty "water_class" field.
# 
# Next steps: After the tool runs, visually examine the classified rasters to determine
# which "Value" category corresponds to water, then manually add the "Value" to the correct
# record in the "water_class" field of the "classfied_rasters" csv file. This is essential! 
# The "classified_rasters" csv file is an input parameter for the Create Lake Polygons tool. 
# 
# Notes: Not all output files will have 6 classes; this depends on the color scheme of the input 
# topographic maps. Adjust the number of classes, minimum class size, and sample interval as
# needed for your study area.
#
# Author: Dr. Alia Lesnek
# School of Earth and Environmental Sciences, Queens College
# Created: 05/19/2025
# Copyright: (c) Alia Lesnek 2025
#
#---------------------------------------------------------------

# # import libraries
import re
import arcpy
import os
import csv

# create a function to rename rasters with location_year
def extract_location_year(raster_name):
    parts = raster_name.split("_")
        
    # look for year
    year = next((p for p in parts if re.fullmatch(r"\d{4}", p)), "unknown")
    
    # find index of year and extract location
    try:
        year_index = parts.index(year)
        location_parts = parts[:year_index - 1] # exclude map code
        location = "_".join(location_parts)
    except:
        location = "UnknownLoc"
        
    return f"{location}_{year}"
    
    
# set parameters in tool
input_gdb = arcpy.GetParameterAsText(0) # geodatabase location
cell_size = arcpy.GetParameterAsText(1) # for resampled raster
num_classes = int(arcpy.GetParameterAsText(2)) # number of classes for ISO cluster unsup. classification
min_size = int(arcpy.GetParameterAsText(3)) # minimum class size; 20 is default
sample_interval = int(arcpy.GetParameterAsText(4)) # sampling interval; 10 is default
output_gdb = arcpy.GetParameterAsText(5) # optional; can be same as input
project_folder = arcpy.GetParameterAsText(6) # choose location where raster names and water class will be saved

# set workspace location and parameters
arcpy.env.workspace = input_gdb
arcpy.env.overwriteOutput = True

# create csv for tracking classified outputs and writing raster names
csv_path = os.path.join(project_folder, "classified_rasters.csv")
if not os.path.exists(csv_path):
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["classified_raster", "water_class"])

# get all rasters in geodatabase
rasters = arcpy.ListRasters()
total = len(rasters)

# loop through resample and classification for all rasters in gdb, save to new file
for idx, raster in enumerate(rasters, start = 1):
    short_name = extract_location_year(raster)

    resampled_name = f"{short_name}_{cell_size}m"
    iso_output_name = f"{short_name}_{num_classes}class"
    
    resampled_path = f"in_memory/{resampled_name}" # temporary file
    iso_output_path = os.path.join(output_gdb, iso_output_name) # saved permanently

    arcpy.AddMessage(f"Processing {idx} of {total}: {raster}")
    
    # RESAMPLE
    arcpy.management.Resample(raster, resampled_path, cell_size, "NEAREST")
    
    arcpy.AddMessage(f"--> Resampled raster to {cell_size} meters: {resampled_name}")
    
    # ISO CLUSTER UNSUPERVISED CLASSIFICATION
    iso_result = arcpy.sa.IsoClusterUnsupervisedClassification(resampled_path, num_classes, min_size, sample_interval)
    iso_result.save(iso_output_path)

    # write output raster name to csv
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([iso_output_name, ""])

    arcpy.AddMessage(f"--> Saved classified raster: {iso_output_name}")
