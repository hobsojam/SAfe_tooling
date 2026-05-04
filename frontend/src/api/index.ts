import type {
  ART,
  Dependency,
  DependencyCreate,
  DependencyUpdate,
  Feature,
  FeatureCreate,
  FeatureUpdate,
  Iteration,
  PI,
  PICreate,
  Risk,
  RiskCreate,
  RiskUpdate,
  Story,
  Team,
} from '../types';

const BASE = '/api';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function patch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
}

export const api = {
  listPIs: () => get<PI[]>('/pi'),
  getPI: (id: string) => get<PI>(`/pi/${id}`),
  createPI: (body: PICreate) => post<PI>('/pi', body),
  deletePI: (id: string) => del(`/pi/${id}`),

  listARTs: () => get<ART[]>('/art'),

  listTeams: () => get<Team[]>('/team'),

  listIterations: (piId: string) => get<Iteration[]>(`/iterations?pi_id=${piId}`),

  listFeatures: (piId: string) => get<Feature[]>(`/features?pi_id=${piId}`),
  createFeature: (body: FeatureCreate) => post<Feature>('/features', body),
  updateFeature: (id: string, body: FeatureUpdate) => patch<Feature>(`/features/${id}`, body),
  deleteFeature: (id: string) => del(`/features/${id}`),

  listStories: () => get<Story[]>('/stories'),

  listRisks: (piId: string) => get<Risk[]>(`/risks?pi_id=${piId}`),
  createRisk: (body: RiskCreate) => post<Risk>('/risks', body),
  updateRisk: (id: string, body: RiskUpdate) => patch<Risk>(`/risks/${id}`, body),
  deleteRisk: (id: string) => del(`/risks/${id}`),

  listDependencies: (piId: string) => get<Dependency[]>(`/dependencies?pi_id=${piId}`),
  createDependency: (body: DependencyCreate) => post<Dependency>('/dependencies', body),
  updateDependency: (id: string, body: DependencyUpdate) => patch<Dependency>(`/dependencies/${id}`, body),
  deleteDependency: (id: string) => del(`/dependencies/${id}`),
};
