import { beforeEach, describe, expect, it, vi } from 'vitest';
import type {
  DependencyCreate,
  DependencyUpdate,
  FeatureCreate,
  FeatureUpdate,
  PICreate,
  RiskCreate,
  RiskUpdate,
} from '../../types';
import { api } from '../../api/index';

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

function resolveOk(data: unknown = null) {
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(data),
  });
}

function resolveError(status: number, statusText: string) {
  mockFetch.mockResolvedValue({ ok: false, status, statusText });
}

beforeEach(() => {
  mockFetch.mockReset();
});

// ---------------------------------------------------------------------------
// GET
// ---------------------------------------------------------------------------

describe('GET methods', () => {
  it('listPIs calls GET /api/pi', async () => {
    resolveOk([]);
    await api.listPIs();
    expect(mockFetch).toHaveBeenCalledWith('/api/pi');
  });

  it('getPI calls GET /api/pi/:id', async () => {
    resolveOk({});
    await api.getPI('abc');
    expect(mockFetch).toHaveBeenCalledWith('/api/pi/abc');
  });

  it('listARTs calls GET /api/art', async () => {
    resolveOk([]);
    await api.listARTs();
    expect(mockFetch).toHaveBeenCalledWith('/api/art');
  });

  it('listTeams calls GET /api/team', async () => {
    resolveOk([]);
    await api.listTeams();
    expect(mockFetch).toHaveBeenCalledWith('/api/team');
  });

  it('listIterations calls GET /api/iterations?pi_id=...', async () => {
    resolveOk([]);
    await api.listIterations('pi1');
    expect(mockFetch).toHaveBeenCalledWith('/api/iterations?pi_id=pi1');
  });

  it('listFeatures calls GET /api/features?pi_id=...', async () => {
    resolveOk([]);
    await api.listFeatures('pi1');
    expect(mockFetch).toHaveBeenCalledWith('/api/features?pi_id=pi1');
  });

  it('listStoriesByFeature calls GET /api/stories?feature_id=...', async () => {
    resolveOk([]);
    await api.listStoriesByFeature('feat1');
    expect(mockFetch).toHaveBeenCalledWith('/api/stories?feature_id=feat1');
  });

  it('listRisks calls GET /api/risks?pi_id=...', async () => {
    resolveOk([]);
    await api.listRisks('pi1');
    expect(mockFetch).toHaveBeenCalledWith('/api/risks?pi_id=pi1');
  });

  it('listDependencies calls GET /api/dependencies?pi_id=...', async () => {
    resolveOk([]);
    await api.listDependencies('pi1');
    expect(mockFetch).toHaveBeenCalledWith('/api/dependencies?pi_id=pi1');
  });
});

// ---------------------------------------------------------------------------
// POST
// ---------------------------------------------------------------------------

describe('POST methods', () => {
  function postOpts(body: unknown) {
    return {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    };
  }

  it('createPI calls POST /api/pi with body', async () => {
    resolveOk({});
    const body: PICreate = {
      name: 'PI 1',
      art_id: 'art1',
      start_date: '2026-01-01',
      end_date: '2026-03-27',
    };
    await api.createPI(body);
    expect(mockFetch).toHaveBeenCalledWith('/api/pi', postOpts(body));
  });

  it('createFeature calls POST /api/features with body', async () => {
    resolveOk({});
    const body: FeatureCreate = {
      name: 'Feature 1',
      user_business_value: 8,
      time_criticality: 5,
      risk_reduction_opportunity_enablement: 3,
      job_size: 4,
    };
    await api.createFeature(body);
    expect(mockFetch).toHaveBeenCalledWith('/api/features', postOpts(body));
  });

  it('createRisk calls POST /api/risks with body', async () => {
    resolveOk({});
    const body: RiskCreate = { description: 'Risk 1', pi_id: 'pi1' };
    await api.createRisk(body);
    expect(mockFetch).toHaveBeenCalledWith('/api/risks', postOpts(body));
  });

  it('createDependency calls POST /api/dependencies with body', async () => {
    resolveOk({});
    const body: DependencyCreate = {
      description: 'Dep 1',
      pi_id: 'pi1',
      from_feature_id: 'feature1',
      to_feature_id: 'feature2',
    };
    await api.createDependency(body);
    expect(mockFetch).toHaveBeenCalledWith('/api/dependencies', postOpts(body));
  });
});

