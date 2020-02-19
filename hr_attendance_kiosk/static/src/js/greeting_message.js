odoo.define('hr_attendance_kiosk.greeting_message', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var GreetingMessage = require('hr_attendance.greeting_message');
var MyAttendances = require('hr_attendance.my_attendances');
var _t = core._t;

// welcome_message & farewell_message is the 2 functions edited, just translations from English to Swedish.
GreetingMessage.include({
	
    welcome_message: function() {
        var self = this;
        var now = this.attendance.check_in.clone();
        this.return_to_main_menu = setTimeout( function() { self.do_action(self.next_action, {clear_breadcrumbs: true}); }, 5000);

        if (now.hours() < 5) {
            this.$('.o_hr_attendance_message_message').append(_t("God natt"));
        } else if (now.hours() < 12) {
            if (now.hours() < 8 && Math.random() < 0.3) {
                if (Math.random() < 0.75) {
                    this.$('.o_hr_attendance_message_message').append(_t("Den som sätter igång först når mest framgång"));
                } else {
                    this.$('.o_hr_attendance_message_message').append(_t("Först till kvarn"));
                }
            } else {
                this.$('.o_hr_attendance_message_message').append(_t("God morgon"));
            }
        } else if (now.hours() < 17){
            this.$('.o_hr_attendance_message_message').append(_t("God eftermiddag"));
        } else if (now.hours() < 23){
            this.$('.o_hr_attendance_message_message').append(_t("God kväll"));
        } else {
            this.$('.o_hr_attendance_message_message').append(_t("God natt"));
        }
        if(this.previous_attendance_change_date){
            var last_check_out_date = this.previous_attendance_change_date.clone();
            if(now - last_check_out_date > 24*7*60*60*1000){
                this.$('.o_hr_attendance_random_message').html(_t("Kul att se dig igen, det var ett tag sedan!"));
            } else {
                if(Math.random() < 0.02){
                    this.$('.o_hr_attendance_random_message').html(_t("Om något är värt att göra, är det värt att göra det bra!"));
                }
            }
        }
    },

    farewell_message: function() {
        var self = this;
        var now = this.attendance.check_out.clone();
        this.return_to_main_menu = setTimeout( function() { self.do_action(self.next_action, {clear_breadcrumbs: true}); }, 5000);

        if(this.previous_attendance_change_date){
            var last_check_in_date = this.previous_attendance_change_date.clone();
            if(now - last_check_in_date > 1000*60*60*12){
                this.$('.o_hr_attendance_warning_message').show().append(_t("<b>Varning! Senaste check in var över 12 timmar sedan.</b><br/>Om detta inte stämmer, var vänligen kontakta HR"));
                clearTimeout(this.return_to_main_menu);
                this.activeBarcode = false;
            } else if(now - last_check_in_date > 1000*60*60*8){
                this.$('.o_hr_attendance_random_message').html(_t("Ännu ett bra arbetspass! Ses snart!"));
            }
        }

        if (now.hours() < 12) {
            this.$('.o_hr_attendance_message_message').append(_t("Ha en trevlig dag!"));
        } else if (now.hours() < 14) {
            this.$('.o_hr_attendance_message_message').append(_t("Ha en trevlig lunch!"));
            if (Math.random() < 0.05) {
                this.$('.o_hr_attendance_random_message').html(_t("Ät frukost som en kung, lunch som en affärsman och kvällsmat som en tiggare"));
            } else if (Math.random() < 0.06) {
                this.$('.o_hr_attendance_random_message').html(_t("Ett äpple om dagen är bra för magen"));
            }
        } else if (now.hours() < 17) {
            this.$('.o_hr_attendance_message_message').append(_t("Ha en god eftermiddag"));
        } else {
            if (now.hours() < 18 && Math.random() < 0.2) {
                this.$('.o_hr_attendance_message_message').append(_t("Morgonstund har guld i mun"));
            } else {
                this.$('.o_hr_attendance_message_message').append(_t("Ha en trevlig kväll"));
            }
        }
    }
});

MyAttendances.include({
	base_url: function() {
		var self = this;
		var base_url;
		
		var def = this._rpc({
				model: 'ir.config_parameter',
				method: 'get_param',
				args: ['hr_attendance_kiosk.base_url'],
			})
			.then(function (res) {
				base_url = res;
			}, function(){
				base_url = '';
				}
			);
		
		while(base_url === undefined){
			
		}
		return base_url;
	}
});


return GreetingMessage;

});
