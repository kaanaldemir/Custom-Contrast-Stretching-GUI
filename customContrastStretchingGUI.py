import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps, __version__ as PILLOW_VERSION
import logging
import os
import sys


# Configure logging
    # logging.basicConfig(filename='app.log', level=logging.INFO,
                       #  format='%(asctime)s:%(levelname)s:%(message)s')

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Contrast Stretching GUI by github.com/kaanaldemir")
        self.root.geometry("1325x980")  # Increased width to accommodate the new slider
        self.root.minsize(980, 980)
        
        # ### Set the window icon ###
        try:
            if getattr(sys, 'frozen', False):
                # If the application is run as a bundled executable, the path is in _MEIPASS
                script_dir = sys._MEIPASS
            else:
                # If run as a script, get the directory of the script
                script_dir = os.path.dirname(os.path.abspath(__file__))

            # Construct the full path to 'cstretch.ico'
            icon_path = os.path.join(script_dir, "cstretch.ico")

            # Check if the icon file exists
            if not os.path.exists(icon_path):
                raise FileNotFoundError(f"Icon file not found at: {icon_path}")

            # Load the icon image using PIL
            icon_image = Image.open(icon_path)
            # Convert the image to a PhotoImage object
            icon_photo = ImageTk.PhotoImage(icon_image)
            # Set the window icon
            self.root.iconphoto(False, icon_photo)
            # Keep a reference to prevent garbage collection
            self.root.icon_photo = icon_photo
        except Exception as e:
            logging.warning(f"Failed to set window icon: {e}")
        # ### End of icon setup ###

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
                             background=self.colors["primary_bg"],
                             foreground=self.colors["sub_text"],
                             font=("Arial", 10, "bold"))
        self.style.map("TButton",
                       foreground=[('active', self.colors["secondary_bg"])],
                       background=[('active', self.colors["sub_text"])])
        
        self.style.configure("TScale", background=self.colors["primary_bg"])

        # Define a new style for Inverse Clip Checkbuttons
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
        # Note: 'indicatorcolor' may not be supported on all platforms/themes

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

        # Attempt to load an icon for the load button (optional)
        try:
            load_icon_image = Image.open("load_icon.png").resize((20, 20))
            load_icon = ImageTk.PhotoImage(load_icon_image)
            load_button = ttk.Button(left_top_frame, text="Load Image", image=load_icon, compound="left", command=self.load_image)
            load_button.image = load_icon  # Prevent garbage collection
        except Exception as e:
            logging.warning(f"Failed to load load_icon.png: {e}")
            # Fallback to text-only button if icon fails to load
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
        sliders_frame.columnconfigure(4, weight=0)  # Column for value labels

        # ### Converted Red and Blue Coefficient Sliders using tk.Scale ###

        # Red Coefficient Slider using tk.Scale
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
            resolution=0.05,                # Step increment set to 0.05
            command=lambda val: self.update_grayscale_no_g(),
            length=200,
            showvalue=0,                     # Hide the built-in value display
            background=self.colors["secondary_bg"],  # Match the background color
            troughcolor=self.colors["red"], # Match the trough color
            highlightthickness=0,           # Remove highlight border for a cleaner look
            borderwidth=0,                   # Remove border
            state='disabled'                 # Disabled initially
        )
        self.red_scale.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.red_value_label = ttk.Label(
            sliders_frame,
            text=f"{self.red_var.get():.2f}",
            font=("Arial", 10),
            foreground=self.colors["red"],
            width=6,  # Accommodates '1.00'
            anchor='center'
        )
        self.red_value_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Blue Coefficient Slider using tk.Scale
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
            resolution=0.05,                # Step increment set to 0.05
            command=lambda val: self.update_grayscale_no_g(),
            length=200,
            showvalue=0,                     # Hide the built-in value display
            background=self.colors["secondary_bg"],  # Match the background color
            troughcolor=self.colors["blue"], # Match the trough color
            highlightthickness=0,           # Remove highlight border for a cleaner look
            borderwidth=0,                   # Remove border
            state='disabled'                 # Disabled initially
        )
        self.blue_scale.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.blue_value_label = ttk.Label(
            sliders_frame,
            text=f"{self.blue_var.get():.2f}",
            font=("Arial", 10),
            foreground=self.colors["blue"],
            width=6,  # Accommodates '1.00'
            anchor='center'
        )
        self.blue_value_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Coefficient Revert Button
        self.reset_coefficients_button = tk.Button(
            sliders_frame,
            text="⟳",  # Unicode rotating arrow
            command=self.reset_coefficients,
            width=2,  # Adjust width as needed
            height=1, # Adjust height as needed
            state='disabled',  # Disabled initially
            bg=self.colors["secondary_bg"],
            fg=self.colors["text"],
            relief='flat'
        )
        self.reset_coefficients_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Warning Label with fixed row height to prevent layout shift
        self.warning_label = ttk.Label(
            sliders_frame,
            text="",
            font=("Arial", 10),
            foreground=self.colors["warning"]
        )
        self.warning_label.grid(row=2, column=0, columnspan=4, pady=(0, 0), sticky="w")
        self.warning_label.configure(anchor='w')  # Align text to the left

        # Control Frame: Contrast Stretch Thresholds
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        # Updated column configuration to accommodate checkboxes
        for i in range(8):
            control_frame.columnconfigure(i, weight=0)

        # Lower Threshold Slider using tk.Scale
        lower_threshold_label = ttk.Label(control_frame, text="Lower Threshold:", font=("Arial", 10))
        lower_threshold_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.lower_threshold_var = tk.IntVar(value=128)  # Set default to 128
        self.lower_threshold_var.trace_add("write", self.update_lower_threshold_label)

        self.lower_threshold_scale = tk.Scale(
            control_frame,
            from_=0,
            to=254,  # Changed maximum value from 255 to 254
            orient=tk.HORIZONTAL,
            variable=self.lower_threshold_var,
            resolution=1,                    # Step increment set to 1
            command=lambda val: self.apply_custom_stretch(),
            length=300,
            showvalue=0,                     # Hide the built-in value display
            background=self.colors["secondary_bg"],  # Match the background color
            troughcolor=self.colors["sub_text"], # Match the trough color
            highlightthickness=0,           # Remove highlight border
            borderwidth=0,                   # Remove border
            state='disabled'                 # Disabled initially
        )
        self.lower_threshold_scale.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.lower_threshold_value_label = ttk.Label(
            control_frame,
            text=f"{self.lower_threshold_var.get()}",
            font=("Arial", 10),
            foreground=self.colors["sub_text"],
            width=6,  # Accommodates '255'
            anchor='center'
        )
        self.lower_threshold_value_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Inverse Clip Checkbox for Lower Threshold
        self.inverse_lower_clip_var = tk.BooleanVar(value=False)
        self.inverse_lower_clip_checkbox = ttk.Checkbutton(
            control_frame,
            text="Inverse Clip",
            variable=self.inverse_lower_clip_var,
            command=self.apply_custom_stretch,
            style='InverseClip.TCheckbutton',
            state='disabled'  # Disabled initially
        )
        self.inverse_lower_clip_checkbox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Upper Threshold Slider using tk.Scale
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
            resolution=1,                    # Step increment set to 1
            command=lambda val: self.apply_custom_stretch(),
            length=300,
            showvalue=0,                     # Hide the built-in value display
            background=self.colors["secondary_bg"],  # Match the background color
            troughcolor=self.colors["sub_text"], # Match the trough color
            highlightthickness=0,           # Remove highlight border
            borderwidth=0,                   # Remove border
            state='disabled'                 # Disabled initially
        )
        self.upper_threshold_scale.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        self.upper_threshold_value_label = ttk.Label(
            control_frame,
            text=f"{self.upper_threshold_var.get()}",
            font=("Arial", 10),
            foreground=self.colors["sub_text"],
            width=6,  # Accommodates '255'
            anchor='center'
        )
        self.upper_threshold_value_label.grid(row=0, column=6, padx=5, pady=5, sticky="w")

        # Inverse Clip Checkbox for Upper Threshold
        self.inverse_upper_clip_var = tk.BooleanVar(value=False)
        self.inverse_upper_clip_checkbox = ttk.Checkbutton(
            control_frame,
            text="Inverse Clip",
            variable=self.inverse_upper_clip_var,
            command=self.apply_custom_stretch,
            style='InverseClip.TCheckbutton',
            state='disabled'  # Disabled initially
        )
        self.inverse_upper_clip_checkbox.grid(row=0, column=7, padx=5, pady=5, sticky="w")

        # Threshold Revert Button
        self.reset_thresholds_button = tk.Button(
            control_frame,
            text="⟳",  # Unicode rotating arrow
            command=self.reset_thresholds,
            width=2,  # Adjust width as needed
            height=1,  # Adjust height as needed
            state='disabled',  # Disabled initially
            bg=self.colors["secondary_bg"],
            fg=self.colors["text"],
            relief='flat'
        )
        self.reset_thresholds_button.grid(row=0, column=8, padx=25, pady=5, sticky="w")

        # Status Bar (Optional)
        self.status_bar = ttk.Label(
            self.root,
            text="Welcome to Image Processor",
            anchor='w',
            background=self.colors["secondary_bg"],
            foreground=self.colors["sub_text"]
        )
        self.status_bar.grid(row=4, column=0, sticky="ew")

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
            title_label = ttk.Label(
                self.image_frame,
                text=title,
                font=("Arial", 10, "bold"),
                foreground=fg_color
            )
            title_label.grid(row=0, column=col, padx=5, pady=5)

        for col, title in enumerate(normalized_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(
                self.image_frame,
                text=title,
                font=("Arial", 10, "bold"),
                foreground=fg_color
            )
            title_label.grid(row=2, column=col, padx=5, pady=5)

        for col, title in enumerate(custom_titles):
            fg_color = self.get_title_color(title)
            title_label = ttk.Label(
                self.image_frame,
                text=title,
                font=("Arial", 10, "bold"),
                foreground=fg_color
            )
            title_label.grid(row=4, column=col, padx=5, pady=5)

        # Create image labels using tk.Label for better alignment control
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

        # Optional: Add Tooltips (Uncomment if desired)
        # self.add_tooltips()

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

    def update_red_label(self, *args):
        self.red_value_label.config(text=f"{self.red_var.get():.2f}")

    def update_blue_label(self, *args):
        self.blue_value_label.config(text=f"{self.blue_var.get():.2f}")

    def update_lower_threshold_label(self, *args):
        self.lower_threshold_value_label.config(text=f"{self.lower_threshold_var.get()}")

    def update_upper_threshold_label(self, *args):
        self.upper_threshold_value_label.config(text=f"{self.upper_threshold_var.get()}")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        if not file_path:
            return

        try:
            self.original_image = Image.open(file_path).convert("RGB")
            self.status_bar.config(text=f"Loaded image: {file_path}")
            logging.info(f"Loaded image: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image.\n{e}")
            logging.error(f"Failed to load image: {file_path} with error: {e}")
            return

        # Enable sliders and checkboxes
        self.enable_widgets()

        self.process_images()
        self.display_images()
        self.update_warning_label()
        self.apply_custom_stretch()

    def enable_widgets(self):
        # Enable sliders
        self.red_scale.config(state='normal')
        self.blue_scale.config(state='normal')
        self.lower_threshold_scale.config(state='normal')
        self.upper_threshold_scale.config(state='normal')

        # Enable checkbuttons
        self.inverse_lower_clip_checkbox.config(state='normal')
        self.inverse_upper_clip_checkbox.config(state='normal')

        # Enable revert buttons
        self.reset_thresholds_button.config(state='normal')
        self.reset_coefficients_button.config(state='normal')

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

        lower = self.lower_threshold_var.get()
        upper = self.upper_threshold_var.get()
        inverse_lower = self.inverse_lower_clip_var.get()
        inverse_upper = self.inverse_upper_clip_var.get()

        # Ensure upper threshold is at least one greater than lower threshold
        if lower >= upper:
            upper = min(lower + 1, 255)  # Ensure upper is at least lower + 1 and does not exceed 255
            self.upper_threshold_var.set(upper)
            self.upper_threshold_value_label.config(text=f"{upper}")
            self.status_bar.config(text="Upper Threshold adjusted to be at least one higher than Lower Threshold.")
            logging.warning("Upper Threshold was less than or equal to Lower Threshold. Adjusted Upper Threshold to be at least one higher.")
        else:
            self.status_bar.config(text="Applying custom contrast stretch.")

        # Update value labels (handled by trace)

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
        self.display_custom_stretched_images()

    def custom_contrast_stretch(self, image, lower_threshold, upper_threshold, inverse_lower, inverse_upper):
        """
        Apply custom contrast stretching to an image based on lower and upper thresholds.
        Pixels below lower_threshold are set to 0 (or 255 if inverse_lower is True).
        Pixels above upper_threshold are set to 255 (or 0 if inverse_upper is True).
        Pixels between are scaled linearly between 0 and 255.
        """
        if upper_threshold == lower_threshold:
            # Avoid division by zero; set all pixels below threshold to 0 (or 255) and above to 255 (or 0)
            if inverse_lower:
                return image.point(lambda p: 255 if p >= lower_threshold else 0)
            else:
                return image.point(lambda p: 0 if p < lower_threshold else 255)
        elif upper_threshold < lower_threshold:
            # Swap thresholds if necessary
            lower_threshold, upper_threshold = upper_threshold, lower_threshold

        # Create a lookup table
        lut = []
        for i in range(256):
            if i < lower_threshold:
                lut.append(255 if inverse_lower else 0)
            elif i > upper_threshold:
                lut.append(0 if inverse_upper else 255)
            else:
                # Scale between 0 and 255
                scaled = int((i - lower_threshold) * 255 / (upper_threshold - lower_threshold))
                lut.append(scaled)
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

        # Retrieve coefficients directly from sliders (0.0 to 1.0)
        red_val = self.red_var.get()
        blue_val = self.blue_var.get()
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
        # Apply contrast stretching
        self.gray_no_g_custom = self.custom_contrast_stretch(
            self.gray_no_g_normalized,
            self.lower_threshold_var.get(),
            self.upper_threshold_var.get(),
            self.inverse_lower_clip_var.get(),
            self.inverse_upper_clip_var.get()
        )

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
        total = self.red_var.get() + self.blue_var.get()
        if total > 1.0:
            self.warning_label.config(text="Warning: Red + Blue coefficients exceed 1.0!")
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
                messagebox.showerror("Error", f"Failed to save image.\n{e}")
                logging.error(f"Failed to save image: {file_path} with error: {e}")

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

    def add_tooltips(self):
        # Define a tooltip function
        def create_tooltip(widget, text):
            tooltip = tk.Toplevel(widget)
            tooltip.withdraw()
            tooltip.overrideredirect(True)
            tooltip_label = tk.Label(
                tooltip,
                text=text,
                background="#333333",
                foreground="#ffffff",
                font=("Arial", 10)
            )
            tooltip_label.pack()

            def enter(event):
                x = event.widget.winfo_rootx() + event.widget.winfo_width()
                y = event.widget.winfo_rooty()
                tooltip.geometry(f"+{x}+{y}")
                tooltip.deiconify()

            def leave(event):
                tooltip.withdraw()

            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

        # Apply tooltips to sliders and checkboxes
        create_tooltip(self.red_scale, "Adjust the red coefficient for grayscale conversion (0.00 to 1.00 in 0.05 increments).")
        create_tooltip(self.blue_scale, "Adjust the blue coefficient for grayscale conversion (0.00 to 1.00 in 0.05 increments).")
        create_tooltip(self.lower_threshold_scale, "Set the lower threshold for contrast stretching. Pixels below this value will be clipped.")
        create_tooltip(self.upper_threshold_scale, "Set the upper threshold for contrast stretching. Pixels above this value will be clipped.")
        create_tooltip(self.inverse_lower_clip_checkbox, "Inverse the clipping behavior for the lower threshold.")
        create_tooltip(self.inverse_upper_clip_checkbox, "Inverse the clipping behavior for the upper threshold.")
        create_tooltip(self.reset_thresholds_button, "Reset Lower and Upper Thresholds to 128 and 255 respectively.")
        create_tooltip(self.reset_coefficients_button, "Reset Red and Blue Coefficients to 0.50.")

    # Callback to reset thresholds to 128 and 255
    def reset_thresholds(self):
        self.lower_threshold_var.set(128)
        self.upper_threshold_var.set(255)
        self.apply_custom_stretch()  # Call this to apply the reset values
        self.status_bar.config(text="Thresholds reset to 128 (Lower) and 255 (Upper).")
        logging.info("Thresholds reset to 128 (Lower) and 255 (Upper).")

    # Callback to reset red and blue coefficients to 0.50
    def reset_coefficients(self):
        self.red_var.set(0.50)
        self.blue_var.set(0.50)
        self.update_grayscale_no_g()  # Call this to apply the reset values
        self.status_bar.config(text="Red and Blue coefficients reset to 0.50.")
        logging.info("Red and Blue coefficients reset to 0.50.")

def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
