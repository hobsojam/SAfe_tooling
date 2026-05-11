export function EmptyState({ message }: { message: string }) {
  return (
    <div
      className="flex flex-col items-center justify-center py-16 text-bark-400"
      role="status"
    >
      <p className="text-sm">{message}</p>
    </div>
  );
}
