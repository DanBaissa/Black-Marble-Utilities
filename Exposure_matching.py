import argparse
import rasterio
from skimage import exposure
import os
import glob  # Import glob module

def load_and_match_histograms(source_directory, reference_path, output_directory):
    # Use glob to find all .tif files in the source directory
    source_paths = glob.glob(os.path.join(source_directory, '*.tif'))

    if source_paths and reference_path and output_directory:
        # Load the reference GeoTIFF
        with rasterio.open(reference_path) as ref:
            image_reference = ref.read(1)  # Reading the first channel

            print("Matching Histograms")

        for source_path in source_paths:
            with rasterio.open(source_path) as src:
                image_source = src.read(1)  # Reading the first channel
                meta_source = src.meta

                # Apply histogram matching
                matched_image = exposure.match_histograms(image_source, image_reference)

                # Construct unique output paths
                base_name = os.path.splitext(os.path.basename(source_path))[0]
                matched_output_path = os.path.join(output_directory, f"{base_name}_matched.tif")

                # Save the matched images
                meta_source.update(count=1)  # Ensure metadata is updated for single channel
                with rasterio.open(matched_output_path, "w", **meta_source) as dest:
                    dest.write(matched_image, 1)

        print("Histogram matching completed for all .tif files in the source directory. Files saved.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Match histograms of all GeoTIFFs in a source directory to a reference.")
    parser.add_argument("--source-directory", required=True, help="Path to the directory containing source GeoTIFF files.")
    parser.add_argument("--reference-path", required=True, help="Path to the reference GeoTIFF file.")
    parser.add_argument("--output-directory", required=True, help="Directory to save the processed files.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    load_and_match_histograms(args.source_directory, args.reference_path, args.output_directory)

if __name__ == "__main__":
    main()
