var iconsJx = (function(){

  function createEditTagsIcon() {
    var editIcon = $("<i>");
    editIcon.attr({
      class: "icon icon-edit icon-gray",
      style: "font-size:12pt, padding-left:4px",
      id: "tooltip-edit_tags"
    });
    return editIcon;
  };


  function createSaveTagsIcon() {
    var saveIcon = $("<i>");
    saveIcon.attr({
      class: "icon icon-upload icon-gray",
      style: "font-size:23px; padding-left:4px",
      id: "tooltip-save_tags"
    });
    return saveIcon;
  };

  return {
    createEditTagsIcon: createEditTagsIcon,
    createSaveTagsIcon: createSaveTagsIcon,
  };

}());
