# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import io, uuid, json, requests, logging
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bulut_sync = fields.Boolean(string='Bulut Tahsilat Sync', default=False, copy=False, help='')


# class ReBank(models.Model):
#     _inherit = 'res.bank'
