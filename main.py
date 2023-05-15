import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image
from pdf2image import convert_from_path

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title('File Converter')

        self.file_path = None
        self.file_type_1 = tk.StringVar()
        self.file_type_2 = tk.StringVar()

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # OptionMenu for file type 1
        ttk.Label(self.root, text="Select input file type:").grid(column=0, row=0)
        file_types_1 = ['.png', '.jpg', '.pdf']
        self.option_menu_1 = ttk.OptionMenu(self.root, self.file_type_1, file_types_1[0], *file_types_1)
        self.option_menu_1.grid(column=1, row=0)

        # Import file button
        self.import_button = ttk.Button(self.root, text="Import File", command=self.import_file)
        self.import_button.grid(column=0, row=1, columnspan=2)

        # OptionMenu for file type 2
        ttk.Label(self.root, text="Select output file type:").grid(column=0, row=2)
        file_types_2 = ['.png', '.jpg', '.pdf']
        self.option_menu_2 = ttk.OptionMenu(self.root, self.file_type_2, file_types_2[0], *file_types_2)
        self.option_menu_2.grid(column=1, row=2)

        # Export file button
        self.export_button = ttk.Button(self.root, text="Export File", command=self.export_file)
        self.export_button.grid(column=0, row=3, columnspan=2)

        # Run button
        self.run_button = ttk.Button(self.root, text="Run", command=self.run_conversion)
        self.run_button.grid(column=0, row=4, columnspan=2)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=200)
        self.progress.grid(column=0, row=5, columnspan=2)

        # Completion label
        self.completion_label = ttk.Label(self.root, text="")
        self.completion_label.grid(column=0, row=6, columnspan=2)

    def import_file(self):
        file_types = [(f"{self.file_type_1.get()} files", f"*{self.file_type_1.get()}")]
        self.file_path = filedialog.askopenfilename(filetypes=file_types)

    def export_file(self):
        file_types = [(f"{self.file_type_2.get()} files", f"*{self.file_type_2.get()}")]
        self.export_path = filedialog.asksaveasfilename(defaultextension=self.file_type_2.get(), filetypes=file_types)

    def run_conversion(self):
        self.progress['value'] = 0
        self.completion_label['text'] = ""
        print(f"Converting '{self.file_path}' from '{self.file_type_1.get()}' to '{self.file_type_2.get()}' and saving to '{self.export_path}'")
        self.root.after(100, self.convert_file)

    def convert_file(self):
        if self.file_type_1.get() != self.file_type_2.get():
            if self.file_type_1.get() == '.pdf':
                images = convert_from_path(self.file_path)
                total = len(images)
                for i in range(total):
                    if self.file_type_2.get() == '.png':
                        images[i].save(self.export_path if total == 1 else f"{self.export_path}_{i}.png", 'PNG')
                    elif self.file_type_2.get() == '.jpg':
                        images[i].convert('RGB').save(self.export_path if total == 1 else f"{self.export_path}_{i}.jpg", 'JPEG')
                    self.progress['value'] = (i+1) / total * 100
                    self.root.update_idletasks()
            else:
                image = Image.open(self.file_path)
                if self.file_type_2.get() == '.png':
                    image.save(self.export_path, 'PNG')
                elif self.file_type_2.get() == '.jpg':
                    image.convert('RGB').save(self.export_path, 'JPEG')
                elif self.file_type_2.get() == '.pdf':
                    image.save(self.export_path, 'PDF', resolution=100.0)
                self.progress['value'] = 100
                self.root.update_idletasks()
        self.completion_label['text'] = "Complete"

def main():
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

