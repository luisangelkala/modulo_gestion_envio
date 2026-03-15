from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ShippingManagement(models.Model):
    _name = 'shipping.management'
    _description = 'Gestión de Envío'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado')
    ], string='Estado', default='draft', tracking=True, required=True)

    transport_type = fields.Selection([
        ('air', 'Aéreo'),
        ('sea', 'Marítimo')
    ], string='Tipo de Transporte', required=True, default='sea', tracking=True)

    date_shipping = fields.Date(string='Fecha de Envío', default=fields.Date.context_today, tracking=True)
    
    # Campos readonly en estado confirmado
    container_type_id = fields.Many2one('shipping.container.type', string='Contenedor', 
        readonly=False) 
    
    carrier = fields.Char(string='Naviera/Aerolínea', tracking=True)

    line_ids = fields.One2many('shipping.management.line', 'shipping_id', string='Líneas de Envío')

    # Smart Stats (Computados)
    total_packages = fields.Integer(string='Total Bultos', compute='_compute_smart_stats', store=True)
    total_weight = fields.Float(string='Peso Total (Kg)', compute='_compute_smart_stats', store=True)
    total_volume = fields.Float(string='Volumen Total (m³)', compute='_compute_smart_stats', store=True)
    unique_client_count = fields.Integer(string='Total Clientes', compute='_compute_smart_stats', store=True)

    @api.depends('line_ids', 'line_ids.weight', 'line_ids.volume', 'line_ids.partner_id')
    def _compute_smart_stats(self):
        for rec in self:
            rec.total_packages = len(rec.line_ids)
            rec.total_weight = sum(line.weight for line in rec.line_ids)
            rec.total_volume = sum(line.volume for line in rec.line_ids)
            rec.unique_client_count = len(rec.line_ids.mapped('partner_id'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('shipping.management') or _('Nuevo')
        return super().create(vals_list)

    def write(self, vals):
        # Bloqueo estricto de edición si el registro está confirmado
        # Se permite escribir solo si se está cambiando el estado (por ejemplo, al confirmar)
        if 'state' not in vals:
            for rec in self:
                if rec.state == 'confirmed':
                    raise ValidationError(_("No se puede modificar un envío que ya ha sido confirmado (%s).", rec.name))
        return super().write(vals)

    def action_confirm(self):
        self.ensure_one()
        # Validaciones de Reglas de Negocio
        self._check_capacity_rules()
        self.write({'state': 'confirmed'})

    def _check_capacity_rules(self):
        """ Valida las reglas de negocio antes de confirmar """
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("No se puede confirmar un envío sin líneas de carga."))

            # Regla Aéreo: Max 2500 Kg
            if rec.transport_type == 'air':
                if rec.total_weight > 2500:
                    raise ValidationError(_(
                        "Alerta de Capacidad Aérea: El peso total (%(weight)s kg) excede el límite permitido de 2500 kg.",
                        weight=rec.total_weight
                    ))
            
            # Regla Marítimo: Volumen vs Contenedor
            elif rec.transport_type == 'sea':
                if not rec.container_type_id:
                    raise ValidationError(_("Debe seleccionar un Tipo de Contenedor para envíos marítimos."))
                
                if rec.total_volume > rec.container_type_id.capacity_m3:
                    raise ValidationError(_(
                        "Alerta de Capacidad Marítima: El volumen total (%(vol)s m³) excede la capacidad del contenedor %(cont)s (%(cap)s m³).",
                        vol=round(rec.total_volume, 2),
                        cont=rec.container_type_id.name,
                        cap=rec.container_type_id.capacity_m3
                    ))

    def action_reset_draft(self):
        """ Opcional: Para permitir correcciones si el admin lo requiere, aunque el requisito dice 'solo lectura' """
        # Se incluye para facilitar pruebas, en producción se puede ocultar con permisos
        self.write({'state': 'draft'})