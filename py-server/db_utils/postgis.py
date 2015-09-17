import psycopg2


GEOJSON_SQL_TEMPLATE = '''
    SELECT row_to_json(fc) as data
    FROM (
     SELECT 'FeatureCollection' AS type
          , array_to_json(array_agg(f)) AS features
      FROM (
      SELECT 'Feature' As type
        , ST_AsGeoJSON({geometry_column})::json As geometry
        , row_to_json(
            (select l from
              (select {attr_columns}) as l
            )
          ) As properties
      FROM {table_name} As lg
     ) AS f
    ) AS fc
'''
GEOMETRY_COLUMN_TYPE_CODE = 16392


def geojson_query(cursor, table_name, geometry_column, attr_columns):
    comma_separated_columns = ','.join(attr_columns)
    cursor.execute(GEOJSON_SQL_TEMPLATE.format(
        table_name=table_name,
        geometry_column=geometry_column,
        attr_columns=comma_separated_columns
    ))
    results = cursor.fetchall()
    return results[0][0]


def retrieve_columns(cursor, table_name):
    attr_columns = []
    geometry_column = ''
    cursor.execute('SELECT * FROM {table_name}'.format(
        table_name=table_name))
    for column in cursor.description:
        if column.type_code == GEOMETRY_COLUMN_TYPE_CODE:
            geometry_column = column.name
        else:
            attr_columns.append(column.name)
    return (attr_columns, geometry_column)


def geojson_from_table(conn_str, table_name):
    with psycopg2.connect(conn_str) as conn:
        with conn.cursor() as curs:
            (attr_columns, geometry_column) = retrieve_columns(
                curs, table_name)
            return geojson_query(
                curs, table_name, geometry_column, attr_columns)
