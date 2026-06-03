import { AlertTriangle } from 'lucide-react';

export default function ErrorState({ message }) {
  return (
    <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 text-red-300">
          <AlertTriangle size={20} />
        </div>
        <div>
          <div className="font-semibold">Failed to analyze</div>
          <div className="mt-1 text-sm text-red-200/80">{message}</div>
        </div>
      </div>
    </div>
  );
}

