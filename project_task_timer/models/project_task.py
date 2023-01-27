# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.
import datetime
import io, uuid, json, requests, logging
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from lxml import etree

_logger = logging.getLogger(__name__)
# TODO : Personelin açık timer ı varsa, başka göreve start yapamasın.
# access_account_analytic_line_user,access.account.analytic.line.user,model_account_analytic_line,project.group_project_user,1,1,1,0

class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_timer_ids = fields.One2many('task.timer', 'task_id', 'task timers')
    start_date_hide = fields.Boolean(string='hide start button', compute='_compute_hide_start_button')
    end_date_hide = fields.Boolean(string='hide end button', compute='_compute_hide_end_button')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(ProjectTask, self).fields_view_get(view_id=view_id, view_type=view_type,
    #                                                    toolbar=toolbar, submenu=False)
    #     if view_type != 'form':
    #         return res
    #     idm = self._context.get('params').get('id')
    #     task_timer = self.env['task.timer'].search(
    #         [('task_id', '=', idm), ('user_id', '=', self.env.user.id), ('end_date', '=', False)])
    #     if task_timer:
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//button[@name='action_start']"):
    #             node.set('invisible', "1")
    #             res['arch'] = etree.tostring(doc)
    #     return res
    #
    # @api.model
    # def default_get(self, fields):
    #     res = super(ProjectTask, self).default_get(fields)
    #     return res

    @api.depends('task_timer_ids')
    def _compute_hide_start_button(self):
        for task in self:
            task_timer = self.env['task.timer'].search([
                ('task_id', '=', task.id),
                ('employee_id', '=', task.env.user.employee_ids[0].id),
                ('end_date', '=', False),
                ('time_sheet_include', '=', False)
            ])
            if task_timer:
                task.start_date_hide = True
                task.end_date_hide = False

    # ('task_id', '=', task.id),
    @api.depends('task_timer_ids')
    def _compute_hide_end_button(self):
        for task in self:
            task_timer = self.env['task.timer'].search(
                [('task_id', '=', task.id),('employee_id', '=', task.env.user.employee_ids[0].id), ('end_date', '=', False), ('time_sheet_include', '=', False)])
            if not task_timer:
                task.start_date_hide = False
                task.end_date_hide = True
            if task.id != task_timer.id:
                task.end_date_hide = True

    # ('task_id', '=', task.id),
    def start_task(self):
        self.ensure_one()
        task_timer = self.env['task.timer']
        timer = task_timer.search([('task_id', '=', self.id), ('employee_id', '=', self.env.user.employee_ids[0].id), ('end_date', '=', False)])
        if not timer:
            task_timer.create({
                'task_id': self.id,
                'start_date': datetime.datetime.now(),
                'employee_id': self.env.user.employee_ids[0].id
            })

    def end_task(self):
        self.ensure_one()
        end_date = self._context.get('end_date')
        process_type = self._context.get('process_type')
        task_timer = self.env['task.timer']
        timer = task_timer.search([('task_id', '=', self.id), ('employee_id', '=', self.env.user.employee_ids[0].id), ('end_date', '=', False), ('time_sheet_include', '=', False)])

        time_stamp = float(((datetime.datetime.strptime(end_date,
                                                        '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
            timer.start_date, '%Y-%m-%d %H:%M:%S')).total_seconds()) / 60 / 60)
        timer.update({
            'end_date': end_date,
            'process_type': process_type,
            'duration': time_stamp
        })
        analytic_line = self._create_analytic_line(timer)
        if analytic_line:
            timer.update({
                'time_sheet_include': True,
                'timesheet_id': analytic_line.id
            })

    def _create_analytic_line(self, timer):
        analytic_line = self.env['account.analytic.line'].sudo()
        date = datetime.datetime.strptime(timer.end_date, '%Y-%m-%d %H:%M:%S').date()
        time_sheet = analytic_line.sudo().create({
            'name': timer.process_type.name,
            'project_id': timer.task_id.project_id.id,
            'task_id': timer.task_id.id,
            'employee_id': timer.user_id.employee_ids[0].id,
            'user_id': timer.user_id.id,
            'date': fields.Date.to_string(date),
            'unit_amount': timer.duration
        })
        return time_sheet
