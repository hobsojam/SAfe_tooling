import { expect, test } from '@playwright/test';
import { goToPage, resetDb, selectPI } from './helpers';

test.beforeEach(async ({ page }) => {
  resetDb();
  await selectPI(page);
  await goToPage(page, 'Capacity');
});

test('shows Capacity heading', async ({ page }) => {
  await expect(page.getByRole('heading', { name: /Capacity/ })).toBeVisible();
});

test('shows iteration rows', async ({ page }) => {
  await expect(page.getByText('Iteration 1')).toBeVisible();
  await expect(page.getByText('Iteration 2')).toBeVisible();
});

test('shows team columns', async ({ page }) => {
  await expect(page.getByRole('columnheader', { name: 'Alpha' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Beta' })).toBeVisible();
});

test('unset cells show Not set', async ({ page }) => {
  const notSetButtons = page.getByRole('button', { name: 'Not set' });
  await expect(notSetButtons.first()).toBeVisible();
});

test('clicking a cell opens the capacity modal', async ({ page }) => {
  await page.getByRole('button', { name: 'Not set' }).first().click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('heading', { name: /Capacity:/ })).toBeVisible();
});

test('modal closes on Cancel', async ({ page }) => {
  await page.getByRole('button', { name: 'Not set' }).first().click();
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
});

test('can set capacity for a cell', async ({ page }) => {
  await page.getByRole('button', { name: 'Not set' }).first().click();
  await page.getByLabel('Team Size').fill('6');
  await page.getByLabel('Iteration Days').fill('10');
  await page.getByLabel('PTO Days').fill('0');
  await page.getByLabel('Overhead %').fill('20');
  await page.getByRole('button', { name: 'Set Capacity' }).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
  // 6 * 10 * 0.8 = 48
  await expect(page.getByText('48')).toBeVisible();
});

test('live preview shows computed capacity', async ({ page }) => {
  await page.getByRole('button', { name: 'Not set' }).first().click();
  await page.getByLabel('Team Size').fill('5');
  await page.getByLabel('Iteration Days').fill('10');
  await page.getByLabel('PTO Days').fill('0');
  await page.getByLabel('Overhead %').fill('20');
  // 5 * 10 * 0.8 = 40
  await expect(page.getByText('40')).toBeVisible();
});

test('can update an existing capacity plan', async ({ page }) => {
  await page.getByRole('button', { name: 'Not set' }).first().click();
  await page.getByLabel('Team Size').fill('6');
  await page.getByLabel('Iteration Days').fill('10');
  await page.getByLabel('PTO Days').fill('0');
  await page.getByLabel('Overhead %').fill('20');
  await page.getByRole('button', { name: 'Set Capacity' }).click();

  await page.getByText('48').click();
  await page.getByLabel('Team Size').fill('8');
  await page.getByRole('button', { name: 'Set Capacity' }).click();
  // 8 * 10 * 0.8 = 64
  await expect(page.getByText('64')).toBeVisible();
  await expect(page.getByText('48')).not.toBeVisible();
});
