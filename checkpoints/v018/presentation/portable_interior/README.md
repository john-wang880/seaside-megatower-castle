> **历史v018资料，不是当前模型。** 当前模型请看[版本v019](https://github.com/john-wang880/seaside-megatower-castle/blob/main/checkpoints/v019/README.md)。本目录保留历史呈现/工具/证据，不再携带旧模型清单和专用分块。旧命令须先在固定历史工作树中运行：
>
> ```sh
> git worktree add --detach ../castle-v018-history 89cce41edf648eef6487d54ee1ce2a46bbb0ae17
> cd ../castle-v018-history
> python checkpoints/v018/restore_checkpoint.py
> ```
>
> 这不会回退当前main或修改其文件。若目标目录已存在，请另选新路径。之后从该历史工作树根目录运行本页原有命令；源模型SHA必须为c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd。不要把v019模型交给绑定v018身份的旧影片脚本。

# 可选：可恢复的内廊影片重渲染工具

这是**新工具、新运行身份**，不是已经发布的影片生成脚本替换版。原 `../interior_route` 的51份冻结文件、已完成影片和原批准记录保持不变。仅当你确实需要自行重渲染时使用；查看工程或现成影片不需要运行它。

当前验证范围：42项专项测试、Linux原质量单帧实际渲染及恢复/拒绝未批准完整阶段检查、Windows接口模拟；原生Windows Blender/NTFS行为尚未实测。严格设置校验可能因平台/Blender构建差异而拒绝运行，工具不会为兼容而自动降低质量或忽略差异。

## 前置条件

从仓库根目录运行。需要完整仓库、已有兼容Blender5.2.3LTS，以及Python3.9或更新版本和Pillow。工具不下载安装任何软件。不支持`python -O/-OO`。Blender内部工作脚本只用标准库，不需要为Blender另装Pillow。

恢复原模型：
```sh
python checkpoints/v018/restore_checkpoint.py
```
预期输出`checkpoints/v018/restored/castle_v018.blend`，SHA256 `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`。已有不同数据不会覆盖；不要拿编辑稿或查看副本替代它。

## Windows PowerShell：先只检查

把Blender路径改成你**已有**的可执行文件位置。使用新的本地输出目录，不要放在冻结档案、已完成影片、源模型目录的上级目录或网络共享中。

```powershell
$tool = 'checkpoints/v018/presentation/portable_interior/run.py'
$source = 'checkpoints/v018/restored/castle_v018.blend'
$blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$out = 'work\my_portable_interior'
python $tool --source $source --blender $blender --output-dir $out --stage pilot --dry-run
```

`--dry-run`不会启动Blender、创建渲染尝试或自动安装依赖。它校验源文件、冻结输入、运行身份和已完成帧。真正的Blender版本/场景设置校验在工作进程打开源文件后、渲染前执行；仅dry-run成功不等于Windows渲染兼容性已通过。

如果明确要试渲染一帧：
```powershell
python $tool --source $source --blender $blender --output-dir $out --stage pilot --max-new-frames 1
```
这只生成一个当前身份下的真实试映帧，然后暂停；**不会**提前写入25帧试映完成记录或批准记录。再次dry-run应显示1帧有效、24帧待完成。再次使用预算1会继续下一帧，不是只做检查；只查询进度请保留`--dry-run`。

## 试映门槛与明确批准

若之后决定继续，去掉预算或设置新的预算可补齐25帧试映；这会消耗实际渲染时间。试映完整后工具仍停止，不会自动生成剩余311帧。先检查入口、转弯和终点的实际图片，再由拥有者明确批准当前身份。

批准文件放在输出目录**之外**，其格式为：
```json
{
  "approved": true,
  "identity": "这里必须是当前pilot_complete.json中完整identity对象，不是字符串",
  "approved_indices": "这里必须是当前pilot_complete.json中frames的index数组",
  "pilot_complete_sha256": "当前pilot_complete.json的SHA256小写十六进制"
}
```
以上只是结构说明，不能直接作为批准文件使用。批准只在你实际审看并同意后创建；历史云端批准不适用。不要修改运行身份或把旧帧复制进来骗过门槛。脚本不会替你自动批准。

完整阶段命令（仅在新的25帧试映已完成并获得明确批准后）：
```powershell
python $tool --source $source --blender $blender --output-dir $out --stage full --approval-file 'work\my_portable_approval.json'
```
默认只生成/校验PNG帧。只有显式加`--encode`才编码，且要求已有ffmpeg/ffprobe（可用`--ffmpeg`、`--ffprobe`指定路径）。缺少工具会报错，不会安装；原始帧保留。视频固定336帧、12fps、28秒、960×694、H264/yuv420p、无插帧/无音频。记录精确工具版本、命令、输入/输出哈希、时间戳检查和严格解码结果。

Linux同样使用这些Python参数；例如：
```sh
python checkpoints/v018/presentation/portable_interior/run.py --source checkpoints/v018/restored/castle_v018.blend --blender /absolute/path/to/blender --output-dir work/my_portable_interior --stage pilot --dry-run
```

## 中断、重复执行与锁

- 正常重复运行只跳过当前身份下校验通过的帧。源/代码/平台/可执行文件/缓存锁配置改变需要新目录和新的试映批准；不迁移历史身份。
- 每个输出目录有协调锁；另有工作进程自己持有的执行锁，协调进程意外退出时仍能保护正在渲染的子进程。不要删除锁文件、按文件年龄强行解除或杀掉不相关Blender。
- 执行锁位于Windows `%LOCALAPPDATA%\castle-portable-render\execution.lock`，Linux `$XDG_CACHE_HOME/castle-portable-render/execution.lock`（默认`~/.cache`）。所有合作进程必须使用同一个本地用户缓存配置。改变缓存位置会改变运行身份；故意使用不同用户/配置、手动启动的Blender不受这个锁协调，不能声称机器全局互斥。
- 云端受限集成测试显式设置`XDG_CACHE_HOME`到批准的工作区缓存；不因此访问用户PC或越过权限。普通用户无需照抄云端路径。
- 失败尝试保留在`attempts`，无效完成帧在身份/锁检查后才移入`quarantine`。新进程不会盲目接纳孤儿尝试。遇到共享冲突/权限问题直接停止，不采用删除后重试的破坏性做法。
- 不支持已知UNC网络输出；同步盘、其他网络挂载或跨主机锁语义未验证，请选择普通本地目录。代码不能自动识别所有挂载类型，不宣称分布式锁保证。
- 不修改模型、灯光或质量：仍是CPU、8线程、80样本、原相机路线和原曝光。兼容性不等于相同机器性能或跨平台像素逐字节一致。

## 测试
```sh
cd checkpoints/v018/presentation/portable_interior
python -m unittest -v test_portable
```
模拟测试不等于真实Windows运行证明。设计与限制见`DESIGN.md`；现成28秒影片仍由原冻结工具生成，不能冒称由本工具重做。

[单帧集成结果](reports/linux_integration.json)：含空格/中文输出路径，1帧验证后预算暂停，24帧仍待完成，没有新试映批准或影片。该帧像素与同Linux历史帧一致，仅证明这一次受控运行；没有据此保证所有平台一致。编码路径仅测试/代码审查，未启动新的完整编码。
