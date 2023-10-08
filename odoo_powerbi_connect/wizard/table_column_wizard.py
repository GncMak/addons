# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class TableColumnWizard(models.TransientModel):
    _name = "table.column.wizard"
    _description = "Column Wizard"

    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field"
    )
    field_type = fields.Selection(string="Type", related="field_id.ttype")
    child_ids = fields.Many2many(
        "ir.model.fields",
        string="Child Fields"
    )

    @api.onchange("field_id")
    def onchangeFieldId(self):
        if self.field_id.ttype in ['many2one','one2many','many2many']:
            return {"domain": {"child_ids": [('model_id.model','=',self.field_id.relation)]}}

    def action_add_column(self):
        if not self.field_id:
            raise ValidationError("Kindly select a field!")
        child_ids = [(6,0,self.child_ids.ids)] if self.child_ids else False
        res = self.env["powerbi.table.column"].create({
            "table_id": self._context['active_id'],
            "field_id": self.field_id.id,
            "field_type": self.field_type,
            "child_field_ids": child_ids
        })
        return True
