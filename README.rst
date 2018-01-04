.. image:: https://img.shields.io/pypi/v/jaraco.logging.svg
   :target: https://pypi.org/project/jaraco.logging

.. image:: https://img.shields.io/pypi/pyversions/jaraco.logging.svg

.. image:: https://img.shields.io/travis/jaraco/jaraco.logging/master.svg
   :target: http://travis-ci.org/jaraco/jaraco.logging

.. image:: https://readthedocs.org/projects/jaracologging/badge/?version=latest
   :target: https://jaracologging.readthedocs.io/en/latest/?badge=latest

Argument Parsing
================

Quickly solicit log level info from command-line parameters::

    parser = argparse.ArgumentParser()
    jaraco.logging.add_arguments(parser)
    args = parser.parse_args()
    jaraco.logging.setup(args)
