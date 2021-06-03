# Copyright 2021 Camptocamp SA - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import _lang_get


class EventRegistration(models.Model):
    _inherit = "event.registration"

    lang = fields.Selection(
        selection=_lang_get,
        string="Language",
        compute="_compute_lang",
        readonly=False,
        store=True,
    )

    @api.depends("partner_id")
    def _compute_lang(self):
        for rec in self:
            if rec.partner_id:
                contact_id = rec.partner_id.address_get().get("contact", False)
                if contact_id:
                    contact = self.env["res.partner"].browse(contact_id)
                    if contact.lang:
                        rec.lang = contact.lang
