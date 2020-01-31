# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timezone, time
import dateutil.parser
import pytz
from odoo import models, api, exceptions, fields


_logger = logging.getLogger(__name__)


class OmnaSyncCollections(models.TransientModel):
    _name = 'omna.sync_collections_wizard'
    _inherit = 'omna.api'

    def sync_collections(self):
        try:
            tzinfos = {
                'PST': -8 * 3600,
                'PDT': -7 * 3600,
            }
            limit = 100
            offset = 0
            requester = True
            collections = []
            while requester:
                response = self.get('collections', {'limit': limit, 'offset': offset})
                data = response.get('data')
                collections.extend(data)
                if len(data) < limit:
                    requester = False
                else:
                    offset += limit

            collection_obj = self.env['omna.collection']
            for collection in collections:
                act_collection = collection_obj.search([('omna_id', '=', collection.get('id'))])
                if act_collection:
                    data = {
                        'name': collection.get('name'),
                        'title': collection.get('title'),
                        'shared_version': collection.get('shared_version'),
                        'summary': collection.get('channel'),
                        'state': collection.get('status'),
                        'updated_at': fields.Datetime.to_string(dateutil.parser.parse(collection.get('updated_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if collection.get('updated_at') else '',
                        'installed_at': fields.Datetime.to_string(dateutil.parser.parse(collection.get('installed_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if collection.get('installed_at') else ''
                    }
                    act_collection.sudo().with_context(synchronizing=True).write(data)
                else:
                    data = {
                        'name': collection.get('name'),
                        'title': collection.get('title'),
                        'omna_id': collection.get('id'),
                        'shared_version': collection.get('shared_version'),
                        'summary': collection.get('channel'),
                        'state': collection.get('status'),
                        'updated_at': fields.Datetime.to_string(dateutil.parser.parse(collection.get('updated_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if collection.get('updated_at') else '',
                        'installed_at': fields.Datetime.to_string(dateutil.parser.parse(collection.get('installed_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if collection.get('installed_at') else ''
                    }
                    act_collection = collection_obj.sudo().with_context(synchronizing=True).create(data)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {'menu_id': self.env.ref('omna.menu_omna_collections').id},
            }
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


