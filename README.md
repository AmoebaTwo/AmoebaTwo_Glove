AmoebaTwo_Glove
===============

Control Amoeba Two with HTTP

Requires Python 3

To install:

    python3 setup.py install

Depends upon:

* [AmoebaTwo lib](https://github.com/chrisalexander/AmoebaTwo)
* [Tornado](https://github.com/facebook/tornado)

To use:

    python3 server.py

Then, you can use the following endpoints (GET requests):

* /drive/forwards
* /drive/left
* /drive/right
* /drive/{anything else} = stop
* /light/top/on
* /light/top/off
* /light/front/on
* /light/front/off
