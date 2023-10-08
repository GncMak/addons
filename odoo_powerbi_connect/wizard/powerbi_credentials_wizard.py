# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import fields, models, _
from odoo.exceptions import ValidationError

class PowerbiCredentialsWizard(models.TransientModel):
    _name = "powerbi.credentials.wizard"
    _description = "Powerbi Credentials Wizard"

    user = fields.Char(
        string='Username',
        required=True)
    update_pwd = fields.Boolean(
        string='Update Password')
    pwd = fields.Char(
        string='Password')

    def action_update(self):
        self.ensure_one()
        ctx = dict(self._context or {})
        if self._context.get('active_id'):
            connection_obj = self.env['powerbi.connection'].browse(self._context['active_id'])
            user, pwd, update_pwd = self.user, self.pwd, self.update_pwd
            data = {
                'user': user
            }
            if update_pwd:
                if not pwd:
                    raise ValidationError('Password is blank...')
                if pwd != connection_obj.pwd:
                    data['pwd'] = pwd
            connection_obj.write(data)
        return self.env['powerbi.message.wizard'].genrated_message('Credentials has been updated successfully', name='Credentails updated successfully')
