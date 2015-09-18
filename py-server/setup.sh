#!/bin/bash -e


install_ubuntu_packages() {
    if [ $(dpkg-query -W -f='${Status}' python3-dev 2>/dev/null | grep -c "ok installed") -eq 0 ];
    then
        echo "Installing python3-dev tools"
        sudo apt-get install -y python3-dev
    fi
    if [ $(dpkg-query -W -f='${Status}' python-pip 2>/dev/null | grep -c "ok installed") -eq 0 ];
    then
        echo "Installing python package installer"
        sudo apt-get install -y python-pip
    fi
    if [ $(dpkg-query -W -f='${Status}' python-mapnik 2>/dev/null | grep -c "ok installed") -eq 0 ];
    then
        echo "Installing python mapnik"
        sudo apt-get install -y python-mapnik
    fi
    if [ $(dpkg-query -W -f='${Status}' python-gdal 2>/dev/null | grep -c "ok installed") -eq 0 ];
    then
        echo "Installing python gdal"
        sudo apt-get install -y python-gdal
    fi
    if [ $(pip freeze | grep -c "dbfpy") -eq 0 ];
    then
        echo "Installing python dbfpy"
        install_python_dbfpy
    fi
}


install_python_dbfpy() {
    wget http://sourceforge.net/projects/dbfpy/files/dbfpy/2.3.1/dbfpy-2.3.1.tar.gz
    tar xvf dbfpy-2.3.1.tar.gz
    cd dbfpy-2.3.1
    sudo python setup.py install
    cd ..
    rm dbfpy-2.3.1.tar.gz
    rm -rf dbfpy-2.3.1
}

install_requirements() {
    sudo pip install -r requirements.txt
}


create_static_folder() {
    if [ ! -d static ];
    then
        mkdir static
    fi
}

main() {
    install_ubuntu_packages
    install_requirements
    create_static_folder
}


main "$@"
