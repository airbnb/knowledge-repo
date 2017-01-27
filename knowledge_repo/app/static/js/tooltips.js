var tooltipsJx = (function(){

function initializeTooltips(post_id){
    var post_id = encodeURI(post_id);
    var raw_tooltip = $("#tooltip-raw");

    if (raw_tooltip[0] !== null){
        raw_tooltip.click(function() {
            document.location.href = "/post/" + post_id + "?render=raw";
        });
    };

    var like_tooltip = $("#tooltip-like");

    if (like_tooltip[0] !== null){
        $("#tooltip-like").click(function() {
            $.ajax({
                type: "GET",
                url: '/like?post_id=' + post_id,
                async: false
            });
            location.reload();
        });
    }

    var unlike_tooltip = $("#tooltip-unlike");

    if (unlike_tooltip[0] !== null){
        $("#tooltip-unlike").click(function() {
            $.ajax({
                type: "GET",
                url: '/unlike?post_id=' + post_id,
                async: false
            });
        location.reload();
     });
   }
}

return  {
    initializeTooltips: initializeTooltips,
}
})();
