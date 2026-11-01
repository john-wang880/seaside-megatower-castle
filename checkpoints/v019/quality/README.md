# 可选：前景树 HIGH / LOW 浏览副本

只切换西侧入口旁这一棵树，**不改验收工程、不生成新模型版本**。HIGH显示v019精细针叶；LOW恢复原v018叶簇，同时隐藏两个新增细节对象，旧木干始终保持。

## 先恢复原工程，再导出副本

从完整仓库根目录运行（Blender路径替换成你已有的5.2.3）：
```sh
python checkpoints/v019/restore_checkpoint.py
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python checkpoints/v019/quality/export_viewer.py -- --source checkpoints/v019/restored/castle_v019.blend --mode HIGH --output checkpoints/v019/restored/my_tree_viewer.blend --report checkpoints/v019/restored/my_tree_viewer.json
```
要默认打开原始低细节，使用`--mode LOW`。输出与报告必须使用**新的文件名**，父目录须存在；工具拒绝覆盖、源文件别名和符号链接目标。不会下载、安装软件或修改验收源文件。导出仅接受原始验收SHA `e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a`，不接受已经编辑过的文件作源。

代码只使用Blender/标准Python。已在云端Linux Blender5.2.3实际导出和验证；**未实测原生Windows界面/文件系统**。导出采用同目录临时文件加独占硬链接；文件系统不支持时会安全失败，而不是降级覆盖源文件。

## 在副本里使用两个按钮

1. 打开新导出的`my_tree_viewer.blend`，不要打开验收原件做修改。
2. 在Blender **Text Editor（文本编辑器）**选择`CASTLE | v019 tree quality controls (manual)`，手动运行脚本。
3. 到3D视图侧栏（N键）的 **Castle** 标签，选择 **HIGH** 或 **LOW**。

脚本不自动执行、不安装插件、不注册自动处理器，也不自动保存文件。重新启动Blender后需再次手动运行文本；**无需全局开启自动执行脚本**。你若要保存浏览设置，请另存自己的副本，不覆盖已校验工程。

按钮总是成对调整原叶簇Mask与两个新对象的视口/渲染开关。重复点击同一模式不会增加对象或改变几何。混合开关、错误权重/Mask、隐藏祖先集合/视图层、多个集合路径等状态会拒绝切换，不会偷偷取消其他隐藏设置。修正自己手动改动的显示状态后再使用。

这只是显示质量开关，**不是恢复所有编辑的按钮**：不会撤销你后来修改的几何或材质。HIGH=v019、LOW=v018的等价验证针对本工具从精确源工程导出的新副本。

## 资源与验证边界

LOW仍把完整高细节网格保存在文件中，所以**不是缩小文件或保证降低初次加载内存的工具**。渲染/求值资源变化仅按实际对照测量报告，不泛化为所有机器的性能保证。其他树林不变，不批量扩展高细节树。

独立测试检查所有原始数据、两种模式的求值几何、再打开、反复切换、手动注册/卸载和故障拒绝。HIGH应与v019一致；LOW应与v018原树冠一致（保留但不启用的专用298顶点权重明确排除于低细节渲染语义）。全部其他网格、材质、灯光、相机和路线保持。

侧栏通过Blender后台API注册/操作测试，不冒充实际鼠标点击或原生Windows交互测试。针叶开放背面、原主干接触包络和有限路线检查的既有边界不变。

### 实际同相机测量

1200×866、原80采样、同一云端CPU/8线程的两个独立进程：HIGH峰值2,122,336KiB，LOW为2,017,628KiB，本次约少102.25MiB；渲染76.83/75.09秒。仅一组顺序观察，不宣称普遍加速。HIGH与原v019对照图、LOW与原v018对照图解码后像素分别完全一致。见[验证汇总](reports/SUMMARY.json)。图片仍可查看[HIGH](../previews/approach_after.png) / [LOW](../previews/approach_before.png)；未通过重打光制造差异。
