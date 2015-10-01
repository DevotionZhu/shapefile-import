
IMPORTANT
-----------
Please drop table before running scripts or use -d param instead of -c
Ask Nico to send you the shapefiles


Import shapefile 26.2MB
------------------------
`cd test_shp2pgsql_performance`
`./rus_adm.sh`

import_shp_file -> ~ 2s
import_shp_file_parallel -> ~ 0.84s
import_shp_file_D -> ~ 2s


Import shapefile 361MB
------------------------
`cd test_shp2pgsql_performance`
`./poi_europe.sh`

import_shp_file -> ~ 6m 13s
import_shp_file_parallel -> ~ 3m 31s
import_shp_file_D -> ~ 52s



Import shapefile 1.55GB
------------------------
`cd test_shp2pgsql_performance`
`./water_world.sh`

import_shp_file -> ~ 12m 26s
import_shp_file_parallel -> ~ 6m 51s
import_shp_file_D -> ~ 2m 4s


Other things
-----------
import_shp_file_D doesn't work with reprojection -s "FROM_SRID:TO_SRID"

