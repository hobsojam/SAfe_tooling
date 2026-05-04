import { expect, test } from '@playwright/test';
import { selectPI } from './helpers';

test.beforeEach(async ({ page }) => {
  await selectPI(page);
});

test('shows program board heading with PI name', async ({ page }) => {
  await expect(page.getByRole('heading', { name: /Program Board — PI 2026\.1/ })).toBeVisible();
});

test('shows iteration column headers', async ({ page }) => {
  await expect(page.getByRole('columnheader', { name: 'I1' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'I2' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'I3' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'I4' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: /I5.*IP/ })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Unplanned' })).toBeVisible();
});

test('shows both team names in the board rows', async ({ page }) => {
  // All ART teams appear as rows, regardless of whether they have assigned features
  await expect(page.getByText('Alpha', { exact: true })).toBeVisible();
  await expect(page.getByText('Beta', { exact: true })).toBeVisible();
});

test('shows all four features', async ({ page }) => {
  // Use exact:true to avoid matching "Auth service token…" in the dependency description
  await expect(page.getByText('Auth Service', { exact: true })).toBeVisible();
  await expect(page.getByText('SSO Integration', { exact: true })).toBeVisible();
  await expect(page.getByText('Observability Dashboard', { exact: true })).toBeVisible();
  await expect(page.getByText('CI/CD Pipeline Upgrade', { exact: true })).toBeVisible();
});

test('Auth Service placed in Iteration 1 column', async ({ page }) => {
  // Alpha row — I1 cell should contain Auth Service
  const i1Header = page.getByRole('columnheader', { name: 'I1' });
  const i1Index = await i1Header.evaluate((el) =>
    Array.from(el.parentElement!.children).indexOf(el),
  );
  const alphaRow = page.locator('tbody tr').filter({ hasText: 'Alpha' });
  const i1Cell = alphaRow.locator('td').nth(i1Index);
  await expect(i1Cell.getByText('Auth Service')).toBeVisible();
});

test('dependencies table shown below the board', async ({ page }) => {
  await expect(page.getByRole('heading', { name: /Dependencies/ })).toBeVisible();
  await expect(page.getByText('Auth API contract')).toBeVisible();
});

test('cross-team dependency shown as red arrow on the board grid', async ({ page }) => {
  // The fixture has exactly 1 cross-team dependency (Observability Dashboard → Auth Service)
  // and 2 same-team dependencies; only the cross-team one should produce an SVG arrow.
  await expect(page.locator('[data-dep-id]')).toHaveCount(1);
});

test('same-team dependencies do not produce board arrows', async ({ page }) => {
  // Total deps = 3, cross-team = 1, so same-team = 2 produce no arrows
  const arrows = page.locator('[data-dep-id]');
  await expect(arrows).toHaveCount(1);
  // Confirm the two same-team dep descriptions are visible in the table but not as arrows
  await expect(page.getByText('Auth API contract', { exact: false })).toBeVisible();
  await expect(page.getByText('Observability metrics endpoint', { exact: false })).toBeVisible();
});
