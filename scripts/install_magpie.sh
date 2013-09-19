#!/bin/bash
# Copyright 2012 Joseph Lewis <joehms22@gmail.com> | <joseph@josephlewis.net>
# this script downloads, installs and starts magpie
# it will be available on port 8080 after starting up

rm -rf magpie
git clone https://github.com/joehms22/magpie.git
cd magpie/magpie/
chmod +x linux_daemon.sh
./linux_deamon.sh &
