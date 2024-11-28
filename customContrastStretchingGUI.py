import tkinter as tk 
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps, __version__ as PILLOW_VERSION
import logging
import os
import sys

# Configure logging to record app events and errors
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class ImageProcessorApp:
    """Main application class for the Image Processor GUI."""
    def __init__(self, root):
        """Initialize the main window and set up the UI."""
        self.root = root
        self.root.title("Custom Contrast Stretching GUI by github.com/kaanaldemir")
        self.root.geometry("1275x980")
        self.root.minsize(1275, 980)
        
        # Attempt to set the window icon
        try:
            if getattr(sys, 'frozen', False):
                script_dir = sys._MEIPASS
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(script_dir, "cstretch.ico")

            if not os.path.exists(icon_path):
                raise FileNotFoundError(f"Icon file not found at: {icon_path}")

            icon_image = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(False, icon_photo)
            self.root.icon_photo = icon_photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            logging.warning(f"Failed to set window icon: {e}")

        # Define color scheme for the UI
        self.colors = {
            "primary_bg": "#2e2e2e",
            "secondary_bg": "#3c3c3c",
            "accent_blue": "#61afef",
            "accent_purple": "#c678dd",
            "green": "#98c379",
            "red": "#e06c75",
            "blue": "#61afef",
            "purple": "#c678dd",
            "text": "#ffffff",
            "sub_text": "#abb2bf",
            "warning": "#e06c75"
        }

        self.root.configure(bg=self.colors["primary_bg"])

        # Set up the style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use 'clam' theme for better customization

        # Configure styles for various ttk widgets
        self.style.configure("TFrame", background=self.colors["primary_bg"])
        self.style.configure("TLabel", background=self.colors["primary_bg"], foreground=self.colors["text"])
        self.style.configure("TButton",
                             background=self.colors["primary_bg"],
                             foreground=self.colors["sub_text"],
                             font=("Arial", 10, "bold"))
        self.style.map("TButton",
                       foreground=[('active', self.colors["secondary_bg"])],
                       background=[('active', self.colors["sub_text"])])
        
        self.style.configure("TScale", background=self.colors["primary_bg"])

        # Custom style for checkboxes
        self.style.configure("InverseClip.TCheckbutton",
                             foreground=self.colors["text"],
                             background=self.colors["secondary_bg"],
                             font=("Arial", 10))
        self.style.map("InverseClip.TCheckbutton",
                       foreground=[('active', self.colors["text"]),
                                  ('disabled', self.colors["sub_text"])],
                       background=[('active', self.colors["secondary_bg"]),
                                   ('disabled', self.colors["primary_bg"])],
                       indicatorcolor=[('active', self.colors["accent_purple"]),
                                      ('disabled', self.colors["sub_text"])])

        # Initialize image-related variables
        self.original_image_loaded = None
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

        self.all_labels = []  # List to hold image labels
        self.fullscreen_window = None  # Reference to fullscreen window
        self.fullscreen_image = None  # Currently displayed fullscreen image

        # Titles for different image views
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

        # Initial coefficients for red and blue channels
        self.current_red_coeff = 0.500
        self.current_blue_coeff = 0.500

        self.num_columns = 5  # Number of image columns in the UI

        # Variable to track if the image should be inverted before processing
        self.invert_before_var = tk.BooleanVar(value=False)

        self.preview_label = None  # Label to show image preview

        self.image_list = []  # List of image file paths in the current folder
        self.current_image_index = -1  # Index of the currently displayed image

        self.setup_ui()  # Set up the user interface

    def setup_ui(self):
        """Set up all the UI components in the main window."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        # Top frame for controls and preview
        top_frame = ttk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        for col in range(self.num_columns):
            top_frame.columnconfigure(col, weight=1)

        # Frame for control buttons
        controls_frame = ttk.Frame(top_frame)
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="w")

        # Checkbox to invert the image before processing
        self.invert_before_checkbox = ttk.Checkbutton(
            controls_frame,
            text="Invert Image",
            variable=self.invert_before_var,
            command=self.on_invert_checkbox_toggle,
            style='InverseClip.TCheckbutton'
        )
        self.invert_before_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Button to load an image
        load_button = ttk.Button(controls_frame, text="Load Image", command=self.load_image)
        load_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Instruction label for user actions
        indicator_label = ttk.Label(
            controls_frame,
            text="Left-click to view full-screen.\nRight-click to save image.",
            font=("Arial", 10),
            foreground=self.colors["sub_text"]
        )
        indicator_label.grid(row=0, column=2, padx=35, pady=5, sticky="w")

        # Container for image preview and navigation buttons
        preview_container = ttk.Frame(top_frame)
        preview_container.grid(row=0, column=2, sticky="n")
        preview_container.columnconfigure(1, weight=1)
        preview_container.rowconfigure(0, weight=1)

        # Button to navigate to the previous image
        self.left_arrow_button = ttk.Button(
            preview_container,
            text="◀",
            command=self.show_previous_image,
            style='TButton',
            width=2
        )
        self.left_arrow_button.grid(row=0, column=0, padx=(0, 5))
        self.left_arrow_button.grid_remove()  # Hide initially

        # Label to display image preview
        self.preview_label = tk.Label(
            preview_container,
            relief="solid",
            bg=self.colors["secondary_bg"],
            bd=2,
            highlightthickness=0
        )
        self.preview_label.grid(row=0, column=1)
        self.preview_label.bind("<Button-1>", self.on_preview_left_click)
        self.preview_label.grid_remove()  # Hide initially

        # Button to navigate to the next image
        self.right_arrow_button = ttk.Button(
            preview_container,
            text="▶",
            command=self.show_next_image,
            style='TButton',
            width=2
        )
        self.right_arrow_button.grid(row=0, column=2, padx=(5, 0))
        self.right_arrow_button.grid_remove()  # Hide initially

        # Frame for sliders controlling red and blue coefficients
        sliders_frame = ttk.Frame(top_frame)
        sliders_frame.grid(row=0, column=3, columnspan=2, padx=20, pady=5, sticky="e")
        sliders_frame.columnconfigure(4, weight=0)

        # Label and slider for Red Coefficient
        red_label = ttk.Label(sliders_frame, text="Red Coefficient:", font=("Arial", 10))
        red_label.grid(row=0, column=0, sticky="w")

        self.red_var = tk.DoubleVar(value=0.5)
        self.red_var.trace_add("write", self.update_red_label)

        self.red_scale = tk.Scale(
            sliders_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.red_var,
            resolution=0.05,
            command=lambda val: self.update_grayscale_no_g(),
            length=200,
            showvalue=0,
            background=self.colors["secondary_bg"],
            troughcolor=self.colors["red"],
            highlightthickness=0,
            borderwidth=0,
            state='disabled'  # Disabled until an image is loaded
        )
        self.red_scale.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Label to show the current value of the Red Coefficient
        self.red_value_label = ttk.Label(
            sliders_frame,
            text=f"{self.red_var.get():.2f}",
            font=("Arial", 10),
            foreground=self.colors["red"],
            width=6,
            anchor='center'
        )
        self.red_value_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Label and slider for Blue Coefficient
        blue_label = ttk.Label(sliders_frame, text="Blue Coefficient:", font=("Arial", 10))
        blue_label.grid(row=1, column=0, sticky="w")

        self.blue_var = tk.DoubleVar(value=0.5)
        self.blue_var.trace_add("write", self.update_blue_label)

        self.blue_scale = tk.Scale(
            sliders_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.blue_var,
            resolution=0.05,
            command=lambda val: self.update_grayscale_no_g(),
            length=200,
            showvalue=0,
            background=self.colors["secondary_bg"],
            troughcolor=self.colors["blue"],
            highlightthickness=0,
            borderwidth=0,
            state='disabled'  # Disabled until an image is loaded
        )
        self.blue_scale.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Label to show the current value of the Blue Coefficient
        self.blue_value_label = ttk.Label(
            sliders_frame,
            text=f"{self.blue_var.get():.2f}",
            font=("Arial", 10),
            foreground=self.colors["blue"],
            width=6,
            anchor='center'
        )
        self.blue_value_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Button to reset red and blue coefficients to default
        self.reset_coefficients_button = tk.Button(
            sliders_frame,
            text="⟳",
            command=self.reset_coefficients,
            width=2,
            height=1,
            state='disabled',  # Disabled until an image is loaded
            bg=self.colors["secondary_bg"],
            fg=self.colors["text"],
            relief='flat'
        )
        self.reset_coefficients_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Label to display warnings related to coefficient values
        self.warning_label = ttk.Label(
            sliders_frame,
            text="",
            font=("Arial", 10),
            foreground=self.colors["warning"]
        )
        self.warning_label.grid(row=2, column=0, columnspan=4, pady=(0, 0), sticky="w")
        self.warning_label.configure(anchor='w')

        # Frame for threshold controls
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        for i in range(8):
            control_frame.columnconfigure(i, weight=0)

        # Label and slider for Lower Threshold
        lower_threshold_label = ttk.Label(control_frame, text="Lower Threshold:", font=("Arial", 10))
        lower_threshold_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.lower_threshold_var = tk.IntVar(value=128)
        self.lower_threshold_var.trace_add("write", self.update_lower_threshold_label)

        self.lower_threshold_scale = tk.Scale(
            control_frame,
            from_=0,
            to=254,
            orient=tk.HORIZONTAL,
            variable=self.lower_threshold_var,
            resolution=1,
            command=lambda val: self.apply_custom_stretch(),
            length=300,
            showvalue=0,
            background=self.colors["secondary_bg"],
            troughcolor=self.colors["sub_text"],
            highlightthickness=0,
            borderwidth=0,
            state='disabled'  # Disabled until an image is loaded
        )
        self.lower_threshold_scale.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Label to show the current value of the Lower Threshold
        self.lower_threshold_value_label = ttk.Label(
            control_frame,
            text=f"{self.lower_threshold_var.get()}",
            font=("Arial", 10),
            foreground=self.colors["sub_text"],
            width=6,
            anchor='center'
        )
        self.lower_threshold_value_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Checkbox to inverse the lower clip behavior
        self.inverse_lower_clip_var = tk.BooleanVar(value=False)
        self.inverse_lower_clip_checkbox = ttk.Checkbutton(
            control_frame,
            text="Inverse Clip",
            variable=self.inverse_lower_clip_var,
            command=self.apply_custom_stretch,
            style='InverseClip.TCheckbutton',
            state='disabled'  # Disabled until an image is loaded
        )
        self.inverse_lower_clip_checkbox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Label and slider for Upper Threshold
        upper_threshold_label = ttk.Label(control_frame, text="Upper Threshold:", font=("Arial", 10))
        upper_threshold_label.grid(row=0, column=4, padx=20, pady=5, sticky="w")
        self.upper_threshold_var = tk.IntVar(value=255)
        self.upper_threshold_var.trace_add("write", self.update_upper_threshold_label)

        self.upper_threshold_scale = tk.Scale(
            control_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.upper_threshold_var,
            resolution=1,
            command=lambda val: self.apply_custom_stretch(),
            length=300,
            showvalue=0,
            background=self.colors["secondary_bg"],
            troughcolor=self.colors["sub_text"],
            highlightthickness=0,
            borderwidth=0,
            state='disabled'  # Disabled until an image is loaded
        )
        self.upper_threshold_scale.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Label to show the current value of the Upper Threshold
        self.upper_threshold_value_label = ttk.Label(
            control_frame,
            text=f"{self.upper_threshold_var.get()}",
            font=("Arial", 10),
            foreground=self.colors["sub_text"],
            width=6,
            anchor='center'
        )
        self.upper_threshold_value_label.grid(row=0, column=6, padx=5, pady=5, sticky="w")

        # Checkbox to inverse the upper clip behavior
        self.inverse_upper_clip_var = tk.BooleanVar(value=False)
        self.inverse_upper_clip_checkbox = ttk.Checkbutton(
            control_frame,
            text="Inverse Clip",
            variable=self.inverse_upper_clip_var,
            command=self.apply_custom_stretch,
            style='InverseClip.TCheckbutton',
            state='disabled'  # Disabled until an image is loaded
        )
        self.inverse_upper_clip_checkbox.grid(row=0, column=7, padx=5, pady=5, sticky="w")

        # Button to reset threshold values to defaults
        self.reset_thresholds_button = tk.Button(
            control_frame,
            text="⟳",
            command=self.reset_thresholds,
            width=2,
            height=1,
            state='disabled',  # Disabled until an image is loaded
            bg=self.colors["secondary_bg"],
            fg=self.colors["text"],
            relief='flat'
        )
        self.reset_thresholds_button.grid(row=0, column=8, padx=25, pady=5, sticky="w")

        # Status bar to display messages to the user
        self.status_bar = ttk.Label(
            self.root,
            text="Welcome to Image Processor",
            anchor='w',
            background=self.colors["secondary_bg"],
            foreground=self.colors["sub_text"]
        )
        self.status_bar.grid(row=4, column=0, sticky="ew")

        # Frame to hold all the image displays
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.image_frame.columnconfigure(tuple(range(self.num_columns)), weight=1)
        for r in range(6):
            self.image_frame.rowconfigure(r, weight=1)

        # Titles for different sets of images
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

        # Add title labels for original images
        for col, title in enumerate(original_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(
                self.image_frame,
                text=title,
                font=("Arial", 10, "bold"),
                foreground=fg_color
            )
            title_label.grid(row=0, column=col, padx=5, pady=5)

        # Add title labels for normalized images
        for col, title in enumerate(normalized_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(
                self.image_frame,
                text=title,
                font=("Arial", 10, "bold"),
                foreground=fg_color
            )
            title_label.grid(row=2, column=col, padx=5, pady=5)

        # Add title labels for custom stretched images
        for col, title in enumerate(custom_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(
                self.image_frame,
                text=title,
                font=("Arial", 10, "bold"),
                foreground=fg_color
            )
            title_label.grid(row=4, column=col, padx=5, pady=5)

        # Create placeholders for image thumbnails
        for row in [1, 3, 5]:
            for col in range(self.num_columns):
                label = tk.Label(
                    self.image_frame,
                    relief="solid",
                    anchor='center',
                    bg=self.colors["secondary_bg"],
                    bd=2,
                    highlightthickness=0
                )
                label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.all_labels.append(label)

        # Add tooltips to various UI elements for better user experience
        self.add_tooltips()

    def get_title_color(self, title):
        """Determine the color of the title based on the image type."""
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

    def update_red_label(self, *args):
        """Update the red coefficient label when the slider value changes."""
        self.red_value_label.config(text=f"{self.red_var.get():.2f}")

    def update_blue_label(self, *args):
        """Update the blue coefficient label when the slider value changes."""
        self.blue_value_label.config(text=f"{self.blue_var.get():.2f}")

    def update_lower_threshold_label(self, *args):
        """Update the lower threshold label when the slider value changes."""
        self.lower_threshold_value_label.config(text=f"{self.lower_threshold_var.get()}")

    def update_upper_threshold_label(self, *args):
        """Update the upper threshold label when the slider value changes."""
        self.upper_threshold_value_label.config(text=f"{self.upper_threshold_var.get()}")

    def load_image(self):
        """Handle the loading of an image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        if not file_path:
            return  # User canceled the file dialog

        try:
            # Open the selected image and convert it to RGB
            self.original_image_loaded = Image.open(file_path).convert("RGB")

            if self.invert_before_var.get():
                # Invert the image colors if the checkbox is selected
                self.original_image = ImageOps.invert(self.original_image_loaded)
                self.status_bar.config(text=f"Loaded and inverted image: {file_path}")
                logging.info(f"Loaded and inverted image: {file_path}")
            else:
                self.original_image = self.original_image_loaded
                self.status_bar.config(text=f"Loaded image: {file_path}")
                logging.info(f"Loaded image: {file_path}")
        except Exception as e:
            # Show an error message if the image fails to load
            messagebox.showerror("Error", f"Failed to load image.\n{e}")
            logging.error(f"Failed to load image: {file_path} with error: {e}")
            return

        # Get the folder containing the image and list all supported image files
        folder = os.path.dirname(file_path)
        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
        self.image_list = sorted([
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(supported_extensions)
        ])
        try:
            # Set the current image index based on the loaded image
            self.current_image_index = self.image_list.index(file_path)
        except ValueError:
            self.current_image_index = -1  # Image not found in the list

        self.enable_widgets()  # Enable UI widgets now that an image is loaded

        self.process_images()  # Process the loaded image
        self.display_images()  # Display all processed images
        self.update_warning_label()  # Update any warning messages
        self.apply_custom_stretch()  # Apply custom contrast stretching

        self.update_preview_label()  # Update the preview thumbnail

        self.update_navigation_arrows()  # Update navigation buttons visibility

    def enable_widgets(self):
        """Enable UI widgets that were disabled until an image was loaded."""
        self.red_scale.config(state='normal')
        self.blue_scale.config(state='normal')
        self.lower_threshold_scale.config(state='normal')
        self.upper_threshold_scale.config(state='normal')

        self.inverse_lower_clip_checkbox.config(state='normal')
        self.inverse_upper_clip_checkbox.config(state='normal')

        self.reset_thresholds_button.config(state='normal')
        self.reset_coefficients_button.config(state='normal')

    def on_invert_checkbox_toggle(self):
        """Handle the event when the invert image checkbox is toggled."""
        if not self.original_image_loaded:
            return  # No image loaded yet

        try:
            if self.invert_before_var.get():
                # Invert the image if checkbox is selected
                self.original_image = ImageOps.invert(self.original_image_loaded)
                self.status_bar.config(text="Image inverted before processing.")
                logging.info("Image inverted before processing.")
            else:
                # Use the original image without inversion
                self.original_image = self.original_image_loaded
                self.status_bar.config(text="Image loaded without inversion.")
                logging.info("Image loaded without inversion.")

            # Re-process and display images after inversion toggle
            self.process_images()
            self.display_images()
            self.update_warning_label()
            self.apply_custom_stretch()
        except Exception as e:
            # Show an error message if inversion fails
            messagebox.showerror("Error", f"Failed to invert image.\n{e}")
            logging.error(f"Failed to invert image with error: {e}")

    def process_images(self):
        """Process the original image into various channels and apply normalization."""
        self.gray_image = ImageOps.grayscale(self.original_image)  # Convert to grayscale
        self.green_image = self.original_image.split()[1]  # Extract green channel
        self.red_image = self.original_image.split()[0]    # Extract red channel
        self.blue_image = self.original_image.split()[2]   # Extract blue channel
        self.gray_no_g_image = self.original_image.convert(
            "L",
            (
                self.current_red_coeff,
                0.0,
                self.current_blue_coeff,
                0
            )
        )  # Grayscale without green channel

        # Apply autocontrast normalization to each channel
        self.gray_normalized = ImageOps.autocontrast(self.gray_image)
        self.green_normalized = ImageOps.autocontrast(self.green_image)
        self.red_normalized = ImageOps.autocontrast(self.red_image)
        self.blue_normalized = ImageOps.autocontrast(self.blue_image)
        self.gray_no_g_normalized = ImageOps.autocontrast(self.gray_no_g_image)

    def display_images(self):
        """Display all processed images in the UI."""
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
        self.all_images = original_images + normalized_images  # Combine all images for display

        for idx, img in enumerate(self.all_images):
            img_resized = self.resize_image(img, 250, 250)  # Resize for thumbnail
            photo = ImageTk.PhotoImage(img_resized)
            self.all_labels[idx].configure(image=photo)
            self.all_labels[idx].image = photo  # Keep a reference to prevent garbage collection

            # Bind left-click to view full-screen and right-click to save the image
            self.all_labels[idx].bind("<Button-1>", lambda e, im=img: self.show_fullscreen(im))
            self.all_labels[idx].bind("<Button-3>", lambda e, im=img, idx=idx: self.save_image(im, idx))

    def apply_custom_stretch(self, event=None):
        """Apply custom contrast stretching based on user-defined thresholds."""
        if not self.original_image:
            return  # No image to process

        lower = self.lower_threshold_var.get()
        upper = self.upper_threshold_var.get()
        inverse_lower = self.inverse_lower_clip_var.get()
        inverse_upper = self.inverse_upper_clip_var.get()

        # Ensure that upper threshold is greater than lower threshold
        if lower >= upper:
            upper = min(lower + 1, 255)
            self.upper_threshold_var.set(upper)
            self.upper_threshold_value_label.config(text=f"{upper}")
            self.status_bar.config(text="Upper Threshold adjusted to be at least one higher than Lower Threshold.")
            logging.warning("Upper Threshold was less than or equal to Lower Threshold. Adjusted Upper Threshold to be at least one higher.")
        else:
            self.status_bar.config(text="Applying custom contrast stretch.")

        # Apply custom contrast stretching to each normalized image
        self.gray_custom = self.custom_contrast_stretch(
            self.gray_normalized, lower, upper, inverse_lower, inverse_upper
        )
        self.green_custom = self.custom_contrast_stretch(
            self.green_normalized, lower, upper, inverse_lower, inverse_upper
        )
        self.red_custom = self.custom_contrast_stretch(
            self.red_normalized, lower, upper, inverse_lower, inverse_upper
        )
        self.blue_custom = self.custom_contrast_stretch(
            self.blue_normalized, lower, upper, inverse_lower, inverse_upper
        )
        self.gray_no_g_custom = self.custom_contrast_stretch(
            self.gray_no_g_normalized, lower, upper, inverse_lower, inverse_upper
        )
        self.custom_images = [
            self.gray_custom,
            self.green_custom,
            self.red_custom,
            self.blue_custom,
            self.gray_no_g_custom
        ]
        self.display_custom_stretched_images()  # Update the display with stretched images

    def custom_contrast_stretch(self, image, lower_threshold, upper_threshold, inverse_lower, inverse_upper):
        """
        Apply a custom contrast stretch to the image based on thresholds.
        
        Parameters:
            image (PIL.Image): The image to process.
            lower_threshold (int): The lower threshold value.
            upper_threshold (int): The upper threshold value.
            inverse_lower (bool): Whether to invert the lower clipping.
            inverse_upper (bool): Whether to invert the upper clipping.
        
        Returns:
            PIL.Image: The contrast-stretched image.
        """
        if upper_threshold == lower_threshold:
            if inverse_lower:
                return image.point(lambda p: 255 if p >= lower_threshold else 0)
            else:
                return image.point(lambda p: 0 if p < lower_threshold else 255)
        elif upper_threshold < lower_threshold:
            lower_threshold, upper_threshold = upper_threshold, lower_threshold

        # Create a lookup table for mapping pixel values
        lut = []
        for i in range(256):
            if i < lower_threshold:
                lut.append(255 if inverse_lower else 0)
            elif i > upper_threshold:
                lut.append(0 if inverse_upper else 255)
            else:
                scaled = int((i - lower_threshold) * 255 / (upper_threshold - lower_threshold))
                lut.append(scaled)
        return image.point(lut)

    def display_custom_stretched_images(self):
        """Display the custom contrast-stretched images in the UI."""
        custom_images = [
            self.gray_custom,
            self.green_custom,
            self.red_custom,
            self.blue_custom,
            self.gray_no_g_custom
        ]
        for idx, img in enumerate(custom_images):
            img_resized = self.resize_image(img, 250, 250)  # Resize for thumbnail
            photo = ImageTk.PhotoImage(img_resized)
            label_idx = self.num_columns*2 + idx  # Calculate label index for custom images
            self.all_labels[label_idx].configure(image=photo)
            self.all_labels[label_idx].image = photo  # Keep a reference to prevent garbage collection

            # Bind left-click to view full-screen and right-click to save the image
            self.all_labels[label_idx].bind("<Button-1>", lambda e, im=img: self.show_fullscreen(im))
            self.all_labels[label_idx].bind("<Button-3>", lambda e, im=img, idx=label_idx: self.save_image(im, idx))

    def update_grayscale_no_g(self, event=None):
        """Update the grayscale image without the green channel based on coefficient sliders."""
        if not self.original_image:
            return  # No image to process

        red_val = self.red_var.get()
        blue_val = self.blue_var.get()
        self.current_red_coeff = red_val
        self.current_blue_coeff = blue_val

        # Create a grayscale image without the green channel using custom coefficients
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
        self.gray_no_g_custom = self.custom_contrast_stretch(
            self.gray_no_g_normalized,
            self.lower_threshold_var.get(),
            self.upper_threshold_var.get(),
            self.inverse_lower_clip_var.get(),
            self.inverse_upper_clip_var.get()
        )

        # Update the grayscale without green channel image in the UI
        img_resized = self.resize_image(self.gray_no_g_image, 250, 250)
        photo = ImageTk.PhotoImage(img_resized)
        label = self.all_labels[4]
        label.configure(image=photo)
        label.image = photo
        label.bind("<Button-1>", lambda e, im=self.gray_no_g_image: self.show_fullscreen(im))
        label.bind("<Button-3>", lambda e, im=self.gray_no_g_image, idx=4: self.save_image(im, idx))

        # Update the normalized version
        img_resized_norm = self.resize_image(self.gray_no_g_normalized, 250, 250)
        photo_norm = ImageTk.PhotoImage(img_resized_norm)
        label_norm = self.all_labels[self.num_columns + 4]
        label_norm.configure(image=photo_norm)
        label_norm.image = photo_norm
        label_norm.bind("<Button-1>", lambda e, im=self.gray_no_g_normalized: self.show_fullscreen(im))
        label_norm.bind("<Button-3>", lambda e, im=self.gray_no_g_normalized, idx=self.num_columns + 4: self.save_image(im, self.num_columns + 4))

        # Update the custom stretched version
        img_resized_custom = self.resize_image(self.gray_no_g_custom, 250, 250)
        photo_custom = ImageTk.PhotoImage(img_resized_custom)
        label_custom = self.all_labels[2 * self.num_columns + 4]
        label_custom.configure(image=photo_custom)
        label_custom.image = photo_custom
        label_custom.bind("<Button-1>", lambda e, im=self.gray_no_g_custom: self.show_fullscreen(im))
        label_custom.bind("<Button-3>", lambda e, im=self.gray_no_g_custom, idx=2 * self.num_columns + 4: self.save_image(im, 2 * self.num_columns + 4))

        self.update_warning_label()  # Check for any coefficient warnings
        self.apply_custom_stretch()   # Re-apply custom stretching with updated coefficients

    def update_warning_label(self):
        """Display a warning if the sum of red and blue coefficients exceeds 1.0."""
        total = self.red_var.get() + self.blue_var.get()
        if total > 1.0:
            self.warning_label.config(text="Warning: Red + Blue coefficients exceed 1.0!")
        else:
            self.warning_label.config(text="")

    def show_fullscreen(self, image):
        """Display the selected image in a fullscreen window."""
        if self.fullscreen_window and self.fullscreen_image == image:
            # If the same image is clicked again, close the fullscreen view
            self.close_fullscreen()
            return
        if self.fullscreen_window:
            # Close any existing fullscreen window before opening a new one
            self.close_fullscreen()
        self.fullscreen_window = tk.Toplevel(self.root)
        self.fullscreen_window.attributes("-fullscreen", True)
        self.fullscreen_window.configure(background='black')
        self.fullscreen_window.bind("<Button-1>", lambda e: self.close_fullscreen())  # Close on click

        # Calculate the appropriate size to fit the screen
        screen_width = self.fullscreen_window.winfo_screenwidth()
        screen_height = self.fullscreen_window.winfo_screenheight()
        img_width, img_height = image.size
        ratio = min(screen_width / img_width, screen_height / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        img_resized = image.resize(new_size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img_resized)

        # Display the image in the fullscreen window
        label = tk.Label(self.fullscreen_window, image=photo, background='black', anchor='center')
        label.image = photo  # Keep a reference to prevent garbage collection
        label.pack(expand=True)
        self.fullscreen_image = image  # Keep track of the current fullscreen image

    def close_fullscreen(self):
        """Close the fullscreen image window."""
        if self.fullscreen_window:
            self.fullscreen_window.destroy()
            self.fullscreen_window = None
            self.fullscreen_image = None

    def save_image(self, image, idx):
        """Save the selected image to disk."""
        title = self.image_titles[idx]
        # Customize the default filename for specific images
        if idx in [4, self.num_columns + 4, 2 * self.num_columns + 4]:
            red = f"{self.current_red_coeff:.2f}"
            blue = f"{self.current_blue_coeff:.2f}"
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
                self.status_bar.config(text=f"Image saved: {file_path}")
                logging.info(f"Image saved: {file_path}")
            except Exception as e:
                # Show an error message if saving fails
                messagebox.showerror("Error", f"Failed to save image.\n{e}")
                logging.error(f"Failed to save image: {file_path} with error: {e}")

    def resize_image(self, image, max_width, max_height):
        """
        Resize the image to fit within the specified dimensions while maintaining aspect ratio.
        
        Parameters:
            image (PIL.Image): The image to resize.
            max_width (int): Maximum width in pixels.
            max_height (int): Maximum height in pixels.
        
        Returns:
            PIL.Image: The resized image.
        """
        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
        pillow_version = tuple(map(int, PILLOW_VERSION.split('.')[:2]))
        if pillow_version >= (10, 0):
            resample_filter = Image.Resampling.LANCZOS
        else:
            resample_filter = Image.ANTIALIAS
        return image.resize(new_size, resample=resample_filter)

    def add_tooltips(self):
        """Add tooltips to various UI elements to enhance user experience."""
        def create_tooltip(widget, text):
            """Create a tooltip for a given widget."""
            tooltip = tk.Toplevel(widget)
            tooltip.withdraw()
            tooltip.overrideredirect(True)
            tooltip_label = tk.Label(
                tooltip,
                text=text,
                background="#803030",
                foreground="#ffffff",
                font=("Arial", 10)
            )
            tooltip_label.pack()

            def enter(event):
                """Show tooltip on mouse enter."""
                x = event.widget.winfo_rootx()
                y = event.widget.winfo_rooty() + event.widget.winfo_height() + 5
                tooltip.geometry(f"+{x}+{y}")
                tooltip.deiconify()

            def leave(event):
                """Hide tooltip on mouse leave."""
                tooltip.withdraw()

            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

        # Add tooltips to sliders and buttons
        create_tooltip(self.red_scale, "Adjust the red coefficient for grayscale conversion (0.00 to 1.00 in 0.05 increments).")
        create_tooltip(self.blue_scale, "Adjust the blue coefficient for grayscale conversion (0.00 to 1.00 in 0.05 increments).")
        create_tooltip(self.lower_threshold_scale, "Set the lower threshold for contrast stretching. Pixels below this value will be clipped.")
        create_tooltip(self.upper_threshold_scale, "Set the upper threshold for contrast stretching. Pixels above this value will be clipped.")
        create_tooltip(self.inverse_lower_clip_checkbox, "Inverse the clipping behavior for the lower threshold.")
        create_tooltip(self.inverse_upper_clip_checkbox, "Inverse the clipping behavior for the upper threshold.")
        create_tooltip(self.reset_thresholds_button, "Reset Lower and Upper Thresholds to 128 and 255 respectively.")
        create_tooltip(self.reset_coefficients_button, "Reset Red and Blue coefficients to 0.50.")
        create_tooltip(self.invert_before_checkbox, "If checked, the image will be inverted before processing.")
        create_tooltip(self.preview_label, "Left-click to view the original image in full-screen.")

    def on_preview_left_click(self, event):
        """Handle left-click on the preview label to view the original image fullscreen."""
        if self.original_image_loaded:
            self.show_fullscreen(self.original_image_loaded)

    def update_preview_label(self):
        """Update the preview thumbnail with the loaded image."""
        if self.original_image_loaded:
            preview_img = self.resize_image(self.original_image_loaded, 100, 100)
            photo_preview = ImageTk.PhotoImage(preview_img)
            self.preview_label.configure(image=photo_preview)
            self.preview_label.image = photo_preview  # Keep a reference
            self.preview_label.grid()  # Make sure the preview is visible
        else:
            self.preview_label.configure(image='')
            self.preview_label.image = None
            self.preview_label.grid_remove()  # Hide if no image is loaded

    def show_next_image(self):
        """Navigate to and load the next image in the image list."""
        if not self.image_list:
            return  # No images to navigate
        self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
        next_image_path = self.image_list[self.current_image_index]
        self.load_image_from_path(next_image_path)

    def show_previous_image(self):
        """Navigate to and load the previous image in the image list."""
        if not self.image_list:
            return  # No images to navigate
        self.current_image_index = (self.current_image_index - 1) % len(self.image_list)
        prev_image_path = self.image_list[self.current_image_index]
        self.load_image_from_path(prev_image_path)

    def load_image_from_path(self, file_path):
        """Load an image from a specific file path."""
        try:
            # Open the image and convert to RGB
            self.original_image_loaded = Image.open(file_path).convert("RGB")

            if self.invert_before_var.get():
                # Invert colors if the checkbox is selected
                self.original_image = ImageOps.invert(self.original_image_loaded)
                self.status_bar.config(text=f"Loaded and inverted image: {file_path}")
                logging.info(f"Loaded and inverted image: {file_path}")
            else:
                self.original_image = self.original_image_loaded
                self.status_bar.config(text=f"Loaded image: {file_path}")
                logging.info(f"Loaded image: {file_path}")
        except Exception as e:
            # Show error message if loading fails
            messagebox.showerror("Error", f"Failed to load image.\n{e}")
            logging.error(f"Failed to load image: {file_path} with error: {e}")
            return

        # Update the image list based on the new folder
        folder = os.path.dirname(file_path)
        supported_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
        self.image_list = sorted([
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(supported_extensions)
        ])
        try:
            self.current_image_index = self.image_list.index(file_path)
        except ValueError:
            self.current_image_index = -1

        self.enable_widgets()  # Ensure widgets are enabled

        self.process_images()  # Process the newly loaded image
        self.display_images()  # Display all processed images
        self.update_warning_label()  # Check for any warnings
        self.apply_custom_stretch()   # Apply custom contrast stretching

        self.update_preview_label()  # Update the preview thumbnail

        self.update_navigation_arrows()  # Update navigation buttons

    def update_navigation_arrows(self):
        """Show or hide navigation arrows based on the number of images."""
        if self.image_list and len(self.image_list) > 1:
            self.left_arrow_button.grid()   # Show left arrow
            self.right_arrow_button.grid()  # Show right arrow
        else:
            self.left_arrow_button.grid_remove()   # Hide left arrow
            self.right_arrow_button.grid_remove()  # Hide right arrow

    def reset_thresholds(self):
        """Reset the lower and upper thresholds to their default values."""
        self.lower_threshold_var.set(128)
        self.upper_threshold_var.set(255)
        self.apply_custom_stretch()  # Re-apply stretching with default thresholds
        self.status_bar.config(text="Thresholds reset to 128 (Lower) and 255 (Upper).")
        logging.info("Thresholds reset to 128 (Lower) and 255 (Upper).")

    def reset_coefficients(self):
        """Reset the red and blue coefficients to their default values."""
        self.red_var.set(0.50)
        self.blue_var.set(0.50)
        self.update_grayscale_no_g()  # Update the grayscale without green channel
        self.status_bar.config(text="Red and Blue coefficients reset to 0.50.")
        logging.info("Red and Blue coefficients reset to 0.50.")

def main():
    """Entry point of the application."""
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
