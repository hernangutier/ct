# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json

class SaleOrderSync(http.Controller):
    # ------------- Metodo para Confirgurar Respuesta --------
    def build_response(self, table):
        response = json.dumps(table, ensure_ascii=False).encode('utf8')
        return Response(response, content_type='application/json;charset=utf-8', status=200)

    # ------------ Metodo para Crear el Object ----------------
    def createRecord(self, rec):
        self.data.append({
            'id': rec.id,
            'number': rec.name,
            'origim': rec.invoice_origin,
            'partner_id': rec.partner_id.id,
            'lines': self.createLines(rec.invoice_line_ids)
        })

    def createLines(self, data):
        lines = []
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

 #---------- Query para Sincronizar Datos -----------------
    @http.route('/ct.api/saleOrder/sync/<userId>', auth='user', methods=['GET'])
    def sync(self,userId):
         try:
             partners=http.request.env['res.partner'].sudo().search([('user_id','=',int(userId)),('state','!=','cancel')])
             #for p in partners:
                #if p.state_invoice==''

             records= http.request.env['sale.order'].sudo().search([
                 ('user_id','=', int(userId)),('partner_id','in',)
             ])
             self.loadList(records)
             return self.build_response(self.data)
         except Exception as e:
             return self.build_response({'err', str(e)})
    #--------------------------------------------------------------
    #
    #    Url para Crear pedidos separados por departamento de
    #    Facturacion (uno a Muchos)
    #--------------------------------------------------------------
    @http.route('/api/saleOrder/create', auth='user', type='json')
    def create(self,**kwargs):
        try:
            #----------------- Separamos las Lineas de Pedido -----------------

            pass
        except Exception as e:
            pass
