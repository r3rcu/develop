# -*- coding: utf-8 -*-

import odoo
import datetime
from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import dateutil.parser
import pytz


def omna_id2real_id(omna_id):
    if omna_id and isinstance(omna_id, str) and len(omna_id.split('-')) == 2:
        res = [bit for bit in omna_id.split('-') if bit]
        return res[1]
    return omna_id


class OmnaIntegration(models.Model):
    _name = 'omna.integration'
    _inherit = 'omna.api'

    @api.model
    def _get_integrations_channel_selection(self):
        try:
            response = self.get('integrations/channels', {})
            selection = []
            for channel in response.get('data'):
                selection.append((channel.get('name'), channel.get('title')))
            return selection
        except Exception as e:
            return []

    @api.model
    def _current_tenant(self):
        # current_tenant = self.env['omna.tenant'].search([('current', '=', True)], limit=1)
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)], limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    name = fields.Char('Name', required=True)
    channel = fields.Selection(selection=_get_integrations_channel_selection, string='Channel', required=True)
    integration_id = fields.Char(string='Integration ID', required=True, index=True)

    @api.model
    def create(self, vals_list):
        if not self._context.get('synchronizing'):
            self.check_access_rights('create')
            data = {
                'name': vals_list['name'],
                'channel': vals_list['channel']
            }
            response = self.post('integrations', {'data': data})
            if response.get('data').get('id'):
                vals_list['integration_id'] = response.get('data').get('id')
                return super(OmnaIntegration, self).create(vals_list)
            else:
                raise exceptions.AccessError("Error trying to push integration to Omna's API.")
        else:
            return super(OmnaIntegration, self).create(vals_list)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            response = rec.delete('integrations/%s' % rec.integration_id)
        return super(OmnaIntegration, self).unlink()


class OmnaWebhook(models.Model):
    _name = 'omna.webhook'
    _inherit = 'omna.api'
    _rec_name = 'topic'

    @api.model
    def _get_webhook_topic_selection(self):
        try:
            response = self.get('webhooks/topics', {})
            selection = []
            for topic in response.get('data'):
                selection.append((topic.get('topic'), topic.get('title')))
            return selection
        except Exception as e:
            return []

    @api.model
    def _current_tenant(self):
        # current_tenant = self.env['omna.tenant'].search([('current', '=', True)], limit=1)
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)], limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    omna_webhook_id = fields.Char("Webhooks identifier in OMNA", index=True)
    topic = fields.Selection(selection=_get_webhook_topic_selection, string='Topic', required=True)
    address = fields.Char('Address', required=True)
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True)

    @api.model
    def create(self, vals_list):
        if not self._context.get('synchronizing'):
            integration = self.env['omna.integration'].search([('id', '=', vals_list['integration_id'])], limit=1)
            data = {
                'integration_id': integration.integration_id,
                'topic': vals_list['topic'],
                'address': vals_list['address'],
            }
            response = self.post('webhooks', {'data': data})
            if response.get('data').get('id'):
                vals_list['omna_webhook_id'] = response.get('data').get('id')
                return super(OmnaWebhook, self).create(vals_list)
            else:
                raise exceptions.AccessError("Error trying to push webhook to Omna's API.")
        else:
            return super(OmnaWebhook, self).create(vals_list)

    def write(self, vals):
        self.ensure_one()
        if not self._context.get('synchronizing'):
            if 'integration_id' in vals:
                integration = self.env['omna.integration'].search([('id', '=', vals['integration_id'])], limit=1)
            else:
                integration = self.env['omna.integration'].search([('id', '=', self.integration_id.id)], limit=1)
                data = {
                    'address': vals['address'] if 'address' in vals else self.address,
                    'integration_id': integration.integration_id,
                    'topic': vals['topic'] if 'topic' in vals else self.topic
                }
            response = self.post('webhooks/%s' % self.omna_webhook_id, {'data': data})
            if response.get('data').get('id'):
                vals['omna_webhook_id'] = response.get('data').get('id')
                return super(OmnaWebhook, self).write(vals)
            else:
                raise exceptions.AccessError("Error trying to update webhook in Omna's API.")
        else:
            return super(OmnaWebhook, self).write(vals)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            response = rec.delete('webhooks/%s' % rec.omna_webhook_id)
        return super(OmnaWebhook, self).unlink()


