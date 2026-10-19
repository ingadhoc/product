.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========================
Product Attribute Template
==========================

This module adds product attribute templates: a named set of attributes (for
example, "T-shirts" with Size and Color) that is assigned to products, so the
attribute lines of all of them can be created at once.

* Create the missing attribute lines, without values, on every product of the
  template.
* Fill the values of those lines from the template form, for all its products.
* See how many products use the template and how many still have attribute
  lines without values.

Installation
============

To install this module, you need to:

#. Just install this module.


Configuration
=============

#. Enable Variants in Sales > Configuration > Settings. Without it, the
   Attributes & Variants tab of the product, where the template is set, is
   hidden.

Usage
=====

To use this module, you need to:

#. Go to Sales > Products > Products attributes templates and create a
   template with its attributes.
#. On each product, in the Attributes & Variants tab, set the template in
   "Product attributes template".
#. Back on the template, press "Update attributes on products". The button
   adds to each product the attribute lines it is missing, without values.
   Lines that already exist are kept as they are. Opening the template form
   also adds them, because its lines list every product and attribute pair.
#. Fill the values in the template lines, or in each product. The "Not
   configured" button opens the products that still have lines without
   values; the same filter, "Attributes not configured", is available in the
   product search.

The menu is only visible to sales administrators.

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
