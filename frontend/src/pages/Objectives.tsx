import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api';
import type { PIObjective, PIObjectiveCreate, PIObjectiveUpdate } from '../types';
import { EmptyState } from '../components/EmptyState';
import { Modal } from '../components/Modal';
import { Spinner } from '../components/Spinner';

interface ObjectiveFormState {
  description: string;
  team_id: string;
  planned_business_value: number;
  actual_business_value: string;
  is_stretch: boolean;
}

const EMPTY_FORM: ObjectiveFormState = {
  description: '',
  team_id: '',
  planned_business_value: 5,
  actual_business_value: '',
  is_stretch: false,
};

export function Objectives() {
  const { piId } = useParams<{ piId: string }>();
  const qc = useQueryClient();

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<PIObjective | null>(null);
  const [form, setForm] = useState<ObjectiveFormState>(EMPTY_FORM);
  const [error, setError] = useState('');
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState('');

  const { data: pi } = useQuery({
    queryKey: ['pi', piId],
    queryFn: () => api.getPI(piId!),
    enabled: !!piId,
  });

  const { data: objectives = [], isLoading } = useQuery({
    queryKey: ['objectives', piId],
    queryFn: () => api.listObjectives(piId!),
    enabled: !!piId,
  });

  const { data: teams = [] } = useQuery({
    queryKey: ['teams'],
    queryFn: api.listTeams,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ['objectives', piId] });

  const createMut = useMutation({
    mutationFn: (body: PIObjectiveCreate) => api.createObjective(body),
    onSuccess: () => { invalidate(); closeModal(); },
    onError: (e: Error) => setError(e.message),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, body }: { id: string; body: PIObjectiveUpdate }) =>
      api.updateObjective(id, body),
    onSuccess: () => { invalidate(); closeModal(); },
    onError: (e: Error) => setError(e.message),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api.deleteObjective(id),
    onSuccess: () => { invalidate(); setDeleteId(null); setDeleteError(''); },
    onError: (e: Error) => setDeleteError(e.message),
  });

  if (isLoading) return <Spinner />;

  const teamMap = Object.fromEntries(teams.map((t) => [t.id, t.name]));
  const committed = objectives.filter((o) => !o.is_stretch);
  const stretch = objectives.filter((o) => o.is_stretch);
  const sorted = [...committed, ...stretch];

  function openNew() {
    setEditing(null);
    setForm({ ...EMPTY_FORM, team_id: teams[0]?.id ?? '' });
    setError('');
    setModalOpen(true);
  }

  function openEdit(o: PIObjective) {
    setEditing(o);
    setForm({
      description: o.description,
      team_id: o.team_id,
      planned_business_value: o.planned_business_value,
      actual_business_value: o.actual_business_value !== null ? String(o.actual_business_value) : '',
      is_stretch: o.is_stretch,
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
    if (!form.team_id) { setError('Team is required.'); return; }

    const actualBV = form.actual_business_value !== '' ? Number(form.actual_business_value) : null;

    if (editing) {
      updateMut.mutate({
        id: editing.id,
        body: {
          description: form.description,
          planned_business_value: form.planned_business_value,
          actual_business_value: actualBV,
          is_stretch: form.is_stretch,
        },
      });
    } else {
      createMut.mutate({
        description: form.description,
        team_id: form.team_id,
        pi_id: piId!,
        planned_business_value: form.planned_business_value,
        actual_business_value: actualBV,
        is_stretch: form.is_stretch,
      });
    }
  }

  const isPending = createMut.isPending || updateMut.isPending;

  return (
    <div className="p-6">
      <div className="mb-5 flex items-baseline justify-between">
        <div>
          <h1 className="mb-1 text-xl font-semibold text-slate-800">
            PI Objectives — {pi?.name}
          </h1>
          <p className="text-sm text-slate-500">
            Committed: {committed.length} · Stretch: {stretch.length}
          </p>
        </div>
        <button
          onClick={openNew}
          className="rounded-md bg-slate-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700 transition-colors"
        >
          + New Objective
        </button>
      </div>

      {sorted.length === 0 ? (
        <EmptyState message="No PI objectives yet." />
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                {['Description', 'Team', 'Type', 'Planned BV', 'Actual BV', ''].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left text-xs font-semibold text-slate-600 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sorted.map((obj) => {
                if (deleteId === obj.id) {
                  return (
                    <tr key={obj.id} className="bg-red-50">
                      <td colSpan={6} className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          {deleteError && <span className="text-xs text-red-600">{deleteError}</span>}
                          <span className="text-sm text-slate-700">
                            Delete <strong>{obj.description.slice(0, 50)}{obj.description.length > 50 ? '…' : ''}</strong>?
                          </span>
                          <button
                            onClick={() => deleteMut.mutate(obj.id)}
                            disabled={deleteMut.isPending}
                            className="rounded-md bg-red-600 px-3 py-1 text-xs font-medium text-white hover:bg-red-700 disabled:opacity-50 transition-colors"
                          >
                            {deleteMut.isPending ? 'Deleting…' : 'Yes, delete'}
                          </button>
                          <button
                            onClick={() => { setDeleteId(null); setDeleteError(''); }}
                            className="text-xs text-slate-500 hover:text-slate-800 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                }

                return (
                  <tr key={obj.id} className="hover:bg-slate-50/60">
                    <td className="px-4 py-2.5 text-slate-800 max-w-xs">
                      <button
                        onClick={() => openEdit(obj)}
                        className="text-left hover:text-slate-600 hover:underline"
                      >
                        {obj.description}
                      </button>
                    </td>
                    <td className="px-4 py-2.5 text-slate-600">{teamMap[obj.team_id] ?? '—'}</td>
                    <td className="px-4 py-2.5">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${obj.is_stretch ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                        {obj.is_stretch ? 'Stretch' : 'Committed'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">{obj.planned_business_value}</td>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">
                      {obj.actual_business_value !== null
                        ? obj.actual_business_value
                        : <span className="text-slate-400">—</span>}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap text-right">
                      <button
                        onClick={() => openEdit(obj)}
                        className="mr-3 text-xs text-slate-500 hover:text-slate-800 underline"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => { setDeleteId(obj.id); setDeleteError(''); }}
                        className="text-xs text-red-400 hover:text-red-600 underline"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        title={editing ? 'Edit Objective' : 'New Objective'}
        onClose={closeModal}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-sm text-red-600">{error}</p>}

          <div>
            <label htmlFor="obj-desc" className="mb-1 block text-sm font-medium text-slate-700">
              Description<span aria-hidden="true"> *</span>
            </label>
            <textarea
              id="obj-desc"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={2}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            />
          </div>

          {!editing && (
            <div>
              <label htmlFor="obj-team" className="mb-1 block text-sm font-medium text-slate-700">
                Team<span aria-hidden="true"> *</span>
              </label>
              <select
                id="obj-team"
                value={form.team_id}
                onChange={(e) => setForm({ ...form, team_id: e.target.value })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              >
                <option value="">Select team…</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="obj-planned-bv" className="mb-1 block text-sm font-medium text-slate-700">
                Planned BV (1–10)<span aria-hidden="true"> *</span>
              </label>
              <input
                id="obj-planned-bv"
                type="number"
                min={1}
                max={10}
                value={form.planned_business_value}
                onChange={(e) => setForm({ ...form, planned_business_value: Number(e.target.value) })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
            <div>
              <label htmlFor="obj-actual-bv" className="mb-1 block text-sm font-medium text-slate-700">
                Actual BV <span className="font-normal text-slate-400">(blank if not yet scored)</span>
              </label>
              <input
                id="obj-actual-bv"
                type="number"
                min={0}
                max={10}
                value={form.actual_business_value}
                onChange={(e) => setForm({ ...form, actual_business_value: e.target.value })}
                placeholder="—"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_stretch}
              onChange={(e) => setForm({ ...form, is_stretch: e.target.checked })}
              className="rounded border-slate-300"
            />
            Stretch objective (not counted in ART predictability)
          </label>

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
              {isPending ? 'Saving…' : editing ? 'Save Changes' : 'Add Objective'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
