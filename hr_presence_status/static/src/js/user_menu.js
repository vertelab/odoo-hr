odoo.define('hr_presence_status.UserMenu', function(require) {
    "use strict";

    /**
     * This widget is appended by the webclient to the right of the navbar.
     * It displays the avatar and the name of the logged user (and optionally the
     * db name, in debug mode).
     * If clicked, it opens a dropdown allowing the user to perform actions like
     * editing its preferences, accessing the documentation, logging out...
     */

    var config = require('web.config');
    var core = require('web.core');
    var framework = require('web.framework');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var WebUserMenu = require('web.UserMenu');

    var _t = core._t;
    var QWeb = core.qweb;

    WebUserMenu.include({

        start: function() {
            var self = this;
            var session = this.getSession();
            console.log('session', session);
            this.$el.on('click', '[data-menu]', function(ev) {
                ev.preventDefault();
                var menu = $(this).data('menu');
                self['_onMenu' + menu.charAt(0).toUpperCase() + menu.slice(1)]();
            });
            return this._super.apply(this, arguments).then(function() {
                var $avatar = self.$('.oe_topbar_avatar');
                if (!session.uid) {
                    $avatar.attr('src', $avatar.data('default-src'));
                    return Promise.resolve();
                }
                var topbar_name = session.name;
                if (config.isDebug()) {
                    topbar_name = _.str.sprintf("%s (%s)", topbar_name, session.db);
                }
                self.$('.oe_topbar_name').text(topbar_name);
                var avatar_src = session.url('/web/image', {
                    model: 'res.users',
                    field: 'image_128',
                    id: session.uid,
                });
                $avatar.attr('src', avatar_src);

                var $status = self.$('.oe_topbar_status');
                console.log('$status', $status);

                self._rpc({
                    route: '/get/status',
                    params: {
                        model: 'res.partner',
                        field: 'im_status',
                        partner_id: session.partner_id,
                    }
                }).then(function(result) {
                    if (result === 'online') {
                        $status.removeClass('fa fa-plane');
                        $status.addClass('fa fa-circle').css('color', '#28a745 !important');
                        $status.attr('title', 'Online');
                        $status.attr('aria-label', 'User is Online');

                    } else {
                        $status.removeClass('fa fa-circle');
                        $status.addClass('fa fa-plane').css('color', '#adb5bd !important');
                        $status.attr('title', 'Offline');
                        $status.attr('aria-label', 'User is Offline'); // #ffac00
                    }
                });
            });
        },

        _onMenuImstatus: function() {
            var self = this;
            var session = this.getSession();
            console.log('session im status', session);
            self._rpc({
                route: '/set/status',
                params: {
                    model: 'res.partner',
                    field: 'im_status',
                    partner_id: session.partner_id,
                }
            })
        },
    });

});