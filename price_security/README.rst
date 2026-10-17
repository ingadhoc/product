.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============
Price Security
==============

Keep prices under control when not everyone in the company may set them.

The module adds two permissions. The first one, *Solo ver: precio venta y
compra* (only view sale and purchase price), stops a user from changing prices,
discounts, pricelists and payment terms. The second one, *Solo ver: precio de
venta* (only view sale price), also hides the cost from the screens that show
it.

Features
========

* **A discount range per user and per pricelist.** Each user gets a list of
  pricelists with the minimum and the maximum discount allowed on each one. The
  range applies to what the user adds *on top of* the pricelist discount, both
  on sale orders and on customer invoices.
* **Prices in read only.** Unit price, cost, sales price, unit of measure and
  vendors become read only for restricted users, on the product, on the sale
  order lines and on the customer invoice lines.
* **Products that anyone may reprice.** A product marked with *Can modify
  prices* is left out: any user may set its price on a sale order or an
  invoice.
* **Pricelists and payment terms in read only.** A restricted user cannot
  create or change a pricelist, a pricelist rule or a payment term.
* **A restricted choice of pricelist and payment term.** Each pricelist and
  each payment term carries the list of the ones a restricted user may pick
  instead of it. On a sale order the user may only choose the one of the
  customer or one from that list. Both also get a sequence field, so the lists
  can be ordered.
* **The cost out of sight.** For users with *Solo ver: precio de venta*, the
  cost is hidden on the product form and on the lists that reach it: the
  accounting cost and the inventory valuation columns on the product and stock
  report lists, the value on the quant lists, and the valuation fields on the
  lot form. The secondary currency columns added by ``stock_currency_valuation``
  are hidden too when that module is installed.

Installation
============

To install this module, you need to:

#. Just install this module.

Configuration
=============

To configure this module, you need to:

#. Give the users you want to restrict one of the two permissions, under the
   *Restricción de precios* privilege.
#. For the same users, set the discount ranges on the *Discounts Permissions*
   tab of their user form.
#. On each pricelist and payment term, fill in *Allowed Pricelists* and
   *Allowed Payment Terms* with the ones a restricted user may pick instead.
#. Tick *Can modify prices* on the products whose price anyone may change.

Usage
=====

A user with *Solo ver: precio venta y compra* cannot:

#. change the unit price on a sale order line or on a customer invoice line;
#. apply a discount outside the range configured for them, on those same lines;
#. apply a global discount or a fixed amount from the discount wizard of a sale
   order, when the pricelist of the order is one of their restricted ones;
#. pick a pricelist or a payment term that is neither the one of the customer
   nor one of the allowed ones, on the sale order and on the contact;
#. change the sales price, the cost, the unit of measure or the vendors of a
   product;
#. create or change a pricelist, a pricelist rule or a payment term.

On the sale order form there is one more guard, and it is only a guard: when a
restricted user picks another customer on an order that already has lines, and
that customer would bring another pricelist, the form warns and puts the
previous customer back. Being an onchange, it lives in the form only — a write,
an import or another module still changes the customer, and the order then
takes the pricelist of the new one.

A user with *Solo ver: precio de venta* cannot do any of the above, and on top
of that does not see the cost anywhere: product form and lists, stock report,
quant lists and lot form.

Note that hiding the cost is interface level security: the fields are out of
the views, but the data can still be reached through exports, filters or
groupings.

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
