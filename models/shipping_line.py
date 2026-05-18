from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import qrcode
import base64
from io import BytesIO


class ShippingManagementLine(models.Model):
    _name = 'shipping.management.line'
    _description = 'Linea de Envio'

    shipping_id = fields.Many2one('shipping.management', string='Envio', ondelete='cascade')

    # Campo para filtrar impresion de HBL
    print_selected = fields.Boolean(string='Imprimir', default=False)

    customer_id = fields.Many2one('res.partner', string='Cliente', help='Cliente que paga o contrata el envio.')

    # Remitente y destinatario
    sender_id = fields.Many2one('res.partner', string='Remitente', required=True)
    receiver_id = fields.Many2one('res.partner', string='Destinatario', required=True)

    shipping_type = fields.Selection([
        ('envio', 'Envio'),
        ('ena', 'ENA'),
    ], string='Tipo de Envio', required=True, default='envio')

    # ENA padre/hijos: una linea ENA hija apunta a una linea ENA padre del mismo manifiesto.
    ena_parent_id = fields.Many2one(
        'shipping.management.line',
        string='ENA Existente',
        domain="[('shipping_type', '=', 'ena'), ('ena_parent_id', '=', False), ('id', '!=', id)]",
        ondelete='set null',
        help='Seleccione un ENA existente para que esta linea use su codigo de paquete.',
    )
    ena_child_ids = fields.One2many('shipping.management.line', 'ena_parent_id', string='Envios Hijos ENA', readonly=True)

    is_ena_child = fields.Boolean(string='Es ENA Hijo', compute='_compute_ena_flags')
    is_ena_parent = fields.Boolean(string='Es ENA Padre', compute='_compute_ena_flags')

    # Se genera al crear la linea para mostrar el codigo real en popup.
    package_code = fields.Char(
        string='Codigo Paquete',
        default=lambda self: self.env['ir.sequence'].next_by_code('shipping.management') or 'NUEVO',
        readonly=True,
        copy=False,
    )

    # QR generado en backend para alta calidad en PDF
    qr_image = fields.Binary(string='QR Code', compute='_compute_qr_image')

    # Detalle de carga
    description = fields.Char(string='Mercancia')
    packages_qty = fields.Integer(string='Cantidad Bultos', default=1)

    # Dimensiones
    length = fields.Float(string='Largo (m)', default=0.0)
    width = fields.Float(string='Ancho (m)', default=0.0)
    height = fields.Float(string='Alto (m)', default=0.0)

    weight = fields.Float(string='Peso (Kg)', default=0.0)
    volume = fields.Float(string='Volumen (m3)', compute='_compute_volume', store=True)

    @api.depends('ena_parent_id', 'ena_child_ids')
    def _compute_ena_flags(self):
        for line in self:
            line.is_ena_child = bool(line.ena_parent_id)
            line.is_ena_parent = bool(line.ena_child_ids)

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
                img = qr.make_image(fill_color='black', back_color='white')
                temp = BytesIO()
                img.save(temp, format='PNG')
                line.qr_image = base64.b64encode(temp.getvalue())
            else:
                line.qr_image = False

    @api.depends('length', 'width', 'height')
    def _compute_volume(self):
        for line in self:
            line.volume = line.length * line.width * line.height

    @api.onchange('shipping_type')
    def _onchange_shipping_type(self):
        if self.shipping_type != 'ena':
            self.ena_parent_id = False

    @api.onchange('ena_parent_id')
    def _onchange_ena_parent_id(self):
        if self.shipping_type != 'ena':
            self.ena_parent_id = False
            return

        if self.ena_parent_id:
            self.package_code = self.ena_parent_id.package_code
        elif self._origin and self._origin.ena_parent_id:
            # Si se despega de un ENA existente, pasa a ENA padre con nuevo codigo.
            self.package_code = self._next_package_code()

    @api.constrains('ena_parent_id', 'shipping_type', 'shipping_id')
    def _check_ena_parent_rules(self):
        for line in self:
            if line.ena_parent_id:
                if line.shipping_type != 'ena':
                    raise ValidationError(_('Solo las lineas tipo ENA pueden vincularse a un ENA existente.'))
                if line.ena_parent_id.id == line.id:
                    raise ValidationError(_('Una linea no puede ser ENA de si misma.'))
                if line.ena_parent_id.shipping_id != line.shipping_id:
                    raise ValidationError(_('El ENA seleccionado debe pertenecer al mismo manifiesto.'))
                if line.ena_parent_id.shipping_type != 'ena':
                    raise ValidationError(_('El ENA seleccionado debe ser una linea tipo ENA.'))
                if line.ena_parent_id.ena_parent_id:
                    raise ValidationError(_('No se puede seleccionar una linea ENA hija como ENA existente.'))

        if not self._check_recursion(parent='ena_parent_id'):
            raise ValidationError(_('No se permite recursion en agrupaciones ENA.'))

    def _next_package_code(self):
        return self.env['ir.sequence'].next_by_code('shipping.management') or 'NUEVO'

    def _get_ena_parent(self, parent_id):
        parent = self.env['shipping.management.line'].browse(parent_id).exists()
        if not parent:
            raise ValidationError(_('El ENA seleccionado no existe.'))
        return parent

    def _validate_parent_candidate(self, parent, shipping_id=None, current_id=None):
        if parent.shipping_type != 'ena':
            raise ValidationError(_('El ENA seleccionado debe ser tipo ENA.'))
        if parent.ena_parent_id:
            raise ValidationError(_('Solo puede seleccionar lineas ENA padre como ENA existente.'))
        if shipping_id and parent.shipping_id.id != shipping_id:
            raise ValidationError(_('El ENA seleccionado debe pertenecer al mismo manifiesto.'))
        if current_id and parent.id == current_id:
            raise ValidationError(_('Una linea no puede ser ENA de si misma.'))

    def _ensure_parent_can_change(self, vals):
        for line in self:
            if not line.ena_child_ids:
                continue

            shipping_type = vals.get('shipping_type', line.shipping_type)
            parent_id = vals.get('ena_parent_id', line.ena_parent_id.id)
            shipping_id = vals.get('shipping_id', line.shipping_id.id)

            if shipping_type != 'ena' or parent_id or shipping_id != line.shipping_id.id:
                raise ValidationError(_(
                    'La linea ENA padre %(code)s tiene envios hijos. Primero mueva o elimine sus hijos.',
                    code=line.package_code or line.display_name,
                ))

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = []
        for vals in vals_list:
            vals = dict(vals)

            shipping_type = vals.get('shipping_type', 'envio')
            parent_id = vals.get('ena_parent_id')
            shipping_id = vals.get('shipping_id')

            if shipping_type != 'ena':
                vals['ena_parent_id'] = False
            elif parent_id:
                parent = self._get_ena_parent(parent_id)
                self._validate_parent_candidate(parent, shipping_id=shipping_id)
                vals['package_code'] = parent.package_code

            prepared_vals_list.append(vals)

        return super().create(prepared_vals_list)

    def write(self, vals):
        self._ensure_parent_can_change(vals)

        vals = dict(vals)

        # Cambio de tipo fuera de ENA: limpiar relacion y generar nuevo codigo unico.
        if 'shipping_type' in vals and vals['shipping_type'] != 'ena':
            vals['ena_parent_id'] = False
            for line in self:
                super(ShippingManagementLine, line).write({'package_code': self._next_package_code()})

        # Si se enlaza a ENA existente, forzar codigo del ENA padre.
        if 'ena_parent_id' in vals and vals['ena_parent_id']:
            parent = self._get_ena_parent(vals['ena_parent_id'])
            for line in self:
                target_type = vals.get('shipping_type', line.shipping_type)
                if target_type != 'ena':
                    raise ValidationError(_('Solo lineas ENA pueden enlazarse a un ENA existente.'))
                self._validate_parent_candidate(
                    parent,
                    shipping_id=vals.get('shipping_id', line.shipping_id.id),
                    current_id=line.id,
                )
            vals['package_code'] = parent.package_code

        # Si una linea ENA hija se convierte en ENA padre (ena_parent_id=False), generar nuevo codigo.
        if 'ena_parent_id' in vals and not vals['ena_parent_id']:
            target_type = vals.get('shipping_type')
            for line in self:
                line_type = target_type or line.shipping_type
                if line_type == 'ena' and line.ena_parent_id:
                    super(ShippingManagementLine, line).write({'package_code': self._next_package_code()})

        res = super().write(vals)

        # Mantener sincronizados codigos de hijos cuando un padre cambia por integridad.
        for line in self.filtered(lambda l: l.shipping_type == 'ena' and l.ena_child_ids):
            line.ena_child_ids.write({'package_code': line.package_code})

        # Asegurar herencia de codigo para lineas hijas ENA.
        for line in self.filtered(lambda l: l.shipping_type == 'ena' and l.ena_parent_id):
            if line.package_code != line.ena_parent_id.package_code:
                super(ShippingManagementLine, line).write({'package_code': line.ena_parent_id.package_code})

        return res

    def unlink(self):
        for line in self:
            if line.ena_child_ids:
                raise ValidationError(_(
                    'No puede eliminar el ENA padre %(code)s mientras tenga envios hijos.',
                    code=line.package_code or line.display_name,
                ))
        return super().unlink()

    def action_duplicate_line(self):
        """Boton para duplicar la linea actual."""
        self.ensure_one()

        default_vals = {
            'shipping_id': self.shipping_id.id,
        }

        # Si se duplica una ENA hija, conserva pertenencia al mismo ENA.
        if self.shipping_type == 'ena' and self.ena_parent_id:
            default_vals['ena_parent_id'] = self.ena_parent_id.id

        self.copy(default_vals)
