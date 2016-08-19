var markdownJx = (function(){

  function escapeEquationBlocks(text, sep) {
    // input: string of markdown and/or latex
    // output: string of markdown and/or latex with underscores escaped
    var cleanText = '';
    var equationBlocks = text.split(sep);

    // when you split something like $$e^2$$ on $$
    // this turns into ["", e^2, ""]
    // every even index is whatever was in between the separator
    for (var i = 0; i < equationBlocks.length; i++) {
      if (i % 2 === 0) {
        // Add the latex to the clean text
        cleanText += equationBlocks[i];
      }
      else {
        // This escapes the underscores in equations correctly
        cleanText += equationBlocks[i].split('_').join('\\_');
      }
      cleanText += sep;
    }
    cleanText = cleanText.slice(0, (sep.length * -1));
    return cleanText;
  }

  function saveDraft(mode) {
    var markdownString = $('#markdown-text').val();
    if (markdownString === '') {
      return;
    }
    var postContent = {};
    postContent.content = markdownString;
    $.ajax({
        type: "POST",
        dataType: "json",
        data: JSON.stringify(postContent),
        contentType: "application/json",
        url: '/draft?draft={{ draft_id }}',
        async: true,
        success: function(response_data) {
          var draftId = response_data['draft_id'];
          if (mode === 'preview') {
            window.location = "/preview?draft=" + draftId;
          }
          else {
            window.location = "/editor?draft=" + draftId;
          }
        },
        error: function(response_data) {
          console.log("ERROR");
          console.log(JSON.stringify(response_data));
          alert("Your draft wasn't saved!");
        }
    });
  }

function refreshRenderedMarkdown() {
    var markdownString = $('#markdown-text').val();

    //escape underscores in equations
    var blocks = markdownString.split('```');
    markdownString = '';

    for (var i = 0; i < blocks.length; i++) {
      var block;
      if (i % 2 === 1) {
        block = blocks[i];
        markdownString += block + '```';
      }
      else {
        block = blocks[i];
        block = escapeEquationBlocks(block, '$$');
        block = escapeEquationBlocks(block, '$');
        markdownString += block;
        if (i !== blocks.length - 1) {
          markdownString += '```';
        }
      }
    }

    // Using async version of marked
    marked(markdownString, function (err, content) {
      if (err) throw err;
      //make sure images are not larger than the page
      content = content.split('<img ')
                       .join('<img style="max-width:100%"');
      //make tables look prettier:
      content = content.split('<table>')
                       .join('<table class="table table-striped table-condensed table-bordered">');
      content = content.split('<table class="dataframe">')
                       .join('<table class="table table-striped table-condensed table-bordered">');
      $('#rendered-markdown').html(content);
    });
    try {
      MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
    }
    catch (e) {
      console.log(e);
    }
  }

  var timeout = null;
  $("#markdown-text").on("input",function(e){
    if($(this).data("lastval")!== $(this).val()){
      $(this).data("lastval",$(this).val());

      $(this).height( 0 );
      $(this).height( this.scrollHeight );

      if (timeout !== null) {
        clearTimeout(timeout);
      }
      //if no new input is entered within 1 second, apply the filters
      timeout = setTimeout(function() {
        refreshRenderedMarkdown();
      }, 500);
    }
  });

  return {
    saveDraft: saveDraft,
    refreshRenderedMarkdown: refreshRenderedMarkdown
  };

}());
