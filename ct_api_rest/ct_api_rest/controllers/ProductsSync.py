from odoo import http
from odoo.http import Response
import json
import base64


class ProductsSync(http.Controller):
    data = []
    price_list = None
    # ------------- Metodo para Configurar Respuesta --------
    def build_response(self, table):
        response = json.dumps(table, ensure_ascii=False).encode('utf8')
        return Response(response, content_type='application/json;charset=utf-8', status=200)

    # ------------ Metodo para Crear el Object ----------------
    def createRecord(self, rec, tarifas):
        self.data.append({
            'id': rec.id,
            'sku': rec.default_code,
            'name': rec.name,
            'qty': rec.qty_available,
            'departament_id': rec.departament_id.id if rec.departament_id.id else None,
            'price': rec.list_price,
            'priceList': self.getListPrices(rec,tarifas)

        })

    # ------------ Metodo para Listar Arreglo de la Query -----
    def loadList(self, list):
        self.data = []
        tarifas=http.request.env['product.pricelist'].sudo().search([])
        for l in list:
            self.createRecord(l,tarifas)

    # ---------- Query para Sincronizar Datos -----------------
    @http.route('/ct.api/products/sync/', auth='user', methods=['GET'])
    def sync(self,**kwargs):
        try:
            #----------- Consultamos los Productos -------
            records = http.request.env['product.product'].sudo().search(
                [('type', '=', 'product')
                 ])
            self.loadList(records)
            return self.build_response(self.data)
        except Exception as e:
            return self.build_response({'err', str(e)})

    # ---------- Query para Sincronizar Departamentos -----------------
    @http.route('/ct.api/departament/sync/', auth='user', methods=['GET'])
    def syncDepartaments(self,**kwargs):
        try:
            records = http.request.env['ct.product.departament'].sudo().search([])
            self.data=[]
            for l in records:
                self.data.append({
                    'id': l.id,
                    'code': l.code,
                    'name': l.name,
                })

            return self.build_response(self.data)
        except Exception as e:
            return self.build_response({'err', str(e)})

    @http.route('/ct.api/products/getImage', methods=['GET'], type='http', auth='none', csrf=False)
    def get_image(self,id):
        filecontent="";
        r=http.request.env['product.product'].sudo().browse(int(id))
        filecontent = base64.b64decode(r.product_tmpl_id.image_1920)
        if not filecontent:
            return http.request.not_found()
        return http.request.make_response(filecontent, [('Content-Type', 'application/octet-stream')])


    def getListPrices(self, p,tarifas):
        price_list=[]
        for t in tarifas:
            price_list.append({
                'product_id': p.id,
                'price_list_id': t.id,
                'price': round(t.get_product_price(p, t.id, None, ), 2)
            })
        return price_list
