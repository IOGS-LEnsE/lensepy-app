How to create a module
######################

.. warning::
   This application and its documentation website are still works in progress


Minimal example
===============

module.xml file
===============

This file contains :

* informations about the module

It is structured as a standard XML file with elements.
Here is the scheme of this file :

.. code-block:: text

    appli
    ├── name
    ├── contributors
    │   ├── contributor
    │   │   ├── name
    │   │   ├── organization
    │       └── mail
    ├── variable
    └── others

Display mode
------------

The interface is divided into two different sections :

* on the left side, a **menu area** (about one-fifth of the screen width),
* on the right side, a **main display** area that is itself divided into four sections:

  * a top-left section,
  * a top-right section,
  * a bottom-left section,
  * a bottom-right section.

.. code-block:: text

    +----------------+-----------------+-----------------+
    |                |                 |                 |
    |     MENU       |    TOP LEFT     |   TOP RIGHT     |
    |   (1/5 width)  |-----------------+-----------------|
    |                |   BOTTOM LEFT   |   BOTTOM RIGHT  |
    |                |                 |                 |
    +----------------+-----------------+-----------------+


Miscellanous
============

Contributors
------------

Contributors appear in the :file:`appli.xml` file in a XML section :envvar:`contributors`.

This section contains a :envvar:`contributor` element per contributor. This element has a :envvar:`type` attribute
that can take the following value :

* ``dev`` : for developpers
* ``sciexp`` : for scientific experts


