import json
import base64
from odoo import http
from odoo.http import request
from odoo import api, fields, models, _
from odoo.addons.ct_api_rest.controllers.PartnerSync import PartnerSync


class SaleMovileSync(http.Controller):
    data = []
    detail = []
    partnerSync = PartnerSync()

    # ------------- Metodo para Configurar Respuesta --------
    def build_response(self, table):
        response = json.dumps(table, ensure_ascii=False).encode('utf8')
        return http.Response(response, content_type='application/json;charset=utf-8', status=200)

    def response(self,code,result):
        data=[]
        if code==200:
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
            'sale_id': rec.id,
            'number': rec.name,
            'partner_id': rec.partner_id.id,
            'date_order': rec.confirmation_date,
            'partner_name': rec.partner_id.name,
            'user_id': rec.user_id.id
        })

    # ------- Url Post para Enviar Pedido ---
    @http.route('/ct.api/sale.movile/post', auth='user', type='json', methods=['POST'], csrf=False)
    def SaleMovilePost(self, **kwargs):

            result=[]
            lines = []
            # ----------- Cargamos el Json -------
            json_request = json.loads(str(http.request.httprequest.data, 'utf-8'))
            partner_id=http.request.env['res.partner'].browse(int(json_request['partner']['id']))
            #---- Validamos el Cliente si Tiene Saldo Deudor ---
            if self.partnerSync.check_due(int(json_request['partner']['id']))==True:
                result.append({
                    'code': 400,
                    'data': 'Cliente Bloqueado por Saldo Vencido!',

                })
                return result
            # ---- Leemos la Lineas de Pedido ----
            for l in json_request['lines']:
                qty=http.request.env['product.product'].browse(int(l['product_id']))
                vals = (0, 0, {
                        'product_id': l['product_id'],
                        'qty': int(l['product_uom_qty']),
                        'product_uom_id': int(l['uom_id']),
                })
                lines.append(vals)


            # ----- Creamos el Pedido Movil -----
            sale_movile = http.request.env['ct.sale.order.movile'].sudo().create({
                'partner_id': json_request['partner']['id'],
                'require_fiscal': int(json_request['saleOrder']['require_fiscal']),
                'user_id': partner_id.user_id.id,
                'order_lines': lines
            })
            new_sale=sale_movile.sudo().action_confirm()
            result.append({
                'code': 200,
                'id': new_sale.id,
                'name': new_sale.name,
                'data': 'Pedido Enviado Correctamente!',
                'date': new_sale.create_date
            })
            return result

