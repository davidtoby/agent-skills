#!/usr/bin/env python3
"""Read-only macOS disk scan; exact deletion targets require --apply."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import stat
import subprocess

TARGETS = {
    'npm-downloads': ['.npm/_cacache'],
    'pip-downloads': ['Library/Caches/pip/http', 'Library/Caches/pip/http-v2'],
    'ollama-models': ['.ollama/models'],
    'lmstudio-models': ['.lmstudio/models'],
}
MODELS = {'ollama-models', 'lmstudio-models'}
PROTECTED = ['Documents', 'Desktop', 'Downloads', 'Pictures', 'Movies', 'Music',
             '.key', '.npm/_npx', '.cache/uv', 'Library/Caches/pip/wheels',
             '.ollama/id_ed25519', '.ollama/id_ed25519.pub', '.ollama/history',
             '.lmstudio/conversations', '.lmstudio/credentials',
             '.lmstudio/config-presets', '.lmstudio/user-files',
             '.lmstudio/bin', '.lmstudio/extensions', '.lmstudio/.internal',
             'Library/Application Support', 'Library/Containers', 'Library/Mobile Documents']


def check_path(home_dir, key, path):
    if path not in [home_dir / relative for relative in TARGETS[key]]:
        raise ValueError('Path is outside the exact allowlist')
    for component in [path, *path.parents]:
        if component.is_symlink():
            raise ValueError('Symbolic link path: ' + str(component))
    if not path.exists():
        return None
    original = path.lstat()
    if not stat.S_ISDIR(original.st_mode) or original.st_uid != os.getuid():
        raise ValueError('Target must be a current-user-owned directory')
    if os.path.ismount(path):
        raise ValueError('Target is a mount point')
    def walk_error(exc):
        raise exc
    for base, dirs, files in os.walk(path, followlinks=False, onerror=walk_error):
        for name in dirs + files:
            child = Path(base) / name
            info = child.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise ValueError('Symbolic link inside target: ' + str(child))
            if info.st_dev != original.st_dev or os.path.ismount(child):
                raise ValueError('Nested filesystem: ' + str(child))
            if info.st_uid != os.getuid():
                raise ValueError('Foreign-owned entry: ' + str(child))
    return original


def du_bytes(path):
    result = subprocess.run(['du', '-sk', str(path)], capture_output=True, text=True,
                            timeout=300, check=True)
    return int(result.stdout.split()[0]) * 1024


def identify_process(command):
    """Parse arguments privately and return only a tool label."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if not tokens:
        return None
    names = [Path(token).name.lower() for token in tokens[:3]]
    executable = tokens[0].lower()
    if names[0] == 'ollama' or '/ollama.app/' in executable:
        return 'ollama'
    # ps does not quote application paths containing spaces.
    app_prefix = command.lower()[:200]
    if names[0] in {'llmster', 'lms'} or '/lm studio.app/' in app_prefix or '/.lmstudio/' in executable:
        return 'lmstudio'
    for name in names:
        if name in {'npm', 'npm-cli.js', 'npx', 'npx-cli.js'}:
            return 'npm'
        if name in {'pip', 'pip3', 'uv'} or name.startswith('pip3.'):
            return 'pip'
    return None


def active_tools():
    output = subprocess.check_output(['ps', '-axo', 'pid=,args='], text=True)
    result = []
    for line in output.splitlines():
        pieces = line.strip().split(None, 1)
        if len(pieces) == 2 and pieces[0].isdigit():
            tool = identify_process(pieces[1])
            if tool:
                result.append({'pid': int(pieces[0]), 'tool': tool})
    return result


def blockers(key, processes):
    tool = {'npm-downloads': 'npm', 'pip-downloads': 'pip',
            'ollama-models': 'ollama', 'lmstudio-models': 'lmstudio'}[key]
    return [process for process in processes if process['tool'] == tool]


def remove_target(home_dir, key, path, authorize_models=False, process_reader=active_tools):
    if key in MODELS and not authorize_models:
        raise ValueError('Current-task model deletion authorization is required')
    running = blockers(key, process_reader())
    if running:
        raise ValueError('Related active processes: ' + json.dumps(running))
    original = check_path(home_dir, key, path)
    if original is None:
        return 'absent'
    current = path.lstat()
    if (original.st_dev, original.st_ino) != (current.st_dev, current.st_ino):
        raise ValueError('Target changed during verification')
    if blockers(key, process_reader()):
        raise ValueError('A related process started during verification')
    shutil.rmtree(path)
    if key in MODELS:
        path.mkdir(mode=stat.S_IMODE(original.st_mode))
        path.chmod(stat.S_IMODE(original.st_mode))
    return 'removed'


