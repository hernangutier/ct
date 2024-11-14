# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json

class PaymentTermSync (http.Controller):
     data=[]
     #------------- Metodo para Confirgurar Respuesta --------
     def build_response(self,table):
         response=json.dumps(table, ensure_ascii=False).encode('utf8')
         return Response(response, content_type='application/json;charset=utf-8',status=200)

#------------ Metodo para Crear el Object ----------------
     def createRecord(self, rec):
         self.data.append({
             'id': rec.id,
             'name': rec.name,
             'active': int(rec.active)
         })
     #------------ Metodo para Listar Arreglo de la Query -----
     def loadList(self,list):
         self.data = []
         for l in list:
             self.createRecord(l)

     #---------- Query para Sincronizar Datos -----------------
     @http.route('/ct.api/paymentTerm/sync/', auth='user', methods=['GET'])
     def sync(self):
        try:
             records= http.request.env['account.payment.term'].sudo().search([
                 ('active','=', True)
             ])
             self.loadList(records)
             return self.build_response(self.data)
        except Exception as e:
             return self.build_response({'err', str(e)})