# my-taste-skills

내가 읽고 공감한 개발 원칙과 스킬을 역할별로 관리한다.
직접 작성한 스킬은 Agent Skills 형식의 `skills/<이름>/SKILL.md`로 보관한다.
Claude, Codex 등 이 형식을 지원하는 에이전트가 같은 본문을 사용할 수 있다.

외부 스킬 본문은 복사하지 않고 출처·분류·선택 이유를 관리한다.
아티클을 바탕으로 직접 만든 스킬은 원문 출처와 평가 기록을 함께 둔다.
Claude marketplace와 설정 적용기는 공통 본문을 연결하는 어댑터다.
기존 `leekensei/agent-skills`는 그대로 유지한다.

## 에이전트 공통 사용

현재 `frontend` 역할에는 [react-composition](skills/react-composition/SKILL.md)이 있다.
[역할 설명](roles/frontend.md)에 선택 이유·적용 범위·우선순위·비용을 기록한다.

`skills/react-composition/` 디렉터리를 사용하는 에이전트의 스킬 검색 경로에
복사하거나 연결한다. 자동 검색 경로와 설치 명령은 각 에이전트의 설정에 따른다.
자동 검색을 지원하지 않으면 에이전트에게 해당 `SKILL.md`를 읽고 적용하도록 요청한다.
본문은 특정 에이전트의 도구, 슬래시 명령, 하위 에이전트에 의존하지 않는다.

범용 형식이라는 점과 모든 에이전트에서 자동 발동을 검증했다는 점은 다르다.
검증 범위와 남은 항목은 [평가 기록](evaluations/react-composition.md)을 참고한다.

## Claude Code 어댑터 사용법

필요한 도구: Bash, jq, Git. 실제 스킬 실행에는 Claude Code가 필요하다.

```sh
git clone https://github.com/leekensei/my-taste-skills.git
cd my-taste-skills
```

`uiux.json`은 비어 있으며 **단독 적용하면 사용자 설정에 등록된 모든 플러그인을
비활성화한다.** `frontend`를 사용하려면 로컬 marketplace를 등록하고 설치한 뒤 적용한다:

```sh
claude plugin marketplace add "$PWD"
claude plugin install react-composition@my-taste-skills
./bin/apply frontend
```

다음 Claude 세션에서 `/react-composition:react-composition`으로 명시적으로 호출하거나
적용 범위에 맞는 요청으로 자동 선택을 확인한다. `bin/apply` 자체는 설치를 수행하지 않는다.

기본 대상은 `$HOME/.claude/settings.json`이다. 격리해서 확인할 때는:

```sh
CLAUDE_CONFIG_DIR="$(mktemp -d)" ./bin/apply uiux
```

`extraKnownMarketplaces`는 기존 값과 병합하고, `enabledPlugins`는 선택한 역할의
합집합만 `true`, 기존의 나머지 항목은 명시적으로 `false`로 만든다.
`source: directory`의 상대 `path`는 실행 위치가 아닌 이 레포의 루트를 기준으로
절대 경로로 바꾼다. 자체 marketplace는 이 clone을 가리키므로 clone을 이동하면 다시 적용한다.
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
| `skills/<이름>/SKILL.md` | 에이전트 공통 스킬 본문과 출처 |
| `.claude-plugin/marketplace.json` | 공통 스킬을 Claude 플러그인으로 노출하는 어댑터 |
| `evaluations/<이름>.md` | 평가 사례, 결과, 검증 범위와 한계 |
| `bin/apply` | 역할 검증, 설정 병합, 백업, 원자적 파일 교체 |

역할은 배타적인 분류가 아니라 **언제 무엇을 켤지 정한 묶음**이다.
같은 플러그인이 여러 역할에 들어가도 된다. 역할이 추가되면
`./bin/apply uiux frontend`처럼 합쳐 적용한다. 아직 없는 역할은 오류로 처리한다.

`uiux`는 UI/UX 작업용이며 아직 비어 있다. `frontend`는 프론트엔드 개발용이다.
`engineering`(설계·구현 품질), `marketing`(마케팅), `dev-workflow`(개발 작업 흐름)는
후보이며, 골격 검증 전에는 빈 역할 파일을 늘리지 않는다.
등재 기준은 **읽고 공감했다**이다. 선택 이유에는 회사·제품 고유 맥락을 넣지 않는다.

## 검증 단계

1. 설정 병합 골격: 다른 설정 보존, 합집합, 명시적 비활성화, 반복 실행, 잘못된 입력 보호.
2. 역할별 스킬 첫 등재: 현재 `frontend`에 자체 제작 스킬을 추가했다. `uiux`는 미등재.
3. 깨끗한 환경에서 clone → apply → 실제 스킬 발동 및 상주 비용 확인.

③의 실제 모델 발동과 비용 확인까지 통과하는 것이 프로젝트 성공 기준이다.
격리 설치 및 형식 검증과 실제 모델의 동작 품질 평가는 별도로 기록한다.
자동 설치, marketplace 자동 인식, 실행 중 세션 반영 여부는 실측 후 여기에 기록한다.

2026-10-21 ① 검증 기록 (macOS, Claude Code 2.1.301):

- 격리 환경에서 설정 보존, 두 역할 합집합·전환, 백업, 멱등성, 신규 설정 생성을 확인했다.
- 없는 역할·잘못된 역할명·잘못된 JSON·미선언 출처는 설정 변경 없이 실패했다.
- 실제 사용자 설정에서도 `apply uiux`를 두 번 실행해 8개 출처 병합과 동일한 결과를
  확인했다. 검증 후 원본 설정을 복원했다. 평소 플러그인 구성은 유지된다.

설정 위치와 범위는 [Claude Code 공식 문서](https://code.claude.com/docs/en/settings)를 참고한다.
출처 선언은 2026-10-21 로컬에 등록된 8개 공개 GitHub 소스를 기준으로 옮겼다.
2026-10-22 자체 제작 스킬용 로컬 marketplace를 추가했다.

## 레퍼런스와 평가 코드

스킬 본문에서 필요한 경우에만 [예시 안내](skills/react-composition/references/examples.md)를 읽는다.
직접 작성한 코드 조각은 1~4단계별로 나눠 도입 조건과 책임 경계를 설명한다.
레퍼런스를 위한 실행 환경이나 동작 테스트는 두지 않는다.

```sh
python3 evaluations/run.py --check
python3 evaluations/artifact_eval.py --check
python3 -m unittest discover -s tests -v
```

Python 테스트는 설정 적용기와 eval 실행기 자체를 검증한다.
eval에는 설계 선택을 확인하는 사례와, 생성 코드·변경 이유를 독립 리뷰하는 결과물 사례가 있다.
실제 모델을 사용하는 스킬 적용 전후 비교는 [평가 안내](evaluations/react-composition.md)에 따른다.
