
#coding:utf-8

def prepare(o):
    o.SITE_DOMAIN = 'z18e1.tk' 
    o.FILE_DOMAIN = 'p.%s'%o.SITE_DOMAIN
    o.FS_DOMAIN = 's.%s'%o.SITE_DOMAIN
    o.PORT = 30900
   
    o.SMTP = 'smtp.mailgun.org'
    o.SMTP_USERNAME = ''
    o.SMTP_PASSWORD = ''
    o.SENDER_MAIL = o.SMTP_USERNAME

    o.ZDATA_PATH = "/home/z18/file/"
