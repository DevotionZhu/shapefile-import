Upload shapefile ZIP
-------
`curl -i -F file=@/vagrant/shapefiles/streetshighways.zip http://localhost:4002/api/import/shp2pgsql`

Metadata SQL Queries
-------
SRID:
`select distinct(ST_SRID(geom)) from  mygov1.streetshighways892015_749_210833;`

Encoding:
Is done at the database level.
It should be UTF-8.
Need to check translation errors.
