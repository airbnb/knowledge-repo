(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');    
ga('create', 'UA-118308331-3', 'auto');
ga('send', 'pageview');

const gaCategory = "knowledgerepo";
const gaUIInteraction = "ui_interaction";
const gaDownload = "download";
const gaUpload = "upload";


var googleAnalyticsObject = {

  /**
   * This function sends the GA event to GA dashboard.
   *
   * @param {string}   actionName       Action for the GA event. For eg. "download", "upload", etc.
   * @param {string}   labelName         Label for the GA event. For eg: "demo_files", "processed_data", etc.
   */
  sendEvent : function(actionName, labelName='') {
    
    ga('send', 'event', {
      eventAction: actionName,
      eventCategory: gaCategory ,
      eventLabel: labelName,
    });
  }
}
