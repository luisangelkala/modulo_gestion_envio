from odoo import models, fields

class ShippingContainerType(models.Model):
    _name = 'shipping.container.type'
    _description = 'Tipo de Contenedor'
    _order = 'name'

    name = fields.Char(string='Tipo (Nombre)', required=True, help="Ej: 20ST, 40HC")
    capacity_m3 = fields.Float(string='Capacidad (m³)', required=True, digits=(16, 2))
    capacity_kg = fields.Float(string='Capacidad (Kg)', required=True, digits=(16, 2))
    
    # Dimensiones internas referenciales
    length = fields.Float(string='Largo (m)', digits=(16, 2))
    width = fields.Float(string='Ancho (m)', digits=(16, 2))
    height = fields.Float(string='Alto (m)', digits=(16, 2))
    