class OmnaFlow(models.Model):
    _name = 'omna.flow'
    _inherit = 'omna.api'
    _rec_name = 'type'

    @api.model
    def _get_flow_types(self):
        try:
            response = self.get('flows/types', {})
            selection = []
            for type in response.get('data'):
                selection.append((type.get('type'), type.get('title')))
            return selection
        except Exception as e:
            return []

    @api.model
    def _current_tenant(self):
        # current_tenant = self.env['omna.tenant'].search([('current', '=', True)], limit=1)
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)], limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True)
    type = fields.Selection(selection=_get_flow_types, string='Type', required=True)
    start_date = fields.Datetime("Start Date", help='Select date and time')
    end_date = fields.Date("End Date")
    days_of_week = fields.Many2many('omna.filters', 'omna_flow_days_of_week_rel', 'flow_id', 'days_of_week_id', domain=[('type', '=', 'dow')])
    weeks_of_month = fields.Many2many('omna.filters', 'omna_flow_weeks_of_month_rel', 'flow_id', 'weeks_of_month_id', domain=[('type', '=', 'wom')])
    months_of_year = fields.Many2many('omna.filters', 'omna_flow_months_of_year_rel', 'flow_id', 'months_of_year_id', domain=[('type', '=', 'moy')])
    omna_id = fields.Char('OMNA Workflow ID', index=True)
    active = fields.Boolean('Active', default=True, readonly=True)

    @api.model
    def create(self, vals):
        integration = self.env['omna.integration'].search([('id', '=', vals.get('integration_id'))], limit=1)
        data = {
            "integration_id": integration.integration_id,
            "type": vals.get('type'),
            "scheduler": {}
        }

        if 'start_date' in vals:
            start_date = datetime.datetime.strptime(vals.get('start_date'), "%Y-%m-%d %H:%M:%S")
            data['scheduler']['start_date'] = start_date.date().strftime("%Y-%m-%d")
            data['scheduler']['time'] = start_date.time().strftime("%H:%M")
        if 'end_date' in vals:
            end_date = datetime.datetime.strptime(vals.get('end_date'), "%Y-%m-%d")
            data['scheduler']['end_date'] = end_date.strftime("%Y-%m-%d")
        if 'days_of_week' in vals:
            dow = []
            days = self.env['omna.filters'].search([('type', '=', 'dow'), ('id', 'in', vals.get('days_of_week')[0][2])])
            for day in days:
                dow.append(day.name)
            data['scheduler']['days_of_week'] = dow
        if 'weeks_of_month' in vals:
            wom = []
            weeks = self.env['omna.filters'].search([('type', '=', 'wom'), ('id', 'in', vals.get('weeks_of_month')[0][2])])
            for week in weeks:
                wom.append(week.name)
            data['scheduler']['weeks_of_month'] = wom
        if 'months_of_year' in vals:
            moy = []
            months = self.env['omna.filters'].search([('type', '=', 'moy'), ('id', 'in', vals.get('months_of_year')[0][2])])
            for month in months:
                moy.append(month.name)
            data['scheduler']['months_of_year'] = moy

        response = self.post('flows', {'data': data})
        if 'id' in response.get('data'):
            vals['omna_id'] = response.get('data').get('id')
            return super(OmnaFlow, self).create(vals)
        else:
            raise exceptions.AccessError("Error trying to push the workflow to Omna.")

    def write(self, vals):
        self.ensure_one()
        if 'type' in vals:
            raise UserError("You cannot change the type of a worflow. Instead you should delete the current workflow and create a new one of the proper type.")
        if 'integration_id' in vals:
            raise UserError("You cannot change the integration of a worflow. Instead you should delete the current workflow and create a new one of the proper type.")

        data = {
            "scheduler": {}
        }

        if 'start_date' in vals:
            start_date = datetime.datetime.strptime(vals.get('start_date'), "%Y-%m-%d %H:%M:%S")
            data['scheduler']['start_date'] = start_date.date().strftime("%Y-%m-%d")
            data['scheduler']['time'] = start_date.time().strftime("%H:%M")
        if 'end_date' in vals:
            end_date = datetime.datetime.strptime(vals.get('end_date'), "%Y-%m-%d")
            data['scheduler']['end_date'] = end_date.strftime("%Y-%m-%d")
        if 'days_of_week' in vals:
            dow = []
            days = self.env['omna.filters'].search([('type', '=', 'dow'), ('id', 'in', vals.get('days_of_week')[0][2])])
            for day in days:
                dow.append(day.name)
            data['scheduler']['days_of_week'] = dow
        if 'weeks_of_month' in vals:
            wom = []
            weeks = self.env['omna.filters'].search([('type', '=', 'wom'), ('id', 'in', vals.get('weeks_of_month')[0][2])])
            for week in weeks:
                wom.append(week.name)
            data['scheduler']['weeks_of_month'] = wom
        if 'months_of_year' in vals:
            moy = []
            months = self.env['omna.filters'].search([('type', '=', 'moy'), ('id', 'in', vals.get('months_of_year')[0][2])])
            for month in months:
                moy.append(month.name)
            data['scheduler']['months_of_year'] = moy

        response = self.post('flows/%s' % self.omna_id, {'data': data})
        if 'id' in response.get('data'):
            return super(OmnaFlow, self).write(vals)
        else:
            raise exceptions.AccessError("Error trying to update the workflow in Omna.")

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for flow in self:
            flow.delete('flows/%s' % flow.omna_id)
        return super(OmnaFlow, self).unlink()


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'omna.api']

    @api.model
    def _current_tenant(self):
        # current_tenant = self.env['omna.tenant'].search([('current', '=', True)], limit=1)
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)], limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)

    omna_product_id = fields.Char("Product identifier in OMNA", index=True)
    integration_ids = fields.Many2many('omna.integration', 'omna_product_template_integration_rel', 'product_id',
                                       'integration_id', 'Integrations')
    no_create_variants = fields.Boolean('Do not create variants automatically', default=True)

    def _create_variant_ids(self):
        if not self.no_create_variants:
            return super(ProductTemplate, self)._create_variant_ids()
        return True

    @api.model
    def create(self, vals_list):
        if not self._context.get('synchronizing'):
            data = {
                'name': vals_list['name'],
                'price': vals_list['list_price'],
                'description': vals_list['description']
            }
            response = self.post('products', {'data': data})
            if response.get('data').get('id'):
                vals_list['omna_product_id'] = response.get('data').get('id')
                return super(ProductTemplate, self).create(vals_list)
            else:
                raise exceptions.AccessError("Error trying to push product to Omna's API.")
        else:
            return super(ProductTemplate, self).create(vals_list)

    def write(self, vals):
        self.ensure_one()
        if not self._context.get('synchronizing'):
            if 'name' in vals or 'list_price' in vals or 'description' in vals:
                data = {
                    'name': vals['name'] if 'name' in vals else self.name,
                    'price': vals['list_price'] if 'list_price' in vals else self.list_price,
                    'description': vals['description'] if 'description' in vals else (self.description or '')
                }
                response = self.post('products/%s' % self.omna_product_id, {'data': data})
                if response.get('data').get('id'):
                    vals['omna_product_id'] = response.get('data').get('id')
                    return super(ProductTemplate, self).write(vals)
                else:
                    raise exceptions.AccessError("Error trying to update product in Omna's API.")
            else:
                return super(ProductTemplate, self).write(vals)
        else:
            return super(ProductTemplate, self).write(vals)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            integrations = [integration.integration_id for integration in rec.integration_ids]
            data = {
                "integration_ids": integrations,
                "delete_from_integration": True,
                "delete_from_omna": True
            }
            response = rec.delete('products/%s' % rec.omna_product_id, {'data': data})
        return super(ProductTemplate, self).unlink()


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'omna.api']
    omna_variant_id = fields.Char("Product Variant identifier in OMNA", index=True)
    variant_integration_ids = fields.Many2many('omna.integration', 'omna_product_integration_rel', 'product_id',
                                               'integration_id', 'Integrations')

    # @api.model
    # def create(self, vals_list):
    #     if not self._context.get('synchronizing'):
    #         data = {
    #             'name': vals_list['name'],
    #             'description': vals_list['description'],
    #             'price': vals_list['lst_price'],
    #             'sku': vals_list['default_code'],
    #             'cost_price': vals_list['standard_price']
    #         }
    #         response = self.post('products/5dfc50ae25d98531cc0a9268/variants', {'data': data})
    #         if response.get('data').get('id'):
    #             vals_list['product_tmpl_id'] = self.env['product.template'].search([('omna_product_id', '=', '5dfc50ae25d98531cc0a9268')])
    #             vals_list['omna_variant_id'] = response.get('data').get('id')
    #             return super(ProductTemplate, self).create(vals_list)
    #         else:
    #             raise exceptions.AccessError("Error trying to push product to Omna's API.")
    #     else:
    #         return super(ProductTemplate, self).create(vals_list)

    def write(self, vals):
        self.ensure_one()
        if not self._context.get('synchronizing'):
            if len(set(['name', 'price', 'description', 'sku', 'cost_price']).intersection(vals)):
                data = {
                    'name': vals['name'] if 'name' in vals else self.name,
                    'description': vals['description'] if 'description' in vals else self.description,
                    'price': vals['lst_price'] if 'lst_price' in vals else self.lst_price,
                    'sku': vals['default_code'] if 'default_code' in vals else self.default_code,
                    'cost_price': vals['standard_price'] if 'standard_price' in vals else self.standard_price
                }
                response = self.post('products/%s/variants/%s' % (self.omna_product_id, self.omna_variant_id),
                                     {'data': data})
                if response.get('data').get('id'):
                    vals['omna_variant_id'] = response.get('data').get('id')
                    return super(ProductProduct, self).write(vals)
                else:
                    raise exceptions.AccessError("Error trying to update product variant in Omna's API.")
            else:
                return super(ProductProduct, self).write(vals)
        else:
            return super(ProductProduct, self).write(vals)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            integrations = [integration.integration_id for integration in rec.integration_ids]
            data = {
                "integration_ids": integrations,
                "delete_from_integration": True,
                "delete_from_omna": True
            }
            response = rec.delete('products/%s/variants/%s' % (rec.omna_product_id, rec.omna_variant_id), {'data': data})
        return super(ProductProduct, self).unlink()


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'omna.api']

    @api.model
    def _current_tenant(self):
        # current_tenant = self.env['omna.tenant'].search([('current', '=', True)], limit=1)
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)], limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    omna_id = fields.Char("OMNA Order ID", index=True)
    integration_id = fields.Many2one('omna.integration', 'OMNA Integration')

    # @api.multi
    def action_cancel(self):
        orders = self.filtered(lambda order: not order.origin == 'OMNA')
        if orders:
            orders.write({'state': 'cancel'})

        for order in self.filtered(lambda order: order.origin == 'OMNA'):
            response = self.delete('orders/%s' % order.omna_id)
            if response:
                order.write({'state': 'cancel'})

        return True


