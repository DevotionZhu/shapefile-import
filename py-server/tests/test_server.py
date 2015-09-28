import unittest
import os
from server import *

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

    def test_create_shapefile(self):
      aa = create_shapefile(MockZipFile)
      self.assertEqual(shp_file, "aaa")
