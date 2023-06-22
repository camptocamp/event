odoo.define("website_event_sale_check_order_before_payment.payment", function(require) {
    "use strict";

    const publicWidget = require("web.public.widget");

    publicWidget.registry.WebsiteSalePayment.include({
        /**
         * @override
         */
        start: function() {
            const res = this._super.apply(this, arguments);
            this.$payButton = $("button#o_payment_form_check_order_and_pay");
            this.$checkbox.trigger("change");
            return res;
        },
    });
});
