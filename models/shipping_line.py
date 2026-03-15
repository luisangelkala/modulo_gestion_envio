from odoo import models, fields, api, _

class ShippingManagementLine(models.Model):
    _name = 'shipping.management.line'
    _description = 'Línea de Envío'

    shipping_id = fields.Many2one('shipping.management', string='Envío', ondelete='cascade')
    
    # Si el cliente no existe, el widget Many2one permite crearlo.
    # Para forzar creación automática sin popup, se requiere personalización JS o un campo Char intermedio.
    # Usamos la mejor práctica de Odoo: Many2one permite "Crear y Editar" o "Crear 'Nombre'" nativamente.
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    
    package_code = fields.Char(string='Código Paquete', help="Código único del bulto")
    
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
            'package_code': False # Resetear código para evitar duplicados si es único
        })