#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************
# Author       : Miacis
# Email        : guvmao@163.com
# Last modified: 20/05/15 17:51
# Filename     : feishu_alert.py
# Description  :
# ******************************************************

import time
from elastalert.alerts import Alerter, DateTimeEncoder
from requests import get, post, RequestException
from elastalert.util import elastalert_logger, EAException

class FeiShuAlerter(Alerter):
    required_options = frozenset(['app_id','app_secret'])

    def __init__(self, *args):
        super(FeiShuAlerter, self).__init__(*args)
        self.app_id = self.rule.get('app_id', '')
        self.app_secret = self.rule.get('app_secret', '')
        self.email = self.rule.get("email", '')
#        self.mobiles = self.rule.get('mobiles', '')
        self.chat_id = ''
        self.user_id = ''
        self.open_id = ''

    def alert(self, matches):

        body = self.create_alert_body(matches)
        self.get_tenant_access_token()
        self.get_chatid()  #向群内发送消息
#        self.get_userid()  #向个人发送消息
        self.senddata(body)

    def get_tenant_access_token(self):
        # 获取企业自建应用 tenant_access_token 
        # https://open.feishu.cn/document/ukTMukTMukTM/uIjNz4iM2MjLyYzM
        body = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        try:
            r = get("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/", json=body).json()
            if r['code'] == 0:
               # elastalert_logger.debug("token: " + r['tenant_access_token'])
                self.tenant_access_token = r['tenant_access_token']
                return self.tenant_access_token
        except Exception as e:
            raise EAException("Get tenant_access_token failed:".format(e))

    def get_userid(self):
        # 获取 userid
        # https://open.feishu.cn/document/ukTMukTMukTM/uUzMyUjL1MjM14SNzITN
        userurl = "https://open.feishu.cn/open-apis/user/v1/batch_get_id?emails=%s" %self.email
        headers = {"Authorization":"Bearer " + self.tenant_access_token}
        try:
            r = get(url=userurl, headers=headers).json()
            if r['code'] == 0:
                self.user_id = r['data']['email_users'][self.email][0]['user_id']
                return self.user_id
        except Exception as e:
            raise EAException("Get user_id failed:".format(e))

    def get_chatid(self):
        # 获取 chatid
        # https://open.feishu.cn/document/ukTMukTMukTM/uITO5QjLykTO04iM5kDN
        chaturl = "https://open.feishu.cn/open-apis/chat/v4/list?page_size=20"
        headers = {"Authorization":"Bearer " + self.tenant_access_token}
        try:
            r = get(url=chaturl, headers=headers).json()
            if r['code'] == 0:
                self.chat_id = r['data']['groups'][0]['chat_id']
                return self.chat_id
        except Exception as e:
            raise EAException("Get user_id failed:".format(e))
 
    def senddata(self, content):
        # 发送文本消息
        # https://open.feishu.cn/document/ukTMukTMukTM/uUjNz4SN2MjL1YzM
        headers = {
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        body = {
            "chat_id": self.chat_id and str(self.chat_id) or '', #群组id
            "open_id": self.open_id and str(self.open_id) or '', #统一id
            "user_id": self.user_id and str(self.user_id) or '', #用户id
            "email": self.email and str(self.email) or '',
            "msg_type": "text",
            "content": {
#                "text": "%s<at user_id=\"%s\">test</at>"%(content,self.user_id)
                "text": content
            }
        }
        try:
            r = post("https://open.feishu.cn/open-apis/message/v4/send/",  json=body, headers=headers)
            r.raise_for_status()
        except RequestException as e:
            raise EAException("Error request to feishu: {}\n{}".format(str(e)))

    def get_info(self):
        return {
            "type": "FeiShuAlerter",
            "timestamp": time.time()
        }
        pass