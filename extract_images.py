
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Martin Kersner, m.kersner@gmail.com
# 2016/12/08

import os
import sys
import glob
import struct
import json

annotations = {}

def main():
    global annotations

    input_dir  = sys.argv[1]
    output_dir = sys.argv[2]

    annotations = json.loads(open(output_dir+"/annotations.json").read())

    # walk through all 'sets' of images
    for x in os.walk(input_dir):
        extract(os.path.join(input_dir, x[0]), output_dir)

def detect_format(image_format):
    if image_format == 100 or image_format == 200:
        return ".raw"
    elif image_format == 101:
        return ".brgb8"
    elif image_format == 102 or image_format == 201:
        return ".jpg"
    elif image_format == 103:
        return ".jbrgb"
    elif image_format == 1 or image_format == 2:
        return ".png"
    else:
        print "Invalid extension format " + image_format
        return None

def write_img(path, img_name, img_data):
    with open(os.path.join(path,img_name), "wb") as f:
        f.write(bytearray(img_data))

def write_xml(path, img_name, img_set, img_volume, img_id, header):
    global annotations
    objects = annotations[img_set][img_volume]["frames"].get(img_id, [])
    objs = ""
    for o in objects:
        xmin = int(o["pos"][0])
        ymin = int(o["pos"][1])
        xmax = int(o["pos"][0]+o["pos"][2])
        #xmax = int(o["pos"][2])
        ymax = int(o["pos"][1]+o["pos"][3])
        #ymax = int(o["pos"][3])

        truncated = "0"
        if xmin < 0 or xmax > header["width"] or ymin < 0 or ymax > header["height"]:
            truncated = "1"

        xmin = max(xmin, 0)
        ymin = max(ymin, 0)
        xmax = min(xmax, header["width"])
        #xmax = int(o["pos"][2])
        ymax = min(ymax, header["height"])
        #ymax = int(o["pos"][3])
        t = """
    <object>
        <name>%s</name>
        <pose>Unspecified</pose>
        <truncated>%s</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%s</xmin>
            <ymin>%s</ymin>
            <xmax>%s</xmax>
            <ymax>%s</ymax>
        </bndbox>
    </object>
""" % ("person", truncated, xmin, ymin, xmax, ymax) #o["lbl"]
        objs += t
        #else:
        #    print 'bad box',  xmin, ymin, xmax, ymax

    if objs:
        xml = """<annotation>
    <folder>Caltech</folder>
    <filename>%s.jpg</filename>
    <size>
        <width>%s</width>
        <height>%s</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    %s
</annotation>
    """ % (img_name, header["width"], header["height"], objs)

        with open(os.path.join(path,img_name+".xml"), "wb") as f:
            f.write(bytearray(xml.encode("utf-8")))

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# def create_output_dir(input_dir, output_dir):
#     create_dir(output_dir)

def extract(input_dir, output_dir):
    # test input dir -> stop
    # test output dir -> create
    SKIP = 28 + 8 + 512

    for filename in glob.glob(os.path.join(input_dir, "*.seq")):
        print filename

        im_set = input_dir[-5:]

        # create_dir(os.path.join(output_dir, im_set))

        with open(filename, "rb") as f:
            f.seek(SKIP)

            header_info = ["width", "height", "imageBitDepth", 
                           "imageBitDepthReal", "imageSizeBytes", 
                           "imageFormat", "numFrames"]
            header = {}

            for attr in header_info:
                header[attr] = struct.unpack('I', f.read(4))[0] 

            f.read(4) # skip 4 bytes

            header["trueImageSize"] = struct.unpack('I', f.read(4))[0] 
            header["fps"] = struct.unpack('d', f.read(8))[0] 

            print header

            ext = detect_format(header["imageFormat"])

            f.seek(432, 1) # skip to image data
            for img_id in range(header["numFrames"]):
                img_size = struct.unpack('I', f.read(4))[0] 

                img_data = f.read(img_size)
                # img_name = str(img_id) + ext
                img_name = im_set[-2:] + os.path.basename(filename)[1:-4] + str(img_id).zfill(6)
                # write_img(os.path.join(output_dir,im_set), img_name, img_data)
                write_img(output_dir+"/JPEGImages/", img_name + ext, img_data)
                write_xml(output_dir+"/Annotations/", img_name, im_set, os.path.basename(filename)[:-4], str(img_id), header)

                f.seek(12, 1) # skip to next image

if __name__ == "__main__":
    main()

