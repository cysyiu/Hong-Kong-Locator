import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from functools import partial
from geopandas import points_from_xy
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


# Import the geocode_address function from the previous code snippet
def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(tk.END, filepath)


def geocode():
    csv_file = entry_file_path.get()
    address_column = entry_address_column.get()
    
    if csv_file and address_column:
        try:
            gdf = geocode_address(csv_file, address_column)
            messagebox.showinfo("Geocoding Complete", "Geocoding completed successfully. Shapefile saved as 'geocoded_data.shp'.")
        except Exception as e:
            messagebox.showerror("Geocoding Error", f"An error occurred during geocoding:\n{str(e)}")
    else:
        messagebox.showerror("Input Error", "Please select a CSV file and enter the address column name.")


# Create the main application window
window = tk.Tk()
window.title("Address Geocoding Application")


# Create and place the widgets
label_file_path = tk.Label(window, text="CSV File Path:")
label_file_path.grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_file_path = tk.Entry(window, width=50)
entry_file_path.grid(row=0, column=1, padx=10, pady=5)
button_browse = tk.Button(window, text="Browse", command=browse_file)
button_browse.grid(row=0, column=2, padx=5, pady=5)

label_address_column = tk.Label(window, text="Address Column:")
label_address_column.grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_address_column = tk.Entry(window, width=30)
entry_address_column.grid(row=1, column=1, padx=10, pady=5)

button_geocode = tk.Button(window, text="Geocode", command=geocode)
button_geocode.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Start the application
window.mainloop()
