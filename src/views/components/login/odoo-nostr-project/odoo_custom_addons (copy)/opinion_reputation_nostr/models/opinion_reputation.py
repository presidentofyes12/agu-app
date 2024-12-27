from odoo import models, fields, api
from odoo.exceptions import UserError
import enum
import logging

_logger = logging.getLogger(__name__)

class AnswerChoice(enum.Enum):
    AGREE = "I Agree"
    DO_NOT_DISAGREE = "I do not disagree"
    DO_NOT_AGREE = "I do not agree"
    DISAGREE = "I Disagree"

class User(models.Model):
    _inherit = 'res.users'

    reputation = fields.Float(default=0)

class Question(models.Model):
    _name = 'opinion.question'
    _description = 'Opinion Question'

    text = fields.Text(required=True)
    explanation = fields.Text()
    created_by = fields.Many2one('res.users', string='Created By')
    created_at = fields.Datetime(default=fields.Datetime.now)
    is_settled = fields.Boolean(default=False)
    last_revisited = fields.Datetime()

class Prediction(models.Model):
    _name = 'opinion.prediction'
    _description = 'Opinion Prediction'

    user_id = fields.Many2one('res.users', required=True)
    question_id = fields.Many2one('opinion.question', required=True)
    answer = fields.Selection([
        ('AGREE', 'I Agree'),
        ('DO_NOT_DISAGREE', 'I do not disagree'),
        ('DO_NOT_AGREE', 'I do not agree'),
        ('DISAGREE', 'I Disagree')
    ], required=True)
    confidence = fields.Float(required=True)
    timestamp = fields.Datetime(default=fields.Datetime.now)
    is_correct = fields.Boolean()

    @api.model
    def create(self, vals):
        prediction = super(Prediction, self).create(vals)
        try:
            self.env['opinion.nostr.event'].create_prediction_event(prediction)
        except Exception as e:
            _logger.error(f"Failed to create Nostr event for prediction {prediction.id}: {str(e)}")
        self.update_reputation(prediction.user_id.id)
        return prediction

    def update_reputation(self, user_id):
        user = self.env['res.users'].browse(user_id)
        predictions = self.search([('user_id', '=', user_id)])
        correct_predictions = predictions.filtered(lambda p: p.is_correct)
        if predictions:
            user.reputation = (len(correct_predictions) / len(predictions)) * 100

class OpinionReputationSystem(models.AbstractModel):
    _name = 'opinion.reputation.system'
    _description = 'Opinion Reputation System'

    @api.model
    def revisit_question(self, question_id):
        question = self.env['opinion.question'].browse(question_id)
        if (fields.Datetime.now() - question.created_at).days >= 4*365:
            predictions = self.env['opinion.prediction'].search([('question_id', '=', question_id)])
            total_votes = len(predictions)
            if total_votes > 0:
                agreement_ratio = len(predictions.filtered(lambda p: p.answer in ['AGREE', 'DO_NOT_DISAGREE'])) / total_votes
                question.write({
                    'is_settled': agreement_ratio >= 0.8333334,
                    'last_revisited': fields.Datetime.now()
                })

    @api.model
    def explain_answer_choices(self):
        return """
        Answer choices explanation:
        1. I Agree: You fully support and believe in the statement.
        2. I do not disagree: You somewhat agree or have no strong objection to the statement.
        3. I do not agree: You somewhat disagree or have some reservations about the statement.
        4. I Disagree: You fully oppose or do not believe in the statement.
        """
