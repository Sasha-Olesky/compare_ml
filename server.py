from flask import Flask, request, redirect
from flask_restful import Api, Resource, reqparse
from object_classfier import *
import urllib

app = Flask(__name__)
api = Api(app)

class ImageUpload(Resource):
    server_idx = 0
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

        try:
            urllib.request.urlretrieve(image_url, file_name)
            jsonFile, jsonpath = getJsonData(file_name, self.server_idx)
            self.server_idx += 1
            os.remove(file_name)
            os.remove(jsonpath)
        except:
            jsonFile = 'cannot find image_url. please input correct url.'

        return jsonFile, 201

class ImageCompare(Resource):
    def post(self):
        content = request.get_json()

        firstData = content['first_data']
        secondData = content['second_data']

        result, jsonpath = image_compare_server(firstData, secondData)
        os.remove(jsonpath)
        return result, 200

class ImageSimilarity(Resource):
    def post(self):
        content = request.get_json()

        firstData = content['first_data']
        secondData = content['second_data']

        result, jsonpath = image_similar_server(firstData, secondData)
        os.remove(jsonpath)
        return result, 203

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
api.add_resource(ImageSimilarity, '/image_similar')
api.add_resource(GetCropImageView, '/')

app.run(host='0.0.0.0')
