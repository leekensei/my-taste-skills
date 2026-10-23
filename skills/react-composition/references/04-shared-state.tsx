import React, { createContext, useContext, useState, type ReactNode } from 'react';

export type Entry = { id: string; title: string };
type CreateEntry = (title: string) => Promise<Entry>;

// 기존 데이터 계층의 훅이다. 성공 시 목록을 갱신하고, 실패는 호출자에게 전파한다고 가정한다.
declare function useBoardModel(boardId: string): {
  entries: readonly Entry[]; pending: boolean; error: string | null; createEntry: CreateEntry;
};
type BoardContract = {
  state: { entries: readonly Entry[]; pending: boolean; error: string | null };
  actions: { add: (title: string) => Promise<Entry> };
};
const BoardContext = createContext<BoardContract | null>(null);

export function useBoard() {
  const value = useContext(BoardContext);
  if (value === null) throw new Error('Board provider is required');
  return value;
}

// 4단계로 전환하기 전: 중간 레이아웃이 액션을 전달만 하는 구조.
export function BoardBefore({ onAdd }: { onAdd: () => void }) {
  return <section><BoardBodyBefore onAdd={onAdd} /></section>;
}
function BoardBodyBefore({ onAdd }: { onAdd: () => void }) {
  return <div><button onClick={onAdd}>Add entry</button></div>;
}

// 4단계: 목록 바깥의 형제 툴바도 같은 액션을 사용해야 한다.
// provider가 공통 상태와 액션을 소유하고 레이아웃은 배치만 담당한다.
export function BoardProvider({ boardId, children }: { boardId: string; children: ReactNode }) {
  const { entries, pending, error, createEntry } = useBoardModel(boardId);
  return (
    <BoardContext.Provider value={{ state: { entries, pending, error }, actions: { add: createEntry } }}>
      {children}
    </BoardContext.Provider>
  );
}

export function AddEntryComposer() {
  const { state: { pending, error }, actions } = useBoard();
  return (
    <>
      <button disabled={pending} onClick={() => { void actions.add('Untitled').catch(() => { /* 오류는 아래에서 사용자에게 표시한다. */ }); }}>
        {pending ? 'Saving' : 'Add entry'}
      </button>
      {error && <p role="alert">{error}</p>}
    </>
  );
}

export function EntryEditor({ entry }: { entry: Entry }) {
  // 형제 항목이 추가돼도 이 컴포넌트의 로컬 편집 내용은 유지한다.
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(entry.title);
  return (
    <li>
      {editing ? <input aria-label={`Draft for ${entry.id}`} value={draft} onChange={event => setDraft(event.target.value)} /> : <span>{entry.title}</span>}
      <button onClick={() => setEditing(value => !value)}>{editing ? 'Close editor' : 'Edit'}</button>
    </li>
  );
}

export function BoardListComposer() {
  const { state: { entries } } = useBoard();
  return <ul>{entries.map(entry => <EntryEditor key={entry.id} entry={entry} />)}</ul>;
}

export function BoardExample({ boardId }: { boardId: string }) {
  return (
    <BoardProvider boardId={boardId}>
      <header><AddEntryComposer /></header>
      <main><BoardListComposer /></main>
    </BoardProvider>
  );
}
