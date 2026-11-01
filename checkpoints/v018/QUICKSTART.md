# 恢复、打开与安全编辑

这些命令从**仓库根目录**执行，不是从`navigation`子目录执行。完整仓库必须含`model_chunks/`；单独下载清单或某个分块无法打开工程。已验证运行环境为Blender5.2.3LTS；原云端4.3.2不能打开该格式。

## 1. 恢复当前源模型
```sh
python checkpoints/v018/restore_checkpoint.py
```
输出：`checkpoints/v018/restored/castle_v018.blend`。脚本逐块和整文件校验；预期35,962,496字节，SHA-256 `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`。同字节文件可重复验证，已有不同内容不会覆盖。

在兼容Blender中打开该文件即可查看原工程。不要开启文件内脚本自动执行。后续手工编辑先另存为独立文件，不覆盖这份可校验源文件；它是回滚基线，不是实时同步的工作稿。

## 2. 需要容易找到的检查相机
先列出视角：
```sh
python checkpoints/v018/navigation/navigation.py --list
```
生成独立查看副本（不渲染，通常比生成影片快得多）：
```sh
blender -b --disable-autoexec --python-exit-code 1 checkpoints/v018/restored/castle_v018.blend --python checkpoints/v018/navigation/navigation.py -- --view west_crown --output checkpoints/v018/restored/castle_viewer.blend
```
`blender`代表你已安装的兼容可执行文件；不在PATH时替换为其完整路径。带空格路径按终端语法引用；Windows PowerShell运行带引号的程序路径需前置`&`。仓库不捆绑Blender程序。

打开生成的`castle_viewer.blend`。工具复用原全景相机，并新增8个自有检查相机，在保存副本中选中指定视角；建筑、森林、材质与照明不改。`west_crown`可换成列表中的`hero`、`west_approach`、`east_portal`、`bend`、`upper_stairs`、`terminal`、`offshore_marker`、`crown`。

**重复运行不会覆盖查看副本**：选择新的输出文件名；输出目录须已存在，源文件与输出不得同一路径。查看副本不符合原源SHA，不能拿它再次冒充规范源输入。需换初始视角时，从原恢复文件生成另一个副本即可。

## 3. 编辑前分清数据
- `v018`是接受模型。`audits/*rejected*`下的树形图、`whole_tree_concept`等是明确拒绝的试验，不要当作最新工程导入。
- 原树林/旧来源数据可能隐藏保留以便恢复；不要只因视口里暂时不可见就删除。复制/删除需先核对依赖与已验证备份。
- 新瓦片不是建筑结构/防水认证；内廊影片只覆盖限定路线，不是全城内部。
- [九视角图片](navigation/README.md)明确区分v018实际图与v017/v016历史参考；[28秒内廊影片](presentation/interior_route/STATUS.md)是v018。历史v016环绕没有后续屋面细节。

## 常见失败
- 缺少/损坏分块：重新取得完整仓库，对照错误中的分块SHA；不要跳过校验或拼接任意文件。
- “Output contains different data”：保留现有文件，使用`restore_checkpoint.py --output 新路径.blend`，不要让恢复操作覆盖编辑稿。
- “Source hash does not match”：输入了编辑稿/查看副本或损坏文件；重新恢复规范源，保留你的编辑文件。
- “Output already exists”：换一个新文件名；工具故意不覆盖。
- 找不到`navigation.py`：使用上面完整仓库相对路径，并先确认终端当前目录是仓库根目录。

本指南涉及恢复/副本工具，不自动启动长期渲染，也不会上传或删除Git历史。

验证环境：上述恢复/列视角/另存流程在Linux云端实际执行；Windows终端引用说明没有在用户本机实测。查看副本的27项Blender安全/数据保持检查另见[验证记录](navigation/reports/quickstart_cli_regression.json)，非GUI点击流程录像。

## 可选：自行重渲染内廊影片
[新的可恢复影片工具](presentation/portable_interior/README.md)提供独立运行身份、原质量试映、进度恢复与新批准门槛，不替换已发布影片的冻结脚本。Linux已做小范围集成与安全测试，Windows接口仅模拟、未实机验证；确实需要重渲染时再考虑。正常查看仍直接使用现成MP4，不必重跑数小时。
