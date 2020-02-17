# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone, time
from odoo import models, api, exceptions


_logger = logging.getLogger(__name__)


class OmnaSyncIntegrations(models.TransientModel):
    _name = 'omna.sync_integrations_wizard'
    _inherit = 'omna.api'

    def sync_integrations(self):
        try:
            limit = 100
            offset = 0
            requester = True
            integrations = []
            while requester:
                response = self.get('integrations', {'limit': limit, 'offset': offset})
                data = response.get('data')
                integrations.extend(data)
                if len(data) < limit:
                    requester = False
                else:
                    offset += limit

            integration_obj = self.env['omna.integration']
            for integration in integrations:
                act_integration = integration_obj.search([('integration_id', '=', integration.get('id'))])
                if act_integration:
                    data = {
                        'name': integration.get('name'),
                        'channel': integration.get('channel'),
                        'authorized': integration.get('authorized')
                    }
                    act_integration.with_context(synchronizing=True).write(data)
                else:
                    data = {
                        'name': integration.get('name'),
                        'integration_id': integration.get('id'),
                        'channel': integration.get('channel'),
                        'authorized': integration.get('authorized')
                    }
                    act_integration = integration_obj.with_context(synchronizing=True).create(data)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {'menu_id': self.env.ref('omna.menu_omna_integration').id},
            }
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


