.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
Products Management Group
=========================

This module creates a new group called "Products Management". Only users on that group can create, edit, archive or delete products (product templates and variants).

Users outside the group get an access error when they try to change a product, even if a native group (for example "Product / Create" or an Inventory administrator) would allow it. Users in the group can manage products without any other product group. Reading products is not affected, and the superuser is never restricted.

IMPORTANT: this module overrides the access domain of ``product.template`` and
``product.product`` (except for the "read" operation), and adds ``ir.access``
permissions for the group on both models.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

#. Nothing to configure

Usage
=====
Once the module is installed, the superuser and the administrator are in the "Products Management" group.

To use this module, you need to:

#. Go to the user settings and add the user to the "Products Management" group to let them create, edit, archive or delete products.
#. Remove the user from the group to take that possibility away.

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
