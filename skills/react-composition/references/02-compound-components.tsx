import React, { createContext, useContext, type ReactNode } from 'react';

// 2단계: 배치 요구가 늘어날 때 조립 가능한 하위 컴포넌트를 제공한다.
// 변경 전: 화면마다 옵션을 추가해야 하는 행 API.
export function DocumentRowBefore({
  title, href, dense = false, showOwner = false, owner, showDownload = false,
}: {
  title: string; href: string; dense?: boolean; showOwner?: boolean;
  owner?: string; showDownload?: boolean;
}) {
  return (
    <div data-density={dense ? 'compact' : 'normal'}>
      <a href={href}>{title}</a>
      {showOwner && <span>{owner}</span>}
      {showDownload && <a href={`${href}/download`} download>Download</a>}
    </div>
  );
}

// 변경 후: 사용하는 쪽이 배치를 결정한다. density는 행 자체의 prop으로 남긴다.
// 이 context는 목록 구조를 맞추는 내부 구현이며 기능 데이터의 공급 경계가 아니다.
const InDocumentGroup = createContext(false);

function Group({ children }: { children: ReactNode }) {
  return <InDocumentGroup.Provider value={true}><ul>{children}</ul></InDocumentGroup.Provider>;
}

function Root({ dense = false, children }: { dense?: boolean; children: ReactNode }) {
  const grouped = useContext(InDocumentGroup);
  const row = <div data-density={dense ? 'compact' : 'normal'}>{children}</div>;
  return grouped ? <li>{row}</li> : row;
}

function Body({ children }: { children: ReactNode }) {
  return <div className="document-body">{children}</div>;
}

function Actions({ children }: { children: ReactNode }) {
  return <div className="document-actions">{children}</div>;
}

export const DocumentRow = { Group, Root, Body, Actions };

export function DocumentRowExample() {
  return (
    <DocumentRow.Group>
      <DocumentRow.Root dense>
        <DocumentRow.Body>
          <a href="/documents/guide">Team guide</a>
          <span>Design team</span>
        </DocumentRow.Body>
        <DocumentRow.Actions>
          <span>Updated today</span>
          <a href="/documents/guide/download" download>Download</a>
        </DocumentRow.Actions>
      </DocumentRow.Root>
    </DocumentRow.Group>
  );
}
