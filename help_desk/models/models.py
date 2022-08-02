# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError
from dateutil.relativedelta import relativedelta


class HdTeam(models.Model):
    _name = 'hd.team'
    # _rec_name = 'name'
    # _description = ''

    name = fields.Char(string="Name", required=True)
    team_leader_id = fields.Many2one(comodel_name="res.users", string="Team Leader", required=True)
    help_desk_manager_id = fields.Many2one(comodel_name="res.users", string="Help Desk Manager", required=True)
    member_ids = fields.Many2many('res.users', string='Team Members')


class HdTicket(models.Model):
    _name = 'hd.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ticket_id'

    @api.model
    def create(self, vals):
        if vals.get('ticket_id', _('New')) == _('New'):
            vals['ticket_id'] = self.env['ir.sequence'].next_by_code(
                'hd.ticket') or _('New')
        res = super(HdTicket, self).create(vals)
        return res

    ticket_id = fields.Char(string='Ticket ID', required=True, readonly=True, default=lambda self: _('New'))
    time_submitted = fields.Datetime(string="Time Submitted", required=False, readonly=True)
    description = fields.Text(string="Description", required=True, )
    team_id = fields.Many2one(comodel_name="hd.team", string="Team", required=False, )
    assign_to_id = fields.Many2one(comodel_name="res.users", string="", required=False, )
    priority = fields.Selection(string="Priority", selection=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                                required=False, )
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", required=True)
    customer_name = fields.Char(string="Customer Name", related='customer_id.name')
    customer_email = fields.Char(string="Customer Email", related='customer_id.email')
    customer_phone = fields.Char(string="Customer phone", related='customer_id.phone')
    tag_ids = fields.Many2many(comodel_name="tag.tag", string='Tags')
    hosting_type = fields.Selection(string="Hosting Type",
                                    selection=[('premise', 'On-premise'), ('cloud', 'Cloud')], required=True, )
    server_url = fields.Char(string="Server Url")
    resolution = fields.Datetime(string="Resolution", readonly=True)
    solved_date = fields.Datetime(string="Solved Date", required=False, readonly=True)
    state = fields.Selection(string="State", selection=[('new', 'New'),
                                                        ('inprogress', 'In Progress'),
                                                        ('solved', 'Solved'),
                                                        ('cancelled', 'Cancelled')]
                             , default='new', readonly=True)

    def action_inprogress(self):
        self.state = 'inprogress'
        self.time_submitted = datetime.datetime.now()

    def action_solved(self):
        self.state = 'solved'
        self.solved_date = datetime.datetime.now()
        if self.time_submitted and self.solved_date:
            day = relativedelta(self.solved_date, self.time_submitted).days
            print("FFFFFFFFFFFFFFFFFFFF", day)
            self.resolution = day

    def action_canelled(self):
        self.state = 'cancelled'

    def unlink(self):
        for check in self:
            if check.state not in ['new', 'cancelled']:
                raise UserError(_("You are not allowed to delete a ticket that is not new or cancelled!"))


class Tags(models.Model):
    _name = 'tag.tag'
    _rec_name = 'tag'
    # _description = ''

    tag = fields.Char(string="Tag", required=True)
