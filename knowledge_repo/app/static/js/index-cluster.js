var indexClusterJx = (function(){

  function addFoldingToGroups() {
    $('.cluster_dir').click(function(e) {
      e.stopPropagation();
      var icon = $(this).find("#" + this.id + "-glyph");
      $(icon).toggleClass("glyphicon-chevron-right glyphicon-chevron-down");
      $(this).siblings("#" + this.id + "-content").toggle("fold");
    });
  }

  function clickTag(tag) {
    if (tag.length > 0) {
      tagId = tag.replace("/", "__");
      $("#" + tagId).trigger("click");
      document.location = "#" + tag;
    }
  }

  function formatButtons(clusterSelected, clusterButtons, sortSelected, sortButtons) {
    $(clusterSelected)[0].setAttribute("checked", "checked");
    $(sortSelected)[0].setAttribute("checked", "checked");

    $.each(clusterButtons, function(i, button) {
      $("#" + button).click(function() {
        clusterSelected = '#' + (this).id;
        $(clusterSelected)[0].setAttribute("checked", "checked");
        if (sortSelected !== '') {
            refreshPage(clusterSelected, sortSelected);
        }
      });
    });

    $.each(sortButtons, function(i, button) {
      $("#" + button).click(function() {
          sortSelected = '#' + (this).id;
          $(sortSelected)[0].setAttribute("checked", "checked")
          if (clusterSelected !== '') {
              refreshPage(clusterSelected, sortSelected);
          }
        });
    });
  }

  function getClusterSelected(clusterSelected) {
    if (clusterSelected.length === 0) {
      clusterSelected = "clusterFolder";
    }
    return clusterSelected;
  }

  function getSortSelected(sortSelected) {
    if (sortSelected.length === 0) {
      sortSelected = "sortAlpha";
    }
    return sortSelected;
  }

  function refreshPage(clusterSelected, sortSelected) {
    var cluster = clusterSelected.replace('#', '')
                                 .replace('cluster', '')
                                 .toLowerCase();
    var sort = sortSelected.replace('#', '')
                           .replace('sort', '')
                           .toLowerCase();
    var filter_var = $('#searchbar').val();
    var loc = '/cluster?group_by=' + cluster + '&sort_by=' + sort;
    if (sort === "alpha") {
      loc += "&sort_asc=1";
    }
    if (filter_var !== '') {
      loc += '&filters=' + filter_var;
    }
    document.location = loc;
  }


  return {
    addFoldingToGroups: addFoldingToGroups,
    clickTag: clickTag,
    refreshPage: refreshPage,
    getClusterSelected: getClusterSelected,
    getSortSelected: getSortSelected,
    formatButtons: formatButtons
  };
}());
