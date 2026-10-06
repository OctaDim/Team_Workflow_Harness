// Filter the installed analyzer in this process only; keep its files intact.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const [entrypoint, ...args] = process.argv.slice(2);
if (!entrypoint) throw new Error('Usage: node plugin_eval_without_human.mjs <installed CLI.js> <command> <target> [options]');

const readdir = fs.readdir.bind(fs);
fs.readdir = async (...args) => (await readdir(...args)).filter(entry => String(entry.name ?? entry) !== 'README.human.md');

const readFile = fs.readFile.bind(fs);
fs.readFile = async (file, ...args) => {
  const filename = file instanceof URL ? fileURLToPath(file) : String(file);
  if (path.basename(filename) === 'README.human.md' || path.basename(await fs.realpath(filename)) === 'README.human.md') {
    throw new Error('Reading README.human.md is forbidden; remove the human guide from the analysis inputs.');
  }
  return readFile(file, ...args);
};

// Analysis reports go to stdout. Reject commands/options that mutate files.
for (const method of ['writeFile', 'appendFile', 'mkdir', 'rm', 'unlink', 'rename', 'copyFile']) {
  fs[method] = async () => { throw new Error('This plugin-eval process is read-only; redirect stdout for reports.'); };
}
if (args.includes('--metric-pack') || ['benchmark', 'init-benchmark'].includes(args[0])) {
  throw new Error('Metric-pack subprocesses and benchmarks require a separate workflow; this launcher filters in-process analysis only.');
}

const cli = await fs.realpath(entrypoint);
process.argv = [process.execPath, cli, ...args];
await import(pathToFileURL(cli).href);
