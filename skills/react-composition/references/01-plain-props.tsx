import React, { useId, useState } from 'react';

// 1단계: 요구가 안정적이면 props와 로컬 상태로 충분하다.
// 다른 컴포넌트가 펼침 상태를 다루지 않으므로 기능 provider를 만들지 않는다.
export function PlainDocumentRow({
  title, href, description, dense = false,
}: { title: string; href: string; description: string; dense?: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const descriptionId = useId();
  return (
    <article data-density={dense ? 'compact' : 'normal'}>
      <a href={href}>{title}</a>
      <button
        aria-expanded={expanded}
        aria-controls={descriptionId}
        onClick={() => setExpanded(value => !value)}
      >
        설명 {expanded ? '접기' : '펼치기'}
      </button>
      <p id={descriptionId} hidden={!expanded}>{description}</p>
    </article>
  );
}

export function PlainPropsExample() {
  return (
    <section aria-label="문서 목록">
      <PlainDocumentRow title="팀 안내" href="/documents/guide" description="팀의 업무 방식을 소개한다." />
      <PlainDocumentRow title="설계 기록" href="/documents/design" description="설계 결정의 배경을 기록한다." dense />
    </section>
  );
}
