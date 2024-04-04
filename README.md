
# Black-Marble-Utilities

## [Introduction](#introduction)
The `Black-Marble-Utilities` project is a collection of Python scripts designed for researchers and GIS professionals working with NASA's VIIRS Black Marble dataset. This dataset provides nightly Earth observations, offering insights into human activities and natural phenomena. The toolkit simplifies data acquisition, preprocessing, exposure adjustment, and geographic targeting, facilitating the integration of Black Marble data into geospatial analyses.

## [Features](#Features)
- [**Downloader**:](#downloader) Automates downloading VIIRS Black Marble data for specified dates and regions.
- [**Exposure Matching**:](#exposure-matching) Standardizes the visual exposure of satellite imagery across datasets.
- [**Raster Stacking**:](#RasterStacking)  Uses astrophotography techniques to stack raster images, enhancing detail and reducing noise.
- [**Data Binning**:](#DataBinningScript) Facilitates spatial analysis by cropping to specific countries and binning data.
- [**Country Cropping**:](#CountryCroppingScript) Enables focused analysis by cropping raster images to precise country boundaries.

## [Prerequisites](#Prerequisites)
You should have Python 3.x installed. This toolkit relies on several libraries, such as Rasterio, GeoPandas, NumPy, and Matplotlib.

## [Installation](#Installation)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Black-Marble-Utilities.git
   cd Black-Marble-Utilities
   ```

2. **Install dependencies**:
   - Install required libraries:
     ```bash
     pip install -r requirements.txt
     ```

## [Usage](#Usage)

Detailed usage instructions for each script are provided in their respective sections below.

### [Downloader](#downloader)

The Downloader script is a tool within the Black-Marble-Utilities toolkit, designed to automate 
the process of downloading NASA's VIIRS (Visible Infrared Imaging Radiometer Suite) Black Marble
data. The VIIRS Black Marble product offers high-resolution nighttime imagery of the Earth, 
revealing patterns of human settlement, economic activity, and natural phenomena under the 
cover of darkness. This data is invaluable for a wide range of applications, from studying 
urbanization and power outages to monitoring natural disasters and ecological changes.

#### How It Works
The `Downloader` script interfaces with NASA's data repositories to fetch VIIRS Black Marble imagery based on user-specified parameters. It requires the user to define a date range for the desired data, the geographical region of interest (typically specified by the country name), and the destination folder where the downloaded data should be stored. Additionally, since access to NASA's data repositories often requires authentication, the script also requires an API token.

#### Key Features
- **Date Range Selection**: Allows users to specify the exact date range for which they need the data, making it easy to obtain historical data or focus on specific events or periods.
- **Geographical Targeting**: By specifying a country, users can narrow down the data download to their region of interest, which optimizes download times and reduces data storage requirements.
- **Automated Data Retrieval**: Once the parameters are set, the script handles the entire process of querying the database, processing the request, and downloading the data, requiring minimal user intervention.

#### Usage Instructions
To use the `Downloader` script, follow the syntax provided in the command-line example below. Replace the placeholders with your specific requirements:

```bash
python Downloader.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD --country "Country Name" --destination-folder ./data --token YOUR_API_TOKEN
```

- `--start-date YYYY-MM-DD`: The start date of the desired data range in the format `YYYY-MM-DD`.
- `--end-date YYYY-MM-DD`: The end date of the desired data range in the format `YYYY-MM-DD`.
- `--country "Country Name"`: The name of the country for which you want to download the data. Ensure the country name is correctly spelled and ideally matches the naming convention used in NASA's datasets.
- `--destination-folder ./data`: The local path to the folder where the downloaded data will be stored. The script will create this folder if it doesn't exist.
- `--token YOUR_API_TOKEN`: Your personal API token for accessing NASA's data repositories. This token is typically obtained by registering on NASA's Earthdata or similar platforms.



### [Exposure Matching](#exposure-matching)

The `Exposure Matching` script is a component of the `Black-Marble-Utilities` toolkit, designed to ensure visual consistency across a series of GeoTIFF images by matching their exposure levels to that of a reference image. This functionality is particularly useful in projects involving time-series analysis of satellite imagery, where differences in lighting conditions, sensor settings, or atmospheric conditions can result in varying exposure levels across images, potentially skewing analysis or visual interpretation.

#### How It Works
The script utilizes image processing techniques to analyze the histogram of pixel values in both the source and reference images. It then applies transformations to the source images to align their histograms with that of the reference image, effectively standardizing exposure across the dataset. This process enhances the comparability of images taken under different conditions by normalizing their visual appearance.

#### Key Features
- **Reference-Based Adjustment**: By using a selected reference image, the script ensures that all adjustments are consistent and centered around a chosen standard, maintaining a uniform look and feel across the image set.
- **Batch Processing**: The script can process an entire directory of GeoTIFF images in one go, automating what would otherwise be a tedious and time-consuming task if done manually.
- **Flexibility in Usage**: The script can be used as a standalone tool or integrated into larger data processing workflows, making it a versatile solution for exposure matching needs.

#### Usage Instructions
To use the `Exposure Matching` script, you need to specify the directory containing the source images you want to adjust, the path to the reference image against which the exposure will be matched, and the directory where the adjusted images will be saved. Follow the example command below, replacing the placeholders with your actual file paths:

```bash
python Exposure_matching.py --source-directory ./source_images --reference-path ./reference_image.tif --output-directory ./matched_images
```

- `--source-directory ./source_images`: The path to the directory containing the source GeoTIFF images whose exposure you want to adjust. The script will process all GeoTIFF files within this directory.
- `--reference-path ./reference_image.tif`: The path to the GeoTIFF image that will serve as the exposure reference. This image should ideally represent the desired visual appearance in terms of lighting and contrast.
- `--output-directory ./matched_images`: The path to the directory where the exposure-matched images will be saved. If this directory does not exist, the script will create it.

### [Country Cropping Script](#CountryCroppingScript) 

The `Country Cropping` script is designed to tailor raster datasets for country-specific analyses. By cropping raster images to the precise geographical boundaries of a chosen country, this tool helps in focusing the analysis on relevant areas, thereby optimizing data handling and processing efforts for tasks that require geographical specificity.

#### How It Works
- **Geospatial Cropping**: Leveraging country boundary data (typically from a shapefile or similar geospatial vector format), the script trims raster images so that only the portions falling within the selected country's borders are retained. This operation reduces the size of the raster files and excludes irrelevant data, making subsequent analyses more efficient and focused.
- **Batch Processing**: The script processes all raster images within a specified directory, applying the cropping operation to each file. This batch processing capability significantly reduces the manual effort required for large datasets.
- **Optional Visualization**: A unique feature of the script is its ability to optionally display the cropped rasters immediately after processing. This immediate feedback is valuable for verifying the cropping results and ensuring that the output aligns with the user's expectations.

#### Key Features
- **Efficiency in Analysis**: By focusing on a specific geographical area, the script makes subsequent data analysis tasks more manageable and relevant.
- **Improved Data Management**: Cropping reduces the file size of raster datasets, facilitating easier storage, handling, and sharing.
- **Versatility**: The script supports a wide range of applications, from environmental monitoring to urban planning, by allowing users to concentrate on areas of interest.

#### Usage Instructions
To utilize the `Country Cropping` script, specify the directory containing the raster files to be cropped, the output directory for the cropped images, the name of the target country, and an optional flag to view the cropped images. The command structure is as follows:

```bash
python Country_cropper.py --raster-dir ./rasters --output-dir ./cropped_rasters --country "Country Name" --view-rasters
```

- `--raster-dir ./rasters`: The directory containing the raster images that need to be cropped. The script will process all compatible files within this directory.
- `--output-dir ./cropped_rasters`: The directory where the cropped raster images will be saved. If this directory doesn't exist, the script will create it.
- `--country "Country Name"`: The name of the country to which the raster images will be cropped. This name should match an entry within the used country boundaries dataset to ensure accurate cropping.
- `--view-rasters`: This optional flag, when included, instructs the script to display the cropped images upon processing. This is useful for immediate visual verification of the cropping operation.


### [Raster Stacking](#RasterStacking) 
The `Raster Stacking` script within the `Black-Marble-Utilities` toolkit is designed to enhance the quality of raster images by reducing noise and improving the signal-to-noise ratio. This script employs two primary techniques: mean stacking and sigma clipping stacking, which can be used individually or combined to process a series of GeoTIFF images. Such techniques are particularly beneficial in astrophotography, remote sensing, and time-series satellite image analysis, where multiple observations of the same area can be combined to mitigate noise and emphasize consistent patterns.

#### How It Works
- **Mean Stacking**: This technique averages the pixel values across a stack of images, effectively reducing random noise. This method is straightforward and effective but can be sensitive to outliers.
- **Sigma Clipping Stacking**: Sigma clipping iteratively excludes pixels that fall beyond a specified standard deviation range (sigma value) from the mean. This method is more robust against outliers, such as transient phenomena or errors in individual images.

#### Key Features
- **Noise Reduction**: Both stacking methods contribute to reducing random noise, enhancing the clarity and usability of the resulting images.
- **Outlier Management**: Sigma clipping stacking provides an added advantage by managing outliers, ensuring that anomalies in individual images do not skew the combined result.
- **Batch Processing**: The script can process all suitable raster images within a specified directory, streamlining the workflow for handling large datasets.

#### Usage Instructions
The script's usage can vary slightly depending on whether mean stacking, sigma clipping stacking, or both methods are desired. Here are examples for each scenario:

- **Mean Stacking Only**:
  ```bash
  python Stacker.py --folder-path ./raster_images --mean-stacking
  ```

- **Sigma Clipping Stacking Only**:
  ```bash
  python Stacker.py --folder-path ./raster_images --sigma-value X --sigma-stacking --iters X
  ```

- **Both Mean and Sigma Clipping Stacking**:
  ```bash
  python Stacker.py --folder-path ./raster_images --sigma-value X --mean-stacking --sigma-stacking --iters X
  ```

In these commands:
- `--folder-path ./raster_images`: Specifies the directory containing the raster images to be stacked.
- `--sigma-value X`: Sets the sigma value for sigma clipping stacking. This parameter defines the standard deviation threshold for excluding outliers. For example --sigma-value 2 removes all values over 2 standard deviations from the median
- `--mean-stacking`: Enables mean stacking.
- `--sigma-stacking`: Enables sigma clipping stacking.
- `--iters X`: Defines the number of iterations for the sigma clipping process. More iterations can improve outlier management but increase processing time. For example --iters 5 performs a maximum of 5 iterations of the algorthm per pixel. 


### [Data Binning Script](#DataBinningScript)

The `Data Binning` script is a specialized tool within the `Black-Marble-Utilities` collection designed to perform spatial analysis by segmenting raster data into uniform, grid-shaped bins. This process is particularly useful for summarizing and analyzing spatial data within specified geographical areas, such as countries. Moreover, this script offers the unique capability to integrate additional data from CSV files into the binning process, allowing for richer, multidimensional analyses.

#### How It Works
- **Country-Specific Cropping**: Initially, the script crops the input raster images to the boundaries of a specified country, focusing the analysis on a particular region of interest and reducing data volume.
- **Binning Process**: The cropped area is then divided into a grid of uniform bins, each representing a specific area size (defined by the bin size parameter). The script aggregates the raster data within each bin, summarizing it according to specified statistical measures (e.g., mean, sum).
- **CSV Data Integration**: If provided, additional data from a CSV file (such as observational data or metadata related to the raster data) can be spatially integrated into the binning process. This data is assigned to bins based on its geographic coordinates, allowing for combined analyses of raster and tabular data.

#### Key Features
- **Focused Analysis**: By cropping data to a specific country, the script allows users to concentrate their analysis on areas of interest, improving both efficiency and relevance.
- **Spatial Summarization**: The binning process provides a summarized view of the raster data, making it easier to identify patterns, trends, and anomalies within the specified region.
- **Data Enrichment**: The ability to incorporate CSV data into the binning process opens up possibilities for more comprehensive analyses, blending raster and non-raster data sources.

#### Usage Instructions
To use the `Data Binning` script, you need to specify the target country, the directory containing the raster files, the optional path to a CSV file containing additional data, the output directory for the binned data, and the bin size in kilometers. Here's how to structure the command:

```bash
python Binner.py --country "Country Name" --raster-dir ./rasters --csv-path ./data.csv --output-dir ./binned_data --bin-size 10
```

- `--country "Country Name"`: The name of the country for which the raster data will be cropped and binned. Ensure the country name matches the naming convention in your geographical data sources.
- `--raster-dir ./rasters`: The directory containing the raster files to be processed.
- `--csv-path ./data.csv`: (Optional) The path to a CSV file containing additional data to be integrated into the binning process. This parameter can be omitted if not applicable.
- `--output-dir ./binned_data`: The directory where the binned data (and any processed CSV data) will be saved.
- `--bin-size 10`: The size of the bins in kilometers, determining the resolution of the spatial summarization.



## Contributing
Contributions are welcome. Please fork the repository, create a feature branch, and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- NASA for providing the VIIRS Black Marble dataset.
- Open-source Python libraries that support geospatial data processing.
