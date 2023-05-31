odoo.define('hr_lunch.AutoFunction', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var web_client = require('web.web_client');

    function isDesiredDivPresent() {
        var desiredDiv = document.querySelector('.o_list_view.custom_tree_view');
        return desiredDiv !== null;
    }

    // Hook into the Odoo web client's initialization
    core.bus.on('web_client_ready', null, function () {

        // Check if the user is logged in
        if (session.uid && isDesiredDivPresent()) {

            // Check if the user has already pressed the "Ok" button
            var model = 'message.wizard';
            var field = 'show_wizard';

            session.rpc('/web/dataset/call_kw', {
                model: model,
                method: 'search_count',
                args: [[['user_id', '=', session.uid], [field, '=', true]]],
                kwargs: {}
            }).then(function (result) {
                if (result === 0) {
                    var action = {
                        action_id: 92, // self.env.ref('hr_lunch.view_message_wizard_form') 
                    };

                    session.rpc('/web/action/load', action).then(function (result) {
                        if (result) {
                            web_client.do_action(result);
                        }
                    });
                }
            });
        }
    });

});
