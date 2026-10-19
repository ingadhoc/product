.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================
Product Internal Code
=====================

This module creates a new field called "Internal Code" on products.
Internal Code must be unique per product variant.
It also creates a sequence to populate this new field automatically upon product creation.

Installation
============

To install this module, you need to:

#. Just install the module.

Configuration
=============

You can change or delete the default sequence on sequences menu. It is called "product" and its code is "product.internal.code".

Usage
=====

Create a product and you can:

#. Set an Internal Code
#. Or leave it empty, then a new code will be automatically assigned by that sequence.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/product/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
