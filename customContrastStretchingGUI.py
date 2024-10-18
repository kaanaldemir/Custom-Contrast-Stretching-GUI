import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, __version__ as PILLOW_VERSION

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fundus Image Processor")
        self.root.geometry("1800x1500")  # Increased height to accommodate five columns and three rows
        self.root.resizable(False, False)

        # Initialize image references
        self.original_image = None
        self.gray_image = None
        self.green_image = None
        self.red_image = None
        self.blue_image = None
        self.gray_no_g_image = None  # Fifth column

        self.gray_normalized = None
        self.green_normalized = None
        self.red_normalized = None
        self.blue_normalized = None
        self.gray_no_g_normalized = None  # Fifth column

        self.gray_custom = None
        self.green_custom = None
        self.red_custom = None
        self.blue_custom = None
        self.gray_no_g_custom = None  # Fifth column

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Load Image Button
        load_button = tk.Button(
            self.root,
            text="Load Image",
            command=self.load_image,
            bg="blue",
            fg="white",
            font=("Arial", 14),
            padx=10,
            pady=5
        )
        load_button.pack(pady=20)

        # Frame for threshold control and apply button
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Threshold Label
        threshold_label = tk.Label(control_frame, text="Contrast Stretch Threshold:", font=("Arial", 12))
        threshold_label.pack(side=tk.LEFT, padx=5)

        # Threshold Scale
        self.threshold_var = tk.IntVar(value=128)
        threshold_scale = tk.Scale(
            control_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            length=300,
            tickinterval=50,
            label="Threshold",
            font=("Arial", 10)
        )
        threshold_scale.pack(side=tk.LEFT, padx=5)

        # Apply Stretch Button
        apply_button = tk.Button(
            control_frame,
            text="Apply Custom Stretch",
            command=self.apply_custom_stretch,
            bg="green",
            fg="white",
            font=("Arial", 12),
            padx=10,
            pady=5
        )
        apply_button.pack(side=tk.LEFT, padx=10)

        # Frame to hold images
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)

        # Define the number of columns
        self.num_columns = 5

        # Titles for original processed images (including fifth column)
        original_titles = ["Grayscale", "Green Channel", "Red Channel", "Blue Channel", "Grayscale No Green"]
        # Titles for normalized images
        normalized_titles = ["Grayscale Normalized", "Green Normalized", "Red Normalized", "Blue Normalized", "Grayscale No Green Normalized"]
        # Titles for custom contrast stretched images
        custom_titles = ["Grayscale Custom Stretch", "Green Custom Stretch", "Red Custom Stretch", "Blue Custom Stretch", "Grayscale No Green Custom Stretch"]

        # Create labels for original images
        self.original_labels = []
        for i in range(self.num_columns):
            label = tk.Label(self.image_frame)
            label.grid(row=0, column=i, padx=10, pady=10)
            self.original_labels.append(label)

        # Create titles for original images
        for idx, title in enumerate(original_titles):
            title_label = tk.Label(self.image_frame, text=title, font=("Arial", 12))
            title_label.grid(row=1, column=idx, pady=(0, 10))

        # Create labels for normalized images
        self.normalized_labels = []
        for i in range(self.num_columns):
            label = tk.Label(self.image_frame)
            label.grid(row=2, column=i, padx=10, pady=10)
            self.normalized_labels.append(label)

        # Create titles for normalized images
        for idx, title in enumerate(normalized_titles):
            title_label = tk.Label(self.image_frame, text=title, font=("Arial", 12))
            title_label.grid(row=3, column=idx, pady=(0, 10))

        # Create labels for custom contrast stretched images
        self.custom_labels = []
        for i in range(self.num_columns):
            label = tk.Label(self.image_frame)
            label.grid(row=4, column=i, padx=10, pady=10)
            self.custom_labels.append(label)

        # Create titles for custom contrast stretched images
        for idx, title in enumerate(custom_titles):
            title_label = tk.Label(self.image_frame, text=title, font=("Arial", 12))
            title_label.grid(row=5, column=idx, pady=(0, 10))

    def load_image(self):
        # Open file dialog to select image
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        if not file_path:
            return  # User cancelled

        try:
            # Load original image
            self.original_image = Image.open(file_path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image.\n{e}")
            return

        # Process images
        self.process_images()

        # Display images
        self.display_images()

        # Reset custom stretched images
        self.reset_custom_stretched_images()

    def process_images(self):
        # Grayscale image
        self.gray_image = ImageOps.grayscale(self.original_image)

        # Extract Green channel as grayscale
        self.green_image = self.original_image.split()[1]  # Green channel

        # Extract Red channel as grayscale
        self.red_image = self.original_image.split()[0]    # Red channel

        # Extract Blue channel as grayscale
        self.blue_image = self.original_image.split()[2]   # Blue channel

        # Grayscale without green channel influence
        # Using custom coefficients: excluding green channel
        # The standard grayscale conversion uses (0.299, 0.587, 0.114)
        # To exclude green, set green coefficient to 0
        self.gray_no_g_image = self.original_image.convert(
            "L",
            (
                0.299,  # Red coefficient
                0.0,    # Green coefficient
                0.114,  # Blue coefficient
                0       # Offset
            )
        )

        # Normalize images using autocontrast (contrast stretching)
        self.gray_normalized = ImageOps.autocontrast(self.gray_image)
        self.green_normalized = ImageOps.autocontrast(self.green_image)
        self.red_normalized = ImageOps.autocontrast(self.red_image)
        self.blue_normalized = ImageOps.autocontrast(self.blue_image)
        self.gray_no_g_normalized = ImageOps.autocontrast(self.gray_no_g_image)

    def display_images(self):
        # Original processed images
        original_images = [
            self.gray_image,
            self.green_image,
            self.red_image,
            self.blue_image,
            self.gray_no_g_image
        ]
        for idx, img in enumerate(original_images):
            # Resize image to fit in the GUI
            img_resized = self.resize_image(img, 250, 300)
            photo = ImageTk.PhotoImage(img_resized)
            self.original_labels[idx].configure(image=photo)
            self.original_labels[idx].image = photo  # Keep a reference to avoid garbage collection

        # Normalized images
        normalized_images = [
            self.gray_normalized,
            self.green_normalized,
            self.red_normalized,
            self.blue_normalized,
            self.gray_no_g_normalized
        ]
        for idx, img in enumerate(normalized_images):
            # Resize image to fit in the GUI
            img_resized = self.resize_image(img, 250, 300)
            photo = ImageTk.PhotoImage(img_resized)
            self.normalized_labels[idx].configure(image=photo)
            self.normalized_labels[idx].image = photo  # Keep a reference to avoid garbage collection

    def reset_custom_stretched_images(self):
        """Clear the custom stretched images from the GUI."""
        for label in self.custom_labels:
            label.configure(image='')
            label.image = None

    def apply_custom_stretch(self):
        if not self.original_image:
            messagebox.showwarning("No Image Loaded", "Please load an image before applying custom stretch.")
            return

        threshold = self.threshold_var.get()

        # Apply custom contrast stretch to normalized images
        self.gray_custom = self.custom_contrast_stretch(self.gray_normalized, threshold)
        self.green_custom = self.custom_contrast_stretch(self.green_normalized, threshold)
        self.red_custom = self.custom_contrast_stretch(self.red_normalized, threshold)
        self.blue_custom = self.custom_contrast_stretch(self.blue_normalized, threshold)
        self.gray_no_g_custom = self.custom_contrast_stretch(self.gray_no_g_normalized, threshold)  # Fifth column

        # Display custom contrast stretched images
        self.display_custom_stretched_images()

    def custom_contrast_stretch(self, image, threshold):
        """Apply custom contrast stretch to an image based on the threshold."""
        if threshold >= 255:
            # All pixels become 0
            return image.point(lambda p: 0)
        elif threshold <= 0:
            # No change
            return image
        else:
            # Create a lookup table for contrast stretching
            lut = []
            for i in range(256):
                if i < threshold:
                    lut.append(0)
                else:
                    # Stretch the pixel value
                    stretched = int((i - threshold) * 255 / (255 - threshold))
                    # Ensure the stretched value does not exceed 255
                    stretched = min(stretched, 255)
                    lut.append(stretched)
            return image.point(lut)

    def display_custom_stretched_images(self):
        custom_images = [
            self.gray_custom,
            self.green_custom,
            self.red_custom,
            self.blue_custom,
            self.gray_no_g_custom
        ]
        for idx, img in enumerate(custom_images):
            # Resize image to fit in the GUI
            img_resized = self.resize_image(img, 250, 300)
            photo = ImageTk.PhotoImage(img_resized)
            self.custom_labels[idx].configure(image=photo)
            self.custom_labels[idx].image = photo  # Keep a reference to avoid garbage collection

    def resize_image(self, image, max_width, max_height):
        """Resize image while maintaining aspect ratio."""
        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
        
        # Determine the appropriate resampling filter based on Pillow version
        pillow_version = tuple(map(int, PILLOW_VERSION.split('.')[:2]))
        if pillow_version >= (10, 0):
            resample_filter = Image.Resampling.LANCZOS
        else:
            resample_filter = Image.ANTIALIAS

        return image.resize(new_size, resample=resample_filter)

def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
