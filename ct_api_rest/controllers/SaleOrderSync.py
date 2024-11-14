# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json

class SaleOrderSync(http.Controller):
    data=[]
    # ------------- Metodo para Confirgurar Respuesta --------
    def build_response(self, table):
        response = json.dumps(table, ensure_ascii=False).encode('utf8')
        return Response(response, content_type='application/json;charset=utf-8', status=200)

    # ------------ Metodo para Crear el Object ----------------
    def createRecord(self, rec):
        self.data.append({
            'id': rec.id,
            'som_id': rec.sale_order_movile_id.id if rec.sale_order_movile_id else None,
            'number': rec.name,
            'departament_id': rec.departament_id.id,
            'date_order': str(rec.date_order),
            'partner_id': rec.partner_id.id,
            'payment_term_id': rec.payment_term_id.id,
            'amount': rec.amount_total,
            'state': str(rec.state),
            'state_invoice': str(rec.invoice_status),
            'state_preparations': str(rec.state_preparations),
            'lines_count': len(rec.order_line),
            'lines': self.createLines(rec.order_line)
        })

    def loadList(self,list):
        self.data=[]
        for l in list:
            self.createRecord(l)

    def createLines(self, data):
        lines = []
        for l in data:
            lines.append({
                'id': l.id,
                'order_id': l.order_id.id,
                'product_id': l.product_id.id,
                'product_name': l.product_id.display_name,
                'qty': l.product_uom_qty,
                'price_unit': l.price_unit,
                'subtotal': l.price_subtotal
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

    @http.route('/ct.api/saleOrder/syncForPartner/<id>', auth='user', methods=['GET'])
    def syncForPartner(self, id):
        sales=http.request.env['sale.order'].search([
            ('partner_id','=',int(id)),
            ('state','!=','cancel'),
            ('invoice_status', 'not in', (''))

        ])
        self.loadList(sales)
        return self.build_response(self.data)

    @http.route('/ct.api/saleOrder/syncByPartner/<id>', auth='user', methods=['GET'])
    def syncByPartner(self, id):
        sales=http.request.env['sale.order'].search([
            ('partner_id','=',int(id)),
        ],limit=500)
        self.loadList(sales)
        return self.build_response(self.data)

    @http.route('/ct.api/saleOrder/syncForSOM/<id>', auth='user', methods=['GET'])
    def syncForSOM(self, id):
        sales = http.request.env['sale.order'].search([
            ('sale_order_movile_id', '=', int(id))
        ])
        self.loadList(sales)
        return self.build_response(self.data)

    
