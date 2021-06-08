# Copyright 2021 Camptocamp SA - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class EventEvent(models.Model):
    _inherit = "event.event"

    def mail_attendees(
        self,
        template_id,
        force_send=False,
        filter_func=lambda self: self.state != "cancel",
    ):
        # Override. Group by email when context key is present
        if not self.env.context.get("group_by_email"):
            return super().mail_attendees(
                template_id, force_send=force_send, filter_func=filter_func
            )
        template = self.env["mail.template"].browse(template_id)
        for event in self:
            attendees = event.registration_ids.filtered(filter_func)
            # Group by email
            email_to_attendee_ids = {}
            for attendee in attendees:
                email = attendee.email or attendee.partner_id.email or False
                email_to_attendee_ids.setdefault(email, []).append(attendee.id)
            # Identify groups without email or groups with only 1 attendee
            # and simply send them the email (ungruped)
            # Otherwise, send the email only to one of them, and post a note in others.
            for email, attendee_ids in email_to_attendee_ids.items():
                if not email or len(attendee_ids) == 1:
                    for attendee_id in attendee_ids:
                        template.send_mail(attendee_id, force_send=force_send)
                else:
                    group_attendees = self.env["event.registration"].browse(
                        attendee_ids
                    )
                    main_attendee = group_attendees[0]
                    # Send email to main attendee
                    template.with_context(records=group_attendees).send_mail(
                        main_attendee.id, force_send=force_send
                    )
                    # Post a note in the others
                    reg_url = '<a href="#model=event.registration&id=%d">%s</a>'
                    other_attendees = group_attendees - main_attendee
                    other_attendees.message_post(
                        body=_(
                            "Communication <b>%s</b> sent to attendee "
                            "with the same email: %s."
                        )
                        % (
                            template.display_name,
                            reg_url % (main_attendee.id, main_attendee.display_name),
                        )
                    )
