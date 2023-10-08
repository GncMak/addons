# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class PowerbiTableColumn(models.Model):
    _name = "powerbi.table.column"
    _description = "Powerbi Table Columns"

    name = fields.Char(string="Name", related="field_id.name")
    table_id = fields.Many2one(
        "powerbi.table",
        string="Table"
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field"
    )
    field_type = fields.Char(string="Type")
    child_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Child Fields",
    )

    def create(self, vals):
        res = super(PowerbiTableColumn, self).create(vals)
        if res and vals.get("table_id"):
            table = self.env["powerbi.table"].browse(vals.get("table_id"))
            table.is_modified = True
        return res
