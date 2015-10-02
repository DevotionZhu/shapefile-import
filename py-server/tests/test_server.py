import unittest
import mock
import os

from server import *
from werkzeug.datastructures import FileStorage


GEOJSON_DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    'data/other/markers.json'
)


class ServerTest(unittest.TestCase):

    def setUp(self):
        self.geojson_data = open(GEOJSON_DATA_FILE).read()
        config_test_file = os.getenv("APP_CONFIG_FILE")
        if not config_test_file or not config_test_file.endswith('testing.py'):
            self.skipTest(
                "Please run `export " +
                "APP_CONFIG_FILE=/vagrant/shapefile-import/config/testing.py`"
            )

    def test_connection_string(self):
        self.assertEqual(
            CONN_STRING,
            "dbname=mygov_test user=mygov_test password=mygov_test"
        )

    def test_allowed_file_not_zip(self):
        text_file = allowed_file('aa.txt')
        self.assertFalse(text_file)

    def test_allowed_file_zip(self):
        zip_file = allowed_file('aa.zip')
        self.assertTrue(zip_file)

    def test_get_shp_prj_dbf_files_from_tree_has_shp_dbf_prj(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        files_to_compare = {
            'shp': 'data/test/streetshighways892015_749_210833.shp',
            'dbf': 'data/test/streetshighways892015_749_210833.dbf',
            'prj': 'data/test/streetshighways892015_749_210833.prj'
        }

        files_to_return = get_shp_prj_dbf_files_from_tree(
            current_dir + '/data/test'
        )

        self.assertIn(files_to_compare['shp'], files_to_return['shp'])
        self.assertIn(files_to_compare['dbf'], files_to_return['dbf'])
        self.assertIn(files_to_compare['dbf'], files_to_return['dbf'])

    def test_get_shp_prj_dbf_files_from_tree_has_none(self):
        files_to_return = get_shp_prj_dbf_files_from_tree('/data/fake')
        self.assertEqual(files_to_return, {})

    # @TODO other tests
    # test_get_shp_prj_dbf_files_from_tree_has_shp
    # test_get_shp_prj_dbf_files_from_tree_has_dbf
    # test_get_shp_prj_dbf_files_from_tree_has_prj

    def test_extract_zip_no_filestream(self):
        files_to_return = extract_zip(None)
        self.assertEqual(files_to_return, None)

    def test_extract_zip_no_zip_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        txt_file = current_dir + '/data/StreetsHighways.txt'

        file = None
        with open(txt_file, 'rb') as fp:
            file = FileStorage(fp)
            files_to_return = extract_zip(file)
            self.assertEqual(files_to_return, None)

    @mock.patch('server.get_shp_prj_dbf_files_from_tree')
    def test_extract_zip(self, mock_get_shp_prj_dbf_files_from_tree):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        zip_file = current_dir + '/data/StreetsHighways.zip'

        files_to_return = {
            'shp': 'data/test/streetshighways892015_749_210833.shp',
            'dbf': 'data/test/streetshighways892015_749_210833.dbf',
            'prj': 'data/test/streetshighways892015_749_210833.prj'
        }

        file = None
        with open(zip_file, 'rb') as fp:
            file = FileStorage(fp)
            mock_get_shp_prj_dbf_files_from_tree.return_value = files_to_return
            files_to_return = extract_zip(file)

            self.assertEqual(files_to_return['shp'], files_to_return['shp'])
            self.assertEqual(files_to_return['dbf'], files_to_return['dbf'])
            self.assertEqual(files_to_return['dbf'], files_to_return['dbf'])

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

    @mock.patch('server.extract_zip')
    @mock.patch('server.shutil')
    @mock.patch('server.tempfile')
    def test_get_data_from_files_no_files(
        self, mock_tempfile, mock_shutil, mock_extract_zip
    ):
        mock_tempfile.mkdtemp.return_value = '/data/test'
        mock_shutil.rmtree.return_value = True
        mock_extract_zip.return_value = None

        file = '/data/test'
        data = get_data_from_files(file)
        self.assertEqual(data, None)

    @mock.patch('server.get_encoding_from_dbf')
    @mock.patch('server.get_srid_from_prj')
    @mock.patch('server.extract_zip')
    @mock.patch('server.shutil')
    @mock.patch('server.tempfile')
    def test_get_data_from_files(
        self, mock_tempfile, mock_shutil, mock_extract_zip,
        mock_get_srid, mock_get_encoding
    ):
        mock_tempfile.mkdtemp.return_value = '/data/test'
        mock_shutil.rmtree.return_value = True
        files_to_return = {
            'shp': 'data/test/streetshighways892015_749_210833.shp',
            'dbf': 'data/test/streetshighways892015_749_210833.dbf',
            'prj': 'data/test/streetshighways892015_749_210833.prj'
        }
        mock_extract_zip.return_value = files_to_return
        mock_get_srid.return_value = '4326'
        mock_get_encoding.return_value = 'LATIN1'

        file = '/data/test'
        data = get_data_from_files(file)

        self.assertEqual(
            data['shape'], 'data/test/streetshighways892015_749_210833.shp'
        )
        self.assertEqual(data['srid'], '4326')
        self.assertEqual(data['encoding'], 'LATIN1')

    @mock.patch('server.geojson_from_table')
    @mock.patch('server.shape2pgsql')
    @mock.patch('server.user_from_request')
    def test_get_geojson(self, mock_user, mock_shape2pgsql, mock_geojson):
        mock_user.return_value = None
        mock_shape2pgsql.return_value = 'table_test'
        mock_geojson.return_value = self.geojson_data
        geojson = get_geojson({}, {'shape': '', 'srid': '', 'encoding': ''})
        self.assertEqual(geojson, self.geojson_data)

    @mock.patch('server.request')
    def test_import_shapefile_shp2pgsql_no_method_post(self, mock_request):
        mock_request.method = 'GET'
        response = import_shapefile_shp2pgsql()
        self.assertEqual(response, None)

    @mock.patch('server.get_data_from_files')
    @mock.patch('server.request')
    def test_import_shapefile_shp2pgsql_no_data(
        self, mock_request, mock_get_data
    ):
        mock_request.method = 'POST'
        mock_get_data.return_value = None
        response = import_shapefile_shp2pgsql()
        self.assertEqual(response, None)

    @mock.patch('server.get_data_from_files')
    @mock.patch('server.request')
    def test_import_shapefile_shp2pgsql_no_shape(
        self, mock_request, mock_get_data
    ):
        mock_request.method = 'POST'
        mock_get_data.return_value = {}
        response = import_shapefile_shp2pgsql()
        self.assertEqual(response, None)

    @mock.patch('server.get_geojson')
    @mock.patch('server.get_data_from_files')
    @mock.patch('server.request')
    def test_import_shapefile_shp2pgsql(
        self, mock_request, mock_get_data, mock_get_geojson
    ):
        mock_request.method = 'POST'
        mock_get_data.return_value = {
            'shape': 'test'
        }
        mock_get_geojson.return_value = self.geojson_data
        import_shapefile_shp2pgsql()
        # @TODO assert
