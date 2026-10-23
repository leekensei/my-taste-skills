# frontend 설치 검증 — 2026-10-23

## 결과

GitHub에 push한 commit `fd5e860`의 fresh clone에서 frontend의 스킬 3개 설치·검색·전환과
Codex 실제 발동을 확인했다. 앞선 로컬 commit `36bef8a` 검증에 이어 원격 배포 검증도 통과했다.
이 기록을 추가하는 후속 커밋은 문서와 증거만 갱신한다.

| 항목 | 결과 |
| --- | --- |
| 새 checkout | GitHub HTTPS URL에서 commit `fd5e860`을 새로 clone |
| Claude 설정·캐시 | 빈 `CLAUDE_CONFIG_DIR`, 기존 사용자 설정·플러그인 캐시 미사용 |
| 표준 패키지 | 원본에서 가져온 세 디렉터리를 새 프로젝트의 `.agents/skills/`에 설치 |
| 파일 무결성 | 세 패키지의 파일 집합·내용 해시가 설치 원본과 모두 일치 |
| Claude 역할 전환 | frontend 3개 활성 → 빈 uiux 0개 활성 → 합집합 3개 활성 |
| Codex 검색 전환 | 같은 app-server에서 명시적 재검색: 3개 → 0개 → 3개 |
| 실제 발동 | 선택 스킬 3개를 읽은 `commandExecution`과 완료된 모델 응답 확인 |
| 원격 clone | 새 설정·캐시에서 세 스킬 설치·역할 전환·Codex 실제 발동 재검증 통과 |

## 환경과 비용

- macOS, Claude Code 2.1.309, Codex CLI 0.163.0-alpha.11.2.
- 모델: `gpt-6-luna`, 추론 `low`, 임시 세션, read-only sandbox.
- Claude 모델 인증은 사용하지 않았다. Claude는 설치·구성·CLI 비용 추정만 검사했다.
- Codex는 기존 계정 인증만 사용했다. 기존 전역 스킬은 경로별로 비활성화하고, 프로젝트 문서·플러그인·앱·MCP를 제외했다.
- 별도 OS 사용자나 컨테이너를 만든 검증은 아니다. 새 설정·캐시·프로젝트 디렉터리를 쓰고 모델에 보이는 스킬 목록을 감사한 논리적 격리다.

| 스킬 | 상주 비용 추정 | 호출 시 본문 추정 | 컴포넌트 |
| --- | ---: | ---: | --- |
| react-composition | 49 tok | 70 tok | 스킬 1개 |
| feature-sliced-design | 238 tok | 5.3k tok | 스킬 1개 |
| vercel-react-best-practices | 96 tok | 1.7k tok | 스킬 1개 |
| 합계 | **383 tok** | 약 7.1k tok | 스킬 3개 |

수치는 Claude의 `plugin details` 추정값이며 실제 과금 토큰·Codex 토큰 수가 아니다.
추가 레퍼런스와 규칙 로드 비용도 별도다. 세 플러그인 모두 에이전트·훅·MCP·LSP가 0개다.

## 설치·역할 전환

새 clone 밖의 빈 작업 폴더에서 임시 설정을 지정해 다음 순서로 실행했다.

1. `bin/apply frontend` 성공. 같은 역할 재적용은 `Already applied`로 종료했다.
2. 명시적으로 등록·설치하기 전 `claude plugin list --json`과 `marketplace list --json`은 모두 `[]`였다.
3. 앞선 로컬 clone 검증에서 `claude plugin install react-composition@my-taste-skills`는 명시적 등록 전에 `not_found`로 실패했다. 설정의 출처 선언만으로 이 비대화형 설치 경로의 marketplace 인식이 되지는 않았다. 원격 clone 재검증에서도 등록 전 목록이 빈 배열임을 확인한 뒤 명시적 등록·설치를 진행했다.
4. `claude plugin marketplace add <새 clone>` 후 세 플러그인을 명시적으로 설치했다. 각 플러그인에서 스킬 1개만 인식했다.
5. frontend → uiux → frontend+uiux를 적용하고 `plugin list --json`에서 활성 상태 `3 → 0 → 3`을 확인했다.

