# Claude-Chan 校服版（独立 Fork）

本仓库是 [Ivanfangsc/claude-chan](https://github.com/Ivanfangsc/claude-chan) 的独立 Fork：
<https://github.com/chevalG/claude-chan>。上游提交历史、MIT 代码许可证和素材授权说明都保留。

## 与 GPT-Chan 的关系

Claude-Chan 和 GPT-Chan 是两个独立项目：

- 独立仓库：本目录是独立 Git 仓库，`origin` 指向上面的 Fork，`upstream` 指向上游原仓库。
- 独立启动入口：`start-claude-chan.bat`。
- 独立配置和运行状态：`data/`（端口 `47801`，单实例键 `claude-chan-uniform-pet`）。
- 独立资产目录：`resources/assets-uniform/`。
- 独立状态适配：继续使用 Claude Code hook 的状态接口（idle / waiting / thinking /
  confirmation / complete / error / drowsy / reading / writing），没有为了复用去改 GPT-Chan 的五状态。
- 两者可以同时运行，互不抢占端口和单实例锁。

## 校服版内容

角色依据用户提供的 Claude-Chan 校园制服三视图和抱书坐姿参考制作：

- 橘色长发、琥珀色眼睛、向日葵发饰、黑色蝴蝶结发带保持不变；
- 白色短袖衬衫、深蓝色蝴蝶结、深灰格纹百褶裙、白色中筒袜、棕色乐福鞋；
- 道具是深色精装书（封面有简单的橙色星形标记），不使用 GPT-Chan 的笔记本电脑；
- 所有状态都在普通教室学生椅上，双手与书、腿的接触关系在制作时逐状态检查。

状态与片段：

| 状态 | 循环 | 说明 |
| --- | --- | --- |
| idle / waiting | H3 单段 K0→K0 loop（共用） | 抱书坐着，呼吸与轻微摇晃 |
| thinking | H3 单段 K0→K0 loop | 指尖抵下巴，另一只手扶书 |
| reading | H3 单段 K0→K0 loop | 摊开的书，视线沿书页移动，不翻页 |
| writing | H3 单段 K0→K0 loop | 羽毛笔在摊开的书页上书写 |
| complete | 程序化呼吸 loop | 把书抱在胸前，温柔微笑 |
| confirmation | 程序化呼吸 loop | 举手询问 |
| drowsy | 程序化呼吸 loop | 闭眼打瞌睡 |
| error | oneshot 关键帧 | 吃惊、抱紧书 |

状态之间的过渡为 1 秒余弦交叉溶解（`scripts/make_uniform_transitions.py`）；
程序化 loop 见 `scripts/make_uniform_loops.py`；manifest 由 `scripts/make_uniform_manifest.py` 生成。
H3 loop 使用 MiniMax H3 的单段 K0→K0 生成，导出时用 `export_frames.py --retime` 做首尾提速；没有使用 MB 桥接。生成产物在本地 `resources/assets-uniform/videos/`。

## 素材与许可证

代码和文档沿用上游 MIT 许可证。角色设计来自 ZipZipPipe（CC BY-NC-SA 4.0）；
本 Fork 新制作的校服素材同样是该人设的二次创作，按 CC BY-NC-SA 4.0 发布：

> 角色素材来自 [Claude-Chan](https://github.com/Ivanfangsc/claude-chan)，人设原作
> [ZipZipPipe](https://www.bilibili.com/opus/1233069202138464289)，CC BY-NC-SA 4.0。

Claude 是 Anthropic, PBC 的商标；本项目是非官方同人作品，与 Anthropic 无关联。

素材文件体积较大，沿用上游做法不进 Git（见 `.gitignore`）；发布时需要单独打包。
具体授权条款见 [ASSETS-LICENSE.md](../ASSETS-LICENSE.md) 和 [LICENSE](../LICENSE)。

## 运行

```bat
start-claude-chan.bat
```

或从源码：

```bat
cd /d "%~dp0"
.venv\Scripts\python.exe -m claude_chan
```

调试面板在源码运行时可用；Hook 服务为 `http://127.0.0.1:47801/event`，
可用上游 README 里的 Claude Code 配置方式接入。

## 验收记录

- 关键帧：8 个状态（idle / thinking / reading / writing / complete / confirmation / drowsy / error）并排、深浅背景和腿部局部检查通过；waiting 与 idle 共用。
- loop 抽帧：idle、thinking、reading、writing 每段 12 帧检查，书、手、腿和椅子保持；reading/writing 的书页朝向有轻微变化，writing 的羽毛笔偏大，这是当前接受的艺术风格选择。
- 实机：idle、thinking、reading、writing、confirmation、complete 的 target/current 正确；error 用 `StopFailure` 触发为 sticky oneshot；drowsy 在临时 15 秒阈值下触发；waiting 与 idle 共用素材，QC 未单独构造后台任务场景。
- 过渡是 1 秒余弦交叉溶解；素材文件在本地不随仓库发布。
