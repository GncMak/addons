# Copyright 2021 Sygel - Manuel Regidor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, MAXYEAR
from dateutil import rrule
import pytz

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]
def _tz_get(self):
    return _tzs

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    salesperson_planner_visit_ids = fields.One2many(
        string="Salesperson Visits",
        comodel_name="crm.salesperson.planner.visit",
        inverse_name="calendar_event_id",
    )
    event_tz = fields.Selection('_event_tz_get', string='Timezone',
                                default=lambda self: self.env.context.get('tz') or self.user_id.tz)

    @api.model
    def _event_tz_get(self):
        return _tz_get(self)


    def write(self, values):
        if values.get("start") or values.get("user_id"):
            salesperson_visit_events = self.filtered(
                lambda a: a.res_model == "crm.salesperson.planner.visit"
            )
            if salesperson_visit_events:
                new_vals = {}
                if values.get("start"):
                    new_vals["date"] = values.get("start")
                if values.get("user_id"):
                    new_vals["user_id"] = values.get("user_id")
                    user_id = self.env["res.users"].browse(values.get("user_id"))
                    if user_id:
                        partner_ids = self.partner_ids.filtered(
                            lambda a: a != self.user_id.partner_id
                        ).ids
                        partner_ids.append(user_id.partner_id.id)
                        values["partner_ids"] = [(6, 0, partner_ids)]
                salesperson_visit_events.mapped(
                    "salesperson_planner_visit_ids"
                ).with_context(bypass_update_event=True).write(new_vals)
        return super(CalendarEvent, self).write(values)

    def unlink(self, can_be_deleted=True):
        if not self.env.context.get("bypass_cancel_visit"):
            salesperson_visit_events = self.filtered(
                lambda a: a.res_model == "crm.salesperson.planner.visit"
                and a.salesperson_planner_visit_ids
            )
            if salesperson_visit_events:
                error_msg = ""
                for event in salesperson_visit_events:
                    error_msg += _(
                        "Event %s is related to salesperson visit %s. "
                        "Cancel it to delete this event.\n"
                    ) % (event.name, event.salesperson_planner_visit_ids[0].name)
                raise ValidationError(error_msg)
        return super(CalendarEvent, self).unlink(can_be_deleted)

    @api.multi
    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        """ Adapt the value of start_date(time)/stop_date(time) according to start/stop fields and allday. Also, compute
            the duration for not allday meeting ; otherwise the duration is set to zero, since the meeting last all the day.
        """

        for meeting in self:
            if meeting.allday:
                meeting.start_date = meeting.start
                meeting.start_datetime = False
                meeting.stop_date = meeting.stop
                meeting.stop_datetime = False
                meeting.duration = 0.0
            else:
                meeting.start_date = self.start_date
                meeting.start_datetime = meeting.start
                meeting.stop_date = False
                meeting.stop_datetime = meeting.stop

                if not meeting.start:
                    meeting.start = fields.Datetime.now()
                meeting.stop_date = (
                            datetime.strptime(meeting.start, '%Y-%m-%d %H:%M:%S') + timedelta(hours=1)).strftime(
                    '%Y-%m-%d %H:%M:%S')
                meeting.stop = (datetime.strptime(meeting.start, '%Y-%m-%d %H:%M:%S') + timedelta(hours=1)).strftime(
                    '%Y-%m-%d %H:%M:%S')
                meeting.duration = self._get_duration(meeting.start, meeting.stop)

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        return super(models.Model, self).search(args)
        # if self._context.get('mymeetings'):
        #     args += [('partner_ids', 'in', self.env.user.partner_id.ids)]
        #
        # new_args = []
        # for arg in args:
        #     new_arg = arg
        #     if arg[0] in ('stop_date', 'stop_datetime', 'stop',) and arg[1] == ">=":
        #         if self._context.get('virtual_id', True):
        #             new_args += ['|', '&', ('recurrency', '=', 1), ('final_date', arg[1], arg[2])]
        #     elif arg[0] == "id":
        #         new_arg = (arg[0], arg[1], self.get_real_ids(arg[2]))
        #     new_args.append(new_arg)
        #
        # if not self._context.get('virtual_id', True):
        #     return super(CalendarEvent, self).search(new_args, offset=offset, limit=limit, order=order, count=count)
        #
        # if any(arg[0] == 'start' for arg in args) and \
        #         not any(arg[0] in ('stop', 'final_date') for arg in args):
        #     # domain with a start filter but with no stop clause should be extended
        #     # e.g. start=2017-01-01, count=5 => virtual occurences must be included in ('start', '>', '2017-01-02')
        #     start_args = new_args
        #     new_args = []
        #     for arg in start_args:
        #         new_arg = arg
        #         if arg[0] in ('start_date', 'start_datetime', 'start',):
        #             new_args += ['|', '&', ('recurrency', '=', 1), ('final_date', arg[1], arg[2])]
        #         new_args.append(new_arg)
        #
        # # offset, limit, order and count must be treated separately as we may need to deal with virtual ids
        # events = super(CalendarEvent, self).search(new_args, offset=0, limit=0, order=None, count=False)
        # events = self.browse(events.get_recurrent_ids(args, order=order))
        # if count:
        #     return len(events)
        # elif limit:
        #     return events[offset: offset + limit]
        # return events

    def _get_recurrent_date_by_event(self, date_field='start'):
        """ Get recurrent dates based on Rule string and all event where recurrent_id is child

        date_field: the field containing the reference date information for recurrence computation
        """
        self.ensure_one()
        if date_field in self._fields and self._fields[date_field].type in ('date', 'datetime'):
            reference_date = self[date_field]
        else:
            reference_date = self.start

        timezone = pytz.timezone(self.event_tz) if self.event_tz else pytz.timezone(self._context.get('tz') or 'UTC')
        event_date = pytz.UTC.localize(fields.Datetime.from_string(reference_date))  # Add "+hh:mm" timezone
        if not event_date:
            event_date = datetime.now()

        use_naive_datetime = self.allday and self.rrule and 'UNTIL' in self.rrule and 'Z' not in self.rrule
        if not use_naive_datetime:
            # Convert the event date to saved timezone (or context tz) as it'll
            # define the correct hour/day asked by the user to repeat for recurrence.
            event_date = event_date.astimezone(timezone)

        # The start date is naive
        # the timezone will be applied, if necessary, at the very end of the process
        # to allow for DST timezone reevaluation
        rset1 = rrule.rrulestr(str(self.rrule), dtstart=event_date.replace(tzinfo=None), forceset=True, ignoretz=True)

        recurring_meetings_ids = self.env.context.get('recurrent_siblings_cache', {}).get(self.id)
        if recurring_meetings_ids is not None:
            recurring_meetings = self.browse(recurring_meetings_ids)
        else:
            recurring_meetings = self.with_context(active_test=False).search([('recurrent_id', '=', self.id)])

        # We handle a maximum of 50,000 meetings at a time, and clear the cache at each step to
        # control the memory usage.
        invalidate = False
        for meetings in self.env.cr.split_for_in_conditions(recurring_meetings, size=50000):
            if invalidate:
                self.invalidate_cache()
            for meeting in meetings:
                recurring_date = fields.Datetime.from_string(meeting.recurrent_id_date)
                if use_naive_datetime:
                    recurring_date = recurring_date.replace(tzinfo=None)
                else:
                    if not recurring_date.tzinfo:
                        recurring_date = pytz.UTC.localize(recurring_date)
                    recurring_date = recurring_date.astimezone(timezone).replace(tzinfo=None)
                if date_field == "stop":
                    recurring_date += timedelta(hours=self.duration)
                rset1.exdate(recurring_date)
            invalidate = True

        def naive_tz_to_utc(d):
            return timezone.localize(d.replace(tzinfo=None), is_dst=True).astimezone(pytz.UTC)
        return [naive_tz_to_utc(d) if not use_naive_datetime else d for d in rset1 if d.year < MAXYEAR]