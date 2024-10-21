# Custom Contrast Stretching GUI with Channel Extractor

A graphical application for processing and analyzing images using custom contrast stretching and color channel extraction.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [How to Use](#how-to-use)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## Description

The **Custom Contrast Stretching GUI with Channel Extractor** is a desktop application that enables users to load, process, and analyze images through custom contrast stretching and color channel manipulation. It provides an interactive graphical user interface (GUI) for extracting color channels, converting them to grayscale, and applying custom contrast adjustments with adjustable parameters.

While the application is suitable for fundus (retinal) images, its functionalities are not limited to any specific type of image. It allows users to explore different grayscale images derived from color channels and to apply custom bottom values for contrast stretching, making it a versatile tool for various image processing tasks.

## Features

- **Load and Display Images**: Easily load images of various formats and display them within the application.
- **Color Channel Extraction**: Extract and display individual Red, Green, and Blue channels from the image.
- **Grayscale Conversion**: Convert images to grayscale, including a custom grayscale that excludes the green channel with adjustable red and blue coefficients.
- **Normalization**: Apply auto-contrast normalization to enhance image contrast automatically.
- **Custom Contrast Stretching**: Perform custom contrast stretching by setting custom bottom values (thresholds) to adjust image intensity levels.
- **Interactive Sliders**:
  - **Red and Blue Coefficients**: Adjust red and blue coefficients for the custom grayscale conversion excluding the green channel.
  - **Contrast Stretch Threshold**: Set the threshold value for custom contrast stretching.
- **Image Interaction**:
  - **Full-Screen View**: Left-click on any image to view it in full-screen mode.
  - **Save Images**: Right-click on any image to save it to your local machine in various formats.
- **User-Friendly GUI**: An intuitive interface built with Tkinter for easy navigation and real-time updates.

## Installation

### Prerequisites

- **Python 3.x**
- **Tkinter**: Usually included with Python. If not, install it via your package manager.
- **Pillow (PIL)**: Python Imaging Library.

### Clone the Repository

```bash
git clone https://github.com/yourusername/custom-contrast-stretching-gui.git
cd custom-contrast-stretching-gui
