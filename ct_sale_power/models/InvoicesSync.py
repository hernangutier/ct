# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json
import time
from odoo import api, fields, models,_


class InvoicesSync(http.Controller):
    data = []


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
            'state': 1 if rec.state_delivered==True else 0,
            'plazo': rec.invoice_payment_term_id.name,
            'despacho': str(rec.date_delivered),
            'days_late': str(rec.day_due) if rec.day_due else None,
            'emision': str(rec.invoice_date),
            'vence': str(rec.date_due_delivered) if rec.state_delivered else str(rec.invoice_date_due),
            'amount': rec.amount_total,
            'amount_due': rec.amount_residual,
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

    # ------------ Metodo para Listar Arreglo de la Query -----
    def loadList(self, list):
        self.data = []
        for l in list:
            self.createRecord(l)

    def loadListReturn(self,list):
        self.data = []
        for l in list:
            self.createRecord(l)
        return self.data

    # ---------- Query para Sincronizar Datos -----------------
    @http.route('/ct.api/invoices/sync/<userId>', auth='user', methods=['GET'])
    def sync(self, userId, **kwargs):
        #try:
            records = http.request.env['account.move'].sudo().search([
                ('state', '=', 'posted'),
                ('user_id', '=', int(userId)),
                ('type', '=', 'out_invoice'),
                ('invoice_payment_state', '=', 'not_paid')
            ])
            self.loadList(records)
            return self.build_response(self.data)
        #except Exception as e:
        #    return self.build_response({'err': str(e)})

            # ---------- Query para Sincronizar Datos -----------------

    @http.route('/ct.api/invoice/single.sync/<id>', auth='user', methods=['GET'])
    def SingleSync(self, id):
            try:
                records = http.request.env['account.move'].sudo().search([
                    ('state', '=', 'posted'),
                    ('partner_id', '=', int(id)),
                    ('type', '=', 'out_invoice'),
                    ('invoice_payment_state', '=', 'not_paid')
                ])
                self.loadList(records)
                return self.build_response(self.data)
            except Exception as e:
                return self.build_response({'err': str(e)})

    @http.route('/ct.api/invoice/SummaryDue/<id>', auth='user', methods=['GET'])
    def SummaryDue(self, id):
        self.data=[]
        data=http.request.env['account.move'].sudo().read_group(
            [('user_id','=',int(id)),('state','=','posted'),('invoice_payment_state','!=','paid'),('date_due_delivered','<',fields.Date.today())],
            ['partner_id','amount_residual_signed'],
            ['partner_id']
        )
        for g in data:
            self.data.append({
                'partner_id': int(g.get('partner_id')[0]),
                'partner_name': http.request.env['res.partner'].sudo().browse(int(g.get('partner_id')[0])).display_name,
                'count': g.get('partner_id_count'),
                'due': g.get('amount_residual_signed')

            })
        return self.build_response(self.data)

    @http.route('/ct.api/invoice/dueForPartner/<id>', auth='user', methods=['GET'])
    def dueForPartner(self,id):
        self.data=[]
        invoice=http.request.env['account.move'].search(
            [('partner_id', '=', int(id)), ('state', '=', 'posted'), ('invoice_payment_state', '!=', 'paid'),
             ('date_due_delivered', '<', fields.Date.today())], order="invoice_date_due desc"
        )
        self.loadList(invoice)
        return self.build_response(self.data)

    @http.route('/ct.api/invoice/invoiceReport/<id>', auth='user', methods=['GET'])
    def invoiceReport(self,id, **kwargs):
        pdf, _ = http.request.env.ref('account.account_invoices').sudo().render_qweb_pdf([int(id)])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return http.request.make_response(pdf, headers=pdfhttpheaders)


