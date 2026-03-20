from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import io
import xlsxwriter

class ShippingReferenceCatalog(models.Model):
    _name = 'shipping.reference.catalog'
    _description = 'Catálogo de Referencias'
    _rec_name = 'name'

    name = fields.Char(string='Identificador / Referencia', required=True, help="Ej: MANIFIESTO-2023-001")
    transport_type = fields.Selection([
        ('air', 'Aéreo'),
        ('sea', 'Marítimo')
    ], string='Tipo de Transporte', required=True)
    active = fields.Boolean(default=True, string="Activo")

class ShippingManagement(models.Model):
    _name = 'shipping.management'
    _description = 'Gestión de Envío'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Referencia', required=True, copy=False, tracking=True)
    
    reference_id = fields.Many2one('shipping.reference.catalog', string='Referencia (Catálogo)', 
                                   help="Seleccione un número de referencia del catálogo", tracking=True)

    @api.onchange('reference_id')
    def _onchange_reference_id(self):
        if self.reference_id:
            self.name = self.reference_id.name

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado')
    ], string='Estado', default='draft', tracking=True, required=True)

    transport_type = fields.Selection([
        ('air', 'Aéreo'),
        ('sea', 'Marítimo')
    ], string='Tipo de Transporte', required=True, default='sea', tracking=True)

    date_shipping = fields.Date(string='Fecha de Envío', default=fields.Date.context_today, tracking=True)
    
    # Campos operativos (Excel)
    agencia_origen = fields.Many2one('res.partner', string='Agencia de Origen', tracking=True)
    pais_id = fields.Many2one('res.country', string='País', tracking=True)
    consignatario_id = fields.Many2one('res.partner', string='Consignatario', tracking=True)
    awb = fields.Char(string='AWB / BL / Contenedor', tracking=True)

    # Campos readonly en estado confirmado
    container_type_id = fields.Many2one('shipping.container.type', string='Contenedor', 
        readonly=False) 
    
    carrier = fields.Many2one('res.partner', string='Naviera / Aerolínea', tracking=True)

    # Campo de Compañía para soporte multi-empresa y reportes
    company_id = fields.Many2one('res.company', string='Compañía', required=True, 
                                 default=lambda self: self.env.company)

    line_ids = fields.One2many('shipping.management.line', 'shipping_id', string='Líneas de Envío')

    # Smart Stats (Computados)
    total_packages = fields.Integer(string='Total Bultos', compute='_compute_smart_stats', store=True)
    total_weight = fields.Float(string='Peso Total (Kg)', compute='_compute_smart_stats', store=True)
    total_volume = fields.Float(string='Volumen Total (m³)', compute='_compute_smart_stats', store=True)
    unique_client_count = fields.Integer(string='Total Clientes', compute='_compute_smart_stats', store=True)

    @api.depends('line_ids.weight', 'line_ids.volume', 'line_ids.sender_id', 'line_ids.packages_qty')
    def _compute_smart_stats(self):
        for rec in self:
            rec.total_packages = sum(line.packages_qty for line in rec.line_ids)
            rec.total_weight = sum(line.weight for line in rec.line_ids)
            rec.total_volume = sum(line.volume for line in rec.line_ids)
            rec.unique_client_count = len(rec.line_ids.mapped('sender_id'))

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

    def action_dummy(self):
        """ Método dummy para los Smart Buttons que son solo informativos """
        pass

    def action_print_bl(self):
        """ Retorna la acción para imprimir el BL, abriendo el PDF en una nueva pestaña """
        self.ensure_one()
        return self.env.ref('modulo_gestion_envio.action_report_shipping_bl').report_action(self)

    def action_export_manifest_excel(self):
        self.ensure_one()
        
        # Crear el archivo Excel en memoria
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Formatos
        title_format = workbook.add_format({'bold': True, 'font_size': 14})
        bold_format = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        
        # Cálculos de totales
        total_bultos = sum(line.packages_qty for line in self.line_ids)
        total_peso = sum(line.weight for line in self.line_ids)
        
        # --- HOJA 1: MANIFIESTO ---
        sheet_man = workbook.add_worksheet('MANIFIESTO')
        
        # Bloque de información superior Manifiesto
        sheet_man.write(0, 0, 'CARGA PARA CUBANACAN', title_format)
        sheet_man.write(1, 0, 'FECHA DESPACHO:', bold_format)
        sheet_man.write(1, 1, self.create_date.strftime('%d-%b-%Y') if self.create_date else '')
        sheet_man.write(2, 0, 'NRO DE VUELO:', bold_format)
        sheet_man.write(2, 1, self.carrier.name if self.carrier else '')
        sheet_man.write(3, 0, 'AWB:', bold_format)
        sheet_man.write(4, 0, 'BL:', bold_format)
        sheet_man.write(4, 1, self.name or '')
        sheet_man.write(5, 0, 'CANT. CONTENEDOR:', bold_format)
        sheet_man.write(6, 0, 'SELLO:', bold_format)
        sheet_man.write(7, 0, 'TOTAL DE BULTOS:', bold_format)
        sheet_man.write(7, 1, total_bultos)
        sheet_man.write(8, 0, 'PESO TOTAL:', bold_format)
        sheet_man.write(8, 1, total_peso)

        # Cabeceras de Tabla Manifiesto (Fila 9)
        headers_man = [
            'NRO. HBL', 'REMITENTE', 'IDENTIFICACION DEL REMITENTE', 'DIRECCION DEL REMITENTE',
            'PROVINCIA DEL REMITENTE', 'PAIS DEL REMITENTE', 'CONSIGNATARIO',
            'IDENTIFICACION DEL CONSIGNATARIO', 'DIRECCION DEL CONSIGNATARIO',
            'MUNICIPIO DEL CONSIGNATARIO', 'PROVINCIA DEL CONSIGNATARIO', 'PAIS CONSIGNATARIO',
            'CANTIDAD DE BULTOS', 'DESCRIPCION DEL CONTENIDO', 'PESO EN KG'
        ]
        
        row_man = 9
        for col, header in enumerate(headers_man):
            sheet_man.write(row_man, col, header, header_format)
            sheet_man.set_column(col, col, 20)
        
        # Datos Manifiesto
        row_man += 1
        for line in self.line_ids:
            sheet_man.write(row_man, 0, line.package_code or '')
            sheet_man.write(row_man, 1, line.sender_id.name or '')
            sheet_man.write(row_man, 2, line.sender_id.vat or '')
            sheet_man.write(row_man, 3, line.sender_id.street or '')
            sheet_man.write(row_man, 4, line.sender_id.state_id.name or '')
            sheet_man.write(row_man, 5, line.sender_id.country_id.name or '')
            sheet_man.write(row_man, 6, line.receiver_id.name or '')
            sheet_man.write(row_man, 7, line.receiver_id.vat or '')
            sheet_man.write(row_man, 8, line.receiver_id.street or '')
            sheet_man.write(row_man, 9, line.receiver_id.city or '')
            sheet_man.write(row_man, 10, line.receiver_id.state_id.name or '')
            sheet_man.write(row_man, 11, line.receiver_id.country_id.name or '')
            sheet_man.write(row_man, 12, line.packages_qty or 1)
            sheet_man.write(row_man, 13, line.description or '')
            sheet_man.write(row_man, 14, line.weight or 0.0)
            row_man += 1

        # --- HOJA 2: BOLETA ---
        sheet_bol = workbook.add_worksheet('BOLETA')
        
        # Bloque de información superior Boleta
        sheet_bol.write(0, 0, 'DETALLE DE BOLETAS', title_format)
        sheet_bol.write(1, 0, 'TOTAL DE BULTOS:', bold_format)
        sheet_bol.write(1, 1, total_bultos)

        # Cabeceras de Tabla Boleta (Fila 2)
        headers_bol = ['NRO. HBL', 'BOLETA', 'CONTENEDOR', 'SELLO', 'CANTIDAD DE BULTOS', 'PESO EN KG']
        row_bol = 2
        for col, header in enumerate(headers_bol):
            sheet_bol.write(row_bol, col, header, header_format)
            sheet_bol.set_column(col, col, 20)

        # Datos Boleta
        row_bol += 1
        for line in self.line_ids:
            sheet_bol.write(row_bol, 0, line.package_code or '')
            sheet_bol.write(row_bol, 1, self.name or '')
            sheet_bol.write(row_bol, 2, '') 
            sheet_bol.write(row_bol, 3, '') 
            sheet_bol.write(row_bol, 4, line.packages_qty or 1)
            sheet_bol.write(row_bol, 5, line.weight or 0.0)
            row_bol += 1

        workbook.close()
        output.seek(0)
        
        # Guardar como adjunto y retornar acción de descarga
        excel_file = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': f'Manifiesto_{self.name}.xlsx',
            'type': 'binary',
            'datas': excel_file,
            'res_model': 'shipping.management',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }