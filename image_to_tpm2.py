#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 00:33:17 2014

@author: Reinhardt A.W. Maier <rema@zaehlwerk.net>
"""
import sys
import numpy as np
import Image
import binascii
#import matplotlib.pyplot as plt

def tpm2(image):
    """
    generate TMP2 file format:
     * image as numpy array with dim(height, width, color)
     * returns tpm2 string
    """
    dim = tuple((np.shape(image)[0], np.shape(image)[1]))
    frameheader = 'C9DA{:04X}'.format(dim[1]*3)
    output = []

    for frame in range(dim[0]): # loop over lines = height
        output += frameheader
        for led in range(dim[1]): # loop over columns = width
            output += '{:02X}{:02X}{:02X}'.format(*image[frame][led])
        output += '36' # end-of-frame
    output += frameheader + '0'*6*dim[1] + '36' # end-of-file: black frame
    return ''.join(output)

def imageFilter(image):
    """
    example filter function
    """
    filteredImage = image.rotate(90)
    filteredImage = filteredImage#.resize((128, 128))

    return filteredImage

def main(imageFilename, tmp2Filename):
    """
    open image, apply filter function and save as TMP2 binary file
    """
    # open image file
    try:
        image = Image.open(imageFilename)
        print 'Image file read.'
    except:
        print 'ERROR: cannot read input image file!'

    # filter image
    image = imageFilter(image)

    # convert to numpy array with dim(height, width, color)
    image = np.array(image)

    # display image
    #plt.imshow(image, interpolation='none')
    #plt.show()

    # convert image to tmp2
    tmp2string = tpm2(image)
    print 'Image converted.'

    # show result to screen
    #print '\n' + tmp2string + '\n'

    # write result to file
    with open(tmp2Filename, 'wb') as binFile:
        tmp2binary = binascii.a2b_hex(tmp2string)
        binFile.write(tmp2binary)
        print 'TPM2 file written.'

if __name__ == "__main__":
    # if this module is being run directly use command line arguments
    if len(sys.argv) < 3:
        print 'Usage: image_to_tpm2.py foo.[jpg|png|gif|...] bar.tp2'
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
