.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========================
Product Replenishment Cost
==========================

Provides an overridable method on product which compute the Replenishment cost of a product. By default it just returns the value of "Cost price" field, but using the product_cost_incl_bom module, it will return the costing from the bom.

As it is a generic module, you can also setup your own way of computing the replenishment_cost for your product.

All OCA modules to compute margins are based on it, so you'll be able to use them in your own way.
New Replenishment Cost Last Update
Track changes of RC (Replenishment Cost) Last update, RC Base Cost, RC Base Cost Currency in the chatter.
Update RC Last Update automatically if RC Base Cost or RC Base Cost Currency changes (NOTE: currency exchange changes are not tracked)
Add Product Replenshiment Cost Rules. Each rule can have several lines, each line can add a percentage and a fixed amount. It also update "RC Last Update" automatically if rule or rule lines change. Also changes in rules lines are tracked inside the rules in the chatter.
Add Replenshiment cost rules to supplierinfo.
You can select "Replenishment Cost Type" to use Replenshiment cost rules in the product or use rules in supplierinfo for the first seller.
Now when create an Purchase Order the price that suggest in the line is the replanishment cost.

Replenishment Cost Updates (run log)
Every run of the "Update Cost from Replenishment Cost" scheduled action and every manual update
from the wizard is logged on "Replenishment Cost Updates" (menu next to the cost rules): when it
started and finished, who launched it, how many products were processed and, for each product whose
accounting cost actually changed, the previous and the new cost.

* A scheduled run processes the products in batches that chain one after the other; all of them
  share the same run record, so "when did it finish" has an answer. When it finishes, a summary is
  posted on the run chatter.
* If the run fails or is interrupted, it is closed with the "Error" state instead of leaving the
  traceback only on the server log.
* The manual wizard shows the result (updated / without changes) as a notification.
* System parameter ``product_replenishment_cost.run_line_retention_days`` (90 by default, zero to
  keep everything): a daily scheduled action deletes the detail lines older than that. The run
  header is always kept.

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
