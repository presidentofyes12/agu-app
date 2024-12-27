from odoo import models, fields

class Relationship(models.Model):
    _name = 'opinion.relationship'
    _description = 'Family Relationship'

    name = fields.Char(string='Relationship Name', required=True)
    description = fields.Text(string='Description')
