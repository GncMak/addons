# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import io, uuid, json, requests, logging
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class TimeSheet(models.Model):
    _inherit = 'account.analytic.line'

    task_timer_id = fields.One2many('task.timer', 'timesheet_id', 'Task Timer')
