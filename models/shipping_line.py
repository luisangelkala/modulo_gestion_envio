from odoo import models, fields, api, _

class ShippingManagementLine(models.Model):
    _name = 'shipping.management.line'
    _description = 'Línea de Envío'

    shipping_id = fields.Many2one('shipping.management', string='Envío', ondelete='cascade')
    
    # Campo para filtrar impresión de HBL
    print_selected = fields.Boolean(string='Imprimir', default=False)

    # Reemplazo de partner_id por remitente y destinatario
    sender_id = fields.Many2one('res.partner', string='Remitente', required=True)
    receiver_id = fields.Many2one('res.partner', string='Destinatario', required=True)
    
    # Código de bulto con valor temporal. Se asigna al confirmar el envío.
    package_code = fields.Char(string='Código Paquete', default='Borrador', readonly=True, copy=False)
    
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

    # Se elimina el método create para que la secuencia se asigne solo al confirmar.

    def action_duplicate_line(self):
        """ Botón para duplicar la línea actual """
        self.ensure_one()
        self.copy({
            'shipping_id': self.shipping_id.id,
            # El package_code se reseteará a su default 'Borrador' al no ser copiado (copy=False).
        })