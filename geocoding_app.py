import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import geopandas as gpd
import requests
import os
from pyproj import Transformer

def geocode_address(input_csv, address_column, output_gis, geocoded_csv, coord_system, gis_format):
    df = pd.read_csv(input_csv, encoding="utf-8")  # Ensure support for Chinese characters
    geocoded_data = df.copy()  # Preserve original data

    # Prepare transformer if converting HK1980 to WGS84
    transformer = None
    if coord_system == "WGS 1984":
        transformer = Transformer.from_crs("EPSG:2326", "EPSG:4326", always_xy=True)

    lat_list, lon_list = [], []

    for address in df[address_column]:
        base_url = 'https://geodata.gov.hk/gs/api/v1.0.0/locationSearch'
        response = requests.get(base_url, params={'q': address})

        if response.status_code == 200 and response.json():
            data = response.json()[0]
            x, y = data['x'], data['y']

            if transformer:
                lon, lat = transformer.transform(x, y)
            else:
                lon, lat = x, y  # Keep in HK1980
        else:
            lon, lat = None, None

        lon_list.append(lon)
        lat_list.append(lat)

    geocoded_data["Longitude"] = lon_list
    geocoded_data["Latitude"] = lat_list
    geocoded_data.to_csv(geocoded_csv, encoding="utf-8", index=False)

    # Build GeoDataFrame with proper CRS based on coordinate system selection
    crs = "EPSG:2326" if coord_system == "Hong Kong 1980" else "EPSG:4326"
    gdf = gpd.GeoDataFrame(
        geocoded_data, 
        geometry=gpd.points_from_xy(geocoded_data["Longitude"], geocoded_data["Latitude"]),
        crs=crs
    )

    # Export using the appropriate format and driver if needed
    if gis_format == "Shapefile":
        gdf.to_file(output_gis)  # default for shapefile
    elif gis_format == "KML":
        gdf.to_file(output_gis, driver="KML")
    elif gis_format == "GeoJSON":
        gdf.to_file(output_gis, driver="GeoJSON")

def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(tk.END, filepath)

    try:
        df = pd.read_csv(filepath, encoding="utf-8")
        column_options = df.columns.tolist()
        selected_column.set(column_options[0])

        dropdown["menu"].delete(0, "end")
        for option in column_options:
            dropdown["menu"].add_command(label=option, command=tk._setit(selected_column, option))

    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file:\n{str(e)}")

def geocode():
    csv_file = entry_file_path.get()
    address_column = selected_column.get()
    coord_system = selected_system.get()
    gis_format = selected_gis_format.get()

    if csv_file and address_column:
        filename, _ = os.path.splitext(os.path.basename(csv_file))
        # Determine output GIS filename based on the selected format
        if gis_format == "Shapefile":
            output_gis = f"{filename}.shp"
        elif gis_format == "KML":
            output_gis = f"{filename}.kml"
        elif gis_format == "GeoJSON":
            output_gis = f"{filename}.geojson"

        geocoded_csv = f"{filename}_geocoded.csv"

        try:
            geocode_address(csv_file, address_column, output_gis, geocoded_csv, coord_system, gis_format)
            messagebox.showinfo("Geocoding Complete", 
                f"GIS file saved as '{output_gis}'.\nGeocoded CSV saved as '{geocoded_csv}'.")
        except Exception as e:
            messagebox.showerror("Geocoding Error", f"Error: {str(e)}")
    else:
        messagebox.showerror("Input Error", "Please select a CSV file, an address column, and a coordinate system.")

window = tk.Tk()
window.title("Geocoding Application")

# CSV file selection
tk.Label(window, text="CSV File Path:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_file_path = tk.Entry(window, width=50)
entry_file_path.grid(row=0, column=1, padx=10, pady=5)
tk.Button(window, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

# Dropdown to choose address column from CSV
tk.Label(window, text="Address Column:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
selected_column = tk.StringVar()
dropdown = tk.OptionMenu(window, selected_column, "")
dropdown.grid(row=1, column=1, padx=10, pady=5)

# Coordinate system selection
tk.Label(window, text="Coordinate System:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
selected_system = tk.StringVar(value="Hong Kong 1980")
coord_dropdown = tk.OptionMenu(window, selected_system, "Hong Kong 1980", "WGS 1984")
coord_dropdown.grid(row=2, column=1, padx=10, pady=5)

# GIS format selection for output
tk.Label(window, text="GIS Export Format:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
selected_gis_format = tk.StringVar(value="Shapefile")
gis_format_dropdown = tk.OptionMenu(window, selected_gis_format, "Shapefile", "KML", "GeoJSON")
gis_format_dropdown.grid(row=3, column=1, padx=10, pady=5)

# Geocode button to start processing
tk.Button(window, text="Geocode", command=geocode).grid(row=4, column=0, columnspan=3, padx=10, pady=10)

window.mainloop()
