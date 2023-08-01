from common.config import YAML_FILE
from utils.other.models import Config
from utils.other.yaml_control import YamlHandler

#获取config文件配置
_data = YamlHandler(YAML_FILE).get_yaml_data()
config = Config(**_data)
