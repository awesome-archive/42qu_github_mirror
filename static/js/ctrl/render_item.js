$.template(
    'note_li',
    '<div class="readl c">'+
        '<a rel="${$data[0]}" href="javascript:void(0)" id="fav${$data[0]}" class="fav{{if $data[5]}}ed{{/if}}"></a>'+
        '<div id="reado${$data[0]}" class="reado">'+
            '<span class="reada">'+
                '<span class="title">${$data[1]}</span>'+
                '<span class="rtip">${$data[2]}</span>'+
            '</span>'+
        '</div>'+
        '<div class="zname">'+
            '<a href="#" rel="${$data[3]}" class="TPH" target="_blank">${$data[4]}</a>'+
        '</div>'+
    '</div>'
)


function _render_note(feed_index, elem, data){
    var result = $.tmpl('note_li', data)
    result.find('.TPH').each(function(){
        this.href="//"+this.rel+HOST_SUFFIX
    })
    result.appendTo(elem);
    note_li($(feed_index))
    return result
}


$.template(
    'note_txt',
    '<pre class="prebody">{{html txt}}'+
        '<div class="readauthor">'+
            '<a target="_blank" href="/${link}">${time}</a>'+
            '<span class="split">,</span>'+
            '{{html user_name}}'+
            '<a class="aH" href="${link}" target="_blank"></a>'+
        '</div>'+
    '</pre>'+
    '<div class="fdbar">'+
        '<a href="javascript:void(0)" class="readx"></a>'+
        '<span><span class="fdopt">'+
            '<a class="${fav}" href="javascript:void(0)" rel="${id}"></a>'+
                '<span class="split">-</span>'+
            '<a href="javascript:share(${id});void(0)" class="vote">推荐</a>'+
                '<span class="split">-</span>'+
            '<a href="/${id}" class="fcma">'+
                '<span class="mr3">{{if reply_count}}${reply_count}{{/if}}</span>'+
                '评论'+
            '</a>'+
        '</span></span>'+
    '</div>'
)


function note_li(feed_index){
    var feeds=$(feed_index[0].parentNode), 
        scrollTop,
        oldtop=-1,
        winj=$(window),
        txt_loading=$(
'<div class="readpad">'+
    '<div class="main_nav" id="main_nav_txt">'+
        '<div id="main_nav_in">'+
            '<div id="main_nav_opt"></div>'+
            '<a href="javascript:void(0)" class="readx"></a>'+
        '</div>'+
    '</div>'+
    '<div id="main_nav_title"></div>'+
    '<div id="read_loading"></div>'+
'</div>'
        ),
        txt_title=txt_loading.find('#main_nav_title'),
        main_nav_txt=txt_loading.find('#main_nav_txt'),
        read_loading=txt_loading.find('#read_loading'),
        txt_opt=txt_loading.find('#main_nav_opt'),
        txt_body;


    function readx(){
        txt_loading.remove()
        feed_index.show() 
        winj.scrollTop(oldtop)
        oldtop=-1
        var fav=txt_body.find(".fav,.faved")[0];
        if(fav){
            $("#fav"+fav.rel)[0].className = fav.className;
        }

        txt_body.replaceWith(read_loading)
    }

    $('.readx').live('click',readx)
    $(document).bind("keyup",function(e){
        if(e.keyCode == 27 && oldtop>=0){
            readx()
        }
    })

    $('.reado').live('click',function(){
        scrollTop = feeds.offset().top-14
        feed_index.hide();
        var self=$(this), 
            title=self.find('.title').addClass('c9'), 
            id=this.id.slice(5), 
            user=$(this.parentNode).find('.TPH'),
            user_link=user[0].href
            ;
        feeds.append(txt_loading);
        oldtop=winj.scrollTop();
        winj.scrollTop(scrollTop);
        txt_title.html(title.html())
        $.get(
        "/j/po/json/"+id,
        function(r){
            r.id=id
            r.user_name=user.html()
            r.link = user_link+id
            r.time = $.timeago(r.create_time)
            r.fav = $('#fav'+id)[0].className

            txt_body = $.tmpl('note_txt',r)
            read_loading.replaceWith(txt_body)
            txt_opt.html(txt_body.find('.fdopt').html());
            winj.scrollTop(scrollTop)
        })

        return false; 
    })




};




