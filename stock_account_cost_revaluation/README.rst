.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=======================================
Stock Account - Cost Change Revaluation
=======================================

Since Odoo 19, changing the cost of a product no longer posts the inventory
revaluation entry: the standard records the price change as a value adjustment
(``product.value``) and leaves the accounting to the inventory valuation closing.
That closing is not run automatically for companies with automated (perpetual)
valuation, so for those products the revaluation never reaches the books on its
own.

This module posts the revaluation entry at the moment the cost changes, for
products whose category uses **automated (perpetual) valuation** with **standard**
or **average (AVCO)** costing:

#. **Every cost change books the entry, whatever its origin.** The Cost field on
   the product form, the update from the replenishment cost
   (``product_replenishment_cost``: the monthly cron "Update Cost from
   Replenishment Cost", exchange rate difference included when the replenishment
   cost is in another currency), an import, or any other write on the cost.
#. **The entry books the difference on the stock on hand** of the company the user
   is working in: ``quantity on hand × (new cost − previous cost)``. A higher cost
   debits the stock valuation account and credits the cost revaluation account; a
   lower cost does the opposite. The entry is posted in the stock journal of the
   category, with the reference "Revaluación de costo: <product>", and its
   valuation line names the product, so the journal items can be filtered per
   product.
#. **The counterpart is the "Cost Revaluation Account" of the product category**, a
   new field shown right after the Stock Valuation Account, only for automated
   valuation with standard or average costing. It is the profit or loss account of
   the revaluation. It is on purpose neither the stock variation account (that one
   belongs to the periodic closing) nor the price difference account (used for the
   purchase price difference).
#. **Without that account, no entry is posted**, the same way the standard books no
   entry for a scrap or adjustment location without an account. The price change is
   still recorded as a value adjustment, so the Inventory Valuation report keeps
   showing it as pending and the next inventory valuation closing books it.
#. **The entry is linked to the value adjustment** that the standard records for the
   price change (field "Journal Entry" of ``product.value``), so whoever reads that
   link can tell the adjustment is already booked. With ``stock_account_ux``
   installed, the Inventory Valuation report stops showing it as pending and the
   inventory valuation closing does not book it a second time.
#. **No entry is posted, by design, for:** FIFO products (there the cost is
   informative and the revaluation is done by adjusting the value of the move),
   categories with periodic valuation (*Periodic (at closing)*: the closing books it), non-storable
   products, products without stock on hand in the company, and a cost that stays
   the same. If the category has no stock valuation account or no stock journal
   the entry is skipped and a warning is written to the server log.

Installation
============

To install this module, you need to:

#. Just install this module.

Configuration
=============

To configure this module, you need to:

#. Go to *Inventory > Configuration > Product Categories* and open the category.
   Set the *Costing Method* to *Standard Price* or *Average Cost (AVCO)* and the
   *Inventory Valuation* to *Perpetual (at invoicing)*, with its stock valuation
   account and stock journal, as for any perpetual category.
#. Fill in the *Cost Revaluation Account* that appears after the *Stock Valuation
   Account* with the profit or loss account of the revaluation. The field is per
   company: set it in each company that revalues. While it is empty no entry is
   posted.

Usage
=====

To use this module, you need to:

#. **Change the cost by hand.** Open the product, edit the *Cost* field (shown as
   *Accounting Cost* when ``product_replenishment_cost`` is installed) and save.
   If the product has stock on hand, a posted entry appears in the stock journal
   under *Accounting > Journal Entries*, with the reference
   "Revaluación de costo: <product>".
#. **Update the cost from the replenishment cost.** With
   ``product_replenishment_cost`` installed, the cron "Update Cost from
   Replenishment Cost" writes the replenishment cost into the cost of every
   product that has one. Each product whose cost changed books its own entry, so
   keep the cron monthly as it comes: running it daily posts an entry per product
   and per change.
#. **Check the Inventory Valuation report** (*Accounting > Reporting > Review >
   Inventory > Inventory Valuation*, Enterprise, with ``stock_account_ux``
   installed). The price change appears in the variation with its journal entry
   and is not part of the pending difference. If the category had no Cost
   Revaluation Account when the cost changed, the adjustment stays pending there
   until the next inventory valuation closing.

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
