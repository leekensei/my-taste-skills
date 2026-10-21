# my-taste-skills

내가 읽고 공감한 Claude Code 스킬을 역할별로 묶어, 다른 PC에서도 같은 구성을 적용한다.
역할별로 필요한 플러그인만 켜서 매 세션의 상주 토큰 비용을 관리한다.

스킬 본문을 복사하거나 남의 스킬을 다시 쓰지 않는다. 이 저장소는 marketplace가 아니며,
출처·내 분류·내 선택 이유를 관리한다. 기존 `leekensei/agent-skills`는 그대로 유지한다.

## 사용법

필요한 도구: Bash, jq, Git. 실제 스킬 실행에는 Claude Code가 필요하다.

```sh
git clone https://github.com/leekensei/my-taste-skills.git
cd my-taste-skills
./bin/apply uiux
```

현재는 ① 설정 병합 골격 단계다. `uiux.json`은 비어 있으며 **적용하면 사용자 설정에
등록된 모든 플러그인을 비활성화한다.** 스킬 첫 등재는 ②에서 진행한다.
플러그인 다운로드·설치는 아직 수행하지 않는다. 새 PC에서의 자동 설치 여부와
명시적 설치 필요성은 ③에서 검증한다. 지금은 새 PC에서 스킬이 발동한다고 보장하지 않는다.

기본 대상은 `$HOME/.claude/settings.json`이다. 격리해서 확인할 때는:

```sh
CLAUDE_CONFIG_DIR="$(mktemp -d)" ./bin/apply uiux
```

`extraKnownMarketplaces`는 기존 값과 병합하고, `enabledPlugins`는 선택한 역할의
합집합만 `true`, 기존의 나머지 항목은 명시적으로 `false`로 만든다.
다른 설정(`env`, `permissions`, `hooks` 등)은 보존한다. 프로젝트·관리자 설정 등
다른 범위의 활성화 여부까지 통제하는 명령은 아니다.

변경 전 설정은 같은 디렉터리의 `settings.json.before-apply.*`에 백업한다.
출력된 백업 파일을 `settings.json`으로 복사하면 되돌릴 수 있다.
같은 역할로 다시 실행하면 내용이 바뀌지 않으며 백업도 추가하지 않는다.
설정 파일을 동시에 편집하거나 여러 apply를 동시에 실행하지 않는다.

## 파일과 역할

| 파일 | 내용 |
| --- | --- |
| `marketplaces.json` | Claude Code `extraKnownMarketplaces` 값에 해당하는 출처 선언 |
| `roles/<역할>.json` | `enabledPlugins` 값에 해당하는 `plugin@marketplace: true` 묶음 |
| `roles/<역할>.md` | 선택 이유, 충돌 우선순위, 상주 토큰 비용 — 첫 등재 때 작성 |
| `bin/apply` | 역할 검증, 설정 병합, 백업, 원자적 파일 교체 |

역할은 배타적인 분류가 아니라 **언제 무엇을 켤지 정한 묶음**이다.
같은 플러그인이 여러 역할에 들어가도 된다. 역할이 추가되면
`./bin/apply uiux frontend`처럼 합쳐 적용한다. 아직 없는 역할은 오류로 처리한다.

첫 역할 `uiux`는 UI/UX 작업용이다. `engineering`(설계·구현 품질),
`frontend`(프론트엔드 개발), `marketing`(마케팅), `dev-workflow`(개발 작업 흐름)는
후보이며, 골격 검증 전에는 빈 역할 파일을 늘리지 않는다.
등재 기준은 **읽고 공감했다**이다. 선택 이유에는 회사·제품 고유 맥락을 넣지 않는다.

## 검증 단계

1. 설정 병합 골격: 다른 설정 보존, 합집합, 명시적 비활성화, 반복 실행, 잘못된 입력 보호.
2. `uiux.json`과 `uiux.md` 첫 등재.
3. 깨끗한 환경에서 clone → apply → 실제 스킬 발동 및 상주 비용 확인.

③ 통과가 프로젝트 성공 기준이다. 이후 스킬 편입은 운영으로 다룬다.
자동 설치, marketplace 자동 인식, 실행 중 세션 반영 여부는 실측 후 여기에 기록한다.

2026-10-21 ① 검증 기록 (macOS, Claude Code 2.1.301):

- 격리 환경에서 설정 보존, 두 역할 합집합·전환, 백업, 멱등성, 신규 설정 생성을 확인했다.
- 없는 역할·잘못된 역할명·잘못된 JSON·미선언 출처는 설정 변경 없이 실패했다.
- 실제 사용자 설정에서도 `apply uiux`를 두 번 실행해 8개 출처 병합과 동일한 결과를
  확인했다. 검증 후 원본 설정을 복원했다. 평소 플러그인 구성은 유지된다.

설정 위치와 범위는 [Claude Code 공식 문서](https://code.claude.com/docs/en/settings)를 참고한다.
출처 선언은 2026-10-21 로컬에 등록된 8개 공개 GitHub 소스를 기준으로 옮겼다.
