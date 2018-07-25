from flask import Flask, request, redirect
from flask_restful import Api, Resource, reqparse
from object_classfier import *
import urllib

app = Flask(__name__)
api = Api(app)

class ImageUpload(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image_url')
        args = parser.parse_args()

        image_url = args['image_url'];
        file_name = image_url.split('/')[-1]
        file_name = file_name.replace('$', '_')
        file_name = file_name.replace('@', '_')
        file_name = file_name.replace('!', '_')
        file_name = file_name.replace('#', '_')
        file_name = file_name.replace('%', '_')
        file_name = file_name.replace('^', '_')
        file_name = file_name.replace('&', '_')
        file_name = file_name.replace('~', '_')
        file_name = file_name.replace('|', '_')
        file_name = file_name.replace('\"', '_')

        urllib.request.urlretrieve(image_url, file_name)
        jsonFile, jsonpath, imagepath = getJsonData(file_name)
        os.remove(imagepath)
        os.remove(jsonpath)
        return jsonFile, 201

class ImageCompare(Resource):
    def post(self):
        content = request.get_json()

        firstData = content['first_data']
        secondData = content['second_data']

        result = image_classfier_json(firstData, secondData)
        return result, 200

class GetCropImage(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image_url')
        args = parser.parse_args()

        image_url = args['image_url'];
        file_name = image_url.split('/')[-1]
        file_name = file_name.replace('$', '_')
        file_name = file_name.replace('@', '_')
        file_name = file_name.replace('!', '_')
        file_name = file_name.replace('#', '_')
        file_name = file_name.replace('%', '_')
        file_name = file_name.replace('^', '_')
        file_name = file_name.replace('&', '_')
        file_name = file_name.replace('~', '_')
        file_name = file_name.replace('|', '_')
        file_name = file_name.replace('\"', '_')

        urllib.request.urlretrieve(image_url, file_name)
        jsonFile, jsonpath = getCropImage(file_name)
        os.remove(file_name)
        os.remove(jsonpath)
        return jsonFile, 202

class GetCropImageView(Resource):
    def get(self):
        name = request.args.get('name')
        ip_address = get('https://api.ipify.org').text
        redirect_url = 'http://' + str(ip_address) + '/' + name
        return redirect(redirect_url, 302)

api.add_resource(ImageUpload, '/image_upload')
api.add_resource(GetCropImage, '/image_crop')
api.add_resource(ImageCompare, '/image_compare')
api.add_resource(GetCropImageView, '/')

app.run(host='0.0.0.0')