// ---------------------------------------------------------------------------
// PATCH
// ---------------------------------------------------------------------------

describe('PATCH methods', () => {
  function patchOpts(body: unknown) {
    return {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    };
  }

  it('updateFeature calls PATCH /api/features/:id', async () => {
    resolveOk({});
    const body: FeatureUpdate = { name: 'Updated Feature' };
    await api.updateFeature('f1', body);
    expect(mockFetch).toHaveBeenCalledWith('/api/features/f1', patchOpts(body));
  });

  it('updateRisk calls PATCH /api/risks/:id', async () => {
    resolveOk({});
    const body: RiskUpdate = { roam_status: 'owned', owner: 'Alice' };
    await api.updateRisk('r1', body);
    expect(mockFetch).toHaveBeenCalledWith('/api/risks/r1', patchOpts(body));
  });

  it('updateDependency calls PATCH /api/dependencies/:id', async () => {
    resolveOk({});
    const body: DependencyUpdate = { status: 'in_progress' };
    await api.updateDependency('d1', body);
    expect(mockFetch).toHaveBeenCalledWith('/api/dependencies/d1', patchOpts(body));
  });
});

// ---------------------------------------------------------------------------
// DELETE
// ---------------------------------------------------------------------------

describe('DELETE methods', () => {
  const deleteOpts = { method: 'DELETE' };

  it('deletePI calls DELETE /api/pi/:id', async () => {
    mockFetch.mockResolvedValue({ ok: true });
    await api.deletePI('pi1');
    expect(mockFetch).toHaveBeenCalledWith('/api/pi/pi1', deleteOpts);
  });

  it('deleteFeature calls DELETE /api/features/:id', async () => {
    mockFetch.mockResolvedValue({ ok: true });
    await api.deleteFeature('f1');
    expect(mockFetch).toHaveBeenCalledWith('/api/features/f1', deleteOpts);
  });

  it('deleteRisk calls DELETE /api/risks/:id', async () => {
    mockFetch.mockResolvedValue({ ok: true });
    await api.deleteRisk('r1');
    expect(mockFetch).toHaveBeenCalledWith('/api/risks/r1', deleteOpts);
  });

  it('deleteDependency calls DELETE /api/dependencies/:id', async () => {
    mockFetch.mockResolvedValue({ ok: true });
    await api.deleteDependency('d1');
    expect(mockFetch).toHaveBeenCalledWith('/api/dependencies/d1', deleteOpts);
  });
});

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

describe('error handling', () => {
  it('throws on a non-ok GET response', async () => {
    resolveError(404, 'Not Found');
    await expect(api.listPIs()).rejects.toThrow('API 404: Not Found');
  });

  it('throws on a non-ok POST response', async () => {
    resolveError(422, 'Unprocessable Entity');
    const body: PICreate = {
      name: 'X',
      art_id: 'a',
      start_date: '2026-01-01',
      end_date: '2026-03-27',
    };
    await expect(api.createPI(body)).rejects.toThrow('API 422: Unprocessable Entity');
  });

  it('throws on a non-ok PATCH response', async () => {
    resolveError(409, 'Conflict');
    await expect(api.updateFeature('f1', { name: 'X' })).rejects.toThrow('API 409: Conflict');
  });

  it('throws on a non-ok DELETE response', async () => {
    resolveError(500, 'Internal Server Error');
    await expect(api.deletePI('x')).rejects.toThrow('API 500: Internal Server Error');
  });
});
