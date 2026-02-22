import Link from 'next/link';

export function Sidebar() {
  return (
    <aside className="w-48 border-r p-4">
      <nav className="flex flex-col gap-2">
        <Link href="/dashboard">대시보드</Link>
        <Link href="/alerts">알림</Link>
        <Link href="/settings">설정</Link>
      </nav>
    </aside>
  );
}
