import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, __version__ as PILLOW_VERSION

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fundus Image Processor")
        self.root.geometry("2000x1600")
        self.root.resizable(False, False)

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

        self.current_red_coeff = 0.299
        self.current_blue_coeff = 0.114

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=20)

        load_button = tk.Button(
            top_frame,
            text="Load Image",
            command=self.load_image,
            bg="blue",
            fg="white",
            font=("Arial", 14),
            padx=10,
            pady=5
        )
        load_button.pack(side=tk.LEFT)

        indicator_label = tk.Label(
            top_frame,
            text="Left-click to view full-screen. Right-click to save image.",
            font=("Arial", 12)
        )
        indicator_label.pack(side=tk.LEFT, padx=20)

        sliders_frame = tk.Frame(top_frame)
        sliders_frame.pack(side=tk.LEFT, padx=20)

        red_label = tk.Label(sliders_frame, text="Red Coefficient:", font=("Arial", 10))
        red_label.pack()
        self.red_scale = tk.Scale(
            sliders_frame,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            resolution=1,
            command=self.update_grayscale_no_g,
            length=200
        )
        self.red_scale.set(int(self.current_red_coeff * 1000))
        self.red_scale.pack()

        blue_label = tk.Label(sliders_frame, text="Blue Coefficient:", font=("Arial", 10))
        blue_label.pack()
        self.blue_scale = tk.Scale(
            sliders_frame,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            resolution=1,
            command=self.update_grayscale_no_g,
            length=200
        )
        self.blue_scale.set(int(self.current_blue_coeff * 1000))
        self.blue_scale.pack()

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        threshold_label = tk.Label(control_frame, text="Contrast Stretch Threshold:", font=("Arial", 12))
        threshold_label.pack(side=tk.LEFT, padx=5)

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

        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)

        self.num_columns = 5

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

        for i in range(self.num_columns):
            label = tk.Label(self.image_frame)
            label.grid(row=0, column=i, padx=10, pady=10)
            self.all_labels.append(label)

        for idx, title in enumerate(original_titles):
            title_label = tk.Label(self.image_frame, text=title, font=("Arial", 12))
            title_label.grid(row=1, column=idx, pady=(0, 10))

        for i in range(self.num_columns):
            label = tk.Label(self.image_frame)
            label.grid(row=2, column=i, padx=10, pady=10)
            self.all_labels.append(label)

        for idx, title in enumerate(normalized_titles):
            title_label = tk.Label(self.image_frame, text=title, font=("Arial", 12))
            title_label.grid(row=3, column=idx, pady=(0, 10))

        for i in range(self.num_columns):
            label = tk.Label(self.image_frame)
            label.grid(row=4, column=i, padx=10, pady=10)
            self.all_labels.append(label)

        for idx, title in enumerate(custom_titles):
            title_label = tk.Label(self.image_frame, text=title, font=("Arial", 12))
            title_label.grid(row=5, column=idx, pady=(0, 10))

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
        self.reset_custom_stretched_images()
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
            img_resized = self.resize_image(img, 250, 300)
            photo = ImageTk.PhotoImage(img_resized)
            self.all_labels[idx].configure(image=photo)
            self.all_labels[idx].image = photo
            self.all_labels[idx].bind("<Button-1>", lambda e, im=img: self.show_fullscreen(im))
            self.all_labels[idx].bind("<Button-3>", lambda e, im=img, idx=idx: self.save_image(im, idx))

    def reset_custom_stretched_images(self):
        for label in self.all_labels[self.num_columns*2:self.num_columns*3]:
            label.configure(image='')
            label.image = None

    def apply_custom_stretch(self):
        if not self.original_image:
            messagebox.showwarning("No Image Loaded", "Please load an image before applying custom stretch.")
            return

        threshold = self.threshold_var.get()
        self.gray_custom = self.custom_contrast_stretch(self.gray_normalized, threshold)
        self.green_custom = self.custom_contrast_stretch(self.green_normalized, threshold)
        self.red_custom = self.custom_contrast_stretch(self.red_normalized, threshold)
        self.blue_custom = self.custom_contrast_stretch(self.blue_normalized, threshold)
        self.gray_no_g_custom = self.custom_contrast_stretch(self.gray_no_g_normalized, threshold)
        self.all_images += [self.gray_custom, self.green_custom, self.red_custom, self.blue_custom, self.gray_no_g_custom]
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
            img_resized = self.resize_image(img, 250, 300)
            photo = ImageTk.PhotoImage(img_resized)
            label_idx = self.num_columns*2 + idx
            self.all_labels[label_idx].configure(image=photo)
            self.all_labels[label_idx].image = photo
            self.all_labels[label_idx].bind("<Button-1>", lambda e, im=img: self.show_fullscreen(im))
            self.all_labels[label_idx].bind("<Button-3>", lambda e, im=img, idx=label_idx: self.save_image(im, idx))

    def update_grayscale_no_g(self, event=None):
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
        img_resized = self.resize_image(self.gray_no_g_image, 250, 300)
        photo = ImageTk.PhotoImage(img_resized)
        self.all_labels[4].configure(image=photo)
        self.all_labels[4].image = photo
        img_resized_norm = self.resize_image(self.gray_no_g_normalized, 250, 300)
        photo_norm = ImageTk.PhotoImage(img_resized_norm)
        self.all_labels[9].configure(image=photo_norm)
        self.all_labels[9].image = photo_norm
        img_resized_custom = self.resize_image(self.gray_no_g_custom, 250, 300)
        photo_custom = ImageTk.PhotoImage(img_resized_custom)
        self.all_labels[14].configure(image=photo_custom)
        self.all_labels[14].image = photo_custom
        self.all_labels[14].bind("<Button-1>", lambda e, im=self.gray_no_g_custom: self.show_fullscreen(im))
        self.all_labels[14].bind("<Button-3>", lambda e, im=self.gray_no_g_custom, idx=14: self.save_image(im, idx))

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
        label = tk.Label(self.fullscreen_window, image=photo, bg='black')
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
        if idx in [4, 9, 14]:
            default_name = f"{title}_R{self.current_red_coeff}_B{self.current_blue_coeff}.png"
        else:
            default_name = f"{title}.png"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg;*.jpeg"), ("BMP Image", "*.bmp"), ("TIFF Image", "*.tif;*.tiff")]
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
