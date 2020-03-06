# -*- coding: utf-8 -*-
# Copyright 2020 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Migration script to convert nan_product_pack from v7 into product_pack from v8.

This migration script will only work if, before launching v8 migration, you run
this script against your database:

.. code-block:: python


    from openupgradelib import openupgrade
    openupgrade.update_module_names(
        cr, [("nan_product_pack", "product_pack")], merge_modules=True,
    )

Otherwise, ``product_pack`` will be kept uninstalled, and ``nan_product_pack``
will stay installed and not migrated.
"""

from openupgradelib import openupgrade


def _was_nan_product_pack(env):
    """Determine if this module was before nan_product_pack."""
    return all(
        (
            openupgrade.column_exists(
                env.cr, "product_pack_line", "parent_product_id"
            ),
            openupgrade.column_exists(
                env.cr, "product_product", "pack_fixed_price"
            ),
            not openupgrade.column_exists(
                env.cr, "product_template", "pack_price_type"
            ),
            not openupgrade.column_exists(env.cr, "product_template", "pack"),
        )
    )


def _migrate_from_nan_product_pack(env):
    """Migrate from nan_product_pack in v7 to product_pack in v8."""
    if not _was_nan_product_pack(env):
        openupgrade.logger(
            "Skipping migration; nan_product_pack garbage not detected"
        )
    openupgrade.add_fields(
        env,
        [
            ("pack", "product.template", None, "boolean", None, "product_pack"),
            (
                "pack_price_type",
                "product.template",
                None,
                "selection",
                None,
                "product_pack",
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET pack = TRUE, pack_price_type = 'components_price'
        WHERE id IN (
            SELECT pp.product_tmpl_id
            FROM
                product_product pp
                INNER JOIN product_pack_line ppl
                ON pp.id = ppl.parent_product_id
        )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET pack_price_type = 'totalice_price'
        WHERE id IN (
            SELECT pp.product_tmpl_id
            FROM
                product_product pp
                INNER JOIN product_pack_line ppl
                ON pp.id = ppl.parent_product_id
            WHERE pp.totalice_price
        )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET pack_price_type = 'fixed_price'
        WHERE id IN (
            SELECT pp.product_tmpl_id
            FROM
                product_product pp
                INNER JOIN product_pack_line ppl
                ON pp.id = ppl.parent_product_id
            WHERE pp.pack_fixed_price
        )
        """,
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _migrate_from_nan_product_pack(env)
