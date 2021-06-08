# Copyright 2021 Camptocamp SA - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class EventMailRegistration(models.Model):
    _inherit = "event.mail.registration"

    def execute(self):
        # Override. Handle group_by_email
        if not self.env.context.get("group_by_email"):
            return super().execute()
        # Group by scheduler
        schedulers = self.mapped("scheduler_id")
        for scheduler in schedulers:
            # Scheduler mails
            mails_to_send = self.filtered(
                lambda mail: (
                    not mail.mail_sent
                    and mail.scheduler_id.id == scheduler.id
                    and mail.registration_id.state in ["open", "done"]
                    and mail.scheduler_id.notification_type == "mail"
                )
            )
            # Group by email
            email_to_mail_ids = {}
            for mail in mails_to_send:
                email = (
                    mail.registration_id.email
                    or mail.registration_id.partner_id.email
                    or False
                )
                email_to_mail_ids.setdefault(email, []).append(mail.id)
            # For groups without email, or groups with a single record, call super()
            single_mail_ids = []
            for email, mail_ids in list(email_to_mail_ids.items()):
                if not email or len(mail_ids) == 1:
                    single_mail_ids += mail_ids
                    del email_to_mail_ids[email]
            if single_mail_ids:
                super(
                    EventMailRegistration,
                    self.with_context(group_by_email=False).browse(single_mail_ids),
                ).execute()
            # Send email to groups
            for __, mail_ids in email_to_mail_ids.items():
                mails = self.browse(mail_ids)
                # Send email only to the first in the group
                main_mail = mails[0]
                main_mail.scheduler_id.template_id.with_context(
                    records=mails.mapped("registration_id")
                ).send_mail(main_mail.registration_id.id)
                # Post a note in the others
                reg_url = '<a href="#model=event.registration&id=%d">%s</a>'
                other_mails = mails - main_mail
                other_mails.mapped("registration_id").message_post(
                    body=_(
                        "Communication <b>%s</b> sent to attendee "
                        "with the same email: %s."
                    )
                    % (
                        mail.scheduler_id.template_id.display_name,
                        reg_url
                        % (
                            main_mail.registration_id.id,
                            main_mail.registration_id.display_name,
                        ),
                    )
                )
                # Mark all as sent
                mails.write({"mail_sent": True})
