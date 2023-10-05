from arclet.alconna import (
    Alconna,
    Arg,
    Args,
    Arparma,
    Option,
    CommandMeta,
    namespace,
    store_true,
    command_manager,
)
from arclet.alconna.config import lang
from typing import Literal
from nonebot import get_driver, require
from nonebot.plugin import PluginMetadata
from collections import deque

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.extension import ExtensionExecutor

from .config import Config

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)
__version__ = "0.2.0"
__plugin_meta__ = PluginMetadata(
    name="Alconna 帮助工具",
    description="基于 nonebot-plugin-alconna，给出所有命令帮助以及统计",
    usage="""\
/help
/statis [count = 10] 
/第3页帮助
/命令统计
""",
    homepage="https://github.com/RF-Tar-Railt/nonebot-plugin-alchelper",
    type="application",
    config=Config,
    extra={
        "author": "RF-Tar-Railt",
        "priority": 3,
        "version": __version__,
    },
)

with namespace("alchelper") as ns:
    ns.prefixes = list(config.alchelper_command_start or global_config.command_start)

    _help = Alconna(
        config.alchelper_help,
        Args["page", int, 0],
        Option("--hide", help_text="是否列出隐藏命令", action=store_true, default=False),
        meta=CommandMeta(
            description="显示所有命令帮助",
            usage="可以使用 --hide 参数来显示隐藏命令",
            example=f"${config.alchelper_help} 1",
        ),
    )
    _help.shortcut("帮助", {"prefix": True})
    _help.shortcut("所有帮助", {"args": ["--hide"], "prefix": True})
    _help.shortcut("第(\d+)页帮助", {"args": ["{0}"], "prefix": True})
    _statis = Alconna(
        config.alchelper_statis,
        Arg("type", Literal["show", "most", "least"], "most"),
        Arg("count", int, config.alchelper_statis_msgcount_default),
        meta=CommandMeta(
            description="命令统计",
            example=f"${config.alchelper_statis} msg",
        ),
    )
    _statis.shortcut("消息统计", {"args": ["show"], "prefix": True})
    _statis.shortcut("命令统计", {"args": ["most"], "prefix": True})

record = deque(maxlen=256)
default_ext = ExtensionExecutor.globals[0]
async def patch_parse_wrapper(bot, state, event, res: Arparma):
    if res.source != _statis.path:
        record.append((res.source, res.origin))

default_ext.parse_wrapper = patch_parse_wrapper
default_ext._overrides["parse_wrapper"] = True


help_cmd = on_alconna(_help, auto_send_output=True)
statis_cmd = on_alconna(_statis, auto_send_output=True)


@help_cmd.handle()
async def help_cmd_handle(arp: Arparma):
    pages = lang.require("manager", "help_pages")
    cmds = [
        i
        for i in command_manager.get_commands()
        if not i.meta.hide or arp.query[bool]("hide.value")
    ]
    header = lang.require("manager", "help_header")
    if config.alchelper_help_max < 1:
        command_string = (
            "\n".join(
                f" {str(index).rjust(len(str(len(cmds))), '0')} {slot.name} : {slot.meta.description}"
                for index, slot in enumerate(cmds)
            )
            if config.alchelper_help_index
            else "\n".join(f" - {cmd.name} : {cmd.meta.description}" for cmd in cmds)
        )
    else:
        page = arp.query[int]("page")
        max_page = len(cmds) // config.alchelper_help_max + 1
        if page < 1 or page > max_page:
            page = 1
        header += "\t" + pages.format(current=page, total=max_page)
        command_string = (
            "\n".join(
                f" {str(index).rjust(len(str(page * config.alchelper_help_max)), '0')} {cmd.name} : {cmd.meta.description}"
                for index, cmd in enumerate(
                    cmds[
                        (page - 1)
                        * config.alchelper_help_max : page
                        * config.alchelper_help_max
                    ],
                    start=(page - 1) * config.alchelper_help_max,
                )
            )
            if config.alchelper_help_index
            else "\n".join(
                f" - {cmd.name} : {cmd.meta.description}"
                for cmd in cmds[
                    (page - 1)
                    * config.alchelper_help_max : page
                    * config.alchelper_help_max
                ]
            )
        )
    help_names = set()
    for i in cmds:
        help_names.update(i.namespace_config.builtin_option_name["help"])
    footer = lang.require("manager", "help_footer").format(help="|".join(help_names))
    return await help_cmd.finish(f"{header}\n{command_string}\n{footer}")


@statis_cmd.assign("type", "show")
async def statis_cmd_show(arp: Arparma):
    if not record:
        return await statis_cmd.finish("暂无命令记录")
    return await statis_cmd.finish(
        "最近的命令记录为：\n"
        + "\n".join(
            [
                f"[{i}]: {record[i][1]}"
                for i in range(min(arp.query[int]("count"), len(record)))
            ]
        )
    )


@statis_cmd.assign("type", "most")
async def statis_cmd_most(arp: Arparma):
    if not record:
        return await statis_cmd.finish("暂无命令记录")
    length = len(record)
    table = {}
    for i, r in enumerate(record):
        source = r[0]
        if source not in table:
            table[source] = 0
        table[source] += i / length
    sort = sorted(table.items(), key=lambda x: x[1], reverse=True)
    sort = sort[:arp.query[int]("count")]
    return await statis_cmd.finish(
        "以下按照命令使用频率排序\n"
        + "\n".join(f"[{k}] {v[0]}" for k, v in enumerate(sort))
    )


@statis_cmd.assign("type", "least")
async def statis_cmd_least(arp: Arparma):
    if not record:
        return await statis_cmd.finish("暂无命令记录")
    length = len(record)
    table = {}
    for i, r in enumerate(record):
        source = r[0]
        if r[source] not in table:
            table[source] = 0
        table[source] += i / length
    sort = sorted(table.items(), key=lambda x: x[1], reverse=False)
    sort = sort[:arp.query[int]("count")]
    return await statis_cmd.finish(
        "以下按照命令使用频率排序\n"
        + "\n".join(f"[{k}] {v[0]}" for k, v in enumerate(sort))
    )
