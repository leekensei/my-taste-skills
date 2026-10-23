import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { DocumentRow } from './02-compound-components';

// 3단계: 렌더링 구조는 같고 데이터 출처를 교체해야 할 때 사용한다.
export type Document = { id: string; title: string };
type QueryState = { documents: readonly Document[]; pending: boolean; error: string | null };
type Contract = { state: QueryState; meta: { emptyLabel: string } };
const DocumentsContext = createContext<Contract | null>(null);

// 실제 프로젝트의 기존 조회 훅을 뜻한다. 조회·캐시 구현은 생략한다.
declare function useRecentDocuments(): QueryState;
declare function useSavedDocuments(): QueryState;

function useDocuments() {
  const value = useContext(DocumentsContext);
  if (value === null) throw new Error('Documents provider가 필요합니다.');
  return value;
}

// 전환 전: 출처가 하나로 안정적이면 props로 충분하다.
export function DocumentsBefore({ documents }: { documents: readonly Document[] }) {
  return <ul>{documents.map(doc => <li key={doc.id}>{doc.title}</li>)}</ul>;
}

// 전환 후: Composer는 출처를 모르고 계약만 읽는다.
export function DocumentsComposer() {
  const { state, meta } = useDocuments();
  if (state.pending) return <p role="status">문서를 불러오는 중</p>;
  if (state.error) return <p role="alert">{state.error}</p>;
  if (state.documents.length === 0) return <p>{meta.emptyLabel}</p>;
  return (
    <DocumentRow.Group>
      {state.documents.map(doc => (
        <DocumentRow.Root key={doc.id}>
          <DocumentRow.Body><a href={`/documents/${doc.id}`}>{doc.title}</a></DocumentRow.Body>
        </DocumentRow.Root>
      ))}
    </DocumentRow.Group>
  );
}

export function RecentDocumentsProvider({ children }: { children: ReactNode }) {
  const state = useRecentDocuments();
  return <DocumentsContext.Provider value={{ state, meta: { emptyLabel: '최근 문서가 없습니다.' } }}>{children}</DocumentsContext.Provider>;
}

export function SavedDocumentsProvider({ children }: { children: ReactNode }) {
  const state = useSavedDocuments();
  return <DocumentsContext.Provider value={{ state, meta: { emptyLabel: '저장한 문서가 없습니다.' } }}>{children}</DocumentsContext.Provider>;
}

// 같은 계약에 정적 데이터를 공급한다. 조회 훅이나 네트워크 클라이언트를 요구하지 않는다.
export function FixtureDocumentsProvider({
  documents, children,
}: { documents: readonly Document[]; children: ReactNode }) {
  return (
    <DocumentsContext.Provider value={{ state: { documents, pending: false, error: null }, meta: { emptyLabel: '문서가 없습니다.' } }}>
      {children}
    </DocumentsContext.Provider>
  );
}

export function DocumentViews() {
  const [view, setView] = useState<'recent' | 'saved'>('recent');
  return (
    <section aria-label="문서 보기">
      <button aria-pressed={view === 'recent'} onClick={() => setView('recent')}>최근 문서</button>
      <button aria-pressed={view === 'saved'} onClick={() => setView('saved')}>저장 문서</button>
      {/* 선택한 provider만 마운트한다. 재진입 시 조회·보존 정책은 기존 조회 계층을 따른다. */}
      {view === 'recent' ? (
        <RecentDocumentsProvider><DocumentsComposer /></RecentDocumentsProvider>
      ) : (
        <SavedDocumentsProvider><DocumentsComposer /></SavedDocumentsProvider>
      )}
    </section>
  );
}
