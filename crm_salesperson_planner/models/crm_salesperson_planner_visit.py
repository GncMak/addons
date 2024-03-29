# Copyright 2021 Sygel - Valentin Vinagre
# Copyright 2021 Sygel - Manuel Regidor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError


class CrmSalespersonPlannerVisit(models.Model):
    _name = "crm.salesperson.planner.visit"
    _description = "Salesperson Planner Visit"
    _order = "date desc,sequence"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Visit Number", required=True, default="/", readonly=True, copy=False)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer", required=True)
    partner_phone = fields.Char(string="Phone", related="partner_id.phone")
    partner_mobile = fields.Char(string="Mobile", related="partner_id.mobile")
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True,)
    sequence = fields.Integer(
        string="Sequence",
        help="Used to order Visits in the different views",
        default=20,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.company_id,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Machine Model",
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Serial No",
    )
    signature = fields.Binary(string="Signature")
    signature_filename = fields.Char(string="Signature File Name")
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
        domain=lambda self: [
            ("groups_id", "in", self.env.ref("sales_team.group_sale_salesman").id)
        ],
    )

    @api.model
    def _compute_form_line(self):
        form_lines = self.env['crm.salesperson.planner.maintenance.application.steps'].search([('active', '=', True)])
        a = []
        for fl in form_lines:
            fl_vals = {
                "maintenance_application_steps_id": fl.id,
                "company_id": 1,
                "measured": 0,
                "corrected": 0,
                "notes": "",
            }
            a.append(fl_vals)
        return a

    form_line_ids = fields.One2many(
        comodel_name='crm.salesperson.planner.checkup.application.form.line',
        inverse_name='visit_id',
        string='Checkup Application Form Line', default=_compute_form_line,
    )
    description = fields.Html(string="Description")
    state = fields.Selection(
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        selection=[
            ("draft", "Draft"),
            ("confirm", "Validated"),
            ("done", "Visited"),
            ("cancel", "Cancelled"),
            ("incident", "Incident"),
        ],
        default="draft",
    )
    close_reason_id = fields.Many2one(
        comodel_name="crm.salesperson.planner.visit.close.reason", string="Close Reason"
    )
    close_reason_image = fields.Binary(attachment=True, string="Close Reason Image", max_width=1024, max_height=1024)
    close_reason_notes = fields.Text(string="Close Reason Notes")
    visit_template_id = fields.Many2one(
        comodel_name="crm.salesperson.planner.visit.template", string="Visit Template"
    )
    calendar_event_id = fields.Many2one(
        comodel_name="calendar.event", string="Calendar Event"
    )

    _sql_constraints = [
        (
            "crm_salesperson_planner_visit_name",
            "UNIQUE (name)",
            "The visit number must be unique!",
        ),
    ]

    @api.model
    def create(self, vals):
        name_add = True
        seq = self.env["ir.sequence"].next_by_code("salesperson.planner.visit")
        for val in vals:
            if 'name' == val:
                if val.get("name") == "/":
                    val.update({'name': seq})
                    name_add = False
        if name_add:
            vals.update({"name": seq})
        return super(CrmSalespersonPlannerVisit, self).create(vals)

    def action_draft(self):
        if self.state not in ["cancel", "incident", "done"]:
            raise ValidationError(
                _("The visit must be in cancelled, incident or visited state")
            )
        if self.calendar_event_id:
            self.calendar_event_id.with_context(bypass_cancel_visit=True).unlink()
        self.write({"state": "draft"})

    def action_confirm(self):
        if self.filtered(lambda a: not a.state == "draft"):
            raise ValidationError(_("The visit must be in draft state"))
        events = self.create_calendar_event()
        if events:
            self.browse(events.mapped("res_id")).write({"state": "confirm"})

    def action_done(self):
        if not self.state == "confirm":
            raise ValidationError(_("The visit must be in confirmed state"))
        self.write({"state": "done"})

    def action_cancel(self, reason_id, image=None, notes=None):
        if self.state not in ["draft", "confirm"]:
            raise ValidationError(_("The visit must be in draft or validated state"))
        if self.calendar_event_id:
            self.calendar_event_id.with_context(bypass_cancel_visit=True).unlink()
        self.write(
            {
                "state": "cancel",
                "close_reason_id": reason_id.id,
                "close_reason_image": image,
                "close_reason_notes": notes,
            }
        )

    def create_calendar_event(self):
        events = self.env["calendar.event"]
        model_id = self.env.ref(
            "crm_salesperson_planner.model_crm_salesperson_planner_visit"
        ).id
        for sel in self:
            event_vals = {
                "name": sel.name,
                "partner_ids": [(6, 0, [sel.partner_id.id, sel.user_id.partner_id.id])],
                "user_id": sel.user_id.id,
                "start_date": sel.date,
                "stop_date": sel.date,
                "start": sel.date,
                "stop": sel.date,
                "allday": True,
                "res_model_id": model_id,
                "res_id": sel.id,
            }
            event = self.env["calendar.event"].create(event_vals)
            if event:
                event.activity_ids.unlink()
                event.write({"res_model": "crm.salesperson.planner.visit"})
                sel.write({"calendar_event_id": event.id})
            events += event
        return events

    def action_incident(self, reason_id, image=None, notes=None):
        if self.state not in ["draft", "confirm"]:
            raise ValidationError(_("The visit must be in draft or validated state"))
        self.write(
            {
                "state": "incident",
                "close_reason_id": reason_id.id,
                "close_reason_image": image,
                "close_reason_notes": notes,
            }
        )

    def unlink(self):
        if any(sel.state not in ["draft", "cancel"] for sel in self):
            raise ValidationError(_("Visits must be in cancelled state"))
        return super(CrmSalespersonPlannerVisit, self).unlink()

    def write(self, values):
        ret_val = super(CrmSalespersonPlannerVisit, self).write(values)
        if (values.get("date") or values.get("user_id")) and not self.env.context.get(
            "bypass_update_event"
        ):
            new_vals = {}
            for sel in self.filtered(lambda a: a.calendar_event_id):
                if values.get("date"):
                    new_vals["start"] = values.get("date")
                    new_vals["stop"] = values.get("date")
                if values.get("user_id"):
                    new_vals["user_id"] = values.get("user_id")
                sel.calendar_event_id.write(new_vals)
        return ret_val
