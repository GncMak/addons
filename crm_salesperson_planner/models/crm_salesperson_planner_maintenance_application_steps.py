# Copyright 2021 Sygel - Valentin Vinagre
# Copyright 2021 Sygel - Manuel Regidor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError


class CrmSalespersonPlannerMaintenanceApplicationSteps(models.Model):
    _name = "crm.salesperson.planner.maintenance.application.steps"
    _description = "Salesperson Planner Maintenance Application Steps"

    name = fields.Char(string="Application Step", required=True, copy=True)
    active = fields.Boolean(required=False,default=True,)
