# -*- coding: utf-8 -*-
"""01_Sundarban_data_extraction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17gPsGY382vAyfQYjvh2zw-ClrElugslt

**Importing Necessary Libraries**
The script begins by importing necessary libraries:

1) ee: Google Earth Engine library for interacting with Earth Engine servers.

2) pandas as pd: A library for data manipulation and analysis.

3) geopandas as gpd: An open-source project to make working with geospatial data in python easier.

4) shapely.geometry: For manipulation and analysis of planar geometric objects.

5) datetime: For working with dates as date objects.
"""

import ee
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from datetime import datetime
import logging

"""**Authentication and Initialization**
The code authenticates and initializes the Earth Engine using ee.Authenticate() and ee.Initialize() respectively.
"""

ee.Authenticate()

ee.Initialize()

"""**Function 1: extract_data**
This function is designed to extract data from Google Earth Engine based on the given parameters.

1) If no region is provided, it defaults to a specified region (the Sundarbans).

2) It creates an ImageCollection filtered by date and region, and selects a specific band (default is NDVI - Normalized Difference Vegetation Index).
"""

def extract_data(start_date, end_date, band='NDVI', dataset='MODIS/006/MOD13A2', region=None, scale=1000):
    """Extract data from Google Earth Engine."""
    try:
        # Default to the Sundarbans if no region is provided
        if region is None:
            region = ee.Geometry.Rectangle([88.0, 21.5, 90.0, 22.5]).centroid()

        collection = (ee.ImageCollection(dataset)
                      .filterDate(ee.Date(start_date), ee.Date(end_date))
                      .filterBounds(region)
                      .select(band))
        return collection
    except Exception as e:
        logging.error(f"An error occurred during data extraction: {e}")
        return None

"""**Function 2: process_data_to_dataframe**

This function processes the Earth Engine data collection into a Pandas dataframe.

1) If no data collection is provided, it raises a ValueError.

2) If no region is specified, it defaults to the Sundarbans.

3) It iterates over a range of dates, filters the collection for each date range, and computes the mean composite for each period.

4) It reduces the region to a dictionary of means for the specified band, and constructs a dataframe from these data points.
"""

def process_data_to_dataframe(collection, start_date, end_date, band='NDVI', temporal_resolution=16, region=None, scale=1000):
    """Process the Earth Engine data collection into a Pandas dataframe."""
    data_points = []

    try:
        if collection is None:
            raise ValueError("No data available to process.")

        # Default to the Sundarbans if no region is provided
        if region is None:
            region = ee.Geometry.Rectangle([88.0, 21.5, 90.0, 22.5]).centroid()

        # Create a list of dates to iterate over
        dates = pd.date_range(start=start_date, end=end_date, freq=f'{temporal_resolution}D')

        for single_date in dates:
            end_date = single_date + pd.Timedelta(days=temporal_resolution)
            filtered_collection = collection.filterDate(ee.Date(single_date.strftime("%Y-%m-%d")), ee.Date(end_date.strftime("%Y-%m-%d")))
            image = filtered_collection.mean()  # Taking the mean composite for the period

            # This function will reduce region to a dictionary of means in the region set by the geometry
            reduction = image.reduceRegion(
              reducer=ee.Reducer.mean(),
              geometry=region,
              scale=scale,
              maxPixels=1e13
            )

            data = reduction.getInfo()

            # Check if the band is in the data
            if band in data:
                value = data[band]
            else:
                value = 'NA'  # If not, set a default value
                logging.warning(f"Data for {band} not available on {single_date.strftime('%Y-%m-%d')}")

            data_points.append({
                'year': single_date.year,
                'month': single_date.month,
                band.lower(): value,
                'latitude': region.coordinates().get(1).getInfo(),
                'longitude': region.coordinates().get(0).getInfo(),
            })

        df = pd.DataFrame(data_points)
        return df

    except Exception as e:
        logging.error(f"An error occurred during data processing: {e}")
        return pd.DataFrame()

"""**Function 3: main**

The main function orchestrates the extraction and processing of data.

1) It defines a time range for data extraction.

2) It calls extract_data to extract data, and process_data_to_dataframe to process the extracted data from the MODIS/006/MOD13A2 into a dataframe.

3) It then writes the dataframe to a CSV file at the specified output_path.

This block ensures that the main function is called when the script is run.
"""

