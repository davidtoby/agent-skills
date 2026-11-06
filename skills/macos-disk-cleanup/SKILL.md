---
name: macos-disk-cleanup
description: Safely inspect and reclaim macOS disk space from regenerable package caches, and remove local AI models when explicitly requested. Use for Mac disk cleanup, low disk space, or deleting Ollama and LM Studio models while preserving work files and application stability.
---

# macOS 磁盘清理

先盘点，再按当前授权范围清理，核对实际可用空间并交付操作记录。占用大不代表可以删除。调用技能本身不授权删除模型或个人资料；过去的删除授权不适用于新的清理任务。

## 授权和保留范围

- 用户要求“执行磁盘清理”时，可检查后清理下表中的 npm / pip 下载缓存，不重复请求泛泛确认。只要求分析、创建或测试技能时，仅扫描。
- 仅在当前任务明确要求删除时清理 Ollama / LM Studio 模型。已明确授权的项继续执行；未授权的候选项先列出具体路径、占用、用途和后果，等待答复。
- 保留源码、项目 node_modules / 虚拟环境、文档、桌面、下载、媒体、云同步、聊天附件、应用容器、应用支持数据、凭据（包括 `~/.key`）、系统文件、备份和快照。不要清空废纸篓、卸载应用或删除未知大文件来凑释放量。
- 保留 Ollama 密钥、历史和日志；保留 LM Studio 的 conversations、credentials、config-presets、user-files、bin、extensions 和内部配置。清理模型后重建空模型目录，保留权限。
- 保留 uv 缓存、npx 运行包、pnpm store、Playwright 浏览器、Docker 数据和推理组件，除非当前任务另有明确授权并完成用途检查。这些可能被服务使用或与环境存在链接关系。
- 不删除运行中浏览器、飞书等应用的缓存，不自动退出应用、终止推理或安装任务。有关进程阻挡时，说明进程和具体目标，继续不受影响的只读检查，等待用户关闭或授权停止。
- 不输出密钥、配置密文、对话正文或进程完整参数。脚本只在内存解析进程参数，输出工具名和 PID。不要上传扫描报告或自动发布技能。

## 流程和脚本

1. 确认 macOS 和真实用户主目录。用 `df -k /System/Volumes/Data` 读取 APFS 数据卷可用空间；根卷 Used 不能代表完整数据占用。
2. 执行默认只读盘点（脚本路径相对本技能目录）：

   ```bash
   python3 scripts/disk_cleanup.py
   ```

   列出四类目标及主目录一层占用，不删除文件。大目录扫描可能耗时，保持进展说明。权限不足时记录扫描不完整，不用管理员权限扩大删除范围。
3. 按盘点和当前授权选择目标：

   | 标识 | 唯一删除范围 | 后果 |
   |---|---|---|
   | npm-downloads | `~/.npm/_cacache` | 安装包需重新下载，保留 `_npx` |
   | pip-downloads | `~/Library/Caches/pip/http` 和 `http-v2` | 安装包需重新下载，保留 wheels |
   | ollama-models | `~/.ollama/models` | 全部本地模型删除，再用需下载 |
   | lmstudio-models | `~/.lmstudio/models` | 全部本地模型删除，保留推理组件 |

   不按整个 `.lmstudio` 占用承诺模型释放量，其中还包含运行组件和用户资料。
4. 执行已授权的下载缓存清理：

   ```bash
   python3 scripts/disk_cleanup.py --targets npm-downloads pip-downloads --apply
   ```

   当前任务明确授权删除模型后，选择相应标识并传入授权标志；标志必须反映真实用户授权：

   ```bash
   python3 scripts/disk_cleanup.py --targets ollama-models lmstudio-models --apply --authorize-model-deletion
   ```

   `--report-dir` 可指定全新的报告目录，默认 `~/disk-cleanup-reports/<UTC时间戳>/`。先写审计，再删除。脚本拒绝符号链接、挂载点、非当前用户文件及关联活动进程；不要用 `rm -rf` 绕过拒绝。
5. 读审计记录，再核对 `df` 和目标剩余占用。错误时停止对应项，报告实际状态，不将部分成功说成全部完成。`protected_paths_preserved` 仅验证原有保护路径仍存在，不等于全部文件内容校验或系统稳定性测试。
6. 报告本轮实际空间变化、最新可用空间、删除类别、保留项、重新下载影响和本地 Markdown / JSON 链接。GiB 为 1024³ 字节；同时给 GB 时明确十进制含义。后台写入和 APFS 共享块会使目标占用之和与实际增量不同。

## 避免重复踩坑

- 不盲用 `npm cache clean --force`：版本实现可能删除整个 npm cache 根目录，影响 `_npx`；精确限定 `_cacache`。
- pip wheels 可能包含本地构建且难以重新获取的包，保留。
- Ollama blobs 与 manifests 相互引用，不删孤立大 blob。本脚本只支持已授权的全部模型清理；用户要求删个别模型时，用本机 Ollama CLI 列表和删除命令，不扩大范围。
- 自定义模型路径、链接或外部磁盘需要先定位、说明实际路径和授权范围，不为套用脚本迁移数据。
- 创建、更新或测试技能时，只跑只读盘点和临时目录测试，不能再次执行真实清理。
