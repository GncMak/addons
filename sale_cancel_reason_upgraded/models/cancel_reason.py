# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

QUOTATION_STATES = ['draft', 'sent', 'sale', 'quotation_approval', 'quotation_approved', 'sale_approval']


class SaleOrderCancel(models.TransientModel):
    _inherit = 'sale.order.cancel'

    @api.multi
    def confirm_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        sale_ids = self._context.get('active_ids')
        if sale_ids is None:
            return act_close
        assert len(sale_ids) == 1, "Only 1 sale ID expected"
        sale = self.env['sale.order'].browse(sale_ids)
        sale.cancel_reason_id = self.reason_id.id
        # in the official addons, they call the signal on quotations
        # but directly call action_cancel on sales orders
        if sale.state in QUOTATION_STATES:
            sale.action_cancel()
        else:
            raise UserError(_('You cannot cancel the Quotation/Order in the '
                              'current state!'))
        return act_close
