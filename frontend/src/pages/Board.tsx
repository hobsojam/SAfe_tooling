import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import { useQueryClient, useQuery, useMutation } from '@tanstack/react-query';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import { DepBadge, FeatureStatusBadge } from '../components/Badge';
import { EmptyState } from '../components/EmptyState';
import { Spinner } from '../components/Spinner';
import type { Dependency, Feature, Story } from '../types';

type BoardGrid = Record<string, Record<string, Feature[]>>;

interface Arrow {
  depId: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  resolved: boolean;
}

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
    // Prefer explicit iteration_id override; fall back to story-majority
    const key = feature.iteration_id ?? featurePrimaryIteration(feature.id, stories);
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

function DraggableFeatureCard({ feature }: { feature: Feature }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: feature.id,
    data: { feature },
  });
  const style = transform
    ? { transform: `translate(${transform.x}px, ${transform.y}px)` }
    : undefined;
  return (
    <div
      ref={setNodeRef}
      style={style}
      data-feature-id={feature.id}
      {...attributes}
      {...listeners}
      className={isDragging ? 'opacity-50 cursor-grabbing' : 'cursor-grab'}
    >
      <FeatureCard feature={feature} />
    </div>
  );
}

function DroppableCell({ id, children }: { id: string; children: React.ReactNode }) {
  const { setNodeRef, isOver } = useDroppable({ id });
  return (
    <div
      ref={setNodeRef}
      className={`min-h-[4rem] p-2 space-y-1.5 border-r border-slate-100 transition-colors ${isOver ? 'bg-blue-50' : ''}`}
    >
      {children}
    </div>
  );
}

function crossTeamOnly(deps: Dependency[], features: Feature[]): Dependency[] {
  return deps.filter((d) => {
    const from = features.find((f) => f.id === d.from_feature_id);
    const to = features.find((f) => f.id === d.to_feature_id);
    return from?.team_id && to?.team_id && from.team_id !== to.team_id;
  });
}

