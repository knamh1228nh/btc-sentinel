import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold">Mini Sentinel</h1>
      <nav className="mt-4 flex gap-4">
        <Link href="/dashboard" className="text-blue-600 underline">대시보드</Link>
        <Link href="/alerts" className="text-blue-600 underline">알림</Link>
        <Link href="/settings" className="text-blue-600 underline">설정</Link>
      </nav>
    </main>
  );
}
