import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixtureDb = path.resolve(__dirname, '../../tests/e2e_fixture.db.json');
const cleanFixture = path.resolve(__dirname, '../../tests/e2e_fixture.clean.json');

export default function globalSetup(): void {
  fs.copyFileSync(cleanFixture, fixtureDb);
}