export function Board() {
  const { piId } = useParams<{ piId: string }>();
  const queryClient = useQueryClient();
  const [activeFeature, setActiveFeature] = useState<Feature | null>(null);
  const boardRef = useRef<HTMLDivElement>(null);
  const [arrows, setArrows] = useState<Arrow[]>([]);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

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

  const ctDeps = useMemo(() => crossTeamOnly(deps, features), [deps, features]);

  const measureArrows = useCallback(() => {
    if (!boardRef.current) return;
    const container = boardRef.current;
    const cr = container.getBoundingClientRect();
    const measured: Arrow[] = [];
    for (const dep of ctDeps) {
      const fromEl = container.querySelector<HTMLElement>(`[data-feature-id="${dep.from_feature_id}"]`);
      const toEl = container.querySelector<HTMLElement>(`[data-feature-id="${dep.to_feature_id}"]`);
      if (!fromEl || !toEl) continue;
      const fr = fromEl.getBoundingClientRect();
      const tr = toEl.getBoundingClientRect();
      measured.push({
        depId: dep.id,
        x1: fr.right - cr.left,
        y1: fr.top + fr.height / 2 - cr.top,
        x2: tr.left - cr.left,
        y2: tr.top + tr.height / 2 - cr.top,
        resolved: dep.status === 'resolved',
      });
    }
    setArrows(measured);
  }, [ctDeps]);

  useEffect(() => {
    const id = requestAnimationFrame(measureArrows);
    return () => cancelAnimationFrame(id);
  }, [measureArrows]);

  useEffect(() => {
    if (!boardRef.current) return;
    const ro = new ResizeObserver(() => requestAnimationFrame(measureArrows));
    ro.observe(boardRef.current);
    return () => ro.disconnect();
  }, [measureArrows]);

  const moveMutation = useMutation({
    mutationFn: ({ featureId, teamId, iterationId }: { featureId: string; teamId: string; iterationId: string | null }) =>
      api.updateFeature(featureId, { team_id: teamId, iteration_id: iterationId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features', piId] });
    },
  });

  function handleDragStart(event: DragStartEvent) {
    const feature = (event.active.data.current as { feature: Feature }).feature;
    setActiveFeature(feature);
  }

  function handleDragEnd(event: DragEndEvent) {
    setActiveFeature(null);
    if (!event.over) return;

    const overId = event.over.id as string;
    const [newTeamId, newIterColId] = overId.split('|');
    const feature = (event.active.data.current as { feature: Feature }).feature;

    const newIterationId = newIterColId === 'unplanned' ? null : newIterColId;
    const currentIterKey = feature.iteration_id ?? featurePrimaryIteration(feature.id, stories);
    const currentIterColId = currentIterKey === null ? 'unplanned' : currentIterKey;

    if (feature.team_id === newTeamId && currentIterColId === newIterColId) return;

    moveMutation.mutate({ featureId: feature.id, teamId: newTeamId, iterationId: newIterationId });
  }

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

  const numCols = iterCols.length + 1; // +1 for Unplanned
  const gridTemplateColumns = `8rem repeat(${numCols}, minmax(120px, 1fr))`;

  return (
    <div className="p-6">
      <h1 className="mb-1 text-xl font-semibold text-slate-800">
        Program Board — {pi?.name}
      </h1>
      <p className="mb-5 text-sm text-slate-500">
        Drag features between cells to reassign team and iteration
      </p>

      <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
        <div ref={boardRef} style={{ position: 'relative' }}>
        <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
          <div style={{ display: 'grid', gridTemplateColumns }}>
            {/* Header row */}
            <div className="border-b border-r border-slate-200 bg-slate-50 px-3 py-2.5">
              <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">Team</span>
            </div>
            {iterCols.map((c) => (
              <div
                key={c.id}
                className="border-b border-r border-slate-200 bg-slate-50 px-3 py-2.5"
              >
                <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
                  {c.label}
                </span>
              </div>
            ))}
            <div className="border-b border-slate-200 bg-slate-50 px-3 py-2.5">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Unplanned
              </span>
            </div>

            {/* Team rows */}
            {teamIds.map((teamId, rowIdx) => {
              const teamGrid = grid[teamId] ?? {};
              const rowBg = rowIdx % 2 === 0 ? '' : 'bg-slate-50/60';
              return (
                <>
                  <div
                    key={`${teamId}-name`}
                    className={`border-b border-r border-slate-100 px-3 py-2 flex items-start ${rowBg}`}
                  >
                    <span className="font-medium text-sm text-slate-700">
                      {teamMap[teamId] ?? teamId}
                    </span>
                  </div>
                  {iterCols.map((c) => (
                    <div key={`${teamId}-${c.id}`} className={`border-b border-slate-100 ${rowBg}`}>
                      <DroppableCell id={`${teamId}|${c.id}`}>
                        {(teamGrid[c.id] ?? []).map((f) => (
                          <DraggableFeatureCard key={f.id} feature={f} />
                        ))}
                      </DroppableCell>
                    </div>
                  ))}
                  <div key={`${teamId}-unplanned`} className={`border-b border-slate-100 ${rowBg}`}>
                    <DroppableCell id={`${teamId}|unplanned`}>
                      {(teamGrid['unplanned'] ?? []).map((f) => (
                        <DraggableFeatureCard key={f.id} feature={f} />
                      ))}
                    </DroppableCell>
                  </div>
                </>
              );
            })}
          </div>

          <DragOverlay>
            {activeFeature ? (
              <div className="opacity-90 shadow-lg">
                <FeatureCard feature={activeFeature} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
        {arrows.length > 0 && (
          <svg
            aria-hidden="true"
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', overflow: 'visible' }}
          >
            <defs>
              <marker id="dep-arrow" markerWidth="6" markerHeight="4" refX="5.5" refY="2" orient="auto">
                <polygon points="0 0, 6 2, 0 4" fill="#dc2626" />
              </marker>
            </defs>
            {arrows.map((a) => {
              const dx = Math.max(40, Math.abs(a.x2 - a.x1) * 0.4);
              return (
                <path
                  key={a.depId}
                  data-dep-id={a.depId}
                  d={`M ${a.x1} ${a.y1} C ${a.x1 + dx} ${a.y1}, ${a.x2 - dx} ${a.y2}, ${a.x2} ${a.y2}`}
                  stroke="#dc2626"
                  strokeWidth="2"
                  fill="none"
                  opacity={a.resolved ? 0.35 : 0.85}
                  strokeDasharray={a.resolved ? '5 3' : undefined}
                  markerEnd="url(#dep-arrow)"
                />
              );
            })}
          </svg>
        )}
        </div>
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
                {deps.map((d) => {
                  const fromFeature = features.find((f) => f.id === d.from_feature_id);
                  const toFeature = features.find((f) => f.id === d.to_feature_id);
                  const fromLabel = fromFeature
                    ? `${fromFeature.name}${fromFeature.team_id ? ` (${teamMap[fromFeature.team_id] ?? ''})` : ''}`
                    : d.from_feature_id;
                  const toLabel = toFeature
                    ? `${toFeature.name}${toFeature.team_id ? ` (${teamMap[toFeature.team_id] ?? ''})` : ''}`
                    : d.to_feature_id;
                  return (
                    <tr key={d.id}>
                      <td className="px-4 py-2.5 text-slate-700">{fromLabel}</td>
                      <td className="px-4 py-2.5 text-slate-700">{toLabel}</td>
                      <td className="px-4 py-2.5 text-slate-600">{d.description}</td>
                      <td className="px-4 py-2.5">
                        <DepBadge status={d.status} />
                      </td>
                      <td className="px-4 py-2.5 text-slate-500">{d.owner ?? '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
