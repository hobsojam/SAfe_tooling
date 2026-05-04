import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import type { Dependency, DependencyCreate, DependencyStatus, DependencyUpdate } from '../types';
import { DepBadge } from '../components/Badge';
import { EmptyState } from '../components/EmptyState';
import { Modal } from '../components/Modal';
import { Spinner } from '../components/Spinner';

const STATUS_OPTIONS: DependencyStatus[] = ['identified', 'owned', 'accepted', 'mitigated', 'resolved'];

interface DepFormState {
  description: string;
  from_team_id: string;
  to_team_id: string;
  status: DependencyStatus;
  owner: string | null;
  needed_by_date: string | null;
  resolution_notes: string;
}

const EMPTY_FORM: DepFormState = {
  description: '',
  from_team_id: '',
  to_team_id: '',
  status: 'identified',
  owner: null,
  needed_by_date: null,
  resolution_notes: '',
};

export function Dependencies() {
  const { piId } = useParams<{ piId: string }>();
  const qc = useQueryClient();

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Dependency | null>(null);
  const [form, setForm] = useState<DepFormState>(EMPTY_FORM);
  const [error, setError] = useState('');

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

  const invalidate = () => qc.invalidateQueries({ queryKey: ['dependencies', piId] });

  const createMut = useMutation({
    mutationFn: (body: DependencyCreate) => api.createDependency(body),
    onSuccess: () => { invalidate(); closeModal(); },
    onError: (e: Error) => setError(e.message),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, body }: { id: string; body: DependencyUpdate }) =>
      api.updateDependency(id, body),
    onSuccess: () => { invalidate(); closeModal(); },
    onError: (e: Error) => setError(e.message),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api.deleteDependency(id),
    onSuccess: invalidate,
  });

  if (isLoading) return <Spinner />;

  const teamMap = Object.fromEntries(teams.map((t) => [t.id, t.name]));
  const unresolved = deps.filter((d) => d.status !== 'resolved').length;

  function openNew() {
    setEditing(null);
    setForm({
      ...EMPTY_FORM,
      from_team_id: teams[0]?.id ?? '',
      to_team_id: teams[1]?.id ?? teams[0]?.id ?? '',
    });
    setError('');
    setModalOpen(true);
  }

  function openEdit(d: Dependency) {
    setEditing(d);
    setForm({
      description: d.description,
      from_team_id: d.from_team_id,
      to_team_id: d.to_team_id,
      status: d.status,
      owner: d.owner,
      needed_by_date: d.needed_by_date,
      resolution_notes: d.resolution_notes,
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
    if (!form.description.trim()) { setError('Description is required.'); return; }
    if (!form.from_team_id || !form.to_team_id) { setError('From and To teams are required.'); return; }
    if (editing) {
      updateMut.mutate({
        id: editing.id,
        body: {
          description: form.description,
          status: form.status,
          owner: form.owner || null,
          needed_by_date: form.needed_by_date || null,
          resolution_notes: form.resolution_notes,
        },
      });
    } else {
      createMut.mutate({
        description: form.description,
        pi_id: piId!,
        from_team_id: form.from_team_id,
        to_team_id: form.to_team_id,
        owner: form.owner || null,
        needed_by_date: form.needed_by_date || null,
      });
    }
  }

  function handleDelete(id: string) {
    if (!window.confirm('Delete this dependency?')) return;
    deleteMut.mutate(id);
  }

  const isPending = createMut.isPending || updateMut.isPending;

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
        <button
          onClick={openNew}
          className="rounded-md bg-slate-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700 transition-colors"
        >
          + New Dependency
        </button>
      </div>

      {deps.length === 0 ? (
        <EmptyState message="No dependencies for this PI." />
      ) : (
        <div className="overflow-x-auto overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                {['From', 'To', 'Description', 'Status', 'Owner', 'Needed By', ''].map((h) => (
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
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    <button
                      onClick={() => openEdit(d)}
                      className="mr-3 text-xs text-slate-500 hover:text-slate-800 underline"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(d.id)}
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
        title={editing ? 'Edit Dependency' : 'New Dependency'}
        onClose={closeModal}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-sm text-red-600">{error}</p>}

          <div>
            <label htmlFor="dep-description" className="mb-1 block text-sm font-medium text-slate-700">
              Description<span aria-hidden="true"> *</span>
            </label>
            <textarea
              id="dep-description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="dep-from" className="mb-1 block text-sm font-medium text-slate-700">
                From Team<span aria-hidden="true"> *</span>
              </label>
              <select
                id="dep-from"
                value={form.from_team_id}
                onChange={(e) => setForm({ ...form, from_team_id: e.target.value })}
                disabled={!!editing}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:bg-slate-50 disabled:text-slate-400"
              >
                <option value="">Select…</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="dep-to" className="mb-1 block text-sm font-medium text-slate-700">
                To Team<span aria-hidden="true"> *</span>
              </label>
              <select
                id="dep-to"
                value={form.to_team_id}
                onChange={(e) => setForm({ ...form, to_team_id: e.target.value })}
                disabled={!!editing}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:bg-slate-50 disabled:text-slate-400"
              >
                <option value="">Select…</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="dep-status" className="mb-1 block text-sm font-medium text-slate-700">Status</label>
            <select
              id="dep-status"
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value as DependencyStatus })}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="dep-owner" className="mb-1 block text-sm font-medium text-slate-700">Owner</label>
              <input
                id="dep-owner"
                type="text"
                value={form.owner ?? ''}
                onChange={(e) => setForm({ ...form, owner: e.target.value || null })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
            <div>
              <label htmlFor="dep-needed-by" className="mb-1 block text-sm font-medium text-slate-700">Needed By</label>
              <input
                id="dep-needed-by"
                type="date"
                value={form.needed_by_date ?? ''}
                onChange={(e) => setForm({ ...form, needed_by_date: e.target.value || null })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
          </div>

          {editing && (
            <div>
              <label htmlFor="dep-resolution" className="mb-1 block text-sm font-medium text-slate-700">Resolution Notes</label>
              <textarea
                id="dep-resolution"
                value={form.resolution_notes}
                onChange={(e) => setForm({ ...form, resolution_notes: e.target.value })}
                rows={2}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
          )}

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
              {isPending ? 'Saving…' : editing ? 'Save Changes' : 'Add Dependency'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
