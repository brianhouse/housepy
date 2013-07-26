housepy -- personal utility library for Python 3
================================================


Notes
-----

pip for python3 is pip-3.2


#### pyglet

note on Pyglet install: I installed the latest from the development branch, ran 2to3 -wn on it manually, and then installed with python3. alpha download from the site didnt work; development branch didnt do 2to3 automatically.



#### pycairo

brew install fontconfig
brew install cairo
export PKG_CONFIG_PATH="/opt/X11/lib/pkgconfig:$PKG_CONFIG_PATH"

had to manually disable (temporarily rename) /usr/bin/python to get it to install with python3

python3 ./waf configure
python3 ./waf build
python3 ./waf install




### Copyright/License

Copyright (c) 2013 Brian House

This code is released under the MIT License and is completely free to use for any purpose. See the LICENSE file for details.
