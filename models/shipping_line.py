from odoo import models, fields, api, _
import qrcode
import base64
from io import BytesIO

class ShippingManagementLine(models.Model):
    _name = 'shipping.management.line'
    _description = 'Línea de Envío'

    shipping_id = fields.Many2one('shipping.management', string='Envío', ondelete='cascade')
    
    # Campo para filtrar impresión de HBL
    print_selected = fields.Boolean(string='Imprimir', default=False)

    customer_id = fields.Many2one('res.partner', string="Cliente", help="Cliente que paga o contrata el envío.")

    # Reemplazo de partner_id por remitente y destinatario
    sender_id = fields.Many2one('res.partner', string='Remitente', required=True)
    receiver_id = fields.Many2one('res.partner', string='Destinatario', required=True)
    
    shipping_type = fields.Selection([
        ('envio', 'Envío'),
        ('ena', 'ENA')
    ], string='Tipo de Envío', required=True, default='envio')

    # El código se inicializa como 'NUEVO' y se genera formalmente al confirmar el envío (shipping.management)
    package_code = fields.Char(string='Código Paquete', default='NUEVO', readonly=True, copy=False)
    
    # QR Code generado en backend para alta calidad en PDF
    qr_image = fields.Binary(string="QR Code", compute="_compute_qr_image")

    @api.depends('package_code')
    def _compute_qr_image(self):
        for line in self:
            if line.package_code:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=6,
                    border=1,
                )
                qr.add_data(line.package_code)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                line.qr_image = qr_image
            else:
                line.qr_image = False

    # Nuevos campos de detalle de carga
    description = fields.Char(string='Mercancía')
    packages_qty = fields.Integer(string='Cantidad Bultos', default=1)
    
    # Dimensiones
    length = fields.Float(string='Largo (m)', default=0.0)
    width = fields.Float(string='Ancho (m)', default=0.0)
    height = fields.Float(string='Alto (m)', default=0.0)
    
    weight = fields.Float(string='Peso (Kg)', default=0.0)
    volume = fields.Float(string='Volumen (m³)', compute='_compute_volume', store=True)

    @api.depends('length', 'width', 'height')
    def _compute_volume(self):
        for line in self:
            line.volume = line.length * line.width * line.height

    def action_duplicate_line(self):
        """ Botón para duplicar la línea actual """
        self.ensure_one()
        self.copy({
            'shipping_id': self.shipping_id.id,
            # El package_code se reseteará a su default 'Borrador' al no ser copiado (copy=False).
        })

    # --- Lógica de Fraccionamiento Dinámico ENA ---

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.shipping_type == 'ena' and line.customer_id:
                line._recompute_ena_package_codes(line.shipping_id.id, line.customer_id.id)
        return lines

    def write(self, vals):
        # Identificar grupos afectados antes de la modificación (por si cambian de cliente o tipo)
        affected_groups = []
        if any(k in vals for k in ['customer_id', 'shipping_id', 'shipping_type']):
            for line in self:
                if line.shipping_type == 'ena' and line.customer_id:
                    affected_groups.append((line.shipping_id.id, line.customer_id.id))

        res = super().write(vals)

        # 1. Recomputar grupos originales (por si quedaron bultos que deben bajar el denominador Y)
        for ship_id, cust_id in set(affected_groups):
            self._recompute_ena_package_codes(ship_id, cust_id)

        # 2. Recomputar grupos nuevos
        if any(k in vals for k in ['customer_id', 'shipping_id', 'shipping_type']):
            for line in self:
                if line.shipping_type == 'ena' and line.customer_id:
                    line._recompute_ena_package_codes(line.shipping_id.id, line.customer_id.id)
                elif 'shipping_type' in vals and vals['shipping_type'] != 'ena':
                    # Si deja de ser ENA, vuelve a estado NUEVO para ser procesado por la secuencia normal
                    super(ShippingManagementLine, line).write({'package_code': 'NUEVO'})
        return res

    def unlink(self):
        # Capturar grupos antes de borrar
        groups_to_recompute = []
        for line in self:
            if line.shipping_type == 'ena' and line.customer_id:
                groups_to_recompute.append((line.shipping_id.id, line.customer_id.id))
        
        res = super().unlink()

        # Recomputar después de borrar para actualizar el conteo X/Y de los que quedan
        for ship_id, cust_id in set(groups_to_recompute):
            self._recompute_ena_package_codes(ship_id, cust_id)
        return res

    def _recompute_ena_package_codes(self, shipping_id_id, customer_id_id):
        """ Método privado para el cálculo dinámico de bultos ENA """
        if not shipping_id_id or not customer_id_id:
            return

        # Buscar todas las líneas ENA del mismo titular en este manifiesto
        lines = self.env['shipping.management.line'].search([
            ('shipping_id', '=', shipping_id_id),
            ('customer_id', '=', customer_id_id),
            ('shipping_type', '=', 'ena')
        ], order='id asc')

        if not lines:
            return

        # Intentar recuperar un código base ya asignado al grupo o generar uno nuevo
        base_code = next((l.package_code.split(' BULTO ')[0] for l in lines if l.package_code and l.package_code != 'NUEVO'), False)
        if not base_code:
            base_code = self.env['ir.sequence'].next_by_code('shipping.management')

        total = len(lines)
        for index, line in enumerate(lines, start=1):
            new_code = f"{base_code} BULTO {index}/{total}"
            if line.package_code != new_code:
                super(ShippingManagementLine, line).write({'package_code': new_code})