def save_report(out, report):
    temp = out / 'audit.json.tmp'
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    temp.chmod(0o600)
    temp.replace(out / 'audit.json')
    gib = 1024 ** 3
    latest = report.get('free_bytes_after', report['free_bytes_before'])
    lines = ['# macOS 磁盘清理记录', '', '模式：' + report['mode'],
             f"开始时可用：{report['free_bytes_before']/gib:.2f} GiB",
             f"最新可用：{latest/gib:.2f} GiB",
             f"观测空间变化：{report.get('observed_free_bytes_change', 0)/gib:.2f} GiB", '',
             '| 目标 | 占用 GiB | 状态 |', '|---|---:|---|']
    for action in report['actions']:
        lines.append(f"| `{action['path']}` | {action.get('allocated_bytes_before', 0)/gib:.3f} | {action['status']} |")
        if action.get('error'):
            lines.append('\n错误：' + action['error'] + '\n')
    if 'home_inventory' in report:
        rows = []
        for line in report['home_inventory']:
            size, separator, path = line.partition('\t')
            if separator and size.isdigit():
                rows.append((int(size) * 1024, path))
        lines += ['', '## 主目录一层占用（只读扫描）', '',
                  '| 路径 | 占用 GiB |', '|---|---:|']
        for size, path in sorted(rows, reverse=True)[:25]:
            lines.append(f'| `{path}` | {size/gib:.2f} |')
        if not report.get('home_inventory_complete'):
            lines += ['', '扫描存在无法访问的路径，结果不完整。']
    if report.get('home_inventory_note'):
        lines += ['', report['home_inventory_note']]
    lines += ['', '仅删除精确限定的目标；保留个人文件、项目依赖、应用配置、凭据、对话和推理组件。',
              '保护路径检查仅验证存在性，不等于全部文件内容完整性校验。',
              '已删缓存和模型以后使用时可能需联网下载。',
              '空间变化受后台写入和 APFS 共享块影响，以实际测量为准。']
    summary = out / 'report.md'
    summary.write_text('\n'.join(lines) + '\n')
    summary.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--targets', nargs='+', choices=TARGETS, default=list(TARGETS))
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--authorize-model-deletion', action='store_true')
    parser.add_argument('--report-dir', type=Path)
    parser.add_argument('--skip-home-inventory', action='store_true')
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        parser.error('This CLI supports macOS only')
    if args.apply and MODELS.intersection(args.targets) and not args.authorize_model_deletion:
        parser.error('Select cache-only targets or provide model deletion authorization')
    if args.apply and os.geteuid() == 0:
        parser.error('Do not run cleanup as root or via sudo')
    home_dir = Path.home()
    for component in [home_dir, *home_dir.parents]:
        if component.is_symlink():
            parser.error('Home path contains a symbolic link; inspect manually')
    timestamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = (args.report_dir or home_dir / 'disk-cleanup-reports' / timestamp).expanduser().absolute()
    for relative in [r for paths in TARGETS.values() for r in paths]:
        target = (home_dir / relative).resolve()
        if out.resolve() == target or target in out.resolve().parents:
            parser.error('Report directory must be outside all cleanup targets')
    for component in [out, *out.parents]:
        if component.is_symlink():
            parser.error('Report path contains a symbolic link')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error('Use a new or empty report directory to preserve existing files')
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    if (out / 'audit.json').exists():
        parser.error('Report directory contains an existing audit; choose a new directory')
    if any(p.is_symlink() for p in [out / 'audit.json', out / 'audit.json.tmp', out / 'report.md']):
        parser.error('Report output contains a symbolic link')
    disk = '/System/Volumes/Data'
    report = {'mode': 'apply' if args.apply else 'scan',
              'started_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'free_bytes_before': shutil.disk_usage(disk).free, 'actions': [],
              'active_tools': active_tools()}
    protected = [home_dir / p for p in PROTECTED if (home_dir / p).exists()]
    save_report(out, report)
    for key in dict.fromkeys(args.targets):
        for relative in TARGETS[key]:
            path = home_dir / relative
            action = {'target': key, 'path': str(path), 'status': 'checking'}
            report['actions'].append(action)
            save_report(out, report)
            print('Checking:', path, flush=True)
            try:
                if check_path(home_dir, key, path) is None:
                    action['status'] = 'absent'
                else:
                    action['allocated_bytes_before'] = du_bytes(path)
                    action['status'] = 'scanned'
                    action['blocked_by'] = blockers(key, active_tools())
                    save_report(out, report)
                    if args.apply:
                        action['status'] = 'deleting'
                        save_report(out, report)
                        action['status'] = remove_target(home_dir, key, path, args.authorize_model_deletion)
                        action['empty_or_absent_after'] = not path.exists() or not any(path.iterdir())
                        if not action['empty_or_absent_after']:
                            raise RuntimeError('Target was repopulated; do not retry blindly')
            except (OSError, ValueError, subprocess.SubprocessError, RuntimeError) as exc:
                action['status'] = 'error'
                action['error'] = str(exc)
            report['free_bytes_after'] = shutil.disk_usage(disk).free
            report['observed_free_bytes_change'] = report['free_bytes_after'] - report['free_bytes_before']
            save_report(out, report)
            print(json.dumps(action, ensure_ascii=False), flush=True)
    if not args.apply and not args.skip_home_inventory:
        print('Scanning top-level home usage (read-only)...', flush=True)
        try:
            result = subprocess.run(['du', '-x', '-k', '-d', '1', str(home_dir)],
                                    capture_output=True, text=True, timeout=300)
            report['home_inventory'] = result.stdout.splitlines()
            report['home_inventory_complete'] = result.returncode == 0
        except subprocess.TimeoutExpired:
            report['home_inventory_complete'] = False
            report['home_inventory_note'] = 'Read-only inventory timed out after 300 seconds'
    report['protected_paths_preserved'] = all(path.exists() for path in protected)
    report['free_bytes_after'] = shutil.disk_usage(disk).free
    report['observed_free_bytes_change'] = report['free_bytes_after'] - report['free_bytes_before']
    report['finished_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    save_report(out, report)
    print('Report:', out / 'report.md', flush=True)
    print(json.dumps({'free_GiB': report['free_bytes_after']/1024**3,
                      'observed_change_GiB': report['observed_free_bytes_change']/1024**3,
                      'protected_paths_preserved': report['protected_paths_preserved']}, indent=2))
    return 1 if any(a['status'] == 'error' for a in report['actions']) or not report['protected_paths_preserved'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
