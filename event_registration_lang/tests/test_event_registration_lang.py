# Copyright 2021 Camptocamp SA - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestEventRegistrationLang(SavepointCase):
    def setUp(self):
        super().setUp()
        self.event = self.env.ref("event.event_0")
        self.partner = self.env.ref("base.res_partner_1")

    def test_01_onchange(self):
        registration = self.env["event.registration"].create(
            {"event_id": self.event.id, "partner_id": self.partner.id}
        )
        self.assertEqual(self.partner.lang, registration.lang)
