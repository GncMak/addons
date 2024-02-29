# Copyright 2021 Sygel - Valentin Vinagre
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta, datetime

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class CrmSalespersonPlannerVisitTemplateCreate(models.TransientModel):
    _name = "crm.salesperson.planner.visit.template.create"
    _description = "crm salesperson planner visit template create"

    def _default_date_to(self):
        template = self.env["crm.salesperson.planner.visit.template"].browse(
            self.env.context.get("active_id")
        )
        date = False
        if template and template.last_visit_date:
            date = datetime.strptime(template.last_visit_date, '%Y-%m-%d') + timedelta(days=7)
        else:
            date = datetime.strptime(fields.Date.context_today(self),'%Y-%m-%d') + timedelta(days=7)
        return date

    date_to = fields.Date(
        string="Date to", default=lambda self: self._default_date_to(), required=True
    )

    def create_visits(self):
        template = self.env["crm.salesperson.planner.visit.template"].browse(
            self.env.context.get("active_id")
        )

        days = (datetime.strptime(self.date_to,'%Y-%m-%d') - datetime.strptime(fields.Date.context_today(self), '%Y-%m-%d')).days
        if days < 0:
            raise ValidationError(_("The date can't be earlier than today"))
        visit_vals = template._create_visits(days=days)
        for vals in visit_vals:
            visits = self.env["crm.salesperson.planner.visit"].create(vals)
            if visits and template.auto_validate:
                visits.action_confirm()
        return {"type": "ir.actions.act_window_close"}
