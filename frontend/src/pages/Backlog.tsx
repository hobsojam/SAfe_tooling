import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import type { Feature, FeatureCreate, FeatureStatus, FeatureUpdate } from '../types';
import { FeatureStatusBadge } from '../components/Badge';
import { EmptyState } from '../components/EmptyState';
import { Modal } from '../components/Modal';
import { Spinner } from '../components/Spinner';

const STATUS_OPTIONS: FeatureStatus[] = ['funnel', 'analyzing', 'backlog', 'implementing', 'done'];

interface FeatureFormState {
  name: string;
  description: string;
  team_id: string | null;
  status: FeatureStatus;
  user_business_value: number;
  time_criticality: number;
  risk_reduction_opportunity_enablement: number;
  job_size: number;
}

const EMPTY_FORM: FeatureFormState = {
  name: '',
  description: '',
  team_id: null,
  status: 'backlog',
  user_business_value: 5,
  time_criticality: 5,
  risk_reduction_opportunity_enablement: 5,
  job_size: 5,
};

export function Backlog() {
  const { piId } = useParams<{ piId: string }>();
  const qc = useQueryClient();

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Feature | null>(null);
  const [form, setForm] = useState<FeatureFormState>(EMPTY_FORM);
  const [error, setError] = useState('');

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

  const invalidate = () => qc.invalidateQueries({ queryKey: ['features', piId] });

  const createMut = useMutation({
    mutationFn: (body: FeatureCreate) => api.createFeature(body),
    onSuccess: () => { invalidate(); closeModal(); },
    onError: (e: Error) => setError(e.message),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, body }: { id: string; body: FeatureUpdate }) =>
      api.updateFeature(id, body),
    onSuccess: () => { invalidate(); closeModal(); },
    onError: (e: Error) => setError(e.message),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api.deleteFeature(id),
    onSuccess: invalidate,
  });

  if (isLoading) return <Spinner />;

  const sorted = [...features].sort((a, b) => b.wsjf_score - a.wsjf_score);
  const teamMap = Object.fromEntries(teams.map((t) => [t.id, t.name]));

  function openNew() {
    setEditing(null);
    setForm(EMPTY_FORM);
    setError('');
    setModalOpen(true);
  }

  function openEdit(f: Feature) {
    setEditing(f);
    setForm({
      name: f.name,
      description: f.description,
      team_id: f.team_id,
      status: f.status,
      user_business_value: f.user_business_value,
      time_criticality: f.time_criticality,
      risk_reduction_opportunity_enablement: f.risk_reduction_opportunity_enablement,
      job_size: f.job_size,
    });
    setError('');
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setEditing(null);
    setError('');
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) { setError('Feature name is required.'); return; }
    if (editing) {
      updateMut.mutate({
        id: editing.id,
        body: { ...form, team_id: form.team_id || null },
      });
    } else {
      createMut.mutate({ ...form, pi_id: piId!, team_id: form.team_id || null });
    }
  }

  function handleDelete(id: string) {
    if (!window.confirm('Delete this feature?')) return;
    deleteMut.mutate(id);
  }

  const isPending = createMut.isPending || updateMut.isPending;

  function numInput(
    label: string,
    key: 'user_business_value' | 'time_criticality' | 'risk_reduction_opportunity_enablement' | 'job_size',
    min: number,
    max: number,
  ) {
    return (
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">
          {label}{' '}
          <span className="font-normal text-slate-400">({min}–{max})</span>
        </label>
        <input
          type="number"
          min={min}
          max={max}
          value={form[key]}
          onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
        />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-5 flex items-baseline justify-between">
        <div>
          <h1 className="mb-1 text-xl font-semibold text-slate-800">
            Program Backlog — {pi?.name}
          </h1>
          <p className="text-sm text-slate-500">Features ranked by WSJF score (highest first)</p>
        </div>
        <button
          onClick={openNew}
          className="rounded-md bg-slate-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700 transition-colors"
        >
          + New Feature
        </button>
      </div>

      {sorted.length === 0 ? (
        <EmptyState message="No features in this PI." />
      ) : (
        <div className="overflow-x-auto overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                {['#', 'Feature', 'Status', 'Team', 'CoD', 'Size', 'WSJF', ''].map((h) => (
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
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    <button
                      onClick={() => openEdit(f)}
                      className="mr-3 text-xs text-slate-500 hover:text-slate-800 underline"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(f.id)}
                      className="text-xs text-red-400 hover:text-red-600 underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        title={editing ? 'Edit Feature' : 'New Feature'}
        onClose={closeModal}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-sm text-red-600">{error}</p>}

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Name *</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={2}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Status</label>
              <select
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value as FeatureStatus })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Team</label>
              <select
                value={form.team_id ?? ''}
                onChange={(e) => setForm({ ...form, team_id: e.target.value || null })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">— none —</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
          </div>

          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            WSJF Inputs
          </p>
          <div className="grid grid-cols-2 gap-3">
            {numInput('User / Business Value', 'user_business_value', 1, 10)}
            {numInput('Time Criticality', 'time_criticality', 1, 10)}
            {numInput('Risk Reduction / OE', 'risk_reduction_opportunity_enablement', 1, 10)}
            {numInput('Job Size', 'job_size', 1, 13)}
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={closeModal}
              className="rounded-md px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50 transition-colors"
            >
              {isPending ? 'Saving…' : editing ? 'Save Changes' : 'Add Feature'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
