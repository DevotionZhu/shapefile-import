from flask import Flask, request, Response
import json
import os
import tempfile
import zipfile

from shape_importer.shp2pgsql import shape2pgsql
from shape_importer.tab2pgsql import shape2pgsql as ogr2ogr
from shape_importer.util import walk2
from db_utils.postgis import geojson_from_table


STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = 'zip'

CONN_STRING = 'dbname=mygov user=mygov password=mygov'
CONFIG = dict(
    db=dict(
        user='mygov',
        name='mygov',
        password='mygov',
        host='localhost'),
    user='mygov1',
    shp2pgsql='shp2pgsql')

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_shapefile(filestream):
    temp_dir = tempfile.mkdtemp()

    if not filestream or not allowed_file(filestream.filename):
        return

    with zipfile.ZipFile(filestream, 'r') as z:
        z.extractall(temp_dir)
        _, _, files, _ = walk2(temp_dir).next()
        for f in files:
            if f.endswith('.shp'):
                return os.path.join(temp_dir, f)


@app.route('/api/import/shp2pgsql', methods=['POST'])
def import_shapefile_shp2pgsql():
    if request.method != 'POST':
        return

    filename = create_shapefile(request.files['file'])

    table_name = shape2pgsql(CONFIG, filename)
    geojson_data = geojson_from_table(CONN_STRING, table_name)

    return Response(
        json.dumps([{'data': geojson_data}]), mimetype='application/json')


# TODO: Make this work
@app.route('/api/import/ogr2ogr')
def import_shapefile_ogr2ogr():
    zip_name = '/vagrant/shapefiles/streetshighways.zip'
    filename = create_shapefile(zip_name)

    config = dict(
        db=dict(
            user='mygov',
            name='mygov',
            password='mygov',
            host='localhost'),
        user='mygov1',
        shp2pgsql='shp2pgsql')

    ogr2ogr(config, filename)
    return '200'


if __name__ == '__main__':
    app.run(port=4002, host='0.0.0.0', debug=True)
