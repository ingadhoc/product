.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================================================
Integration between Replenishment Cost and Manufacture
======================================================

#. Add a method to compute the replenishment cost using the BoM's replenishment cost.
#. Modify the "Bill of Materials Structure" report to use the replenishment cost
#. Support for replenishment cost calculation in subcontracted BOMs, adding the supplier/subcontractor cost to the components' cost

Installation
============

To install this module, you need to:

#. Just install module.

Configuration
=============

To configure this module, you need to:

#. No configuration needed.

Usage
=====

To use this module, you need to:

#. On a product with a bill of materials, set the replenishment cost type to "Basado en Ldm" (based on BoM).
#. The replenishment cost of the product is the sum of the replenishment cost of its BoM components, plus the subcontractor price on subcontracted BoMs and the extra cost per unit of normal BoMs, converted to the product currency and unit of measure. If the product has a replenishment cost rule, it is applied on top.
#. On the bill of materials, the "BoM Overview" button shows the BoM structure costed with the replenishment cost of the components, or their cost when they have none.


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
