from flask import Flask, Response
from shape_importer.shp2pgsql import shape2pgsql

STATIC_FOLDER = "static"
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
CONN_STRING = 'dbname=mygov user=mygov password=mygov'


@app.route('/api/import')
def import_shapefile():
    filename = '/vagrant/shapefiles/firehydrants_749_210833.shp'
    shape2pgsql(
      {
      "db":
        {
          "user": "mygov",
          "name":"mygov",
          "password":"mygov",
          "host":"localhost"
        },
      "user": "mygov1",
      "shp2pgsql": "shp2pgsql"
      },
      filename)
    return '200'


if __name__ == '__main__':
    app.run(port=4002, host='0.0.0.0', debug=False)
