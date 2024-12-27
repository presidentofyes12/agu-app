from odoo import models, fields, api
from datetime import datetime, timedelta
import json
import os

class Question(models.Model):
    _name = 'opinion.question'
    _description = 'Question Model'
    
    text = fields.Text(required=True)
    explanation = fields.Text()
    created_by = fields.Many2one('opinion.user')
    created_at = fields.Datetime(default=fields.Datetime.now)
    is_settled = fields.Boolean(default=False)
    last_revisited = fields.Datetime()
    predictions = fields.One2many('opinion.prediction', 'question_id')

    @api.model
    def revisit_questions(self):
        four_years_ago = datetime.now() - timedelta(days=4*365)
        questions = self.search([
            ('created_at', '<=', four_years_ago),
            ('is_settled', '=', False)
        ])
        for question in questions:
            predictions = question.predictions
            total_votes = len(predictions)
            if total_votes > 0:
                agreement_ratio = sum(1 for p in predictions if p.answer in ['agree', 'do_not_disagree']) / total_votes
                question.is_settled = agreement_ratio >= 0.8333334
                question.last_revisited = fields.Datetime.now()

    @api.model
    def load_default_questions(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'default_questions.json')
        with open(file_path, 'r') as file:
            data = json.load(file)
            default_questions = data['default_questions']
        
        for q in default_questions:
            existing_question = self.search([('text', '=', q['question'])], limit=1)
            if not existing_question:
                self.create({
                    'text': q['question'],
                    'explanation': q['explanation'],
                })

    @api.model
    def get_answer_options(self):
        return self.env['opinion.prediction'].get_answer_options()
