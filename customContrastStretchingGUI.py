import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps, __version__ as PILLOW_VERSION

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fundus Image Processor")
        self.root.geometry("1400x900")  # Increased width for better layout
        self.root.minsize(1000, 700)

        # Initialize color palette
        self.colors = {
            "primary_bg": "#2e2e2e",       # Dark Gray
            "secondary_bg": "#3c3c3c",     # Slightly Lighter Gray
            "accent_blue": "#61afef",      # Soft Blue
            "accent_purple": "#c678dd",    # Soft Purple
            "green": "#98c379",            # Soft Green
            "red": "#e06c75",              # Soft Red
            "blue": "#61afef",             # Soft Blue (same as accent_blue for consistency)
            "purple": "#c678dd",           # Soft Purple for Grayscale No Green
            "text": "#ffffff",             # White
            "sub_text": "#abb2bf",         # Light Gray
            "warning": "#e06c75"           # Soft Red (same as "red" for consistency)
        }

        # Apply dark theme to root window
        self.root.configure(bg=self.colors["primary_bg"])

        # Configure styles for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern theme

        # Configure ttk styles for dark theme with color accents
        self.style.configure("TFrame", background=self.colors["primary_bg"])
        self.style.configure("TLabel", background=self.colors["primary_bg"], foreground=self.colors["text"])
        self.style.configure("TButton",
                             background=self.colors["accent_blue"],
                             foreground=self.colors["text"],
                             font=("Arial", 10, "bold"))
        self.style.map("TButton",
                       foreground=[('active', self.colors["text"])],
                       background=[('active', self.colors["accent_purple"])])
        
        self.style.configure("TScale", background=self.colors["primary_bg"])

        # Initialize image-related attributes
        self.original_image = None
        self.gray_image = None
        self.green_image = None
        self.red_image = None
        self.blue_image = None
        self.gray_no_g_image = None

        self.gray_normalized = None
        self.green_normalized = None
        self.red_normalized = None
        self.blue_normalized = None
        self.gray_no_g_normalized = None

        self.gray_custom = None
        self.green_custom = None
        self.red_custom = None
        self.blue_custom = None
        self.gray_no_g_custom = None

        self.all_labels = []
        self.fullscreen_window = None
        self.fullscreen_image = None

        self.image_titles = [
            "Grayscale",
            "Green Channel",
            "Red Channel",
            "Blue Channel",
            "Grayscale No Green",
            "Grayscale Normalized",
            "Green Normalized",
            "Red Normalized",
            "Blue Normalized",
            "Grayscale No Green Normalized",
            "Grayscale Custom Stretch",
            "Green Custom Stretch",
            "Red Custom Stretch",
            "Blue Custom Stretch",
            "Grayscale No Green Custom Stretch"
        ]

        self.current_red_coeff = 0.500
        self.current_blue_coeff = 0.500

        self.num_columns = 5  # Define number of columns before setup_ui
        self.setup_ui()

    def setup_ui(self):
        # Configure grid weights for scalability
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)  # Image display is in row=2, allow row=3 to expand

        # Top Frame: Load Button, Indicator, Sliders on the Right
        top_frame = ttk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(0, weight=1)  # Left side (load button and indicator)
        top_frame.columnconfigure(1, weight=0)  # Right side (sliders)

        # Left Side of Top Frame
        left_top_frame = ttk.Frame(top_frame)
        left_top_frame.grid(row=0, column=0, sticky="w")

        load_button = ttk.Button(left_top_frame, text="Load Image", command=self.load_image)
        load_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        indicator_label = ttk.Label(
            left_top_frame,
            text="Left-click to view full-screen. Right-click to save image.",
            font=("Arial", 10),
            foreground=self.colors["sub_text"]
        )
        indicator_label.grid(row=0, column=1, padx=20, pady=5, sticky="w")

        # Right Side of Top Frame: Sliders
        sliders_frame = ttk.Frame(top_frame)
        sliders_frame.grid(row=0, column=1, padx=20, pady=5, sticky="e")
        sliders_frame.columnconfigure(3, weight=0)  # Column for value labels

        # Red Coefficient Slider
        red_label = ttk.Label(sliders_frame, text="Red Coefficient:", font=("Arial", 10))
        red_label.grid(row=0, column=0, sticky="w")
        self.red_scale = ttk.Scale(
            sliders_frame,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            command=self.update_grayscale_no_g,
            length=200
        )
        self.red_scale.set(int(self.current_red_coeff * 1000))
        self.red_scale.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.red_value_label = ttk.Label(sliders_frame, text=f"{self.red_scale.get():.0f}", font=("Arial", 10), foreground=self.colors["red"])
        self.red_value_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Blue Coefficient Slider
        blue_label = ttk.Label(sliders_frame, text="Blue Coefficient:", font=("Arial", 10))
        blue_label.grid(row=1, column=0, sticky="w")
        self.blue_scale = ttk.Scale(
            sliders_frame,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            command=self.update_grayscale_no_g,
            length=200
        )
        self.blue_scale.set(int(self.current_blue_coeff * 1000))
        self.blue_scale.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.blue_value_label = ttk.Label(sliders_frame, text=f"{self.blue_scale.get():.0f}", font=("Arial", 10), foreground=self.colors["blue"])
        self.blue_value_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Warning Label with fixed row height to prevent layout shift
        self.warning_label = ttk.Label(sliders_frame, text="", font=("Arial", 10), foreground=self.colors["warning"])
        self.warning_label.grid(row=2, column=0, columnspan=3, pady=(0, 0), sticky="w")
        self.warning_label.configure(anchor='w')  # Align text to the left

        # Control Frame: Contrast Stretch Threshold
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        control_frame.columnconfigure(2, weight=0)  # Column for value label

        threshold_label = ttk.Label(control_frame, text="Contrast Stretch Threshold:", font=("Arial", 10))
        threshold_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.threshold_var = tk.IntVar(value=128)
        threshold_scale = ttk.Scale(
            control_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            command=self.apply_custom_stretch,
            length=300
        )
        threshold_scale.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.threshold_value_label = ttk.Label(control_frame, text=f"{self.threshold_var.get()}", font=("Arial", 10), foreground=self.colors["accent_purple"])
        self.threshold_value_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Image Display Frame
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.image_frame.columnconfigure(tuple(range(self.num_columns)), weight=1)
        for r in range(6):  # 3 stages x 2 (title + image)
            self.image_frame.rowconfigure(r, weight=1)

        # Titles for image columns
        original_titles = [
            "Grayscale",
            "Green Channel",
            "Red Channel",
            "Blue Channel",
            "Grayscale No Green"
        ]
        normalized_titles = [
            "Grayscale Normalized",
            "Green Normalized",
            "Red Normalized",
            "Blue Normalized",
            "Grayscale No Green Normalized"
        ]
        custom_titles = [
            "Grayscale Custom Stretch",
            "Green Custom Stretch",
            "Red Custom Stretch",
            "Blue Custom Stretch",
            "Grayscale No Green Custom Stretch"
        ]

        # Add titles with color-coded text
        for col, title in enumerate(original_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(self.image_frame, text=title, font=("Arial", 10, "bold"), foreground=fg_color)
            title_label.grid(row=0, column=col, padx=5, pady=5)

        for col, title in enumerate(normalized_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(self.image_frame, text=title, font=("Arial", 10, "bold"), foreground=fg_color)
            title_label.grid(row=2, column=col, padx=5, pady=5)

        for col, title in enumerate(custom_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(self.image_frame, text=title, font=("Arial", 10, "bold"), foreground=fg_color)
            title_label.grid(row=4, column=col, padx=5, pady=5)

        # Create image labels using tk.Label for better alignment control
        for row in [1, 3, 5]:
            for col in range(self.num_columns):
                label = tk.Label(self.image_frame, relief="solid", anchor='center', bg=self.colors["secondary_bg"], bd=2, highlightthickness=0)
                label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.all_labels.append(label)

    def get_title_color(self, title):
        """
        Determine the color of the title based on its text.
        """
        if "Grayscale No Green" in title:
            return self.colors["purple"]
        elif "Green" in title:
            return self.colors["green"]
        elif "Red" in title:
            return self.colors["red"]
        elif "Blue" in title:
            return self.colors["blue"]
        else:
            return self.colors["text"]

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        if not file_path:
            return

        try:
            self.original_image = Image.open(file_path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image.\n{e}")
            return

        self.process_images()
        self.display_images()
        self.update_warning_label()
        self.apply_custom_stretch()

    def process_images(self):
        self.gray_image = ImageOps.grayscale(self.original_image)
        self.green_image = self.original_image.split()[1]
        self.red_image = self.original_image.split()[0]
        self.blue_image = self.original_image.split()[2]
        self.gray_no_g_image = self.original_image.convert(
            "L",
            (
                self.current_red_coeff,
                0.0,
                self.current_blue_coeff,
                0
            )
        )
        self.gray_normalized = ImageOps.autocontrast(self.gray_image)
        self.green_normalized = ImageOps.autocontrast(self.green_image)
        self.red_normalized = ImageOps.autocontrast(self.red_image)
        self.blue_normalized = ImageOps.autocontrast(self.blue_image)
        self.gray_no_g_normalized = ImageOps.autocontrast(self.gray_no_g_image)

    def display_images(self):
        original_images = [
            self.gray_image,
            self.green_image,
            self.red_image,
            self.blue_image,
            self.gray_no_g_image
        ]
        normalized_images = [
            self.gray_normalized,
            self.green_normalized,
            self.red_normalized,
            self.blue_normalized,
            self.gray_no_g_normalized
        ]
        self.all_images = original_images + normalized_images
        for idx, img in enumerate(self.all_images):
            img_resized = self.resize_image(img, 250, 250)
            photo = ImageTk.PhotoImage(img_resized)
            self.all_labels[idx].configure(image=photo)
            self.all_labels[idx].image = photo  # Prevent garbage collection
            self.all_labels[idx].bind("<Button-1>", lambda e, im=img: self.show_fullscreen(im))
            self.all_labels[idx].bind("<Button-3>", lambda e, im=img, idx=idx: self.save_image(im, idx))

    def apply_custom_stretch(self, event=None):
        if not self.original_image:
            return

        threshold = self.threshold_var.get()
        self.threshold_value_label.config(text=f"{threshold}")
        self.gray_custom = self.custom_contrast_stretch(self.gray_normalized, threshold)
        self.green_custom = self.custom_contrast_stretch(self.green_normalized, threshold)
        self.red_custom = self.custom_contrast_stretch(self.red_normalized, threshold)
        self.blue_custom = self.custom_contrast_stretch(self.blue_normalized, threshold)
        self.gray_no_g_custom = self.custom_contrast_stretch(self.gray_no_g_normalized, threshold)
        self.custom_images = [
            self.gray_custom,
            self.green_custom,
            self.red_custom,
            self.blue_custom,
            self.gray_no_g_custom
        ]
        self.display_custom_stretched_images()

    def custom_contrast_stretch(self, image, threshold):
        if threshold >= 255:
            return image.point(lambda p: 0)
        elif threshold <= 0:
            return image
        else:
            lut = [0 if i < threshold else min(int((i - threshold) * 255 / (255 - threshold)), 255) for i in range(256)]
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
            img_resized = self.resize_image(img, 250, 250)
            photo = ImageTk.PhotoImage(img_resized)
            label_idx = self.num_columns*2 + idx  # Custom images start after original and normalized
            self.all_labels[label_idx].configure(image=photo)
            self.all_labels[label_idx].image = photo  # Prevent garbage collection
            self.all_labels[label_idx].bind("<Button-1>", lambda e, im=img: self.show_fullscreen(im))
            self.all_labels[label_idx].bind("<Button-3>", lambda e, im=img, idx=label_idx: self.save_image(im, idx))

    def update_grayscale_no_g(self, event=None):
        if not self.original_image:
            return

        red_val = self.red_scale.get() / 1000
        blue_val = self.blue_scale.get() / 1000
        self.current_red_coeff = red_val
        self.current_blue_coeff = blue_val
        self.gray_no_g_image = self.original_image.convert(
            "L",
            (
                self.current_red_coeff,
                0.0,
                self.current_blue_coeff,
                0
            )
        )
        self.gray_no_g_normalized = ImageOps.autocontrast(self.gray_no_g_image)
        threshold = self.threshold_var.get()
        self.gray_no_g_custom = self.custom_contrast_stretch(self.gray_no_g_normalized, threshold)

        # Update Red and Blue value labels with appropriate colors
        self.red_value_label.config(text=f"{self.red_scale.get():.0f}", foreground=self.colors["red"])
        self.blue_value_label.config(text=f"{self.blue_scale.get():.0f}", foreground=self.colors["blue"])

        # Update "Grayscale No Green" original image
        img_resized = self.resize_image(self.gray_no_g_image, 250, 250)
        photo = ImageTk.PhotoImage(img_resized)
        label = self.all_labels[4]
        label.configure(image=photo)
        label.image = photo
        label.bind("<Button-1>", lambda e, im=self.gray_no_g_image: self.show_fullscreen(im))
        label.bind("<Button-3>", lambda e, im=self.gray_no_g_image, idx=4: self.save_image(im, idx))

        # Update "Grayscale No Green Normalized" image
        img_resized_norm = self.resize_image(self.gray_no_g_normalized, 250, 250)
        photo_norm = ImageTk.PhotoImage(img_resized_norm)
        label_norm = self.all_labels[self.num_columns + 4]
        label_norm.configure(image=photo_norm)
        label_norm.image = photo_norm
        label_norm.bind("<Button-1>", lambda e, im=self.gray_no_g_normalized: self.show_fullscreen(im))
        label_norm.bind("<Button-3>", lambda e, im=self.gray_no_g_normalized, idx=self.num_columns + 4: self.save_image(im, self.num_columns + 4))

        # Update "Grayscale No Green Custom Stretch" image
        img_resized_custom = self.resize_image(self.gray_no_g_custom, 250, 250)
        photo_custom = ImageTk.PhotoImage(img_resized_custom)
        label_custom = self.all_labels[2 * self.num_columns + 4]
        label_custom.configure(image=photo_custom)
        label_custom.image = photo_custom
        label_custom.bind("<Button-1>", lambda e, im=self.gray_no_g_custom: self.show_fullscreen(im))
        label_custom.bind("<Button-3>", lambda e, im=self.gray_no_g_custom, idx=2 * self.num_columns + 4: self.save_image(im, 2 * self.num_columns + 4))

        self.update_warning_label()
        self.apply_custom_stretch()

    def update_warning_label(self):
        total = self.red_scale.get() + self.blue_scale.get()
        if total > 1000:
            self.warning_label.config(text="Warning: Red + Blue coefficients exceed 1000!")
        else:
            self.warning_label.config(text="")  # Empty string keeps the label's height consistent

    def show_fullscreen(self, image):
        if self.fullscreen_window and self.fullscreen_image == image:
            self.close_fullscreen()
            return
        if self.fullscreen_window:
            self.close_fullscreen()
        self.fullscreen_window = tk.Toplevel(self.root)
        self.fullscreen_window.attributes("-fullscreen", True)
        self.fullscreen_window.configure(background='black')
        self.fullscreen_window.bind("<Button-1>", lambda e: self.close_fullscreen())
        screen_width = self.fullscreen_window.winfo_screenwidth()
        screen_height = self.fullscreen_window.winfo_screenheight()
        img_width, img_height = image.size
        ratio = min(screen_width / img_width, screen_height / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        img_resized = image.resize(new_size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img_resized)
        label = tk.Label(self.fullscreen_window, image=photo, background='black', anchor='center')
        label.image = photo
        label.pack(expand=True)
        self.fullscreen_image = image

    def close_fullscreen(self):
        if self.fullscreen_window:
            self.fullscreen_window.destroy()
            self.fullscreen_window = None
            self.fullscreen_image = None

    def save_image(self, image, idx):
        title = self.image_titles[idx]
        if idx in [4, self.num_columns + 4, 2 * self.num_columns + 4]:
            red = f"{self.current_red_coeff:.3f}"
            blue = f"{self.current_blue_coeff:.3f}"
            default_name = f"{title}_R{red}_B{blue}.png"
        else:
            default_name = f"{title}.png"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg;*.jpeg"),
                ("BMP Image", "*.bmp"),
                ("TIFF Image", "*.tif;*.tiff")
            ]
        )
        if file_path:
            try:
                image.save(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image.\n{e}")

    def resize_image(self, image, max_width, max_height):
        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
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
