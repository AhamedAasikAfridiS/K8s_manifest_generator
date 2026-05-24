export default function LoadingSpinner({ label = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-700 border-t-brand-yellow" />
      <p className="text-sm text-gray-400">{label}</p>
    </div>
  );
}
