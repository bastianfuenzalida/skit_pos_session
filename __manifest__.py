# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Close Session',
    'version': '1.0',
    'author': 'Srikesh Infotech',
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'sequence': 15,
    'summary': 'Close session in Point of Sale screen',
    'description': """
Session In POS
==================================================================
This module allows you to directly close the session, manage
the Cash control and print the session summary report from
Point of Sale.

""",
    'images': ['images/main_screenshot.png'],
    'price': 30,
    'currency': 'EUR',
    'category': 'Point of sales',
    'depends': ['point_of_sale'],
    'data': ['views/pos_session_templates.xml',
             'views/pos_session_action.xml',
             'report/report_pos_statement.xml',
             ],
    'qweb': ['static/src/xml/pos_session.xml'],

    'installable': True,
    'auto_install': False,
    'application': True,
}
