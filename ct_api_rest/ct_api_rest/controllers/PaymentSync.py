# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json

class PartnerSync (http.Controller):
     data=[]
     #------------- Metodo para Configurar Respuesta --------
     def build_response(self,table):
         response=json.dumps(table, ensure_ascii=False).encode('utf8')
         return Response(response, content_type='application/json;charset=utf-8',status=200)

     #------------ Metodo para Crear el Object ----------------
     def createRecord(self, rec):
         self.data.append({
             'id': rec.id,
            'journal_name': rec.journal_id.name,
            'journal_id': rec.journal_id.id,
            'partner_id': rec.partner_id.id,
            'amount': rec.amount,
            'date': str(rec.payment_date),
            'state': str(rec.state),
            'note': rec.note,
            'payment_reference': rec.payment_reference,
            #'number': rec.number
         })
     #------------ Metodo para Listar Arreglo de la Query -----
     def loadList(self,list):
         self.data = []
         for l in list:
             self.createRecord(l)

     #---------- Query para Sincronizar Datos -----------------
     @http.route('/ct.api/payments/sync/<id>', auth='user', methods=['GET'])
     def sync(self, id):
         try:
             records = http.request.env["account.payment"].sudo().search([
                 ('partner_id', '=', int(id))
             ])
             self.loadList(records)
             return self.build_response(self.data)
         except Exception as e:
             return self.build_response(
                 self.data.append({
                     'error': str(e)
                 })
             )

         # ----- Recepcion de Pago  ---------

     @http.route('/ct.api/payments/post', auth='user', type='json', methods=['POST'], csrf=False)
     def paymentPost(self, **kw):
         data = []
         try:
             # ----------- Consultamos los Productos -------
             json_request = json.loads(str(http.request.httprequest.data, 'utf-8'))
             # ---- Restricciones ---

             pay = http.request.env['account.payment'].sudo().search([])
             pay_data = []
             pay_data.append({
                 'partner_id': int(json_request['partner_id']),
                 'journal_id': int(json_request['journal_id']),
                 'note': json_request['note'],
                 'payment_reference': json_request['payment_reference'],
                 'amount': json_request['amount'],
                 'payment_type': 'inbound',
                 'partner_type': 'customer',
                 'payment_method_id': 1
             })
             # --- Aplicar Restriccion de Duplicacion de Monto al mismo Diario el Mismo Dia

             result = pay.create(pay_data)
             new_register = http.request.env['account.payment'].sudo().browse(int(result.id))
             new_register.update({
                 'number': http.request.env['ir.sequence'].sudo().next_by_code('payment')
             })
             # new_register = http.request.env['account.payment'].sudo().browse(int(result.id))
             data.append({
                 'code': 200,
                 'id': new_register.id,
                 'data': new_register.number,
                 'date': str(new_register.payment_date)
             })
             return data
         except Exception as e:
             return self.respose(400, str(e))
