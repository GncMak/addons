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

class PowerbiSyncHistory(models.Model):
    _name = "powerbi.sync.history"
    _description = "Powerbi Synchronization History"

    status = fields.Selection([
        ('yes', 'Successfull'),
        ('no', 'Un-Successfull')
    ], string='Status')
    action = fields.Selection([
        ('a', 'Import'),
        ('b', 'Export'),
        ('c', 'Update'),
        ('d', 'Delete')
    ], string='Action')
    action_on = fields.Selection([
        ('workspace', 'Workspace'),
        ('dataset', 'Dataset'),
        ('table', 'Table'),
        ('report', 'Report'),
        ('dashboard', 'Dashboard'),
        ('token', 'Embed Token')
    ], string="Action On")
    create_date = fields.Datetime(string='Created Date')
    error_message = fields.Text(string='Summary')
