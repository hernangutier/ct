# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json

class InvoicesSync (http.Controller):
     data=[]
     
     #------------- Metodo para Confirgurar Respuesta --------
     def build_response(self,table):
         response=json.dumps(table, ensure_ascii=False).encode('utf8')
         return Response(response, content_type='application/json;charset=utf-8',status=200)

     #------------ Metodo para Crear el Object ----------------
     def createRecord(self, rec):
         self.data.append({
             'id': rec.id,
             'number': rec.name,
             'origim': rec.invoice_origin,
             'partner_id': rec.partner_id.id,
             'lines': self.createLines(rec.invoice_line_ids)
         })
     def createLines(self,data):
         lines=[]
         for l in data:
             lines.append({
                 'id': l.id,
                 'invoiceId': l.move_id.id,
                 'productId': l.product_id.id,
                 'productName': l.product_id.display_name,
                 'qty': l.quantity,
                 'priceUnit': l.price_unit,
                 'subTotal': l.price_subtotal
             })
         return lines
     #------------ Metodo para Listar Arreglo de la Query -----
     def loadList(self,list):
         self.data = []
         for l in list:
             self.createRecord(l)



     # ---------- Query para Sincronizar Datos -----------------
     @http.route('/ct.api/invoices/sync/<userId>', auth='user', methods=['GET'])
     def sync(self,userId,**kwargs):
         try:
             records = http.request.env['account.move'].sudo().search([
                 ('state', '=', 'posted'),
                 ('user_id', '=', int(userId)),
                 ('type','=','out_invoice'),
                 ('invoice_payment_state','=','not_paid')
             ])
             self.loadList(records)
             return self.build_response(self.data)
         except Exception as e:
             return self.build_response({'err': str(e)})

