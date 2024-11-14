# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json

class PartnerSync (http.Controller):
     data=[]
     #------------- Metodo para Confirgurar Respuesta --------
     def build_response(self,table):
         response=json.dumps(table, ensure_ascii=False).encode('utf8')
         return Response(response, content_type='application/json;charset=utf-8',status=200)

     #------------ Metodo para Crear el Object ----------------
     def createRecord(self, rec):
         self.data.append({
             'id': rec.id,
             'cc': rec.ref,
             'vat': rec.vat,
             'name': rec.display_name,
             'street': rec.street if rec.street else 'N/A',
             'phone': rec.phone if rec.phone else 'N/A',
             'mobile': rec.mobile if rec.mobile else 'N/A',
             'city': rec.city if rec.city else 'N/A',
             'country': rec.state_id.name if rec.state_id else 'N/A',
             'email': rec.email if rec.email else 'N/A',
             'payment_term_id': rec.property_payment_term_id.id if rec.property_payment_term_id else None,
             'due_amount': rec.customer_due_amount,
             'active': 1 if rec.active else 0,
             'price_list_id': rec.property_product_pricelist.id
         })
     #------------ Metodo para Listar Arreglo de la Query -----
     def loadList(self,list):
         self.data = []
         for l in list:
             self.createRecord(l)

     #---------- Query para Sincronizar Datos -----------------
     @http.route('/ct.api/partner/sync/<userId>', auth='user', methods=['GET'])
     def sync(self,userId):
        try:
             records= http.request.env['res.partner'].sudo().search([
                 ('user_id','=', int(userId)),('customer_rank','!=',0)
             ])
             self.loadList(records)
             return self.build_response(self.data)
        except Exception as e:
             return self.build_response({'err', str(e)})

