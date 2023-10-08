# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

class PowerbiReportWizard(models.TransientModel):
    _name = "powerbi.report.wizard"
    _description = "View Powerbi Reports"

    powerbi_id = fields.Char(string="Powerbi Id", required=True)
    name = fields.Char(string="Name")
    