var tagsJx = (function () {

  function deleteTagPosts(tag) {
    tag.addEventListener('click', function () {
      var tagList = tag.id.split('__');
      var tagId = tagList[1];
      var urlRequest = 'delete_tag_post?tag_id=' + tagId;
      $.ajax({
        type: 'GET',
        url: urlRequest,
        async: false
      });
      location.reload();
    });
  }

  function renameTagPosts(tag) {
    tag.addEventListener('click', function () {
      var oldTagList = this.id.split('__');
      var oldTagId = oldTagList[1]
      var newTagForm = $('#' + oldTagId + '__new_tag_name')[0];
      var newTagName = newTagForm.value;
      var urlRequest = '/rename_tag';
      var tagData = {};
      tagData.oldTagId = oldTagId;
      tagData.newTag = newTagName;
      $.ajax({
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(tagData),
        contentType: 'application/json',
        url: urlRequest,
        async: false
      });
      location.reload();
    });
  }

function removeTagFromPosts(tag) {
  tag.addEventListener('click', function () {
    var id = tag.id;
    var tagId = id.split('remove_posts__')[1];
    var clicked = $('#check_box__' + tagId + ' > label > input:checkbox:checked');
    var paths = [];
    $.each(clicked, function (i, clickVal) {
      paths.push(clickVal.id);
    });
    var jsonData = {};
    jsonData.tagId = tagId;
    jsonData.posts = paths;
    var urlRequest = '/remove_posts_tags';
    $.ajax({
      type: 'POST',
      dataType: 'json',
      data: JSON.stringify(jsonData),
      contentType: 'application/json',
      url: urlRequest,
      async: false
    });
    location.reload();
  });
}

function editTagDescription(tag) {
  tag.addEventListener('click', function () {
    var id = tag.id;
    var tagId = id.split('edit_desc__')[1];
    var tagDescForm = $('#' + tagId + '__new_tag_description')[0];
    var newDesc = tagDescForm.value;
    var urlRequest = '/edit_tag_description';
    var tagDesc = {};
    tagDesc.tagId = tagId
    tagDesc.tagDesc = newDesc;
    $.ajax({
      type: 'POST',
      dataType: 'json',
      data: JSON.stringify(tagDesc),
      contentType: 'application/json',
      url: urlRequest,
      async: false
    });
    location.reload();
   });
}

function addTagSubscriptionListener(v) {
    id = v.id
    text = v.innerText
    full_tag_id = v.id.split("__").slice(1).join('__')
    full_tag_slash = v.id.split("__").slice(1).join('/')
    url_request = 'toggle_tag_subscription?tag_name=' + full_tag_slash
    if (text == 'Subscribe') {
      url_request = url_request + "&subscribe_action=subscribe"
    } else if (text == 'Unsubscribe') {
      url_request = url_request + "&subscribe_action=unsubscribe"
    }
    $.ajax({
      type: "POST",
      url: url_request,
      async: true,
      success: function() {
        // We want to toggle all the buttons for all the relevant tags
        // Toggle non-popover buttons
        var all_buttons = $('[id^=tag-subscription]')
        $.each(all_buttons, function(i, button){
          if ($(button).attr("id") == 'tag-subscription-top__' + full_tag_id) {
            $(button).toggleClass('btn-default');
            $(button).toggleClass('btn-primary');
            if (text == 'Unsubscribe'){
              button.innerHTML = '<i class="glyphicon glyphicon-ok-sign glyphicon-filled"></i>' + 'Subscribe';
            } else {
              button.innerHTML = '<i class="glyphicon glyphicon-remove-sign glyphicon-white"></i>' + 'Unsubscribe';
            }
          }
        })

        // Toggle popover buttons
        var all_popovers = $('[data-toggle="popover"]')
        $.each(all_popovers, function(i, popover){
          tag_name = $(popover).data('tag-name');
          if ($(popover).data('tag-name') == full_tag_id) {
            data_content = $(popover).data('content');
            el = document.createElement( 'html' );
            el.innerHTML = data_content
            id = $('button[id^=tag-subscription]', el).attr("id")
            $(popover).toggleClass('label-subscribed');
            $(popover).toggleClass('label-unsubscribed');
            if (text == "Subscribe"){
              popover.setAttribute('data-content',
                            "<div class='content'> <button class='btn btn-small btn-unsubscribe btn-primary' title='' " +
                             "id='" + id + "'> " +
                             "<i class='glyphicon glyphicon-remove-sign glyphicon-white'></i>Unsubscribe" +
                             "</button></div>")
            } else {
               popover.setAttribute('data-content',
                            "<div class='content'> <button class='btn btn-small btn-subscribe btn-default' title='' " +
                             "id='" + id + "'> " +
                             "<i class='glyphicon glyphicon-ok-sign glyphicon-filled'></i>Subscribe" +
                             "</button></div>");
            }
          }
        })
      }
    });
}

function createTagLink(i, tag) {
    var aElem = $('<a>');
    var encodedTag = encodeURIComponent(tag);
    var aTagId = tag.replace('/', '__'); // id's can't have / in them
    var tagName = '#' + tag;
    aElem.attr('href', '/tag_pages?tag=' + encodedTag);
    aElem.attr('id', 'tag-tooltip-' + i + '-' + aTagId);
    aElem.attr('style', 'font-weight:normal');
    aElem[0].innerHTML = tagName;

    return aElem;
}

function createTagTooltip(i, tag, subscriptionsList) {
    var tooltip = $('<div>');
    var idTag = tag.replace('/', '__');
    tooltip.attr({
      'class': 'tooltip tooltip-top-left',
       role: 'tooltip',
      'data-trigger': '#tag-tooltip-' + i + '-' + idTag,
      'data-fixed': 'true',
      'data-sticky': 'true'
    });

    var panel = $('<p>');
    panel.attr('class', 'panel-body');

    var button = $('<button>');
    button.attr({
      id: 'tag-subscription-' + i + '__' + idTag,
      style: 'font-color:white'
    });
    if (subscriptionsList.indexOf(tag) >= 0) {
        button.attr('class', 'btn btn-small btn-default');
        button[0].innerHTML = 'Unsubscribe';
    } else {
        button.attr('class', 'btn btn-small btn-primary');
        button[0].innerHTML = 'Subscribe';
    }

    panel.append(button);
    tooltip.append(panel);
    return tooltip;

}

function changeAndSaveTags(postPath, tagsString) {
  var tagsList = tagsString.split(',');

  var re = /^[a-z0-9\-\:]+$/i;
  var good = true;

  $.each(tagsList, function (i, tag) {
      var cleanTag = tag.trim();
      var error = '';
      if (cleanTag.length === 0) {
          error = 'There is a tag with length 0 - possibly a trailing comma?';
      } else if (cleanTag.search('/') === -1) {
          error = 'The tag: ' + cleanTag + ' ,does not have the correct structure. Make sure there is a / between the group and the tag';
      } else {
          var tagGroup = cleanTag.split('/')[0].trim();
          var tagName = cleanTag.split('/')[1].trim();
          if (!re.test(tagGroup) || !re.test(tagName)) {
              error = 'Only alphanumeric characters in the tag group and tag name please';
          }
      }

      if (error.length !== 0) {
        good = false;
        alert(error);
      }
  });

  var oldHref = window.location.href;
  if (good) {
      var postContent = {};
      postContent.tags = tagsString;
      $.ajax({
          type: 'POST',
          dataType: 'json',
          data: JSON.stringify(postContent),
          contentType: 'application/json',
          url: '/tag_list?post_path=' + postPath,
          async: false
      });
  window.location = oldHref;
  }

}

// Export public functions
  return {
    deleteTagPosts: deleteTagPosts,
    renameTagPosts: renameTagPosts,
    removeTagFromPosts: removeTagFromPosts,
    editTagDescription: editTagDescription,
    addTagSubscriptionListener: addTagSubscriptionListener,
    createTagTooltip: createTagTooltip,
    createTagLink: createTagLink,
    changeAndSaveTags: changeAndSaveTags
  };
}());
