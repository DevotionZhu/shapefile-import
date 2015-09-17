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
