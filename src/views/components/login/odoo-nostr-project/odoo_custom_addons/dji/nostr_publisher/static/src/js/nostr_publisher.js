odoo.define('nostr_publisher.nostr_publisher', function (require) {
    "use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var _t = core._t;

    var NostrPublisherListController = ListController.extend({
        buttons_template: 'NostrPublisherListView.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_test_relays': '_onTestRelays',
            'click .o_button_update_active_relays': '_onUpdateActiveRelays',
        }),

        _onTestRelays: function () {
            var self = this;
            this._rpc({
                model: 'nostr.publisher',
                method: 'action_test_relays',
                args: [[]],
            }).then(function () {
                self.do_notify(_t("Success"), _t("Relay test initiated."));
            }).guardedCatch(function (error) {
                self.do_warn(_t("Error"), _t("Failed to initiate relay test."));
            });
        },

        _onUpdateActiveRelays: function () {
            var self = this;
            this._rpc({
                model: 'nostr.publisher',
                method: 'update_active_relays',
                args: [[]],
            }).then(function () {
                self.do_notify(_t("Success"), _t("Active relays updated."));
            }).guardedCatch(function (error) {
                self.do_warn(_t("Error"), _t("Failed to update active relays."));
            });
        },
    });

    var NostrPublisherListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: NostrPublisherListController,
        }),
    });

    viewRegistry.add('nostr_publisher_list', NostrPublisherListView);

    return {
        NostrPublisherListController: NostrPublisherListController,
        NostrPublisherListView: NostrPublisherListView,
    };
});
