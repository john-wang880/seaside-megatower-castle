# 中央桥墩表面去重：独立重建配方

只处理两对重叠的原始桥墩/墩脚长方体，不是新增支承、填洞或桥拱改形。保留原始网格，使用两个各16顶点的反向 Mask 隐藏旧组件，添加两个8顶点/6面精确并集长方体。现有材质、世界光照、拱券、桥面、地基和全部其他组件不变。

## 输入与运行

唯一模型输入为已接受 v020，SHA256：
`673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614`。
可从项目固定历史提交 `23fd4aaaceb64996913bfa3ff4109fc149737b9d` 的 v020 检查点及其恢复说明取得；本配方不联网、不下载、不安装软件。

使用现有 Blender **5.2.3 Linux**。不声称 Windows 或其他版本已经验证。路径可含空格/中文；以下每个路径保持引号。输出文件和报告必须不存在，源模型不会保存或覆盖。

```sh
"/absolute/path/to/blender" --background --threads 8 --disable-autoexec --python-exit-code 1 \
  --python "/absolute/path/to/rebuild/scripts/build.py" -- \
  --source "/absolute/path/to/source v020.blend" \
  --plan "/absolute/path/to/rebuild/plan.json" \
  --output "/absolute/path/to/new result/candidate.blend" \
  --report "/absolute/path/to/new result/build.json"
```

显式运行此命令即为选择执行；不需要额外维护者授权。不会渲染、发布、修改 Git 或自动接受新版本。`build.py` 仅依赖同目录 `deep_snapshot.py`、本包 `plan.json`、Python 标准库和 Blender 自带模块，无历史工作目录或私有候选模型依赖。

成功要求进程返回0，报告中四项 `checks` 全部为true，`source_unchanged` 为true，并核对输出SHA。报告绑定输入源、计划、执行脚本和快照助手SHA，保存前后检查稳定。输出通过同目录临时文件和排他硬链接发布，拒绝覆盖现有路径；`--python-exit-code 1` 必须保留。Python优化模式会由不可被`-O`删除的显式RuntimeError保护拒绝。

## 验证范围与当前证据

`python test_preflight.py`：四项纯Python失败控制（错误源SHA、已存在输出、源/输出别名、`-O`），不启动Blender。
`python test_plan.py`：两项纯Python数学测试（两个精确并集体积恒等式、盒面朝向/正体积）。

`evidence/build_guard_tests.json` 保存所有者已运行的四项失败控制；`evidence/builder_hardening.json` 记录最初执行脚本SHA及唯一保护修订。原始已执行脚本另存所有者本地 `work/v021_pier_surface/executed/`，**不是此配方运行依赖**。

原候选457348…由修订前脚本在正常非优化模式下构建，并通过独立技术验证。当前硬化版仅修改`-O`保护，几何配方不变；**本包的干净隔离 Blender 重建尚待执行，不能以纯测试代替模型重建结果**。之后必须对新输出独立验证：原始完整场景数据仅有明确32权重/两Mask增量、非目标求值属性逐项保持、两个并集占用集合精确、同朝向重复皮肤消失。报告中的面记录互补检查并非完整属性或场景认证。`.blend` 文件字节可能不同；完整持久/求值语义等价需独立证明。实际图像验收与几何验收分开。

## 可逆回退

同时关闭两个 `V021 candidate | original pier … rollback mask` 的视图/渲染开关，并同时隐藏两个 `V021 candidate | central pier … surface union` 对象（视图及渲染）。原始32顶点和24面始终保存在原网格。只切换一半会重现重复表面或留下缺失表示；不要删除原始组件。该回退仅针对这次表面替换，不撤销用户后续任意编辑。
