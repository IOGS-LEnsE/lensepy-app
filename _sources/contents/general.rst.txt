General functions
#################

This section gathers general functions included in the lensepy package.


Using dictionnary
*****************

It is possible to use functions to automaticaly translate some part of a user interface for exemple in a specific language.

Translation data files
======================

For that, you need to create a CSV file for each language. For example, a file named :file:`lang_FR.csv` can contain all the definitions for the French language.

The file should have the following format:
	# comment
	# comment
	key_1 ; language_word_1
	key_2 ; language_word_2


Functions for translations
==========================
.. autofunction:: lensepy.load_dictionary
   :noindex:
   
.. autofunction:: lensepy.translate
   :noindex:

Import functions from lensepy
=============================

To import the previous functions, you have to include this line to your python script:

.. code-block:: python

  from lensepy import load_dictionary, translate, dictionary

:code:`dictionary` is a global variable. It is a Python dictionary containing the translated expression for a specific key.  
  
How to use
==========


Load a dictionary file
----------------------

To load an existing dictionary file, you can use the following instruction where :code:`file_name_dict` is the path to the CSV file containing the definition of the different keys.

.. code-block:: python

	load_dictionary(file_name_dict)


Translate function
------------------

.. code-block:: python

	label = QLabel(translate("label_key"))
	
If the :code:`label_key` is in the global dictionary, the :code:`translate` function returns the associated value. Otherwise, the value :code:`label_key` is returned.
