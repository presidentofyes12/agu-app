from odoo import models, fields, api

class User(models.Model):
    _name = 'opinion.user'
    _description = 'User Model'
    
    name = fields.Char(required=True)
    reputation = fields.Float(compute='_compute_reputation', store=True)
    predictions = fields.One2many('opinion.prediction', 'user_id')

    @api.depends('predictions.is_correct')
    def _compute_reputation(self):
        for user in self:
            predictions = user.predictions
            correct_predictions = sum(1 for p in predictions if p.is_correct)
            total_predictions = len(predictions)
            user.reputation = (correct_predictions / total_predictions) * 100 if total_predictions else 0
