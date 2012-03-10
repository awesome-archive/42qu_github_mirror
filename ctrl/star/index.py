# -*- coding: utf-8 -*-
from _handler import Base, LoginBase, XsrfGetBase
from ctrl._urlmap.star import urlmap
from zkit.errtip import Errtip
from zkit.pic import picopen
from model.zsite_star import star_ico_new, zsite_star_new, zsite_star_get, txt_new, star_pic_bind
from model.days import ymd2days, today_days, days2ymd
from model.cid import CID_STAR

def _upload_pic(self, errtip):
    files = self.request.files
    pic_id = self.get_argument('pic_id', None)

    if 'pic' in files:
        pic = files['pic'][0]['body']
        if pic:
            pic = picopen(pic)
            if pic:
                pic_id = star_ico_new(self.current_user_id, pic)
            if not pic:
                errtip.pic = "图片格式有误"

    return pic_id


@urlmap('/')
class Index(Base):
    def get(self):
        self.render()

@urlmap('/new')
class New(LoginBase):
    def get(self):
        self.render(errtip=Errtip())

    def post(self):
        errtip=Errtip()
        user_id = self.current_user_id

        name = self.get_argument('name', None)
        if not name:
            errtip.name = "请输入名称"

        donate_min = self.get_argument('donate_min', None)

        if not donate_min:
            errtip.donate_min = "请输入启动金额"
        elif not donate_min.isdigit():
            errtip.donate_min = "请输入正整数" 

        end_time = int(self.get_argument('end_time', 0))
        if end_time:
            try:
                end_days = ymd2days(end_time)
            except ValueError:
                errtip.end_time = "请选择一个确切的结束时间"
            else:
                if end_days-today_days()<1:
                    errtip.end_time = "结束时间距当前不能小于1天"
 
        else:
            errtip.end_time = "请输入结束日期"


        txt = self.get_argument('txt', '')

        pic_id = _upload_pic(self, errtip)


        if not errtip.pic and not pic_id:
            errtip.pic = "请上传图片"


        if errtip:
            self.render(
                pic_id = pic_id,
                errtip = errtip,
                name = name,
                donate_min = donate_min,
                txt = txt,
                end_time = end_time
            )
        else:
            zsite = zsite_star_new(
                user_id, 
                name,  
                txt, 
                donate_min, 
                end_days, 
                pic_id
            )
            self.redirect("/po/%s"%zsite.id)

class StarBase(Base):
    def zsite(self, id):
        zsite = zsite_star_get(id)
        if not zsite:
            self.redirect("/")
        return zsite

@urlmap('/new/(\d+)')
class NewId(StarBase):
    def get(self, id):
        zsite = self.zsite(id)
        if not zsite:
            return
        return self._render(zsite)

    def _render(self, zsite, errtip=Errtip()):
        star = zsite.star
        self.render(
            "/ctrl/star/index/new.htm",
            zsite=zsite, 
            name=zsite.name,
            txt=zsite.txt,
            donate_min=star.donate_min,
            pic_id=star.pic_id,
            end_time=days2ymd(star.end_days),
            errtip=errtip,
        )
    
    def post(self, id):
        zsite = self.zsite(id)
        if not zsite:
            return
        
        errtip = Errtip() 
        user_id = self.current_user_id
        star = zsite.star

        name = self.get_argument('name', None)
        if name:
            zsite.name = zsite.name

        txt = self.get_argument('txt', '')
        if txt:
            txt_new(id, txt)


        end_time = int(self.get_argument('end_time', 0))
        if end_time:
            try:
                end_days = ymd2days(end_time)
            except ValueError:
                errtip.end_time = "请选择一个确切的结束时间"
            else:
                if end_days != star.end_days:
                    if end_days-today_days()<1:
                        errtip.end_time = "结束时间距当前不能小于1天"
                    else:
                        star.end_days = end_days


        donate_min = self.get_argument('donate_min', None)

        if not donate_min:
            errtip.donate_min = "请输入启动金额"
        elif not donate_min.isdigit():
            errtip.donate_min = "请输入正整数" 
        else:
            star.donate_min = donate_min

        pic_id = _upload_pic(self, errtip)
        if pic_id and pic_id!=star.pic_id:
            star_pic_bind(user_id, pic_id, id) 
 
        zsite.save()
        star.save()
        return self._render(zsite, errtip)

@urlmap('/po/(\d+)')
class PoId(StarBase):
    def get(self, id):
        zsite = self.zsite(id)
        if not zsite:
            return
        self.render(zsite=zsite)

    def post(self, id):
        zsite = self.zsite()
        if not zsite:
            return
        self.render(zsite=zsite)

