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

`uiux`와 함께 쓸 때는 `./bin/apply uiux frontend`로 적용한다.
