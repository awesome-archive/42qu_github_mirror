
$(function(){
    var say = $('#say');
    if(!say[0])return;
    var txt = $('#say_txt'),
    after=$('<div class="pop_banner"><a class="pop_submit" href="javascript:post_say();void(0)">发表</a><div class="pop_tip"></div><a class="pop_close" href="javascript:close_pop();void(0)"></a></div>'),
    tiptxt='今天 , 想说什么?',
    pop_tip=after.find('.pop_tip'),
    can_say = txt_maxlen(txt,pop_tip,142)
;

    txt.val(tiptxt).focus(function(){
        if(!say.hasClass('pop_say')){
            say.attr('class','pop_say')
            txt.attr('class','pop_txt').after(after)
            if(txt.val()==tiptxt)txt.val('');
            else txt.select();
        }   
    })
    

    close_pop = function (){
        say.attr('class','say')
        txt.attr('class','say_txt')
        if($.trim(txt.val())==''){
            txt.val(tiptxt)
        }
        $('.pop_banner').remove()
    }

    post_say = function (){
        if(!can_say()){
            pop_tip.fadeOut(function(){pop_tip.fadeIn()})
            return false
        }
        txt.replaceWith($('<pre class="pop_txt" id="pop_txt"/>').html(txt.val()))
        pop_tip.replaceWith('<div class="say_loading pop_tip"></div>')
        $('.pop_close,.pop_submit').hide()
        $.postJSON(
            '/j/po/word',
            {
                "txt":$('.pop_txt').val()
            },
            function(){
                $('.pop_tip').replaceWith('<div class="pop_ok pop_tip">发表成功</div>')
                var pop_ok = $('.pop_ok')  
                pop_ok.fadeIn(function(){
                    location="/word"
                })
            }
        )
    }
})




function fav(){
    fancybox_word(
        '备注 :',
        '/j/fav/txt'
    )
    $("#fav_a").text('设置').attr('href','/fav')
}
