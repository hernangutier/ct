# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
import textwrap


class KardexReportWz(models.TransientModel):
    _name = 'ct.kardex.report.wz'
    _description = 'Dialogo para Crear Reporte de Movimientos de Stock'

    date_from = fields.Datetime(
        string='Desde', required=True, default=fields.Datetime.now)
    date_to = fields.Datetime(
        string='Hasta', required=True, default=fields.Datetime.now)
    product = fields.Many2one('product.product', required=True)
    location = fields.Many2one('stock.location', required=True)
    #--------- para controlar interfaz grafica ----------------
    is_readonly=fields.Boolean('solo lectura', default=False)


    def loadData(self):
        self.env['ct.kardex'].search([]).unlink()
        self._cr.execute('''
                SELECT
                a.done - b.done
                AS
                total
                FROM
                (
                    SELECT sum(qty_done)
                    AS
                    done
                    FROM
                    stock_move_line
                    WHERE
                    product_id = %s
                    AND
                    state = \'done\'
                    AND
                    date < %s
                    AND
                    location_dest_id = %s
                )
                a
                CROSS JOIN
                (
                    SELECT sum(qty_done)
                    AS
                    done
                    FROM
                    stock_move_line
                    WHERE
                    product_id = %s
                    AND
                    state = \'done\'
                    AND
                    date < %s
                    AND
                    location_id = %s
                )
                b
                ''', [
            self.product.id, self.date_from, self.location.id,
            self.product.id, self.date_from, self.location.id
        ])
        start_qty = self._cr.dictfetchall()
        total = 0
        if start_qty[0]['total']:
            total = start_qty[0]['total']
        self._cr.execute("""WITH one AS (
                    SELECT
                    sml.product_id, sml.product_uom_id,
                    sml.lot_id, sml.owner_id, sml.package_id,
                    sml.qty_done, sml.move_id, sml.location_id,
                    sml.location_dest_id, sm.date, sm.origin,
                    sm.state
                    FROM stock_move_line sml
                    INNER JOIN stock_move sm
                    ON sml.move_id = sm.id
                    WHERE
                    sm.date >= %s
                    AND sm.date <= %s),
                    two AS (
                        SELECT *
                        FROM one
                        WHERE location_id = %s
                        OR location_dest_id = %s)
                    SELECT *
                    FROM two
                    WHERE product_id = %s
                    AND state = 'done'
                    ORDER BY date;""", [
            self.date_from, self.date_to,
            self.location.id, self.location.id,
            self.product.id
        ])
        moves = self._cr.dictfetchall()
        report_list = []
        report_list.append({
            'product_id': self.product.id,
            'qty_done': 0,
            'date': self.date_from,
            'origin': _('Balance Inicial'),
            'balance': total,
        })
        for rec in moves:
            qty_in = 0
            qty_out = 0
            done_qty = rec['qty_done']
            if rec['location_id'] == self.location.id:
                done_qty = -rec['qty_done']
            total += done_qty
            origin = rec['origin'] if rec['origin'] else 'Ajuste/Inventaio'
            if origin:
                origin = textwrap.shorten(
                    origin, width=80, placeholder="...")
                # ------ Consultamos el Partner ----
                order = self.env['sale.order'].search([('name', '=', origin)], limit=1)
                if order:
                    rec['owner_id'] = order.partner_id.id
            if done_qty > 0:
                qty_in = done_qty
            else:
                qty_out = done_qty

            line = {
                'move_id': rec['move_id'],
                'product_id': rec['product_id'],
                'product_uom_id': rec['product_uom_id'],
                'lot_id': rec['lot_id'],
                'owner_id': rec['owner_id'],
                'package_id': rec['package_id'],
                'qty_done': done_qty,
                'qty_in': qty_in,
                'qty_out': qty_out,
                'location_id': rec['location_id'],
                'location_dest_id': rec['location_dest_id'],
                'date': rec['date'],
                'balance': total,
                'origin': origin,
            }
            report_list.append(line)
        self.env['ct.kardex'].create(report_list)

    def open_table(self):
        self.loadData()
        tree_view_id = self.env.ref(
            'ct_products_kardex.view_ct_kardex_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_id': tree_view_id,
            'view_mode': 'tree',
            'name': _('Stock Report'),
            'res_model': 'ct.kardex',
        }
        return action

    def get_report(self):
        self.loadData()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_init': self.date_from,
                'date_end': self.date_to,
                'product_id': self.product.id,
                'location_id': self.location.id,
            },
        }
        return self.env.ref('ct_products_kardex.kardex_report_200').report_action(self, data=data)


class ReportKardex(models.AbstractModel):
    _name = "report.ct_products_kardex.ct_pdf_report_200"

    def _get_report_values(self, docids, data=None):
        docs = self.env['ct.kardex'].search_read([],order='date asc')
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_init': data['form']['date_init'],
            'date_end': data['form']['date_end'],
            'company': self.env.user.company_id,
            'user': self.env.user,
            'product_name': self.env['product.product'].browse(int(data['form']['product_id'])).name,
            'docs': docs,
        }

