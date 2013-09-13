# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
#
#    Creado por Andres Ignacio Baez Alba
#
##############################################################################

from osv import osv, fields
from lxml import etree
import xlrd
import base64
class urban_bridge_wizard_import_elements(osv.osv_memory):
    """
    Wizard to load information from excel
    """ 
    _name="urban_bridge.wizard.import_elements"
    _columns={
        'srid':fields.integer('Source SRID','Source Data System Reference'),
        'element':fields.many2one('urban_bridge.structure_element_type','Element Type'),
        'file':fields.binary('File'),
    }

    def next (self,cr,uid,ids,context=None):
        search_obj = self.pool.get('ir.ui.view')
        search_id = search_obj.search(cr,uid,[('model','=','urban_bridge.wizard.import_elements'),\
                                              ('name','=','Import Elements Page 2')])
        context["current_ids"]=ids[0]
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'urban_bridge.wizard.import_elements',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': search_id[0],
            'context': context
            }
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Trae los campos de la vista para pintarla de manera adecuada
        
        """
        result = super(urban_bridge_wizard_import_elements, self).fields_view_get(cr, uid, view_id, \
                                        view_type, context, toolbar,submenu)
        search_obj = self.pool.get('ir.ui.view')
        search_id = search_obj.search(cr,uid,[('model','=','urban_bridge.wizard.import_elements'),\
                                              ('name','=','Import Elements Page 2')])
        if (view_id == search_id[0]):
            current_id = context["current_ids"]
            wizard = self.browse(cr,uid,current_id,context=None)
            #1. Armar un diccionario que va a funcionar en los comboboxes
            workbook = xlrd.open_workbook(file_contents=base64.decodestring(wizard.file))
            worksheets = workbook.sheet_names()
            if worksheets.__len__()>1:
                raise Exception('File has more than one worksheet, please delete unused worksheets and try execute wizard again!')
            ws = workbook.sheets()[0]
            x = 0
            combo_list = []
            #Columnas que se van a mostrar
            for col in range(ws.ncols):
                value = ws.cell(0,col).value
                combo_list.append((x,value))
            #2. Determinar los campos que tienen el objeto y de acuerdo a los campos definidos en el objeto se crea una
            xml=etree.fromstring(result['arch'])
            maingroup = etree.Element("group",colspan="4",col="4")
            subgroup=etree.SubElement(maingroup,"group",colspan="4",col="2")
            etree.SubElement(subgroup, "separator", string=wizard.element.name)
            #3. El campo nombre que se encuentra en el objeto structure_element
            result['fields']["name"] = {
                        'domain':[],
                        'string':"Name",
                        'selectable':True,
                        'type':"selection",
                        'context':{},
                        'selection':combo_list,
                        'required':True,
                        }
            etree.SubElement(maingroup,"field",name="name")
            #4. El resto de atributos que se definen para el objeto. 
            for attribute in wizard.element.attributes:
                new_id = str(wizard.element.id)+"_"+str(attribute.id)
                result['fields'][new_id] = {
                        'domain':[],
                        'string':attribute.name,
                        'selectable':True,
                        'type':"selection",
                        'context':{},
                        'selection':combo_list,
                        'required':True,
                        }
                etree.SubElement(maingroup,"field",name=new_id)
            xml.insert(0,maingroup)
            result['arch'] = etree.tostring(xml)
        return result
    
    def create(self, cr, uid, vals, context=None):
        """
        This method si called when every action at wizard
        """
        if vals.has_key('srid'):
            id_val = super(urban_bridge_wizard_import_elements,self).create(cr, uid, vals, context=context)
        else:
            #Abrir 

        
        
        return id_val
    
    
    def import_elements(self,cr,uid,ids,context=None):
        """
        Import
        """
        res = {'type': 'ir.actions.act_window_close'}
        return res
    
    
    
    
urban_bridge_wizard_import_elements()

    
