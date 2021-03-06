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
#    Creado Por: Andres Ignacio Baez Alba
#
#
##############################################################################


from osv import osv, fields
from lxml import etree
from ast import literal_eval
from shapely.wkt import dumps, loads
from openerp.osv.osv import except_osv
from tools.translate import _
import common_fun
#from suds.client import Client

class urban_bridge_wizard_structure_elem(osv.osv_memory):
    _name="urban_bridge.wizard.structure_elem"
    _description="Fill Bridge Properties"
    _columns={
        'name':fields.char('Name',size=128),
        'elem_id':fields.many2one('urban_bridge.structure_element','Structure Element')
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        #attrib_obj = self.pool.get('urban_bridge.structure_element_attribute')
        struct_elem_obj = self.pool.get('urban_bridge.structure_element_type')
        if context is None:
            context = {}
        result = super(urban_bridge_wizard_structure_elem, self).fields_view_get(cr, uid, view_id, \
                                        view_type, context, toolbar,submenu)
        #1. Se obtiene el ID del combo box con los tipos de elementos de infraestructura
        xml = etree.fromstring(result['arch'])
        elem_id = context['element_id']
        elem_types_id=[]
        elem_types_id.append(context['element_type_id'])
        #2. Para cada elemento de infraestructura del combo, se obtienen la lista de atributos para construir un diccionario
        for elem_inf in struct_elem_obj.browse(cr,uid,elem_types_id):
            maingroup = etree.Element("group",colspan="4",col="4")
            notebook = etree.SubElement(maingroup,"notebook")
            page_string_features = etree.SubElement(notebook,"page",string="Element Features")
            page_phographic_registry = etree.Element("page",string="Photographic Registry")
            photogroup = etree.SubElement(page_phographic_registry,"group",colspan="4",col="2")
            attributes = elem_inf.attributes
            for att in attributes:
                new_id = str(elem_inf.id)+"_"+str(att.id)+"_"+str(elem_id)
                elem_string = att.name
                is_required="0"
                if (att.is_required):
                    is_required = "1"
                data_type = att.data_type
                if (data_type =='char'):
                    result['fields'][new_id] = {
                        'domain':[],
                        'string':elem_string,
                        'selectable':True,
                        'type':data_type,
                        'context':{},
                        'size':256,
                        'required':is_required,
                        }
                    etree.SubElement(page_string_features,"field",required=is_required,name=new_id)
                elif (data_type == 'selection'):
                    result['fields'][new_id] = {
                        'domain':[],
                        'string':elem_string,
                        'selectable':True,
                        'type':data_type,
                        'context':{},
                        'selection':literal_eval(att.selection_text),
                        'required':is_required,
                        }
                    etree.SubElement(page_string_features,"field",required=is_required,name=new_id)
                elif (data_type=='binary'):
                    result['fields'][new_id] = {
                        'domain':[],
                        'string':elem_string,
                        'selectable':True,
                        'type':data_type,
                        'context':{},
                        'required':is_required,
                        }
                    #Agrega field al photogroup
                    etree.SubElement(photogroup,"field",required=is_required,name=new_id,widget="image",img_width="840",img_height="600",width="840",height="600")
                elif ((data_type=='geo_point') or (data_type=='geo_line') or (data_type=='geo_polygon')):
                    result['fields'][new_id] = {
                        'domain':[],
                        'string':elem_string,
                        'selectable':True,
                        'type':"text",
                        'context':{},
                        'required':is_required,
                        }
                    etree.SubElement(page_string_features,"field",required=is_required,name=new_id)
                else:
                    result['fields'][new_id] = {
                        'domain':[],
                        'string':elem_string,
                        'selectable':True,
                        'type':data_type,
                        'string':elem_string,
                        'context':{},
                        'required':is_required,
                        'readonly':True,
                        }
                    etree.SubElement(page_string_features,"field",name=new_id)
            #Si no hay campo tipo foto no se pone el tab 
            if (len(photogroup) > 0):
                notebook.insert(2,page_phographic_registry)
            xml.insert(1,etree.Element("separator",colspan="4",string=elem_inf.name))
            xml.insert(2,maingroup)
        result['arch'] = etree.tostring(xml)
        return result

    def default_get(self,cr, uid, fields, context=None):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        
        res = super(urban_bridge_wizard_structure_elem, self).default_get(cr, uid, fields, context=context)
        #1. Se determina si el campo field viene dentro del contexto, si no esta se trata de una solicitud de imagen
        #si el campo [active_id] viene dentro del contexto el programa necesita refrescar los campos alfanuméricos de la vista 
        active_id = False
        for k in context:
            if k == 'active_id':
                active_id = context[k]
        
        if active_id == False:#Se trata de una solicitud de imagen
            value_obj = self.pool.get('urban_bridge.structure_element_value')
            for field in fields:
                #Descomponer los elementos del field de la vista que entra en el metodo en donde esta almacenada la imagen, para luego devolverla a la plataforma
                field_list=field.split("_")
                attr_id=field_list[1]
                elem_id=field_list[2]
                #3. Lastimosamente toca mandar el query ya que los parametros que se intentan enviar se convierten en False False, ya que lo que el OpenErp hace es comparación de
                #nombres de manera subyacente y eso en esta logica del EAV no funciona.
                query = "select id from urban_bridge_structure_element_value \
                        where element_id = %s and element_attribute_id = %s"
                cr.execute(query,(elem_id,attr_id))
                
                #list_ids = value_obj.search(cr,uid,[("element_id","=",elem_id),("element_attribute_id","=",attr_id)])
                for row in cr.fetchall():#Actualizacion de la imagen el el field que entra
                    value = value_obj.browse(cr,uid,row[0])
                    image =  value.value_binary
                    res.update({field:image})
            return res
        str_element_obj = self.pool.get('urban_bridge.structure_element')
        #str_element_value = self.pool.get('urban_bridge_structure_element_value')         
        str_element = str_element_obj.browse(cr, uid,active_id, context=context);
        #1. Update elem_id que aparece en el wizard
        res.update({'elem_id': str_element.id})
        for value in str_element.values:
            #Llenar el valor de cada campo con lo que venga en los datos
            elem_type = str_element.element_type_id
            attribute = value.element_attribute_id
            field_id = str(elem_type.id)+"_"+str(attribute.id)+"_"+str(active_id)
            #Se debe verificar la definicion de tipo de dato para evitar inconsistencias o errores            
            data_type = attribute.data_type
            if (data_type=='integer'):
                res.update({field_id:value.value_integer})
            elif (data_type=='text'):
                res.update({field_id:value.value_text})
            elif (data_type=='datetime'):
                res.update({field_id:value.value_datetime})
            elif (data_type=='float'):
                res.update({field_id:value.value_float})
            elif (data_type=='boolean'):
                res.update({field_id:value.value_bool})
            elif(data_type=='char'):
                res.update({field_id:value.value_char})
            elif(data_type=='date'):
                res.update({field_id:value.value_date})
            elif(data_type=='selection'):
                res.update({field_id:value.value_selection})
            elif(data_type=='binary'):
                res.update({field_id:value.value_binary})
            elif(data_type=='geo_point'):
                geom = self.__transform_from_web_mercator_to_source_coordinates(cr,uid,value.value_point,context)
                if (geom is not None):
                    res.update({field_id:geom})
            elif(data_type=='geo_line'):
                geom = self.__transform_from_web_mercator_to_source_coordinates(cr, uid,value.value_line, context)
                if (geom is not None):
                    res.update({field_id:geom})
            elif(data_type=='geo_polygon'):
                geom = self.__transform_from_web_mercator_to_source_coordinates(cr, uid,value.value_polygon,context)
                if (geom is not None):
                    res.update({field_id:geom})
        return res


    def __transform_from_web_mercator_to_source_coordinates(self,cr,uid,input_geometry,context):
        try:
            spatial_ref_sys = self.pool.get('ir.config_parameter').get_param(cr, uid, 'urban_bridge.local_spatial_reference', default='', context=context)
            #Llamada al codigo que hace la conversion con la base de datos
            if  (input_geometry is not False):
                return common_fun.transform_from_web_mercator_to_source_coordinates(cr, input_geometry.wkt, spatial_ref_sys)
        except Exception as e:
            raise except_osv(_('Error'), str("something is wrong : "+str(e.value)))
                
    def __transform_source_geometry_to_web_mercator(self,cr,uid,input_wkt,context):
        try:
            spatial_ref_sys = self.pool.get('ir.config_parameter').get_param(cr, uid, 'urban_bridge.local_spatial_reference', default='', context=context)
            return common_fun.transform_source_geometry_to_web_mercator(cr, input_wkt, spatial_ref_sys)
        except Exception as e:
            raise e


    def elem_create (self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}


    def create(self, cr, uid, vals, context=None):
        """
        Create the wizard and set the values for structure element in EAV model 
        """
        try:
            if context is None: context = {}
            #1. Se obtiene el valor de elem_id
            elem_id = context['element_id'] 
            context['elem_type_vals']=vals
            
            #2. Se crea el registro de que se hizo un inventario
            urban_bridge_wizard_structure_elem_id = super(urban_bridge_wizard_structure_elem,self).create(cr, uid, {'elem_id': elem_id}, context=context)
            #3. Se ejemplifica el objeto structure_elem que se invocó y se miran los valores que tiene con el fin de asignarles un valor que se va 
            #a actualizar.
            structure_elem_obj=self.pool.get('urban_bridge.structure_element')
            structure_elem_value_obj=self.pool.get('urban_bridge.structure_element_value')
            structure_elem_attribute_obj=self.pool.get('urban_bridge.structure_element_attribute')
            structure_elem = structure_elem_obj.browse(cr,uid,elem_id)
            #Se itera sobre los elementos recibidos
            #Si no existen se crean
            for value_form in vals:
                #Values aren't name or structure_elem
                if not (str(value_form).startswith("n") or str(value_form).startswith("e")):
                    s = value_form.split('_')
                    struct_elem_attribute_id = int(s[1])
                    attribute = structure_elem_attribute_obj.browse(cr,uid,struct_elem_attribute_id)
                    data_type = attribute.data_type
                    #4. Se arma el diccionario que se va a pasar al metodo
                    str_elem_val_vals={}
                    str_elem_val_vals['element_attribute_id']=struct_elem_attribute_id
                    str_elem_val_vals['element_id']=elem_id
                    if (data_type=='integer'):
                        str_elem_val_vals['value_integer']=vals[value_form]
                    elif (data_type=='text'):
                        str_elem_val_vals['value_text']=vals[value_form]
                    elif (data_type=='datetime'):
                        str_elem_val_vals['value_datetime']=vals[value_form]
                    elif (data_type=='float'):
                        str_elem_val_vals['value_float']=vals[value_form]
                    elif (data_type=='boolean'):
                        str_elem_val_vals['value_bool']=vals[value_form]
                    elif(data_type=='char'):
                        str_elem_val_vals['value_char']=vals[value_form]
                    elif(data_type=='date'):
                        str_elem_val_vals['value_date']=vals[value_form]
                    elif(data_type=='selection'):
                        str_elem_val_vals['value_selection']=vals[value_form]
                    elif(data_type=='binary'):
                        str_elem_val_vals['value_binary']=vals[value_form]
                    elif(data_type=='geo_line'):
                        shape_line = self.__transform_source_geometry_to_web_mercator(cr, uid,vals[value_form], context)
                        str_elem_val_vals['value_line']=shape_line
                    elif(data_type=='geo_point'):
                        shape_point = self.__transform_source_geometry_to_web_mercator(cr, uid,vals[value_form], context)
                        str_elem_val_vals['value_point']= shape_point
                    elif(data_type=='geo_polygon'):
                        shape_polygon = self.__transform_source_geometry_to_web_mercator(cr, uid,vals[value_form], context)
                        str_elem_val_vals['value_polygon']= shape_polygon
                    isnew=True
                    id_value=0 
                    for struc_elem_value in structure_elem.values:
                        if (int(struc_elem_value.element_attribute_id) == struct_elem_attribute_id):
                            id_value=struc_elem_value.id
                            isnew=False
                    if (not isnew):
                        #Write
                        structure_elem_value_obj.write(cr,uid,id_value,str_elem_val_vals)
                    else:
                        #Create
                        structure_elem_value_obj.create(cr,uid,str_elem_val_vals)
            return urban_bridge_wizard_structure_elem_id
        except Exception as e:
            raise except_osv(_('Error'), str("something is wrong : "+str(e)))
            

urban_bridge_wizard_structure_elem()
