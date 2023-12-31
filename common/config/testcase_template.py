#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast

import allure
import pytest

from utils.file_tools.get_yaml_data_analysis import GetTestCase
from utils.requests.RequestSend import RequestSend
from utils.other.regular_control import config_regular

case_id = case_list
TestData = GetTestCase.get_case_data(case_id)
re_data = ast.literal_eval(config_regular(str(TestData)))

@allure.epic("allureEpic")
@allure.feature("allureFeature")
class class_name:

    @allure.story("allureStory")
    @pytest.mark.parametrize('in_data', re_data, ids=[i['remark'] for i in TestData])
    def function_name(self, in_data):
        RequestSend(in_data).http_request()
