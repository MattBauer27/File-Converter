import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
from pdf2image import convert_from_path
import geopandas as gpd
import os
import zipfile
import tempfile


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Converter")
        self.file_path = ''
        self.export_path = ''
        self.file_type_1 = tk.StringVar(self.root)
        self.file_type_2 = tk.StringVar(self.root)
        self.file_types = ['.pdf', '.png', '.jpg', '.geojson', '.shp']
        self.file_type_mappings = {
            '.pdf': ['.png', '.jpg'],
            '.png': ['.jpg', '.pdf'],
            '.jpg': ['.png', '.pdf'],
            '.geojson': ['.shp'],
            '.shp': ['.geojson']
        }
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10),
                             background='green', foreground='black')
        self.style.map('TButton',
                       foreground=[('pressed', 'red'), ('active', 'red')],
                       background=[('pressed', 'green'), ('active', 'green')]
                       )
        self.file_type_1.set('.pdf')  # Set the initial file_type_1
        self.create_widgets()
        # Update file_type_2 options based on the initial file_type_1
        self.update_file_type_2_options()

    def create_widgets(self):
        ttk.Label(self.root, text="Select input file type:").grid(
            column=0, row=0)
        self.file_type_1_menu = ttk.OptionMenu(
            self.root, self.file_type_1, *self.file_types)
        self.file_type_1_menu.grid(column=1, row=0)

        self.import_button = ttk.Button(
            self.root, text="Import file", command=self.import_file)
        self.import_button.grid(column=0, row=1, columnspan=2)

        self.file_type_2_menu = ttk.OptionMenu(
            self.root, self.file_type_2, *self.file_type_mappings[self.file_type_1.get()])
        self.file_type_2_menu.grid(column=1, row=2)

        self.export_button = ttk.Button(
            self.root, text="Export file", command=self.export_file)
        self.export_button.grid(column=0, row=3, columnspan=2)

        self.run_button = ttk.Button(
            self.root, text="Run", command=self.run_conversion)
        self.run_button.grid(column=0, row=4, columnspan=2)

        self.progress = ttk.Progressbar(self.root, length=200)
        self.progress.grid(column=0, row=5, columnspan=2)

        self.completion_label = ttk.Label(self.root, text="")
        self.completion_label.grid(column=0, row=6, columnspan=2)
        self.file_type_1.trace("w", self.update_file_type_1_options)
        self.file_type_1.trace("w", self.update_file_type_2_options)

    def update_file_type_1_options(self, *args):
        menu = self.file_type_1_menu["menu"]
        menu.delete(0, "end")
        for string in self.file_types:
            menu.add_command(label=string,
                             command=lambda value=string: self.file_type_1.set(value))

    def import_file(self):
        file_types = [(f"{self.file_type_1.get()} files",
                       f"*{self.file_type_1.get()}"), ("All files", "*.*")]
        if self.file_type_1.get() == '.shp':
            file_types.insert(0, (".zip files", "*.zip"))
        self.file_path = filedialog.askopenfilename(filetypes=file_types)
        if self.file_path.lower().endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(self.file_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            shp_file = next((f for f in os.listdir(temp_dir)
                            if f.lower().endswith('.shp')), None)
            if shp_file is None:
                self.completion_label['text'] = "No .shp file found in zip archive"
                return
            self.file_path = os.path.join(temp_dir, shp_file)

    def update_file_type_2_options(self, *args):
        menu = self.file_type_2_menu["menu"]
        menu.delete(0, "end")
        for string in self.file_type_mappings.get(self.file_type_1.get(), []):
            menu.add_command(label=string,
                             command=lambda value=string: self.file_type_2.set(value))
        if self.file_type_mappings.get(self.file_type_1.get()):
            self.file_type_2.set(
                self.file_type_mappings.get(self.file_type_1.get())[0])

    def export_file(self):
        self.export_path = filedialog.asksaveasfilename(
            defaultextension=self.file_type_2.get())

    def run_conversion(self):
        self.progress['value'] = 0
        self.completion_label['text'] = ""
        try:
            if self.file_type_1.get() in ['.png', '.jpg', '.pdf']:
                self.convert_image()
            elif self.file_type_1.get() in ['.geojson', '.shp']:
                self.convert_geo_data()
        except Exception as e:
            self.completion_label['text'] = str(e)
            print(f"Error: {e}")  # print the exception to the console

    def convert_image(self):
        if self.file_type_1.get() == '.pdf':
            images = convert_from_path(self.file_path)
            image = images[0]
        else:  # PNG or JPEG
            image = Image.open(self.file_path)
        if self.file_type_2.get() == '.png':
            image.save(self.export_path, 'PNG')
        elif self.file_type_2.get() == '.jpg':
            image.convert('RGB').save(self.export_path, 'JPEG')
        elif self.file_type_2.get() == '.pdf':
            image.convert('RGB').save(
                self.export_path, 'PDF', resolution=100.0)
        self.progress['value'] = 100
        self.completion_label['text'] = "Complete"

    def convert_geo_data(self):
        geo_data = gpd.read_file(self.file_path)
        if self.file_type_2.get() == '.geojson':
            geo_data.to_file(self.export_path, driver='GeoJSON')
        elif self.file_type_2.get() == '.shp':
            geo_data.to_file(self.export_path, driver='ESRI Shapefile')
            # Zip the shapefile components
            base_path = os.path.splitext(self.export_path)[0]
            with zipfile.ZipFile(f"{base_path}.zip", 'w') as zipf:
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    if os.path.exists(f"{base_path}{ext}"):
                        zipf.write(f"{base_path}{ext}", arcname=os.path.basename(
                            f"{base_path}{ext}"))
                        os.remove(f"{base_path}{ext}")
            self.export_path = f"{base_path}.zip"
        self.progress['value'] = 100
        self.completion_label['text'] = "Complete"


if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()
