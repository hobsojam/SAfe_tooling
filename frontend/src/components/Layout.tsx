import { useQuery } from '@tanstack/react-query';
import { NavLink, Outlet, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import { PIStatusBadge } from './Badge';

const NAV = [
  { to: 'board', label: 'Board' },
  { to: 'backlog', label: 'Backlog' },
  { to: 'risks', label: 'Risks' },
  { to: 'dependencies', label: 'Dependencies' },
];

export function Layout() {
  const { piId } = useParams<{ piId: string }>();
  const navigate = useNavigate();

  const { data: pis = [] } = useQuery({
    queryKey: ['pis'],
    queryFn: api.listPIs,
  });

  const activePi = pis.find((p) => p.id === piId);

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
          <label className="mb-1 block text-xs text-slate-400">Program Increment</label>
          <select
            value={piId ?? ''}
            onChange={(e) => {
              if (e.target.value) navigate(`/pi/${e.target.value}/board`);
            }}
            className="w-full rounded bg-slate-700 px-2 py-1.5 text-sm text-slate-100 focus:outline-none"
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
    </div>
  );
}
