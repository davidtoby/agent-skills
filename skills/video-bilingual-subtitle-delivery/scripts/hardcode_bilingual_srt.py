#!/usr/bin/env python3
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

import pysubs2
from PIL import Image, ImageDraw, ImageFont


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_video(video_path: Path):
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate',
        '-show_entries', 'format=duration', '-of', 'json', str(video_path)
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    stream = data['streams'][0]
    width = int(stream['width'])
    height = int(stream['height'])
    fps_num, fps_den = map(int, stream['r_frame_rate'].split('/'))
    fps = fps_num / fps_den
    duration = float(data['format']['duration'])
    return width, height, fps, duration


def load_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size=size)
    except Exception:
        fallback = '/Library/Fonts/Arial Unicode.ttf'
        return ImageFont.truetype(fallback, size=size)


def render_subtitle_png(text: str, out_path: Path, width: int, height: int, font_path: str, font_size: int, bottom_margin: int):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = load_font(font_path, font_size)

    max_text_width = int(width * 0.86)
    # PIL doesn't auto-wrap multiline captions, so wrap each paragraph greedily.
    wrapped_lines = []
    for raw_line in text.splitlines():
        words = raw_line.split(' ')
        if not words:
            wrapped_lines.append('')
            continue
        line = words[0]
        for word in words[1:]:
            test = line + ' ' + word
            bbox = draw.textbbox((0, 0), test, font=font, stroke_width=max(1, font_size // 18))
            if bbox[2] - bbox[0] <= max_text_width:
                line = test
            else:
                wrapped_lines.append(line)
                line = word
        wrapped_lines.append(line)
    wrapped_text = '\n'.join(wrapped_lines)

    stroke = max(1, font_size // 18)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center', spacing=max(4, font_size // 6), stroke_width=stroke)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_x, pad_y = 28, 14
    box_w = min(width - 40, text_w + pad_x * 2)
    box_h = text_h + pad_y * 2
    box_x = (width - box_w) // 2
    box_y = max(0, height - bottom_margin - box_h)

    draw.rounded_rectangle((box_x, box_y, box_x + box_w, box_y + box_h), radius=18, fill=(0, 0, 0, 128))
    text_x = width // 2
    text_y = box_y + pad_y - bbox[1]
    draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255, 255), anchor='ma', align='center', spacing=max(4, font_size // 6), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    img.save(out_path)


def main():
    parser = argparse.ArgumentParser(description='Hardcode bilingual subtitles by generating PNG overlays and compositing with ffmpeg.')
    parser.add_argument('--video', required=True)
    parser.add_argument('--srt', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--font', default='/Library/Fonts/Arial Unicode.ttf')
    parser.add_argument('--font-size', type=int, default=34)
    parser.add_argument('--bottom-margin', type=int, default=56)
    parser.add_argument('--workdir', default=None)
    parser.add_argument('--keep-workdir', action='store_true')
    parser.add_argument('--video-preset', default='veryfast')
    args = parser.parse_args()

    video_path = Path(args.video)
    srt_path = Path(args.srt)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height, fps, duration = probe_video(video_path)
    fps_str = f'{fps:.6f}'
    subs = pysubs2.load(str(srt_path), encoding='utf-8')

    workdir = Path(args.workdir) if args.workdir else output_path.with_suffix('')
    if workdir.exists():
        shutil.rmtree(workdir)
    overlays_dir = workdir / 'overlays'
    overlays_dir.mkdir(parents=True, exist_ok=True)

    blank = overlays_dir / 'blank.png'
    Image.new('RGBA', (width, height), (0, 0, 0, 0)).save(blank)

    concat_path = workdir / 'subtitles.ffconcat'
    with concat_path.open('w', encoding='utf-8') as f:
        f.write('ffconcat version 1.0\n')
        cursor = 0.0
        idx = 0
        for line in subs:
            start = max(0.0, line.start / 1000.0)
            end = min(duration, line.end / 1000.0)
            text = line.text.replace('\\N', '\n').replace('\\n', '\n').strip()
            if end <= start:
                continue
            if start > cursor:
                f.write(f"file '{blank.resolve()}'\n")
                f.write(f'duration {start - cursor:.6f}\n')
            png = overlays_dir / f'{idx:04d}.png'
            render_subtitle_png(text, png, width, height, args.font, args.font_size, args.bottom_margin)
            f.write(f"file '{png.resolve()}'\n")
            f.write(f'duration {end - start:.6f}\n')
            cursor = end
            idx += 1
        if cursor < duration:
            f.write(f"file '{blank.resolve()}'\n")
            f.write(f'duration {duration - cursor:.6f}\n')
        # ffconcat requires the last file repeated without duration.
        f.write(f"file '{blank.resolve()}'\n")

    overlay_mov = workdir / 'subtitle_overlay.mov'
    run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_path),
        '-vf', f'fps={fps_str},format=rgba', '-c:v', 'qtrle', str(overlay_mov)
    ])
    run([
        'ffmpeg', '-y', '-i', str(video_path), '-i', str(overlay_mov),
        '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto[v]',
        '-map', '[v]', '-map', '0:a?',
        '-c:v', 'libx264', '-preset', args.video_preset, '-crf', '20',
        '-c:a', 'copy', '-movflags', '+faststart', '-pix_fmt', 'yuv420p',
        str(output_path)
    ])

    if not args.keep_workdir:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == '__main__':
    main()
