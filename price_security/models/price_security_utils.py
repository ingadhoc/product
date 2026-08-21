##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################


def hide_cost_fields(arch, view_type, field_names):
    """Hide cost fields from users that can only see the sale price.

    On list views the attribute has to be "column_invisible": "invisible" is
    evaluated per record, so it only blanks the cells and leaves the header,
    the optional columns toggle and the footer sum in place.
    """
    attribute = "column_invisible" if view_type == "list" else "invisible"
    for field_name in field_names:
        for node in arch.xpath("//field[@name='%s']" % field_name):
            node.set(attribute, "1")
