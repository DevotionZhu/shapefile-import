import unittest
import mock
import os
from server import *
from werkzeug.datastructures import FileStorage

class ServerTest(unittest.TestCase):

    def setUp(self):
      configTestFile = os.getenv("APP_CONFIG_FILE")
      if not configTestFile or not configTestFile.endswith('testing.py'):
        self.skipTest("Please run `export APP_CONFIG_FILE=/vagrant/shapefile-import/config/testing.py`")

    def test_connection_string(self):
      self.assertEqual(CONN_STRING, "dbname=mygov_test user=mygov_test password=mygov_test")

    def test_allowed_file_not_zip(self):
      textFile = allowed_file('aa.txt')
      self.assertFalse(textFile)

    def test_allowed_file_zip(self):
      zipFile = allowed_file('aa.zip')
      self.assertTrue(zipFile)

    def test_get_shp_prj_dbf_files(self):
      current_dir = os.path.dirname(os.path.realpath(__file__))
      zip_file = current_dir + '/data/StreetsHighways.zip'

      files_to_compare = {
        'shp': 'data/test/streetshighways892015_749_210833.shp',
        'dbf': 'data/test/streetshighways892015_749_210833.dbf',
        'prj': 'data/test/streetshighways892015_749_210833.prj'
      }

      file = None
      with open(zip_file, 'rb') as fp:
        file = FileStorage(fp)
        files_to_return = get_shp_prj_dbf_files(file, current_dir + '/data/test')

        self.assertIn(files_to_compare['shp'], files_to_return['shp'])
        self.assertIn(files_to_compare['dbf'], files_to_return['dbf'])
        self.assertIn(files_to_compare['dbf'], files_to_return['dbf'])

    def test_get_shp_prj_dbf_files_no_filestream(self):
      files_to_return = get_shp_prj_dbf_files(None, '/data/test')
      self.assertEqual(files_to_return, None)

    def test_get_shp_prj_dbf_files_no_zipfile(self):
      current_dir = os.path.dirname(os.path.realpath(__file__))
      txt_file = current_dir + '/data/StreetsHighways.txt'

      file = None
      with open(txt_file, 'rb') as fp:
        file = FileStorage(fp)
        files_to_return = get_shp_prj_dbf_files(file, current_dir + '/data/test')
        self.assertEqual(files_to_return, None)

    @mock.patch('server.request')
    def test_user_from_request(self, mock_request):
      mock_request.headers = {
        'X-MyGov-Authentication': 'Test User'
      }
      user_name = user_from_request(mock_request)
      self.assertEqual(user_name, 'Test User')

    @mock.patch('server.request')
    def test_user_from_request_none(self, mock_request):
      mock_request.headers = {
        'No-MyGov-Authentication': ''
      }
      user_name = user_from_request(mock_request)
      self.assertEqual(user_name, None)

    @mock.patch('server.request')
    def test_import_shapefile_shp2pgsql_no_method_post(self, mock_request):
      mock_request.method = 'GET'
      response = import_shapefile_shp2pgsql()
      self.assertEqual(response, None)

    @mock.patch('server.geojson_from_table')
    @mock.patch('server.shape2pgsql')
    @mock.patch('server.shutil')
    @mock.patch('server.tempfile')
    @mock.patch('server.request')
    def test_import_shapefile_shp2pgsql(self, mock_request, mock_tempfile, mock_shutil, mock_shape2pgsql, mock_geojson_from_table):
      mock_request.method = 'POST'
      mock_request.headers = {
        'X-MyGov-Authentication': 'test_user'
      }
      current_dir = os.path.dirname(os.path.realpath(__file__))
      zip_file = current_dir + '/data/StreetsHighways.zip'
      mock_request.files = {
        'file': None
      }
      with open(zip_file, 'rb') as fp:
        mock_request.files = {
          'file': FileStorage(fp)
        }
        mock_tempfile.mkdtemp.return_value = current_dir + '/data/test'
        mock_shutil.rmtree.return_value = True
        mock_shape2pgsql.return_value = 'test_table_name'
        mock_geojson_from_table.return_value = {
            "type": "FeatureCollection",
            "features": [
            {
                "type": "Feature",
                "properties": {
                    "title": "Phil",
                    "description": "Van",
                    "deliveries": 3,
                    "pendingDeliveries": 15,
                    "pickups": 4,
                    "pendingPickups": 7,
                    "shiftTime": "07:00-16:00"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        174.7554874420166,
                        -41.278838514514064
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "title": "Rick",
                    "description": "Truck"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        174.7734260559082,
                        -41.29354341293027
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "title": "Tony",
                    "description": "Scooter"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        174.77797508239746,
                        -41.30714894088784
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "title": "Al",
                    "description": "Van"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        174.759521484375,
                        -41.302119739913735
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "title": "Mike",
                    "description": "Truck"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        174.8013210296631,
                        -41.290318938190254
                    ]
                }
            }
        ]
        }
        response = import_shapefile_shp2pgsql()
        #TODO: some asserts









