import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import type { PICreate } from '../types';
import { Modal } from './Modal';
import { PIStatusBadge } from './Badge';

const NAV = [
  { to: 'board', label: 'Board' },
  { to: 'backlog', label: 'Backlog' },
  { to: 'objectives', label: 'Objectives' },
  { to: 'predictability', label: 'Predictability' },
  { to: 'capacity', label: 'Capacity' },
  { to: 'risks', label: 'Risks' },
  { to: 'dependencies', label: 'Dependencies' },
  { to: 'stories', label: 'Stories' },
  { to: 'setup', label: 'PI Setup' },
  { to: 'team-setup', label: 'Team Setup' },
];

const EMPTY_PI_FORM: PICreate = {
  name: '',
  art_id: '',
  start_date: '',
  end_date: '',
};

export function Layout() {
  const { piId } = useParams<{ piId: string }>();
  const location = useLocation();
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
    <div className="flex h-screen bg-bark-50">
      {/* Sidebar */}
      <aside className="flex w-56 flex-col bg-bark-900 text-bark-100">
        <div className="px-4 py-5">
          <span className="text-sm font-semibold tracking-wide text-bark-300 uppercase">
            SAFe Tools
          </span>
        </div>

        {/* PI selector */}
        <div className="px-3 pb-4">
          <label
            htmlFor="pi-select"
            className="mb-1 block text-xs text-bark-400"
          >
            Program Increment
          </label>
          <select
            id="pi-select"
            value={piId ?? ''}
            onChange={(e) => {
              if (e.target.value) navigate(`/pi/${e.target.value}/board`);
            }}
            className="w-full rounded bg-bark-700 px-2 py-1.5 text-sm text-bark-100 focus:outline-none focus:ring-2 focus:ring-moss-500"
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
            <div className="mt-1.5 flex items-center gap-1.5 text-xs text-bark-400">
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
                      ? 'bg-bark-700 text-white'
                      : 'text-bark-400 hover:bg-bark-800 hover:text-bark-100'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        )}

        {/* Global nav */}
        <div className="mt-auto border-t border-bark-700 px-2 pt-2">
          <NavLink
            to="/art-setup"
            className={({ isActive }) =>
              `block rounded px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-bark-700 text-white'
                  : 'text-bark-400 hover:bg-bark-800 hover:text-bark-100'
              }`
            }
          >
            ART Setup
          </NavLink>
        </div>

        {/* New PI button */}
        <div className="px-3 py-2">
          <button
            onClick={openNewPI}
            className="w-full rounded bg-bark-700 px-2 py-1.5 text-left text-sm text-bark-300 hover:bg-bark-600 hover:text-white transition-colors"
          >
            + New PI
          </button>
        </div>

        {/* Disclaimer */}
        <p className="px-3 pb-4 text-xs leading-tight text-bark-500">
          Not an official Scaled Agile product. SAFe® is a registered trademark of Scaled Agile, Inc.
        </p>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {piId || !location.pathname.startsWith('/pi') ? (
          <Outlet />
        ) : (
          <div className="flex h-full items-center justify-center text-bark-400">
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
            <label htmlFor="pi-name" className="mb-1 block text-sm font-medium text-bark-700">
              Name<span aria-hidden="true"> *</span>
            </label>
            <input
              id="pi-name"
              type="text"
              value={piForm.name}
              onChange={(e) => setPiForm({ ...piForm, name: e.target.value })}
              placeholder="e.g. PI 2026.2"
              className="w-full rounded-md border border-bark-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-moss-500"
            />
          </div>

          <div>
            <label htmlFor="pi-art" className="mb-1 block text-sm font-medium text-bark-700">
              ART<span aria-hidden="true"> *</span>
            </label>
            <select
              id="pi-art"
              value={piForm.art_id}
              onChange={(e) => setPiForm({ ...piForm, art_id: e.target.value })}
              className="w-full rounded-md border border-bark-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-moss-500"
            >
              <option value="">Select ART…</option>
              {arts.map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
            {arts.length === 0 && (
              <p className="mt-1 text-xs text-bark-400">
                No ARTs found.{' '}
                <a href="/art-setup" className="underline hover:text-bark-300">
                  Create one in ART Setup.
                </a>
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="pi-start" className="mb-1 block text-sm font-medium text-bark-700">
                Start Date<span aria-hidden="true"> *</span>
              </label>
              <input
                id="pi-start"
                type="date"
                value={piForm.start_date}
                onChange={(e) => setPiForm({ ...piForm, start_date: e.target.value })}
                className="w-full rounded-md border border-bark-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-moss-500"
              />
            </div>
            <div>
              <label htmlFor="pi-end" className="mb-1 block text-sm font-medium text-bark-700">
                End Date<span aria-hidden="true"> *</span>
              </label>
              <input
                id="pi-end"
                type="date"
                value={piForm.end_date}
                onChange={(e) => setPiForm({ ...piForm, end_date: e.target.value })}
                className="w-full rounded-md border border-bark-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-moss-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setPiModalOpen(false)}
              className="rounded-md px-4 py-2 text-sm text-bark-600 hover:bg-bark-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createPIMut.isPending}
              className="rounded-md bg-moss-600 px-4 py-2 text-sm font-medium text-white hover:bg-moss-700 disabled:opacity-50 transition-colors"
            >
              {createPIMut.isPending ? 'Creating…' : 'Create PI'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
