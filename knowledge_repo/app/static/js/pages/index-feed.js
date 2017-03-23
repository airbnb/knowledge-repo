(function($) {

    function em_to_px(parent, em) {
        return parseFloat(getComputedStyle(parent).fontSize) * em;
    }

    function posts_open(event) {
        var is_mac = navigator.platform.indexOf('Mac') != -1;
        if (is_mac && event.metaKey || !is_mac && event.ctrlKey) {
            window.open($(this).data('url'), '_blank');
        } else {
            window.location = $(this).data('url');
        }

    }

    function posts_expand_tldr(event) {
        event.stopPropagation();
        var tldr = $(this).parent().children('.feed-tldr');

        if (! tldr.data('expanded') ) {
            // Compute height of nested (and potentially masked elements) elements
            var height = $(tldr).children().map(function(undefined, elem) { return $(elem).outerHeight() + 5; }).toArray().reduce(function(prev, curr) { return prev + curr; }, 0);

            $(tldr).animate({"height": Math.max(height + 25, em_to_px(this, 5) + 5)}, 400);
            $(tldr).data('expanded', true);
            $(this).html('<a>- Show Less</a>');
        } else {
            $(tldr).animate({"height": em_to_px(this, 5) + 5}, 400);
            $(tldr).data('expanded', false);
            $(this).html('<a>+ Show More</a>');
        }
    }

    $("body").on("click", ".feed-post", posts_open);
    $("body").on("click", ".feed-post .feed-tldr-expander", posts_expand_tldr);

})(jQuery);
