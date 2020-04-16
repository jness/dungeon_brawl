
$(document).ready(function(){
    $('[data-toggle="popover"]').popover({html:true});

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('my_response', function(msg) {
        location.reload(true);
    });

});

$(document).on('click', function (e) {
    $('[data-toggle="popover"],[data-original-title]').each(function () {
        //the 'is' for buttons that trigger popups
        //the 'has' for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            (($(this).popover('hide').data('bs.popover')||{}).inState||{}).click = false  // fix for BS 3.3.6
        }

    });
});

function get_percentage() {
  return "25%";
}

$('input[type=radio]').on('change', function() {
    $(this).closest("form").submit();
});
