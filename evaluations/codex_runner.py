"""Codex CLI 어댑터. stdin 프롬프트를 받아 최종 JSON만 stdout에 출력한다."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    binary = os.environ.get('SKILL_EVAL_CODEX_BIN') or shutil.which('codex')
    if not binary:
        raise RuntimeError('codex CLI가 필요합니다.')
    prompt = sys.stdin.read()
    model = os.environ.get('SKILL_EVAL_MODEL', 'gpt-6.1-sol')
    # 호스트 검색 생략 플래그만으로는 ~/.agents/skills 목록이 제거되지 않아 명시적으로 끈다.
    paths = set()
    for root in (Path.home() / '.agents/skills', Path.home() / '.codex/skills', Path.home() / '.codex/skills/.system'):
        for skill in root.glob('*/SKILL.md'):
            paths.update((str(skill), str(skill.resolve()), str(skill.parent), str(skill.parent.resolve())))
    disabled_skills = '[' + ','.join('{path=' + json.dumps(path) + ', enabled=false}' for path in sorted(paths)) + ']'
    with tempfile.TemporaryDirectory(prefix='composition-codex-') as temp:
        output = Path(temp) / 'answer.json'
        command = [
            binary, 'exec', '--model', model, '--ephemeral', '--ignore-user-config', '--ignore-rules',
            '--skip-git-repo-check', '--sandbox', 'read-only',
            '--disable', 'skill_search',
            '--disable', 'shell_tool', '--disable', 'apps', '--disable', 'multi_agent',
            '--disable', 'shell_snapshot',
            '--disable', 'plugins', '--disable', 'remote_plugin',
            '-c', 'project_doc_max_bytes=0', '-c', 'web_search="disabled"',
            '-c', 'skills.config=' + disabled_skills,
            '-c', 'skills.max_context_tokens=1',
            '-c', 'model_reasoning_effort="low"',
            '-c', 'developer_instructions="Return only the requested JSON. Do not use tools, read files, or access network resources. Work solely from the supplied prompt."',
            '--json', '--output-last-message', str(output), '-',
        ]
        completed = subprocess.run(command, input=prompt, text=True, capture_output=True, cwd=temp, timeout=300)
        # CLI 상태·사용량을 보존하되 인증 파일이나 환경 변수는 기록하지 않는다.
        events = []
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            events.append(event)
        item_types = sorted({event.get('item', {}).get('type') for event in events if event.get('item', {}).get('type')})
        tools = [event for event in events if event.get('item', {}).get('type') in ('command_execution', 'mcp_tool_call', 'web_search', 'file_change', 'collab_tool_call', 'image_view')]
        usage = [event for event in events if event.get('type') == 'turn.completed']
        notices = [event['item'] for event in events if event.get('item', {}).get('type') == 'error']
        print(json.dumps({'runner': 'codex', 'model': model, 'reasoning_effort': 'low', 'disabled_skill_paths': len(paths), 'returncode': completed.returncode, 'usage': usage, 'tool_events': len(tools), 'item_types': item_types, 'notices': notices}, ensure_ascii=False), file=sys.stderr)
        if completed.returncode or tools or not output.is_file():
            print(completed.stderr[-4000:], file=sys.stderr)
            raise RuntimeError('Codex 실행 실패 또는 도구 사용 감지')
        value = json.loads(output.read_text())
        print(json.dumps(value, ensure_ascii=False))


if __name__ == '__main__':
    main()
