---
name: chinese-video-transcribe-pdf
description: 将中文字幕视频（或无字幕视频）转写为文本，并生成中文PDF报告。使用 faster-whisper 做语音转写（不受字幕限制），ReportLab 生成专业中文PDF。适用于YouTube、MP4等来源的视频。
---

# Chinese Video Transcription to PDF

将中文视频转写为结构化文本并生成专业中文PDF报告。

## 核心工作流

```
1. yt-dlp 下载视频
2. ffmpeg 抽出音频（16kHz PCM）  ← 关键步骤，避免视频解码问题
3. faster-whisper tiny/medium 模型转写（支持中文，无需字幕）
4. 整理 Markdown 报告内容
5. render_cn_report_pdf.py 生成 PDF
```

## Step 1：下载视频

```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  -o "~/Downloads/%(title)s.%(ext)s" "VIDEO_URL"
```

如下载中断，用 `--force-overwrites` 或直接重新运行（yt-dlp 自动续传）。

## Step 2：抽出音频（关键）

视频编码（AV1等）可能导致 Whisper 卡在43% 解码位置。**必须先抽出音频**：

```bash
ffmpeg -i "INPUT.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio.wav -y
```

参数说明：
- `-vn` 不要视频
- `-acodec pcm_s16le` 线性PCM，避免压缩编码问题
- `-ar 16000` Whisper 推荐的采样率
- `-ac 1` 单声道

## Step 3：转写（faster-whisper）

**不要用 openai-whisper CLI**（输出 pipe 到 `tail` 时无法观察进度，且某些视频编码会卡住）。

用 Python API + faster-whisper：

```python
from faster_whisper import WhisperModel

model = WhisperModel("tiny", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "/tmp/audio.wav",
    language="zh",
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=800)
)

results = []
for seg in segments:
    results.append({
        "start": round(seg.start, 2),
        "end": round(seg.end, 2),
        "text": seg.text.strip()
    })

# 保存为 JSON
import json
with open("/tmp/transcript.json", "w", encoding="utf-8") as f:
    json.dump({"segments": results, "language": info.language}, f, ensure_ascii=False, indent=2)
```

**模型选择**：
- `tiny` — 最快（3分钟左右转写40分钟），中文识别准确率已很好
- `medium` — 更准但更慢，适合关键内容

## Step 4：生成 Markdown 报告

根据转写内容整理 Markdown 结构，使用中文标题和自然段落。

## Step 5：生成 PDF

```bash
python3 $SKILL_DIR/../../../openclaw-imports/chinese-pdf-report/scripts/render_cn_report_pdf.py \
  --input /tmp/report.md \
  --output ~/Downloads/输出报告.pdf
```

字体自动注册：`SongtiSC`（正文）、`HeitiSC`（标题）、`KaitiSC`（引用）。

## 故障排除

| 问题 | 原因 | 解法 |
|------|------|------|
| youtube-transcript-api 返回 disabled | 视频字幕被禁用 | 直接用 faster-whisper 转写，无需字幕 |
| Whisper CLI 卡在43% | 视频流解码问题 | 先用 ffmpeg 抽出 WAV 音频再转写 |
| openai-whisper 无输出 | pipe 到 tail 导致 stdout buffer | 用 faster-whisper Python API，轮询进程状态 |
| PDF 中文乱码 | 字体未嵌入 | 用 render_cn_report_pdf.py，自动注册中文字体 |
| Whisper 模型下载慢 | 网络问题 | 提前下载好：`ls ~/.cache/whisper/` |

## 依赖安装

```bash
pip3 install faster-whisper
# 无需安装 openai-whisper CLI
```

## 输出标准

最终交付：
1. PDF 报告文件（中文无乱码）
2. 源 Markdown 文件
3. 转写 JSON 文件（可选）

文件命名规范：`主题_报告类型_YYYYMMDD.pdf`
