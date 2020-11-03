var pathname = window.location.pathname;
var count = 0;
$(function() {

  $(".sortable_list").sortable({
    connectWith: ".connectedSortable",

    receive: function(event, ui) {
      if (this.id == "sortable2")
        count++;
      else
        count--;
    }
  }).disableSelection();
});

function beforeSub() { // synchronize
  $.ajaxSetup({
    async: false
  }); // in order to synchro the post requests, we want to send this post req and then the form post req
  $.post(pathname, {
    "preferedCount": count
  })
}
