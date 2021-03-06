
import os
import shutil
import tensorflow as tf
import json
import math
from requests import get
from utils import label_map_util
from utils import visualization_utils as vis_util
from hash_compare import *
from ssim_compare import *
from face_compare import *
from histogram_compare import *
from lbp_compare import *
from google.cloud import storage
import base64

PATH_TO_CKPT = 'model/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('model', 'mscoco_label_map.pbtxt')

# variables from docker

APP_VERSION = os.environ.get("APP_VERSION") or '1.2.0'
APP_NAME = os.environ.get("APP_NAME") or 'Image_Compare_ML'
GS_BUCKET_NAME = 'image-ml'

if not os.path.exists('model/frozen_inference_graph.pb'):
	print ('Cannot find model')
else:
	print ('Model already exists')

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=90, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# get json api
def object_detection(strImagePath):
    image_np = cv2.imread(strImagePath)
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

            objects = vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8)

    biggest_area = 0
    object_name = ''
    object_image = image_np
    height, width, channels = image_np.shape
    for box, name in objects.items():
        ymin, xmin, ymax, xmax = box
        x1 = xmin * width
        y1 = ymin * height
        x2 = xmax * width
        y2 = ymax * height
        object_width = (xmax - xmin) * width
        object_height = (ymax - ymin) * height
        area = object_width * object_height
        if area > biggest_area:
            biggest_area = area
            object_name = name
            object_image = image_np[round(y1):round(y2), round(x1):round(x2)]

    return (object_name, object_image)

def getJsonData(strImagePath, identificator):
    full_path = os.path.splitext(strImagePath)[0]
    file_name = os.path.basename(full_path)
    jsonfile = file_name + '.json'

    object_name, object_image = object_detection(strImagePath)
    ssim_val = get_ssim(strImagePath)
    hash_val = get_hash(object_image)
    hist_val = get_hist(object_image)
    lbp_val = get_lbp(object_image)

    with open(strImagePath, 'rb') as open_file:
        byte_content = open_file.read()

    base64_bytes = base64.b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8')

    data = {}
    data['object'] = {}
    data['object'].append({
        'object_name': str(object_name),
        'ssim' : str(ssim_val),
        'hash' : str(hash_val),
        'hist' : str(hist_val),
        'lbp' : str(lbp_val),
        'feature' : base64_string,
        'identificator' : identificator
    })

    data['version'] = {}
    data['version'].append({
        'Name': APP_NAME,
        'version': str(APP_VERSION)
    })

    with open(jsonfile, 'w') as outfile:
        json.dump(data, outfile)

    return data, jsonfile

# compare image api
def image_compare(strFirstImage, strSecondImage, first_object_name, second_object_name):
    first_object_image = cv2.imread(strFirstImage)
    second_object_image = cv2.imread(strSecondImage)

    ssim_similar, ssim_value = ssim_compare(strFirstImage, strSecondImage)
    if ssim_similar == 'Same Image':
        return ssim_similar

    if first_object_name == '' and second_object_name == '':
        hash_result, hash_val = hash_compare(first_object_image, second_object_image)
        if hash_result == 'Same Image':
            hist_result, hist_val = hist_compare(first_object_image, second_object_image)
            if hist_result == 'Same Image':
                return compare_lbps(first_object_image, second_object_image)
            else:
                return 'Different Image'
        else:
            return 'Different Image'
    elif first_object_name == second_object_name:
        if first_object_name == 'person':
            return face_compare(first_object_image, second_object_image)
        elif first_object_name == 'N/A':
            hash_result, hash_val = hash_compare(first_object_image, second_object_image)
            if hash_result == 'Same Image':
                return compare_lbp(first_object_image, second_object_image)
            else:
                return 'Different Image'
        else:
            hash_result, hash_val = hash_compare(first_object_image, second_object_image)
            if hash_result == 'Same Image':
                hist_result, hist_val = hist_compare(first_object_image, second_object_image)
                return hist_result
            else:
                return hash_result
    else:
        return 'Different Image'

def image_compare_local(strFirstJson, strSecondJson):
    with open(strFirstJson, 'r') as f:
        firstData = json.load(f)

    with open(strSecondJson, 'r') as f:
        secondData = json.load(f)

    return image_compare_server(firstData, secondData)

def image_compare_server(firstData, secondData):
    first_version_data = firstData['version'][0]
    first_version = first_version_data['version']
    second_version_data = secondData['version'][0]
    second_version = second_version_data['version']
    if first_version != second_version:
        return createCompareJson(401, 'Json Version Error')

    first_object = firstData['object'][0]
    first_object_name = first_object['object_name']
    first_indentificator = first_object['identificator'] + '.jpg'
    first_feature_base64_string = first_object['feature']
    first_feature_base64_bytes = first_feature_base64_string.encode('utf-8')
    first_feature_decode_bytes = base64.b64decode(first_feature_base64_bytes)
    first_feature = open(first_indentificator, 'wb')
    first_feature.write(first_feature_decode_bytes)

    second_object = secondData['object'][0]
    second_object_name = second_object['object_name']
    second_indentificator = second_object['identificator'] + '.jpg'
    second_feature_base64_string = second_object['feature']
    second_feature_base64_bytes = second_feature_base64_string.encode('utf-8')
    second_feature_decode_bytes = base64.b64decode(second_feature_base64_bytes)
    second_feature = open(second_indentificator, 'wb')
    second_feature.write(second_feature_decode_bytes)

    compare_result = image_compare(first_indentificator, second_indentificator, first_object_name, second_object_name)

    if compare_result == 'Same Image':
        return createCompareJson(1, compare_result)
    else:
        return createCompareJson(0, compare_result)

