# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
from odoo.addons.ct_api_rest.controllers.InvoicesSync import InvoicesSync
from odoo.addons.ct_api_rest.controllers.PaymentSync import PaymentSync
import json
import time
from odoo import api, fields, models,_


class PartnerSync(http.Controller):
    data = []
    payment=PaymentSync()
    invoiceSync= InvoicesSync()
    # ------------- Metodo para Confirgurar Respuesta --------
    def build_response(self, table):
        response = json.dumps(table, ensure_ascii=False).encode('utf8')
        return Response(response, content_type='application/json;charset=utf-8', status=200)

    def response(self, code, result):
        data = []
        if code == 200:
            data.append({
                'code': "200",
                'data': result,
            })
        else:
            data.append({
                'code': "400",
                'data': result,
            })
        return data

    # ------------ Metodo para Crear el Object ----------------
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




    # ------------ Metodo para Listar Arreglo de la Query -----
    def loadList(self, list):
        self.data = []
        for l in list:
            self.createRecord(l)

    # ---------- Query para Sincronizar Datos -----------------
    @http.route('/ct.api/partner/sync/<userId>', auth='user', methods=['GET'])
    def sync(self, userId):
        try:
            records = http.request.env['res.partner'].sudo().search([
                ('user_id', '=', int(userId)), ('customer_rank', '!=', 0)
            ])
            self.loadList(records)
            return self.build_response(self.data)
        except Exception as e:
            return self.build_response({'err', str(e)})

    @http.route('/ct.api/partner/single.sync/<id>', auth='user', methods=['GET'])
    def single_sync(self, id):
        try:
            records = http.request.env['res.partner'].sudo().search([
                ('id', '=', int(id)), ('customer_rank', '!=', 0)
            ])
            self.loadList(records)
            return self.build_response(self.data)
        except Exception as e:
            return self.build_response({'err', str(e)})

    @http.route('/ct.api/partner/post', auth='user', type='json', methods=['POST'], csrf=False)
    def post(self, **kwargs):

        try:
            # ----------- Cargamos el Json -------
            json_request = json.loads(str(http.request.httprequest.data, 'utf-8'))
            partner = http.request.env['res.partner'].browse(int(json_request['id']))
            # --- Actualizamos el Cliente ----
            partner.write({
                'phone': json_request['phone'],
                'email': json_request['email'],
                'city': json_request['city'],
                'property_payment_term_id': json_request['payment_term_id'],
            })
            return self.response(200, 'Registro Actualizado Correctamente...')
        except Exception as e:
            return self.response(400, str(e))

    def check_due(self,id):
        data = http.request.env['account.move'].sudo().search(
            [('partner_id', '=', int(id)),
             ('state', '=', 'posted'),
             ('invoice_payment_state', '!=', 'paid'),
             ('date_due_delivered', '<', fields.Date.today())
             ])
        if len(data):
            return True
        else:
            return False

    @http.route('/ct.api/partner/single.complete.sync/<id>', auth='user', methods=['GET'])
    def syncSingle(self, id):
        invoicesData = []
        paymenstData=[]
        rec = http.request.env['res.partner'].sudo().browse(int(id))
        if rec:
                #---- Cargamos las Facturas ---
                rec_ids=rec.invoice_ids.filtered(
                    lambda x: x.type == 'out_invoice' and x.state == 'posted' and x.invoice_payment_state == 'not_paid')

                invoicesData=self.invoiceSync.loadListReturn(rec_ids)
                #------ Consultamos los Pagos Registrados para el Cliente ---
                pays = http.request.env["account.payment"].sudo().search([
                    ('partner_id', '=', int(id))
                ])
                paymenstData = self.payment.loadListReturn(pays)

                self.data=[]
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
                    'price_list_id': rec.property_product_pricelist.id,
                    'invoice_ids': invoicesData,
                    'payment_ids': paymenstData
                })
                return self.build_response(self.data)

                #----- Creamos el Registro Completo para Actualizacion



