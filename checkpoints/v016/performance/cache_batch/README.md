# 缓存批量渲染：不采用默认变更

同一v016原模型、8线程、80采样、720×520，两个全新进程分别缓存OFF与ON；各自依次渲染全景→内廊→全景。三组对应图像RGB逐像素完全一致，源文件未保存或改变。

|模式|各帧秒数|合计秒数|峰值RSS KiB|
|---|---|---|---|
|OFF|63.71 / 79.12 / 67.24|210.07|1,381,916|
|ON|63.42 / 77.66 / 62.14|203.22|1,448,816|

ON仅减少约3.26%等待，增加约4.84%峰值内存；只有一次固定先OFF后ON的比较，不建立普遍收益。**不启用缓存默认、不继续微调**。这只是未改场景、切换相机，不证明任意几何/材质修改后的缓存正确性。

完整原图、设置、耗时、审查见results。相机配方快照来自v015导航，但两个实际使用配方与当前v016完全相同；渲染模型明确是v016而非v015。矩阵检查排除新相机预求值快照陈旧问题。

复现需要Linux、Python3/Pillow、Blender及恰好9个可用逻辑CPU；禁止同时运行其他Blender，输出目录需不存在：
```
python checkpoints/v016/performance/cache_batch/run_cache_comparison.py --blender /path/to/blender --source /path/to/castle_v016.blend --output-dir /new/path/results
```
