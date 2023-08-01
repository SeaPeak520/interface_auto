#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
from typing import Text

from utils.exceptions.exceptions import ValueNotFoundError
from utils.cache.cache_control import CacheHandler
from utils.other.file_control import get_value


class SetCurrentRequestCache:
    """将用例中的请求或者响应内容存入缓存"""

    def __init__(
            self,
            current_request_set_cache,
            request_data,
            response_data
    ):
        self.current_request_set_cache = current_request_set_cache
        self.request_data = request_data
        self.response_data = response_data.text

    def set_request_cache(
            self,
            jsonpath_value: Text,
            cache_name: Text) -> None:
        """将接口的请求参数存入缓存"""
        _request_data = get_value(
            self.request_data,
            jsonpath_value
        )
        if _request_data is not False:
            CacheHandler.update_cache(cache_name=cache_name, value=_request_data[0])
        else:
            raise ValueNotFoundError(
                "缓存设置失败，程序中未检测到需要缓存的数据。"
                f"请求参数: {self.request_data}"
                f"提取的 jsonpath 内容: {jsonpath_value}"
            )

    def set_response_cache(
            self,
            jsonpath_value: Text,
            cache_name
    ):
        """将响应结果存入缓存"""
        _response_data = get_value(json.loads(self.response_data), jsonpath_value)
        if _response_data is not False:
            CacheHandler.update_cache(cache_name=cache_name, value=_response_data[0])
        else:
            raise ValueNotFoundError("缓存设置失败，程序中未检测到需要缓存的数据。"
                                     f"请求参数: {self.response_data}"
                                     f"提取的 jsonpath 内容: {jsonpath_value}")

    def set_caches_main(self):
        """设置缓存"""
        if self.current_request_set_cache is not None:
            for i in self.current_request_set_cache:
                _jsonpath = i.jsonpath
                _cache_name = i.set_cache
                if isinstance(_jsonpath,str) and isinstance(_cache_name,str):
                    if i.type == 'request':
                        self.set_request_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
                    elif i.type == 'response':
                        self.set_response_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
                elif isinstance(_jsonpath,list) and isinstance(_cache_name,list) and len(_jsonpath) == len(_cache_name):
                    for index, value in enumerate(_jsonpath):
                        if i.type == 'request':
                            self.set_request_cache(jsonpath_value=value, cache_name=_cache_name[index])
                        elif i.type == 'response':
                            self.set_response_cache(jsonpath_value=value, cache_name=_cache_name[index])
                else:
                    raise ValueNotFoundError(f"{_jsonpath} 和 {_cache_name} 的类型对不上，同list或str")


