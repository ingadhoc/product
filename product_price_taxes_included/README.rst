.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===================================
Product Price Taxes Included or Not
===================================

#. This modules allow you to see product prices with or without taxes included.

1. Add inside the configurations of Accounting a boolean to show price with tax in the product template kanban view.
2. Create a new field on products that shows the product price with taxes included in the kanban and tree view (Taxed Sale Price).
3. When filtering a pricelist in the product tree view, the column "Pricelist Price" will show the sale price according to the selected pricelist (need to have installed product_pricelist module).

Installation
============

To install this module, you need to:

#. Just install module.

Technical readme
================

#. Create new field on products that is shown on tree and form that shows "Product Price" with taxes included (on previous versions it was same lst_price field but then you couldn't search and sort by this field, so for siplicity we keep native odoo fields and add our owns)
#. Also modify pricelist method so that if include_taxes is sent on context you will get prices with taxes included
#. Add in config of sale the boolean to show price with tax in the product template kanban view.

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
