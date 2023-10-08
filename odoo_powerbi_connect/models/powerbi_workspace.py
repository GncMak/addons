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
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class PowerbiWorkspace(models.Model):
    _name = "powerbi.workspace"
    _description = "Powerbi Workspace/Group"

    name = fields.Char(string="Workspace Name")
    powerbi_id = fields.Char(string="Workspace Powerbi Id", size=50, readonly=True)
    state = fields.Selection(
        [('topublish','To Publish'),('published','Published')],
        compute="_compute_state",
        string="State"
    )
    is_published = fields.Boolean(string="Is Published", default=False)
    default_workspace = fields.Boolean(string="Default Workspace", default=False)

    @api.model
    def create(self, vals):
        if vals.get('default_workspace'):
            recs = self.search([('default_workspace','=',True)])
            if len(recs) > 0:
                raise ValidationError('Warning: Can\'t create more than 1 default workspace.')
        return super(PowerbiWorkspace, self).create(vals)
    
    def write(self, vals):
        if vals.get('default_workspace'):
            if len(self)>1:
                raise ValidationError('Warning: Can\'t create more than 1 default workspace.')
            else:
                recs = self.search([('default_workspace','=',True)])
                recs -= self
                if len(recs) > 0:
                    raise ValidationError('Warning: Can\'t create more than 1 default workspace.')
        return super(PowerbiWorkspace, self).write(vals)

    @api.depends("is_published")
    def _compute_state(self):
        for rec in self:
            if rec.is_published == True:
                rec.state = "published"
            else:
                rec.state = "topublish"

    def action_publish(self):
        return self.publish_to_powerbi()

    def publish_to_powerbi(self):
        success, failure, already_published = [], [], []
        msg = ""
        msgModel = self.env["powerbi.message.wizard"]
        connObj = self.env["powerbi.connection"].get_active_connection()
        if not connObj:
            return msgModel.genrated_message("No active connection found!")

        url = f"{connObj.api_url}/groups"
        scopes = ['Workspace.ReadWrite.All']
        connection = connObj._create_powerbi_connection(scopes)
        for expObj in self:
            if expObj.default_workspace:
                continue
            if expObj.is_published:
                already_published.append(expObj.id)
                continue
            data = {
                "name": expObj.name,
            }
            resp = self.env["powerbi.synchronization"].callPowerbiApi(url, 'post', data, connection.get('token',''), scopes)
            if resp.get('status', False):
                value = resp.get('value')
                expObj.powerbi_id = value.get('id','')
                expObj.is_published = True
                success.append(expObj.id)
            else:
                failure.append(expObj.id)
                self.env["powerbi.sync.history"].create({
                    "status": "no",
                    "action": "b",
                    "action_on": "workspace",
                    "error_message": "Workspace export error, id "+str(expObj.id)+": Reason - "+str(resp.get("message"))
                })
        if success:
            msg+=f"{len(success)} workspace(s) successfully published."
            self.env["powerbi.sync.history"].create({
                    "status": "yes",
                    "action": "b",
                    "action_on": "workspace",
                    "error_message": "Workspace id(s) "+str(success)+" successfully exported to powerbi."
                })
        if failure:
            msg+=f"{len(failure)} workspaces(s) can't be published."
        if already_published:
            msg+=f"{len(already_published)} workspaces(s) are already published."

        return msgModel.genrated_message(msg)

    @api.model
    def _create_sale_order_data(self):
        saleModule = self.env["ir.module.module"].search([('name','=','sale'),('state','=','installed')],limit=1)
        if saleModule:
            modelObj = self.env["ir.model"].search([("model","=","sale.order")],limit=1)
            model = modelObj.model
            workspace = self.search([('default_workspace','=',True)],limit=1)
            if not workspace:
                workspace = self.create({"name": "My Workspace", "default_workspace": True, "is_published": True})
            dataset = self.env["powerbi.dataset"].create({
                "name": "Odoo Sales",
                "dataset_type": "temp",
                "workspace_id": workspace.id
            })
            table = self.env["powerbi.table"].create({
                "name": "Sales",
                "dataset_id": dataset.id,
                "model_id": modelObj.id,
                "model_name": model
            })
            self._create_table_column(model, table,{
                "name": "",
                "amount_total": "",
                "date_order": "",
                "partner_id": "name"
            })
        return True

    @api.model
    def _create_invoice_data(self):
        invModule = self.env["ir.module.module"].search([('name','=','account'),('state','=','installed')],limit=1)
        if invModule:
            modelObj = self.env["ir.model"].search([("model","=","account.move")],limit=1)
            model = modelObj.model
            workspace = self.search([('default_workspace','=',True)],limit=1)
            if not workspace:
                workspace = self.create({"name": "My Workspace", "default_workspace": True, "is_published": True})
            dataset = self.env["powerbi.dataset"].create({
                "name": "Odoo Invoices",
                "dataset_type": "temp",
                "workspace_id": workspace.id
            })
            table = self.env["powerbi.table"].create({
                "name": "Invoices",
                "dataset_id": dataset.id,
                "model_id": modelObj.id,
                "model_name": model
            })
            self._create_table_column(model, table,{
                "name": "",
                "amount_total": "",
                "invoice_date": "",
                "invoice_origin": "",
                "move_type": ""
            })
        return True

    @api.model
    def _create_stock_data(self):
        stockModule = self.env["ir.module.module"].search([('name','=','stock'),('state','=','installed')],limit=1)
        if stockModule:
            modelObj = self.env["ir.model"].search([("model","=","stock.move")],limit=1)
            model = modelObj.model
            workspace = self.search([('default_workspace','=',True)],limit=1)
            if not workspace:
                workspace = self.create({"name": "My Workspace", "default_workspace": True, "is_published": True})
            dataset = self.env["powerbi.dataset"].create({
                "name": "Odoo Inventory",
                "dataset_type": "temp",
                "workspace_id": workspace.id
            })
            table = self.env["powerbi.table"].create({
                "name": "Inventory",
                "dataset_id": dataset.id,
                "model_id": modelObj.id,
                "model_name": model
            })
            self._create_table_column(model, table,{
                "name": "",
                "origin": "",
                "price_unit": "",
                "product_id": "name"
            })
        return True

    @api.model
    def _create_purchase_data(self):
        purchaseModule = self.env["ir.module.module"].search([('name','=','purchase'),('state','=','installed')],limit=1)
        if purchaseModule:
            modelObj = self.env["ir.model"].search([("model","=","purchase.order")],limit=1)
            model = modelObj.model
            workspace = self.search([('default_workspace','=',True)],limit=1)
            if not workspace:
                workspace = self.create({"name": "My Workspace", "default_workspace": True, "is_published": True})
            dataset = self.env["powerbi.dataset"].create({
                "name": "Odoo Purchase",
                "dataset_type": "temp",
                "workspace_id": workspace.id
            })
            table = self.env["powerbi.table"].create({
                "name": "Purchase",
                "dataset_id": dataset.id,
                "model_id": modelObj.id,
                "model_name": model
            })
            self._create_table_column(model, table,{
                "name": "",
                "origin": "",
                "amount_total": "",
                "date_order": "",
                "partner_id": "name"
            })
        return True

    @api.model
    def _create_pos_data(self):
        posModule = self.env["ir.module.module"].search([('name','=','point_of_sale'),('state','=','installed')],limit=1)
        if posModule:
            modelObj = self.env["ir.model"].search([("model","=","pos.order")],limit=1)
            model = modelObj.model
            workspace = self.search([('default_workspace','=',True)],limit=1)
            if not workspace:
                workspace = self.create({"name": "My Workspace", "default_workspace": True, "is_published": True})
            dataset = self.env["powerbi.dataset"].create({
                "name": "Odoo POS",
                "dataset_type": "temp",
                "workspace_id": workspace.id
            })
            table = self.env["powerbi.table"].create({
                "name": "POS",
                "dataset_id": dataset.id,
                "model_id": modelObj.id,
                "model_name": model
            })
            self._create_table_column(model, table,{
                "name": "",
                "amount_total": "",
                "date_order": "",
                "partner_id": "name"
            })
        return True
            

    def _create_table_column(self, model, table, fields):
        for field in fields.keys():
            field_id = self.env["ir.model.fields"].search([('model_id.model','=',model),('name','=',field)],limit=1)
            child = []
            if fields.get(field):
                ch_field_id = self.env["ir.model.fields"].search([('model_id.model','=',field_id.relation),('name','=',fields.get(field))],limit=1)
                child = [(6,0,[ch_field_id.id])]
            self.env["powerbi.table.column"].create({
                "table_id": table.id,
                "field_id": field_id.id,
                "field_type": field_id.ttype,
                "child_field_ids": child if child else False
            })
