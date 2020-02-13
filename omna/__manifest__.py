# -*- coding: utf-8 -*-
{
    'name': "OMNA for Odoo",

    'summary': """Automate Multichannel Selling, OMNA API""",

    'description': """
        Manage multiple sales channel efficiently. Integrated with online marketplaces for product 
        listing, order consolidation, and inventory sync.

        Supported Integrations:
            - Shopify
            - Shopee
            - Lazada
            - Qoo10
            - MercadoLibre
            - Backmarket
            - Shipstation

        The OMNA Commerce API is simple connector API to integrate ecommerce sale channels, such us marketplaces and ecommerce platforms.

        An easy way to get orders, synchronize inventory and list product information to commerce solutions around the globe.

        It is built on top of an integration platform Cenit IO (https://cenit.io)
    """,

    'author': "OMNA Pte Ltd",
    'website': "https://www.omna.io/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management'],

    # always loaded
    'data': [
        # security
        'security/omna_security.xml',
        'security/ir.model.access.csv',

        # views
        'views/parent.xml',
        'views/config.xml',
        'views/data.xml',
        'views/integrations.xml',
        'views/integration_channels.xml',
        'views/webhooks.xml',
        'views/tasks.xml',
        'views/flows.xml',
        'views/tenants.xml',
        'views/collections.xml',
        'views/omna_templates.xml',

        # wizard
        'wizard/omna_sync_products_view.xml',
        'wizard/omna_sync_orders_view.xml',
        'wizard/omna_sync_integrations_view.xml',
        'wizard/omna_sync_workflows_view.xml',
        'wizard/omna_action_start_workflows_view.xml',
        'wizard/omna_action_status_workflows_view.xml',
        'wizard/omna_sync_tenants_view.xml',
        'wizard/omna_sync_collections_view.xml',

        # initial data
        'data/dow.xml',
        'data/wom.xml',
        'data/moy.xml'

    ],
    'qweb': [
        'static/src/xml/systray.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
    'application': True,
    'auto_install': False,
}
