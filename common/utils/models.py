import types
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
    SQL_DATA = ("sql_data", True)
    SQL_ASSERT = ("sql_assert", True)

    CURRENT_RE_SET_CACHE = ("current_request_set_cache", False)
    SQL = ("sql", False)
    ASSERT_DATA = ("assert_data", True)
    SETUP_SQL = ("setup_sql", False)
    TEARDOWN = ("teardown", False)
    TEARDOWN_SQL = ("teardown_sql", False)
    SLEEP = ("sleep", False)
    PROCESS = ("process", True)


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
    dependent_sql: Union[Text, None]
    jsonpath: Union[Text, None]
    set_cache: Optional[Text]
    replace_key: Union[Dict, None]


class DependentCaseData(BaseModel):
    case_id: Text
    # dependent_data: List[DependentData]
    dependent_data: Union[None, List[DependentData]] = None


class TestCase(BaseModel):
    url: Text
    method: Text
    remark: Text
    # assert_data: Union[Dict, Text] = Field(..., alias="assert")
    is_run: Union[None, bool]
    headers: Union[None, Dict, Text]
    requestType: Text
    requestData: Union[Dict, Text, None, list]
    dependence_case: Union[None, bool] = False
    dependence_case_data: Optional[Union[None, List["DependentCaseData"], Text]] = None
    sql_data: Union[list, Text, None]
    sql_assert: Union[list, Text, None]
    assert_data: Union[Dict, Text]
    # current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
    # sleep: Optional[Union[int, float]]
    process: Union[Dict, Text]



class Config(BaseModel):
    info: Dict
    mysql: Dict
    redis: Dict
    email: Dict
    # tester_name: Text
    # notification_type: Text = '0'
    # excel_report: bool
    # ding_talk: "DingTalk"
    # mysql_db: "MySqlDB"
    # mirror_source: Text
    # wechat: "Webhook"
    # email: "Email"
    # lark: "Webhook"
    # real_time_update_test_cases: bool = False
    # host: Text

class ResponseData(BaseModel):
    yaml_is_run: Union[None, bool, Text]
    yaml_remark: Text
    yaml_body: Any
    yaml_assert_data: Dict
    yaml_data: "TestCase"
    yaml_sql_data: Union[None, list, Text]
    yaml_sql_assert: Union[None, list, Text]

    req_url: Text
    req_method: Text
    req_headers: Dict

    res_sql_result: Union[bool, None]
    res_data: Any
    res_cookie: Dict
    res_time: Union[int, float]
    res_status_code: int

    file: Text
    is_decorator: bool


class SetupTeardown_Type(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    INSERT = "INSERT"
    DELETE = "DELETE"
    SELETE = "SELETE"
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
    
class YamlInfoData(BaseModel):
    host: Text
    url: Text
    method: Text
    remark: Text
    is_run: Union[None , bool]
    headers: Union[None , Dict]
    requestType: Text
    requestData: Union[None , Dict]
    assert_data: Union[None , Dict]
    process: Union[None , Dict]