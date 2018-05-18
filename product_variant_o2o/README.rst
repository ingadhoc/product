.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=================================
Product Variant Force One Two One
=================================

Add a new field "One variant per product" on products (product.template) that changes current behaviour in this way:

#. One variant per product can be created (only one attribute value per attribute can be setted).
#. Change odoo behaviour when changing attribute values, if:
    #. False: default odoo behaviour, if you change an attribute or remove it odoo creates a new variant.
    #. True: change attributes wont change variants, it will only update variants attributes

Installation
============

To install this module, you need to:


Configuration
=============

To configure this module, you need to:


Usage
=====

To use this module, you need to:

#. Go to a product and under Variants tab set "One variant per product" option.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

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
