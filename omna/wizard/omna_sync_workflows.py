# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timezone
from dateutil.parser import parse
from odoo import models, api, exceptions


_logger = logging.getLogger(__name__)


class OmnaSyncWorkflows(models.TransientModel):
    _name = 'omna.sync_workflows_wizard'
    _inherit = 'omna.api'

    def sync_workflows(self):
        try:
            limit = 100
            offset = 0
            requester = True
            flows = []
            while(requester):
                response = self.get('flows', {'limit': limit, 'offset': offset})
                data = response.get('data')
                flows.extend(data)
                if len(data) < limit:
                    requester = False
                else:
                    offset += limit

            for flow in flows:
                act_flow = self.env['omna.flow'].search([('omna_id', '=', flow.get('id'))])
                if act_flow:
                    # Update flow
                    pass
                else:
                    # Create flow
                    pass
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


