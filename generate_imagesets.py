#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import random

def main():
    input_dir = sys.argv[1]

    names = [i[:-4] for i in os.listdir(input_dir+"/Annotations/") if i.endswith(".xml")]
    random.shuffle(names)

    test = names[:3001]
    trainval = names[3001:]
    val = trainval[:10001]
    train = trainval[10001:]

    open(input_dir+"/ImageSets/Main/test.txt", "w").write("\n".join(test))
    open(input_dir+"/ImageSets/Main/trainval.txt", "w").write("\n".join(trainval))
    open(input_dir+"/ImageSets/Main/val.txt", "w").write("\n".join(val))
    open(input_dir+"/ImageSets/Main/train.txt", "w").write("\n".join(train))

if __name__ == "__main__":
    main()

