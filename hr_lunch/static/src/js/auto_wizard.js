odoo.define('hr_lunch.auto_wizard', function (require) {
    'use strict';

    console.log("KRAZY1"); 
    var FormController = require('web.FormController');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');

    var _t = core._t;
    console.log("KRAZY2"); 
    FormController.include({
        _onDataLoaded: function (record, fields, event) {
            // this._super.apply(this, arguments);
            rpc.query({
                model: 'message.wizard',
                method: 'open_existing_wizard',
                // args: [this.initialState.res_id],


            }).then(function (data) {
                console.log("KRAZY3"); 
            });
            
            // }).then(function (result) {

            //     var action = result;
            //     action.on_close = function () {
            //         // Handle close action if needed
            //         // ...
            //     };

            //     core.bus.trigger('do-action', {
            //         action: action,
            //     });

            // });
    
        },
    });
});
