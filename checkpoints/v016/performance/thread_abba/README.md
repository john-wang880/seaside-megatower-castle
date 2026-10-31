# 同像素线程性能对照（不改模型默认）

Blender 5.2.3 LTS、此云端9个可用逻辑CPU，v016原模型SHA `d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb`。
四个顺序全新进程，线程数3、8、8、3。原相机/世界/灯光/曝光及80采样质量保留，统一720×520、CPU Cycles、固定种子0、OIDN accurate。没有其他Blender并行干扰。

|线程|两次渲染秒数|平均秒数|
|---|---|---|
|3|157.64 / 158.57|158.10|
|8|65.89 / 66.40|66.15|

此单机单视角测试8线程平均耗时约缩短58%，即2.39倍速度；四张解码RGB逐像素完全相同。PNG文件字节因渲染耗时元数据不同而不同。峰值RSS约1.34–1.35GB（KiB原始量见报告），未建立可靠内存下降。8线程CPU秒数约增加10.4%，是缩短等待而非更省总计算量。

**限制：** 每配置只有两次、一个云端和一个低分辨率视角，不推广为所有相机/分辨率/机器的速度保证。导航工具自身是24采样，不能说已对该配置测得2.39倍。原模型仍固定3线程，导航工具默认仍4线程；只添加显式 `--threads 8` 可选参数，不改变用户机器默认或任何保存的场景。

`results/`保留四张原始PNG、各次设置/资源/时间报告、日志、汇总及PNG元数据解释。`renderer_change_validation.json`记录导航渲染正文归一化AST一致；另有4个参数测试及独立代码复核。

## 复现
依赖Python3与Pillow、兼容Blender、Linux的/proc及CPU亲和性接口。先按仓库说明恢复原v016文件；输出目录必须不存在，且不能与其他Blender渲染重叠：
```
python checkpoints/v016/performance/thread_abba/run_abba.py --blender /path/to/blender --source /path/to/castle_v016.blend --output-dir /new/path/results
```
不保存、不覆盖源模型；复现实测脚本要求恰好9个可用CPU，并验证源哈希。
