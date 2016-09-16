var commentsJx = (function(){

  function postComment(comment_author, post_author, post_title, post_path) {
    var comment_text = $('#comment-text').val()

    if (comment_text === '') {
      return;
    }

    var postContent = {};
    postContent.what = 'comment';
    postContent.author = comment_author;
    postContent.text = comment_text;
    postContent.post_author = post_author;
    postContent.post_title = post_title;

    $.ajax({
      type: "POST",
      dataType: "json",
      data: JSON.stringify(postContent),
      contentType: "application/json",
      url: '/comment?path=' + encodeURI(post_path),
      async: false
    });
    location.reload();
  }


  function deleteComment(post_path, comment_id){
    $.ajax({
      type:"GET",
      url: "/delete_comment?comment_id=" + comment_id,
      async: false
    });
    location.reload();
  }


  return {
    postComment: postComment,
    deleteComment: deleteComment
  }

}());
