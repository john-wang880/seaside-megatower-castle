> **历史v020记录，不是最新模型入口。** 最新工程见[仓库首页](../../README.md)。本文v020恢复/复现及绑定673模型的工具请在固定历史工作树内运行：
> ```sh
> git worktree add --detach ../castle-v020-history 23fd4aaaceb64996913bfa3ff4109fc149737b9d
> cd ../castle-v020-history
> python checkpoints/v020/restore_checkpoint.py
> ```
> 之后仍在该工作树内执行本文命令。已有同名目录请改用新路径；不要把v021模型传给旧版工具。旧版模型/图像与代码在Git历史保留，展陈图未改标为新版本。

# v020 程序复现与精确恢复

恢复验收模型请优先运行`restore_checkpoint.py`，它复原673开头的精确SHA；程序重建用于检查配方，不替代归档。

## 来源

唯一来源是历史v019/e717，可从固定历史工作树恢复：
```sh
git worktree add --detach ../castle-v019-history 15ed444cf3d1396d1d16e8fe5c176f8e39082435
python ../castle-v019-history/checkpoints/v019/restore_checkpoint.py
```
工作树目录必须不存在；无需重新下载或运行任何新软件。

## 三阶段配方

```sh
python checkpoints/v020/reproduce/rebuild.py --source ../castle-v019-history/checkpoints/v019/restored/castle_v019.blend --blender /absolute/path/to/existing/blender --output-dir /new/path/threshold-result
```
在Linux Blender5.2.3上，以仅复制公开代码/计划及精确来源的独立中文/空格路径完成三阶段真实执行；输入和执行文件保持。程序化保存产生不同SHA是预期元数据差异，必须通过独立语义验证，不用肉眼相似替代。

`reproduce/README.md`和`RECIPE_FILES.json`保留实际执行前冻结的状态记录，因此其中“尚未真实运行”是当时状态。后续执行证据见`reports/rebuild/`；完整原始与求值语义独立比较精确通过，4项负例与边界几何复验见`reports/repeat/`，最终独立验证与发布状态见验收收据。不得把控制器成功状态当作艺术/几何验收。

独立验证命令见`qa/README.md`。它需要精确v019来源、673验收模型及新生成模型，比较原始/求值语义、材质、变换及明确例外；最终几何结果需读取`focused_geometry_pass`，不能只看退出码。

本包不联网、不安装、不渲染、不自动发布。原生Windows执行尚未实测；中文/空格路径的真实检查在Linux完成。没有把旧失败候选或私有独立树文件作为必要输入。
