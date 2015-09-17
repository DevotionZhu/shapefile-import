from flask import Flask
import os
import tempfile
import zipfile

from shape_importer.shp2pgsql import shape2pgsql
from shape_importer.util import walk2


STATIC_FOLDER = 'static'
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
CONN_STRING = 'dbname=mygov user=mygov password=mygov'


def create_shapefile(input_zip):
    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(input_zip, 'r') as z:
        z.extractall(temp_dir)
        _, _, files, _ = walk2(temp_dir).next()
        for f in files:
            if f.endswith('.shp'):
                return os.path.join(temp_dir, f)


@app.route('/api/import')
def import_shapefile():
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

    shape2pgsql(config, filename)
    return '200'


if __name__ == '__main__':
    app.run(port=4002, host='0.0.0.0', debug=True)
