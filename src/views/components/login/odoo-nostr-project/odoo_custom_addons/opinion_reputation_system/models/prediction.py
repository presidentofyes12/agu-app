from odoo import models, fields, api

class Prediction(models.Model):
    _name = 'opinion.prediction'
    _description = 'Prediction Model'
    
    user_id = fields.Many2one('opinion.user', required=True)
    question_id = fields.Many2one('opinion.question', required=True)
    answer = fields.Selection([
        ('agree', 'I Agree'),
        ('do_not_disagree', 'I do not disagree'),
        ('do_not_agree', 'I do not agree'),
        ('disagree', 'I Disagree')
    ], required=True)
    confidence = fields.Float(required=True)
    timestamp = fields.Datetime(default=fields.Datetime.now)
    is_correct = fields.Boolean()

    @api.model
    def get_answer_options(self):
        return [
            ('agree', 'I Agree'),
            ('do_not_disagree', 'I do not disagree'),
            ('do_not_agree', 'I do not agree'),
            ('disagree', 'I Disagree')
        ]
