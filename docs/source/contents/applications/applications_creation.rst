How to create an application
############################

.. warning::
   This application and its documentation website are still works in progress


Minimal example
===============

appli.xml file
==============

This file contains :

* informations about the application : name, organization, year of development...
* the global structure of the final application : modules to include
* contributors
* required "global" variables

It is structured as a standard XML file with elements.
Here is the scheme of this file :

.. code-block:: text

    appli
    ├── name
    ├── appname
    ├── organization
    ├── year
    ├── logo
    ├── imgdir
    ├── contributors
    │   ├── contributor
    │   │   ├── name
    │   │   ├── organization
    │       └── mail
    ├── module
    │   ├── name
    │   └── location
    ├── variable
    └── others


Miscellanous
============

Contributors
------------

Contributors appear in the :file:`appli.xml` file in a XML section :envvar:`contributors`.

This section contains a :envvar:`contributor` element per contributor. This element has a :envvar:`type` attribute
that can take the following value :

* ``dev`` : for developpers
* ``sciexp`` : for scientific experts


