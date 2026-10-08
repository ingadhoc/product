##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models
from odoo.tools.pdf import merge_pdf

# Each label report is rendered by a single wkhtmltopdf call. A picking with
# thousands of units produces thousands of pages and wkhtmltopdf dies out of
# memory (signal 11 -> return code -11). We split the render into batches of
# labels, cut at whole pages, and merge the PDFs.
DYMO_REPORT = "product.report_product_label_dymo"  # one label per page
SHEET_REPORT = "product.report_product_label_pdf"  # rows x columns labels per page
DEFAULT_BATCH_SIZE = 200  # labels per wkhtmltopdf call (whole pages on sheets)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report = self._get_report(report_ref)
        if report.report_name not in (DYMO_REPORT, SHEET_REPORT) or not data or not data.get("labels"):
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        batch_size = (
            self.env["ir.config_parameter"].sudo().get_int("product_ux.dymo_label_batch_size", DEFAULT_BATCH_SIZE)
        )
        if batch_size <= 0:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        if report.report_name == DYMO_REPORT:
            labels_per_page = 1
        else:
            layout = data.get("layout") or {}
            labels_per_page = max(int(layout.get("rows") or 1) * int(layout.get("columns") or 1), 1)
        batches = self._label_batches(data, max(batch_size // labels_per_page, 1) * labels_per_page)
        if len(batches) <= 1:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        pdf_contents = []
        for batch_data in batches:
            content, report_type = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=batch_data)
            if report_type != "pdf":
                # Rendered as HTML (tests do it): there is no wkhtmltopdf call to split.
                return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
            pdf_contents.append(content)
        return merge_pdf(pdf_contents), "pdf"

    def _label_batches(self, data, labels_per_batch):
        """Split the labels into chunks of at most ``labels_per_batch`` labels,
        so each chunk is rendered by an independent (small) wkhtmltopdf call.

        The data shape is the one built by the ``product.label.layout`` wizard:
        ``labels`` is a list of dicts, each one printed ``copies`` times. A label
        with more copies than fit in a chunk is split between chunks. Pass a
        multiple of the labels per page, so every chunk but the last one holds
        whole pages and the merged PDF has the same pages as a single render.
        """
        batches, batch, count = [], [], 0
        for label in data["labels"]:
            copies = int(label.get("copies", 1))
            while copies > 0:
                take = min(copies, labels_per_batch - count)
                batch.append(dict(label, copies=take))
                count += take
                copies -= take
                if count == labels_per_batch:
                    batches.append(batch)
                    batch, count = [], 0
        if batch:
            batches.append(batch)
        return [dict(data, labels=batch) for batch in batches]
