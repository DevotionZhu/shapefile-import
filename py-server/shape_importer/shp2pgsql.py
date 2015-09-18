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


def table_exists(connection, full_table_name):
    cursor = connection.cursor()
    sql = '''
        SELECT EXISTS (
            SELECT 1
            FROM   pg_catalog.pg_class c
            JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE  n.nspname = '{schema_name}'
            AND    c.relname = '{table_name}'
        );
    '''
    [schema_name, table_name] = full_table_name.split('.')
    cursor.execute(sql.format(schema_name=schema_name, table_name=table_name))
    exists = cursor.fetchall()[0][0]
    return exists


def create_schema_if_none(cursor, schema):
    create_schema = '''
        CREATE SCHEMA IF NOT EXISTS {schema}
    '''
    cursor.execute(create_schema.format(schema=schema))


def shape_to_pgsql(config, conn, shape_path, table, import_mode, srid=-1,
                   encoding='latin1', log_file=None, batch_size=1000):

    command_args = [
        config['shp2pgsql'],
        import_mode,
        '-W', encoding,
        '-s', str(srid) + ':4326',
        shape_path,
        table
    ]

    p = subprocess.Popen(command_args, stdout=subprocess.PIPE, stderr=log_file)

    cursor = conn.cursor()
    user_schema = table.split('.')[0]
    create_schema_if_none(cursor, user_schema)

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


def get_import_mode(conn, full_table_name):
    if table_exists(conn, full_table_name):
        return IMPORT_MODES['DROP_CREATE']
    return IMPORT_MODES['CREATE']


def shape2pgsql(config, user_schema, shapefile, srid, encoding):
    import psycopg2
    import os.path

    conn = psycopg2.connect('host=%s dbname=%s user=%s password=%s' % (
        config['db']['host'], config['db']['name'],
        config['db']['user'], config['db']['password']))

    table = os.path.splitext(os.path.split(shapefile)[1])[0]
    full_table_name = user_schema + '.' + table

    import_mode = get_import_mode(conn, full_table_name)
    shape_to_pgsql(config, conn, shapefile, full_table_name,
                   import_mode, srid, encoding)
    vacuum_analyze(conn, full_table_name)

    return full_table_name
