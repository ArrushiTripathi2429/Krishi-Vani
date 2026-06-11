export default function SourceCard({ source, index }) {
  return (
    <div className="bg-white border border-green-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-green-700 bg-green-100 px-2 py-1 rounded-full">
          Source {index + 1}
        </span>
        <span className="text-xs text-gray-400">
          Score: {(source.score * 100).toFixed(1)}%
        </span>
      </div>

      <div className="grid grid-cols-2 gap-1 text-xs text-gray-600 mb-2">
        <span>🌾 {source.crop || "N/A"}</span>
        <span>📍 {source.district || "N/A"}</span>
        <span>🗺 {source.zone || "N/A"} zone</span>
      </div>

      <p className="text-xs text-gray-500 italic border-t pt-2 mt-1">
        "{source.query?.slice(0, 80)}..."
      </p>
    </div>
  );
}