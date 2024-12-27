from odoo import models, fields, api
import json
import requests

class DistributedNode(models.Model):
    _name = 'atom.distributed.node'
    _description = 'Distributed Node'

    name = fields.Char(string='Node Name', required=True)
    url = fields.Char(string='Node URL', required=True)
    is_active = fields.Boolean(string='Is Active', default=True)

class AtomDistributedAPI(models.AbstractModel):
    _name = 'atom.distributed.api'
    _description = 'Atom Distributed API'

    @api.model
    def distribute_operation(self, operation, data):
        nodes = self.env['atom.distributed.node'].search([('is_active', '=', True)])
        results = []
        for node in nodes:
            try:
                response = requests.post(f"{node.url}/atom/{operation}", json=data)
                results.append(json.loads(response.text))
            except Exception as e:
                self.env['atom.log'].create({
                    'name': f'Distribution Error: {node.name}',
                    'description': str(e),
                    'type': 'error'
                })
        return results

    @api.model
    def distributed_search(self, criteria):
        return self.distribute_operation('search', criteria)

    @api.model
    def distributed_create(self, values):
        return self.distribute_operation('create', values)