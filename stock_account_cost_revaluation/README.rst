=======================================
Stock Account - Cost Change Revaluation
=======================================

Postea el asiento de revaluación de inventario al cambiar el costo contable
(``standard_price``) de productos con categoría de valoración perpetua
(``real_time``), en costeo estándar o promedio (AVCO).

Características
===============

- Al cambiar el costo contable (``standard_price``) de un producto con
  **categoría de valoración perpetua** (``real_time``) y costeo **estándar** o
  **promedio (AVCO)**, genera automáticamente el asiento de revaluación de
  inventario por la diferencia sobre el stock on hand:
  ``qty_on_hand × (costo_nuevo − costo_viejo)``.
- Aplica a cualquier origen del cambio de costo, ya que engancha en el punto
  común de todo cambio de ``standard_price``: edición manual del costo en la
  ficha, actualización desde el costo de reposición (módulo
  ``product_replenishment_cost`` cuando está instalado, incluida la diferencia
  de tipo de cambio con costo en moneda secundaria), importaciones, etc.
- El signo del asiento (Debe/Haber) lo maneja la misma lógica del cierre de
  inventario nativo (``res.company._prepare_inventory_aml_vals``).
- **Contrapartida = la cuenta de revaluación de inventario de la categoría**
  (``property_cost_revaluation_account_id``, campo nuevo "Cost Revaluation
  Account"), que es la cuenta de resultado de la revaluación. Si esa cuenta **no
  está configurada, no se postea** el asiento (misma lógica que el core con la
  cuenta de una ubicación de scrap/ajuste: sin cuenta, sin asiento). No se usa la
  cuenta de variación de stock (pertenece al cierre continental) ni la de
  diferencia de precio (se usa para la diferencia de precio de compras / PPV).
- El asiento queda **vinculado al ``product.value``** que el estándar registra por
  el cambio de costo (campo ``account_move_id``, que aporta ``stock_account_ux``).
  Sin ese vínculo el ajuste sigue figurando como pendiente en el reporte de
  valuación y el cierre de inventario lo vuelve a contabilizar.
- **No** genera asiento (por diseño): productos con costeo FIFO
  (``standard_price`` es informativo), categorías con valoración periódica (lo
  materializa el cierre de inventario), productos sin stock on hand y categorías
  sin cuenta de revaluación.

Detalles Técnicos
=================

- Modelos heredados:

  - ``product.product``: override de ``_change_standard_price``, método
    ``_create_cost_revaluation_entry`` que arma y postea el ``account.move`` de
    revaluación, y ``_link_cost_revaluation_entry`` que lo deja apuntado en el
    ``product.value`` del cambio de costo.
  - ``product.category``: campo nuevo ``property_cost_revaluation_account_id``
    ("Cost Revaluation Account"), Many2one a ``account.account``,
    company-dependent.

- Vistas incluidas:

  - ``view_category_property_form``: hereda
    ``stock_account.view_category_property_form`` y agrega el campo
    ``property_cost_revaluation_account_id`` en el formulario de categoría de
    producto (visible solo para valoración ``real_time`` y costeo
    ``standard``/``average``).

Uso
===

1. En la **categoría de producto**, configurar método de costeo *Estándar* o
   *Promedio (AVCO)* y valoración de inventario *Automática (perpetua)*, junto
   con las cuentas y el diario de stock (como toda valoración automática).
2. Definir la **Cuenta de revaluación de inventario** ("Cost Revaluation Account")
   en la categoría (es la cuenta de resultado de la revaluación). Si no se define,
   el módulo no postea el asiento.
3. Al cambiar el costo contable de un producto con stock — manualmente en la
   ficha o por la actualización desde el costo de reposición — el módulo postea
   automáticamente el asiento de revaluación por la diferencia.

Arquitectura
============

La lógica se engancha en ``product.product._change_standard_price``, el punto
por el que pasa todo cambio de ``standard_price`` en Odoo. Tras el
comportamiento estándar, para los productos elegibles (categoría ``real_time``,
costeo estándar o promedio, almacenable y con stock on hand) se calcula la
diferencia de valuación y se postea el asiento entre la cuenta de valuación y la
**cuenta de revaluación de inventario** de la categoría. Si esa cuenta de
resultado no está configurada no se genera asiento, igual que el core no valoriza
un movimiento hacia una ubicación sin cuenta de valuación.

Dependencias
============

- ``stock_account``

Autor
=====

ADHOC SA

Licencia
========

AGPL-3
