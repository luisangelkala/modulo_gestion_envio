{
    'name': 'Gestión de Envio (Logística)',
    'version': '17.0.1.0.0',
    'category': 'Logistics',
    'summary': 'Gestión de envíos Aéreos y Marítimos',
    'description': """
        Módulo para la gestión de logística de envíos internacionales.
        Reemplaza flujo de Excel con validaciones de carga y roles.
    """,
    'author': 'Gemini Code Assist',
    'depends': ['base', 'mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/container_data.xml',
        'views/menus.xml',
        'views/shipping_management_views.xml', 
        'views/container_type_views.xml',
        'report/shipping_reports.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}