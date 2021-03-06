# -*- coding: utf-8 -*-
"""My Object Detection Training: Espresso Mug

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UZtmVrrGEtciHgDJrJgPVNk8MDG886Ks

## Step 1: Download the project
"""

!git clone https://github.com/lysanda/ObjDet.git

"""### Change directory into the project"""

cd ObjDet/

"""### Clone the MMDetection project"""

!git clone https://github.com/open-mmlab/mmdetection.git

"""### Move the data into the mmdetection directory"""

mv data/ mmdetection/

"""### Change into the mmdetection directory"""

cd mmdetection/

"""### Build and setup MMDetection"""

!sudo pip install -r requirements/build.txt
!sudo pip install "git+https://github.com/open-mmlab/cocoapi.git#subdirectory=pycocotools"
!sudo pip install -v -e .
!sudo pip install mmcv-full

!sudo pip install mmcv==1.0.5

"""## Step 2: Setup code structure

### Setup the libraries we need
"""

import os
from os.path import exists, join, basename, splitext
import json
import pandas as pd
import numpy as np

"""### Setup model structure for choosing the file to run"""

# This provides you a link to the file you want to use and the selected model you want to build

MODELS_CONFIG = {
    'faster_rcnn_r50_fpn_1x_coco':{
        'config_file': 'configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'
    }
}

"""### Setup the number of epochs and model structure"""

# Pick the model you want to use

# Select a model in `MODELS_CONFIG`.
selected_model = 'faster_rcnn_r50_fpn_1x_coco' 

# Total training epochs if you want to update the number of training epoch
total_epochs = 12

# Recommended resize value
image_size = (1333, 800)

# Name of the config file.
config_file = MODELS_CONFIG[selected_model]['config_file']

"""### Edit files to update classes to match our own class names


> MMDetection trains using 80 classes, our project only has one class, so we 
update some files to update class names and number of classes
"""

# We want to get the classes we are annotating from
annotation_path = os.path.join("", "data/coco/annotations", "instances_train2017.json")
json_file = open(annotation_path)
coco = json.load(json_file)
print(coco["categories"])
classes_names = [category["name"] for category in coco["categories"]]
print(classes_names)

"""### Update the "/mmdet/datasets/coco.py" file to update the class names"""

coco_dataset_class_file = "mmdet/datasets/coco.py"
import re
fname = coco_dataset_class_file
with open(fname) as f:
  s = f.read()
  s = re.sub('CLASSES = \(.*?\)',
               'CLASSES = ({})'.format("".join(["\'{}\',".format(name) for name in classes_names])), s, flags=re.S)
with open(fname, 'w') as f:
    f.write(s)

"""### Setup the base code from where all its code stems from"""

base_config_fname = 'configs/_base_/models/faster_rcnn_r50_fpn.py'

"""### Update the number of classes we are working on in the base file"""

fname = base_config_fname
with open(fname) as f:
    s = f.read()
    # Update `num_classes` including `background` class.
    s = re.sub('num_classes=.*?,',
               'num_classes={},'.format(len(classes_names)), s)
with open(fname, 'w') as f:
    f.write(s)

"""### Create helper function"""

def replace_second_occurrence(text, find_this, replace_with):
    return text.replace(find_this, replace_with, 2).replace(replace_with, find_this, 1)

"""### Update the image size, we also add the update the test json files"""

coco_instance_segmentation_fname = 'configs/_base_/datasets/coco_instance.py'
fname = coco_instance_segmentation_fname
with open(fname) as f:
    s = f.read()
    s = re.sub('img_scale=\(.*?,.*?\)',
               'img_scale={}'.format(image_size), s)
    s = replace_second_occurrence(s, 'annotations/instances_val2017.json', 'annotations/instances_test2017.json')
    s = replace_second_occurrence(s, 'val2017/', 'test2017/')
with open(fname, 'w') as f:
    f.write(s)
    
