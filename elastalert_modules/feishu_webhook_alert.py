#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************
# Author       : Miacis
# Email        : guvmao@163.com
# Last modified: 20/05/15 17:51
# Filename     : feishu_alert.py
# Description  :
# ******************************************************

import json
import requests
from elastalert.alerts import Alerter, DateTimeEncoder
from requests.exceptions import RequestException
from elastalert.util import EAException


class FeiShuAlerter(Alerter)
    
    required_options = frozenset(['feishu_webhook'])

    def __init__(self, rule)
        super(FeiShuAlerter, self).__init__(rule)
        self.feishu_webhook_url = self.rule['feishu_webhook']

    def format_body(self, body)
        return body.encode('utf8')
    
    def alert(self, matches)
        body = self.create_alert_body(matches)
        payload = {
            text body
        }
        try
            response = requests.post(self.feishu_webhook_url,data=json.dumps(payload))
            response.raise_for_status()
        except RequestException as e
            raise EAException(Error request to feishu {0}.format(str(e)))

    def get_info(self)
        return {
            type FeiShuAlerter,
            feishu_webhook self.feishu_webhook_url
        }
        pass
