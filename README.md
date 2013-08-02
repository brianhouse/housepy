housepy
=======
Personal utility library for Python 3


Installation
------------

    brew install python3        # current: 3.3.2
    sudo pip-3.3 install -r requirements.txt

#### pyglet

note on Pyglet install: alpha download from the site didnt work. repository download didnt do 2to3 automatically.

    hg clone https://pyglet.googlecode.com/hg/ pyglet
    cd pyglet
    2to3 -wn pyglet
    sudo python3 setup.py install



#### pycairo

    brew install fontconfig
    brew install cairo
    export PKG_CONFIG_PATH="/opt/X11/lib/pkgconfig:$PKG_CONFIG_PATH"

had to manually disable (temporarily rename) /usr/bin/python to get it to install with python3

    python3 ./waf configure
    python3 ./waf build
    python3 ./waf install


#### other
to check installed modules:

    pip freeze



### Copyright/License

Copyright (c) 2013 Brian House

This code is released under the MIT License and is completely free to use for any purpose. See the LICENSE file for details.
