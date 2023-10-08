# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

import ast
import logging

from odoo.http import request
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class PowerbiTable(models.Model):
    _name = "powerbi.table"
    _description = "Powerbi Table"

    name = fields.Char(string="Table Name", required=True)
    dataset_id = fields.Many2one(
        "powerbi.dataset",
        string="Dataset",
        domain="[('is_published','!=',True)]",
        required=True)
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        ondelete="set null",
    )
    model_name = fields.Char(string="Model Name")
    column_ids = fields.One2many(
        "powerbi.table.column",
        inverse_name="table_id",
        string="Table Fields",
    )
    filter_domain = fields.Char(string="Domain")
    state = fields.Selection(
        [('topublish','To Publish'),('published','Published')],
        compute="_compute_state",
        string="State"
    )
    is_published = fields.Boolean(string="Is Published", default=False)
    is_modified = fields.Boolean(string="Modified", default=False)
    run_cron = fields.Boolean(string="Run cron", default=False)
    export_action = fields.Integer(string="Action Id", default=0)

    @api.depends("is_published")
    def _compute_state(self):
        for rec in self:
            if rec.is_published == True:
                rec.state = "published"
            else:
                rec.state = "topublish"

    @api.onchange("model_id")
    def onchange_model(self):
        self.model_name = self.model_id.model
        self.column_ids = [(6,0,[])]
        model = self.model_id.model
        if model == "sale.order":
            self._create_column(model, {
                "name": "",
                "amount_total": "",
                "date_order": "",
                "partner_id": "name",
                "order_line": "product_id"
            })
        elif model == "account.move":
            self._create_column(model, {
                "name": "",
                "invoice_origin": "",
                "amount_total": "",
                "invoice_date": "",
                "move_type": ""
            })
        elif model == "stock.move":
            self._create_column(model, {
                "name": "",
                "origin": "",
                "price_unit": "",
                "product_id": "name"
            })

    def _create_column(self, model, fields):
        for field in fields.keys():
            field_id = self.env["ir.model.fields"].search([('model_id.model','=',model),('name','=',field)],limit=1)
            child = []
            if fields.get(field):
                ch_field_id = self.env["ir.model.fields"].search([('model_id.model','=',field_id.relation),('name','=',fields.get(field))],limit=1)
                child = [(6,0,[ch_field_id.id])]
            self.env["powerbi.table.column"].create({
                "table_id": self.id,
                "field_id": field_id.id,
                "field_type": field_id.ttype,
                "child_field_ids": child if child else False
            })

    def write(self, vals):
        if "column_ids" in vals:
            vals.update(is_modified=True)
        return super(PowerbiTable, self).write(vals)

    def action_export(self):
        return self.export_to_powerbi()
    
    def action_delete(self):
        return self.delete_powerbi_data()
    
    def action_update_schema(self):
        return self.update_table_schema()

    def export_to_powerbi(self):
        success, failure, not_published, no_data = [], [], 0, 0
        msg = ""
        msgModel = self.env["powerbi.message.wizard"]
        connObj = self.env["powerbi.connection"].get_active_connection()
        if not connObj:
            return msgModel.genrated_message("No active connection found!")
        scopes = ["Dataset.ReadWrite.All"]
        connection = connObj._create_powerbi_connection(scopes)
        for expObj in self:
            if not expObj.is_published:
                not_published += 1
                continue
            model = self.env[expObj.model_id.model]
            domain = []
            if expObj.filter_domain:
                domain = ast.literal_eval(expObj.filter_domain)
            records = model.search(domain)
            rows = []
            for rec in records:
                rows.extend(expObj.get_row_data(rec))
            if not rows:
                no_data += 1
                continue
            if expObj.dataset_id.workspace_id.default_workspace:
                url = f"{connObj.api_url}/datasets/{expObj.dataset_id.powerbi_id}/tables/{expObj.name}/rows"
            else:
                url = f"{connObj.api_url}/groups/{expObj.dataset_id.workspace_id.powerbi_id}/datasets/{expObj.dataset_id.powerbi_id}/tables/{expObj.name}/rows"
            count = 10000
            tempRows = rows[:count] if len(rows) > count else rows
            while tempRows:
                data = {
                    "rows" : tempRows
                }
                resp = self.env["powerbi.synchronization"].callPowerbiApi(url, "post", data=data, token=connection.get('token'), scope=scopes)
                if resp.get('status'):
                    if expObj.id not in success:
                        success.append(expObj.id)
                else:
                    if expObj.id not in failure:
                        failure.append(expObj.id)
                    self.env["powerbi.sync.history"].create({
                        "status": "no",
                        "action": "b",
                        "action_on": "table",
                        "error_message": "Table data export error, id "+str(expObj.id)+": Reason - "+str(resp.get("message"))
                    })
                if len(rows) > len(tempRows):
                    tempRows = rows[count:count+10000] if len(rows) > count+10000 else rows[count:]
                    count += 10000
                else:
                    tempRows = []
        if success:
            msg+=f"{len(success)} table data successfully exported."
            self.env["powerbi.sync.history"].create({
                    "status": "yes",
                    "action": "b",
                    "action_on": "table",
                    "error_message": "Data for table id(s) "+str(success)+" successfully exported to powerbi."
                })
        if failure:
            msg+=f"{len(failure)} table data can't be exported."
        if not_published:
            msg+=f"{not_published} tables not published yet."
        if no_data:
            msg+=f"{no_data} tables have no data to export."
        return msgModel.genrated_message(msg)

    def get_row_data(self, dataObj):
        self.ensure_one()
        rows = []
        simpleRow = {}
        for col in self.column_ids.filtered(lambda l: l.field_type not in ['one2many','many2many','many2one']):
            value = getattr(dataObj, col.name)
            simpleRow[col.name] = value or '' if col.field_type in ['date','datetime'] else value
        rows.append(simpleRow)
        for col in self.column_ids.filtered(lambda l: l.field_type in ['one2many','many2many','many2one']):
            if col.child_field_ids:
                Objs = getattr(dataObj, col.name)
                if not Objs:
                    continue
                for child in col.child_field_ids.filtered(lambda ch: ch.ttype not in ['one2many','many2one','many2many']):
                    rRows = []
                    keyName = col.name+"."+child.name
                    for Obj in Objs:
                        value = getattr(Obj, child.name)
                        rRows.append({keyName: value or '' if child.ttype in ['date','datetime'] else value})
                    for r1 in rRows:
                        tempRows = []
                        for r2 in rows:
                            if keyName in r2.keys():
                                newrow = dict(r2)
                                newrow.update(r1)
                                tempRows.append(newrow)
                            else:
                                r2.update(r1)
                        rows.extend(tempRows)
                for child in col.child_field_ids.filtered(lambda ch: ch.ttype in ['one2many','many2one','many2many']):
                    keyName = col.name+"."+child.name
                    for Obj in Objs:
                        rRows = []
                        childObjs = getattr(Obj, child.name)
                        if not childObjs:
                            continue
                        for childObj in childObjs:
                            value = getattr(childObj,childObj._rec_name)
                            rRows.append({keyName: value})
                        for r1 in rRows:
                            tempRows = []
                            for r2 in rows:
                                if keyName in r2.keys():
                                    newrow = dict(r2)
                                    newrow.update(r1)
                                    tempRows.append(newrow)
                                else:
                                    r2.update(r1)
                            rows.extend(tempRows)
            else:
                rRows = []
                Objs = getattr(dataObj, col.name)
                if not Objs:
                    continue
                for Obj in Objs:
                    value = getattr(Obj,Obj._rec_name)
                    rRows.append({col.name: value})
                for r1 in rRows:
                    tempRows = []
                    for r2 in rows:
                        if col.name in r2.keys():
                            newrow = dict(r2)
                            newrow.update(r1)
                            tempRows.append(newrow)
                        else:
                            r2.update(r1)
                    rows.extend(tempRows)
        return self.remove_duplicates(rows)
    
    def remove_duplicates(self, rows):
        filtered_rows = []
        for row in rows:
            if row not in filtered_rows:
                filtered_rows.append(row)
        return filtered_rows

    def delete_powerbi_data(self):
        success, failure, not_published = [], [], 0
        msg = ""
        msgModel = self.env["powerbi.message.wizard"]
        connObj = self.env["powerbi.connection"].get_active_connection()
        if not connObj:
            return msgModel.genrated_message("No active connection found!")
        scopes = ["Dataset.ReadWrite.All"]
        connection = connObj._create_powerbi_connection(scopes)
        for Obj in self:
            if not Obj.is_published:
                not_published += 1
            if Obj.dataset_id.workspace_id.default_workspace:
                url = f"{connObj.api_url}/datasets/{Obj.dataset_id.powerbi_id}/tables/{Obj.name}/rows"
            else:
                url = f"{connObj.api_url}/groups/{Obj.dataset_id.workspace_id.powerbi_id}/datasets/{Obj.dataset_id.powerbi_id}/tables/{Obj.name}/rows"
            resp = self.env["powerbi.synchronization"].callPowerbiApi(url, "delete", token=connection.get('token',''), scope=scopes)
            if resp.get('status'):
                success.append(Obj.id)
            else:
                failure.append(Obj.id)
                self.env["powerbi.sync.history"].create({
                    "status": "no",
                    "action": "d",
                    "action_on": "table",
                    "error_message": "Table data delete error, id "+str(Obj.id)+": Reason - "+str(resp.get("message"))
                })
        if success:
            msg+=f"{len(success)} table data successfully deleted."
            self.env["powerbi.sync.history"].create({
                    "status": "yes",
                    "action": "d",
                    "action_on": "table",
                    "error_message": "Data for table id(s) "+str(success)+" successfully deleted."
                })
        if failure:
            msg+=f"{len(failure)} table data can't be deleted."
        if not_published:
            msg+=f"{not_published} tables not published yet."
        return msgModel.genrated_message(msg)

    def update_table_schema(self):
        success, failure, not_published, no_columns = [], [], 0, 0
        msg = ""
        msgModel = self.env["powerbi.message.wizard"]
        connObj = self.env["powerbi.connection"].get_active_connection()
        if not connObj:
            return msgModel.genrated_message("No active connection found!")
        scopes = ["Dataset.ReadWrite.All"]
        connection = connObj._create_powerbi_connection(scopes)
        for Obj in self:
            if not Obj.is_modified:
                continue
            if not Obj.is_published:
                not_published += 1
                continue
            columns = self.env["powerbi.dataset"].get_table_columns(Obj)
            if not columns:
                no_columns += 1
                continue
            data = {
                "name": Obj.name,
                "columns": columns
            }
            if Obj.dataset_id.workspace_id.default_workspace:
                url = f"{connObj.api_url}/datasets/{Obj.dataset_id.powerbi_id}/tables/{Obj.name}"
            else:
                url = f"{connObj.api_url}/groups/{Obj.dataset_id.workspace_id.powerbi_id}/datasets/{Obj.dataset_id.powerbi_id}/tables/{Obj.name}"
            resp = self.env["powerbi.synchronization"].callPowerbiApi(url, "put", data=data, token=connection.get('token'), scope=scopes)
            if resp.get('status'):
                Obj.is_modified = False
                success.append(Obj.id)
            else:
                failure.append(Obj.id)
                self.env["powerbi.sync.history"].create({
                    "status": "no",
                    "action": "c",
                    "action_on": "table",
                    "error_message": "Table update error, id "+str(Obj.id)+": Reason - "+str(resp.get("message"))
                })
        if success:
            msg+=f"{len(success)} tables successfully updated.\n"
            self.env["powerbi.sync.history"].create({
                    "status": "yes",
                    "action": "c",
                    "action_on": "table",
                    "error_message": "Table id(s) "+str(success)+" successfully updated."
                })
        if failure:
            msg+=f"{len(failure)} tables can't be updated.\n"
        if not_published:
            msg+=f"{not_published} tables not published yet.\n"
        if no_columns:
            msg+=f"{no_columns} tables does not have any columns to update.\n"
        return msgModel.genrated_message(msg)

    def open_column_wizard(self):
        partial = self.env["table.column.wizard"].create({})
        ctx = dict(self._context or {})
        ctx['domain_model_name'] = self.model_id.model
        ctx['map_ids'] = [col.field_id.id for col in self.column_ids]
        return {'name': "Add Column",
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'table.column.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                'domain': '[]',
                }

    def create_server_action(self):
        self.ensure_one()
        model_id = self.model_id.id
        name = self.model_id.name
        existing_action = self.search([('model_id','=',model_id),
                                    ('export_action','!=',0)],limit=1)
        if not existing_action:
            message = 'Message: Server Action Created Succesfully For Model %s'%name
            code = "action = env['powerbi.wizard'].start_data_synchronisation()"
            action_server = False
            try:
                action_server = self.env['ir.actions.server'].create({
                    'name':'Export To Powerbi',
                    'model_id': model_id,
                    'state':'code',
                    'binding_model_id': model_id,
                    'code': code
                })
            except Exception as e:
                message= 'Message: Error While Creating Server Action: %s'%str(e)
            if action_server:
                self.export_action = action_server.id
        else:
            message = 'Message: Server Action Is Already Created For The Model %s'%name
        return self.env['powerbi.message.wizard'].genrated_message(message)

    def delete_server_action(self):
        self.ensure_one()
        model_id = self.model_id.id
        name = self.model_id.name
        existing_action = self.search([('model_id','=',model_id),
                                    ('export_action','!=',0)],limit=1)

        if existing_action:
            message = 'Server Action deleted successfully for model %s'%name
            action_server = self.env['ir.actions.server'].search([('id','=',existing_action.export_action)])
            if action_server:
                try:
                    res = action_server.unlink()
                    if res:
                        existing_action.export_action = 0
                except Exception as e:
                    message = 'Error while deleting server action: %s'%str(e)
            else:
                message = "No server action found for the model %s"%name
        else:
            message = "No server action found for the model %s"%name
        return self.env["powerbi.message.wizard"].genrated_message(message)

    def configure_cron(self):
        self.ensure_one()
        action_cron = request.env.ref("odoo_powerbi_connect.powerbi_export_data_cron")
        return {'name': "Cron",
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'ir.cron',
                'res_id': action_cron.id,
                'type': 'ir.actions.act_window',
                }
