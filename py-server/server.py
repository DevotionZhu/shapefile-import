from flask import Flask, request, Response
import json
import os
import tempfile
import zipfile

from shape_importer.shp2pgsql import shape2pgsql
from shape_importer.tab2pgsql import shape2pgsql as ogr2ogr
from shape_importer.util import walk2
from db_utils.postgis import geojson_from_table
from gdal_utils.metadata_finder import get_srid_from_prj, get_encoding_from_dbf


STATIC_FOLDER = '../client'
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
        shp_file = prj_file = dbf_file = ''

        z.extractall(temp_dir)
        _, _, files, _ = walk2(temp_dir).next()
        for f in files:
            if f.endswith('.shp'):
                shp_file = os.path.join(temp_dir, f)
            if f.endswith('.prj'):
                prj_file = os.path.join(temp_dir, f)
            if f.endswith('.dbf'):
                dbf_file = os.path.join(temp_dir, f)
            if shp_file and prj_file and dbf_file:
                break
        srid = get_srid_from_prj(prj_file)
        encoding = get_encoding_from_dbf(dbf_file)
        return shp_file, srid, encoding


def user_from_request(request):
    username = request.headers.get('X-MyGov-Authentication')
    return username


@app.route('/api/import/shp2pgsql', methods=['POST'])
def import_shapefile_shp2pgsql():
    if request.method != 'POST':
        return

    (filename, srid, encoding) = create_shapefile(request.files['file'])

    user_name = user_from_request(request)
    table_name = shape2pgsql(CONFIG, user_name, filename, srid, encoding)
    geojson_data = geojson_from_table(CONN_STRING, table_name)

    return Response(
        json.dumps([{'data': geojson_data}]), mimetype='application/json')


# TODO: Make this work
@app.route('/api/import/ogr2ogr')
def import_shapefile_ogr2ogr():
    zip_name = '/vagrant/shapefiles/streetshighways.zip'
    filename = create_shapefile(zip_name)

    ogr2ogr(CONFIG, filename)
    return '200'


if __name__ == '__main__':
    app.run(port=4002, host='0.0.0.0', debug=True)
