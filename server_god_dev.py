#!/usr/bin/env python
#coding:utf-8
import config.dev
import config


if __name__ == '__main__':
    from zkit.reloader.reload_server import auto_reload
    from server_god import run
    auto_reload(run)
