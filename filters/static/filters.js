$(function() {
    $(document).click(function() {                                                                                                                                                                      
        $('.drop_down .input .content').fadeOut();                                                                                                                                                     
    });    
    $("a[rel=drop_link]").live('click', function(e) {
        var obj = $(this).parent().parent().find('.content');
        if (obj.is(':visible'))
            obj.fadeOut();
        else
            obj.fadeIn();
        e.preventDefault();
        return false;
    });
});
