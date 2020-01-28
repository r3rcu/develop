#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# config.py
#
#  Copyright 2015 D.H. Bahr <dhbahr@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from odoo.http import request
import logging
import requests
import json
import werkzeug

from odoo import models, fields, exceptions, api

_logger = logging.getLogger(__name__)


class OmnaSettings(models.TransientModel):
    _name = 'omna.settings'
    _inherit = 'res.config.settings'

    cenit_url = fields.Char('Cenit URL')


    ############################################################################
    # Default values getters
    ############################################################################
    @api.model
    def get_values(self):
        res = super(OmnaSettings, self).get_values()
        res.update(
            cenit_url=self.env["ir.config_parameter"].sudo().get_param("omna_odoo.cenit_url", default=None),
        )
        return res

    ############################################################################
    # Values setters
    ############################################################################

    def set_values(self):
        super(OmnaSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param("omna_odoo.cenit_url", record.cenit_url or '')


class OnmaSignInSettings(models.TransientModel):
    _name = "omna.signin.settings"
    _inherit = "res.config.settings"

    cenit_url = fields.Char('OMNA API URL', default='https://cenit.io/app/ecapi-v1')

    @api.model
    def get_values(self):
        res = super(OnmaSignInSettings, self).get_values()
        res.update(
            cenit_url=self.env["ir.config_parameter"].sudo().get_param("omna_odoo.cenit_url", default=None)
        )
        return res

    ############################################################################
    # Actions
    ############################################################################

    def execute(self):
        self.env.user.context_omna_sing_in_ip = request.httprequest.environ['REMOTE_ADDR']
        redirect = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/omna/sign_in/'
        self.env['ir.config_parameter'].sudo().set_param("omna_odoo.cenit_url", self.cenit_url or '')
        return {
            "type": "ir.actions.act_url",
            "url": '%s?%s' % (self.cenit_url + '/sign_in', werkzeug.urls.url_encode({'redirect_uri': redirect})),
            "target": "self",
        }
