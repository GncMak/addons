# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import logging
_logger = logging.getLogger(__name__)
from odoo import api, models

class PowerbiSnippet(models.TransientModel):
    _name = "powerbi.snippet"
    _description = "Powerbi Snippet"

    @api.model
    def powerbi_export(self):
        tables = self.env["powerbi.table"].search([("is_published","=",True),("run_cron","=",True)])
        if tables:
            tables.export_to_powerbi()
        return True
