var tooltipsJx = (function(){

function initializeTooltips(is_webeditor, post_id, id, data_repo_github_root){
    var view_tooltip = $("#tooltip-view");
    var post_id = encodeURI(post_id);

    if (view_tooltip[0] !== null){
       view_tooltip.click(function() {
            document.location.href = "/render?markdown=" + post_id;
        });
    };

   var raw_tooltip = $("#tooltip-raw");

   if (raw_tooltip[0] !== null){
        raw_tooltip.click(function() {
            document.location.href = "/raw?markdown=" + post_id;
        });
    };

    var edit_tooltip = $("#tooltip-edit");

    if (edit_tooltip[0] !== null){
        edit_tooltip.click(function(){
          document.location.href =  "/posteditor?post_id=" + id;
        });
    }

    var presentation_tooltip = $("#tooltip-presentation");

    if (presentation_tooltip[0] !== null){
        presentation_tooltip.click(function() {
            document.location.href = "/presentation?markdown=" + post_id;
        });
    }

    var github_tooltip = $("#tooltip-ghe");

    if (github_tooltip[0] !== null){
        github_tooltip.click(function() {
            document.location.href = github_tooltip.attr('data-weburi');
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
