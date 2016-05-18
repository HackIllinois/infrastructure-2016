$(document).ready(function(){
    $('.single-route-info > h4').on('click', function(e){
        var children = $($(e.currentTarget).closest('.single-route-info')[0]).children();
        for (var i = 0; i < children.length; i++){
            $(children[i]).toggleClass("show");
            $(children[i]).find(".arrow").toggleClass("rotated");
        }
    });
});
