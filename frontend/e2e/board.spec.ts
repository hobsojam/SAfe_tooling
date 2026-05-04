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
  // Use the team-name span inside tbody (not getByRole('cell') — ARIA role not resolved here)
  await expect(page.locator('tbody td span').filter({ hasText: /^Alpha$/ })).toBeVisible();
  await expect(page.locator('tbody td span').filter({ hasText: /^Beta$/ })).toBeVisible();
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
