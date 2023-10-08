# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import logging
import msal

from odoo.http import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

required_scopes = ['Workspace.Read.All','Report.Read.All','Dashboard.Read.All','Dataset.Read.All',
                'Workspace.ReadWrite.All','Report.ReadWrite.All','Dashboard.ReadWrite.All',
                'Dataset.ReadWrite.All']

class PowerbiConnection(models.Model):
    _name = "powerbi.connection"
    _description = "Powerbi Connection Configuration"
    _rec_name = "instance"


    def _default_api_url(self):
        return "https://api.powerbi.com/v1.0/myorg"
    
    def _default_authorization_url(self):
        return "https://login.microsoftonline.com"

    def _default_instance_name(self):
        return self.env[
            'ir.sequence'].next_by_code('powerbi.connection')

    instance = fields.Char(
        string='Instance Name',
        default=lambda self: self._default_instance_name()
    )
    api_url = fields.Char(
        string='API URL',
        track_visibility="onchange",
        default=lambda self:self._default_api_url(),
        readonly=True
    )
    authority_url = fields.Char(
        string="Authorization URL",
        track_visibility="onchange",
        default=lambda self:self._default_authorization_url(),
        readonly=True
    )
    user = fields.Char(
        string='Username',
        track_visibility="onchange",
        )
    pwd = fields.Char(
        string='Password',
        track_visibility="onchange",
        )
    status = fields.Char(string='Status', readonly=True)
    connection_status = fields.Boolean(
        string="Connection Status",
        default=False,
        readonly=True)
    active = fields.Boolean(
        string="Active",
        track_visibility="onchange",
        default=True)
    access_method = fields.Selection(
        [('mu','MasterUser'),('sp','ServicePrinciple')],
        string='Access Method',
        track_visibility="onchange",
        required=True
    )
    token = fields.Char(string='Token', size=2500)
    client_id = fields.Char(string='Client Id', size=50)
    client_secret = fields.Char(string='Client Secret', size=50)
    tenent_id = fields.Char(string='Tenent Id', size=50)

    redirect_uri = fields.Char(string='Redirect URI', required=True)

    @api.model
    def create(self, vals):
        activeConn = self.search([('active','=',True)])
        if activeConn:
            raise UserError(
                _('Warning!\nSorry, Only one active connection is allowed.'))
        method = vals.get('access_method', '')
        if method == 'mu':
            if not (vals.get('user','') and vals.get('pwd','') and vals.get('client_id','')):
                raise ValidationError(
                    _('Warning!\nUsername, Password and Client Id are required in MasterUser access method.')
                )
        else:
            if not (vals.get('tenent_id','') and vals.get('client_secret','') and vals.get('client_id','')):
                raise ValidationError(
                    _('Warning!\Tenent Id, Client Id and Client Secret are required in Serviceprinciple access method.')
                )
        vals['instance'] = self.env[
            'ir.sequence'].next_by_code('powerbi.connection')
        return super().create(vals)

    def write(self, vals):
        activeConn = self.search([('active','=',True)])
        if len(activeConn)>1:
            raise UserError(
                _('Warning!\nSorry, Only one active connection is allowed.'))
        for instance_obj in self:
            if not instance_obj.instance:
                vals['instance'] = self.env[
                        'ir.sequence'].next_by_code('powerbi.connection')
        return super().write(vals)

    def test_powerbi_connection(self):
        token = ""
        status = "Not Connected to Powerbi."
        connection_status = False
        text = "Unsuccessful connection, kindly verify your credential!!"
        connection = self._create_powerbi_connection()
        if connection.get("token", ""):
            self.token = str(connection.get("token", ""))
            status = "Congratulation, It's Successfully Connected with Powerbi."
            connection_status = True
            text = connection.get("message", "")
        else:
            status = connection.get("message", "")
        self.status = status
        self.connection_status = connection_status
        res_model = 'powerbi.message.wizard'
        partial = self.env[res_model].create({'text': text})
        ctx = dict(self._context or {})
        ctx['text'] = text
        ctx['instance_id'] = self.id
        return {'name': ("Odoo Powerbi Connector"),
                'view_mode': 'form',
                'res_model': res_model,
                'view_id': False,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'context': ctx,
                'target': 'new',
                }

    def _create_powerbi_connection(self, scope=[]):
        text, token, status = "", "", False
        url = self.authority_url+"/"+self.tenent_id
        client_id = self.client_id
        client_secret = self.client_secret
        resource_url = "https://analysis.windows.net/powerbi/api"
        all_scopes = []
        for s in scope:
            all_scopes.append(resource_url+"/"+s)
        app = msal.ConfidentialClientApplication(client_id, client_credential=client_secret, authority=url)
        if self.access_method == "mu":
            user = self.user
            pswd = self.pwd
            if not (user and pswd):
                return {'token':token, 'message':"Username or Password not set!", 'status':status}
            resp = app.acquire_token_by_username_password(user, pswd, scopes=all_scopes)
        else:
            resp = app.acquire_token_for_client(scopes=all_scopes)
        if resp.get("access_token", ""):
            token = "Bearer "+str(resp.get("access_token", ""))
            text = "Test connection successful, now you can proceed with synchronization!!"
            status = True
        else:
            text = "Connection error : "+resp.get("error_description")
            if resp.get("suberror")=="consent_required":
                allScopes = ''
                for scp in required_scopes:
                    allScopes+=f'{resource_url}/{scp} '
                text = """Connection error: The user or administrator has not consented to use the application.
                        Send an interactive authorization request on this url - """
                text += f"{url}/oauth2/v2.0/authorize?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}&response_mode=query&scope={allScopes}openid&state=12345"
        return {'token':token, 'message':text, 'status':status}

    def get_active_connection(self):
        domain = ['&',('active','=',True),('connection_status','=',True)]
        connObj = self.search(domain)
        return connObj
    
    def update_credentials(self):
        self.ensure_one()
        partial = self.env['powerbi.credentials.wizard'].create({
            'user': self.user
        })
        return {
            'name': ("Update Credentials."),
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'powerbi.credentials.wizard',
            'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': self._context,
            'domain': '[]',
        }

    def open_report_wizard(self):
        partial = self.env["powerbi.wizard"].create({})
        ctx = dict(self._context or {})
        ctx['report'] = True
        view_id = request.env.ref('odoo_powerbi_connect.id_powerbi_wizard_view_form').id
        return {'name': "Import Powerbi Reports",
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'powerbi.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    def open_dashboard_wizard(self):
        partial = self.env["powerbi.wizard"].create({})
        ctx = dict(self._context or {})
        ctx['dashboard'] = True
        view_id = request.env.ref('odoo_powerbi_connect.id_powerbi_wizard_view_form').id
        return {'name': "Import Powerbi Dashboards",
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'powerbi.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }
    
    def action_import_workspace(self):
        success = []
        msgModel = self.env["powerbi.message.wizard"]
        scope = ["Workspace.Read.All"]
        connection = self._create_powerbi_connection(scope)
        if connection.get('status'):
            url = f"{self.api_url}/groups"
            resp = self.env["powerbi.synchronization"].callPowerbiApi(url, "get", token=connection.get('token'), scope=scope)
            if resp.get('status'):
                workspaces = resp['value'].get('value',[])
                workspaceModel = self.env["powerbi.workspace"]
                for workspace in workspaces:
                    pid = workspace.get('id','')
                    name = workspace.get('name','')
                    workspaceObj = workspaceModel.search([('powerbi_id', '=', pid)])
                    if not workspaceObj:
                        res = workspaceModel.create({
                                "powerbi_id": pid,
                                "name": name,
                                "is_published": True
                            })
                        success.append(res.id)
                if success:
                    self.env["powerbi.sync.history"].create({
                        "status": "yes",
                        "action": "a",
                        "action_on": "workspace",
                        "error_message": "Workspace id(s) "+str(success)+" successfully imported."
                    })
                return msgModel.genrated_message("All Workspaces imported successfully.")
            else:
                self.env["powerbi.sync.history"].create({
                        "status": "no",
                        "action": "a",
                        "action_on": "workspace",
                        "error_message": "Workspace import error, Reason: "+resp.get("message")
                    })
                return msgModel.genrated_message(resp.get('message'))
        else:
            return msgModel.genrated_message(connection.get('message'))
