
$(function(){
    var pop_add = $("#pop_add")
    if(pop_add[0]){
        pop_add.click(function(){
            $.fancybox({'content':'<div id="popline" class="line"><div>产品名称<input autocomplete="off" value="" class="input" name="product_name" id="pop_name"></div><div>简单描述<input autocomplete="off" class="input" name="product_about" value=""></div><div>相关链接<input class="input" name="product_url" value=""></div><div style="margin:7px 0 0 70px"><span class="btnw"><button type="submit">添加产品</button></span></div></div>','onComplete':function(){

                $('#pop_name').focus()
            }
            })
        })
    }else{
        $('.product_name:last').live('blur',function(){
            var self = $(this)
            if($.trim($('.line:last').find('input[name="product_name"]').val()).length>0){
                var wrap = self.parent().parent(),
                id = parseInt(wrap.attr('id').substr(4))+1
                wrap.after('<div class="line" id="line'+id+'"> <span class="L"><input name="product_name" class="product_name" value="" autocomplete="off"><input value="" name="product_about" class="product_about" autocomplete="off"><input value="" name="product_url" class="product_url"></span><a href="javascript:close_item('+id+');void(0)" class="close_item"></a></div>')
            }
            self.unbind('blur')
        })
    }
})
function close_item(id){
    $('#line'+id).remove()
}
