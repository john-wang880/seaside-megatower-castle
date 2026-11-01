# 九视角导航 · v018

新增西塔低矮八角屋帽检查相机，不改路线、建筑、照明或原工程。
这是相机静帧与可选查看副本，不是人物连续行走或全城通行证明。

## 当前版本图片

本版实际渲染：

| 全景 | 西塔低矮屋帽 |
|---|---|
| ![v018全景](renders/hero.png) | ![v018西塔屋帽](renders/west_crown.png) |
全景1200×866、西塔屋帽1200×800，原80采样/世界/灯光/曝光。
最终图片来源与SHA见各自JSON，不使用旧原型图片冒充最终版。

## 明确保留的历史参考

| 参考视角 | 图片来源 |
|---|---|
| 主冠屋面 `renders/crown.png` | v017，主冠瓦片参考 |
| 西侧接近、东入口、内廊、楼梯、终点、小塔 | v016，各自原始JSON保留 |

| 西侧接近（v016） | 东侧入口（v016） |
|---|---|
| ![西侧](renders/west_approach.png) | ![入口](renders/east_portal.png) |
| 内廊转角（v016） | 回看楼梯（v016） |
| ![内廊](renders/bend.png) | ![楼梯](renders/upper_stairs.png) |
| 终点暗部（v016） | 离岸小塔（v016） |
| ![终点](renders/terminal.png) | ![小塔](renders/offshore_marker.png) |

主冠屋面（v017）：![主冠](renders/crown.png)

详见 `reports/historical_image_provenance.json`。这些未重渲染为v018，
也不声称逐像素等价。终点原有暗部保持；离岸小塔是独立资产。
历史v016八秒局部环绕视频仍为v016来源，不冒充v018影片。

## 可选查看副本

以下命令在仓库根目录执行；`blender`须替换为本机兼容Blender可执行文件路径。先恢复源文件：
```
python checkpoints/v018/restore_checkpoint.py
python checkpoints/v018/navigation/navigation.py --list
blender -b --disable-autoexec --python-exit-code 1 checkpoints/v018/restored/castle_v018.blend --python checkpoints/v018/navigation/navigation.py -- --view west_crown --output checkpoints/v018/restored/castle_viewer.blend
```
输出必须为另一个尚不存在的.blend文件；重复运行请选择新的输出名，工具不会覆盖已有查看副本。带空格的可执行文件/路径需按所用终端语法加引号。详见[恢复、打开与安全编辑](../QUICKSTART.md)。工具仅新增8个自有检查相机、
复用已有全景相机，并设置查看/选择状态；不覆盖源文件。`--list`列出9视角。

原静帧辅助工具 `render_manifest_still.py` 维持720×520/24采样快速预览，
默认4线程、可显式传 `--threads 8`；不能与本次原80采样正式静帧混淆。
原质量脚本 `render_hero_original_quality.py` / `render_crown_original_quality.py`
只在云端临时使用8线程，不修改源文件保存的3线程默认。

验证通过：9项标准Python测试，27项Blender深度原数据/查看副本断言。见reports。
源SHA：`c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`。

九张图片的完整来源映射：`reports/all_nine_image_provenance.json`；本版两相机实际姿态核对：`reports/current_camera_reconciliation.json`。
后侧屋帽亮白斜面在匹配v017基线中已存在，见`reports/rear_paired_visual_review.json`；不归因为新增瓦片，也不借此判断原材质原因。

## 平台边界：查看副本、单帧与影片不是同一工具
- 恢复/列视角/查看副本入口见[快速开始](../QUICKSTART.md)。已实际验证Linux；没有宣称在用户Windows电脑跑过。
- `render_manifest_still.py`原先无条件导入仅Unix提供的`resource`，会让Windows连单帧都无法开始。现在把Linux峰值RSS改为可选遥测：Linux仍记原`ru_maxrss`数值，Windows/macOS等或接口不可用时字段为`null`，**不是0、不是把未知单位当KiB**。渲染设置保持720×520/24采样，线程默认4；模拟平台测试不等于Windows实机验收。
- 单帧工具是快速预览，不是80采样正式成片；输出PNG和同名JSON请用新路径，现有该路径文件可能被覆盖。它不保存源blend。
- 已完成28秒影片的冻结脚本依赖Linux `fcntl`文件锁、`/proc`进程检查和`resource`，**不是Windows通用渲染器**。这些历史脚本/51文件身份保持不变以保存复现与审批绑定；不能为“兼容”随意跳过锁或挪用旧批准。Windows可先直接查看已备份MP4或用兼容Blender打开工程。

官方接口边界：[Python resource](https://docs.python.org/3/library/resource.html)、[Python fcntl](https://docs.python.org/3/library/fcntl.html)。修复范围仅单帧可选统计，不承诺整个影片流水线跨平台。