즉 `bin/apply`는 설정 적용기다. 자동 설치기라고 안내하지 않는다. 대화형 Claude의 최초 실행·동기화 동작까지 일반화한 결과도 아니다.
실행 중 Claude 세션의 변경 반영은 실측하지 않았으며, 공식 안내대로 새 세션 또는 `/reload-plugins`를 사용한다.
[Claude 설치·로드 안내](https://code.claude.com/docs/en/discover-plugins)를 참고한다.

## 에이전트 공통 디렉터리와 Codex 발동

Claude 캐시에서 새로 받은 원본 패키지를 새 프로젝트의 아래 경로에 복사했다.
외부 패키지 본문을 이 저장소에 편입한 것은 아니다.

```text
.agents/skills/
  react-composition/SKILL.md
  feature-sliced-design/SKILL.md
  vercel-react-best-practices/SKILL.md
```

참조·규칙 파일도 함께 복사했다. 세 패키지의 파일 집합과 해시는 원본과 일치했고,
모델 입력 목록 감사에서는 이 세 스킬만 노출됐다. 다른 Agent Skills 지원 에이전트도
같은 디렉터리를 자신의 검색 경로에 설치할 수 있다. 모든 에이전트의 실제 동작을 검증했다는 뜻은 아니다.
[Codex의 표준 검색 경로](https://learn.chatgpt.com/docs/build-skills)를 참고한다.

같은 Codex app-server 프로세스에서 `skills/list`에 `forceReload: true`를 주고,
설치 디렉터리를 잠시 검색 경로 밖으로 옮겼다가 복원했다. 검색 결과는 3 → 0 → 3이었다.
이는 명시적 재검색의 결과이며 이미 시작한 턴의 문맥이나 자동 갱신 속도를 검증한 것은 아니다.

실제 발동에는 app-server의 표준 `turn/start` 입력을 사용했다. 요청한 세 스킬 각각에
`{type: "skill", name, path: "<설치 경로>/SKILL.md"}`를 전달했다.
`item/completed`의 `commandExecution`에서 세 설치 파일을 각각 읽은 명령 3건과 종료 코드 0을 확인했다.
모델의 “읽었다”는 자기보고만을 증거로 삼지 않았다.

완료된 응답은 호출부 조립과 dense prop 유지, 단일 소비자의 로직을 pages에 배치,
독립 조회를 `Promise.all`로 병렬화하는 결과를 제시했다. 이 결과는 발동 smoke 확인이며
외부 스킬의 전체 품질 평가나 생성 코드의 컴파일·동작 테스트가 아니다.

초기 CLI 텍스트 `$skill` 요청은 모델의 자기보고만 남고 파일 읽기 근거가 없어서 발동 증거에서 제외했다.
이후 정식 skill 입력과 실제 파일 읽기 이벤트를 사용한 결과만 통과로 판정했다.

## 기록과 검증 범위

- [해시·버전·실행 근거 요약](2026-10-23-installation-summary.json)은 저장소에서 관리한다.
- 원문 CLI 출력·Codex 이벤트·임시 재현 스크립트는 `evaluations/results/2026-10-23-installation/`(로컬 clone)과 `evaluations/results/2026-10-23-installation-remote/`(GitHub clone)에 보관했다. 두 폴더는 gitignore 대상이며 인증 파일은 복사하지 않았다.
- 현재 사용자 Claude 설정과 Codex 스킬 설치 디렉터리는 변경하지 않았다. 설치는 모두 임시 경로에서 수행했다.
- GitHub clone의 설치·발동까지 통과해 task ③의 검증 조건을 충족했다. Claude의 실제 모델 발동과 다른 에이전트별 실행 검증은 이번 범위에 포함하지 않았다.
