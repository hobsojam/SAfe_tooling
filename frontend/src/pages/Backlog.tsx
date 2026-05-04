import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import { FeatureStatusBadge } from '../components/Badge';
import { EmptyState } from '../components/EmptyState';
import { Spinner } from '../components/Spinner';

export function Backlog() {
  const { piId } = useParams<{ piId: string }>();

  const { data: pi } = useQuery({
    queryKey: ['pi', piId],
    queryFn: () => api.getPI(piId!),
    enabled: !!piId,
  });

  const { data: features = [], isLoading } = useQuery({
    queryKey: ['features', piId],
    queryFn: () => api.listFeatures(piId!),
    enabled: !!piId,
  });

  const { data: teams = [] } = useQuery({
    queryKey: ['teams'],
    queryFn: api.listTeams,
  });

  if (isLoading) return <Spinner />;

  const sorted = [...features].sort((a, b) => b.wsjf_score - a.wsjf_score);
  const teamMap = Object.fromEntries(teams.map((t) => [t.id, t.name]));

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold text-slate-800">
        Program Backlog — {pi?.name}
      </h1>
      <p className="mb-5 text-sm text-slate-500">Features ranked by WSJF score (highest first)</p>

      {sorted.length === 0 ? (
        <EmptyState message="No features in this PI." />
      ) : (
        <div className="overflow-x-auto overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                {['#', 'Feature', 'Status', 'Team', 'CoD', 'Size', 'WSJF'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sorted.map((f, i) => (
                <tr key={f.id} className="hover:bg-slate-50/60">
                  <td className="px-4 py-2.5 text-slate-400 tabular-nums">{i + 1}</td>
                  <td className="px-4 py-2.5">
                    <p className="font-medium text-slate-800">{f.name}</p>
                    {f.description && (
                      <p className="mt-0.5 text-xs text-slate-400 line-clamp-1">
                        {f.description}
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-2.5">
                    <FeatureStatusBadge status={f.status} />
                  </td>
                  <td className="px-4 py-2.5 text-slate-600">
                    {f.team_id ? (teamMap[f.team_id] ?? f.team_id) : '—'}
                  </td>
                  <td className="px-4 py-2.5 tabular-nums text-slate-700">{f.cost_of_delay}</td>
                  <td className="px-4 py-2.5 tabular-nums text-slate-700">{f.job_size}</td>
                  <td className="px-4 py-2.5">
                    <span className="font-semibold text-slate-800 tabular-nums">
                      {f.wsjf_score}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
