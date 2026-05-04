import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { NavLink, Outlet, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import type { PICreate } from '../types';
import { Modal } from './Modal';
import { PIStatusBadge } from './Badge';

const NAV = [
  { to: 'board', label: 'Board' },
  { to: 'backlog', label: 'Backlog' },
  { to: 'risks', label: 'Risks' },
  { to: 'dependencies', label: 'Dependencies' },
  { to: 'setup', label: 'PI Setup' },
];

const EMPTY_PI_FORM: PICreate = {
  name: '',
  art_id: '',
  start_date: '',
  end_date: '',
};

export function Layout() {
  const { piId } = useParams<{ piId: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [piModalOpen, setPiModalOpen] = useState(false);
  const [piForm, setPiForm] = useState<PICreate>(EMPTY_PI_FORM);
  const [piError, setPiError] = useState('');

  const { data: pis = [] } = useQuery({
    queryKey: ['pis'],
    queryFn: api.listPIs,
  });

  const { data: arts = [] } = useQuery({
    queryKey: ['arts'],
    queryFn: api.listARTs,
  });

  const activePi = pis.find((p) => p.id === piId);

  const createPIMut = useMutation({
    mutationFn: (body: PICreate) => api.createPI(body),
    onSuccess: (pi) => {
      qc.invalidateQueries({ queryKey: ['pis'] });
      setPiModalOpen(false);
      navigate(`/pi/${pi.id}/board`);
    },
    onError: (e: Error) => setPiError(e.message),
  });

  function openNewPI() {
    setPiForm({ name: '', art_id: arts[0]?.id ?? '', start_date: '', end_date: '' });
    setPiError('');
    setPiModalOpen(true);
  }

  function handlePISubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!piForm.name.trim()) { setPiError('Name is required.'); return; }
    if (!piForm.art_id) { setPiError('ART is required.'); return; }
    if (!piForm.start_date || !piForm.end_date) { setPiError('Start and end dates are required.'); return; }
    createPIMut.mutate(piForm);
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="flex w-56 flex-col bg-slate-900 text-slate-100">
        <div className="px-4 py-5">
          <span className="text-sm font-semibold tracking-wide text-slate-300 uppercase">
            SAFe Tools
          </span>
        </div>

        {/* PI selector */}
        <div className="px-3 pb-4">
          <label
            htmlFor="pi-select"
            className="mb-1 block text-xs text-slate-400"
          >
            Program Increment
          </label>
          <select
            id="pi-select"
            value={piId ?? ''}
            onChange={(e) => {
              if (e.target.value) navigate(`/pi/${e.target.value}/board`);
            }}
            className="w-full rounded bg-slate-700 px-2 py-1.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            <option value="" disabled>
              Select PI…
            </option>
            {pis.map((pi) => (
              <option key={pi.id} value={pi.id}>
                {pi.name}
              </option>
            ))}
          </select>
          {activePi && (
            <div className="mt-1.5 flex items-center gap-1.5 text-xs text-slate-400">
              <PIStatusBadge status={activePi.status} />
              <span>
                {activePi.start_date} – {activePi.end_date}
              </span>
            </div>
          )}
        </div>

        {/* Nav links */}
        {piId && (
          <nav className="flex-1 space-y-0.5 px-2">
            {NAV.map(({ to, label }) => (
              <NavLink
                key={to}
                to={`/pi/${piId}/${to}`}
                className={({ isActive }) =>
                  `block rounded px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-700 text-white'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        )}

        {/* New PI button */}
        <div className="mt-auto px-3 pb-2">
          <button
            onClick={openNewPI}
            className="w-full rounded bg-slate-700 px-2 py-1.5 text-left text-sm text-slate-300 hover:bg-slate-600 hover:text-white transition-colors"
          >
            + New PI
          </button>
        </div>

        {/* Disclaimer */}
        <p className="px-3 pb-4 text-xs leading-tight text-slate-500">
          Not an official Scaled Agile product. SAFe® is a registered trademark of Scaled Agile, Inc.
        </p>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {piId ? (
          <Outlet />
        ) : (
          <div className="flex h-full items-center justify-center text-slate-400">
            <p className="text-sm">Select a Program Increment to get started.</p>
          </div>
        )}
      </main>

      <Modal
        open={piModalOpen}
        title="New Program Increment"
        onClose={() => setPiModalOpen(false)}
      >
        <form onSubmit={handlePISubmit} className="space-y-4">
          {piError && <p className="text-sm text-red-600">{piError}</p>}

          <div>
            <label htmlFor="pi-name" className="mb-1 block text-sm font-medium text-slate-700">
              Name<span aria-hidden="true"> *</span>
            </label>
            <input
              id="pi-name"
              type="text"
              value={piForm.name}
              onChange={(e) => setPiForm({ ...piForm, name: e.target.value })}
              placeholder="e.g. PI 2026.2"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            />
          </div>

          <div>
            <label htmlFor="pi-art" className="mb-1 block text-sm font-medium text-slate-700">
              ART<span aria-hidden="true"> *</span>
            </label>
            <select
              id="pi-art"
              value={piForm.art_id}
              onChange={(e) => setPiForm({ ...piForm, art_id: e.target.value })}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
            >
              <option value="">Select ART…</option>
              {arts.map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
            {arts.length === 0 && (
              <p className="mt-1 text-xs text-slate-400">
                No ARTs found. Create one with the CLI first.
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="pi-start" className="mb-1 block text-sm font-medium text-slate-700">
                Start Date<span aria-hidden="true"> *</span>
              </label>
              <input
                id="pi-start"
                type="date"
                value={piForm.start_date}
                onChange={(e) => setPiForm({ ...piForm, start_date: e.target.value })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
            <div>
              <label htmlFor="pi-end" className="mb-1 block text-sm font-medium text-slate-700">
                End Date<span aria-hidden="true"> *</span>
              </label>
              <input
                id="pi-end"
                type="date"
                value={piForm.end_date}
                onChange={(e) => setPiForm({ ...piForm, end_date: e.target.value })}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setPiModalOpen(false)}
              className="rounded-md px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createPIMut.isPending}
              className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50 transition-colors"
            >
              {createPIMut.isPending ? 'Creating…' : 'Create PI'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
