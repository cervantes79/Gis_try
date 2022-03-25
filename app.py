from flask import Flask, render_template, jsonify, request
import load_data
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
app.secret_key = 'Superstar'
api = Api(app)
baseUrl = "/api/"


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/loaddata')
def load():
    return jsonify(load_data.check_db())


@app.route('/addresses')
def addresses():
    """ It gets 3 parameters
        sw: south west point of bounding box,
            Example sw=-11.962067381231293,51.81965717678804
        ne: north east point of bounding box,
            Example ne=5.31906738123115,56.60417303370079
        zoom: zoom level, Example zoom=5.51

        it returns list of dictionaries with keys below:
        [{'latitude':'','longitude':'','count':''}]
        """
    sw = request.args.get('sw')
    ne = request.args.get('ne')
    zoom = request.args.get('zoom')
    if zoom is None:
        zoom = 5.51
    if sw is None:
        sw = "-11.962067381231293,51.81965717678804"
    if ne is None:
        ne = "5.31906738123115,56.60417303370079"

    result_data = load_data.get_data(sw, ne, zoom)
    return jsonify(result_data)


class webAddresses(Resource):
    def __init__(self, *args, **kwargs):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sw', type=str, location='json')
        self.reqparse.add_argument('en', type=str, location='json')
        self.reqparse.add_argument('zoom', type=str, location='json')
        super(webAddresses, self).__init__(*args, **kwargs)

    def get(self):
        """ It gets 3 parameters
        sw: south west point of bounding box,
            Example sw=-11.962067381231293,51.81965717678804
        ne: north east point of bounding box,
            Example ne=5.31906738123115,56.60417303370079
        zoom: zoom level, Example zoom=5.51

        it returns list of dictionaries with keys below:
        [{'latitude':'','longitude':'','count':''}]
        """
        args = self.reqparse.parse_args()
        sw = args.get("sw")
        ne = args.get("ne")
        zoom = args.get("zoom")
        if zoom is None:
            zoom = 5.51
        if sw is None:
            sw = "-11.962067381231293,51.81965717678804"
        if ne is None:
            ne = "5.31906738123115,56.60417303370079"

        result_data = load_data.get_data(sw, ne, zoom)

        return jsonify(result_data)

    def post(self):
        """ It gets 3 parameters
        sw: south west point of bounding box,
            Example sw=-11.962067381231293,51.81965717678804
        ne: north east point of bounding box,
            Example ne=5.31906738123115,56.60417303370079
        zoom: zoom level, Example zoom=5.51

        it returns list of dictionaries with keys below:
        [{'latitude':'','longitude':'','count':''}]
        """
        args = self.reqparse.parse_args()
        sw = args.get("sw")
        ne = args.get("ne")
        zoom = args.get("zoom")
        if zoom is None:
            zoom = 5.51
        if sw is None:
            sw = "-11.962067381231293,51.81965717678804"
        if ne is None:
            ne = "5.31906738123115,56.60417303370079"

        result_data = load_data.get_data(sw, ne, zoom)

        return jsonify(result_data)


api.add_resource(webAddresses, f'{baseUrl}address', endpoint='wAddress')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=83, threaded=True)
