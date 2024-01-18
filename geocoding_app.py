import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from functools import partial
from geopandas import points_from_xy

# Import the geocode_address function from the previous code snippet
from geocoding_function import geocode_address

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