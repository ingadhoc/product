.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============================
Price Security with sale margin
===============================

This module is an integration of Price Security with Sale Margin.

Installation
============

To install this module, you need to:

#. Just install this module.


Configuration
=============

To configure this module, you need to:

#. On the user, set one of the Price Security groups: "Solo ver: precio venta y compra" (view only sale and purchase prices) or "Solo ver: precio de venta" (view only the sale price).


Usage
=====

To use this module, you need to:

On the lines of a sales order, the cost (``purchase_price``), the margin and the margin percentage follow the user's Price Security group:

* "Solo ver: precio venta y compra": the three fields are shown but read only.
* "Solo ver: precio de venta": the three fields are hidden, and so is the order margin shown in the order totals.

The same applies to any list view of sales order lines that shows those fields.

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
