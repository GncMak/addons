# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.
import datetime
import io, uuid, json, requests, logging
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProjectTaskTimerActionWizard(models.TransientModel):
    _name = 'project.task.timer.action.wizard'
    _description = 'Task Timer Wizard'

    action_type = fields.Char('Action type passed on the context', required=True)
    end_date = fields.Datetime(string='End Date')
    process_type = fields.Many2one('task.timer.process.type', 'Type')
    task_timer_ids = fields.One2many('task.timer', 'task_id', 'task timers')

    def action_confirm(self):
        self.ensure_one()
        employee_id = self.env.user.employee_ids[0].id
        self.end_date = datetime.datetime.now()
        active_id = self._context.get('active_ids')
        task = self.env['project.task'].browse(active_id)
        for item in task:
            res = getattr(item.with_context(end_date=self.end_date, process_type=self.process_type, empolyee=employee_id), self.action_type)()
            return res




