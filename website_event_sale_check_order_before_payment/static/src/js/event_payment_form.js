odoo.define(
    "website_event_sale_check_order_before_payment.event_payment_form",
    function(require) {
        "use strict";

        var paymentForm = require("payment.payment_form");
        const core = require("web.core");
        const _t = core._t;

        paymentForm.include({
            /**
             * @override
             */
            // eslint-disable-next-line no-unused-vars
            payEvent: async function(ev) {
                // This._super only works before any await operation, so store it here
                const _super = this._super;
                const order_validity_data = await this._rpc({
                    route: "/shop/payment/order_validity",
                    params: [],
                });
                if (order_validity_data.order_is_valid) {
                    return _super.apply(this, arguments);
                }
                this.displayError(
                    _t("The payment can't be processed"),
                    _t(order_validity_data.invalid_order_message || "Unexpected error")
                );
                return;
            },
        });
    }
);
