from odoo import models, fields, api

class DAO(models.Model):
    _name = 'decentralized.sync.dao'
    _description = 'DAO'

    manager_id = fields.Many2one('decentralized.sync.manager', string='Sync Manager')
    tier = fields.Selection([('primary', 'Primary'), ('secondary', 'Secondary'), ('tertiary', 'Tertiary')], string='Tier')
    location_lat = fields.Float(string='Latitude')
    location_lon = fields.Float(string='Longitude')
    storage_capacity = fields.Float(string='Storage Capacity')
    network_speed = fields.Float(string='Network Speed')
    local_state = fields.Text(string='Local State')

class Creator(models.Model):
    _name = 'decentralized.sync.creator'
    _description = 'Creator'

    manager_id = fields.Many2one('decentralized.sync.manager', string='Sync Manager')
    location_lat = fields.Float(string='Latitude')
    location_lon = fields.Float(string='Longitude')
    productivity = fields.Float(string='Productivity')
    dao_id = fields.Many2one('decentralized.sync.dao', string='Associated DAO')

class Program(models.Model):
    _name = 'decentralized.sync.program'
    _description = 'Program'

    manager_id = fields.Many2one('decentralized.sync.manager', string='Sync Manager')
    creator_id = fields.Many2one('decentralized.sync.creator', string='Creator')
    size = fields.Float(string='Size')
    version = fields.Integer(string='Version')
    content = fields.Text(string='Content')
    host_ids = fields.Many2many('decentralized.sync.dao', string='Hosts')

class Event(models.Model):
    _name = 'decentralized.sync.event'
    _description = 'Sync Event'

    manager_id = fields.Many2one('decentralized.sync.manager', string='Sync Manager')
    description = fields.Text(string='Event Description')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

class Connection(models.Model):
    _name = 'decentralized.sync.connection'
    _description = 'Connection between Creator and DAO'

    manager_id = fields.Many2one('decentralized.sync.manager', string='Sync Manager')
    creator_id = fields.Many2one('decentralized.sync.creator', string='Creator')
    dao_id = fields.Many2one('decentralized.sync.dao', string='DAO')
