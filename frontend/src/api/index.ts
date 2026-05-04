import type { Dependency, Feature, Iteration, PI, Risk, Story, Team } from '../types';

const BASE = '/api';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  listPIs: () => get<PI[]>('/pi'),
  getPI: (id: string) => get<PI>(`/pi/${id}`),

  listTeams: () => get<Team[]>('/team'),

  listIterations: (piId: string) => get<Iteration[]>(`/iterations?pi_id=${piId}`),

  listFeatures: (piId: string) => get<Feature[]>(`/features?pi_id=${piId}`),

  listStories: () => get<Story[]>('/stories'),

  listRisks: (piId: string) => get<Risk[]>(`/risks?pi_id=${piId}`),

  listDependencies: (piId: string) => get<Dependency[]>(`/dependencies?pi_id=${piId}`),
};