coco_detection_fname = 'configs/_base_/datasets/coco_detection.py'
fname = coco_detection_fname
with open(fname) as f:
    s = f.read()
    s = re.sub('img_scale=\(.*?,.*?\)',
               'img_scale={}'.format(image_size), s)
    s = replace_second_occurrence(s, 'annotations/instances_val2017.json', 'annotations/instances_test2017.json')
    s = replace_second_occurrence(s, 'val2017/', 'test2017/')
with open(fname, 'w') as f:
    f.write(s)

"""### Update the number of epochs and learning rate"""

base_schedule_fname = 'configs/_base_/schedules/schedule_1x.py'
lr = 0.02

fname = base_schedule_fname
with open(fname) as f:
    s = f.read()
    s = re.sub('total_epochs = \d+',
               'total_epochs = {}'.format(total_epochs), s)
    s = re.sub('lr=\d+.\d+',
               'lr={}'.format(lr), s)
with open(fname, 'w') as f:
    f.write(s)

"""### Add a pretrained model"""

# Commented out IPython magic to ensure Python compatibility.
# # If you want to use a COCO pretrained model, you need a link to the model. 
# # You replace the None in load_from with the link to the pretrained model. 
# # We do not have a pretrained model for ResNet18 on COCO, 
# # so do not update the load_from, leave it as None
# 
# %%writefile configs/_base_/default_runtime.py
# checkpoint_config = dict(interval=1)
# # yapf:disable
# log_config = dict(
#     interval=50,
#     hooks=[
#         # dict(type='TextLoggerHook'),
#         # dict(type='TensorboardLoggerHook')
#     ])
# # yapf:enable
# dist_params = dict(backend='nccl')
# log_level = 'INFO'
# load_from = 'https://open-mmlab.s3.ap-northeast-2.amazonaws.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth'
# resume_from = None
# workflow = [('train', 1)]

"""## Step 3: Training Time!!!

### Time to train the model
"""

!python tools/train.py {config_file}

"""### Confirmed the trained model exists"""

# Confirm the latest trained model exists
work_dir = "work_dirs/" + selected_model
checkpoint_file = os.path.join(work_dir, "latest.pth")
assert os.path.isfile(checkpoint_file), '`{}` not exist'.format(checkpoint_file)
checkpoint_file = os.path.abspath(checkpoint_file)
checkpoint_file

"""### Evaluate the results of the model"""

# Evaluate your model by bbox for bounding box
!python tools/test.py {config_file} {checkpoint_file} --eval bbox

"""### Step 4: Time to test the model

### Setup library and functions for testing the model
"""

import glob
from mmdet.apis import inference_detector, init_detector, show_result_pyplot

# Collect the list of images to test. You can update this list with the files you want to test. It can be a single image or multiple images
files_for_test = glob.glob("data/coco/test2017/*.jpg")

"""### Create a helper function to test our model"""

# We create a helper method that takes an image and returns its prediction. We save a copy of the image appending result at the beginning of the original image name
from IPython.display import Image
def show_result(img_path, score_thr):
  
  # build the model from a config file and a checkpoint file
  model = init_detector(config_file, checkpoint_file, device='cuda:0')

  img_result_path = 'result_' + img_path.split("/")[-1]

  print("Result: ", img_result_path)

  result = inference_detector(model, img_path)
  res2 = model.show_result(img_path, result,
            score_thr=score_thr, thickness = 4, 
            bbox_color = "green",  
            font_scale=1.0, 
            out_file=img_result_path, 
            text_color="green"
            )
  
  # Show the image with bbox overlays.
  Image(filename=img_result_path)

# Testing the above method for only one image
score_thr = 0.5 # Choose the threshold of the accuracy you want
img = 'data/coco/test2017/62.jpg' # Location of the image
show_result(img, score_thr) # Call the method passing in the necessary parameters

"""### Test the prediction on the test models"""

# To test on images in a list
score_thr = 0.5 # Choose accuracy threshold
for file in files_for_test:
  show_result(file, score_thr)