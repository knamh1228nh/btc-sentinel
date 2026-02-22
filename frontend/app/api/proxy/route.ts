import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  const path = request.nextUrl.searchParams.get('path') || '';
  const res = await fetch(`${API_URL}/${path}`);
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data);
}

export async function POST(request: NextRequest) {
  const path = request.nextUrl.searchParams.get('path') || '';
  const body = await request.json().catch(() => ({}));
  const res = await fetch(`${API_URL}/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data);
}
