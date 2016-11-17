.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
  :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
  :alt: License: AGPL-3

==========================
Planned Price for Products
==========================

This module add a new field "Planned Price" to products that can be extended by other modules to calculte this prices based in different conditions. It also add a wizard to update "List Price" using "Planned Price" value. Optionally, you can activate a cron to run this update auomatically.


Installation
============

To install this module, you need to:

#. Just Install.


Configuration
=============

To configure this module, you need to:

#. Go to Pricelist/Pricelist Items/ config "Base" to "Computed List Price".

Usage
=====

To use this module, you need to:

#. No usege needed.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.adhoc.com.ar/

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "9.0" for example


Bug Tracker
===========

#. Known Bugs:

There is a bug Odoo that if you add a product in a sale order, use a product other than the product unit and open, price that shows you is, according to the unit in the sales order and not according to the unit you're seeing the product.
An alternative would be to lst_price readonly to not pass this error the product form view, this could be improved

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/product/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Images
------

* ADHOC SA: `Icon <http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png>`_.

Contributors
------------


Maintainer
----------

.. image:: http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png
  :alt: Odoo Community Association
  :target: https://www.adhoc.com.ar

This module is maintained by the ADHOC SA.

To contribute to this module, please visit https://www.adhoc.com.ar.