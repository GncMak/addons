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

class PowerbiDataset(models.Model):
    _name = "powerbi.dataset"
    _description = "Powerbi Dataset"

    powerbiDatatypes = {
        "char": "string",
        "text": "string",
        "selection": "string",
        "float": "Double",
        "integer": "Int64",
        "monetary": "Double",
        "boolean": "bool",
        "many2one": "string",
        "date": "DateTime",
        "datetime": "DateTime",
        "many2many": "string",
        "one2many": "string"
    }

    name = fields.Char(string="Dataset Name", required=True)
    powerbi_id = fields.Char(string="Dataset Powerbi Id", size=50, readonly=True)
    dataset_type = fields.Selection(
        [('perm','Permanent'),('temp','Temporary')],
        string="Type",
        required=True
    )
    state = fields.Selection(
        [('topublish','To Publish'),('published','Published')],
        compute="_compute_state",
        string="State"
    )
    is_published = fields.Boolean(string="Is Published", default=False)
    workspace_id = fields.Many2one(
        "powerbi.workspace",
        string="Workspace",
        required=True
    )
    table_ids = fields.One2many(
        "powerbi.table",
        inverse_name="dataset_id",
        string="Tables",
        readonly=True
    )
    
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
        success, failure, already_published, no_tables = [], [], [], []
        msg = ""
        msgModel = self.env["powerbi.message.wizard"]
        connObj = self.env["powerbi.connection"].get_active_connection()
        if not connObj:
            return msgModel.genrated_message("No active connection found!")
        scopes = ['Dataset.ReadWrite.All']
        connection = connObj._create_powerbi_connection(scopes)
        for expObj in self:
            if expObj.is_published:
                already_published.append(expObj.id)
                continue
            if expObj.workspace_id.default_workspace:
                url = f"{connObj.api_url}/datasets"
            else:
                url = f"{connObj.api_url}/groups/{expObj.workspace_id.powerbi_id}/datasets"
            tables = expObj.get_tables_data()
            if not tables:
                no_tables.append(expObj.id)
                continue
            data = {
                "name": expObj.name,
                "defaultMode": "Push",
                "tables": tables
            }
            resp = self.env["powerbi.synchronization"].callPowerbiApi(url, 'post', data, connection.get('token',''), scopes)
            if resp.get('status', False):
                value = resp.get('value')
                expObj.powerbi_id = value.get('id','')
                expObj.is_published = True
                expObj.table_ids.is_published = True
                success.append(expObj.id)
            else:
                failure.append(expObj.id)
                self.env["powerbi.sync.history"].create({
                    "status": "no",
                    "action": "b",
                    "action_on": "dataset",
                    "error_message": "Dataset export error, id "+str(expObj.id)+": Reason - "+str(resp.get("message"))
                })
        if success:
            msg+=f"{len(success)} dataset(s) successfully published."
            self.env["powerbi.sync.history"].create({
                    "status": "yes",
                    "action": "b",
                    "action_on": "dataset",
                    "error_message": "Dataset(s) "+str(success)+" successfully exported to powerbi."
                })
        if failure:
            msg+=f"{len(failure)} dataset(s) can't be published."
        if already_published:
            msg+=f"{len(already_published)} dataset(s) already published."
        if no_tables:
            msg+=f"{len(no_tables)} dataset(s) doesn't contain any table."

        return msgModel.genrated_message(msg)

    def get_tables_data(self):
        return_data = []
        for table in self.table_ids:
            table_data = {
                "name" : table.name,
                "columns" : self.get_table_columns(table)
            }
            return_data.append(table_data)
        return return_data

    def get_table_columns(self,table):
        columns = []
        for col in table.column_ids:
            if col.child_field_ids:
                for child in col.child_field_ids:
                    columns.append({
                        "name": col.name+"."+child.name,
                        "dataType": self.powerbiDatatypes[child.ttype]
                    })
            else:
                columns.append({
                    "name" : col.name,
                    "dataType" : self.powerbiDatatypes[col.field_type]
                })
        return columns
