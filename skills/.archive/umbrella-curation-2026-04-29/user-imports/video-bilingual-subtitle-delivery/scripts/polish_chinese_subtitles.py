#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

REPLACEMENTS = [
    (r'谢谢$', '非常感谢。'),
    (r'^好吧,', '好，'),
    (r',', '，'),
    (r'\.', '。'),
    (r'睡觉(\d+)小时', r'睡\1小时'),
    (r'晚上睡觉(\d+)小时', r'每晚只睡\1小时'),
    (r'或更长时间的男子', '以上的男性'),
    (r'男人通常每晚只睡四到五个小时 就会有睾酮', '长期每晚只睡4到5小时的男性，睾酮水平会'),
    (r'也就是10岁高龄的人', '相当于年长他10岁的人。'),
    (r'在健康的关键方面,缺乏睡眠会使一个人老化十年。', '所以就这一关键健康指标而言，睡眠不足会让男性一下老10岁。'),
    (r'而我们看到女性生殖健康因睡眠不足引起的等效障碍。', '女性生殖健康也会因睡眠不足受到同样程度的损害。'),
    (r'塔尼娅·库什曼审查员', 'Tanya Cushman：'),
    (r'审查员', '主持人'),
    (r'谢谢$', '谢谢。'),
    (r'非常感谢。$', '非常感谢。'),
    (r'睾丸明显小于', '睾丸会明显小于'),
    (r'男性的睾丸会明显小于睡觉7小时或更长时间的男子', '男性的睾丸会明显小于每晚睡7小时以上的男性'),
    (r'非谈判性的生物必要性', '不可妥协的生物必需品'),
    (r'不容商榷的生物需要', '不可妥协的生物必需品'),
    (r'高龄的人', '年长者'),
    (r'岁高龄', '岁'),
    (r'心脏病发作', '心梗'),
    (r'自然杀伤细胞', '自然杀伤细胞'),
]


def polish_line(zh: str, en: str = ''):
    s = zh.strip()
    for pattern, repl in REPLACEMENTS:
        s = re.sub(pattern, repl, s)
    s = re.sub(r'\s+', '', s)
    s = s.replace('，，', '，').replace('。。', '。')
    if s and s[-1] not in '。！？：”』】）':
        # Only auto-punctuate when line does not already look like a short fragment.
        if len(s) >= 6:
            s += '。'
    return s


def main():
    parser = argparse.ArgumentParser(description='Polish machine-translated Chinese subtitle lines with lightweight heuristic rules.')
    parser.add_argument('--input-json', required=True, help='JSON array with idx, zh and optional en')
    parser.add_argument('--output-json', required=True)
    args = parser.parse_args()

    items = json.loads(Path(args.input_json).read_text(encoding='utf-8'))
    out = []
    for item in items:
        out.append({
            'idx': item['idx'],
            'zh': polish_line(item['zh'], item.get('en', ''))
        })
    Path(args.output_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote={args.output_json}')


if __name__ == '__main__':
    main()
