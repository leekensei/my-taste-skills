# react-composition 평가

## 범위와 현재 상태

2026-10-22, macOS, Claude Code 2.1.307에서 작성했다.
원문 출처는 [Orus Engineering Blog](https://backstage.orus.eu/react-composition-patterns-at-orus/)다.
범용 본문은 [SKILL.md](../skills/react-composition/SKILL.md), 직접 작성한 예제는
[references/](../skills/react-composition/references/examples.md)에 있다.

설명용 레퍼런스에는 별도의 실행 환경이나 동작 테스트를 두지 않는다.
검증 대상은 스킬의 구조·판단 품질과 실제 실행 도구다.

| 층 | 확인 대상 | 현재 기록 |
| --- | --- | --- |
| 구조·연결 | 표준 frontmatter, 레퍼런스 연결, Claude 어댑터 설치·인식 | skill-creator 검증 통과. 격리 Claude 설정에서 설치 후 스킬 1개 인식. |
| 실행 도구 | 설정 보존, eval 실행·채점 오류 처리 | Python 테스트 16개 통과. 레퍼런스 코드 조각은 테스트 대상이 아니다. |
| 모델 판단·결과물 | 스킬 적용 전후의 판단과 실제 생성 코드 품질 | 기본·Luna 사례 각각 5개를 1회 A/B 실행했고, 이후 본문 축약 후보 5개를 Luna로 평가했다. 현재 SKILL.md 파일은 frontmatter 포함 133단어이며 축약 전보다 77% 짧다. 상세 점수와 한계는 결과 보고서 참고. 결정 사례 7개는 모델 미실행. |

실제 실행 조건·코드 관찰·한계는 [2026-10-22 결과](2026-10-22-result.md)에 기록했다.
Luna를 사용한 경계 사례 결과는 [2차 결과](2026-10-22-luna-result.md)에 기록했다.
본문 축약과 최종 후보 선택은 [축약 평가](2026-10-22-ablation-result.md)에 기록했다.

작성자 검토에서 보완한 점: 단순한 fixture 렌더링만으로 context를 강제하지 않도록 했고,
설치된 React API, 비활성 뷰의 마운트 방식, 비동기 액션 실패 처리도 확인하도록 했다.
이것은 작성자의 내용 검토이며 독립 모델 평가 결과가 아니다.

## 실행 도구 확인

```sh
python3 evaluations/run.py --check
python3 -m unittest discover -s tests -v
```

설정 적용기의 테스트는 다른 설정 보존·역할 전환·반복 적용·잘못된 입력 보호를 확인한다.
eval 실행기의 테스트는 채점·스킬 유무 비교·runner 입출력·오류 처리를 확인한다.
실제 사용자 설정 대신 임시 디렉터리에서 실행한다.

## 에이전트 공통 모델 eval

### 결과물 평가

[결과물 사례](artifact-cases.json)는 원본 코드·변경 요청·코드 리뷰 기준을 포함한다.
[결과물 실행기](artifact_eval.py)는 다음 흐름으로 평가한다.

1. 생성 runner에 원본 코드와 요청을 주고 최종 코드와 변경 이유를 받는다.
2. 별도 judge runner가 원본·요청·결과물을 검토한다. 스킬 본문, 적용 여부, 생성 모델과 앞선 점수는 전달하지 않는다.
3. 요구 충족, 책임 경계, 기존 동작 보존, 변경 범위, 설명과 코드의 일치를 사례별 기준으로 판정한다.
4. 각 판정에 실제 원본 또는 결과 코드의 근거 조각과 이유를 요구한다. 실행기는 인용이 해당 코드에 존재하는지 확인한다.
5. 스킬 유무에 따른 기준별 결과와 평균 점수 차이, 최종 TSX, 설명, 평가 원문을 저장한다.

```sh
python3 evaluations/artifact_eval.py --check
python3 evaluations/artifact_eval.py --cases evaluations/luna-artifact-cases.json --runner '/absolute/path/to/generator-wrapper' --judge-runner '/absolute/path/to/reviewer-wrapper' --runs 1 --output /tmp/composition-artifacts
```

결과물 사례는 단순 props 유지, 조립 가능한 행 API와 두 사용 예시, 교체 가능한 공급자,
공유 액션과 로컬 draft 보존, 스타일만 수정하는 작업이다. 생성 단계에 리뷰 정답은 넣지 않는다.
생성 runner는 `code`, `explanation` 문자열을 담은 JSON을 반환한다. 평가 runner의 JSON 형식은
실행기가 보내는 프롬프트에 정의한다. 두 runner 모두 매 호출마다 독립 세션을 시작하고,
글로벌 스킬·세션 기록이 섞이지 않는 동일한 생성 설정을 사용해야 한다. 코드 리뷰에 실행 도구는 필요 없다.

인증된 Codex CLI용 [어댑터](codex_runner.py)도 제공한다. 기본 모델은 `gpt-6.1-sol`,
추론 강도는 `low`다. `SKILL_EVAL_MODEL` 환경 변수로 모델을 지정할 수 있다.
각 호출은 새 ephemeral 세션에서 실행한다. 사용자 설정·프로젝트 지침·전역 스킬·플러그인·
셸·웹 검색·앱·하위 에이전트를 비활성화하고, 실제 도구 이벤트가 있으면 오류로 처리한다.
모델명과 토큰 사용량은 각 호출의 metadata 파일에 저장한다.

```sh
python3 evaluations/artifact_eval.py \
  --runner "python3 '$PWD/evaluations/codex_runner.py'" \
  --judge-runner "python3 '$PWD/evaluations/codex_runner.py'" \
  --runs 1 --timeout 360 --output evaluations/results/local-artifacts
```

사례 파일은 `--cases`로 지정한다. Codex 어댑터 모델은 `SKILL_EVAL_MODEL` 환경 변수로 바꾼다.
Luna 경계 사례의 실행은 다음처럼 재현한다.

```sh
SKILL_EVAL_MODEL=gpt-6-luna python3 evaluations/artifact_eval.py \
  --cases evaluations/luna-artifact-cases.json \
  --runner "python3 '$PWD/evaluations/codex_runner.py'" \
  --judge-runner "python3 '$PWD/evaluations/codex_runner.py'" \
  --runs 1 --timeout 360 --output evaluations/results/local-luna-artifacts
```

설명 일치 기준의 근거는 결과물 설명에서 인용할 수 있다. 그 외 기준은 원본 또는 결과
코드에서 인용해야 한다. 이는 설명의 근거를 코드에서만 찾도록 강제했던 초기 검증 오류를
수정한 것이다. 실행 오류 기록은 모델 품질 점수에서 제외한다.
독립된 `...` 행으로 여러 근거를 연결하면 각 코드 조각의 존재를 따로 확인한다.
중단 후에는 같은 `--output` 경로와 `--resume`으로 동일한 프롬프트의 기존 응답을
재사용할 수 있다. 프롬프트가 달라졌다면 새 출력 폴더를 사용한다.

5개 사례 × 3회 × 2개 arm × 생성·리뷰 2호출 = 총 60호출이다.
judge는 양쪽 arm에서 동일한 모델·설정·기준을 사용한다. 한 기준이라도 실패하면 해당 결과물은
통과하지 못한 것으로 기록하며, 점수는 충족한 기준의 비율로 함께 제공한다.

이 평가는 **생성 코드의 정적 리뷰**다. 코드 인용 검사는 근거의 존재만 확인하며 판정의 타당성까지
보장하지 않는다. judge의 오판 가능성이 있으므로 실제 결과를 사람이 표본 검토해야 한다.
컴파일·실행 결과, 자동 스킬 선택, 레퍼런스의 실제 탐색 여부를 검증했다고 해석하면 안 된다.
실제 모델 결과는 위 실행 기록에서 확인한다. 실행기 테스트의 가짜 응답은 모델 품질 증거가 아니다.

### 설계 선택 평가

[사례 파일](react-composition.cases.json)과 [실행기](run.py)는 특정 모델 SDK에 의존하지 않는다.
Python 3 표준 라이브러리만 사용한다. runner는 stdin으로 프롬프트를 받고 stdout으로
JSON 결정 하나를 반환하는 명령이다. 사용하는 에이전트 CLI나 API를 이 입출력에 연결한다.
상태 로그는 stderr로 보내고, 명령의 실행 파일·스크립트 경로는 절대 경로로 지정한다.
실행기는 shell을 사용하지 않으며 명령을 토큰화해 직접 실행한다.

```sh
python3 evaluations/run.py --check
python3 evaluations/run.py --runner '/absolute/path/to/agent-eval-wrapper' --runs 3 --output /tmp/react-composition-eval
```

7개 사례 × 3회 × 2개 arm = 모델 호출 42회다. 처음에는 `--runs 1`로 runner 연결을
확인한다. 실제 실행은 선택한 모델의 계정·과금·사용량을 사용한다.
실행기 자체가 원격 보고서를 게시하거나 에이전트를 설치하지 않는다.

- `with`: 스킬 본문을 추가하고 같은 요청을 전달한다.
- `without`: 스킬 본문 없이 같은 요청과 동일한 출력 형식을 전달한다.
- 두 arm에서 같은 모델·추론 설정·도구 정책을 쓰고, runner는 매번 새 세션을 시작해야 한다.
  ambient skill이나 글로벌 에이전트 지침이 baseline에 섞이지 않는 별도 설정을 사용한다.
  이 suite는 결정만 반환하므로 도구를 비활성화한 runner가 적절하다.
  실행기는 각 호출에 별도의 빈 작업 디렉터리를 제공한다.
- 정답은 모델 입력에 포함하지 않는다. 각 run의 원문 응답, 프롬프트, 필드별 채점,
  스킬·사례 해시와 평균 차이를 지정한 출력 디렉터리에 남긴다.
- timeout, 프로세스 실패, 비정상 JSON은 품질 점수 0으로 섞지 않고 실행 오류로 기록한다.
  오류가 나면 추가 호출을 중단하고 부분 보고서를 남긴다.

응답 형식과 필드별 어휘는 실행기가 프롬프트에 포함한다. 예를 들어 단순 API 사례는:

```json
{
  "applicable": true,
  "ui_api": "props",
  "feature_context": false,
  "source_boundary": false,
  "shared_action_boundary": false,
  "reason": "현재 사용하는 쪽에 새로운 배치나 상태 공유 요구가 없습니다."
}
```

`feature_context`는 이번 작업에서 새 feature context를 도입하는지를 뜻한다.
primitive 내부의 비공개 coordination context는 여기에 포함하지 않는다.
`source_boundary`와 `shared_action_boundary`도 새 경계를 도입하는 결정이다.
`ui_api: props`는 일반 props API를 선택·유지하는 경우,
`unchanged`는 UI API가 이번 변경 대상이 아닌 경우다.

이미 받은 응답을 모델 호출 없이 재채점할 수도 있다. 파일 구조는
`<응답폴더>/<with|without>/<사례ID>/run-1.json`이다.

```sh
python3 evaluations/run.py --responses /absolute/path/to/responses --runs 1 --output /tmp/regraded-composition
```

종료 코드: 0은 완전 실행 및 with 기준 충족, 1은 완전 실행했지만 with 판단 기준 미충족,
2는 입력·실행 오류다. `--arm without`만 실행하면 품질 게이트 없이 완료 여부를 반환한다.

## 사례와 수용 기준

| 사례 | 핵심 수용 기준 |
| --- | --- |
| stable-props | 유지할 수 있는 props에 구조 통일만을 이유로 provider를 추가하지 않는다. |
| variable-layout | 조립 가능한 부분을 제안하고 실제 row 상태인 density는 prop으로 남긴다. |
| interchangeable-sources | 명시적으로 요구된 교체 가능한 공급 경계를 만들고 fixture에서 네트워크를 요구하지 않는다. |
| sibling-actions | 형제들의 공통 경계에서 액션을 제공하되 로컬 draft와 비동기 실패 처리를 보존한다. |
| effect-query-deferral | 마운트 또는 query 실행을 실제로 제어한다. Suspense만 추가해서 해결했다고 하지 않는다. |
| react18-fixture | 버전을 올리지 않고 기존 context API로 fixture를 연결한다. |
| css-only | 합성 스킬의 개입 범위 밖으로 판단하고 구조를 바꾸지 않는다. |

각 사례 점수는 명시된 결정 필드의 충족 비율이다. 단어·정규식으로 설명 문구를
맞추는 검사는 하지 않는다. 테스트의 가짜 runner와 fixture 응답은 실행기 검증용이며
실제 모델의 성능 증거가 아니다.

기존 결정 suite는 설계 결정의 회귀 신호다. 설명의 타당성, 생성 코드의 품질, 자동 스킬
선택, 레퍼런스의 실제 참조 여부는 자동 채점하지 않는다. 스킬 본문만 주입하며 연결된
레퍼런스를 자동으로 넣지 않으므로, 점수를 코드 생성 능력이나 전체 스킬 패키지의 평가로
해석하면 안 된다. 결과가 같으면 이 suite에서 개선 효과를 보이지 못한 것이다.
실제 적용 사례에서는 코드 diff와 프로젝트 테스트까지 별도로 검토한다.
