Start App
---------
`cd py-server`
`./start.sh`

Run Tests
----------
First time running of the tests, please set up from console
export APP_CONFIG_FILE=/vagrant/shapefile-import/config/testing.py

`cd py-server`
`python -m coverage run -m unittest discover tests`

Show report in console
`python -m coverage report —omit=“*/__init__*,tests/*,/usr/*”`

Show report in browser
`python -m coverage html —omit=“*/__init__*,tests/*,/usr/*”`


Upload shapefile ZIP
-------
`curl -i -H 'X-MyGov-Authentication: mygov1' -F file=@/vagrant/shapefiles/streetshighways.zip http://localhost:4002/api/import/shp2pgsql`

Metadata SQL Queries
-------
SRID:
`select distinct(ST_SRID(geom)) from  mygov1.streetshighways892015_749_210833;`

Encoding:
Is done at the database level.
It should be UTF-8.
Need to check translation errors.

Reprojecting
------
```
CREATE TABLE mygov1.streetshighways892015_749_210833_4326 AS
  SELECT ST_Transform(geom,4326) AS the_geom
  FROM mygov1.streetshighways892015_749_210833;
```