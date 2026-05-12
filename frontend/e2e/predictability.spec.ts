import { expect, test } from '@playwright/test';
import { goToPage, resetDb, selectPI } from './helpers';

// Fixture objectives:
//   Alpha (committed): planned=10, actual=10  → 100%
//   Beta  (committed): planned=10, actual=8   → 80%
//   Alpha (stretch):   planned=5,  actual=null → excluded
// ART total: actual=18, planned=20 → 90%

test.beforeEach(async ({ page }) => {
  await resetDb();
  await selectPI(page);
  await goToPage(page, 'Predictability');
});

test('shows ART Predictability heading with PI name', async ({ page }) => {
  await expect(
    page.getByRole('heading', { name: /ART Predictability — PI 2026\.1/ }),
  ).toBeVisible();
});

test('shows explanatory subtitle', async ({ page }) => {
  await expect(page.getByText(/Committed objectives only/)).toBeVisible();
});

test('shows correct column headers', async ({ page }) => {
  for (const col of ['Team', 'Objectives', 'Planned BV', 'Actual BV', 'Predictability']) {
    await expect(page.getByRole('columnheader', { name: col })).toBeVisible();
  }
});

test('shows both ART team rows', async ({ page }) => {
  await expect(page.getByRole('cell', { name: 'Alpha' })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'Beta' })).toBeVisible();
});

test('Alpha team shows 100% predictability badge', async ({ page }) => {
  const alphaRow = page.getByRole('row', { name: /Alpha/ });
  await expect(alphaRow.getByText('100%')).toBeVisible();
});

test('Beta team shows 80% predictability badge', async ({ page }) => {
  const betaRow = page.getByRole('row', { name: /Beta/ });
  await expect(betaRow.getByText('80%')).toBeVisible();
});

test('ART Total row shows 90% predictability', async ({ page }) => {
  // Alpha: 10/10=100%, Beta: 8/10=80% → ART: 18/20=90%
  await expect(page.locator('tfoot').getByText('90%')).toBeVisible();
});

test('ART Total counts only committed objectives (stretch excluded)', async ({ page }) => {
  // 2 committed objectives in the fixture (Alpha + Beta), 1 stretch is excluded
  const footer = page.locator('tfoot');
  await expect(footer.getByRole('cell', { name: '2', exact: true })).toBeVisible();
});

test('Alpha planned BV is 10', async ({ page }) => {
  const alphaRow = page.getByRole('row', { name: /Alpha/ });
  await expect(alphaRow.getByRole('cell', { name: '10', exact: true }).first()).toBeVisible();
});

test('Predictability nav link appears in sidebar after selecting a PI', async ({ page }) => {
  await expect(page.getByRole('link', { name: 'Predictability' })).toBeVisible();
});

test('shows footnote explaining the formula', async ({ page }) => {
  await expect(page.getByText(/Predictability = Actual BV ÷ Planned BV × 100/)).toBeVisible();
  await expect(page.getByText(/Stretch objectives are excluded/)).toBeVisible();
});
