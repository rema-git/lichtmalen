"""
Created on Mon Oct 27 00:33:17 2014

@author: Reinhardt A.W. Maier <rema@zaehlwerk.net>
"""
import os
import argparse
import binascii
import numpy as np
from PIL import Image, ImageOps


def tpm2(image: Image, last_frame_black: bool = False):
    """
    generate TPM2 file format:
     * image as numpy array with dim(height, width, color)
     * returns tpm2 as string
    """
    dim = tuple((np.shape(image)[0], np.shape(image)[1]))
    frameheader = "C9DA{:04X}".format(dim[1] * 3)
    output = []
    for frame in range(dim[0]):  # loop over lines = height
        output += frameheader
        for led in range(dim[1]):  # loop over columns = width
            output += "{:02X}{:02X}{:02X}".format(*image[frame][led])
        output += "36"  # end-of-frame
    if last_frame_black:
        output += frameheader + "0" * 6 * dim[1] + "36"  # black frame
        print("Added black frame to EOF")

    return "".join(output)


def image_filter(image: Image):
    """
    example filter function
    """
    filtered_image = image.rotate(-90, expand=True)

    return filtered_image


def image_fit_to_leds(image: Image, n_leds: int = 121):
    """
    resize image to number of LEDs
    """
    scale = n_leds / float(image.size[0])
    hsize = int((float(image.size[1]) * float(scale)))
    image = image.resize((n_leds, hsize))

    return image


def rgb_to_grb(image: np.ndarray):
    """
    swap color order of numpy array: RGB -> GRB
    """
    R, G, B = image.T

    return np.array([G, R, B]).T


def main(image_filename: str, tpm2_filename: str, *args):
    """
    open image, apply filter function and save as TPM2 binary file
    """
    # open image file
    image = Image.open(image_filename)

    # If the image is has a rotation stored in the EXIF data,
    # rotate it accordingly.
    image = ImageOps.exif_transpose(image)

    print("Image read from", image_filename)

    # filter image
    if image.mode != "RGB":
        print("Convert image to RGB")
        image = image.convert("RGB")
    image = image_filter(image)
    image = image_fit_to_leds(image)

    # convert to numpy array with dim(height, width, color)
    image = np.array(image)

    # swap colors
    image = rgb_to_grb(image)

    # convert image to tpm2
    tpm2_string = tpm2(image, *args)
    print("Image successfully converted")

    # write result to file
    with open(tpm2_filename, "wb") as bin_file:
        tpm2_binary = binascii.a2b_hex(tpm2_string)
        bin_file.write(tpm2_binary)
        print("TPM2 file written to", tpm2_filename)


if __name__ == "__main__":
    # if this module is being run directly use command line arguments
    parser = argparse.ArgumentParser(description="convert an image file to tpm2 format")
    parser.add_argument(
        "--noloop",
        action="store_true",
        dest="last_frame_black",
        help="add a black frame to stop with",
    )
    parser.add_argument(
        "infile",
        type=argparse.FileType("r"),
        help="image file to be converted. Supported are all common image formats, e.g. .jpg, .png, .gif, .bmp",
    )
    parser.add_argument(
        "outfile",
        type=argparse.FileType("w"),
        default=None,
        nargs="?",
        help="tpm2 file to be created (default: infile.tp2)",
    )
    args = parser.parse_args()

    # set output filename, if not given use input filename with extension .tp2
    if args.outfile == None:
        outfile = os.path.splitext(args.infile.name)[0] + ".tp2"
    else:
        outfile = args.outfile.name

    main(args.infile.name, outfile, args.last_frame_black)
