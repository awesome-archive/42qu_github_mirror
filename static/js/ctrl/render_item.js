$.template(
    'note_li',
    '<div class="readl c">'+
        '<div id="reado${$data[0]}" class="reado">'+
            '<a rel="${$data[0]}" href="javascript:void(0)" id="fav${$data[0]}" class="fav${$data[0]} fav{{if $data[5]}}ed{{/if}}"></a>'+
            '<span class="reada">'+
                '<span class="title">${$data[1]}</span>'+
                '<span class="rtip">${$data[2]}</span>'+
            '</span>'+
        '</div>'+
        '{{if $data[3]}}<div class="zname">'+
            '<a href="#" rel="${$data[3]}" class="TPH" target="_blank">${$data[4]}</a>'+
        '</div>{{/if}}'+
    '</div>'
)


$.template(
    'tag_cid',
'<div class="com_main" id="com_main_${$data[0]}">'+
    '<div id="feeds"><div id="feed_index">'+
        '<div class="main_nav">'+
            '<a class="now" href="/cid/${$data[0]}">'+
                '${$data[1]}'+
            '</a>'+
            '<span class="R">共 ${$data[2]} 篇</span>'+
        '</div>'+
        '<div id="item_list_${$data[0]}" class="tag_item_list"></div>',
    '</div></div>'+
'</div>'
)

function _render_tag_cid(id, data){
    $.tmpl('tag_cid', data).appendTo(id)
    var i=0,cid, item, t;
    for(;i<data.length;++i){
        t = data[i]
        cid = t[0]
        item = t[3]
        _render_note("#com_main_"+cid, "#item_list_"+cid, item)
    }
}

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
            '{{if link}}'+
            '<span class="split">,</span>'+
            '{{html user_name}}'+
            '<a class="aH" href="${link}" target="_blank"></a>'+
            '{{/if}}'+
        '</div>'+
    '</pre>'+
    '<div class="fdbar">'+
        '<a href="javascript:void(0)" class="readx"></a>'+
        '<span><span class="fdopt">'+
            '<a class="${fav} fav${id}" href="javascript:void(0)" rel="${id}"></a>'+
                '<span class="split">-</span>'+
            '<a href="javascript:share(${id});void(0)" class="vote">推荐</a>'+
                '<span class="split">-</span>'+
            '<a href="/po/${id}" target="_blank" class="fcma bzreply">'+
                '<span class="count mr3">{{if reply_count}}${reply_count}{{/if}}</span>'+
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
            '<a href="javascript:void(0)" title="快捷键 ESC" class="readx"></a>'+
        '</div>'+
    '</div>'+
    '<div id="main_nav_title" class="readtitle"></div>'+
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

        txt_body.replaceWith(read_loading)
    }

    $('.readx').live('click',readx)
    $(document).bind("keyup",function(e){
        if(e.keyCode == 27 && oldtop>=0){
            readx()
        }
    })

    $('.reada').live('click',function(){
        scrollTop = feeds.offset().top-28
        feed_index.hide();
        var p = this.parentNode,
            self=$(p), 
            title=self.find('.title').addClass('c9'), 
            id=p.id.slice(5), 
            user=$(p.parentNode).find('.TPH'),
            user_link
            ;
        feeds.append(txt_loading);
        oldtop=winj.scrollTop();
        winj.scrollTop(scrollTop);
        txt_title.html(title.html())
        $.get(
        "/j/po/json/"+id,
        function(r){
            r.id=id
            if(user[0]){
                user_link=user[0].href+id
            }else{
                user_link = 0
            }
            r.user_name=user.html()
            r.link = user_link
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



