# 重建和核验 v006

本检查点是两段真实石肋分块样板，不是 14 天项目的最终版本。源文件为已验收 v005。所有命令使用相对文件名示意，不依赖作者电脑目录。

## 重建

使用 Blender 5.2.2 LTS，关闭自动执行：

```sh
blender -b --disable-autoexec "海边巨塔城堡_v005_双塔石砌校准.blend" --python scripts/refine_v006.py -- --output "海边巨塔城堡_v006_局部石肋分块样板.blend" --report reports/v006_build_validation.json
```

输出必须与输入文件不同。脚本只重建自身集合，隐藏并保留原主体对象；新对象复制原网格，仅替换两个指定的独立八顶点分量；原网格及其余构件保留。再次运行可重建，不会叠加重复石块、对象或材质。无需外部纹理、插件或下载。

## 真实渲染

```sh
blender -b --disable-autoexec -t 3 "海边巨塔城堡_v006_局部石肋分块样板.blend" --python scripts/render_v006_review.py -- --views main_rib,west_rib,hero --output-dir previews --prefix v006
```

工艺近景固定 1200×1000、24 样本；全景固定 900×600、16 样本。渲染脚本不保存工程，不改世界、灯光或曝光。每张渲染记录输入工程 SHA256。

## 重开核验

```sh
blender -b --disable-autoexec --python scripts/validate_v006.py -- --baseline "海边巨塔城堡_v005_双塔石砌校准.blend" --checkpoint "海边巨塔城堡_v006_局部石肋分块样板.blend" --report reports/v006_delivery_validation.json
```

另从 v006 本身重跑建模脚本、输出另一个文件，再用同一核验脚本比较两份 v006，可以检验语义一致性。封存包中的重跑报告记录了本次实际结果。

## 预览净化

```sh
python scripts/clean_preview_metadata.py previews/example.png previews/example.png reports/example_metadata_check.json
```

该步骤只移除 PNG 文本/EXIF 元数据，保留压缩像素数据和色彩管理块，核对 IDAT 哈希不变。没有修图或生成式补画。

## 局部几何独立复验

```sh
blender -b --disable-autoexec -t 1 "海边巨塔城堡_v006_局部石肋分块样板.blend" --python scripts/validate_v006_sample_geometry.py -- --report reports/v006_sample_geometry_validation.json
```

此只读检查逐面匹配未触及的构件，验证八道真实缝宽与背衬退进、四处上下接触及闭合网格，不依赖渲染外观推断几何。
