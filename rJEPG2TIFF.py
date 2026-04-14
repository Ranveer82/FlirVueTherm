import os
import subprocess
import json
import re
import tempfile
import numpy as np
import tifffile

def rjpeg_to_tiff(filename, emissivity=None, distance=None, Ta=None, Tr=None, RH=None):
    """
    Reads a radiometric JPEG file acquired with a FLIR thermal camera into a numpy array 
    and converts it to a 32-bit floating-point TIFF with temperature values (Celsius).
    @Author: Ranveer Kumar
    
    Args:
        filename (str): Path to the RJPEG file.
        emissivity (float, optional): Emissivity of the object (0 - 1).
        distance (float, optional): Object distance in meters.
        Ta (float, optional): Atmospheric temperature in Celsius.
        Tr (float, optional): Reflected apparent temperature in Celsius.
        RH (float, optional): Relative humidity as %.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    # --Extract EXIF data using exiftool's JSON format
    try:
        exif_cmd = ['exiftool', '-j', filename]
        exif_process = subprocess.run(exif_cmd, capture_output=True, text=True, check=True)
        exif_data = json.loads(exif_process.stdout)[0]
    except FileNotFoundError:
        raise RuntimeError("exiftool not found. Please ensure it is installed and in your PATH.")

    # --Helper function to extract numeric values from EXIF dictionary safely
    def get_exif_num(key_substring):
        target = key_substring.lower().replace(" ", "")
        for k, v in exif_data.items():
            if target in k.lower().replace(" ", ""):
                if isinstance(v, str):
                    # Use regex to pull the first float/int found in the string (e.g. "1.00 m" -> 1.0)
                    match = re.search(r"[-+]?\d*\.\d+|\d+", v)
                    return float(match.group()) if match else None
                return float(v)
        raise KeyError(f"Could not find EXIF key matching: {key_substring}")

    # --Extract Raw Thermal Image to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_tif:
        temp_tif_path = temp_tif.name
    
    try:
        # --Extract binary raw thermal image to temporary TIFF
        with open(temp_tif_path, "wb") as f:
            subprocess.run(['exiftool', '-b', '-rawthermalimage', filename], stdout=f, check=True)
        
        # --Load raw thermal image and convert to float64 for calculations
        uTot = tifffile.imread(temp_tif_path).astype(np.float64)
    finally:
        # --Clean up temporary file
        if os.path.exists(temp_tif_path):
            os.remove(temp_tif_path)

    # --Parameter overrides: Use EXIF if kwargs are not provided
    emissivity = emissivity if emissivity is not None else get_exif_num("Emissivity")
    distance = distance if distance is not None else get_exif_num("ObjectDistance")
    Tr = Tr if Tr is not None else get_exif_num("ReflectedApparentTemperature")
    Ta = Ta if Ta is not None else get_exif_num("AtmosphericTemperature")
    RH = RH if RH is not None else get_exif_num("RelativeHumidity")

    # --Extract Planck and Atmospheric Constants
    B = get_exif_num("PlanckB")
    F = get_exif_num("PlanckF")
    O = get_exif_num("PlanckO")
    R1 = get_exif_num("PlanckR1")
    R2 = get_exif_num("PlanckR2")
    
    A1 = get_exif_num("AtmosphericTransAlpha1")
    A2 = get_exif_num("AtmosphericTransAlpha2")
    B1 = get_exif_num("AtmosphericTransBeta1")
    B2 = get_exif_num("AtmosphericTransBeta2")
    X = get_exif_num("AtmosphericTransX")

    # --Perform Radiometric Calculations
    # Calculate atmospheric transmission
    # Note: Corrected the final term to Ta**3 (Standard FLIR formula). The MATLAB code had Ta**2.
    H2O = (RH / 100.0) * np.exp(1.5587 + 6.939e-2 * Ta - 2.7816e-4 * (Ta**2) + 6.8455e-7 * (Ta**3))
    tau = X * np.exp(-np.sqrt(distance) * (A1 + B1 * np.sqrt(H2O))) + (1 - X) * np.exp(-np.sqrt(distance) * (A2 + B2 * np.sqrt(H2O)))

    # Get atmospheric emittance
    uAtm = R1 / (R2 * (np.exp(B / (Ta + 273.15)) - F)) - O
    attAtm = (1 - tau) * uAtm

    # Get object reflectance
    uRefl = R1 / (R2 * (np.exp(B / (Tr + 273.15)) - F)) - O
    attRefl = (1 - emissivity) * tau * uRefl

    # Correct total radiance (in FLIR raw dn) for atmospheric and reflections
    uObj = (uTot - attAtm - attRefl) / emissivity / tau

    # Convert radiance (in FLIR raw dn) to temperature using Planck's law
    img_temp = B / np.log(R1 / (R2 * (uObj + O)) + F) - 273.15

    # Convert image to single precision (32-bit floating point)
    img_single = img_temp.astype(np.float32)

    # 6. Write to TIFF
    base, _ = os.path.splitext(filename)
    tif_name = f"{base}.tif"

    # Save as 32-bit TIFF with MinIsBlack photometric interpretation
    tifffile.imwrite(
        tif_name, 
        img_single, 
        photometric='minisblack',
        compression=None
    )

    # --Append original JPEG metadata to the new TIFF
    subprocess.run([
        'exiftool', 
        '-TagsFromFile', filename, 
        '-all:all>all:all', 
        tif_name, 
        '-overwrite_original'
    ], check=True)

    print(f"Successfully converted {filename} to {tif_name}")

# Example Usage:
#rjpeg_to_tiff('20221130_110116_R.jpg', emissivity=0.97, distance=100, Ta=15, Tr=15, RH=75)