# 校服素材生成记录

本文件记录 `resources/assets-uniform/` 的生成方法。素材体积大、按上游约定不进 Git；
仓库里保留关键帧 manifest 和生成脚本。

## 环境

- ComfyUI：`D:/Comfyui-WF-2026.8.8/ComfyUI`
- 关键帧：Qwen Image 2.1 turbo int8 + 一致性 LoRA，9 步、euler、CFG 1，原生 RGBA
- 动画：MiniMax H3 low-VRAM（turbo v4 LoRA、10 步、H3SigmaRefiner、euler）

## 1. 关键帧

以用户提供的 Claude-Chan 校服坐姿参考为 idle：把它缩放到 1026×1824、人物约占画面高度 85%，
背景保留原生透明。其余状态用 Qwen Image 编辑（只改姿势/道具，保持人物、校服、椅子、
书本和构图），再按椅子/鞋所在的下部区域对齐到 idle。

关键帧文件名：

```
resources/assets-uniform/keyframes/claude-girl-uniform-{idle,thinking,reading,writing,complete,confirmation,drowsy,error}-transparent-9x16.png
```

`waiting` 与 `idle` 共用关键帧。

## 2. loop

- `idle / thinking / reading / writing`：MiniMax H3 单段 K0→K0 生成，首尾都锚在关键帧；
  导出时用 `export_frames.py --retime` 做首尾提速。生成时使用固定机位、纯青背景。
- `complete / confirmation / drowsy`：这些状态没有大幅动作，用
  `scripts/make_uniform_loops.py` 从关键帧生成 ±0.15% 的呼吸缩放 loop，保证书页、手指和椅子不变形。

## 3. 过渡

`scripts/make_uniform_transitions.py` 把所有状态与枢纽 A 之间的过渡做成 1 秒余弦交叉溶解，
两端分别是 idle loop 和目标状态 loop 的首帧（error 用关键帧）。所有状态都挂在枢纽 A，
因此状态之间通过 idle 中转，播放器不需要额外的 A/B 枢纽动画。

## 4. manifest 与导出

```bat
.venv\Scripts\python.exe scripts\make_uniform_manifest.py
D:\Comfyui-WF-2026.8.8\python\python.exe ..\GPT-Chan\scripts\export_frames.py
```

`make_uniform_manifest.py` 只登记已经存在 webm 的片段；导出脚本把 webm 转成桌宠播放的 AVIF，
并生成 `hitmask.png`。环境变量 `GPT_CHAN_ASSETS` 指向本目录：

```bat
set GPT_CHAN_ASSETS=C:\Users\Lenovo\Documents\Qoder\2026-11-16\f8841727\Claude-Chan\resources\assets-uniform
```

## 5. 检查

- 关键帧：`scripts/qc_uniform_keyframes.py`
- 实机：`scripts/qc_uniform_states.py`
- 逐段抽帧：`..\GPT-Chan\scripts\qc_strips.py`
