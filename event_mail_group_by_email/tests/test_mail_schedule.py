# Copyright 2021 Camptocamp SA - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common


class TestMailSchedule(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template_badge = cls.env.ref("event.event_registration_mail_template_badge")
        cls.template_subscription = cls.env.ref("event.event_subscription")
        cls.template_reminder = cls.env.ref("event.event_reminder")
        cls.event = cls.env["event.event"].create(
            {
                "name": "Test Event",
                "auto_confirm": False,
                "date_begin": fields.Datetime.now() + relativedelta(days=1),
                "date_end": fields.Datetime.now() + relativedelta(days=15),
            }
        )

    def _get_event_registrations_mails(self, registration):
        return self.env["mail.mail"].search(
            [("model", "=", "event.registration"), ("res_id", "in", registration.ids)]
        )

    def test_00_after_sub_grouped(self):
        # Configure event
        self.event.event_mail_ids = [
            (5, 0),
            (
                0,
                0,
                {
                    "interval_unit": "now",
                    "interval_type": "after_sub",
                    "group_by_email": True,
                    "template_id": self.template_badge.id,
                },
            ),
        ]
        # Create some registrations
        EventRegistration = self.env["event.registration"]
        reg_1 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Jon Snow",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        reg_2 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Samwell Tarly",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        reg_3 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Daenerys Targaryen",
                "email": "queen.of.everything@fire.io",
            }
        )
        # After registration confirmation, mails should be grouped
        registrations = reg_1 | reg_2 | reg_3
        registrations.confirm_registration()
        mails = self._get_event_registrations_mails(registrations)
        self.assertEqual(len(mails), 2, "Only two emails should've been sent")
        # Reg 1
        reg_1_mails = self._get_event_registrations_mails(reg_1)
        self.assertEqual(len(reg_1_mails), 1, "Reg 1 should've received 1 email.")
        self.assertEqual(
            len(reg_1_mails.attachment_ids), 2, "Both badges should be in the email."
        )
        # Reg 2
        reg_2_mails = self._get_event_registrations_mails(reg_2)
        self.assertEqual(
            len(reg_2_mails), 0, "Reg 2 shouldn't have received any email."
        )
        # Reg 3
        reg_3_mails = self._get_event_registrations_mails(reg_3)
        self.assertEqual(len(reg_3_mails), 1, "Reg 3 should've received 1 email.")
        self.assertEqual(
            len(reg_3_mails.attachment_ids), 1, "Only one badge in the email."
        )

    def test_01_after_sub_ungrouped(self):
        # Configure event
        self.event.event_mail_ids = [
            (5, 0),
            (
                0,
                0,
                {
                    "interval_unit": "now",
                    "interval_type": "after_sub",
                    "group_by_email": False,
                    "template_id": self.template_badge.id,
                },
            ),
        ]
        # Create some registrations
        EventRegistration = self.env["event.registration"]
        reg_1 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Jon Snow",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        reg_2 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Samwell Tarly",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        reg_3 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Daenerys Targaryen",
                "email": "queen.of.everything@fire.io",
            }
        )
        # Default behaviour is expected, no groupings
        registrations = reg_1 | reg_2 | reg_3
        registrations.confirm_registration()
        mails = self._get_event_registrations_mails(registrations)
        self.assertEqual(len(mails), 3, "3 emails should've been sent")
        # Reg 1
        reg_1_mails = self._get_event_registrations_mails(reg_1)
        self.assertEqual(len(reg_1_mails), 1, "Reg 1 should've received 1 email.")
        self.assertEqual(
            len(reg_1_mails.attachment_ids), 1, "One badge should be in the email."
        )
        # Reg 2
        reg_2_mails = self._get_event_registrations_mails(reg_2)
        self.assertEqual(len(reg_2_mails), 1, "Reg 2 should've received 1 email.")
        self.assertEqual(
            len(reg_2_mails.attachment_ids), 1, "One badge should be in the email."
        )
        # Reg 3
        reg_3_mails = self._get_event_registrations_mails(reg_3)
        self.assertEqual(len(reg_3_mails), 1, "Reg 3 should've received 1 email.")
        self.assertEqual(
            len(reg_3_mails.attachment_ids), 1, "One badge should be in the email."
        )

    def test_03_before_event_grouped(self):
        # Configure event
        self.event.event_mail_ids = [
            (5, 0),
            (
                0,
                0,
                {
                    "interval_nbr": 1,
                    "interval_unit": "days",
                    "interval_type": "before_event",
                    "group_by_email": True,
                    "template_id": self.template_badge.id,
                },
            ),
        ]
        # Create some registrations
        EventRegistration = self.env["event.registration"]
        reg_1 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Jon Snow",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        reg_2 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Samwell Tarly",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        # After registration confirmation, mails should be grouped
        registrations = reg_1 | reg_2
        registrations.confirm_registration()
        # Execute schedulers manually
        self.event.event_mail_ids.execute()
        # Check
        mails = self._get_event_registrations_mails(registrations)
        self.assertEqual(len(mails), 1, "Only one email should've been sent")
        # Reg 1
        reg_1_mails = self._get_event_registrations_mails(reg_1)
        self.assertEqual(len(reg_1_mails), 1, "Reg 1 should've received 1 email.")
        self.assertEqual(
            len(reg_1_mails.attachment_ids), 2, "Both badges should be in the email."
        )
        # Reg 2
        reg_2_mails = self._get_event_registrations_mails(reg_2)
        self.assertEqual(
            len(reg_2_mails), 0, "Reg 2 shouldn't have received any email."
        )

    def test_04_before_event_ungrouped(self):
        # Configure event
        self.event.event_mail_ids = [
            (5, 0),
            (
                0,
                0,
                {
                    "interval_nbr": 1,
                    "interval_unit": "days",
                    "interval_type": "before_event",
                    "group_by_email": False,
                    "template_id": self.template_badge.id,
                },
            ),
        ]
        # Create some registrations
        EventRegistration = self.env["event.registration"]
        reg_1 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Jon Snow",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        reg_2 = EventRegistration.create(
            {
                "event_id": self.event.id,
                "name": "Samwell Tarly",
                "email": "the.black.crow@nigthswatch.org",
            }
        )
        # After registration confirmation, mails should be grouped
        registrations = reg_1 | reg_2
        registrations.confirm_registration()
        # Execute schedulers manually
        self.event.event_mail_ids.execute()
        # Check
        mails = self._get_event_registrations_mails(registrations)
        self.assertEqual(len(mails), 2, "Two emails should've been sent")
        # Reg 1
        reg_1_mails = self._get_event_registrations_mails(reg_1)
        self.assertEqual(len(reg_1_mails), 1, "Reg 1 should've received 1 email.")
        self.assertEqual(
            len(reg_1_mails.attachment_ids), 1, "Only one badge should be in the email."
        )
        # Reg 2
        reg_2_mails = self._get_event_registrations_mails(reg_2)
        self.assertEqual(len(reg_2_mails), 1, "Reg 2 should've received 1 email.")
        self.assertEqual(
            len(reg_2_mails.attachment_ids), 1, "Only one badge should be in the email."
        )

    def test_05_onchange_event_type(self):
        event_type = self.env["event.type"].create(
            {
                "name": "Test Event Type",
                "event_type_mail_ids": [
                    (
                        0,
                        0,
                        {
                            "interval_unit": "now",
                            "interval_type": "after_sub",
                            "group_by_email": True,
                            "template_id": self.template_badge.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "interval_nbr": 1,
                            "interval_unit": "days",
                            "interval_type": "before_event",
                            "group_by_email": True,
                            "template_id": self.template_badge.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(len(self.event.event_mail_ids), 0)
        self.event.event_type_id = event_type.id
        self.event._onchange_type()
        self.assertEqual(len(self.event.event_mail_ids), 2)
        for mail in self.event.event_mail_ids:
            self.assertTrue(mail.group_by_email)
