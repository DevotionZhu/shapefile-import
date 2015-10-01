#!/bin/bash -e

import_shp_file() {
  time shp2pgsql -d /vagrant/shapefile-import/shapefiles/Rus_adm_1/Rus_adm0.shp client_test.rus_adm0 \
    | PGPASSWORD=mygov psql -U mygov -d mygov
}

import_shp_file_parallel() {
  time find ../Rus_adm_1/ -name '*.shp' \
    | parallel "shp2pgsql -c /vagrant/shapefile-import/shapefiles/Rus_adm_1/Rus_adm0.shp client_test.rus_adm0 | PGPASSWORD=mygov psql -U mygov -d mygov"
}

import_shp_file_D() {
  time shp2pgsql -D -c /vagrant/shapefile-import/shapefiles/Rus_adm_1/Rus_adm0.shp client_test.rus_adm0 \
    | PGPASSWORD=mygov psql -U mygov -d mygov
}

main() {
    #import_shp_file
    #import_shp_file_parallel
    import_shp_file_D
}

main "$@"