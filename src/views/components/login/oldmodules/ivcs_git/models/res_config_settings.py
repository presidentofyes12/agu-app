from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ivcs_repo_base_path = fields.Char('IVCS Repository Base Path', config_parameter='ivcs.repo_base_path')
    github_token = fields.Char(string="GitHub Token", config_parameter='ivcs_git.github_token')
