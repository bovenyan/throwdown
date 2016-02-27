var layout = {
    bindEvent : function(){
        $(".newboly-nav-btn").click(function(){
            var $btn_id = $(this).attr("id"),
                $main_id = $(this).attr("main-id");
            layout.show($btn_id, $main_id);
        });
    },
    show : function(btn_id, main_id){
        layout.hide();
        $("#" + main_id).removeClass("hide-main");
        $("#" + btn_id).addClass("active");

    },
    hide : function(){
        $(".newboly-main").each(function(){
            $(this).addClass("hide-main");
        });
        $(".newboly-nav-btn").each(function(){
            $(this).removeClass("active");
        });
    }
}

/**
 * main fun
 */
$(function(){
    layout.bindEvent();
})