#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

TIME_RE = re.compile(r'^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})$')
SKILL_DIR = Path(__file__).resolve().parent.parent


def run(cmd):
    subprocess.run(cmd, check=True)


def parse_srt(path: Path):
    text = path.read_text(encoding='utf-8')
    blocks = re.split(r'\n\s*\n', text.strip())
    items = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip() != '']
        if len(lines) < 3 or not lines[0].isdigit():
            continue
        m = TIME_RE.match(lines[1])
        if not m:
            continue
        items.append({
            'idx': lines[0],
            'start': m.group(1),
            'end': m.group(2),
            'text': ' '.join(lines[2:]).strip(),
        })
    return items


def write_srt(items, path: Path, bilingual=False):
    out = []
    for i, item in enumerate(items, start=1):
        out.append(str(i))
        out.append(f"{item['start']} --> {item['end']}")
        out.append(item['en'])
        if bilingual:
            out.append(item['zh'])
        out.append('')
    path.write_text('\n'.join(out), encoding='utf-8')


def group_items(items, min_words=18):
    grouped = []
    buf = []
    start = None
    end = None
    count = 0
    for item in items:
        text = re.sub(r'\s+', ' ', item['text']).strip()
        if not text:
            continue
        if start is None:
            start = item['start']
        end = item['end']
        buf.append(text)
        wc = len(' '.join(buf).split())
        if wc >= min_words or text.endswith(('.', '?', '!', ':')):
            count += 1
            merged = ' '.join(buf)
            merged = re.sub(r'\s+([,.;?!])', r'\1', merged)
            grouped.append({'idx': str(count), 'start': start, 'end': end, 'en': merged})
            buf, start, end = [], None, None
    if buf:
        count += 1
        merged = ' '.join(buf)
        merged = re.sub(r'\s+([,.;?!])', r'\1', merged)
        grouped.append({'idx': str(count), 'start': start, 'end': end, 'en': merged})
    return grouped


def manual_placeholder(en: str):
    return '【待补中文】' + en


def run_skill_python(script_name: str, *args):
    venv_python = SKILL_DIR / '.venv-local' / 'bin' / 'python'
    if not venv_python.exists():
        raise SystemExit(f'Skill local venv missing: {venv_python}')
    script = SKILL_DIR / 'scripts' / script_name
    run([str(venv_python), str(script), *map(str, args)])


def translate_with_argos(items, output_dir: Path, polish_zh: bool):
    input_json = output_dir / 'grouped_items_for_translation.json'
    raw_output_json = output_dir / 'argos_translations.raw.json'
    final_output_json = output_dir / 'argos_translations.json'
    input_json.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')

    run_skill_python('translate_argos.py', '--input-json', input_json, '--output-json', raw_output_json)

    raw_items = json.loads(raw_output_json.read_text(encoding='utf-8'))
    if polish_zh:
        indexed = []
        en_map = {it['idx']: it['en'] for it in items}
        for it in raw_items:
            indexed.append({'idx': it['idx'], 'zh': it['zh'], 'en': en_map.get(it['idx'], '')})
        temp_for_polish = output_dir / 'argos_translations.with_en.json'
        temp_for_polish.write_text(json.dumps(indexed, ensure_ascii=False, indent=2), encoding='utf-8')
        run_skill_python('polish_chinese_subtitles.py', '--input-json', temp_for_polish, '--output-json', final_output_json)
    else:
        final_output_json.write_text(json.dumps(raw_items, ensure_ascii=False, indent=2), encoding='utf-8')
    return json.loads(final_output_json.read_text(encoding='utf-8'))


def translate_items(items, backend: str, output_dir: Path, polish_zh: bool):
    if backend == 'none':
        return [{'idx': it['idx'], 'zh': ''} for it in items]
    if backend == 'manual':
        return [{'idx': it['idx'], 'zh': manual_placeholder(it['en'])} for it in items]
    if backend == 'argos':
        return translate_with_argos(items, output_dir, polish_zh=polish_zh)
    raise SystemExit(f'Unsupported translate backend: {backend}')


def extract_audio(video: Path, wav: Path):
    run(['ffmpeg', '-y', '-i', str(video), '-vn', '-ac', '1', '-ar', '16000', str(wav)])


def transcribe_whisper(wav: Path, out_dir: Path, model: str, language: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    run([
        'whisper', str(wav),
        '--model', model,
        '--language', language,
        '--task', 'transcribe',
        '--output_format', 'srt',
        '--output_dir', str(out_dir),
    ])
    srt = out_dir / f'{wav.stem}.srt'
    if not srt.exists():
        raise SystemExit(f'Whisper output missing: {srt}')
    return srt


def main():
    parser = argparse.ArgumentParser(description='Build English and bilingual subtitles with local Whisper and pluggable translation backends.')
    parser.add_argument('--video', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--basename', default='video')
    parser.add_argument('--whisper-model', default='turbo')
    parser.add_argument('--whisper-language', default='en')
    parser.add_argument('--translate-backend', default='manual', choices=['manual', 'none', 'argos'])
    parser.add_argument('--group-min-words', type=int, default=18)
    parser.add_argument('--no-polish-zh', action='store_true', help='Skip Chinese post-processing rules for machine translated output.')
    args = parser.parse_args()

    video = Path(args.video)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    wav = output_dir / f'{args.basename}_audio.wav'
    whisper_dir = output_dir / 'whisper_out'
    english_raw = output_dir / f'{args.basename}_english_raw.srt'
    english_grouped = output_dir / f'{args.basename}_english_grouped.srt'
    bilingual = output_dir / f'{args.basename}_bilingual.srt'
    meta = output_dir / f'{args.basename}_subtitle_build.json'

    extract_audio(video, wav)
    whisper_srt = transcribe_whisper(wav, whisper_dir, args.whisper_model, args.whisper_language)
    english_raw.write_text(whisper_srt.read_text(encoding='utf-8'), encoding='utf-8')

    raw_items = parse_srt(english_raw)
    grouped = group_items(raw_items, min_words=args.group_min_words)
    write_srt(grouped, english_grouped, bilingual=False)

    translations = translate_items(grouped, args.translate_backend, output_dir, polish_zh=not args.no_polish_zh)
    zh_map = {it['idx']: it['zh'] for it in translations}
    bilingual_items = []
    for it in grouped:
        bilingual_items.append({**it, 'zh': zh_map.get(it['idx'], '')})
    write_srt(bilingual_items, bilingual, bilingual=True)

    meta.write_text(json.dumps({
        'video': str(video),
        'output_dir': str(output_dir),
        'basename': args.basename,
        'whisper_model': args.whisper_model,
        'whisper_language': args.whisper_language,
        'translate_backend': args.translate_backend,
        'polish_zh': not args.no_polish_zh,
        'raw_blocks': len(raw_items),
        'grouped_blocks': len(grouped),
        'artifacts': {
            'audio_wav': str(wav),
            'english_raw_srt': str(english_raw),
            'english_grouped_srt': str(english_grouped),
            'bilingual_srt': str(bilingual),
        }
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'english_raw={english_raw}')
    print(f'english_grouped={english_grouped}')
    print(f'bilingual={bilingual}')
    print(f'meta={meta}')


if __name__ == '__main__':
    main()
