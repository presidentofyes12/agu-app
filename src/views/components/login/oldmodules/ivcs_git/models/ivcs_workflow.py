from odoo import models, fields, api
from odoo.exceptions import UserError

class IVCSWorkflow(models.Model):
    _name = 'ivcs.workflow'
    _description = 'IVCS Workflow'

    name = fields.Char('Workflow Name', required=True)
    description = fields.Text('Description')
    stage_ids = fields.One2many('ivcs.workflow.stage', 'workflow_id', string='Stages')

class IVCSWorkflowStage(models.Model):
    _name = 'ivcs.workflow.stage'
    _description = 'IVCS Workflow Stage'
    _order = 'sequence'

    name = fields.Char('Stage Name', required=True)
    workflow_id = fields.Many2one('ivcs.workflow', string='Workflow', required=True)
    sequence = fields.Integer('Sequence', default=10)

class IVCSItemWorkflow(models.Model):
    _name = 'ivcs.item.workflow'
    _description = 'IVCS Item Workflow'

    item_id = fields.Many2one('ivcs.item', string='Item', required=True)
    workflow_id = fields.Many2one('ivcs.workflow', string='Workflow', required=True)
    current_stage_id = fields.Many2one('ivcs.workflow.stage', string='Current Stage')

    def move_to_next_stage(self):
        self.ensure_one()
        current_sequence = self.current_stage_id.sequence
        next_stage = self.workflow_id.stage_ids.filtered(lambda s: s.sequence > current_sequence)
        if next_stage:
            self.current_stage_id = next_stage[0]
        else:
            raise UserError("This item is already at the final stage of the workflow.")
