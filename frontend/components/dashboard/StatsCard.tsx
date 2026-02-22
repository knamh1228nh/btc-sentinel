import { Card } from '@/components/ui/Card';

export function StatsCard({ title, value }: { title: string; value: string | number }) {
  return (
    <Card>
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-xl font-semibold">{value}</div>
    </Card>
  );
}
