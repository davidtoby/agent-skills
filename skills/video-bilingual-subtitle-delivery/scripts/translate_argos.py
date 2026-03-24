#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Translate grouped English subtitle items to Simplified Chinese with Argos Translate.')
    parser.add_argument('--input-json', required=True, help='JSON array of subtitle items with idx/en fields')
    parser.add_argument('--output-json', required=True, help='JSON array of {idx, zh}')
    args = parser.parse_args()

    import argostranslate.translate  # lazy import inside venv-backed runtime

    items = json.loads(Path(args.input_json).read_text(encoding='utf-8'))
    installed = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed if lang.code == 'en'), None)
    to_lang = next((lang for lang in installed if lang.code == 'zh'), None)
    if not from_lang or not to_lang:
        raise SystemExit('Argos en->zh model is not installed. Install it first.')
    translation = from_lang.get_translation(to_lang)

    out = []
    for item in items:
        zh = translation.translate(item['en']).strip()
        out.append({'idx': item['idx'], 'zh': zh})

    Path(args.output_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote={args.output_json}')


if __name__ == '__main__':
    main()
