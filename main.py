import os
import shutil
import glob
from rJEPG2TIFF import rjpeg_to_tiff  # Make sure rJEPG2TIFF.py is in the same folder as main.py

def batch_process_thermal_images(input_folder, output_folder, **kwargs):
    """
    Reads all JPEGs in the input folder, converts them to radiometric TIFFs,
    and moves the resulting TIFFs to the output folder.
    """
    # 1. Ensure the output directory exists; if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output directory: {output_folder}")

    # Find all JPEG files in the input folder (case-insensitive for extension)
    search_pattern = os.path.join(input_folder, '*.[jJ][pP][gG]')
    image_files = glob.glob(search_pattern)
    
    # Also grab .jpeg files just in case
    image_files.extend(glob.glob(os.path.join(input_folder, '*.[jJ][pP][eE][gG]')))

    if not image_files:
        print(f"No JPEG images found in {input_folder}")
        return

    print(f"Found {len(image_files)} images to process.")

    # 3. Loop through and process each image
    success_count = 0
    for img_path in image_files:
        print(f"\nProcessing: {os.path.basename(img_path)}...")
        
        try:
            # Run the conversion function from your imported script
            # Pass any extra keyword arguments (like emissivity, distance, etc.)
            rjpeg_to_tiff(img_path, **kwargs)
            
            # The original script saves the TIFF in the same folder as the input JPEG.
            # We need to find that newly created TIFF and move it.
            base, _ = os.path.splitext(img_path)
            generated_tif_path = f"{base}.tif"
            
            if os.path.exists(generated_tif_path):
                # Construct the final destination path
                filename = os.path.basename(generated_tif_path)
                destination_path = os.path.join(output_folder, filename)
                
                # Move the file to the new folder (will overwrite if it already exists)
                shutil.move(generated_tif_path, destination_path)
                print(f"--> Saved to: {destination_path}")
                success_count += 1
            else:
                print(f"--> Error: Expected TIFF not found at {generated_tif_path}")

        except Exception as e:
            # Catch errors so one bad image doesn't crash the whole batch
            print(f"--> FAILED to process {os.path.basename(img_path)}: {e}")

    print(f"\nBatch processing complete! Successfully converted {success_count} out of {len(image_files)} images.")

if __name__ == "__main__":
    # Define your folders here
    INPUT_DIR = r"D:\Documents\kumar\OneDrive - BRGM\Bureau\FlirVueTherm-main\raw_images"
    OUTPUT_DIR = r"D:\Documents\kumar\OneDrive - BRGM\Bureau\FlirVueTherm-main\converted_tiffs"

    # Run the batch process
    # You can also pass your optional environmental parameters here if you don't want to rely solely on EXIF
    batch_process_thermal_images(
        input_folder=INPUT_DIR, 
        output_folder=OUTPUT_DIR,
        emissivity=0.95,  # Emissivity
        distance=None,  # Object Distance-- None will trigger exiftool to get the object distance from the image.
        Ta=15,  # Atmospheric Temperature (Ta)
        Tr=15,  #Reflected Apparent Temperature (Tr);; Generally Ta=Tr
        RH=75  # Relative Humidity (RH)
    )