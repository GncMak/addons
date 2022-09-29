# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import io, uuid, json, requests, logging
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountCheckAction(models.Model):
    _inherit = 'account.check.action'

