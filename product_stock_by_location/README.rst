.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
Product Stock By Location
=========================

#. Adds the option "Show stock on products and sales" on stock locations. It is enabled by default.
#. Adds a "View Stock Detail" button on the product list and kanban views. It opens a window with the
   product's stock in each internal location that has the option enabled: On Hand, Forecasted,
   Incoming and Outgoing. For a product with variants, the quantities add up all its variants.
#. On the product kanban, shows the forecasted quantity next to the on-hand quantity.

Installation
============

To install this module, you need to:

#. Just install the module.

Configuration
=============

To configure this module, you need to:

#. Go to Inventory > Configuration > Locations.
#. On each internal location, the option "Show stock on products and sales" is enabled by default.
   Uncheck it on locations you do not want to show (for example, scrap locations set as internal).

Usage
=====

To use this module, you need to:

#. Go to Inventory > Products > Products.
#. In the list view, click the magnifier icon next to "On Hand"; in the kanban view, click
   "View Stock Detail".
#. A window opens with the stock of that product in each location.

The forecasted quantity and the "View Stock Detail" button and link only show for products that
track inventory, and only to Inventory users.

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
