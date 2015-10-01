#!/bin/bash -e

import_shp_file() {
  time shp2pgsql -c /vagrant/shapefile-import/shapefiles/POIEurope2/POIEuropePolygons_2.shp client_test.poieuropepolygons_2 \
    | PGPASSWORD=mygov psql -U mygov -d mygov
}

import_shp_file_parallel() {
  time find ../POIEurope2/ -name '*.shp' \
    | parallel "shp2pgsql -c /vagrant/shapefile-import/shapefiles/POIEurope2/POIEuropePolygons_2.shp client_test.poieuropepolygons_2 | PGPASSWORD=mygov psql -U mygov -d mygov"
}

import_shp_file_D() {
  time shp2pgsql -D -c /vagrant/shapefile-import/shapefiles/POIEurope2/POIEuropePolygons_2.shp client_test.poieuropepolygons_2 \
    | PGPASSWORD=mygov psql -U mygov -d mygov
}


main() {
    # import_shp_file
    # import_shp_file_parallel
    import_shp_file_D
}

main "$@"