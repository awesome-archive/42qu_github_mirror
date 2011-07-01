(function( jQuery ){
jQuery.extend({
    cookie : {
        set:function(dict, days, path){
            if(typeof(days)=='string'){
                path=days;
                days=0;
            }
            days = days || 99;
            path = path||'/';
            var date = new Date();
            date.setTime(date.getTime()+(days*24*60*60*1000));
            var expires = "; expires="+date.toGMTString();
            for (var i in dict){
                document.cookie = i+"="+dict[i]+expires+"; path="+path;
            }
        },
        get:function(name) {
            var e = name + "=";
            var ca = document.cookie.split(';');
            for(var i=0;i < ca.length;i++) {
                var c = ca[i];
                while (c.charAt(0)==' ') c = c.substring(1,c.length);
                if (c.indexOf(e) == 0) {
                    return c.substring(e.length,c.length).replace(/\"/g,'');
                }
            }
            return null;
        }
    },
    postJSON : function(url, data, callback) {
        data = data||{};
        if ( jQuery.isFunction( data ) ) {
            callback = data;
        }
        var _xsrf = jQuery.cookie.get("_xsrf");
        if(typeof data=="string"){
            data+="&_xsrf="+_xsrf
        }else{
            data._xsrf = _xsrf;
        }
        jQuery.ajax({
            url: url,
            data: data, 
            dataType: "json", 
            type: "POST",
            success: function(data, textStatus, jqXHR){
                if(data.login){
                    login()
                }else if(callback){
                    callback(data, textStatus, jqXHR)
                }
            }
        });
    },
/*
    getScript : function(url, callback, cache){
        jQuery.holdReady(false);
        jQuery.ajax({
           type: "GET",
           url: url,
           success: function(){
               jQuery.holdReady(false);
               callback&&callback();
           },
           dataType: "script",
           cache: cache||true
        })
    },
*/
    isotime : function(timestamp){
        var date = new Date(timestamp*1000),hour=date.getHours(),minute=date.getMinutes();
        if(hour<9){
            hour = "0"+hour
        }
        if(minute<9){
            minute = "0"+minute
        }
        return [
            date.getFullYear(), date.getMonth() + 1, date.getDate()
        ].join("-")+" "+[
            hour,minute 
        ].join(":") 
    },
    timeago : function(timestamp){
        var date = new Date(timestamp*1000);
        var ago = parseInt((new Date().getTime() - date.getTime())/1000);
        var minute;
        if(ago>-60&&ago<=0){
            return "刚刚"
        }else if(ago<60){
            return ago+"秒前"
        }else{
            minute = parseInt(ago/60)
            if(minute<60){
                return minute+"分钟前"
            }
        }
        return jQuery.isotime(timestamp)
    } 
})
})(jQuery);
(function (){
var RE_CNCHAR = /[^\x00-\x80]/g;

function _cnenlen(str) {  
    if (typeof str == "undefined") {  
        return 0  
    }  
    var aMatch = str.match(RE_CNCHAR);  
    return (str.length + (!aMatch ? 0 : aMatch.length))  
} 
 
cnenlen = function(str) {  
        return Math.ceil(_cnenlen($.trim(str)) / 2)  
} 
})();

function uuid(){
    return (""+ Math.random()).replace( /\D/g,"")
}
