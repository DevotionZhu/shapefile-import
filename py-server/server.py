from flask import Flask, request, Response
import json
import os
import fnmatch
import tempfile
import shutil
import zipfile

from shape_importer.shp2pgsql import shape2pgsql
from shape_importer.tab2pgsql import shape2pgsql as ogr2ogr
from db_utils.postgis import geojson_from_table
from gdal_utils.metadata_finder import get_srid_from_prj, get_encoding_from_dbf

STATIC_FOLDER = '../client'

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
app.config.from_envvar('APP_CONFIG_FILE')

CONN_STRING = 'dbname={dbname} user={user} password={password}'.format(
    dbname=app.config['DB_NAME'],
    user=app.config['DB_USER'],
    password=app.config['DB_PASSWORD']
)
ALLOWED_EXTENSIONS = 'zip'


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_shp_prj_dbf_files_from_tree(temp_dir):
    files_to_return = {}
    patterns = ['[a-zA-Z]*.shp', '[a-zA-Z]*.prj', '[a-zA-Z]*.dbf']

    for path, dirs, files in os.walk(os.path.abspath(temp_dir)):
        for extension in patterns:
            for filename in fnmatch.filter(files, extension):
                files_to_return[extension[-3:]] = os.path.join(path, filename)

    return files_to_return


def extract_zip(filestream, temp_dir):
    if not filestream or not allowed_file(filestream.filename):
        return

    with zipfile.ZipFile(filestream, 'r') as z:
        z.extractall(temp_dir)
        files_to_return = get_shp_prj_dbf_files_from_tree(temp_dir)

        return files_to_return


def user_from_request(request):
    username = request.headers.get('X-MyGov-Authentication')
    return username


def get_data_from_files(file):
    temp_dir = tempfile.mkdtemp()
    files = extract_zip(file, temp_dir)

    if not files or not files['shp']:
        shutil.rmtree(os.path.abspath(temp_dir))
        return

    data = {
        'shape': files['shp']
    }
    data['srid'] = get_srid_from_prj(files['prj'] or '')
    data['encoding'] = get_encoding_from_dbf(files['dbf'] or '')

    shutil.rmtree(os.path.abspath(temp_dir))

    return data


def get_geojson(request, data):
    user_name = user_from_request(request) or 'client_test'
    table_name = shape2pgsql(
        app.config, user_name, data['shape'], data['srid'], data['encoding']
    )
    geojson_data = geojson_from_table(CONN_STRING, table_name)

    return geojson_data


@app.route('/api/import/shp2pgsql', methods=['POST'])
def import_shapefile_shp2pgsql():
    if request.method != 'POST':
        return

    data = get_data_from_files(request.files['file'])

    if not data or not data['shape']:
        return

    geojson_data = get_geojson(request, data)

    return Response(
        json.dumps([{'data': geojson_data}]), mimetype='application/json')


# TODO: Make this work
@app.route('/api/import/ogr2ogr')
def import_shapefile_ogr2ogr():  # pragma: no cover
    zip_file = '/vagrant/shapefiles/streetshighways.zip'
    filename = create_shapefile(zip_file)

    ogr2ogr(app.config, filename)
    return '200'

if __name__ == '__main__':  # pragma: no cover
    app.run(port=4002, host='0.0.0.0', debug=True)
