from lxml import html
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged

# Classes that hide a cell on a wide (desktop) screen.
HIDDEN_ON_DESKTOP = {"d-sm-none", "d-md-none", "d-lg-none"}


def _visible_on_desktop(cell):
    classes = set(cell.get("class", "").split())
    if classes & HIDDEN_ON_DESKTOP:
        return False
    return "d-none" not in classes or any(c.endswith("table-cell") for c in classes)


def _width(row, tag):
    return sum(int(c.get("colspan") or 1) for c in row.findall(tag) if _visible_on_desktop(c))


@tagged("post_install", "-at_install")
class TestProductBrandReport(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids += cls.env.ref("sales_team.group_sale_salesman") + cls.env.ref("base.group_system")
        cls.brand = cls.env["product.brand"].create({"name": "Brand Test"})
        cls.product_a.product_brand_id = cls.brand
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "order_line": [
                    (0, 0, {"display_type": "line_section", "name": "Section"}),
                    (0, 0, {"product_id": cls.product_a.id, "product_uom_qty": 1, "discount": 10}),
                    (0, 0, {"display_type": "line_note", "name": "Note"}),
                ],
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_date": "2019-01-01",
                "invoice_line_ids": [
                    (0, 0, {"display_type": "line_section", "name": "Section"}),
                    (0, 0, {"product_id": cls.product_a.id, "quantity": 1, "price_unit": 100, "discount": 10}),
                    (0, 0, {"display_type": "line_note", "name": "Note"}),
                ],
            }
        )
        cls.invoice.action_post()

    def _set_show_brand(self, value):
        self.env["res.config.settings"].create(
            {"show_brand_sales_report": value, "show_brand_invoice_report": value}
        ).execute()

    def _render_report(self, report_ref, records):
        content = self.env["ir.actions.report"]._render_qweb_html(report_ref, records.ids)[0]
        return html.fromstring(content)

    def _render_portal(self):
        content = self.env["ir.qweb"]._render(
            "sale.sale_order_portal_content", {"sale_order": self.sale_order, "report_type": "html"}
        )
        return html.fromstring(str(content))

    def _assert_rows_aligned(self, table):
        header = table.find(".//thead/tr")
        header_width = _width(header, "th")
        for row in table.findall(".//tbody/tr"):
            cells = [c for c in row.findall("td") if _visible_on_desktop(c)]
            if not cells or any(int(c.get("colspan") or 1) >= 99 for c in cells):
                continue
            self.assertEqual(_width(row, "td"), header_width, html.tostring(row))

    def _check_table(self, doc, table_xpath, show_brand):
        table = doc.xpath(table_xpath)[0]
        headers = [th.text_content().strip() for th in table.find(".//thead/tr").findall("th")]
        self.assertEqual("Brand" in headers, show_brand)
        self.assertEqual("Brand Test" in table.text_content(), show_brand)
        self._assert_rows_aligned(table)

    def test_invoice_report(self):
        for show_brand in (False, True):
            self._set_show_brand(show_brand)
            doc = self._render_report("account.account_invoices", self.invoice)
            self._check_table(doc, "//table[@name='invoice_line_table']", show_brand)

    def test_invoice_report_grouped(self):
        section = self.invoice.invoice_line_ids.filtered(lambda line: line.display_type == "line_section")
        for collapse in ("collapse_composition", "collapse_prices"):
            section[collapse] = True
            for show_brand in (False, True):
                self._set_show_brand(show_brand)
                doc = self._render_report("account.account_invoices", self.invoice)
                table = doc.xpath("//table[@name='invoice_line_table']")[0]
                self._assert_rows_aligned(table)
            section[collapse] = False

    def test_sale_report(self):
        for show_brand in (False, True):
            self._set_show_brand(show_brand)
            doc = self._render_report("sale.action_report_saleorder", self.sale_order)
            self._check_table(doc, "//table[contains(@class, 'o_main_table')]", show_brand)

    def test_sale_portal(self):
        for show_brand in (False, True):
            self._set_show_brand(show_brand)
            doc = self._render_portal()
            self._check_table(doc, "//table[@id='sales_order_table']", show_brand)
