import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { expect, type Page } from '@playwright/test';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixtureDb = path.resolve(__dirname, '../../tests/e2e_fixture.db.json');
const cleanFixture = path.resolve(__dirname, '../../tests/e2e_fixture.clean.json');

export function resetDb(): void {
  fs.copyFileSync(cleanFixture, fixtureDb);
}

export async function selectPI(page: Page, name = 'PI 2026.1') {
  await page.goto('/');
  await expect(page.getByRole('combobox')).toBeVisible();
  await page.getByRole('combobox').selectOption({ label: name });
  await page.waitForURL(/\/pi\/.+\/board/);
}

export async function goToPage(page: Page, label: 'Board' | 'Backlog' | 'Risks' | 'Dependencies' | 'PI Setup') {
  await page.getByRole('link', { name: label }).click();
  const slug = label.split(' ').pop()!.toLowerCase();
  await page.waitForURL(new RegExp(`/${slug}`));
}