def createCompareJson(code, detail):
    data = {}
    data['result'] = {}
    data['result'].append({
        'result_code': str(code),
        'detail': detail
    })

    data['version'] = {}
    data['version'].append({
        'Name': APP_NAME,
        'version': str(APP_VERSION)
    })

    jsonpath = 'result.json'
    with open(jsonpath, 'w') as outfile:
        json.dump(data, outfile)

    return data, jsonpath

# similar image api
def image_similar_local(strFirstJson, strSecondJson):
    with open(strFirstJson, 'r') as f:
        firstData = json.load(f)

    with open(strSecondJson, 'r') as f:
        secondData = json.load(f)

    return image_similar_server(firstData, secondData)

def image_similar(strFirstImage, strSecondImage, first_object_name, second_object_name):
    first_object_image = cv2.imread(strFirstImage)
    second_object_image = cv2.imread(strSecondImage)

    ssim_similar, ssim_val = ssim_compare(strFirstImage, strSecondImage)
    if ssim_val > 90:
        similar = ssim_val
    else:
        hash_result, hash_val = hash_compare(first_object_image, second_object_image)
        hist_result, hist_val = hist_compare(first_object_image, second_object_image)
        hash_val = hash_val / 4
        hist_val = hist_val / 4
        if first_object_name == second_object_name:
            similar = 50 + hash_val + hist_val
        else:
            similar = hash_val + hist_val

        similar = math.ceil(similar*100) / 100

    return similar

def image_similar_server(firstData, secondData):
    first_version_data = firstData['version'][0]
    first_version = first_version_data['version']
    second_version_data = secondData['version'][0]
    second_version = second_version_data['version']
    if first_version != second_version:
        similar = 'Json Version Error'
    else:
        first_object = firstData['object'][0]
        first_object_name = first_object['object_name']
        first_indentificator = first_object['identificator'] + '.jpg'
        first_feature_base64_string = first_object['feature']
        first_feature_base64_bytes = first_feature_base64_string.encode('utf-8')
        first_feature_decode_bytes = base64.b64decode(first_feature_base64_bytes)
        first_feature = open(first_indentificator, 'wb')
        first_feature.write(first_feature_decode_bytes)

        second_object = secondData['object'][0]
        second_object_name = second_object['object_name']
        second_indentificator = second_object['identificator'] + '.jpg'
        second_feature_base64_string = second_object['feature']
        second_feature_base64_bytes = second_feature_base64_string.encode('utf-8')
        second_feature_decode_bytes = base64.b64decode(second_feature_base64_bytes)
        second_feature = open(second_indentificator, 'wb')
        second_feature.write(second_feature_decode_bytes)

        similar = image_similar(first_indentificator, second_indentificator, first_object_name, second_object_name)

    data = {}
    data['result'] = {}
    data['result'].append({
        'Similarity': str(similar)
    })

    data['version'] = {}
    data['version'].append({
        'Name': APP_NAME,
        'version': str(APP_VERSION)
    })

    jsonpath = 'result.json'
    with open(jsonpath, 'w') as outfile:
        json.dump(data, outfile)

    return data, jsonpath

def upload_gcloud_storage(image_path):
    client = storage.Client()
    bucket = client.get_bucket(GS_BUCKET_NAME)
    file_name = image_path.split('/')[-1]
    gs_url = 'gs://' + GS_BUCKET_NAME + '/' + file_name
    blob = bucket.blob(gs_url)
    blob.upload_from_filename(filename=image_path)
    return gs_url

