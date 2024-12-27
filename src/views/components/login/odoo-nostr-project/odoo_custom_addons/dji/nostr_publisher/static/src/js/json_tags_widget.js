odoo.define('nostr_publisher.json_tags_widget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');

    var JsonTagsWidget = AbstractField.extend({
        template: 'JsonTagsWidget',
        events: {
            'click .tag .remove': '_onTagRemove',
        },

        _renderEdit: function () {
            this.$el.empty();
            var tags = JSON.parse(this.value || '[]');
            var $tagList = $('<div class="tag-list"></div>');
            tags.forEach(function (tag) {
                $tagList.append($('<span class="tag badge badge-primary">' + 
                                  tag[0] + ': ' + tag[1] + 
                                  '<span class="remove">&times;</span></span>'));
            });
            this.$el.append($tagList);
        },

        _onTagRemove: function (ev) {
            var $tag = $(ev.currentTarget).closest('.tag');
            var tagText = $tag.text().trim().slice(0, -1);  // Remove the '×' character
            var [key, value] = tagText.split(':').map(s => s.trim());
            var tags = JSON.parse(this.value || '[]');
            tags = tags.filter(tag => !(tag[0] === key && tag[1] === value));
            this._setValue(JSON.stringify(tags));
        },
    });

    registry.add('json_tags', JsonTagsWidget);

    return JsonTagsWidget;
});
