import express, { Request, Response } from 'express';
import cors from 'cors';
import { Pool } from 'pg';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  port: parseInt(process.env.PGPORT || '5432', 10),
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'postgres',
  database: process.env.PGDATABASE || 'disaster_relief',
});

const queriesDir = path.resolve(__dirname, '../../db/queries');
const docsDir = path.resolve(__dirname, '../../docs');
const projectRoot = path.resolve(__dirname, '../..');

// Helper to extract query title and concepts from SQL file header
function parseQueryHeader(content: string) {
  const titleMatch = content.match(/-- Problem Statement:\s*(.+)/);
  const conceptsMatch = content.match(/-- Concepts Tested:\s*(.+)/);
  const columnsMatch = content.match(/-- Expected Output Columns:\s*(.+)/);

  return {
    title: titleMatch ? titleMatch[1].trim() : 'Query',
    concepts: conceptsMatch ? conceptsMatch[1].trim() : '',
    expectedColumns: columnsMatch ? columnsMatch[1].trim() : '',
  };
}

// 1. List all queries Q01-Q20 with live file contents
app.get('/api/queries', (req: Request, res: Response) => {
  try {
    const files = fs.readdirSync(queriesDir).filter(f => f.endsWith('.sql')).sort();
    const queries = files.map(filename => {
      const id = filename.replace('.sql', '');
      const filePath = path.join(queriesDir, filename);
      const sqlContent = fs.readFileSync(filePath, 'utf-8');
      const meta = parseQueryHeader(sqlContent);
      const isStub = sqlContent.includes("'TODO' AS not_attempted");

      return {
        id,
        filename,
        title: meta.title,
        concepts: meta.concepts,
        expectedColumns: meta.expectedColumns,
        sql: sqlContent,
        isStub,
      };
    });
    res.json(queries);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 2. Run query directly reading from disk at request time
app.post('/api/queries/:id/run', async (req: Request, res: Response) => {
  const { id } = req.params;
  const filePath = path.join(queriesDir, `${id}.sql`);

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: `Query file ${id}.sql not found` });
  }

  const sqlContent = fs.readFileSync(filePath, 'utf-8');

  // Strip comment lines for execution
  const executableSql = sqlContent
    .split('\n')
    .filter(line => !line.trim().startsWith('--'))
    .join('\n')
    .trim();

  if (!executableSql) {
    return res.status(400).json({ error: 'SQL file contains no executable statements' });
  }

  const startTime = process.hrtime();
  try {
    const result = await pool.query(executableSql);
    const diff = process.hrtime(startTime);
    const executionTimeMs = (diff[0] * 1000 + diff[1] / 1e6).toFixed(2);

    const fields = result.fields ? result.fields.map(f => f.name) : [];
    res.json({
      id,
      success: true,
      fields,
      rows: result.rows,
      rowCount: result.rowCount,
      executionTimeMs: parseFloat(executionTimeMs),
    });
  } catch (err: any) {
    const diff = process.hrtime(startTime);
    const executionTimeMs = (diff[0] * 1000 + diff[1] / 1e6).toFixed(2);
    res.status(400).json({
      id,
      success: false,
      error: err.message,
      executionTimeMs: parseFloat(executionTimeMs),
    });
  }
});

// 3. Get test statuses from test runner
app.get('/api/tests/status', async (req: Request, res: Response) => {
  try {
    const { stdout } = await execAsync('python3 tests/runner.py', { cwd: projectRoot });
    // Parse test output
    const lines = stdout.split('\n');
    const statuses: Record<string, string> = {};
    for (const line of lines) {
      const match = line.match(/^(Q\d+)\s*\|\s*(\x1b\[[0-9;]*m)?(PASS|FAIL|NOT ATTEMPTED)/);
      if (match) {
        statuses[match[1]] = match[3];
      }
    }
    res.json({ success: true, statuses, rawOutput: stdout });
  } catch (err: any) {
    // python runner exits with 1 if there's any failure, stdout still contains table
    const stdout = err.stdout || '';
    const lines = stdout.split('\n');
    const statuses: Record<string, string> = {};
    for (const line of lines) {
      const match = line.match(/^(Q\d+)\s*\|\s*(\x1b\[[0-9;]*m)?(PASS|FAIL|NOT ATTEMPTED)/);
      if (match) {
        statuses[match[1]] = match[3];
      }
    }
    res.json({ success: true, statuses, rawOutput: stdout });
  }
});

// 4. Serve ER diagram markdown
app.get('/api/docs/er-diagram', (req: Request, res: Response) => {
  try {
    const filePath = path.join(docsDir, 'er-diagram.md');
    const content = fs.readFileSync(filePath, 'utf-8');
    res.json({ content });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 5. Serve compiled React frontend
const clientDist = path.resolve(__dirname, '../client/dist');
if (fs.existsSync(clientDist)) {
  app.use(express.static(clientDist));
  app.get('*', (req: Request, res: Response) => {
    res.sendFile(path.join(clientDist, 'index.html'));
  });
}

app.listen(port, () => {
  console.log(`SQL Lab server ready on http://localhost:${port}`);
});
