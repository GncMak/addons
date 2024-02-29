# Copyright 2021 Sygel - Valentin Vinagre
# Copyright 2021 Sygel - Manuel Regidor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError


class CrmSalespersonPlannerCheckupApplicationFormLine(models.Model):
    _name = "crm.salesperson.planner.checkup.application.form.line"
    _description = "Salesperson Planner Checkup Application Form Line"
    _order = "sequence"

    sequence = fields.Integer(string="Sequence",default=1,)
    maintenance_application_steps_id = fields.Many2one(comodel_name="crm.salesperson.planner.maintenance.application.steps", string="Maintenance Application Steps", required=True)
    measured = fields.Float(string='Measured')
    corrected = fields.Float(string='Corrected')
    notes = fields.Char(string="Notes")
    company_id = fields.Many2one(comodel_name="res.company",string="Company",default=lambda self: self.company_id,)
    visit_id = fields.Many2one(comodel_name="crm.salesperson.planner.visit",string="Crm Salesperson Planner Visit",)
