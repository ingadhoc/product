##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

import io

from odoo import _, http
from odoo.http import content_disposition, request


class ProductCatalogXlsxController(http.Controller):
    @http.route(
        "/product_catalog/<int:catalog_id>/export.xlsx",
        type="http",
        auth="user",
        readonly=True,
    )
    def export_catalog_xlsx(self, catalog_id, taxes_included="0", use_planned_price="0"):
        catalog = request.env["product.product_catalog_report"].browse(catalog_id)
        catalog.check_access_rights("read")
        catalog = catalog.with_context(
            taxes_included=taxes_included == "1",
            use_planned_price=use_planned_price == "1",
        )
        catalog = catalog.prepare_report()

        buffer = io.BytesIO()
        import xlsxwriter  # noqa: PLC0415

        workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
        worksheet = workbook.add_worksheet()

        headers = [_("EAN"), _("Ref"), _("Name"), _("Category"), _("Real Stock"), _("Virtual Stock")]
        headers += [pl.name for pl in catalog.pricelist_ids]
        worksheet.write_row(0, 0, headers)
        column_widths = [len(h) for h in headers]

        for row_idx, product in enumerate(catalog.get_all_products(), start=1):
            row = [
                product.barcode or "",
                product.default_code or "",
                catalog.get_description(product),
                product.categ_id.display_name or "",
                product.qty_available,
                product.virtual_available,
            ]
            for pricelist in catalog.pricelist_ids:
                row.append(catalog.get_price(product, pricelist))
            worksheet.write_row(row_idx, 0, row)
            for col_idx, value in enumerate(row):
                column_widths[col_idx] = max(column_widths[col_idx], len(str(value)))

        for col_idx, width in enumerate(column_widths):
            worksheet.set_column(col_idx, col_idx, width)
        workbook.close()
        content = buffer.getvalue()
        buffer.close()

        filename = "Product Catalog - %s.xlsx" % catalog.name
        return request.make_response(
            content,
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                ("Content-Disposition", content_disposition(filename)),
            ],
        )
