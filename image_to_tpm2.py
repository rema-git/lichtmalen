#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 00:33:17 2014

@author: Reinhardt A.W. Maier <rema@zaehlwerk.net>
"""
import os
import argparse
import binascii
import numpy as np
import Image as pil
#import textwrap
#import matplotlib.pyplot as plt

def tpm2(image, lastFrameBlack=False):
    """
    generate TPM2 file format:
     * image as numpy array with dim(height, width, color)
     * returns tpm2 as string
    """
    dim = tuple((np.shape(image)[0], np.shape(image)[1]))
    frameheader = 'C9DA{:04X}'.format(dim[1]*3)
    output = []
    for frame in range(dim[0]): # loop over lines = height
        output += frameheader
        for led in range(dim[1]): # loop over columns = width
            output += '{:02X}{:02X}{:02X}'.format(*image[frame][led])
        output += '36' # end-of-frame
    if lastFrameBlack:
        output += frameheader + '0'*6*dim[1] + '36' # black frame
        print 'Added black frame to EOF'
    return ''.join(output)

def imageFilter(image):
    """
    example filter function
    """
    filteredImage = image.rotate(90)

    return filteredImage

def imageFit2LEDs(image, n_LEDs=24):
    """
    resize image to number of LEDs
    """
    scale = n_LEDs / float(image.size[0])
    hsize = int((float(image.size[1]) * float(scale)))
    image = image.resize((n_LEDs, hsize))

    return image

def main(imageFilename, tpm2Filename, *opts):
    """
    open image, apply filter function and save as TPM2 binary file
    """
    # open image file
    try:
        image = pil.open(imageFilename)
        print 'Image read from', imageFilename
    except:
        print 'ERROR: cannot read input image file!'

    # filter image
    image = imageFilter(image)
    image = imageFit2LEDs(image)

    # convert to numpy array with dim(height, width, color)
    image = np.array(image)

    # display image
    #plt.imshow(image, interpolation='none')
    #plt.show()

    # convert image to tpm2
    tpm2string = tpm2(image, *opts)
    print 'Image successfully converted'

    # show result to screen
    #print textwrap.fill('\n' + tpm2string + '\n')

    # write result to file
    with open(tpm2Filename, 'wb') as binFile:
        tpm2binary = binascii.a2b_hex(tpm2string)
        binFile.write(tpm2binary)
        print 'TPM2 file written to', tpm2Filename

if __name__ == "__main__":
    # if this module is being run directly use command line arguments
    parser = argparse.ArgumentParser(description='convert an image file to tpm2 format')
    parser.add_argument('--noloop',
        action='store_true', dest='lastFrameBlack', 
        help='add a black frame to stop with')
    parser.add_argument('infile',
        type=argparse.FileType('r'),
        help="image file to be converted. Supported are all common image formats, e.g. .jpg, .png, .gif, .bmp")
    parser.add_argument('outfile',
        type=argparse.FileType('w'), default=None, nargs='?',
        help="tpm2 file to be created (default: infile.tp2)")
    args = parser.parse_args()

    # set output filename, if not given use input filename with extension .tp2
    if args.outfile == None:
        outfile = os.path.splitext(args.infile.name)[0] + '.tp2'
    else:
        outfile = args.outfile.name

    main(args.infile.name, outfile, args.lastFrameBlack)
