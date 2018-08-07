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

#. Set 'Restrict Prices' for users you want to restrict.
#. For the same users, configure discounts range on "Discounts Permissions" users tab.


Usage
=====

To use this module, you need to:

For users with price restriction, it restricts:

* on sales orders: change payment term or pricelist
* on sales order lines: change unit price and set limits on discount (limits configured on user)
* on partners: change payment term or pricelist
* on invoices: change unit price
* on invoice lines: change unit price and set limits on discount (limits configured on user)
* on product: change price

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
