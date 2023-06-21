from common.config import ROOT_DIR
from common.utils.models import Config
from common.utils.yaml_control import YamlHandler

#获取config文件配置
_data = YamlHandler(f'{ROOT_DIR}common/config/config.yaml').get_yaml_data()
config = Config(**_data)