.. image:: https://img.shields.io/pypi/v/jaraco.logging.svg
   :target: https://pypi.org/project/jaraco.logging

.. image:: https://img.shields.io/pypi/pyversions/jaraco.logging.svg

.. image:: https://img.shields.io/pypi/dm/jaraco.logging.svg

.. image:: https://img.shields.io/travis/jaraco/jaraco.logging/master.svg
   :target: http://travis-ci.org/jaraco/jaraco.logging

Additional facilities to supplement Python's stdlib logging module.

License
=======

License is indicated in the project metadata (typically one or more
of the Trove classifiers). For more details, see `this explanation
<https://github.com/jaraco/skeleton/issues/1>`_.

Argument Parsing
================

Quickly solicit log level info from command-line parameters::

    parser = argparse.ArgumentParser()
    jaraco.logging.add_arguments(parser)
    args = parser.parse_args()
    jaraco.logging.setup(args)
