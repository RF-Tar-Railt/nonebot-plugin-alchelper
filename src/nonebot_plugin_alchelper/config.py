from pydantic import Extra, BaseModel, Field
from typing import Optional, Set

class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    alchelper_command_start: Optional[Set[str]] = None
    """插件使用的命令前缀，如果不填则使用全局命令前缀 (COMMAND_START)"""

    alchelper_help: str = "help"
    """插件使用的帮助命令名称"""

    alchelper_help_index: bool = False
    """插件使用的帮助命令是否显示索引"""

    alchelper_help_max: int = -1
    """插件使用的帮助命令最大显示数量，-1 为不限制"""

    alchelper_statis: str = "statis"
    """插件使用的统计命令名称"""

    alchelper_statis_msgcount_default: int = Field(10, ge=1, le=120)
    """插件使用的统计命令默认显示消息数量"""
