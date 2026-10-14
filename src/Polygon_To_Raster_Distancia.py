
import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
from rasterio.features import rasterize

# -----------------------------
# Paths
# -----------------------------
vector_path = "Clases_Distancia.shp"
snap_raster_path = "DEM_SanJorge.tif"
output_raster = "Clases_Distancia_raster.tif"

# -----------------------------
# Load polygon
# -----------------------------
gdf = gpd.read_file(vector_path)

# -----------------------------
# Convert "Clase" (string → numeric)
# -----------------------------
mapping = {
    "0-30": 1,
    "30-60": 2,
    "60-120": 3,
    "120-240": 4,
    ">240": 5
}

gdf["Clase_code"] = gdf["Clase"].map(mapping)

# Validate mapping
if gdf["Clase_code"].isna().any():
    raise ValueError("⚠️ Some 'Clase' values were not mapped.")

# -----------------------------
# Open snap raster (DEM)
# -----------------------------
with rasterio.open(snap_raster_path) as src:
    transform = src.transform
    crs = src.crs
    width = src.width
    height = src.height

# Reproject if needed
if gdf.crs != crs:
    gdf = gdf.to_crs(crs)

# -----------------------------
# Prepare shapes
# -----------------------------
shapes = [
    (geom, value) for geom, value in zip(gdf.geometry, gdf["Clase_code"])
]

# -----------------------------
# Rasterize (aligned to DEM)
# -----------------------------
raster = rasterize(
    shapes=shapes,
    out_shape=(height, width),
    transform=transform,
    fill=0,
    dtype="int16",
    all_touched=False
)

# -----------------------------
# Save raster
# -----------------------------
with rasterio.open(
    output_raster,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype="int16",
    crs=crs,
    transform=transform,
    compress="lzw"
) as dst:
    dst.write(raster, 1)

print("✅ Raster created with full DEM extent and snap alignment!")



