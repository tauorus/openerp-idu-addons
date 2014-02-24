# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Información Centro de Costo IDU',
    'version': '1.0',
    'category': '',
    'description': """
    Este módulo permite obtener la información del centro de costo IDU desde Stone
""",
    'author': 'Instituto De Desarrollo Urbano',
    'website': 'http://www.idu.gov.co',
    'depends': [
                'contrato_idu',
    ],
    'data': [
        'stone_erp_idu_view.xml',
    ],
    'init_xml' : ['stone_erp_idu_view.xml'],
    'demo': [],
    'update_xml': [
                   'stone_erp_idu_view.xml',
               ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: