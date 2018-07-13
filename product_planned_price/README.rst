.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================
Product Planned Price
=====================

This module add a new field "Planned Price" to products that can be extended by other modules to calculte this prices based in different conditions.

#. It also add a wizard to update "List Price" using "Planned Price" value. Optionally, you can activate a cron to run this update auomatically.
#. Also Extends Planned Price and allow to set prices based on Replenishment Cost with a fixed and/or percentage margin.
#. Allow to set prices base in other currency.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

#. Go to Pricelist/Pricelist Items/ config "Base" to "Computed List Price".
#. Go to any product template and define the method to compute the Planned Price.

Usage
=====

To use this module, you need to:

#. Go to Product Template and set the planned price "based on" to set by different methods to compute this price.

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
