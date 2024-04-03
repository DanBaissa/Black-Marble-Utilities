import argparse
import glob
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import rasterstats
from geopandas.tools import sjoin
from rasterio.io import MemoryFile
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import Polygon
from shapely.geometry import mapping


def crop_raster_with_shapefile(raster_path, country_shape, output_path):
    with rasterio.open(raster_path) as src:
        country_shape = country_shape.to_crs(src.crs)
        out_image, out_transform = mask(src, [mapping(geom) for geom in country_shape.geometry], crop=True)
        out_meta = src.meta.copy()

        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(out_image[0], 1)

def process_raster_data(selected_country, raster_paths, csv_path, output_dir, bin_size):
    country_shapefile = 'Data/World_Countries/World_Countries_Generalized.shp'
    shapefile = gpd.read_file(country_shapefile)
    gdf = shapefile[shapefile['COUNTRY'] == selected_country]

    if gdf.empty:
        raise ValueError(f"No shape data found for the selected country: {selected_country}")

    for raster_path in raster_paths:
        cropped_raster_path = os.path.join(output_dir, os.path.basename(raster_path))
        crop_raster_with_shapefile(raster_path, gdf, cropped_raster_path)

    # Adjust bin_size from km to meters for CRS EPSG:3857
    bin_size_m = bin_size * 1000
    gdf = gdf.to_crs(epsg=3857)

    xmin, ymin, xmax, ymax = gdf.total_bounds
    rows = int(np.ceil((ymax - ymin) / bin_size_m))
    cols = int(np.ceil((xmax - xmin) / bin_size_m))

    polygons = []
    for x in range(cols):
        for y in range(rows):
            polygons.append(Polygon([(x * bin_size_m + xmin, y * bin_size_m + ymin),
                                     ((x + 1) * bin_size_m + xmin, y * bin_size_m + ymin),
                                     ((x + 1) * bin_size_m + xmin, (y + 1) * bin_size_m + ymin),
                                     (x * bin_size_m + xmin, (y + 1) * bin_size_m + ymin)]))

    grid = gpd.GeoDataFrame({'geometry': polygons}, crs='EPSG:3857')
    intersection = gpd.overlay(gdf, grid, how='intersection')

    # Process rasters
    for raster_path in raster_paths:
        with rasterio.open(raster_path) as src:
            nodata_value = src.nodata if src.nodata else -32768
            raster_data = src.read(1)
            raster_data = np.where(raster_data == nodata_value, np.nan, raster_data)  # replace nodata with NaN

            transform, width, height = calculate_default_transform(src.crs, intersection.crs, src.width, src.height,
                                                                   *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': intersection.crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with MemoryFile() as memfile:
                with memfile.open(**kwargs) as mem_dst:
                    reproject(
                        source=rasterio.band(src, 1),
                        destination=rasterio.band(mem_dst, 1),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=intersection.crs,
                        resampling=Resampling.nearest
                    )
                reprojected_raster = memfile.open().read(1)

            zonal_stats = rasterstats.zonal_stats(intersection, reprojected_raster, affine=transform, stats='mean')
            raster_column_name = os.path.splitext(os.path.basename(raster_path))[0]
            intersection[raster_column_name] = [stat['mean'] for stat in zonal_stats]

    # Process CSV only if a path is provided
    if csv_path:
        df = pd.read_csv(csv_path)
        gdf_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
        gdf_points.set_crs("EPSG:4326", inplace=True)
        gdf_points = gdf_points.to_crs(epsg=3857)

        joined = sjoin(gdf_points, intersection, how='inner')
        for column in df.columns.difference(['longitude', 'latitude']):
            mean_obs = joined.groupby('index_right')[column].mean()
            intersection[column] = mean_obs

    intersection.to_file(os.path.join(output_dir, 'intersection.shp'))

    # Visualization
    for column in [col for col in intersection.columns if col not in ['geometry']]:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        intersection.plot(column=column, ax=ax, legend=True, edgecolor='black')
        plt.title(f'{column}')
        plt.savefig(os.path.join(output_dir, f'{column}.png'))

def parse_arguments():
    parser = argparse.ArgumentParser(description="Crop rasters to a specified country and optionally process CSV data.")
    parser.add_argument("--country", required=True, help="Name of the country for cropping.")
    parser.add_argument("--raster-dir", required=True, help="Directory containing raster files.")
    parser.add_argument("--csv-path", help="Optional path to a CSV file for additional processing.")
    parser.add_argument("--output-dir", required=True, help="Output directory for processed files.")
    parser.add_argument("--bin-size", type=int, default=10, help="Bin size for the grid in kilometers. Default is 10km.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    raster_paths = glob.glob(os.path.join(args.raster_dir, '*.tif'))
    process_raster_data(args.country, raster_paths, args.csv_path, args.output_dir, args.bin_size)
    print("All processing completed successfully.")

if __name__ == "__main__":
    main()
