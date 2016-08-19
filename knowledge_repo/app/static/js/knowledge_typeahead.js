knowledgeTypeahead = (function(){

  var substringMatcher = function(pageMeta) {
      return function findMatches(q, syncResultFunction, asyncResultsFunction) {
        // an array that will be populated with substring matches
        var matches = [];

        // regex used to determine if a string contains the substring `q`
        var substrRegex = new RegExp(q, 'i');

        // iterate through the pool of strings and for any string that
        // contains the substring `q`, add it to the `matches` array
        $.each(pageMeta, function(i, meta) {
          var match = false;
          if (substrRegex.test(meta.title) || substrRegex.test(meta.author)){
            matches.push(meta);
          }
        });

        syncResultFunction(matches);
      };
    };

  function initializeSearchbarTypeahead(typeaheadPostInfo){
      $('#searchbar').typeahead({
        hint: false,
        highlight: true,
        minLength: 1
      },
      {
        name: 'knowledge_posts',
        display: function (item) {
          return item.title;
        },
        templates: {
          empty: Handlebars.compile(
            '<div class="tt-not-found">' +
              'Unable to find any posts that match the current query' +
              '</div>'
          ),
          suggestion: function(data) {
            return '<p><strong class="text-rausch">' + data.author + '</strong> – ' + data.title + '</p>';
          }
        },
        source: substringMatcher(typeaheadPostInfo)
      }
  );

    $('#searchbar').bind('typeahead:select', function(obj, datum, name) {
      window.location = '/render?markdown=' + encodeURIComponent(datum.path);
    });

    $('#searchbar').keypress(function(event){
      var keycode = event.keyCode || event.which;
      if(keycode === 13){
           var path = document.location.pathname;
           window.location = path + '?filters=' + $('#searchbar').val()
      }
    });

  }

  return {
    initializeSearchbarTypeahead: initializeSearchbarTypeahead
  }
}());
