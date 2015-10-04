import unittest
import mock
import os

from server import *
from werkzeug.datastructures import FileStorage


GEOJSON_DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    'data/other/markers.json'
)


class ServerBasicTest(unittest.TestCase):
    def setUp(self):
        self.geojson_data = open(GEOJSON_DATA_FILE).read()

        self.shp_db_prj_files = {
            'shp': 'data/test/streetshighways892015_749_210833.shp',
            'dbf': 'data/test/streetshighways892015_749_210833.dbf',
            'prj': 'data/test/streetshighways892015_749_210833.prj'
        }
        config_test_file = os.getenv("APP_CONFIG_FILE")
        if not config_test_file or not config_test_file.endswith('testing.py'):
            self.skipTest(
                "Please run `export " +
                "APP_CONFIG_FILE=/vagrant/shapefile-import/config/testing.py`"
            )


class ServerAllowedFileTest(ServerBasicTest):

    def test_not_zip(self):
        text_file = allowed_file('aa.txt')
        self.assertFalse(text_file)

    def test_zip(self):
        zip_file = allowed_file('aa.zip')
        self.assertTrue(zip_file)


class ServerGetShpPrjDbfFilesFromTreeTest(ServerBasicTest):

    def test_has_shp_dbf_prj(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        files_to_compare = self.shp_db_prj_files

        files_to_return = get_shp_prj_dbf_files_from_tree(
            current_dir + '/data/test'
        )

        self.assertIn(files_to_compare['shp'], files_to_return['shp'])
        self.assertIn(files_to_compare['dbf'], files_to_return['dbf'])
        self.assertIn(files_to_compare['dbf'], files_to_return['dbf'])

    def test_has_none(self):
        files_to_return = get_shp_prj_dbf_files_from_tree('/data/fake')
        self.assertEqual(files_to_return, {})

    # @TODO other tests
    # test_get_shp_prj_dbf_files_from_tree_has_shp
    # test_get_shp_prj_dbf_files_from_tree_has_dbf
    # test_get_shp_prj_dbf_files_from_tree_has_prj


class ServerExtractZipTest(ServerBasicTest):

    def test_no_filestream(self):
        files_to_return = extract_zip(None)
        self.assertEqual(files_to_return, None)

    def test_no_zip_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        txt_file = current_dir + '/data/StreetsHighways.txt'

        file = None
        with open(txt_file, 'rb') as fp:
            file = FileStorage(fp)
            files_to_return = extract_zip(file)
            self.assertEqual(files_to_return, None)

    @mock.patch('server.get_shp_prj_dbf_files_from_tree')
    def test_all_good(self, mock_get_shp_prj_dbf_files_from_tree):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        zip_file = current_dir + '/data/StreetsHighways.zip'
        files_to_return = self.shp_db_prj_files

        file = None
        with open(zip_file, 'rb') as fp:
            file = FileStorage(fp)
            mock_get_shp_prj_dbf_files_from_tree.return_value = files_to_return
            files_to_return = extract_zip(file)

            self.assertEqual(files_to_return['shp'], files_to_return['shp'])
            self.assertEqual(files_to_return['dbf'], files_to_return['dbf'])
            self.assertEqual(files_to_return['dbf'], files_to_return['dbf'])


class ServerGetDataFromFilesTest(ServerBasicTest):

    @mock.patch('server.extract_zip')
    @mock.patch('server.shutil')
    @mock.patch('server.tempfile')
    def test_no_files(
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
    def test_all_good(
        self, mock_tempfile, mock_shutil, mock_extract_zip,
        mock_get_srid, mock_get_encoding
    ):
        mock_tempfile.mkdtemp.return_value = '/data/test'
        mock_shutil.rmtree.return_value = True
        files_to_return = self.shp_db_prj_files
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


class ServerImportShapefileShp2pgsql(ServerBasicTest):

    @mock.patch('server.request')
    def test_no_post_method(self, mock_request):
        mock_request.method = 'GET'
        response = import_shapefile_shp2pgsql()
        self.assertEqual(response, None)

    @mock.patch('server.get_data_from_files')
    @mock.patch('server.request')
    def test_no_data(
        self, mock_request, mock_get_data
    ):
        mock_request.method = 'POST'
        mock_get_data.return_value = None
        response = import_shapefile_shp2pgsql()
        self.assertEqual(response, None)

    @mock.patch('server.get_data_from_files')
    @mock.patch('server.request')
    def test_no_shape(
        self, mock_request, mock_get_data
    ):
        mock_request.method = 'POST'
        mock_get_data.return_value = {}
        response = import_shapefile_shp2pgsql()
        self.assertEqual(response, None)

    @mock.patch('server.get_geojson')
    @mock.patch('server.get_data_from_files')
    @mock.patch('server.request')
    def test_all_good(
        self, mock_request, mock_get_data, mock_get_geojson
    ):
        mock_request.method = 'POST'
        mock_get_data.return_value = {
            'shape': 'test'
        }
        mock_get_geojson.return_value = self.geojson_data
        import_shapefile_shp2pgsql()
        # @TODO assert


class ServerOtherTest(ServerBasicTest):

    def test_connection_string(self):
        self.assertEqual(
            CONN_STRING,
            "dbname=mygov_test user=mygov_test password=mygov_test"
        )

    @mock.patch('server.geojson_from_table')
    @mock.patch('server.shape2pgsql')
    def test_get_geojson(self, mock_shape2pgsql, mock_geojson):
        mock_shape2pgsql.return_value = 'table_test'
        mock_geojson.return_value = self.geojson_data
        geojson = get_geojson({}, {'shape': '', 'srid': '', 'encoding': ''})
        self.assertEqual(geojson, self.geojson_data)

