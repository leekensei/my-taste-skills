# frontend

프론트엔드 구현 중 컴포넌트 API와 책임 경계를 판단할 때 쓰는 묶음이다.

## react-composition

- 등록: `react-composition@my-taste-skills`
- 공통 본문: [SKILL.md](../skills/react-composition/SKILL.md). Agent Skills 형식을 읽는 에이전트에서 같은 파일을 사용한다. 위 등록 ID는 Claude 전용 어댑터다.
- 출처: Maxime Grébauval, [Orus Engineering Blog](https://backstage.orus.eu/react-composition-patterns-at-orus/), 2026-07-15. 원문이나 예제 코드를 복제하지 않고 판단 지침으로 작성했다.
- 선택 이유: 컴포넌트 API와 데이터·상태 경계를 구체적인 변경 요구에 맞춰 결정하는 데 사용한다.
- 적용 범위: React 합성 설계·리팩터링·리뷰. CSS 수정과 일반적인 성능 최적화에는 적용하지 않는다.
- 충돌 우선순위: 사용자의 요구와 프로젝트 규칙, 설치된 React·UI 라이브러리의 API를 우선한다. 이 스킬 때문에 기존 명명법을 일괄 변경하지 않는다. 다른 성능 스킬은 실제 성능 문제를 다룰 때 함께 쓴다.
- 비용: 스킬 하나만 포함하며 훅·MCP·추가 에이전트 정의가 없다. 레퍼런스는 필요한 단계만 읽는다. 현재 한글 본문 기준 토큰 비용은 미측정이며 에이전트별로 확인해야 한다.
- 평가: [평가 기록](../evaluations/react-composition.md). 작성자 사례 검토와 모델 실행 평가는 구분한다.

## feature-sliced-design

- 등록: `feature-sliced-design@my-taste-skills`. 이 레포의 marketplace는 원본 GitHub 저장소와 `feature-sliced-design/` 디렉터리만 연결한다. 외부 본문은 복사하지 않는다.
- 출처·설치: [feature-sliced/skills](https://github.com/feature-sliced/skills). Agent Skills를 지원하는 다른 에이전트에서는 원본 안내의 `npx skills add feature-sliced/skills`로 설치한다.
- 선택 이유: 프론트엔드 코드의 배치와 import 경계를 FSD v2.1 기준으로 판단한다. 페이지에 먼저 두고, 실제 공유 책임이 생길 때 추출하는 접근을 사용한다.
- 적용 범위: FSD 구조 설계·리뷰·마이그레이션, slice 공개 API와 계층 간 의존성. FSD 도입이 요청되지 않은 프로젝트를 일괄 재구성하지 않는다.
- 충돌 우선순위: 사용자 요구와 프로젝트의 기존 아키텍처·프레임워크 규칙을 우선한다. `react-composition`은 컴포넌트 조립과 상태 소유권, 이 스킬은 파일 배치와 계층 경계를 담당한다.
- 비용: 2026-10-23 격리 설치의 Claude CLI 추정치는 상주 약 238토큰, 호출 시 본문 약 5.3k토큰이다. 관련 레퍼런스는 필요할 때만 읽는다. 모델 품질 평가는 별도로 실행하지 않았으며 원본의 eval을 유지한다.
- 검증: marketplace strict 검사 통과. 임시 Claude 설정에서 설치 후 스킬 1개 인식, 에이전트·훅·MCP·LSP는 0개 확인.

## vercel-react-best-practices

- 등록: `vercel-react-best-practices@my-taste-skills`. 원본 저장소의 `skills/react-best-practices/`만 연결하며 다른 Vercel 스킬은 포함하지 않는다.
- 출처·설치: [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills). 다른 Agent Skills 지원 에이전트에서는 `npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices`로 설치한다.
- 선택 이유: React·Next.js의 데이터 조회 waterfall, 번들 크기, 서버·클라이언트 렌더링 비용을 영향도에 따라 개선한다.
- 적용 범위: React·Next.js 코드 작성·리뷰·리팩터링과 성능 개선. 설치된 프레임워크 버전과 서버·클라이언트 경계를 확인해 해당 규칙만 적용한다.
- 충돌 우선순위: 사용자 요구와 프로젝트 규칙을 우선한다. FSD의 공개 API 경계를 유지하면서 import를 최적화하고, barrel 회피를 이유로 slice 내부를 직접 참조하지 않는다. `react-composition`의 책임 경계도 보존한다.
- 비용: 2026-10-23 격리 설치의 Claude CLI 추정치는 상주 약 96토큰, 호출 시 본문 약 1.7k토큰이다. 전체 규칙 문서와 개별 규칙을 추가로 읽는 비용은 별도다.
- 검증: `git-subdir`로 요청한 하위 디렉터리만 설치해 스킬 1개 인식을 확인했다. marketplace strict 검사와 설정 적용기 테스트를 통과했다. 에이전트·훅·MCP·LSP는 0개이며 별도 모델 품질 평가는 실행하지 않았다.

`uiux`와 함께 쓸 때는 `./bin/apply uiux frontend`로 적용한다.
