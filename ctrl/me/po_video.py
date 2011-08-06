# -*- coding: utf-8 -*-
from _handler import LoginBase
from ctrl._urlmap.me import urlmap
from model.po import Po
from model.po_video import po_video_new, VIDEO_CID_YOUKU, VIDEO_CID_TUDOU, VIDEO_CID_SINA
from model.zsite_tag import zsite_tag_new_by_tag_id
from model.cid import CID_VIDEO
from model.state import STATE_ACTIVE

@urlmap('/po/video')
@urlmap('/po/video/(\d+)')
class PoVideo(LoginBase):
    def post(self, po_id=0):
        cid = CID_VIDEO
        url = self.get_argument('video', None)
        name = self.get_argument('name', None)
        txt = self.get_argument('txt', None)


        link = '/live'

        if po_id:
            po_id = int(po_id)
            po = Po.mc_get(po_id)
            if po and po.user_id == self.current_user_id:
                po.name_ = name
                po.txt_set(txt)
                po.save()
                link = '/po/tag/%s' % po_id
        else:
            if url:
                video, video_site = self._video(url)
                if video:
                    user_id = self.current_user_id
                    po = po_video_new(user_id, name, txt, video, video_site)
                    if po:
                        po_id = po.id
                        link = '/po/tag/%s' % po_id


        return self.redirect(link)

    def _video(self, url):
        if url.startswith('http://v.youku.com/v_show/id_'):
            video = url[29:url.rfind('.')]
            video_site = VIDEO_CID_YOUKU
        elif url.startswith('http://player.youku.com/player.php/sid/'):
            video = url[39:url.find("/",39)]
            video_site = VIDEO_CID_YOUKU
        elif url.startswith('http://www.tudou.com/programs/view/'):
            video = url[35:].rstrip("/")
            video_site = VIDEO_CID_TUDOU
        elif url.startswith('http://video.sina.com.cn/v/b/'):
            video = url[29:url.rfind('.')]
            video_site = VIDEO_CID_SINA
        else:
            video = None
            video_site = None
        return video, video_site

