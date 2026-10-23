# 단계별 합성 패턴 레퍼런스

[Orus 아티클](https://backstage.orus.eu/react-composition-patterns-at-orus/)의 네 단계를
별도 도메인의 코드 조각으로 설명한다. 원문의 코드를 그대로 복제하지 않았다.
각 단계는 현재 문제를 해결할 때만 선택한다. 모든 컴포넌트를 4단계까지 바꾸는 절차가 아니다.

| 단계 | 예제 | 도입 이유 | 이 단계에서 추가하는 것 |
| --- | --- | --- | --- |
| 1. 일반 props | [01-plain-props.tsx](01-plain-props.tsx) | API가 작고 사용하는 쪽의 요구가 안정적이다. | props와 컴포넌트 내부 상태만 사용한다. |
| 2. Compound components | [02-compound-components.tsx](02-compound-components.tsx) | 화면마다 새로운 배치 옵션을 추가해야 한다. | 사용하는 쪽이 조립할 수 있는 하위 컴포넌트를 제공한다. |
| 3. Composer와 Providers | [03-composer-providers.tsx](03-composer-providers.tsx) | 같은 UI가 서로 교체 가능한 데이터 출처를 사용해야 한다. | 렌더링과 출처를 작은 계약으로 분리한다. |
| 4. 계약 뒤로 공유 상태 이동 | [04-shared-state.tsx](04-shared-state.tsx) | 상태와 액션이 레이아웃 계층을 넘어 형제 컴포넌트에도 필요하다. | 공통 provider가 상태·액션의 경계를 제공한다. |

## 1단계: props로 충분한 경우

`PlainDocumentRow`는 제목·링크·설명을 props로 받고 설명 펼침 여부만 내부에서 관리한다.
`PlainPropsExample`의 두 행은 서로의 펼침 상태를 알 필요가 없다.
이 상태를 공유 provider로 옮길 이유가 없다.

배치를 바꾸기 위해 화면마다 새 옵션을 추가해야 하는 문제가 생기면 2단계를 검토한다.

## 2단계: 마크업 조립

`DocumentRowBefore`와 `DocumentRowExample`을 비교한다.
플래그로 미리 정한 배치를 고르는 대신 `Root`, `Body`, `Actions`를 조립한다.
행 자체의 밀도를 정하는 `dense`는 prop으로 유지한다.

이 예제의 비공개 context는 목록 안에 있는지를 판단해 `ul`/`li` 구조를 맞출 뿐이다.
기능 데이터의 출처를 공급하는 3단계 context와는 책임이 다르다.
context를 썼다는 이유만으로 3단계가 되는 것은 아니다.

## 3단계: 데이터 출처 교체

`DocumentsBefore`는 안정적인 단일 출처라면 props로 충분하다는 출발점이다.
출처 교체가 실제 요구가 되면 `DocumentsComposer`는 계약만 읽고,
최근 문서·저장 문서·fixture provider가 같은 계약을 채운다.
Composer는 2단계의 `DocumentRow`를 재사용해 UI를 조립한다.

`DocumentViews`는 선택한 출처만 마운트하는 예시다. 실제 지연 조회 여부는 프로젝트의
탭 마운트 정책과 조회 라이브러리의 동작을 확인해야 한다.
정적 데이터로 테스트한다는 이유만으로 항상 provider가 필요한 것은 아니다.

## 4단계: 경계를 넘는 상태와 액션

`BoardBefore`에서는 중간 레이아웃이 액션을 전달만 한다.
목록 밖의 헤더도 같은 액션을 사용해야 하면 `BoardProvider`를 두 분기의 공통 상위에 둔다.
헤더와 목록은 같은 계약을 읽고, 개별 항목의 편집 여부와 draft는 로컬에 남긴다.

3단계가 같은 렌더링에 다른 출처를 연결하는 데 초점을 둔다면,
4단계는 여러 컴포넌트가 같은 기능 상태와 액션을 사용하는 경계를 정하는 데 초점을 둔다.
두 필요가 함께 있다면 하나의 계약에 필요한 `state`, `meta`, `actions`만 조합한다.
원문의 4단계 사례는 게시 시점에 제안된 구현 방향이었다.

## 예제의 범위

이 파일들은 이론을 설명하는 코드 조각이다. React 18과 호환되는 문법을 사용한다.
`declare`로 표시한 조회·변경 훅은 실제 프로젝트의 기존 데이터 계층을 뜻하며 구현하지 않는다.
로딩·오류·캐시·갱신 정책은 해당 계층의 계약을 따른다. 독립 실행 앱이나 테스트 대상 라이브러리가 아니다.

스킬의 판단 품질을 비교하는 eval은 레포 루트의 `evaluations/react-composition.md`에서 다룬다.
