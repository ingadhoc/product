Porduct no Translation
======================

This module sets the translatable fields of the product object (name,
descriptions) to non-translatable fields.

This change is usefull for companies that work with only one language.
And it reduces the start time of the Point of Sale !

IMPORTANT: On installation, it will sync the values of translations of first installed language (different from en_US) as source values.

Models and fields:

* Product Template: description_sale, description_purchase, description, name
* Product Category: name
* Product Attribute: name
* Product Attribute Value: name
* Product Uom Categ: name
* Product Uom: name
* Product Ul (logistic unit): name