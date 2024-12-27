from odoo import models, fields, api

class LoadQuestionsWizard(models.TransientModel):
    _name = 'load.questions.wizard'
    _description = 'Load Default Questions Wizard'

    @api.model
    def default_get(self, fields):
        res = super(LoadQuestionsWizard, self).default_get(fields)
        current_questions = self.env['opinion.question'].search_count([])
        res['current_question_count'] = current_questions
        return res

    current_question_count = fields.Integer(string="Current Number of Questions", readonly=True)

    def action_load_questions(self):
        self.env['opinion.question'].load_default_questions()
        new_question_count = self.env['opinion.question'].search_count([])
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Loaded {new_question_count - self.current_question_count} new questions.',
                'type': 'success',
                'sticky': False,
            }
        }
