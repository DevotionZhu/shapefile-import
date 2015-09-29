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
      self.assertEqual(files_to_return, {})

    def test_get_shp_prj_dbf_files_no_zipfile(self):
      current_dir = os.path.dirname(os.path.realpath(__file__))
      txt_file = current_dir + '/data/StreetsHighways.txt'

      file = None
      with open(txt_file, 'rb') as fp:
        file = FileStorage(fp)
        files_to_return = get_shp_prj_dbf_files(file, current_dir + '/data/test')
        self.assertEqual(files_to_return, {})







