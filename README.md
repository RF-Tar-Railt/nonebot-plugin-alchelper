# nonebot-plugin-alchelper
基于 [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna), 适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的命令帮助插件。

## 安装

- 使用 nb-cli

```shell
nb plugin install nonebot-plugin-alchelper
```

- 使用 pip

```shell
pip install nonebot-plugin-alchelper
```

## 注意事项

本插件使用了 `nonebot-plugin-orm`, 这需要你自行配置数据库相关配置

例如，在使用 `sqlite` 作为数据库驱动的情况下，你需要

1. 运行 `pip install nonebot-plugin-alchelper[aiosqlite]`
2. 在.env配置文件中设置 `SQLALCHEMY_DATABASE_URL=sqlite+aiosqlite:///path-to-your-database`
3. 通过 `nb-cli` 运行 `nb orm upgrade`，然后通过 `nb orm check` 检查是否存在问题

更多内容参阅 [`orm文档`](https://deploy-preview-2545--nonebot2.netlify.app/docs/next/best-practice/db/).

## 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://nonebot.dev/docs/appendices/config)

### `alchelper_command_start`
 - 类型：`Optional[Set[str]]`
 - 默认：`None`
 - 说明：插件使用的命令前缀，如果不填则使用全局命令前缀 (COMMAND_START)

### `alchelper_help`
 - 类型：`str`
 - 默认：`"help"`
 - 说明：插件使用的帮助命令名称

### `alchelper_help_index`
 - 类型：`bool`
 - 默认：`False`
 - 说明：插件使用的帮助命令是否显示索引

### `alchelper_help_max`
 - 类型：`int`
 - 默认：`-1`
 - 说明：插件使用的帮助命令最大显示数量，-1 为不限制

### `alchelper_statis`
 - 类型：`str`
 - 默认：`"statis"`
 - 说明：插件使用的统计命令名称

### `alchelper_statis_msgcount_default`
 - 类型：`int`
 - 默认：`10`
 - 说明：插件使用的统计命令默认显示消息数量

## 使用

> /help
> /statis [count = 10] 
> /第3页帮助
> /命令统计
> /用户统计 @xxx