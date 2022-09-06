# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import io, uuid, json, requests, logging
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.template'

    bulut_tahsilat_expense_code = fields.Char('Bulut Tahsilat Expense Code', help='', copy=False)
