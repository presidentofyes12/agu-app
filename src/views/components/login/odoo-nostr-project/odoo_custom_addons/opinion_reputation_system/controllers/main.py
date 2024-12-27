from odoo import http
from odoo.http import request

class OpinionController(http.Controller):

    @http.route('/api/register', type='json', auth='public')
    def register(self, name):
        user = request.env['opinion.user'].sudo().create({'name': name})
        return {'id': user.id, 'name': user.name}

    @http.route('/api/questions', type='json', auth='public')
    def get_questions(self):
        questions = request.env['opinion.question'].sudo().search([])
        return [{
            'id': q.id,
            'text': q.text,
            'explanation': q.explanation,
            'is_settled': q.is_settled
        } for q in questions]

    @http.route('/api/predict', type='json', auth='public')
    def predict(self, user_id, question_id, answer, confidence):
        prediction = request.env['opinion.prediction'].sudo().create({
            'user_id': user_id,
            'question_id': question_id,
            'answer': answer,
            'confidence': confidence
        })
        return {
            'id': prediction.id,
            'user_id': prediction.user_id.id,
            'question_id': prediction.question_id.id
        }

    @http.route('/api/user_reputation', type='json', auth='public')
    def get_user_reputation(self, user_id):
        user = request.env['opinion.user'].sudo().browse(user_id)
        return {'reputation': user.reputation}
