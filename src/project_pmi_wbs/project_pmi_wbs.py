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

from openerp.osv import fields, osv

class project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"
    
    _columns = {
        'wbs_ids': fields.one2many('project_pmi.wbs', 'project_id', string='Work Breakdown Structure'),
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        project_id = super(project, self).create(cr, uid, vals, context)
        wbs_pool = self.pool.get('project_pmi.wbs')
        values = {
              'project_id': project_id,
              'name': vals['name'],
        }
        wbs_pool.create(cr, uid, values, context)
        return project_id

project()

class project_pmi_wbs(osv.osv):
    _name = "project_pmi.wbs"
    _inherit = ['mail.thread']
    _description = "Defines the Work Breakdown Structure and management methods"
    _columns = {
        'code': fields.char('Code', size=20, required=True, select=True),
        'name': fields.char('Name', size=255, required=True, select=True),
        'project_id': fields.many2one('project.project','Project'),
        'deliverable_ids': fields.one2many('project_pmi.deliverable', 'wbs_id', string='WBS Deliverables Structure'),
        'active':fields.boolean('Active', help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
    }
    _defaults = {
        'active': True,
        'state': 'draft',
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'project_pmi.wbs')
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        wbs_id = super(project_pmi_wbs, self).create(cr, uid, vals, context)
        deliverable_pool = self.pool.get('project_pmi.deliverable')
        values = {
              'wbs_id': wbs_id,
              'name': vals['name'],
        }
        deliverable_pool.create(cr, uid, values, context)
        return wbs_id

project_pmi_wbs()

class project_pmi_deliverable(osv.osv):
    _name = "project_pmi.deliverable"
    _inherit = ['mail.thread']
    _description = "Defines a deliverables tree that belongs to a WBS"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'code': fields.char('Code', size=20, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'name': fields.char('Name', size=255, required=True, select=True),
        'weight': fields.float('Weight'),
        'description': fields.text('Description'),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
        'wbs_id': fields.many2one('project_pmi.wbs','WBS'),
        'work_package_ids': fields.one2many('project_pmi.work_package', 'deliverable_id', string='Work Packages'),
        'parent_id': fields.many2one('project_pmi.deliverable','Parent Deliverable', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('project_pmi.deliverable', 'parent_id', string='Child Deliverables'),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list."),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
    }
    _defaults = {
        'active': True,
        'state': 'draft',
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'project_pmi.deliverable')
    }
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_id DESC'

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from project_pmi_deliverable where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive deliverable.', ['parent_id'])
    ]
    def child_get(self, cr, uid, ids):
        return [ids]

project_pmi_deliverable()

class project_pmi_work_package(osv.osv):
    _name = "project_pmi.work_package"
    _inherit = ['mail.thread']
    _description = "Defines a traceable Work Package in a WBS"
    _columns = {
        'code': fields.char('Code', size=20, required=True, select=True),
        'name': fields.char('Name', size=255, required=True, select=True),
        'weight': fields.float('Weight'),
        'description': fields.text('Description'),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
        'deliverable_id': fields.many2one('project_pmi.deliverable','Deliverable'),
    }
    _defaults = {
        'active': True,
        'state': 'draft',
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'project_pmi.work_package')
    }

project_pmi_work_package()
