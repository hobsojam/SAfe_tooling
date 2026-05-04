import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import { ROAMBadge } from '../components/Badge';
import { EmptyState } from '../components/EmptyState';
import { Spinner } from '../components/Spinner';

export function Risks() {
  const { piId } = useParams<{ piId: string }>();

  const { data: pi } = useQuery({
    queryKey: ['pi', piId],
    queryFn: () => api.getPI(piId!),
    enabled: !!piId,
  });

  const { data: risks = [], isLoading } = useQuery({
    queryKey: ['risks', piId],
    queryFn: () => api.listRisks(piId!),
    enabled: !!piId,
  });

  const { data: teams = [] } = useQuery({
    queryKey: ['teams'],
    queryFn: api.listTeams,
  });

  if (isLoading) return <Spinner />;

  const teamMap = Object.fromEntries(teams.map((t) => [t.id, t.name]));

  const unroamed = risks.filter((r) => r.roam_status === 'unroamed').length;

  return (
    <div className="p-6">
      <div className="mb-5 flex items-baseline justify-between">
        <div>
          <h1 className="mb-1 text-xl font-semibold text-slate-800">
            Risk Register — {pi?.name}
          </h1>
          <p className="text-sm text-slate-500">
            {risks.length} risk{risks.length !== 1 ? 's' : ''}
            {unroamed > 0 && (
              <span className="ml-2 font-medium text-red-600">{unroamed} unroamed</span>
            )}
          </p>
        </div>
      </div>

      {risks.length === 0 ? (
        <EmptyState message="No risks for this PI." />
      ) : (
        <div className="overflow-x-auto overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                {['Description', 'Team', 'Status', 'Owner', 'Raised', 'Notes'].map((h) => (
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
              {risks.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50/60">
                  <td className="px-4 py-2.5 font-medium text-slate-800">{r.description}</td>
                  <td className="px-4 py-2.5 text-slate-600">
                    {r.team_id ? (teamMap[r.team_id] ?? r.team_id) : '—'}
                  </td>
                  <td className="px-4 py-2.5">
                    <ROAMBadge status={r.roam_status} />
                  </td>
                  <td className="px-4 py-2.5 text-slate-500">{r.owner ?? '—'}</td>
                  <td className="px-4 py-2.5 text-slate-500 tabular-nums">{r.raised_date}</td>
                  <td className="max-w-xs px-4 py-2.5 text-slate-500">
                    {r.mitigation_notes || '—'}
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
