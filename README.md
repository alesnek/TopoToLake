# The "Topo To Lake" Toolbox
 
**TopoToLake** is a pair of ArcGIS Pro script tools that extract water features from historical USGS topographic map rasters using unsupervised classification. The tools are designed to work together to automate lake mapping from scanned maps, particularly where traditional vector water data may be missing or outdated.

Developed by [Dr. Alia Lesnek](https://www.qc.cuny.edu/academics/sees/alia-lesnek/) at CUNY Queens College, these tools are ideal for reserach in historical hydrology and environmental science.

---

## 🧰 Tools Included

### 1. `IsoClass.py` — *Step 1: Classify Topographic Maps*

**Purpose:**  
Searches a geodatabase for USGS topographic map rasters, resamples them to a user-specified cell size, and applies ISO Cluster Unsupervised Classification with a user-defined number of classes.

**Outputs:**
- Classified rasters saved to a geodatabase
- A CSV file (`classified_rasters.csv`) with:
  - `classified_raster`: the name of each output raster
  - `water_class`: an empty field to be manually filled in later

**Next Steps:**
After running the tool, open the classified rasters and visually identify which `"Value"` corresponds to water. Manually enter that value into the `water_class` column of the CSV. This step is **essential** for the second tool to run correctly.

**Notes:**
- Not all outputs will contain 6 classes — results depend on the input map's color scheme.
- You may need to adjust the number of classes, minimum class size, or sample interval to suit your study area.

---

### 2. `CreateLakePolygons.py` — *Step 2: Create Lake Polygons*

**Purpose:**  
Generates simplified lake polygons based on the ISO classification results. It reads the classified rasters and the corresponding water class values from the `classified_rasters.csv` file.

**Outputs:**
- Vector polygons of lakes clipped to a user-specified shoreline feature
- Polygons are saved to a geodatabase but are **not automatically added to the map**

**Next Steps:**
Add the output polygons to your map manually. Review and clean up the polygons to remove errors or non-lake features.

**Notes:**
- You must complete the `classified_rasters.csv` file before running this tool.
- The clipping step requires a shoreline polygon, but you can skip or modify this step for inland areas.

---

## 🛠 Requirements

- ArcGIS Pro 3.x
- Spatial Analyst extension
- Python 3.9+ with ArcPy

---

## 📁 Project Structure
 ```
TopoToLake/
 ├── README.md
 ├── LICENSE
 ├── tools/
 │ ├── LakeMapping.atbx # ArcGIS Pro toolbox
 │ ├── IsoClass.py # Script for classification
 │ ├── CreateLakePolygons.py # Script for lake polygon creation
 ```

---

## 👩‍💻 Workflow

1. Download USGS topographic maps and add them to a single geodatabase in your ArcGIS Pro project.
2. Add `TopoToLake.atbx` to your ArcGIS Pro project.
3. Run **Step 1: Classify Topographic Maps** to classify your topographic maps.
4. Open the resulting classified rasters and manually populate the `water_class` column in `classified_rasters.csv`.
5. Run **Step 2: Create Lake Polygons** to extract vector lake features using the completed CSV.

---

🚫 This repository is provided for reference and download only.
**Please do not submit pull requests**. If you'd like to modify the tools, feel free to fork your own copy.

---

## 👩‍🔬 Author

**Dr. Alia Lesnek**  
School of Earth and Environmental Sciences  
Queens College, City University of New York  
© 2025

---

## 📜 License

[MIT License](LICENSE) — free to use, modify, and share with attribution.
