{
    'name': 'Axx Stock Extensions',
    'summary': 'Axx Stock Characteristics',
    'description': 'Define dimensions to track the products quantities similar to lots, ',
    'category': 'Inventory',
    'version': '14.0.1.0.0',
    'author': 'axxelia GmbH',
    'website': 'http://www.axxelia.com',
    'depends': [
        # ---------------------
        # Odoo
        # ---------------------
        'stock',
        # ---------------------
        # OCA
        # ---------------------
        # ---------------------
        # EE
        # ---------------------
        # ---------------------
        # Thirdparty
        # ---------------------
        # ---------------------
        # Axxelia
        # ---------------------
        # ---------------------
        # PROJECT
        # ---------------------

    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Wizards
        'wizard/axx_stock_product_wizard_view.xml',
        'wizard/axx_stock_retrieve_wizard_view.xml',
        # Data
        'data/axx_stock_pallet_data.xml',
        # views
        'views/stock/stock_quant_views.xml',
        'views/stock/axx_stock_storage_views.xml',
        'views/stock/stock_location_views.xml',
        'views/stock/axx_stock_pallet_views.xml',
        'views/stock/axx_stock_location_log_views.xml',
        'views/stock/axx_stock_retrieval_views.xml',
        # Menus
        # Reports
        # Templates
    ],
    'installable': True,
    'application': True
}