# crop image api
def cropImage(strImagePath):
    image_np = cv2.imread(strImagePath)
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

            objects = vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8)

    biggest_area = 0
    object_name = ''
    object_image = image_np
    height, width, channels = image_np.shape
    exist_object = False
    for box, name in objects.items():
        ymin, xmin, ymax, xmax = box
        x1 = xmin * width
        y1 = ymin * height
        x2 = xmax * width
        y2 = ymax * height
        object_width = (xmax - xmin) * width
        object_height = (ymax - ymin) * height
        area = object_width * object_height
        if area > biggest_area:
            biggest_area = area
            object_name = name
            object_rect = (x1, x2, y1, y2)
            exist_object = True

    if exist_object:
        x1, x2, y1, y2 = object_rect
        object_width = x2 - x1
        object_height = y2 - y1
        if object_width > width - object_width / 3 and object_height > height - object_height / 3:
            object_image = image_np
        else:
            if width > object_width * 1.5 and height > object_height * 1.5:
                average_img = image_np[0:int(y1), 0:int(x1)]
                avg_color_per_row = np.average(average_img, axis=0)
                avg_color = np.average(avg_color_per_row, axis=0)
                thresh_img = cv2.inRange(image_np, (avg_color[0]-10, avg_color[1]-10, avg_color[2]-10), (avg_color[0]+10, avg_color[1]+10, avg_color[2]+10))
                white_pixels = cv2.findNonZero(thresh_img)
                white_pixel_cnt = 0
                for pixel in white_pixels:
                    white_pixel_cnt = white_pixel_cnt + 1
                ratio = white_pixel_cnt * 100 / (width * height)
                if ratio < 70:
                    padding_x1 = x1
                    padding_x2 = width - x2
                    if object_height > object_width:
                        scale = object_height / 3
                    else:
                        scale = object_width / 3

                    if padding_x1 > padding_x2:
                        crop_x1 = x1 - scale * 4
                        crop_x2 = x2 + scale * 2
                    else:
                        crop_x1 = x1 - scale * 2
                        crop_x2 = x2 + scale * 4
                    crop_y1 = y1 - scale * 4
                    crop_y2 = y2 + scale * 2
                    if crop_x1 > 0 and crop_x2 < width and crop_y1 > 0 and crop_y2 < height:
                        object_image = image_np[int(crop_y1):int(crop_y2), int(crop_x1):int(crop_x2)]
                    else:
                        if object_height > object_width:
                            scale = object_height / 2
                        else:
                            scale = object_width / 2
                        if padding_x1 > padding_x2:
                            crop_x1 = x1 - scale * 3
                            crop_x2 = x2 + scale
                        else:
                            crop_x1 = x1 - scale
                            crop_x2 = x2 + scale * 3
                        crop_y1 = y1 - scale * 2
                        crop_y2 = y2 + scale
                        if crop_x1 > 0 and crop_x2 < width and crop_y1 > 0 and crop_y2 < height:
                            object_image = image_np[int(crop_y1):int(crop_y2), int(crop_x1):int(crop_x2)]
                        else:
                            if object_height > object_width:
                                scale = object_height / 3
                            else:
                                scale = object_width / 3
                            if padding_x1 > padding_x2:
                                crop_x1 = x1 - scale * 4
                                crop_x2 = x2 + scale
                            else:
                                crop_x1 = x1 - scale
                                crop_x2 = x2 + scale * 4
                            crop_y1 = y1 - scale * 1.5
                            crop_y2 = y2 + scale
                            if crop_x1 > 0 and crop_x2 < width and crop_y1 > 0 and crop_y2 < height:
                                object_image = image_np[int(crop_y1):int(crop_y2), int(crop_x1):int(crop_x2)]
                            else:
                                crop_x1 = x1 - object_width / 4
                                crop_x2 = x2 + object_width / 4
                                crop_y1 = y1 - object_height / 4
                                crop_y2 = y2 + object_height / 4
                                if crop_x1 > 0 and crop_x2 < width and crop_y1 > 0 and crop_y2 < height:
                                    object_image = image_np[int(crop_y1):int(crop_y2),
                                                   int(crop_x1):int(crop_x2)]
                                else:
                                    object_image = image_np[int(y1):int(y2), int(x1):int(x2)]
                else:
                    crop_x1 = x1 - object_width / 4
                    crop_x2 = x2 + object_width / 4
                    crop_y1 = y1 - object_height / 4
                    crop_y2 = y2 + object_height / 4
                    if crop_x1 > 0 and crop_x2 < width and crop_y1 > 0 and crop_y2 < height:
                        object_image = image_np[int(crop_y1):int(crop_y2),
                                       int(crop_x1):int(crop_x2)]
                    else:
                        object_image = image_np[int(y1):int(y2), int(x1):int(x2)]

            else:
                object_image = image_np[int(y1):int(y2), int(x1):int(x2)]

    cropfilename = os.path.splitext(strImagePath)[0]
    strObjectImagePath = os.path.basename(cropfilename) + '_crop.jpg'
    cv2.imwrite(strObjectImagePath, object_image)
    
    #gs_url = upload_gcloud_storage(strObjectImagePath)
    return (object_name, strObjectImagePath)

def getCropImage(strImagePath):
    full_path = os.path.splitext(strImagePath)[0]
    file_name = os.path.basename(full_path)
    jsonfile = file_name + '_crop.json'

    object_name, image_path = cropImage(strImagePath)
    with open(image_path, 'rb') as open_file:
        byte_content = open_file.read()

    base64_bytes = base64.b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8')

    data = {}
    data['crop_image'] = {}
    data['crop_image'].append({
        'crop_data': base64_string,
        'object_name' : str(object_name)
    })

    data['version'] = {}
    data['version'].append({
        'Name': APP_NAME,
        'version': str(APP_VERSION)
    })

    with open(jsonfile, 'w') as outfile:
        json.dump(data, outfile)

    return data, jsonfile

