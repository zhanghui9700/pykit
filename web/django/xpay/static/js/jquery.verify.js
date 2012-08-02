/*
 * verify plugin by kiko
 * 2011/12/18
 *  */

var qf = qf || {};
qf.validate = (function(){
    return {
        isNull:function(obj){
            var obj = $(obj);
            if(obj && (obj.val()=="" || obj.val() == null))
                return true;
            else
                return false;
	    },
        showError:function(element,errmsg){
            //debugger
            var containerDiv = $(element).parentsUntil(".verify");
            if(containerDiv.length != 1){
                containerDiv = $(element).parentsUntil(".verify_tip");
            }
            if(containerDiv.length == 1){
                containerDiv = containerDiv.parent();
                qf.validate.showErrTip($(containerDiv),errmsg);
            }
            else
                console.log('container error!');
        },
        showErrTip:function(obj, errString){
		    $(".errors",obj).hide();
		    if(errString) {
			    $(".errTip", obj).text(errString);
		    } else {
			    $(".errTip", obj).text("输入不能为空");	
		    }	
		
		    $(".errTip, .tipImg", obj).show();
		    $(".tipImg", obj).css({
			    backgroundPosition : "left -26px"
		    });	
	    },
	    showPassTip:function(obj){
		    $(".errTip,.errors,.tipImg", obj).hide();	
		    $(".tipImg", obj).css({
			    display: "inline-block",
			    backgroundPosition : "left top"
		    });		
	    }, 
        hideErrTip:function(obj){		
		    $(".errTip, .tipImg", obj).hide();
	    }
    };
})();

(function($){
	var listener_funcs = {};
	$.fn.add_verify_listener = function(func, errString){
		var func_id = $(this).attr("id");
		
		listener_funcs[func_id] = {}
		listener_funcs[func_id]["id"] = func_id;
		listener_funcs[func_id]["func"] = func;
		listener_funcs[func_id]["err"] = errString;	
	}
		
	function isNull(obj){
        if(obj.val() == "" || obj.val() == null) {
            if(obj.hasClass('required'))
                return true;
            else
                return false;
        } else {
                return false;
        }
	}
	
	function showErrTip(obj, errString){
		$(".errors",obj).hide();
		if(errString) {
			$(".errTip", obj).text(errString);
		} else {
			$(".errTip", obj).text("输入不能为空");	
		}	
		
		$(".errTip, .tipImg", obj).show();
		$(".tipImg", obj).css({
			backgroundPosition : "left -26px"
		});	
	}
	
	function showPassTip(obj){
		$(".errTip,.errors,.tipImg", obj).hide();	
		$(".tipImg", obj).css({
			display: "inline-block",
			backgroundPosition : "left top"
		});		
	}
	
	function hideErrTip(obj){		
		$(".errTip, .tipImg", obj).hide();
	}

	function showTipBox(obj){
		$("#tipBox #tipContent").text(obj.attr("tip"));	
		$("#tipBox").css({
			top : obj.offset().top - $("#tipBox").outerHeight() + 8,
			left : obj.offset().left
		}).show();
	}
	
	function hideTipBox(){
		$("#tipBox").hide();
	}
	
	$(document).ready(function(){
		//show tips on focus
        $(".varify_input", $(".verify")).focus(function(){
			var $thisBlock = $(this).parentsUntil(".verify").parent();	
			showTipBox($(this));
			hideErrTip($thisBlock);
		});
        
        //hide error on focus
		$(".varify_input", $(".verify_tip")).focus(function(){
			var $tipBlock = $(this).parentsUntil(".verify_tip").parent();	
			showTipBox($(this));
            hideErrTip($tipBlock);
		});
        
        //validate on blur
		$(".varify_input", $(".verify")).blur(function(){
			var is_null = isNull($(this));
            var this_id = $(this).attr("id");
			var $thisBlock = $(this).parentsUntil(".verify").parent();
	
			if(is_null) {
				showErrTip($thisBlock);
			} else {
				if(this_id && listener_funcs[this_id]) {
					for(var i in listener_funcs) {	
						if(listener_funcs[i].id == this_id) {
							var is_ok = listener_funcs[i].func($(this));
							if(is_ok) {
								showPassTip($thisBlock);
							} else {
								showErrTip($thisBlock, listener_funcs[i].err);
							}
						} else {
							//
						}
					}
				} else {
					showPassTip($thisBlock);
				}
			}
			hideTipBox();
		});
		$(".varify_input", $(".verify_tip")).blur(function(){
				var is_null = isNull($(this)),
					this_id = $(this).attr("id"),
					$thisBlock = $(this).parentsUntil(".verify_tip").parent();
		
				if(is_null) {
					showErrTip($thisBlock);
				} else {
					if(this_id && listener_funcs[this_id]) {
						for(var i in listener_funcs) {
							
							if(listener_funcs[i].id == this_id) {
								
								var is_ok = listener_funcs[i].func($(this));
								
								if(is_ok) {
									showPassTip($thisBlock);
								} else {
									
									showErrTip($thisBlock, listener_funcs[i].err);
								}
							} else {
								//
							}
						}
					} else {
						showPassTip($thisBlock);
					}	
				}
				hideTipBox();
			});
	});
})(jQuery)


$.show_msg = function(obj,need_parent, has_error, msg){
		if(need_parent) obj = obj.parent();
		tipImg = obj.nextAll(".tipImg");
			tipMsg = obj.nextAll(".errTip");
			if(has_error){
				tipImg.css({backgroundPosition : "left -26px"}).show();
				tipMsg.show().html(msg);
				}
			else{
				tipImg.css({display: "inline-block",backgroundPosition : "left top" }).show();
				tipMsg.show().html("");
				}
		};

$.hide_msg = function(obj,need_parent){
		if(need_parent) obj = obj.parent();
		tipImg = obj.nextAll(".tipImg");
		tipMsg = obj.nextAll(".errTip");

		tipImg.hide();
		tipMsg.hide();
		};

