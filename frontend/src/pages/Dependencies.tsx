import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import { DepBadge } from '../components/Badge';
import { EmptyState } from '../components/EmptyState';
import { Spinner } from '../components/Spinner';

export function Dependencies() {
  const { piId } = useParams<{ piId: string }>();

  const { data: pi } = useQuery({
    queryKey: ['pi', piId],
    queryFn: () => api.getPI(piId!),
    enabled: !!piId,
  });

  const { data: deps = [], isLoading } = useQuery({
    queryKey: ['dependencies', piId],
    queryFn: () => api.listDependencies(piId!),
    enabled: !!piId,
  });

  const { data: teams = [] } = useQuery({
    queryKey: ['teams'],
    queryFn: api.listTeams,
  });

  if (isLoading) return <Spinner />;

  const teamMap = Object.fromEntries(teams.map((t) => [t.id, t.name]));
  const unresolved = deps.filter((d) => d.status !== 'resolved').length;

  return (
    <div className="p-6">
      <div className="mb-5 flex items-baseline justify-between">
        <div>
          <h1 className="mb-1 text-xl font-semibold text-slate-800">
            Dependencies — {pi?.name}
          </h1>
          <p className="text-sm text-slate-500">
            {deps.length} dependenc{deps.length !== 1 ? 'ies' : 'y'}
            {unresolved > 0 && (
              <span className="ml-2 font-medium text-red-600">{unresolved} unresolved</span>
            )}
          </p>
        </div>
      </div>

      {deps.length === 0 ? (
        <EmptyState message="No dependencies for this PI." />
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                {['From', 'To', 'Description', 'Status', 'Owner', 'Needed By'].map((h) => (
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
              {deps.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50/60">
                  <td className="px-4 py-2.5 font-medium text-slate-700">
                    {teamMap[d.from_team_id] ?? d.from_team_id}
                  </td>
                  <td className="px-4 py-2.5 font-medium text-slate-700">
                    {teamMap[d.to_team_id] ?? d.to_team_id}
                  </td>
                  <td className="px-4 py-2.5 text-slate-600">{d.description}</td>
                  <td className="px-4 py-2.5">
                    <DepBadge status={d.status} />
                  </td>
                  <td className="px-4 py-2.5 text-slate-500">{d.owner ?? '—'}</td>
                  <td className="px-4 py-2.5 text-slate-500 tabular-nums">
                    {d.needed_by_date ?? '—'}
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
