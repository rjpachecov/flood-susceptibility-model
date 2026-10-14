import geopandas as gpd
import rasterio
from rasterio.features import rasterize

# Rutas de archivos
vector_path = r'D:\CVS_RONDA_HIDRICA\SIG\Shapefile\Cobertura\CuencaSanJorge\CoberturaTierra_UsoActual.shp'
snap_raster_path = r'D:\CVS_RONDA_HIDRICA\SIG\DEM_Cuenca_SanJorge\DEM_SanJorge.tif'
output_raster = r'D:\CVS_RONDA_HIDRICA\WoE\CuencaSanJorge\Raster_Cobertura\Raster_Cobertura.tif'

# -----------------------------
# 1. Cargar y limpiar el shapefile
# -----------------------------
gdf = gpd.read_file(vector_path)
gdf = gdf[gdf.geometry.notnull() & gdf.is_valid]  # Eliminar geometrías vacías o corruptas

# -----------------------------
# 2. Conversión automática de texto a numérico (Evita diccionarios manuales)
# -----------------------------
# Se usa '.cat.codes + 1' para que los códigos comiencen en 1 (reservando el 0 para NoData)
gdf["N3_COBERT_code"] = gdf["N3_COBERT"].astype("category").cat.codes + 1

# Generar y mostrar el diccionario de mapeo automático para tu referencia
category_mapping = dict(enumerate(gdf["N3_COBERT"].astype("category").cat.categories, start=1))
print("📋 Mapeo automático de categorías:", category_mapping)

# -----------------------------
# 3. Abrir el raster base (DEM) y extraer perfil
# -----------------------------
with rasterio.open(snap_raster_path) as src:
    meta = src.meta.copy()
    transform = src.transform
    crs = src.crs
    width = src.width
    height = src.height

# Reproyectar el shapefile si su sistema de coordenadas no coincide con el DEM
if gdf.crs != crs:
    gdf = gdf.to_crs(crs)

# -----------------------------
# 4. Preparar formas (geometría, valor)
# -----------------------------
shapes = ((geom, value) for geom, value in zip(gdf.geometry, gdf["N3_COBERT_code"]))

# -----------------------------
# 5. Rasterizar
# -----------------------------
nodata_value = 0
raster = rasterize(
    shapes=shapes,
    out_shape=(height, width),
    transform=transform,
    fill=nodata_value,
    dtype="int16",
    all_touched=False
)

# -----------------------------
# 6. Actualizar metadatos y guardar de forma optimizada
# -----------------------------
meta.update({
    'driver': 'GTiff',
    'height': height,
    'width': width,
    'count': 1,
    'dtype': 'int16',
    'crs': crs,
    'transform': transform,
    'nodata': nodata_value,
    'compress': 'lzw'
})

with rasterio.open(output_raster, 'w', **meta) as dst:
    dst.write(raster, 1)

print("✅ ¡Raster mejorado, con metadatos limpios y perfectamente alineado al DEM!")



