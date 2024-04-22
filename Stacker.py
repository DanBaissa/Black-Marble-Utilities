import argparse
import os
import glob
import rasterio
import numpy as np
from datetime import datetime
from astropy.stats import SigmaClip
import matplotlib.pyplot as plt


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process and stack .tif files by month, with options to delete the originals.")
    parser.add_argument("--folder-path", required=True, help="Path to the folder containing .tif files.")
    parser.add_argument("--sigma-value", type=float, default=None,
                        help="Sigma value for sigma clipping, required if --sigma-stacking is enabled.")
    parser.add_argument("--threshold-value", type=float, required=True,
                        help="Threshold value to set numbers above this to NaN.")
    parser.add_argument("--mean-stacking", action='store_true', help="Enable mean stacking.")
    parser.add_argument("--sigma-stacking", action='store_true', help="Enable sigma clipping stacking.")
    parser.add_argument("--iters", type=int, default=5, help="Number of iterations for sigma clipping.")
    parser.add_argument("--monthly-stacking", action='store_true', help="Stack rasters monthly based on their dates.")
    parser.add_argument("--delete-originals", action='store_true',
                        help="Delete original raster files after processing.")
    return parser.parse_args()


def julian_to_month(julian_day):
    return datetime.strptime(julian_day, '%Y%j').strftime('%Y-%m')


def delete_original_files(files):
    for file in files:
        os.remove(file)
        print(f"Deleted file: {file}")


def stack_and_save(data_arrays, month, folder_path, meta, mean_stacking, sigma_stacking, maxiters, sigma_value):
    if not data_arrays:
        print("No data arrays available for stacking.")
        return

    stacked_arrays = np.stack(data_arrays, axis=0)
    fig, axs = plt.subplots(1, 2 if mean_stacking and sigma_stacking else 1, figsize=(10, 5))
    if not isinstance(axs, np.ndarray):
        axs = [axs]
    plot_idx = 0

    if mean_stacking:
        mean_array = np.nanmean(stacked_arrays, axis=0)
        output_path = os.path.join(folder_path, f'output_mean_{month}.tif')
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(mean_array, 1)
        axs[plot_idx].imshow(np.log1p(mean_array), cmap='turbo')
        axs[plot_idx].set_title(f'Log of Mean Stack {month}')
        plot_idx += 1

    if sigma_stacking:
        sigma_clip = SigmaClip(sigma=sigma_value, maxiters=maxiters)
        clipped_arrays = sigma_clip(stacked_arrays, axis=0)
        mean_array_clipped = np.nanmean(clipped_arrays, axis=0)
        output_path = os.path.join(folder_path, f'output_sigma_clipped_{month}.tif')
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(mean_array_clipped, 1)
        axs[plot_idx].imshow(np.log1p(mean_array_clipped), cmap='turbo')
        axs[plot_idx].set_title(f'Log of Sigma Clipped {month}')

    plt.tight_layout()
    plt.savefig(os.path.join(folder_path, f'output_plot_{month}.pdf'))



def process_tif_files(args):
    file_list = glob.glob(os.path.join(args.folder_path, '*.tif'))
    if args.monthly_stacking:
        grouped_files = {}
        for file in file_list:
            base_name = os.path.basename(file)
            try:
                date_part = base_name.split('_')[1][:7]  # Assuming format 'Country_YYYYDDD'
                month_key = julian_to_month(date_part)
                if month_key not in grouped_files:
                    grouped_files[month_key] = []
                grouped_files[month_key].append(file)
            except ValueError as e:
                print(f"Skipping file {base_name} due to error: {e}")

        for month, files in grouped_files.items():
            data_arrays = []
            reference_shape = None
            metadata = None
            for file in files:
                with rasterio.open(file) as src:
                    data = src.read(1).astype('float32')  # Read first band
                    data[data > args.threshold_value] = np.nan
                    if reference_shape is None:
                        reference_shape = data.shape
                        metadata = src.meta.copy()
                        metadata.update(count=1)  # Ensure metadata is for single-band output
                    if data.shape == reference_shape:
                        data_arrays.append(data)
                    else:
                        print(f"Skipping array from {file} due to shape mismatch: expected {reference_shape}, got {data.shape}")

            if data_arrays:
                stack_and_save(data_arrays, month, args.folder_path, metadata, args.mean_stacking, args.sigma_stacking, args.iters, args.sigma_value)
            if args.delete_originals:
                delete_original_files(files)




def main():
    args = parse_arguments()
    process_tif_files(args)


if __name__ == "__main__":
    main()
