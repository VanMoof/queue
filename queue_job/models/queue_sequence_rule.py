# (c) 2022 Vanmoof <https://vanmoof.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models


class QueueSequenceRule(models.Model):
    """
    A model that defines rules for grouping and running queue jobs sequentially.

    A queue job is considered part of a sequence group if the value of the field specified in the `field_id`
    attribute is the same as the value of the field on the related record.

    Example:
        - If the `field_id` attribute is set to 'journal_id', jobs will be grouped and run sequentially
          if the invoices they are processing have the same journal.

    Don't confuse this with sequential queues. Those are simply channels with capacity 1, while this allows
    channels with a larger capacity and can conditionally run jobs in sequence.

    Attributes:
        name (str): The name of the rule.
        model_id (many2one): The name of the model for which the rule applies.
        field_id (many2one): The name of the field on the model used to group jobs.
    """
    _name = 'queue.sequence.rule'
    _description = 'Sequence rules for queue jobs'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True
    )
    field_id = fields.Many2one(comodel_name='ir.model.fields', string='Field', required=True,
                               domain="[('model_id', '=', model_id)]")

    _sql_constraints = [
        (
            "uniq_model_id",
            "UNIQUE(model_id)",
            ("Only one rule per model allowed"),
        ),
        (
            "uniq_name",
            "UNIQUE(name)",
            ("Rule name must be unique"),
        ),
    ]

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_id = False

    @api.constrains('model_id', 'field_id')
    def _check_field_belongs_to_model(self):
        for record in self:
            if record.field_id.model_id != record.model_id:
                raise ValueError(_('The selected field must belong to the selected model.'))
