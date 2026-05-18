from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import io
import xlsxwriter

class ShippingReferenceCatalog(models.Model):
    _name = 'shipping.reference.catalog'
    _description = 'CatÃ¡logo de Referencias'
    _rec_name = 'name'

    name = fields.Char(string='Identificador / Referencia', required=True, help="Ej: MANIFIESTO-2023-001")
    transport_type = fields.Selection([
        ('air', 'AÃ©reo'),
        ('sea', 'MarÃ­timo')
    ], string='Tipo de Transporte', required=True)
    active = fields.Boolean(default=True, string="Activo")

class ShippingManagement(models.Model):
    _name = 'shipping.management'
    _description = 'GestiÃ³n de EnvÃ­o'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Referencia', required=True, copy=False, tracking=True)
    
    reference_id = fields.Many2one('shipping.reference.catalog', string='Referencia (CatÃ¡logo)', 
                                   help="Seleccione un nÃºmero de referencia del catÃ¡logo", tracking=True)

    @api.onchange('reference_id')
    def _onchange_reference_id(self):
        if self.reference_id:
            self.name = self.reference_id.name

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado')
    ], string='Estado', default='draft', tracking=True, required=True)

    transport_type = fields.Selection([
        ('air', 'AÃ©reo'),
        ('sea', 'MarÃ­timo')
    ], string='Tipo de Transporte', required=True, default='sea', tracking=True)

    date_shipping = fields.Date(string='Fecha de EnvÃ­o', default=fields.Date.context_today, tracking=True)
    
    # Campos operativos (Excel)
    agencia_origen = fields.Many2one('res.partner', string='Agencia de Origen', tracking=True)
    pais_id = fields.Many2one('res.country', string='PaÃ­s', tracking=True)
    consignatario_id = fields.Many2one('res.partner', string='Consignatario', tracking=True)
    awb = fields.Char(string='AWB / BL / Contenedor', tracking=True)

    # Campos readonly en estado confirmado
    container_type_id = fields.Many2one('shipping.container.type', string='Contenedor', 
        readonly=False) 
    
    carrier = fields.Many2one('res.partner', string='Naviera / AerolÃ­nea', tracking=True)

    # Campo de CompaÃ±Ã­a para soporte multi-empresa y reportes
    company_id = fields.Many2one('res.company', string='CompaÃ±Ã­a', required=True, 
                                 default=lambda self: self.env.company)

    line_ids = fields.One2many('shipping.management.line', 'shipping_id', string='LÃ­neas de EnvÃ­o')

    # --- LÃ³gica de Filtrado en Pantalla ---
    line_search = fields.Char(string='Buscar en lÃ­neas', store=False) # Campo temporal para escribir
    line_ids_display = fields.One2many(
        'shipping.management.line',
        'shipping_id',
        string='LÃ­neas Visibles',
        compute='_compute_line_ids_display',
        inverse='_inverse_dummy',
    )

    @api.depends('line_ids', 'line_search')
    def _compute_line_ids_display(self):
        for rec in self:
            if rec.line_search:
                s = rec.line_search.lower()
                # Filtra si el texto coincide con CÃ³digo, Cliente, Remitente o Destinatario
                rec.line_ids_display = rec.line_ids.filtered(lambda l: 
                    (l.package_code and s in l.package_code.lower()) or
                    (l.customer_id.name and s in l.customer_id.name.lower()) or
                    (l.sender_id.name and s in l.sender_id.name.lower()) or
                    (l.receiver_id.name and s in l.receiver_id.name.lower())
                )
            else:
                rec.line_ids_display = rec.line_ids

    def _inverse_dummy(self):
        # Necesario para que el campo computed sea editable y permita agregar lÃ­neas
        pass

    # Smart Stats (Computados)
    total_packages = fields.Integer(string='Total Bultos', compute='_compute_smart_stats', store=True)
    total_weight = fields.Float(string='Peso Total (Kg)', compute='_compute_smart_stats', store=True)
    total_volume = fields.Float(string='Volumen Total (mÂ³)', compute='_compute_smart_stats', store=True)
    unique_client_count = fields.Integer(string='Total Clientes', compute='_compute_smart_stats', store=True)

    @api.depends('line_ids.weight', 'line_ids.volume', 'line_ids.sender_id', 'line_ids.packages_qty')
    def _compute_smart_stats(self):
        for rec in self:
            rec.total_packages = sum(line.packages_qty for line in rec.line_ids)
            rec.total_weight = sum(line.weight for line in rec.line_ids)
            rec.total_volume = sum(line.volume for line in rec.line_ids)
            rec.unique_client_count = len(rec.line_ids.mapped('sender_id'))

    def write(self, vals):
        # Bloqueo estricto de ediciÃ³n si el registro estÃ¡ confirmado
        # Se permite escribir solo si se estÃ¡ cambiando el estado (por ejemplo, al confirmar)
        if 'state' not in vals:
            for rec in self:
                if rec.state == 'confirmed':
                    raise ValidationError(_("No se puede modificar un envÃ­o que ya ha sido confirmado (%s).", rec.name))
        return super().write(vals)

    def action_confirm(self):
        self.ensure_one()
        # BLOQUEO TEMPORAL: Retornar sin ejecutar lÃ³gica
        return True

        # Validaciones de Reglas de Negocio
        self._check_capacity_rules()
        # AsignaciÃ³n de cÃ³digos de bulto segÃºn reglas (ENA vs Normal)
        self._assign_package_codes()
        self.write({'state': 'confirmed'})

    def _assign_package_codes(self):
        """
        Asigna los cÃ³digos de bulto finales.
        - EnvÃ­os normales: secuencia Ãºnica si no tiene.
        - ENA padre: conserva su cÃ³digo propio.
        - ENA hija: hereda cÃ³digo del ENA padre seleccionado.
        """
        for rec in self:
            for line in rec.line_ids:
                if line.shipping_type != 'ena':
                    if not line.package_code or line.package_code == 'NUEVO':
                        line.package_code = self.env['ir.sequence'].next_by_code('shipping.management')
                    continue

                if line.ena_parent_id:
                    line.package_code = line.ena_parent_id.package_code
                elif not line.package_code or line.package_code == 'NUEVO':
                    line.package_code = self.env['ir.sequence'].next_by_code('shipping.management')

    def _check_capacity_rules(self):
        """ Valida las reglas de negocio antes de confirmar """
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("No se puede confirmar un envÃ­o sin lÃ­neas de carga."))

            # Regla AÃ©reo: Max 2500 Kg
            if rec.transport_type == 'air':
                if rec.total_weight > 2500:
                    raise ValidationError(_(
                        "Alerta de Capacidad AÃ©rea: El peso total (%(weight)s kg) excede el lÃ­mite permitido de 2500 kg.",
                        weight=rec.total_weight
                    ))
            
            # Regla MarÃ­timo: Volumen vs Contenedor
            elif rec.transport_type == 'sea':
                if not rec.container_type_id:
                    raise ValidationError(_("Debe seleccionar un Tipo de Contenedor para envÃ­os marÃ­timos."))
                
                if rec.total_volume > rec.container_type_id.capacity_m3:
                    raise ValidationError(_(
                        "Alerta de Capacidad MarÃ­tima: El volumen total (%(vol)s mÂ³) excede la capacidad del contenedor %(cont)s (%(cap)s mÂ³).",
                        vol=round(rec.total_volume, 2),
                        cont=rec.container_type_id.name,
                        cap=rec.container_type_id.capacity_m3
                    ))

    def action_reset_draft(self):
        """ Opcional: Para permitir correcciones si el admin lo requiere, aunque el requisito dice 'solo lectura' """
        # Se incluye para facilitar pruebas, en producciÃ³n se puede ocultar con permisos
        self.write({'state': 'draft'})

    def action_dummy(self):
        """ MÃ©todo dummy para los Smart Buttons que son solo informativos """
        pass

    def action_print_bl(self):
        """ Retorna la acciÃ³n para imprimir el BL, abriendo el PDF en una nueva pestaÃ±a """
        self.ensure_one()
        # BLOQUEO TEMPORAL return True
        return self.env.ref('modulo_gestion_envio.action_report_shipping_bl').report_action(self)

    def action_export_manifest_excel(self):
        self.ensure_one()
        # BLOQUEO TEMPORAL return True 

        # Crear el archivo Excel en memoria
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Formatos
        bold_format = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'text_wrap': True, 'valign': 'vcenter'})
        
        # CÃ¡lculos de totales
        total_envios = len(self.line_ids)
        total_bultos = sum(line.packages_qty for line in self.line_ids)
        total_peso = sum(line.weight for line in self.line_ids)
        fecha_str = self.create_date.strftime('%d/%m/%Y') if self.create_date else ''
        
        # --- HOJA 1: MANIFIESTO ---
        sheet_man = workbook.add_worksheet('MANIFIESTO')
        
        # 1. Bloque de informaciÃ³n superior (Filas 0 a 8)
        sheet_man.write(0, 0, 'AGENCIA ORIGEN', bold_format)
        sheet_man.write(0, 1, 'ORDAZ')
        
        sheet_man.write(1, 0, 'PAÃS', bold_format)
        sheet_man.write(1, 1, 'PANAMÃ')
        
        sheet_man.write(2, 0, 'CONSIGNATARIO', bold_format)
        sheet_man.write(2, 1, 'Cubanacan Express S.A')
        
        sheet_man.write(3, 0, 'MBL/AWB', bold_format)
        sheet_man.write(3, 1, self.name or '')
        
        sheet_man.write(4, 0, 'CONTENEDOR', bold_format)
        sheet_man.write(4, 1, '') # Dejar en blanco para llenar manual o mapear en el futuro
        
        sheet_man.write(5, 0, 'TOTAL ENVÃOS', bold_format)
        sheet_man.write(5, 1, total_envios)
        
        sheet_man.write(6, 0, 'TOTAL DE BULTOS', bold_format)
        sheet_man.write(6, 1, total_bultos)
        
        sheet_man.write(7, 0, 'TOTAL PESO (Kg)', bold_format)
        sheet_man.write(7, 1, total_peso)
        
        sheet_man.write(8, 0, 'FECHA', bold_format)
        sheet_man.write(8, 1, fecha_str)

        # 2. Cabeceras de Tabla Manifiesto (Fila 10)
        headers_man = [
            'No. ENVÃO (HBL)', 'REMITENTE', 'DIRECCIÃ“N REMITENTE', 'DNI/PASAPORTE REMITENTE',
            'DESTINATARIO', 'DIRECCIÃ“N DESTINATARIO', 'MUNICIPIO', 'PROVINCIA', 
            'CARNÃ‰ IDENTIDAD', 'TELÃ‰FONO FIJO', 'TELÃ‰FONO MÃ“VIL', 'BULTOS', 
            'PESO (Kg)', 'MERCANCIA', 'OBSERVACIONES'
        ]
        
        row_man = 10
        for col, header in enumerate(headers_man):
            sheet_man.write(row_man, col, header, header_format)
            # Ajustar anchos de columna para mejor lectura
            if col in [2, 5, 13]: # Direcciones y Mercancia
                sheet_man.set_column(col, col, 35)
            elif col in [1, 4]: # Nombres
                sheet_man.set_column(col, col, 25)
            else:
                sheet_man.set_column(col, col, 15)
        
        # 3. Datos de la Tabla Manifiesto
        row_man += 1
        for line in self.line_ids:
            sheet_man.write(row_man, 0, line.package_code or '')
            sheet_man.write(row_man, 1, line.sender_id.name or '')
            
            # DirecciÃ³n Remitente (Concatenada)
            sender_address = f"{line.sender_id.street or ''} {line.sender_id.street2 or ''}".strip()
            sheet_man.write(row_man, 2, sender_address)
            
            sheet_man.write(row_man, 3, line.sender_id.vat or '')
            sheet_man.write(row_man, 4, line.receiver_id.name or '')
            
            # DirecciÃ³n Destinatario (Concatenada)
            receiver_address = f"{line.receiver_id.street or ''} {line.receiver_id.street2 or ''}".strip()
            sheet_man.write(row_man, 5, receiver_address)
            
            sheet_man.write(row_man, 6, line.receiver_id.city or '')
            sheet_man.write(row_man, 7, line.receiver_id.state_id.name or '')
            sheet_man.write(row_man, 8, line.receiver_id.vat or '')
            
            # TelÃ©fonos (Si solo hay uno en Odoo, lo ponemos en mÃ³vil y dejamos fijo vacÃ­o)
            sheet_man.write(row_man, 9, '') # TelÃ©fono Fijo (Dejar vacÃ­o o mapear si tienes el campo)
            sheet_man.write(row_man, 10, line.receiver_id.phone or '') # TelÃ©fono MÃ³vil
            
            sheet_man.write(row_man, 11, line.packages_qty or 1)
            sheet_man.write(row_man, 12, line.weight or 0.0)
            sheet_man.write(row_man, 13, line.description or '')
            sheet_man.write(row_man, 14, '') # Observaciones
            row_man += 1

        # --- HOJA 2: BOLETA (Se mantiene bÃ¡sica por ahora) ---
        sheet_bol = workbook.add_worksheet('BOLETA')
        sheet_bol.write(0, 0, 'DETALLE DE BOLETAS', bold_format)
        sheet_bol.write(1, 0, 'TOTAL DE BULTOS:', bold_format)
        sheet_bol.write(1, 1, total_bultos)

        headers_bol = ['NRO. HBL', 'BOLETA', 'CONTENEDOR', 'SELLO', 'CANTIDAD DE BULTOS', 'PESO EN KG']
        row_bol = 3
        for col, header in enumerate(headers_bol):
            sheet_bol.write(row_bol, col, header, header_format)
            sheet_bol.set_column(col, col, 20)

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
        
        # Guardar como adjunto y retornar acciÃ³n de descarga
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
