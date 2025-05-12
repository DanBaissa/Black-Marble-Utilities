import argparse
import contextlib
import os
import re
import shutil
import ssl
import sys
import urllib.request
from datetime import datetime, timedelta
from tkinter import filedialog
import geopandas as gpd
import h5py
import rasterio
import requests
from rasterio.merge import merge
from rasterio.transform import from_bounds

# Constants
USERAGENT = 'tis/download.py_1.0--' + sys.version.replace('\n','').replace('\r','')

# Load the shapefiles
shapefile_path = 'Data/Black_Marble_IDs/Black_Marble_World_tiles.shp'
boundary_shapefile_path = 'Data/Black_Marble_IDs/BlackMarbleTiles/BlackMarbleTiles.shp'
shapefile = gpd.read_file(shapefile_path)
boundary_shapefile = gpd.read_file(boundary_shapefile_path)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Download and process Black Marble Night Lights data.")
    parser.add_argument("--start-date", required=True, help="Start date in format 'YYYY-MM-DD'.")
    parser.add_argument("--end-date", required=True, help="End date in format 'YYYY-MM-DD'.")
    parser.add_argument("--country", required=True, help="Country name.")
    parser.add_argument("--destination-folder", required=True, help="Folder to save downloaded and processed files.")
    parser.add_argument("--token", required=True, help="Authentication token for downloading data.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    selected_country = args.country
    destination_folder = args.destination_folder
    token = args.token

    bounding_box = get_bounding_box(selected_country, shapefile)
    collection_id = "C3365931269-LAADS"  # Updated collection ID for VNP46A2 version 2

    urls = search_nasa_cmr(collection_id, start_date, end_date, bounding_box)
    if urls:
        download(urls, destination_folder, token, selected_country)
    else:
        print("No URLs found for the given parameters.")

def get_bounding_box(country, gdf):
    country_gdf = gdf[gdf['COUNTRY'] == country]
    return country_gdf.total_bounds

def search_nasa_cmr(collection_id, start_date, end_date, bounding_box):
    cmr_search_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
    bbox_str = f"{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}"
    h5_links = []
    current_date = start_date

    while current_date <= end_date:
        target_date = current_date.strftime('%Y-%m-%d')
        temporal_range = f"{target_date}T00:00:00Z,{target_date}T23:59:59Z"
        params = {
            "collection_concept_id": collection_id,
            "temporal": temporal_range,
            "bounding_box": bbox_str,
            "page_size": 50
        }
        response = requests.get(cmr_search_url, params=params)

        if response.status_code == 200:
            granules = response.json().get('feed', {}).get('entry', [])
            print(f"{target_date}: Found {len(granules)} granules")
            for granule in granules:
                for link in granule.get('links', []):
                    href = link.get('href', '')
                    if href.startswith('https') and href.endswith('.h5'):
                        h5_links.append(href)
                        print("Found URL:", href)
        else:
            print(f"Error on {target_date}: {response.status_code}", response.text)
        current_date += timedelta(days=1)

    return h5_links

def download(urls, destination_folder, token, selected_country):
    print("Download Started.")
    ctx = ssl.create_default_context()
    headers = {'user-agent': USERAGENT, 'Authorization': f'Bearer {token}'}
    start_download_thread(urls, headers, ctx, destination_folder, selected_country)

def start_download_thread(urls, headers, ctx, destination_folder, selected_country):
    for url in urls:
        filename = url.split('/')[-1]
        dest = os.path.join(destination_folder, filename)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response, open(dest, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            print(f"Successfully downloaded {filename}")
        except Exception as e:
            print(f'Failed to download {url} due to {e}')
            continue

    print('Download of all files completed.')
    print('Please Wait. Converting and Merging .h5 files into Geo.tifs...')
    process_h5_files(shapefile_path, boundary_shapefile_path, selected_country, destination_folder, destination_folder)
    print('Processing complete!')

def process_h5_files(country_shapefile_path, boundary_shapefile_path, selected_country, input_folder, output_folder):
    selected_rows = shapefile[shapefile['COUNTRY'] == selected_country.strip()]
    files = [f for f in os.listdir(input_folder) if f.endswith('.h5')]
    files_by_day = {}
    for file in files:
        day = re.search('\.A(\d+)\.', file).group(1)
        files_by_day.setdefault(day, []).append(file)

    for day, files in files_by_day.items():
        rasters = []
        for file in files:
            tile_id = re.search('h\d{2}v\d{2}', file).group()
            shape = selected_rows[selected_rows['TileID'] == tile_id]
            if not shape.empty:
                with h5py.File(os.path.join(input_folder, file), "r") as f:
                    ntl_path = "/HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields/Gap_Filled_DNB_BRDF-Corrected_NTL"
                    if ntl_path not in f:
                        print(f"⚠️ Skipping {file}: dataset not found.")
                        continue
                    ntl_data = f[ntl_path][...]
                    boundary_shape = boundary_shapefile[boundary_shapefile['TileID'] == tile_id]
                    left, bottom, right, top = boundary_shape.total_bounds
                    temp_file = os.path.join(input_folder, f"temp_{tile_id}.tif")
                    with rasterio.open(temp_file, "w", driver="GTiff",
                                       height=ntl_data.shape[0], width=ntl_data.shape[1], count=1,
                                       dtype=ntl_data.dtype, crs=shape.crs.to_epsg(),
                                       transform=from_bounds(left, bottom, right, top,
                                                             ntl_data.shape[1], ntl_data.shape[0])) as dst:
                        dst.write(ntl_data, 1)
                    rasters.append(temp_file)

        with contextlib.ExitStack() as stack:
            files_to_merge = [stack.enter_context(rasterio.open(raster)) for raster in rasters]
            merged, transform = merge(files_to_merge)

        for raster in rasters:
            os.remove(raster)

        output_file = os.path.join(output_folder, f"{selected_country}_{day}.tif")
        with rasterio.open(output_file, "w", driver="GTiff", height=merged.shape[1],
                           width=merged.shape[2], count=1, dtype=merged.dtype,
                           crs=shape.crs.to_epsg(), transform=transform) as dest:
            dest.write(merged)
            for file in files:
                os.remove(os.path.join(input_folder, file))

def browse_destination_folder(self):
    self.destination_folder.set(filedialog.askdirectory())

if __name__ == "__main__":
    main()
