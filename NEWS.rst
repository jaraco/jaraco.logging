v3.4.0
======

Features
--------

- Add support for log_level accepting an integer input.


v3.3.0
======

Features
--------

- Replaced deprecated datetime.utcfromtimestamp. (#3)


v3.2.1
======

No significant changes.


v3.2.0
======

Features
--------

- Require Python 3.8 or later.


v3.1.2
======

Refresh packaging. Require Python 3.7 or later.

v3.1.1
======

Rely on PEP 420 for namespace package.

v3.1.0
======

Refresh packaging. Remove unneeded dependency on six.

v3.0.0
======

Require Python 3.6 or later.

2.0
===

Switch to `pkgutil namespace technique
<https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages>`_
for the ``jaraco`` namespace.

1.5.2
=====

Repair incorrect form of namespace package.

1.5.1
=====

Refresh distribution package.

1.5
===

Allow log level to be passed on the command-line
as a numeric value as well.

1.4.1
=====

Refresh distribution package.

1.4
===

Added some nominal documentation.

Implemented automatic deploys using Travis-CI.

1.3
===

Move hosting to github.

Fix test failure due to version detection.

1.2
===

Allow passing default_level to add_arguments.

1.0
===

Initial release based on jaraco.util 10.8.
