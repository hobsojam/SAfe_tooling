import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import { DepBadge, FeatureStatusBadge } from '../components/Badge';
import { EmptyState } from '../components/EmptyState';
import { Spinner } from '../components/Spinner';
import type { Feature, Story } from '../types';

type BoardGrid = Record<string, Record<string, Feature[]>>;

function featurePrimaryIteration(featureId: string, stories: Story[]): string {
  const weight: Record<string, number> = {};
  for (const s of stories) {
    if (s.feature_id === featureId && s.iteration_id) {
      weight[s.iteration_id] = (weight[s.iteration_id] ?? 0) + s.points;
    }
  }
  const entries = Object.entries(weight);
  if (entries.length === 0) return 'unplanned';
  return entries.sort(([, a], [, b]) => b - a)[0][0];
}

function buildBoard(features: Feature[], stories: Story[]): BoardGrid {
  const grid: BoardGrid = {};
  for (const feature of features) {
    if (!feature.team_id) continue;
    const key = featurePrimaryIteration(feature.id, stories);
    (grid[feature.team_id] ??= {})[key] ??= [];
    grid[feature.team_id][key].push(feature);
  }
  return grid;
}

function FeatureCard({ feature }: { feature: Feature }) {
  return (
    <div className="rounded border border-slate-200 bg-white px-2 py-1.5 shadow-sm">
      <p className="text-xs font-medium text-slate-800 leading-snug">{feature.name}</p>
      <div className="mt-1 flex items-center gap-1.5">
        <FeatureStatusBadge status={feature.status} />
        <span className="text-xs text-slate-400">WSJF {feature.wsjf_score}</span>
      </div>
    </div>
  );
}

export function Board() {
  const { piId } = useParams<{ piId: string }>();

  const { data: pi } = useQuery({
    queryKey: ['pi', piId],
    queryFn: () => api.getPI(piId!),
    enabled: !!piId,
  });

  const { data: iterations = [] } = useQuery({
    queryKey: ['iterations', piId],
    queryFn: () => api.listIterations(piId!),
    enabled: !!piId,
  });

  const { data: features = [], isLoading: loadingFeatures } = useQuery({
    queryKey: ['features', piId],
    queryFn: () => api.listFeatures(piId!),
    enabled: !!piId,
  });

  const { data: stories = [] } = useQuery({
    queryKey: ['stories'],
    queryFn: api.listStories,
  });

  const { data: teams = [] } = useQuery({
    queryKey: ['teams'],
    queryFn: api.listTeams,
  });

  const { data: deps = [] } = useQuery({
    queryKey: ['dependencies', piId],
    queryFn: () => api.listDependencies(piId!),
    enabled: !!piId,
  });

  if (loadingFeatures) return <Spinner />;

  const sortedIters = [...iterations].sort((a, b) => a.number - b.number);
  const assignedFeatures = features.filter((f) => f.team_id);

  if (assignedFeatures.length === 0) {
    return <EmptyState message="No features assigned to teams for this PI." />;
  }

  const grid = buildBoard(assignedFeatures, stories);
  const teamMap = Object.fromEntries(teams.map((t) => [t.id, t.name]));
  const teamIds = [...new Set(assignedFeatures.map((f) => f.team_id!))];

  const iterCols = sortedIters.map((i) => ({
    id: i.id,
    label: `I${i.number}${i.is_ip ? ' (IP)' : ''}`,
  }));

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold text-slate-800">
        Program Board — {pi?.name}
      </h1>
      <p className="mb-5 text-sm text-slate-500">
        Features placed by story-point majority per iteration
      </p>

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="w-full table-fixed border-collapse text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="w-32 px-3 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">
                Team
              </th>
              {iterCols.map((c) => (
                <th
                  key={c.id}
                  className="px-3 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide"
                >
                  {c.label}
                </th>
              ))}
              <th className="px-3 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Unplanned
              </th>
            </tr>
          </thead>
          <tbody>
            {teamIds.map((teamId, i) => {
              const teamGrid = grid[teamId] ?? {};
              return (
                <tr
                  key={teamId}
                  className={i % 2 === 0 ? 'bg-white' : 'bg-slate-50/60'}
                >
                  <td className="border-r border-slate-100 px-3 py-2 align-top">
                    <span className="font-medium text-slate-700">
                      {teamMap[teamId] ?? teamId}
                    </span>
                  </td>
                  {iterCols.map((c) => (
                    <td key={c.id} className="border-r border-slate-100 px-2 py-2 align-top">
                      <div className="space-y-1.5">
                        {(teamGrid[c.id] ?? []).map((f) => (
                          <FeatureCard key={f.id} feature={f} />
                        ))}
                      </div>
                    </td>
                  ))}
                  <td className="px-2 py-2 align-top">
                    <div className="space-y-1.5">
                      {(teamGrid['unplanned'] ?? []).map((f) => (
                        <FeatureCard key={f.id} feature={f} />
                      ))}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Dependencies */}
      {deps.length > 0 && (
        <div className="mt-8">
          <h2 className="mb-3 text-base font-semibold text-slate-700">
            Dependencies ({deps.length})
          </h2>
          <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  {['From', 'To', 'Description', 'Status', 'Owner'].map((h) => (
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
                  <tr key={d.id}>
                    <td className="px-4 py-2.5 text-slate-700">
                      {teamMap[d.from_team_id] ?? d.from_team_id}
                    </td>
                    <td className="px-4 py-2.5 text-slate-700">
                      {teamMap[d.to_team_id] ?? d.to_team_id}
                    </td>
                    <td className="px-4 py-2.5 text-slate-600">{d.description}</td>
                    <td className="px-4 py-2.5">
                      <DepBadge status={d.status} />
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">{d.owner ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
