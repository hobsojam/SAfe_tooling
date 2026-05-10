import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Backlog } from './pages/Backlog';
import { Board } from './pages/Board';
import { Capacity } from './pages/Capacity';
import { Dependencies } from './pages/Dependencies';
import { Objectives } from './pages/Objectives';
import { Risks } from './pages/Risks';
import { ARTSetup } from './pages/ARTSetup';
import { Predictability } from './pages/Predictability';
import { Setup } from './pages/Setup';
import { TeamSetup } from './pages/TeamSetup';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/pi" replace />} />
          <Route path="pi" element={null} />
          <Route path="pi/:piId/board" element={<Board />} />
          <Route path="pi/:piId/backlog" element={<Backlog />} />
          <Route path="pi/:piId/objectives" element={<Objectives />} />
          <Route path="pi/:piId/predictability" element={<Predictability />} />
          <Route path="pi/:piId/capacity" element={<Capacity />} />
          <Route path="pi/:piId/risks" element={<Risks />} />
          <Route path="pi/:piId/dependencies" element={<Dependencies />} />
          <Route path="pi/:piId/setup" element={<Setup />} />
          <Route path="pi/:piId/team-setup" element={<TeamSetup />} />
          <Route path="art-setup" element={<ARTSetup />} />
        </Route>
      </Routes>
    </Router>
  );
}
