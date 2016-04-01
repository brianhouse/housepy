housepy
=======
Personal utility library for Python 3  
(note: other projects may use older housepy for 2.7, deprecated, may or may not be equiv)


Python 3.5
----------
Jinja2 requires >= 3.3; other dependencies should work in 3.2


Usage
-----
Place or symlink in your project directory.

    from housepy import log, config


Installation
------------
    sudo apt-get install python3-dev
    sudo pip3.5 install -r requirements.txt


#### pycairo

    brew install fontconfig
    brew install cairo


#### other
to check installed modules:

    pip3.5 freeze


#### Ubuntu notes

To install pip for python3 on Ubuntu, install easy_install3 first:
    
    sudo apt-get install easy_install3
    sudo easy_install3 pip

numpy and scipy must be installed through apt-get:

    sudo apt-get install python3-numpy
    sudo apt-get install python3-scipy


### Copyright/License

Copyright (c) 2010-2016 Brian House

This code is released under the MIT License and is completely free to use for any purpose. See the LICENSE file for details.
