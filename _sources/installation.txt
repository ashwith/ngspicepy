************
Installation
************

Before installing, make sure you have ngspice's shared library installed at 
/usr/local/lib/. To do so, first download ngspice from `ngspice's sourceforge
page
<https://sourceforge.net/projects/ngspice/files/ng-spice-rework/26/>`_.  
Then run the following commands:

.. code:: shell

    $ tar xvzf ngspice-26.tar.gz
    $ cd ngspice-26
    $ mkdir release
    $ cd release
    $ ../configure --with-ngshared
    $ make
    $ sudo make install

If all goes well, the library should be installed in /usr/local/lib. If not,
please consult ngspice's installation instructions.

Once the library is installed, simply run,

.. code:: shell
   
    $ pip3 install git+https://github.com/ashwith/ngspicepy

Note that ngspicepy requires python 3.5.
