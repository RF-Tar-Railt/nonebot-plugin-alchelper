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
from nonebot import get_driver, require, get_plugin_config
from nonebot.plugin import PluginMetadata
from collections import deque

require("nonebot_plugin_orm")
require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.extension import Extension, add_global_extension
from nonebot_plugin_orm import get_session
from sqlalchemy import select, func

from .config import Config
from .model import Record

driver = get_driver()
global_config = driver.config
_config = get_plugin_config(Config)
__version__ = "0.4.0"
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
    ns.prefixes = list(_config.alchelper_command_start or global_config.command_start)

    _help = Alconna(
        _config.alchelper_help,
        Args["page", int, 0],
        Option("--hide", help_text="是否列出隐藏命令", action=store_true, default=False),
        meta=CommandMeta(
            description="显示所有命令帮助",
            usage="可以使用 --hide 参数来显示隐藏命令",
            example=f"${_config.alchelper_help} 1",
        ),
    )
    _help.shortcut("帮助", {"prefix": True, "fuzzy": False})
    _help.shortcut("所有帮助", {"args": ["--hide"], "prefix": True, "fuzzy": False})
    _help.shortcut(r"第(\d+)页帮助", {"args": ["{0}"], "prefix": True, "fuzzy": False})
    _statis = Alconna(
        _config.alchelper_statis,
        Arg("type", Literal["show", "most", "least"], "most"),
        Arg("count", int, _config.alchelper_statis_msgcount_default),
        meta=CommandMeta(
            description="命令统计",
            example=f"${_config.alchelper_statis} msg",
        ),
    )
    _statis.shortcut("消息统计", {"args": ["show"], "prefix": True})
    _statis.shortcut("命令统计", {"args": ["most"], "prefix": True})

#record = deque(maxlen=256)

class HelperExtension(Extension):
    @property
    def priority(self) -> int:
        return 16

    @property
    def id(self) -> str:
        return "nonebot_plugin_alchelper:HelperExtension"

    async def parse_wrapper(self, bot, state, event, res: Arparma) -> None:
        if res.source != _statis.path:
            async with get_session() as session:
                session.add(Record(source=res.source, origin=res.origin))
                await session.commit()

add_global_extension(HelperExtension())

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
    if _config.alchelper_help_max < 1:
        command_string = (
            "\n".join(
                f" {str(index).rjust(len(str(len(cmds))), '0')} {slot.header_display} : {slot.meta.description}"
                for index, slot in enumerate(cmds)
            )
            if _config.alchelper_help_index
            else "\n".join(f" - {cmd.name} : {cmd.meta.description}" for cmd in cmds)
        )
    else:
        page = arp.query[int]("page", 0)
        max_page = len(cmds) // _config.alchelper_help_max + 1
        if page < 1 or page > max_page:
            page = 1
        header += "\t" + pages.format(current=page, total=max_page)
        command_string = (
            "\n".join(
                f" {str(index).rjust(len(str(page * _config.alchelper_help_max)), '0')} {cmd.name} : {cmd.meta.description}"
                for index, cmd in enumerate(
                    cmds[
                        (page - 1)
                        * _config.alchelper_help_max : page
                        * _config.alchelper_help_max
                    ],
                    start=(page - 1) * _config.alchelper_help_max,
                )
            )
            if _config.alchelper_help_index
            else "\n".join(
                f" - {cmd.name} : {cmd.meta.description}"
                for cmd in cmds[
                    (page - 1)
                    * _config.alchelper_help_max : page
                    * _config.alchelper_help_max
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
    async with get_session() as session:
        records = (await session.scalars(
            select(Record).order_by(Record.time.desc())
        )).fetchall()
    if not records:
        return await statis_cmd.finish("暂无命令记录")
    return await statis_cmd.finish(
        "最近的命令记录为：\n"
        + "\n".join(
            [
                f"[{i}]: {records[i].origin}"
                for i in range(min(arp.query[int]("count", _config.alchelper_statis_msgcount_default), len(records)))
            ]
        )
    )


@statis_cmd.assign("type", "most")
async def statis_cmd_most(arp: Arparma):
    async with get_session() as session:
        stmt = select(Record.source, func.count(Record.source).label("count")).group_by(Record.source).order_by(func.count(Record.source).desc())
        records = await session.execute(stmt)
    records = records.scalars().fetchall()
    if not records:
        return await statis_cmd.finish("暂无命令记录")
    return await statis_cmd.finish(
        "以下按照命令使用频率排序\n"
        + "\n".join(f"[{k}] {v[0]}" for k, v in enumerate(records[:arp.query[int]("count")]))
    )
    


@statis_cmd.assign("type", "least")
async def statis_cmd_least(arp: Arparma):
    async with get_session() as session:
        stmt = select(Record.source, func.count(Record.source).label("count")).group_by(Record.source).order_by(func.count(Record.source).asc())
        records = await session.execute(stmt)
    records = records.scalars().fetchall()
    if not records:
        return await statis_cmd.finish("暂无命令记录")
    return await statis_cmd.finish(
        "以下按照命令使用频率排序\n"
        + "\n".join(f"[{k}] {v[0]}" for k, v in enumerate(records[:arp.query[int]("count")]))
    )
