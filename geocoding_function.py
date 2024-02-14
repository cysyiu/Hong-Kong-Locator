import requests
import pandas as pd
import geopandas as gpd

def geocode_address(input_csv, output_csv):
    # Read the input CSV file
    df = pd.read_csv(input_csv)
    # column_names = df.columns.tolist()
    # Create a new DataFrame to store the geocoded results
    geocoded_data = pd.DataFrame([])

    # Iterate over each address in the input CSV
    for address in df['Address']:
        #Create the API request URL
        base_url = 'https://geodata.gov.hk/gs/api/v1.0.0/locationSearch'
        params = {'q': address}
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            # Extract the X and Y values from the first search result
            data = response.json()
            first_result = pd.DataFrame(data).iloc[0]
            x = first_result['x']
            y = first_result['y']
            geocoded_data = pd.concat([geocoded_data, pd.DataFrame({'Address': [address], 'X': [x], 'Y': [y]})], ignore_index=True)
        else:
                # If no results found, set X and Y as None
            geocoded_data = pd.concat([geocoded_data, pd.DataFrame({'Address': [address], 'X': [None], 'Y': [None]})], ignore_index=True)

    # Write the geocoded data to the output CSV file
    geocoded_data.to_csv(output_csv, index=False)

    #Create a GeoDataFrame from the geocoded data
    geometry = gpd.points_from_xy(geocoded_data['X'], geocoded_data['Y'])
    gdf = gpd.GeoDataFrame(geocoded_data, geometry=geometry, crs='EPSG:2326')

    #Save the GeoDataFrame as a shapefile
    gdf.to_file('output.shp')

# Usage example
input_file = input("Enter the input CSV file name: ")
output_file = input("Enter the output CSV file name: ")
geocode_address(input_file, output_file)