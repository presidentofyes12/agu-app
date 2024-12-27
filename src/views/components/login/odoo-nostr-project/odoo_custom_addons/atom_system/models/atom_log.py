from odoo import models, fields, api
import logging
import time

_logger = logging.getLogger(__name__)

class AtomLog(models.Model):
    _name = 'atom.log'
    _description = 'Atom System Log'

    name = fields.Char(string='Log Name', required=True)
    type = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ], string='Log Type', required=True)
    description = fields.Text(string='Description')
    create_date = fields.Datetime(string='Created On', default=fields.Datetime.now, readonly=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)

    @api.model
    def log_message(self, name, log_type, description):
        self.create({
            'name': name,
            'type': log_type,
            'description': description,
        })
        _logger.info(f"Atom Log: [{log_type}] {name} - {description}")

class AtomPerformanceMonitor(models.Model):
    _name = 'atom.performance.monitor'
    _description = 'Atom Performance Monitor'

    operation = fields.Char(string='Operation', required=True)
    duration = fields.Float(string='Duration (seconds)', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)

    @api.model
    def log_performance(self, operation, duration):
        self.create({
            'operation': operation,
            'duration': duration,
        })

class AtomAPI(models.AbstractModel):
    _inherit = 'atom.api'

    @api.model
    def search_atoms(self, domain):
        start_time = time.time()
        result = super(AtomAPI, self).search_atoms(domain)
        duration = time.time() - start_time
        self.env['atom.performance.monitor'].log_performance('search_atoms', duration)
        return result