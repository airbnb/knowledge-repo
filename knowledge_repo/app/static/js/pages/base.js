$(document).ready(function() {
    $("#searchbar")[0].setSelectionRange(1000, 1000);

    $('#searchbar').typeahead({
        hint: false,
        highlight: true,
        minLength: 1
    }, {
        name: 'knowledge_posts',
        limit: 20,
        display: function(item) {
            return item.title + " - " + item.author;
        },
        templates: {
            empty: Handlebars.compile(
                '<div class="tt-not-found">' +
                'Unable to find any posts that match the current query' +
                '</div>'
            ),
            suggestion: function(data) {
                return '<p style="overflow-wrap:break-word">' + data.title + ' – <em>' + data.author + '</em></p>';
            }
        },
        source: function(q, sync, async) {
            $.ajax('/ajax/index/typeahead?search=' + q, {
                success: function(data, status) {
                    async(JSON.parse(data));
                }
            })
        }
    });


    $('#searchbar').bind('typeahead:select', function(obj, datum, name) {
        window.location = '/post/' + encodeURIComponent(datum.path);
    });

    $('#searchbar').keypress(function(event) {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == '13') {
            var path = document.location.pathname;
            window.location = '/feed?filters=' + $('#searchbar').val()
        }
    });

    var padding = $('.tt-menu').outerWidth()
    $('.tt-menu').width($('#searchbar').width() + padding + "px")


    function update_panel_widths(panel_name) {
        if (window.matchMedia( "(min-width: 1200px)" ).matches){
            $(panel_name).width($(panel_name).parent().width());
            $(panel_name).css("position", "fixed");
        } else {
            $(panel_name).width('auto');
            $(panel_name).css("position", "relative");
        }
    }

    update_panel_widths('#panel-left');
    update_panel_widths('#panel-right');
    $(window).resize(update_panel_widths.bind(null, '#panel-left'));
    $(window).resize(update_panel_widths.bind(null, '#panel-right'));
});
