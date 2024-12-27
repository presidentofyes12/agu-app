odoo.define('nostr_bridge.NostrClient', function (require) {
    "use strict";

    var Class = require('web.Class');

    var NostrClient = Class.extend({
        init: function (relayUrls) {
            this.relayUrls = relayUrls;
            this.relayPool = new NostrTools.RelayPool(this.relayUrls);
        },

        subscribe: function (filters, callback) {
            this.relayPool.subscribe(filters, callback);
        },

        publish: function (event) {
            this.relayPool.publish(event);
        }
    });

    return NostrClient;
});
