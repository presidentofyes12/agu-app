from odoo import models, fields

class IVCSCommit(models.Model):
    _name = 'ivcs.commit'
    _description = 'IVCS Commit'

    name = fields.Char(string='Commit Hash', required=True)
    message = fields.Text(string='Commit Message', required=True)
    author = fields.Char(string='Author', required=True)
    date = fields.Datetime(string='Commit Date', required=True)
    item_id = fields.Many2one('ivcs.item', string='IVCS Item', required=True, ondelete='cascade')
    branch = fields.Char(string='Branch', required=True)
