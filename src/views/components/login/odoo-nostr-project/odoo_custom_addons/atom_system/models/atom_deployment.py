from odoo import models, fields, api
import os
import subprocess

class AtomDeployment(models.Model):
    _name = 'atom.deployment'
    _description = 'Atom System Deployment'

    name = fields.Char(string='Deployment Name', required=True)
    version = fields.Char(string='Version', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('testing', 'Testing'),
        ('staging', 'Staging'),
        ('production', 'Production'),
        ('rolled_back', 'Rolled Back')
    ], string='State', default='draft')
    log = fields.Text(string='Deployment Log')

    def deploy_to_testing(self):
        self.ensure_one()
        self.state = 'testing'
        self.log += f"Deployed to testing environment at {fields.Datetime.now()}\n"
        # Add logic for deploying to testing environment

    def deploy_to_staging(self):
        self.ensure_one()
        self.state = 'staging'
        self.log += f"Deployed to staging environment at {fields.Datetime.now()}\n"
        # Add logic for deploying to staging environment

    def deploy_to_production(self):
        self.ensure_one()
        self.state = 'production'
        self.log += f"Deployed to production environment at {fields.Datetime.now()}\n"
        # Add logic for deploying to production environment

    def rollback(self):
        self.ensure_one()
        self.state = 'rolled_back'
        self.log += f"Rolled back deployment at {fields.Datetime.now()}\n"
        # Add logic for rolling back the deployment

    @api.model
    def run_tests(self):
        test_command = "odoo-bin -c /etc/odoo/odoo.conf -d %s -i atom_system --test-enable --stop-after-init" % self.env.cr.dbname
        process = subprocess.Popen(test_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise UserError("Tests failed:\n%s" % stderr.decode())
        return True