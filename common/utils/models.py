import types
from dataclasses import dataclass
from enum import Enum, unique
from typing import Text, Union, Dict, Any, Optional, List

from pydantic import BaseModel


def load_module_functions(module):
    """ 获取 module中方法的名称和所在的内存地址 """
    return {
        name: item
        for name, item in vars(module).items()
        if isinstance(item, types.FunctionType)
    }


@unique
class AssertMethod(Enum):
    """断言类型"""
    equals = "=="
    less_than = "lt"
    less_than_or_equals = "le"
    greater_than = "gt"
    greater_than_or_equals = "ge"
    not_equals = "not_eq"
    string_equals = "str_eq"
    length_equals = "len_eq"
    length_greater_than = "len_gt"
    length_greater_than_or_equals = 'len_ge'
    length_less_than = "len_lt"
    length_less_than_or_equals = 'len_le'
    contains = "contains"
    contained_by = 'contained_by'
    startswith = 'startswith'
    endswith = 'endswith'


class TestCaseEnum(Enum):
    URL = ("url", True)
    HOST = ("host", True)
    METHOD = ("method", True)
    REMARK = ("remark", True)
    IS_RUN = ("is_run", True)
    HEADERS = ("headers", True)
    REQUEST_TYPE = ("requestType", True)
    REQUEST_DATA = ("requestData", True)
    DE_CASE = ("dependence_case", True)
    DE_CASE_DATA = ("dependence_case_data", False)
    DATABASE_ASSERT_SQL = ("database_assert_sql", True)
    DATABASE_ASSERT_RESULT = ("database_assert_result", True)
    CURRENT_RE_SET_CACHE = ("current_request_set_cache", False)
    SETUP_SQL = ("setup_sql", False)
    ASSERT_DATA = ("assert_data", True)
    TEARDOWN = ("teardown", False)
    TEARDOWN_SQL = ("teardown_sql", False)
    SLEEP = ("sleep", False)


class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTION = "OPTION"


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = 'FILE'
    EXPORT = "EXPORT"
    NONE = "NONE"


@unique
class DependentType(Enum):
    """
    数据依赖相关枚举
    """
    RESPONSE = 'response'
    REQUEST = 'request'
    SQL_DATA = 'sqlData'
    CACHE = "cache"


class DependentData(BaseModel):
    dependent_type: Text
    jsonpath: Union[Text, None, list]
    set_cache: Union[Text, None, list]
    replace_key: Union[Dict, None]


class DependentCaseData(BaseModel):
    case_id: Text
    dependent_data: Union[None, List[DependentData]] = None


class TeardownData(BaseModel):
    case_id: Union[None, Text]
    replace_key: Union[None, Dict]

class CurrentRequestSetCache(BaseModel):
    type: Text
    jsonpath: Union[Text, List]
    set_cache: Union[Text, List]


class TestCase(BaseModel):
    case_id: Text
    url: Text
    method: Text
    remark: Text
    is_run: Optional[bool]
    headers: Union[None, Dict, Text]
    requestType: Text
    requestData: Union[Dict, Text, List, None]
    dependence_case: Union[None, bool] = False
    dependence_case_data: Optional[Union[None, List["DependentCaseData"], Text]] = None
    setup_sql: Union[None, List, Text]
    database_assert_sql: Union[list, Text, None]
    database_assert_result: Union[list, Text, None]
    assert_data: Union[Dict, Text, None]
    current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
    teardown_sql: Optional[List] = None
    teardown: Optional[Union[None, List["TeardownData"], Text]] = None
    #sleep: Optional[Union[int, float]]
    is_retry: bool = None



class NotificationType(Enum):
    """ 自动化通知方式 """
    DEFAULT = '0'
    DING_TALK = '1'
    WECHAT = '2'
    EMAIL = '3'
    FEI_SHU = '4'


class DingTalk(BaseModel):
    webhook: Union[Text, None]
    secret: Union[Text, None]


class Webhook(BaseModel):
    webhook: Union[Text, None]


class Email(BaseModel):
    host: Union[Text, None]
    port: Union[int, None]
    user: Union[Text, None]
    pwd: Union[Text, None]
    sender: Union[Text, None]
    receivers: Union[list, None]
    receivers_list: Union[list, None]
    to: Union[Text, None]


class Host(BaseModel):
    gateway_host: Union[Text, None]
    lawyer_host: Union[Text, None]
    callback_host: Union[Text, None]


class MySqlDB(BaseModel):
    switch: bool = False
    db: Union[Text, None] = None
    host: Union[Text, None] = None
    user: Union[Text, None] = None
    pwd: Union[Text, None] = None
    port: Union[int, None] = 3306


class RedisDB(BaseModel):
    host: Union[Text, None] = None
    pwd: Union[Text, None] = None
    port: Union[int, None] = 6379
    db: Union[Text, None] = None


class Config(BaseModel):
    project_name: Union[Text, None]
    env: Union[Text, None]
    host: "Host"
    tester_name: Union[Text, None]
    notification_type: Text = '0'
    # excel_report: bool
    # 数据库
    mysql: "MySqlDB"
    redis: "RedisDB"
    # 通知
    ding_talk: "DingTalk"
    wechat: "Webhook"
    email: "Email"
    # mirror_source: Text
    # lark: "Webhook"
    # real_time_update_test_cases: bool = False


class ResponseData(BaseModel):
    yaml_is_run: Union[None, bool, Text]
    yaml_remark: Text
    yaml_body: Any
    yaml_assert_data: Dict
    yaml_data: "TestCase"
    yaml_database_assert_sql: Union[None, list, Text]
    yaml_database_assert_result: Union[None, list, Text]

    req_url: Text
    req_method: Text
    req_headers: Dict

    res_assert_result: Optional[bool]
    res_data: Any
    res_cookie: Dict
    res_time: Union[int, float]
    res_status_code: int

    file: Text
    is_decorator: bool


class SetupTeardownType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    INSERT = "INSERT"
    DELETE = "DELETE"
    SELECT = "SELECT"
    NUM = 'NUM'


@unique
class AllureAttachmentType(Enum):
    """
    allure 报告的文件类型枚举
    """
    TEXT = "txt"
    CSV = "csv"
    TSV = "tsv"
    URI_LIST = "uri"

    HTML = "html"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    PCAP = "pcap"

    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

    MP4 = "mp4"
    OGG = "ogg"
    WEBM = "webm"

    PDF = "pdf"


@dataclass
class TestMetrics:
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text
