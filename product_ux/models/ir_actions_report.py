##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models
from odoo.tools.pdf import merge_pdf

# The Dymo report prints one label per page. A picking with thousands of units
# produces a PDF of thousands of pages and wkhtmltopdf dies out of memory
# (signal 11 -> return code -11). We split the render into batches and merge.
DYMO_REPORT = "product.report_producttemplatelabel_dymo"
DEFAULT_BATCH_SIZE = 200


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report = self._get_report(report_ref)
        if report.report_name != DYMO_REPORT or not data:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        batch_size = int(
            self.env["ir.config_parameter"].sudo().get_param("product_ux.dymo_label_batch_size", DEFAULT_BATCH_SIZE)
        )
        if batch_size <= 0:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        batches = self._dymo_label_batches(data, batch_size)
        if len(batches) <= 1:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        pdf_contents = []
        for batch_data in batches:
            content, _dummy = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=batch_data)
            pdf_contents.append(content)
        return merge_pdf(pdf_contents), "pdf"

    def _dymo_label_batches(self, data, batch_size):
        """Split the label data into chunks of at most ``batch_size`` labels,
        so each chunk is rendered by an independent (small) wkhtmltopdf call.

        The data shape is the one built by the ``product.label.layout`` wizard:
        ``quantity_by_product`` ({product: qty}) plus an optional
        ``custom_barcodes`` ({product: [(barcode, qty)]}) for lots/serials.
        """
        qty_by_product = data.get("quantity_by_product") or {}
        custom_barcodes = data.get("custom_barcodes") or {}

        # Flatten everything to a stream of (source, key, barcode, qty) groups.
        units = [("qty", key, None, int(q)) for key, q in qty_by_product.items()]
        for key, barcode_qtys in custom_barcodes.items():
            units += [("custom", key, bc, int(q)) for bc, q in barcode_qtys]

        batches = []
        cur_qty, cur_custom, count = {}, {}, 0
        for source, key, barcode, qty in units:
            while qty > 0:
                take = min(qty, batch_size - count)
                if source == "qty":
                    cur_qty[key] = cur_qty.get(key, 0) + take
                else:
                    cur_custom.setdefault(key, []).append((barcode, take))
                count += take
                qty -= take
                if count >= batch_size:
                    batches.append((cur_qty, cur_custom))
                    cur_qty, cur_custom, count = {}, {}, 0
        if count:
            batches.append((cur_qty, cur_custom))

        result = []
        for b_qty, b_custom in batches:
            batch_data = dict(data)
            batch_data["quantity_by_product"] = b_qty
            if custom_barcodes:
                batch_data["custom_barcodes"] = b_custom
            result.append(batch_data)
        return result
