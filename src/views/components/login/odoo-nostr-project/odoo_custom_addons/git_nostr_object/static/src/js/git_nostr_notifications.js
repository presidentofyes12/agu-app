// static/src/js/git_nostr_notifications.js
odoo.define('git_nostr_object.notifications', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var BusService = require('bus.BusService');

    BusService.include({
        _onNotification: function (notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                if (notification[0][1] === 'simple_notification') {
                    self.displayNotification({
                        title: notification[1].title,
                        message: notification[1].message,
                        type: 'info',
                    });
                }
            });
            this._super.apply(this, arguments);
        },
    });
});
