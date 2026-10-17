# 重建和核验 v005

本检查点是两塔主体石材校准，不是 14 天项目的最终版本。源文件为已验收 v004。所有命令使用相对文件名示意，不依赖作者电脑目录。

## 重建

使用 Blender 5.2.2 LTS，关闭自动执行：

```sh
blender -b --disable-autoexec "海边巨塔城堡_v004_双塔层级窗群.blend" --python scripts/refine_v005.py -- --output "海边巨塔城堡_v005_双塔石砌校准.blend" --report reports/v005_build_validation.json
```

输出必须与输入文件不同。脚本只重建自身集合，隐藏并保留原主体对象；新对象链接原网格，仅采用对象级材质槽覆盖。再次运行可重建，不会叠加重复对象或材质。无需外部纹理、插件或下载。

## 真实渲染

```sh
blender -b --disable-autoexec -t 3 "海边巨塔城堡_v005_双塔石砌校准.blend" --python scripts/render_v005_review.py -- --views main,west,hero,west_stone --output-dir previews --prefix v005_final
```

近景固定 1000×750、20 样本；全景固定 900×600、16 样本。渲染脚本不保存工程，不改世界、灯光或曝光。每张渲染记录输入工程 SHA256。

## 重开核验

```sh
blender -b --disable-autoexec --python scripts/validate_v005.py -- --baseline "海边巨塔城堡_v004_双塔层级窗群.blend" --checkpoint "海边巨塔城堡_v005_双塔石砌校准.blend" --report reports/v005_delivery_validation.json
```

另从 v005 本身重跑建模脚本、输出另一个文件，再用同一核验脚本比较两份 v005，可以检验语义一致性。封存包中的重跑报告记录了本次实际结果。

## 预览净化

```sh
python scripts/clean_preview_metadata.py previews/example.png previews/example.png reports/example_metadata_check.json
```

该步骤只移除 PNG 文本/EXIF 元数据，保留压缩像素数据和色彩管理块，核对 IDAT 哈希不变。没有修图或生成式补画。
