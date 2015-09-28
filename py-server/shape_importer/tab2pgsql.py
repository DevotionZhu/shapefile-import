#!/usr/bin/python

"""
This is mostly a Python wrapper for the ogr2ogr with the PGDump driver.

You can probably turn this into a general ogr2ogr importer with minor
adjustments, not much TAB specific in here.
"""

import subprocess
import os.path

# TODO: Find the correct OGR2OGR import command
def shape2pgsql(config, shapefile): # pragma: no cover
    table = os.path.splitext(os.path.split(shapefile)[1])[0]
    full_table_name = '.'.join([config['user'], table])

    args = [
        'ogr2ogr',
        '-f "ESRI Shapefile"',
        shapefile,
        'PG:"host=localhost user=%s port=5432 dbname=%s password=%s"' %
        (config['DB_USER'], config['DB_NAME'],
         config['DB_PASSWORD']),
        '-nln "%s"' % full_table_name
    ]
    print ' '.join(args)

    subprocess.Popen(args, stdout=subprocess.PIPE)
