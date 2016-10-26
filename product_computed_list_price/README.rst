    'description': """
Product Computed List Price
===========================
Errores conocidos:
Hay un bug de odoo por defecto que si agregas un producto en una sale order,
usas una unidad distinta a la del producto y abris el producto, el precio
que te muestra es según la unidad en la orden de venta y no según la unidad que
estás viendo del producto.
Una alternativa sería hacer lst_price readonly para que no pase este error en
la vista form de productos, esto se podría mejorar
    """,