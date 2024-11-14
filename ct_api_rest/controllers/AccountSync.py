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
     #-------- Envia Datos Variados para Actualizar estado de Cuenta ---
     @http.route('/ct.api/state.accouny/sync/', type='json', methods=['POST'], csrf=False)
     def postStateAccount(self,**kwargs):
         paymentList=[]
         invoiceList=[]
         ordersList=[]
         # ----------- Consultamos los Productos -------
         json_request = json.loads(str(http.request.httprequest.data, 'utf-8'))

         partner=http.request.env['res.partner'].sudo().browse(int(json_request['id']))
         #-------  Cargamos los Pagos
         for i in partner.invoice_ids:
             invoiceList.append({
                 'id': i.id,
                 'number': rec.name,
                 'origim': rec.invoice_origin,
                 'partner_id': rec.partner_id.id,
             })
         for s in partner.sale_order_ids:
             ordersList.append({
                 'id': rec.id,
                 'number': rec.name,
                 'origim': rec.invoice_origin,
                 'partner_id': rec.partner_id.id,
             })