class OmnaOrderLine(models.Model):
    _inherit = 'sale.order.line'

    omna_id = fields.Char("OMNA OrderLine ID", index=True)


class OmnaFilters(models.Model):
    _name = 'omna.filters'
    _rec_name = 'title'

    name = fields.Char("Name")
    title = fields.Char("Title")
    type = fields.Char("Type")


class OmnaTask(models.Model):
    _name = 'omna.task'
    _inherit = 'omna.api'
    _rec_name = 'description'

    status = fields.Selection(
        [('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('retrying', 'Retrying')], 'Status',
        required=True)
    description = fields.Text('Description', required=True)
    progress = fields.Float('Progress', required=True)
    task_created_at = fields.Datetime('Created At')
    task_updated_at = fields.Datetime('Updated At')
    task_execution_ids = fields.One2many('omna.task.execution', 'task_id', 'Executions')
    task_notification_ids = fields.One2many('omna.task.notification', 'task_id', 'Notifications')

    # @api.multi
    def read(self, fields_read=None, load='_classic_read'):
        result = []
        tzinfos = {
            'PST': -8 * 3600,
            'PDT': -7 * 3600,
        }
        for task_id in self.ids:
            task = self.get('tasks/%s' % omna_id2real_id(task_id), {})
            data = task.get('data')
            res = {
                'id': task_id,
                'status': data.get('status'),
                'description': data.get('description'),
                'progress': float(data.get('progress')),
                'task_created_at': fields.Datetime.to_string(
                    dateutil.parser.parse(data.get('created_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if data.get('created_at') else '',
                'task_updated_at': fields.Datetime.to_string(
                    dateutil.parser.parse(data.get('updated_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if data.get('updated_at') else '',
                'task_execution_ids': [],
                'task_notification_ids': []
            }
            for execution in data.get('executions', []):
                res['task_execution_ids'].append((0, 0, {
                    'status': execution.get('status'),
                    'exec_started_at': fields.Datetime.to_string(
                        dateutil.parser.parse(execution.get('started_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if execution.get('started_at') else '',
                    'exec_completed_at': fields.Datetime.to_string(
                        dateutil.parser.parse(execution.get('completed_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if execution.get('completed_at') else '',
                }))
            for notification in data.get('notifications', []):
                res['task_notification_ids'].append((0, 0, {
                    'status': notification.get('status'),
                    'message': notification.get('message')
                }))
            result.append(res)

        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        params = {}
        for term in args:
            if term[0] == 'description':
                params['term'] = term[2]
            if term[0] == 'status':
                params['status'] = term[2]

        if count:
            tasks = self.get('tasks', params)
            return int(tasks.get('pagination').get('total'))
        else:
            params['limit'] = limit
            params['offset'] = offset
            tasks = self.get('tasks', params)
            task_ids = self.browse([task.get('id') for task in tasks.get('data')])
            return task_ids.ids

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        self.check_access_rights('read')
        fields = self.check_field_access_rights('read', fields)
        result = []
        tzinfos = {
            'PST': -8 * 3600,
            'PDT': -7 * 3600,
        }
        params = {
            'limit': limit,
            'offset': offset,
            # 'with_details': 1
        }
        for term in domain:
            if term[0] == 'description':
                params['term'] = term[2]
            if term[0] == 'status':
                params['status'] = term[2]

        tasks = self.get('tasks', params)
        for task in tasks.get('data'):
            res = {
                'id': '1-' + task.get('id'),  # amazing hack needed to open records with virtual ids
                'status': task.get('status'),
                'description': task.get('description'),
                'progress': float(task.get('progress')),
                'task_created_at': odoo.fields.Datetime.to_string(
                    dateutil.parser.parse(task.get('created_at'), tzinfos=tzinfos).astimezone(pytz.utc)),
                'task_updated_at': odoo.fields.Datetime.to_string(
                    dateutil.parser.parse(task.get('updated_at'), tzinfos=tzinfos).astimezone(pytz.utc)),
            }
            result.append(res)

        return result

    def retry(self):
        self.ensure_one()
        response = self.get('/tasks/%s/retry' % omna_id2real_id(self.id))
        return True

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            response = rec.delete('tasks/%s' % omna_id2real_id(rec.id))
        return True


class OmnaTaskExecution(models.Model):
    _name = 'omna.task.execution'

    status = fields.Selection(
        [('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], 'Status',
        required=True)
    exec_started_at = fields.Datetime('Started At')
    exec_completed_at = fields.Datetime('Completed At')
    task_id = fields.Many2one('omna.task', string='Task')


class OmnaTaskNotification(models.Model):
    _name = 'omna.task.notification'

    type = fields.Selection(
        [('info', 'Info'), ('error', 'Error'), ('warning', 'Warning')], 'Type', required=True)
    message = fields.Char('Message')
    task_id = fields.Many2one('omna.task', string='Task')


class OmnaTenant(models.Model):
    _name = 'omna.tenant'
    _inherit = 'omna.api'

    name = fields.Char('Name', required=True)
    omna_tenant_id = fields.Char('Tenant identifier in OMNA', index=True, readonly=True)
    token = fields.Char('Token', required=True, readonly=True)
    secret = fields.Char('Secret', required=True, readonly=True)
    is_ready_to_omna = fields.Boolean('Is ready to OMNA', readonly=True)
    deactivation = fields.Datetime('Deactivation', readonly=True)

    def _compute_current(self):
        for record in self:
            record.current = self.env.user.context_omna_current_tenant.id == record.id

    current = fields.Boolean('Current Tenant', default=False, invisible=True, compute=_compute_current)

    @api.model
    def create(self, vals_list):
        if not self._context.get('synchronizing'):
            data = {
                'name': vals_list['name']
            }
            response = self.post('tenants', {'data': data})
            tzinfos = {
                'PST': -8 * 3600,
                'PDT': -7 * 3600,
            }
            if response.get('data').get('id'):
                vals_list['omna_tenant_id'] = response.get('data').get('id')
                vals_list['token'] = response.get('data').get('token')
                vals_list['secret'] = response.get('data').get('secret')
                vals_list['is_ready_to_omna'] = response.get('data').get('is_ready_to_omna')
                vals_list['deactivation'] = odoo.fields.Datetime.to_string(
                            dateutil.parser.parse(response.get('data').get('deactivation'), tzinfos=tzinfos).astimezone(pytz.utc))
                return super(OmnaTenant, self).create(vals_list)
            else:
                raise exceptions.AccessError("Error trying to push tenant to Omna's API.")
        else:
            return super(OmnaTenant, self).create(vals_list)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            response = rec.delete('tenants/%s' % rec.omna_tenant_id)
        return super(OmnaTenant, self).unlink()

    @api.model
    def _switch(self):
        self.ensure_one()
        # current = self.env['omna.tenant'].search([('current', '=', True)])
        # if current:
        #     current.write({'current': False})
        # self.write({'current': True})
        self.env.user.context_omna_current_tenant = self.id
        return True

    def switch(self):
        self._switch()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }

    @api.model
    def switch_action(self, id):
        tenant = self.browse(id)
        if tenant:
            return tenant._switch()
        else:
            return False

