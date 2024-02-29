# Copyright 2021 Sygel - Valentin Vinagre
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmSalespersonPlannerVisit(models.Model):
    _inherit = "crm.salesperson.planner.visit"

    task_ids = fields.One2many("project.task", "visit_id", string="Tasks")
    task_count = fields.Integer(compute="_compute_task_data", string="Number of Tasks", store=True)

    @api.depends("task_ids.visit_id")
    def _compute_task_data(self):
        task_domain = [("visit_id", "in", self.ids),]
        task_data = self.env["project.task"].read_group(
            domain=task_domain, fields=["visit_id"], groupby=["visit_id"]
        )
        mapped_task_data = {m["visit_id"][0]: m["visit_id_count"] for m in task_data}
        for sel in self:
            sel.task_count = mapped_task_data.get(sel.id, 0)

    def _prepare_context_from_action(self):
        return {
            "search_default_visit_id": self.id,
            "default_visit_id": self.id,
            "search_default_partner_id": self.partner_id.commercial_partner_id.id,
            "default_partner_id": self.partner_id.commercial_partner_id.id,
            "default_company_id": self.company_id.id or self.env.company.id,
            "default_user_id": self.user_id.id,
        }

    def action_project_task_new(self):
        view_id = self.sudo().get_formview_id(access_uid=None)
        ctx = dict(visit_id=self.id, default_visit_id=self.id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'new',
            'views': [(view_id, 'form')],
            # 'context': dict(self._context),
            'context': ctx,

        }
        # visit_menu = self.env.ref('crm_salesperson_planner_task.crm_salesperson_visit_action_task_new').id
        # action = self.env["ir.actions.act_window"]._for_xml_id(
        #     "crm_salesperson_planner_task.crm_salesperson_visit_action_task_new"
        # )
        # action["context"] = self._prepare_context_from_action()
        # return action

    @api.multi
    def action_view_project_task(self):
        # action = self.env["ir.actions.act_window"]._for_xml_id(
        #     "project.action_tasks_with_onboarding"
        # )

        # ctx = self._prepare_context_from_action()
        # ctx.update(search_default_draft=1)
        # action["context"] = ctx
        tasks = self.mapped('task_ids')
        action = self.env.ref("project.project_task_action_sub_task").read()[0]
        if len(tasks) > 1:
            action["domain"] = [("id", "in", tasks.ids)]
        elif len(tasks) == 1:
            action["views"] = [(self.env.ref("project.view_task_form2").id, "form")]
            # task = self.order_ids.filtered(lambda l: l.visit_id != "Null")
            action["res_id"] = tasks.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
