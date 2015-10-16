from flask import Flask, request, Response, jsonify
import json
import os
import fnmatch
import tempfile
import shutil
import zipfile


from error import InvalidUsage
from shape_importer.shp2pgsql import shape2pgsql
from shape_importer.tab2pgsql import shape2pgsql as ogr2ogr
from db_utils.postgis import geojson_from_table
from gdal_utils.metadata_finder import get_srid_from_prj, get_encoding_from_dbf
from werkzeug import secure_filename

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


def get_shp_prj_dbf_shx_files_from_tree(temp_dir):
    files_to_return = {}
    patterns = [
        '[a-zA-Z]*.shp',
        '[a-zA-Z]*.prj',
        '[a-zA-Z]*.dbf',
        '[a-zA-Z]*.shx'
    ]

    for path, dirs, files in os.walk(os.path.abspath(temp_dir)):
        for extension in patterns:
            for filename in fnmatch.filter(files, extension):
                files_to_return[extension[-3:]] = os.path.join(path, filename)

    if not files_to_return or not files_to_return['shp'] or \
        not files_to_return['prj'] or \
        not files_to_return['dbf'] or \
            not files_to_return['shx']:
            raise InvalidUsage(
                'A shapefile must contain shp, prj, dbf, shx files',
                status_code=500
            )

    return files_to_return


def extract_zip(filestream, temp_dir):

    if not filestream or not allowed_file(filestream.filename):
        raise InvalidUsage(
            'No filestream or no zipfile',
            status_code=500
        )

    with zipfile.ZipFile(filestream, 'r') as z:
        z.extractall(temp_dir)
        files_to_return = get_shp_prj_dbf_shx_files_from_tree(temp_dir)

        return files_to_return


def get_shape_srid_encoding(files, temp_dir):

    data = {
        'shape': files['shp']
    }
    data['srid'] = get_srid_from_prj(files['prj'])
    data['encoding'] = get_encoding_from_dbf(files['dbf'])

    return data


def get_data_from_zipfile(file, temp_dir):
    files = extract_zip(file, temp_dir)

    data = get_shape_srid_encoding(files, temp_dir)

    return data


def get_data_from_files(filestreams, temp_dir):

    for file in filestreams:
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(temp_dir, filename))

    files = get_shp_prj_dbf_shx_files_from_tree(temp_dir)

    data = get_shape_srid_encoding(files, temp_dir)

    return data


def get_geojson(request, data):
    table_name = shape2pgsql(
        app.config, data['shape'], data['srid'], data['encoding']
    )
    geojson_data = geojson_from_table(CONN_STRING, table_name)

    return geojson_data


def get_data_from_request(files_from_request, temp_dir):
    files = files_from_request.getlist('file')
    data = None
    if len(files) is 1:
        data = get_data_from_zipfile(files[0], temp_dir)
    if len(files) is 4:
        data = get_data_from_files(files, temp_dir)

    if not data:
        raise InvalidUsage(
            'Please upload a zip or 4 files(shp, dbf, shx, prj)',
            status_code=500
        )
    return data


@app.route('/api/import/shp2pgsql', methods=['POST'])
def import_shapefile_shp2pgsql():
    if request.method != 'POST':
        raise InvalidUsage('Method allowed is POST', status_code=405)

    temp_dir = tempfile.mkdtemp()

    data = get_data_from_request(request.files, temp_dir)
    if not data or not data['shape']:
        shutil.rmtree(os.path.abspath(temp_dir))
        raise InvalidUsage('No data or no shp file found', status_code=500)

    geojson_data = get_geojson(request, data)
    shutil.rmtree(os.path.abspath(temp_dir))

    return Response(
        json.dumps([{'data': geojson_data}]), mimetype='application/json')


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# TODO: Make this work
@app.route('/api/import/ogr2ogr')
def import_shapefile_ogr2ogr():  # pragma: no cover
    zip_file = '/vagrant/shapefiles/streetshighways.zip'
    filename = create_shapefile(zip_file)

    ogr2ogr(app.config, filename)
    return '200'

if __name__ == '__main__':  # pragma: no cover
    app.run(port=4002, host='0.0.0.0', debug=True)
