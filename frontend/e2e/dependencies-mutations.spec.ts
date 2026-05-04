import { expect, test } from '@playwright/test';
import { goToPage, resetDb, selectPI } from './helpers';

test.beforeEach(async ({ page }) => {
  resetDb();
  await selectPI(page);
  await goToPage(page, 'Dependencies');
});

test('New Dependency button opens modal', async ({ page }) => {
  await page.getByRole('button', { name: '+ New Dependency' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'New Dependency' })).toBeVisible();
});

test('modal closes on Cancel', async ({ page }) => {
  await page.getByRole('button', { name: '+ New Dependency' }).click();
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
});

test('create form requires description', async ({ page }) => {
  await page.getByRole('button', { name: '+ New Dependency' }).click();
  await page.getByLabel('From Team').selectOption({ value: '' });
  await page.getByRole('button', { name: 'Add Dependency' }).click();
  await expect(page.getByText('Description is required.')).toBeVisible();
});

test('create form requires from and to teams', async ({ page }) => {
  await page.getByRole('button', { name: '+ New Dependency' }).click();
  await page.getByLabel('Description').fill('A dependency');
  await page.getByLabel('From Team').selectOption({ value: '' });
  await page.getByRole('button', { name: 'Add Dependency' }).click();
  await expect(page.getByText('From and To teams are required.')).toBeVisible();
});

test('can create a new dependency', async ({ page }) => {
  await page.getByRole('button', { name: '+ New Dependency' }).click();
  await page.getByLabel('Description').fill('Payment gateway API needed by checkout');
  await page.getByLabel('From Team').selectOption({ label: 'Alpha' });
  await page.getByLabel('To Team').selectOption({ label: 'Beta' });
  await page.getByLabel('Owner').fill('Eve');
  await page.getByRole('button', { name: 'Add Dependency' }).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
  await expect(page.getByText('Payment gateway API needed by checkout')).toBeVisible();
  await expect(page.getByRole('cell', { name: 'Eve' })).toBeVisible();
});

test('Edit button opens modal pre-filled and teams are disabled', async ({ page }) => {
  const row = page.getByRole('row', { name: /Observability metrics endpoint/ });
  await row.getByRole('button', { name: 'Edit' }).click();
  await expect(page.getByRole('heading', { name: 'Edit Dependency' })).toBeVisible();
  await expect(page.getByLabel('Description')).toHaveValue(
    'Observability metrics endpoint needed by CI/CD pipeline health checks',
  );
  await expect(page.getByLabel('From Team')).toBeDisabled();
  await expect(page.getByLabel('To Team')).toBeDisabled();
});

test('can edit dependency status', async ({ page }) => {
  const row = page.getByRole('row', { name: /Observability metrics endpoint/ });
  await row.getByRole('button', { name: 'Edit' }).click();
  await page.getByLabel('Status').selectOption('resolved');
  await page.getByRole('button', { name: 'Save Changes' }).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
  await expect(row.getByText('resolved')).toBeVisible();
});

test('can delete a newly created dependency', async ({ page }) => {
  await page.getByRole('button', { name: '+ New Dependency' }).click();
  await page.getByLabel('Description').fill('TEMP: to be deleted');
  await page.getByRole('button', { name: 'Add Dependency' }).click();
  await expect(page.getByText('TEMP: to be deleted')).toBeVisible();

  const row = page.getByRole('row', { name: /TEMP: to be deleted/ });
  page.once('dialog', (d) => d.accept());
  await row.getByRole('button', { name: 'Delete' }).click();
  await expect(page.getByText('TEMP: to be deleted')).not.toBeVisible();
});
