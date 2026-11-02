> 新增可选功能：导出时加 `--editing-index`，在派生副本手动运行 Text 后提供四组已接受几何的选择入口。默认关闭，不修改模型或相机，不自动取消隐藏。详见 [EDIT_INDEX_GUIDE.md](EDIT_INDEX_GUIDE.md)。当前独立证据见 `qa/edit_index/`。下面保留的既有质量／相机说明仍适用；旧报告不是本次索引验证证据。

# v028 检查副本：18书签与可选单树 HIGH / LOW

独立的可选浏览副本，不修改验收工程。保留前16个检查视角的精确姿态和历史出处，新增接待室入口及校正后的回望入口视角，共18个手动书签、17台新增相机。历史向下看的漫游影片不变；新书签不是连续通行认证。

当前绑定模型 f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096，47,806,291字节。本地真实v028清单下的OFF/HIGH/LOW导出、重开及独立原生验证均通过；远程发布后仍需独立复核。旧v027结果仅存于provenance/v027_quality_acceptance，未冒充新版结果。

## 显式导出

```sh
"$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 --python-expr 'import sys; sys.dont_write_bytecode=True' --python "$tool/export_inspection.py" -- --repository-root "$repo" --source "$restored_v028" --output "$new_viewer" --report "$new_report" --tree-mode HIGH
```

使用已有Blender5.2.3和新的输出路径；真实清单必须匹配，拒绝旧源、未知未来版本、歧义版本目录、符号链接、覆盖或优化模式。不会安装、下载、自动执行脚本、渲染或保存源工程。

- 不传`--tree-mode`：OFF，普通检查副本，不启用树按钮；OFF不是LOW。
- 显式HIGH/LOW：启用单棵树的两个手动按钮，只改变原V019树Mask及两个细节对象的六个可见性标志。
- 接待室三个Mask、148个原组件权重、四个替代网格、两盏灯及所有其他对象不受树切换影响。

打开副本后，可在Text Editor手动运行`INSPECT28 | Run manually for bookmarks.py`，再使用View3D的Castle检查面板。不要开启全局自动执行。按钮不自动保存。HIGH/LOW不能撤销用户随后做的任意几何或材质编辑。切换不同OFF/ON副本时，旧注册界面可能被所有权保护拒绝；先卸载原副本自己的界面或重启Blender，不强删外部注册类。

LOW仍保存全部高细节网格，不承诺缩小文件、减少载入内存或提升特定速度。没有Windows或桌面点击性能测试。

## 已完成的本地验证

18项实现预检、24项独立路径预检、9项质量控制纯测试、8项比较纯测试；对OFF/HIGH/LOW三份新副本分别通过13类源数据保护、18书签、27项原生负例、注册重复和重开。c46历史v018只用于原树目标组件的独立谱系检查，不是运行时依赖，也不表示整场景回退。详情见qa/README.md。
