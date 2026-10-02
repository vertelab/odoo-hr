# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel AB <info@vertel.se>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Utveckling över tid — poäng per stil över samtliga mätningar.

Detta är den vy som gör modulen värd något: beteendet kan utvecklas, och
mätningen görs upprepat. Tidslinjen visar rörelsen mot tjänstens zon.

Zonen ritas som referens. Ingen procentsats, ingen "måluppfyllelse" — bara
värden, datum och zonen de jämförs mot.
"""

from odoo import api, fields, models


class HrWorkstyleTrend(models.TransientModel):
    _name = 'hr.workstyle.trend'
    _description = 'Behavioural Development Over Time'

    res_model = fields.Selection([
        ('hr.employee', 'Employee'),
        ('hr.applicant', 'Applicant'),
    ], string='Applies To', required=True)
    res_id = fields.Integer(string='Record', required=True)
    res_name = fields.Char(string='Person', compute='_compute_res_name')
    job_id = fields.Many2one('hr.job', string='Job Position')
    line_ids = fields.One2many(
        'hr.workstyle.trend.line', 'trend_id', string='Development')

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for trend in self:
            trend.res_name = False
            if trend.res_model and trend.res_id:
                record = self.env[trend.res_model].browse(
                    trend.res_id).exists()
                if record:
                    trend.res_name = record.display_name

    @api.model
    def action_open(self, res_model, res_id):
        """Öppna utvecklingsvyn för en person."""
        trend = self.create({'res_model': res_model, 'res_id': res_id})
        trend._build_lines()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Behavioural Development',
            'res_model': 'hr.workstyle.trend',
            'res_id': trend.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _build_lines(self):
        self.ensure_one()
        self.line_ids = [(5, 0, 0)]
        record = self.env[self.res_model].browse(self.res_id).exists()
        if not record:
            return
        self.job_id = record.job_id.id
        styles = self.env['hr.workstyle.style'].search([])
        zones = {line.style_id.id: line
                 for line in (record.job_id.workstyle_line_ids
                              if record.job_id else [])}
        assessments = record.workstyle_assessment_ids.sorted(
            key=lambda a: (a.date or fields.Date.today(), a.id))
        lines = []
        for assessment in assessments:
            scores = {line.style_id.id: line.score
                      for line in assessment.line_ids}
            for style in styles:
                zone = zones.get(style.id)
                lines.append((0, 0, {
                    'style_id': style.id,
                    'date': assessment.date,
                    'score': scores.get(style.id, 0),
                    'zone_min': zone.ideal_min if zone else 0,
                    'zone_max': zone.ideal_max if zone else 0,
                }))
        self.line_ids = lines


class HrWorkstyleTrendLine(models.TransientModel):
    _name = 'hr.workstyle.trend.line'
    _description = 'Behavioural Development Point'
    _order = 'style_id, date'

    trend_id = fields.Many2one(
        'hr.workstyle.trend', required=True, ondelete='cascade')
    style_id = fields.Many2one('hr.workstyle.style', string='Style')
    date = fields.Date(string='Date')
    score = fields.Integer(string='Score')
    zone_min = fields.Integer(string='Zone From')
    zone_max = fields.Integer(string='Zone To')
