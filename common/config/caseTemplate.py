#!/usr/bin/env python
# -*- coding: utf-8 -*-

import allure
import pytest
from common.assertion.assert_control import AssertUtil
from common.file_tools.get_yaml_data_analysis import GetTestCase
from common.unit.RequestSend import RequestSend
from common.utils.regularHandle import regular

case_id = case_list
TestData = GetTestCase.case_data(case_id)
re_data = eval(regular(str(TestData)))

@allure.epic("allureEpic")
@allure.feature("allureFeature")
class class_name:

    @allure.story("allureStory")
    @pytest.mark.parametrize('in_data', re_data, ids=[i['remark'] for i in TestData])
    def function_name(self, in_data):
        res = RequestSend(in_data).http_request()
        AssertUtil(assert_data=in_data['assert_data'],
               request_data=res.yaml_body,
               response_data=res.res_data,
               status_code=res.res_status_code).assert_type_handle()

