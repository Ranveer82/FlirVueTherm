# FLIR RJPEG to 32-bit TIFF Thermal Converter

This tool provides an automated pipeline to batch convert proprietary FLIR Radiometric JPEGs (RJPEGs) into standard 32-bit floating-point TIFF images. Unlike standard JPEGs that only display a visual color map of heat, the generated TIFF files contain pure, raw scientific data where every pixel value represents the absolute temperature in degrees Celsius. 

This is highly useful for importing drone thermography data into GIS software or photogrammetry tools (like Agisoft Metashape or Pix4D) to build accurate 2D/3D thermal maps.

---

## 🔬 The Physics: How it Works

Thermal cameras do not natively \"measure temperature.\" Instead, their microbolometer sensors measure the intensity of infrared radiation hitting them, recording this as raw Digital Numbers (DN). 

To convert these raw DN values into true temperature readings, this script applies **FLIR's proprietary atmospheric correction** and **Planck's Law of black-body radiation**.

### 1. Atmospheric and Environmental Correction
Before determining the temperature of the object, the sensor's raw reading must be corrected for environmental interference. The total radiation reaching the drone's camera consists of three parts:
1.  **Emission from the object itself** (what we want).
2.  **Reflected radiation** from the surroundings bouncing off the object.
3.  **Atmospheric emission**, which is the radiation emitted by the air (water vapor) between the object and the camera.

The script calculates atmospheric transmission ($\tau$), atmospheric emittance, and object reflectance using the Relative Humidity (`RH`), Atmospheric Temperature (`Ta`), and Object Distance (`distance`). It deducts the interference to isolate the pure radiance of the target object.

### 2. Planck's Law
Once the pure object radiance is isolated, the script uses a modified version of Planck's Law to convert the radiance back into a temperature value. The formula relies on specific calibration constants ($B, F, O, R_1, R_2$) that FLIR embeds into the EXIF metadata of every image at the factory.

$$T = \\frac{B}{\\ln\\left(\\frac{R_1}{R_2 \\times (\\text{Radiance} + O)} + F\\right)} - 273.15$$

*The result is the true surface temperature in degrees Celsius.*

---

## ⚙️ Prerequisites & Installation

To run this tool, you need Python installed on your system, along with `exiftool`.

### Install ExifTool
The script relies heavily on [ExifTool by Phil Harvey](https://exiftool.org/) to crack open the RJPEG, extract the raw binary thermal data, and read the FLIR calibration constants.
* **Windows**: Download the Windows Executable, rename `exiftool(-k).exe` to `exiftool.exe`, and place it in a folder included in your system's `PATH` (or directly in the project folder).
* **Mac/Linux**: Install via standard package managers (e.g., `brew install exiftool` or `sudo apt install libimage-exiftool-perl`).

### Install Python Dependencies
Ensure you have a `requirements.txt` file in your directory containing:
