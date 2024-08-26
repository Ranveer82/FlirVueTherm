import subprocess
from PIL import Image
import numpy as np
import os

def rJPEG2TIFF(filename, *args, **kwargs):
    # parse inputs
    emissivity = kwargs.get('emissivity')
    distance = kwargs.get('distance')
    Ta = kwargs.get('Ta')
    Tr = kwargs.get('Tr')
    RH = kwargs.get('RH')

    # extract exif data from file and put into list
    exifdata = subprocess.check_output(['exiftool', filename]).decode().split('\n')
    exifdata = exifdata[:-1]
    exifdata = [line.split(':', 1) for line in exifdata]
    exifdata = [list(map(str.strip, line)) for line in exifdata]
    # print(exifdata)

    # load raw thermal image
    subprocess.run(['exiftool', '-b', '-rawthermalimage', filename, '>', 'tempImage.tif'])
    temp_image = Image.open('tempImage.tif')
    uTot = np.array(temp_image)
    print(uTot.shape)

    # # extract data for radiometric computations (unless already entered as variables)
    # if emissivity is None:
    #     emissivity = float(exifdata[51][1])
    # if distance is None:
    #     distance = float(exifdata[52][1].split()[0])
    # if Tr is None:
    #     Tr = float(exifdata[53][1].split()[0])
    # if Ta is None:
    #     Ta = float(exifdata[54][1].split()[0])
    # if RH is None:
    #     RH = float(exifdata[57][1].split()[0])

    # # extract Planck formula constants (determined when camera was calibrated by FLIR)
    # B = float(exifdata[59][1])
    # F = float(exifdata[60][1])
    # O = float(exifdata[85][1])
    # R1 = float(exifdata[58][1])
    # R2 = float(exifdata[86][1])

    # # extract atmospheric (determined when camera was calibrated by FLIR)
    # A1 = float(exifdata[61][1])
    # A2 = float(exifdata[62][1])
    # B1 = float(exifdata[63][1])
    # B2 = float(exifdata[64][1])
    # X = float(exifdata[65][1])

    # # calculate atmospheric transmission
    # H2O = (RH / 100) * np.exp(1.5587 + 6.939e-2 * Ta - 2.7816e-4 * Ta**2 + 6.8455e-7 * Ta**2)
    # tau = X * np.exp(-np.sqrt(distance) * (A1 + B1 * np.sqrt(H2O))) + (1 - X) * np.exp(-np.sqrt(distance) * (A2 + B2 * np.sqrt(H2O)))

    # # get atmospheric emittance
    # uAtm = R1 / (R2 * (np.exp(B / (Ta + 273.15)) - F)) - O
    # attAtm = (1 - tau) * uAtm

    # # get object reflectance
    # uRefl = R1 / (R2 * (np.exp(B / (Tr + 273.15)) - F)) - O
    # attRefl = (1 - emissivity) * tau * uRefl

    # # correct total radiance (in FLIR raw dn) for atmospheric and reflections
    # uObj = (uTot - attAtm - attRefl) / emissivity / tau

    # # convert radiance (in FLIR raw dn) to temperature using Planck's law
    # img = B / np.log(R1 / (R2 * (uObj + O)) + F) - 273.15

    # # convert image to single precision
    # img = img.astype(np.float32)

    # # get output filename
    # pathstr, name = os.path.split(filename)
    # name = os.path.splitext(name)[0]
    # tifName = os.path.join(pathstr, name + '.tif')

    # # write TIFF
    # with Image.open(tifName, 'w') as t:
    #     t.tag.ImageLength = img.shape[0]
    #     t.tag.ImageWidth = img.shape[1]
    #     t.tag.Compression = 'lzw'
    #     t.tag.SampleFormat = 'ieeefp'
    #     t.tag.Photometric = 'minisblack'
    #     t.tag.BitsPerSample = 32
    #     t.tag.SamplesPerPixel = 1
    #     t.tag.PlanarConfiguration = 'chunky'
    #     t.write(img.tobytes())
    
    # # append original JPEG metadata to TIFF
    # subprocess.run(['exiftool', '-TagsFromFile', filename, '-all:all>all:all', tifName, '-overwrite_original'])

    # # delete temporary image file
    # os.remove('tempImage.tif')

# example usage:
rJPEG2TIFF('20221201_063539_R.jpg', emissivity=0.97, distance=100, Ta=15, Tr=15, RH=75)
