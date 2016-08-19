var helpersJx = (function(){
  var path = document.location.pathname

  function getParameterByName(name, url) {
    url = url || document.location.search;
    url = url.toLowerCase();
    name = name.replace(/[\[\]]/g, "\\$&").toLowerCase();
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)")
    var results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
  }

  function changePage(next_start, results, filters) {
    var newlocation = path + '?'
    if (path === '/tag_pages') {
      newlocation = newlocation + 'tag=' + getParameterByName('tag') + "&";
    }
    newlocation = newlocation + 'start=' + next_start.toString() + '&results=' + results.toString();
    if (filters && filters != 'None') {
      newlocation = newlocation + '&filters=' + filters;
    }
    document.location = newlocation;
  }

  function linkifyHeaders(){
    // Turn all headers to links (except h1, which is the title)
    var all_headers = [$("h2"), $("h3"), $("h4"), $("h5"), $("h6")]
    $.each(all_headers, function(index, value){
      $.each(value, function(i, v) {
        var inner_html = v.innerHTML;
        var inner_html_no_special = inner_html.replace(/[^a-zA-Z\- ]/g, "");
        var inner_link = "#" + inner_html_no_special.toLowerCase().split(" ").join("-");
        v.innerHTML = "<a href='" + inner_link + "' class=link-reset>" + inner_html + "</a>";
      })
    })
  }

  return {
    changePage: changePage,
    linkifyHeaders: linkifyHeaders,
  };
})();

