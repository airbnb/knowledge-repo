var postEditorJx = (function() {

    function urlExists(url) {
        var http = new XMLHttpRequest();
        http.open('HEAD', url, false);
        try {
            http.send();
        } catch(err) {
            console.log(err)
        }
            return http.status !== 404;
    }


    function parseDate(ds, errorName) {
      var parsedDate = ds.split("-");
      var errorMessage = errorName  + " is not in the right format. \
                          Make sure it's YYYY-mm-dd! Your post was not saved, please try again";
      if (parsedDate.length !== 3) {
        alert(errorMessage);
        return false;
      }
      var year = parsedDate[0].trim();
      var month = parsedDate[1].trim();
      var day = parsedDate[2].trim();
      if (year.length !== 4) {
        alert(errorMessage);
        return false;
      }

      if (parseInt(month) <= 0 || parseInt(month) >= 13) {
        alert(errorMessage);
        return false;
      }

      if (parseInt(day) <= 0 || parseInt(day) >= 32) {
        alert(errorMessage);
        return false;
      }

      return true;
    }


    function validatePost(typeahead_post_info, status){
        var saveButton = $("#btn_save")[0];
        saveButton.setAttribute("class", "btn btn-large btn-primary");
        var error = false;

        var title = $("#post_title")[0].value;
        var project = $('#post_project').typeahead('val');
        // Currently, the tags from the post_tags are in a list
        var tags = $("#post_tags").select2().val();
        var tldr = $("#post_tldr")[0].value;
        var createdAt = $("#post_created_at")[0].value;
        var updatedAt = $("#post_updated_at")[0].value;
        var author = $("#post_author")[0].value;
        var markdown = $("#post_text")[0].value;
        var feedImage = $("#post_image_feed")[0].value;

        if (title === '' || project === '' || tags === [] ||
            tldr === '' || author === '' || markdown === ''){
                alert("One of the fields was left empty! Your post was not saved, please try again");
                error = true;
        } else {
            // check to make sure the user didn't create another project
            if (typeahead_post_info.indexOf(project) === -1 && is_editor === 0) {
                error_message = "Please do not create another project, use an existing one.\n" +
                                "Your post was not saved, please try again. ";
                alert(error_message);
                error = true;
            }
        }


        if (feedImage === '') {
            feedImage = '/static/images/default_thumbnail.png';
        }

        if (!urlExists(feedImage)) {
            alert("Could not find image. Your post was not saved, please try again.");
            error = true;
        }

        // check the tags of the post
        $.each(tags, function(i, tag) {
            tag = tag.trim();
            if (tag[0] !== '#') {
                alert("The tag: " + tag + " needs a pound sign in front of it. Your post was not saved, please try again.");
                error = true;
            } else {
                if (tag.split("/").length === 1) {
                    alert("The tag: " + tag + " needs to have a / to separate the tag_type and tag_name.\n" +
                        "Your post was not saved try again");
                    error = true;
                }
            }
        })

        var tagsString = tags.join(",");

        // Check the dates
        checkCreatedAt = parseDate(createdAt, "Created_At");
        checkUpdatedAt = parseDate(updatedAt, "Updated_At");
        if (!checkCreatedAt || !checkUpdatedAt){
            error = true;
        }

        postContent = {
            'title': title,
            'project': project,
            'feed_image': feedImage,
            'tags': tagsString,
            'tldr': tldr,
            'status': status,
            'created_at': createdAt,
            'updated_at': updatedAt,
            'author': author,
            'markdown': encodeURIComponent(markdown)
        }


        return {
            'postContent': postContent,
            'error': error
        }

 }


    return {
        validatePost: validatePost
    };

}());
