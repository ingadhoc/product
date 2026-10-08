.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=================
Product Usability
=================

Several Improvements to products:

#. Now the field "Active" (Archive) keeps tracking in chatter.
#. Incorporates the possibility to search a product by the vendor product code in the product.template and product.product models.
#. Add smart button from pricelist to pricelists items, with the number of items, and search and group the items by what they apply on and by product category.
#. Surcharge pricelist rules are rounded by default to the "Product Price" precision (discount rules are not, so sales keep showing the discount).
#. Add product warranty field that was deprecated by odoo.
#. Add new field "Description" on product UOMs, shown in their list and form and used when searching them.
#. Incorporates the possibility to search the Pricelist Price of products in the tree view.
#. Renders the product labels (Dymo and sheets) in batches of pages so large print jobs (thousands of labels) do not crash wkhtmltopdf by memory.

Installation
============

To install this module, you need to:

#. Just install this module.

Configuration
=============

To configure this module, you need to:

#. Optionally set the system parameter ``product_ux.dymo_label_batch_size`` (default 200) to tune how many labels are rendered per wkhtmltopdf call (on sheets it is rounded down to whole pages, at least one). Set it to 0 to render the labels in a single call.

Usage
=====

To use this module, you need to:


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
