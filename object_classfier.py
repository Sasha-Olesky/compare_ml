
import os
import tensorflow as tf
import cv2
import json
import base64

from utils import label_map_util
from utils import visualization_utils as vis_util
from hash_compare import *
from ssim_compare import *
#from surf_compare import *
from face_compare import *
from histogram_compare import *

PATH_TO_CKPT = 'model/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('model', 'mscoco_label_map.pbtxt')

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
        width = (xmax - xmin) * width
        height = (ymax - ymin) * height
        area = width * height
        if area > biggest_area:
            biggest_area = area
            object_name = name
            object_image = image_np[round(y1):round(y2), round(x1):round(x2)]

    name = os.path.splitext(strImagePath)[0]
    strObjectImagePath = os.path.basename(name) + '.jpg'
    cv2.imwrite(strObjectImagePath, object_image)
    return (object_name, object_image)

def getJsonData(strImagePath):
    full_path = os.path.splitext(strImagePath)[0]
    file_name = os.path.basename(full_path)
    jsonfile = file_name + '.json'

    object_name, object_image = object_detection(strImagePath)
    hash_value = get_hash(object_image)
    hist_value = get_hist(object_image)

    imagefile = file_name + '.jpg'
    with open(imagefile, 'rb') as open_file:
        byte_content = open_file.read()

    base64_bytes = base64.b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8')

    data = {}
    data['object'] = []
    data['object'].append({
        'object_name': str(object_name),
        'hash_value': str(hash_value),
        'hist_value': str(hist_value),
        'image': base64_string
    })

    data['version'] = []
    data['version'].append({
        'Name': 'ML Image Compare',
        'version': '1.0'
    })

    with open(jsonfile, 'w') as outfile:
        json.dump(data, outfile)

    return data, jsonfile, imagefile

# compare image api
def image_classfier(strFirstImage, strSecondImage, first_object_name, second_object_name):
    first_object_image = cv2.imread(strFirstImage)
    second_object_image = cv2.imread(strSecondImage)

    ssim_similar = ssim_compare(strFirstImage, strSecondImage)
    if ssim_similar == 'Same Image':
        return ssim_similar

    if first_object_name == '' and second_object_name == '':
        hash_result = hash_compare(first_object_image, second_object_image)
        if hash_result == 'Same Image':
            return hist_compare(first_object_image, second_object_image)
        else:
            return 'Different Image'
    elif first_object_name == second_object_name:
        if first_object_name == 'person':
            return face_compare(first_object_image, second_object_image)
        elif first_object_name == 'N/A':
            hash_result = hash_compare(first_object_image, second_object_image)
            return hash_result
        else:
            hash_result = hash_compare(first_object_image, second_object_image)
            if hash_result == 'Same Image':
                hist_result = hist_compare(first_object_image, second_object_image)
                return hist_result
            else:
                return hash_result
    else:
        return 'Different Image'

def image_classfier_json_local(strFirstJson, strSecondJson):
    with open(strFirstJson, 'r') as f:
        firstData = json.load(f)

    with open(strSecondJson, 'r') as f:
        secondData = json.load(f)

    return image_classfier_json(firstData, secondData)

def image_classfier_json(firstData, secondData):
    first_version_data = firstData['version'][0]
    first_version = first_version_data['version']
    second_version_data = secondData['version'][0]
    second_version = second_version_data['version']
    if first_version != second_version:
        return createReturnJson(401, 'Json Version Error')

    first_object = firstData['object'][0]
    first_object_name = first_object['object_name']
    first_image_base64_string = first_object['image']
    first_image_base64_bytes = first_image_base64_string.encode('utf-8')
    first_image_decode_bytes = base64.b64decode(first_image_base64_bytes)
    first_image = open('first.png', 'wb')
    first_image.write(first_image_decode_bytes)

    second_object = secondData['object'][0]
    second_object_name = second_object['object_name']
    second_image_base64_string = second_object['image']
    second_image_base64_bytes = second_image_base64_string.encode('utf-8')
    second_image_decode_bytes = base64.b64decode(second_image_base64_bytes)
    second_image = open('second.png', 'wb')
    second_image.write(second_image_decode_bytes)

    compare_result = image_classfier('first.png', 'second.png', first_object_name, second_object_name)
    os.remove('first.png')
    os.remove('second.png')

    if compare_result == 'Same Image':
        return createReturnJson(1, compare_result)
    else:
        return createReturnJson(0, compare_result)

def createReturnJson(code, detail):
    data = {}
    data['result'] = []
    data['result'].append({
        'result_code': str(code),
        'detail': detail
    })

    data['version'] = []
    data['version'].append({
        'Name': 'ML Image Compare',
        'version': '1.0'
    })

    with open('result.json', 'w') as outfile:
        json.dump(data, outfile)

    return data

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
    for box, name in objects.items():
        ymin, xmin, ymax, xmax = box
        x1 = xmin * width
        y1 = ymin * height
        x2 = xmax * width
        y2 = ymax * height
        width = (xmax - xmin) * width
        height = (ymax - ymin) * height
        area = width * height
        if area > biggest_area:
            biggest_area = area
            object_name = name
            object_image = image_np[round(y1):round(y2), round(x1):int(x2)]

    name = os.path.splitext(strImagePath)[0]
    strObjectImagePath = os.path.basename(name) + '_crop.jpg'
    cv2.imwrite(strObjectImagePath, object_image)
    directory = '/var/www/html/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    strFinalImagePath = directory + name + '_crop.jpg'
    os.rename(strObjectImagePath, strFinalImagePath)
    strObjectImagePath = 'http://146.148.111.219/' + strFinalImagePath
    return (object_name, strObjectImagePath)

def getCropImage(strImagePath):
    full_path = os.path.splitext(strImagePath)[0]
    file_name = os.path.basename(full_path)
    jsonfile = file_name + '_crop.json'

    object_name, image_path = cropImage(strImagePath)

    data = {}
    data['crop_image'] = []
    data['crop_image'].append({
        'image_path': str(image_path),
        'object_name': str(object_name),
    })

    data['version'] = []
    data['version'].append({
        'Name': 'ML Image Compare',
        'version': '1.0'
    })

    with open(jsonfile, 'w') as outfile:
        json.dump(data, outfile)

    return data, jsonfile

