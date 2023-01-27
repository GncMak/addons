# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import io, uuid, json, requests, logging
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree

_logger = logging.getLogger(__name__)


class TaskProcessTypes(models.Model):
    _name = 'task.timer.process.type'
    _description = 'Task Timer Process Type'

    name = fields.Char(string='Name')


class TaskTimer(models.Model):
    _name = 'task.timer'
    _description = 'Task Timer'

    task_id = fields.Many2one('project.task', 'task')
    user_id = fields.Many2one('res.users', 'user', default=lambda self: self.env.uid)
    employee_id = fields.Many2one('hr.employee', "Employee")
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    duration = fields.Float(string='Duration')
    process_type = fields.Many2one('task.timer.process.type', string='Type')
    time_sheet_include = fields.Boolean(string='Time Sheet Include', default=False)
    timesheet_id = fields.Many2one('account.analytic.line', 'TimeSheet')

    def unlink(self):
        for timer in self:
            timer.timesheet_id.unlink()
        return super(TaskTimer, self).unlink()