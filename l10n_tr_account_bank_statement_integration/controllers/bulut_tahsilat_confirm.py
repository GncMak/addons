# -*- coding: utf-8 -*-
# Copyright 2021 Konien Ltd.Şti.

import io, uuid, json, requests, logging
from odoo import fields, models, _, api, http
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BulutTahsilat(http.Controller):

    @http.route('/bulut_tahsilat/confirm', type='http', auth="public", website=True)
    def bulut_tahsilat_confirm(self, **kw):
        raise UserError(kw)

