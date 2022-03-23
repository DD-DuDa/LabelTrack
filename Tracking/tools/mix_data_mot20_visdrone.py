import json
import os

"""
cd datasets
mkdir -p mix_mot20_vd/annotations
cp VisDrone/annotations/test.json mix_mot20_vd/annotations/test.json
cd mix_mot20_vd/
ln -s ../MOT20/train mot20_train
ln -s ../VisDrone/train/ visdrone_train
ln -s ../VisDrone/test/ visdrone_test
cd ..
"""

mot_json = json.load(open('../datasets/MOT20/annotations/train.json','r'))
vd_json = json.load(open('../datasets/VisDrone/annotations/train.json','r'))

img_list = list()
for img in mot_json['images']:
    img['file_name'] = 'mot20_train/' + img['file_name']
    img_list.append(img)

ann_list = list()
for ann in mot_json['annotations']:
    ann_list.append(ann)

video_list = mot_json['videos']
category_list = vd_json['categories']

max_img = 10000
max_ann = 2000000
max_video = 10
img_id_count = 0
for img in vd_json['images']:
    img_id_count += 1
    img['file_name'] = 'visdrone_train/' + img['file_name']
    img['frame_id'] = img_id_count
    img['prev_image_id'] = img['id'] + max_img
    img['next_image_id'] = img['id'] + max_img
    img['id'] = img['id'] + max_img
    img['video_id'] = max_video
    img_list.append(img)
    
for ann in vd_json['annotations']:
    ann['id'] = ann['id'] + max_ann
    ann['image_id'] = ann['image_id'] + max_img
    ann_list.append(ann)

video_list.append({
    'id': max_video,
    'file_name': 'visdrone_train'
})

mix_json = dict()
mix_json['images'] = img_list
mix_json['annotations'] = ann_list
mix_json['videos'] = video_list
mix_json['categories'] = category_list
json.dump(mix_json, open('../datasets/mix_mot20_vd/annotations/train.json','w'))