#!/usr/bin/python

'''
This is mostly a Python wrapper for the shp2pgsql command line utility.
'''

import subprocess
import util


IMPORT_MODES = dict(
    DROP_CREATE='-d',
    APPEND='-a',
    CREATE='-c',
    PREPARE='-p'
)


def shape_to_pgsql(config, conn, shape_path, table, import_mode, srid=-1,
                   encoding='latin1', log_file=None, batch_size=1000):

    command_args = [
        config['SHAPE2PGSQL'],
        import_mode,
        '-W', encoding,
        '-s', str(srid) + ':4326',
        shape_path,
        table
    ]

    p = subprocess.Popen(command_args, stdout=subprocess.PIPE, stderr=log_file)

    cursor = conn.cursor()

    try:
        with p.stdout as stdout:
            for commands in util.groupsgen(util.read_until(stdout, ';'),
                                           batch_size):
                command = ''.join(commands).strip()
                if len(command) > 0:
                    cursor.execute(command)
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        cursor.close()


def vacuum_analyze(conn, table):
    isolation_level = conn.isolation_level
    conn.set_isolation_level(0)
    cursor = conn.cursor()
    try:
        cursor.execute('vacuum analyze %s;' % table)
    finally:
        cursor.close()
        conn.set_isolation_level(isolation_level)


def shape2pgsql(config, shapefile, srid, encoding):
    import psycopg2
    import uuid

    conn = psycopg2.connect('host=%s dbname=%s user=%s password=%s' % (
        config['DB_HOST'], config['DB_NAME'],
        config['DB_USER'], config['DB_PASSWORD']))

    generate_uuid = uuid.uuid4()
    full_table_name = 'mygov_' + str(generate_uuid).replace('-', '_')

    import_mode = IMPORT_MODES['CREATE']
    shape_to_pgsql(config, conn, shapefile, full_table_name,
                   import_mode, srid, encoding)
    vacuum_analyze(conn, full_table_name)

    return full_table_name
