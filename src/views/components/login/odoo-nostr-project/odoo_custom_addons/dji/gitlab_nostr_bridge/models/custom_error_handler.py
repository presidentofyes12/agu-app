import logging
import traceback
from odoo import models, fields, api
from functools import wraps

_logger = logging.getLogger(__name__)

class GitLabNostrErrorLog(models.Model):
    _name = 'gitlab.nostr.error.log'
    _description = 'GitLab Nostr Bridge Error Log'

    name = fields.Char(string='Error Summary', required=True)
    model = fields.Char(string='Model', required=True)
    method = fields.Char(string='Method', required=True)
    error_details = fields.Text(string='Error Details', required=True)
    stack_trace = fields.Text(string='Stack Trace')
    create_date = fields.Datetime(string='Error Timestamp', default=fields.Datetime.now, readonly=True)

    @api.model
    def log_error(self, summary, model, method, error, context=None):
        _logger.error(f"GitLab-Nostr Bridge Error: {summary} in {model}.{method}", exc_info=True)
        self.create({
            'name': summary,
            'model': model,
            'method': method,
            'error_details': str(error),
            'stack_trace': traceback.format_exc(),
        })

def gitlab_nostr_error_handler(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            error_log = self.env['gitlab.nostr.error.log']
            error_log.log_error(
                summary=str(e),
                model=self._name,
                method=func.__name__,
                error=e,
                context=self._context
            )
            # Re-raise the exception after logging
            raise
    return wrapper
