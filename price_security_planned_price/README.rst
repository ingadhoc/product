.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=================================
Price Security with planned price
=================================

This module is an integration of Price Security with Product Planned Price.

Installation
============

To install this module, you need to:

#. Just install this module.


Configuration
=============

To configure this module, you need to:

#. On Settings > Users, give the user one of the groups of the "Price
   restriction" privilege that Price Security adds: "Only view: sale and
   purchase price" or "Only view: sale price".


Usage
=====

To use this module, you need to:

Open a product. On both the product template form and the product variant
form, the planned price fields that Product Planned Price adds are restricted
by group:

* "Only view: sale and purchase price" leaves the planned price fields
  readonly: based on, margin, surcharge, price in another currency, its
  currency, and the manual planned price
* "Only view: sale price" (which implies the group above) also hides the whole
  Planned Price block

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
