from chardet.universaldetector import UniversalDetector
from dbfpy.dbf import Dbf
from osgeo import osr
from urllib import urlencode
from urllib2 import urlopen
import json


def get_srid_from_prj(prj_file):
    # Try detecting the SRID, by default we set to 4326 and hope the best
    srid = 4326
    with open(prj_file, 'r') as prj_filef:
        prj_txt = prj_filef.read()
        srs = osr.SpatialReference()
        srs.ImportFromESRI([prj_txt])
        srs.AutoIdentifyEPSG()
        code = srs.GetAuthorityCode(None)
        if code:
            srid = code
        else:
            # Ok, no luck, lets try with the OpenGeo service
            query = urlencode({
                'exact': True,
                'error': True,
                'mode': 'wkt',
                'terms': prj_txt})
            webres = urlopen('http://prj2epsg.org/search.json', query)
            jres = json.loads(webres.read())
            if jres['codes']:
                srid = int(jres['codes'][0]['code'])

        return srid


def get_encoding_from_dbf(dbf_file):
    with open(dbf_file, 'r') as dbf_filef:
        db = Dbf(dbf_filef)

        detector = UniversalDetector()
        for row in db:
            detector.feed(str(row))
            if detector.done:
                break
        detector.close()

        encoding = detector.result['encoding']
        if encoding == 'ascii':
            encoding = 'LATIN1'

    return encoding
