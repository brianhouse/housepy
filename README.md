housepy
=======
Personal utility library for Python 3  
(note: other projects may use older housepy for 2.7, deprecated, may or may not be equiv)


Python 3.4
----------
Jinja2 requires >= 3.3; other dependencies should work in 3.2


Usage
-----
Place or symlink in your project directory.

    from housepy import log, config


Installation
------------
    sudo apt-get install python3-dev
    sudo pip3.4 install -r requirements.txt


#### pyglet

note on Pyglet install: alpha download from the site didnt work. repository download didnt do 2to3 automatically.

    hg clone https://pyglet.googlecode.com/hg/pyglet
    cd pyglet
    2to3 -wn pyglet
    sudo python3 setup.py install



#### pycairo

    brew install fontconfig
    brew install cairo
    export PKG_CONFIG_PATH="/opt/X11/lib/pkgconfig:$PKG_CONFIG_PATH"

had to manually disable (temporarily rename) system python to get it to install with python3

    sudo mv /usr/bin/python /usr/bin/python_
    git clone git://git.cairographics.org/git/pycairo
    cd pycairo
    python3 ./waf configure
    python3 ./waf build
    python3 ./waf install
    sudo mv /usr/bin/python_ /usr/bin/python


#### PIL

    sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms1-dev libwebp-dev tcl8.5-dev tk8.5-dev
    sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
    sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib
    sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib

    git clone https://github.com/smarnach/pil-py3k
    cd pil-py3k
    python3 setup.py build_ext -i
    python3 selftest.py
    sudo python3 setup.py install


#### other
to check installed modules:

    pip3.4 freeze


#### Ubuntu notes

To install pip for python3 on Ubuntu, install easy_install3 first:
    
    sudo apt-get install easy_install3
    sudo easy_install3 pip

numpy and scipy must be installed through apt-get:

    sudo apt-get install python3-numpy
    sudo apt-get install python3-scipy


### Copyright/License

Copyright (c) 2014 Brian House

This code is released under the MIT License and is completely free to use for any purpose. See the LICENSE file for details.
