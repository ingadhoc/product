.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============================
Product Catalog Tree Stock
==============================

This module provides compatibility between product_catalog_tree and stock modules.

When both modules are installed, it adds:

* A **Supplier UoM** column in the product catalog list view, showing the unit of measure
  configured for the supplier in purchase orders.
* Makes the **UoM** and **Forecasted Quantity** (virtual_available) columns optional/visible
  in the catalog view.
* Hides irrelevant columns (website fields, brand, category, type, currency) from the catalog view.

Installation
============

To install this module, you need to:

#. This module is auto-installed when both product_catalog_tree and stock modules are present.

Configuration
=============

No additional configuration is required.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/ingadhoc/product/issues>`_.

Credits
=======

Authors
~~~~~~~

* ADHOC SA
