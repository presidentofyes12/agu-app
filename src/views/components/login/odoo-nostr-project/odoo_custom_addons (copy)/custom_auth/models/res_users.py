from odoo import models, api
from odoo.exceptions import AccessDenied
import requests

class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _login(cls, db, login, password):
        if not cls.validate_external_auth(login, password):
            raise AccessDenied()
        return super(ResUsers, cls)._login(db, login, password)

    @classmethod
    def validate_external_auth(cls, login, token):
        # Replace with your actual localhost API endpoint
        validation_url = 'http://localhost/validate_admin'
        response = requests.post(validation_url, json={'login': login, 'token': token})
        return response.status_code == 200 and response.json().get('is_admin', False)
