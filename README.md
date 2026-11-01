# 海边巨塔城堡 · 持续精修

最新检查点：**[v019 西侧入口前景针叶树](checkpoints/v019/README.md)**。

仅替换入口旁一株近景树的可见树冠，保留原树与整个森林，新增层次分明的针叶枝条；建筑、道路、材质和原照明不改。不是整片森林升级，也不是性能优化：工程体积增加32.3%，本次两组独立进程峰值内存增加约119–125MiB。

- [原光照前后对照](checkpoints/v019/previews/tree_crop_pair.png) · [整体全景](checkpoints/v019/previews/hero_after.png)
- **[恢复、检查与原树切换](checkpoints/v019/README.md)**
- [可选 HIGH/LOW 浏览副本和两个按钮](checkpoints/v019/quality/README.md)（不改原工程）
- [恢复清单](checkpoints/v019/MANIFEST.json) · [持续计划](CONTINUATION.md)

克隆完整仓库（含model_chunks），运行 `python checkpoints/v019/restore_checkpoint.py`，用兼容Blender5.2.3LTS打开。逐块和整文件SHA-256验证，精确恢复原字节。

已从远端提交`3f7be81d9b2401fe7ec70cf5d0d225a1e3d10b9a`字节精确恢复并重验，见[验证收据](checkpoints/v019/reports/remote/VERIFIED.json)。当前只保留最新模型载荷。旧版Git历史保留，不强推、不永久清除历史。

## 历史呈现与工具（不是v019影片）
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含本次树冠修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
