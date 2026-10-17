# 重建和核验 v004

本检查点是选择性窗群扩展，不是 14 天项目的最终版本。源文件为已验收 v003。所有命令使用相对文件名示意，不依赖作者电脑目录。

## 重建

使用 Blender 5.2.2 LTS，关闭自动执行：

```sh
blender -b --disable-autoexec "海边巨塔城堡_v003_双塔样板窗洞.blend" --python scripts/refine_v004.py -- --output "海边巨塔城堡_v004_双塔层级窗群.blend" --report reports/v004_build_validation.json
```

输出必须与输入文件不同。脚本只重建自身集合，隐藏并保留原墙体对象。再次运行可重建，不会叠加重复窗框。无需外部纹理、插件或下载。

## 真实渲染

```sh
blender -b --disable-autoexec -t 3 "海边巨塔城堡_v004_双塔层级窗群.blend" --python scripts/render_v004_review.py -- --views main_tower,west_tower,hero --output-dir previews --prefix v004
```

全高近景固定 1000×1000、20 样本；全景固定 900×600、16 样本。渲染脚本不保存工程，不改世界、灯光或曝光。每张渲染记录输入工程 SHA256。

## 重开核验

```sh
blender -b --disable-autoexec --python scripts/validate_v004.py -- --baseline "海边巨塔城堡_v003_双塔样板窗洞.blend" --checkpoint "海边巨塔城堡_v004_双塔层级窗群.blend" --report reports/v004_delivery_validation.json
```

另从 v004 本身重跑建模脚本、输出另一个文件，再用同一核验脚本比较两份 v004，可以检验语义一致性。封存包中的重跑报告记录了本次实际结果。

## 预览净化

```sh
python scripts/clean_preview_metadata.py previews/example.png previews/example.png reports/example_metadata_check.json
```

该步骤只移除 PNG 文本/EXIF 元数据，保留压缩像素数据和色彩管理块，核对 IDAT 哈希不变。没有修图或生成式补画。
