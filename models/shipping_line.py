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

    # Reemplazo de partner_id por remitente y destinatario
    sender_id = fields.Many2one('res.partner', string='Remitente', required=True)
    receiver_id = fields.Many2one('res.partner', string='Destinatario', required=True)
    
    shipping_type = fields.Selection([
        ('envio', 'Envío'),
        ('ena', 'ENA')
    ], string='Tipo de Envío', required=True, default='envio')

    # Código de bulto con valor temporal. Se asigna al confirmar el envío.
    package_code = fields.Char(string='Código Paquete', default=lambda self: self.env['ir.sequence'].next_by_code('shipping.management'), readonly=True, copy=False)
    
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