def main(output_path='/content/drive/MyDrive/Processed_data/sundarban_ndvi.csv'):
    # Define the time range
    start_date = '2000-02-18'
    end_date = '2020-07-09'

    # Step 1: Data Extraction
    collection = extract_data(start_date, end_date, band='NDVI')

    # Step 2: Data Processing
    df = process_data_to_dataframe(collection, start_date, end_date, band='NDVI')

    # Output the DataFrame to a CSV file
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
    main()

"""**Function 4: main**

The main function serves as the entry point to the script, coordinating the data extraction, processing, and saving the air temperature data to a CSV file. Time Range Definition:

1) The time range for data extraction is defined by specifying start_date and end_date.

2) The extract_data function is called with the specified time range, band, and dataset to extract the data from the ECMWF/ERA5/DAILY dataset for the mean 2-meter air temperature.

3) The process_data_to_dataframe function is called to process the extracted data into a dataframe. The temporal resolution and scale are specified as arguments.

4) The dataframe is then written to a CSV file at the specified output_path.

This block ensures that the main function is called when the script is run.


"""

def main(output_path='/content/drive/MyDrive/Processed_data/temperature_data.csv'):
    # Define the time range
    start_date = '2000-02-18'
    end_date = '2020-07-09'

    # Step 1: Data Extraction
    collection = extract_data(start_date, end_date, band='mean_2m_air_temperature', dataset='ECMWF/ERA5/DAILY')

    # Step 2: Data Processing
    df = process_data_to_dataframe(collection, start_date, end_date, band='mean_2m_air_temperature', temporal_resolution=16,
                                   scale=27830)

    # Output the DataFrame to a CSV file
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
    main()

"""**Function 5: main**

The main function orchestrates the steps of data extraction, processing, and exporting in relation to precipitation data.

1) A time range for data extraction is defined by specifying the start_date and end_date.

2) The extract_data function is invoked to extract data concerning total precipitation from the ECMWF/ERA5/DAILY dataset within the defined time range.

3) The process_data_to_dataframe function is utilized to process the extracted data into a DataFrame, with specific arguments for the band, temporal resolution, and scale.

4) The DataFrame is then outputted to a CSV file at the specified output_path.

This block ensures that the main function is executed when the script is run.
"""

def main(output_path='/content/drive/MyDrive/Processed_data/precipitation_data.csv'):
    # Define the time range
    start_date = '2000-02-18'
    end_date = '2020-07-09'

    # Step 1: Data Extraction
    collection = extract_data(start_date, end_date, band='total_precipitation', dataset='ECMWF/ERA5/DAILY')

    # Step 2: Data Processing
    df = process_data_to_dataframe(collection, start_date, end_date, band='total_precipitation', temporal_resolution=16,
                                   scale = 27830)

    # Output the DataFrame to a CSV file
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
    main()

"""**Function 5: main**

The main function orchestrates the steps of data extraction, processing, and exporting in relation to surface elevation data.

1) A time range for data extraction is defined by specifying the start_date and end_date.

2) The extract_data function is invoked to extract data concerning total precipitation from the HYCOM/sea_surface_elevation dataset within the defined time range.

3) The process_data_to_dataframe function is utilized to process the extracted data into a DataFrame, with specific arguments for the band, temporal resolution, and scale.

4) The DataFrame is then outputted to a CSV file at the specified output_path.

This block ensures that the main function is executed when the script is run.
"""

def main(output_path='/content/drive/MyDrive/Processed_data/sea_surface_anomaly_data.csv'):
    # Define the time range
    start_date = '2000-02-18'
    end_date = '2020-07-09'

    # Step 1: Data Extraction
    collection = extract_data(start_date, end_date, band='surface_elevation', dataset='HYCOM/sea_surface_elevation')

    # Step 2: Data Processing
    df = process_data_to_dataframe(collection, start_date, end_date, band='surface_elevation', temporal_resolution=16,
                                   scale = 8905.6)

    # Output the DataFrame to a CSV file
    df.to_csv(output_path, index=False)

if __name__ == '__main__':
    main()