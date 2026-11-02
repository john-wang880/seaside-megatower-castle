# v029 候选检查副本：20书签与可选编辑索引

**当前本地原生验证通过，远程重放与发布核验仍待完成。** 绑定候选源：

- SHA256：`4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5`
- 大小：47,825,562字节。
- 20个手动书签：原18条相机记录完全不变，新增 `stores_entry`、`stores_return`；19台新增检查相机，默认全景沿用源相机。
- 5组可选几何选择入口，默认关闭，见 [EDIT_INDEX_GUIDE.md](EDIT_INDEX_GUIDE.md)。

规范源仍由项目发布流程决定。本工具只接受最新真实清单中的已审阅v029身份；若仓库仍以v028为最新版本，或出现未知未来版本，会明确拒绝，不使用旧清单回退、不伪造清单。

## 导出独立副本

使用已有Blender5.2.3和**尚不存在**的输出文件；输出父目录须已存在。以下命令须在正式v029清单与源模型可用后执行，不是要求当前绕过待验收状态。

Linux示例（路径按实际位置填写）：

```sh
export PYTHONDONTWRITEBYTECODE=1
"$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python-expr 'import sys; sys.dont_write_bytecode=True' \
  --python "$tool/export_inspection.py" -- \
  --repository-root "$repo" --source "$restored_v029" \
  --output "$new_viewer" --report "$new_report" \
  --tree-mode HIGH --editing-index
```

PowerShell示例（**Windows原生尚未验证**）：

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
& 'C:\Existing Blender\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 `
  --python-expr 'import sys; sys.dont_write_bytecode=True' `
  --python 'D:\Castle\scripts\current_inspection\export_inspection.py' -- `
  --repository-root 'D:\Castle' --source 'D:\CastleWork\castle_v029.blend' `
  --output 'D:\CastleWork\new_inspection.blend' --report 'D:\CastleWork\new_inspection.json' `
  --tree-mode HIGH --editing-index
```

无自动安装、下载、渲染或源工程保存。拒绝旧源、未知/歧义版本、符号链接、覆盖和优化模式。独占硬链接发布不受文件系统支持时明确失败，不回退为覆盖写入。

## 手动使用与可选功能

打开派生副本，在Text Editor中手动运行 **`INSPECT29 | Run manually for bookmarks.py`**，再使用View3D的 **Castle检查** 面板。不要开启全局自动执行。新Text不自动注册、不安装插件，按钮不自动保存。

- 不传 `--tree-mode`：OFF，仅不启用树质量按钮；OFF不是LOW。
- 显式 `--tree-mode HIGH` 或 `LOW`：启用原V019单棵树的质量按钮，只改变该树Mask与两个细节对象的六个可见性标志，不改房间、其他森林或旧版回退控制。
- `--editing-index`：显式加入5组选择按钮；省略时关闭，与树质量按钮独立。
- 书签只选择检查相机/视图，不偷偷修改画幅、质量、灯光或曝光。新室内参考画幅为960×694；其他书签各有历史参考画幅，若当前画幅不同，人工核对构图，不宣称画幅已自动匹配。
- 新两书签来自候选的实际渲染相机回执，不是连续漫游、完整通行或结构安全认证。历史v018/v026影片仍属于历史模型，未重新标为v029。

LOW仍保存全部高细节网格，不承诺缩小文件、减少载入内存或提升特定速度。按钮不能认证或撤销日后的任意几何/材质编辑；请先另存编辑成果。不同配置副本共用受保护注册机制，如遇身份冲突，先卸载原副本自己的面板或重启Blender，不强删外部注册类。

## 当前验证状态与历史证据

当前77项纯Python测试通过（45运行时、24独立预检、8比较），覆盖版本/源身份、路径/发布保护、目录别名、选择事务、面板条件及新增相机/五组映射。原18条相机记录、原接待室20灯具/入口石肋/HIGH树映射比对不变。四种导出配置完成3阶段原生检查：13类源保护、20书签/19新增相机、5组/45目标、27质量负例、37选择负例、6面板场景及64次LOW拒绝通过。注册重复、重开及选择事务亦已验证。 没有Windows桌面点击通过声明。

当前本地证据为 `VALIDATION.json` 和 [qa/v029_current/README.md](qa/v029_current/README.md)，实际摘要为 `qa/v029_current/reports/SUMMARY.json`。当前发布清单为 `PUBLIC_PAYLOAD.json`；远程仍待验证。旧当前清单已原样保存在 `provenance/v028_prior_current_tool/`；原 `qa/edit_index/`、`qa/validate_modes.py`、`reports/`、`REMOTE_REPLAY.md` / `EDIT_INDEX_REPLAY.md` 均保留历史意义，不作为当前通过证明。`provenance/`内各回执保持原始源版本；本次新增两条回执明确绑定上述候选源。当前原生验证已完成；发布负责人还需完成新远程恢复与重放，本工具不预先宣称远程完成。

当前独立QA重放入口是 `qa/v029_current/run_qa.py`；其中历史来源README示例里的 `qa/edit_index/run_qa.py` 路径应替换为此新目录，脚本及参数保持原样。原生输入需要当前源、历史v018树谱系基线和四份全新导出副本及回执；不使用旧版本QA执行当前验收。
