import { Alert } from '@/components/ui/Alert';

export function AlertList({ items = [] }: { items?: { id: string; title: string }[] }) {
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <Alert key={item.id}>{item.title}</Alert>
      ))}
    </div>
  );
}
