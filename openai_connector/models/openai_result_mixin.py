# -*- coding: utf-8 -*-
# Copyright (C) 2022 - Myrrkel (https://github.com/myrrkel).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpenAiResultMixin(models.AbstractModel):
    _name = 'openai.result.mixin'
    _description = 'OpenAI result Mixin'

    name = fields.Char(compute='_compute_name')
    model_id = fields.Many2one('ir.model', string='Model', readonly=True, ondelete='cascade')
    model = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    target_field_id = fields.Many2one('ir.model.fields', string='Target Field', readonly=True)
    res_id = fields.Integer('Resource ID', readonly=True)
    resource_ref = fields.Reference(string='Record', selection='_selection_target_model',
                                    compute='_compute_resource_ref', inverse='_set_resource_ref', readonly=True)
    prompt = fields.Text(readonly=True)

    @api.model
    def _selection_target_model(self):
        model_ids = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in model_ids]

    @api.depends('model_id', 'res_id')
    def _compute_resource_ref(self):
        for rec in self:
            if rec.model_id and rec.res_id:
                record = self.env[rec.model_id.model].browse(rec.res_id)
                res_id = record[0] if record else 0
                rec.resource_ref = '%s,%s' % (rec.model_id.model, res_id.id)
            else:
                rec.resource_ref = False

    @api.onchange('resource_ref')
    def _set_resource_ref(self):
        for rec in self:
            rec.res_id = rec.resource_ref.id