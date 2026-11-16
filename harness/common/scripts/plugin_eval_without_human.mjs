// Filter the installed analyzer in this process only; keep its files intact.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const lstat = fs.lstat.bind(fs);
const readdir = fs.readdir.bind(fs);
async function ordinaryPath(file) {
  const filename = file instanceof URL ? fileURLToPath(file) : String(file);
  const absolute = path.isAbsolute(filename) ? filename : `${process.cwd()}/${filename}`;
  let component = path.parse(absolute).root;
  // Keep '..' until its preceding component has been checked.
  for (const part of absolute.slice(component.length).split(path.sep)) {
    component = path.join(component, part);
    try {
      if ((await lstat(component)).isSymbolicLink()) throw new Error(`Symlink forbidden: ${component}`);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
  }
  return absolute;
}

async function ordinaryTree(directory) {
  await ordinaryPath(directory);
  let info;
  try { info = await lstat(directory); } catch (error) {
    if (error.code === 'ENOENT') return;
    throw error;
  }
  if (!info.isDirectory()) return;
  const pending = [directory];
  while (pending.length) {
    const current = pending.pop();
    await ordinaryPath(current);
    for (const entry of await readdir(current, {withFileTypes: true})) {
      const child = path.join(current, entry.name);
      if (entry.isSymbolicLink()) throw new Error(`Symlink forbidden: ${child}`);
      if (entry.isDirectory()) pending.push(child);
    }
  }
}

await ordinaryPath(process.argv[1]);
const script = fileURLToPath(import.meta.url);
await ordinaryPath(script);
await ordinaryTree(path.join(path.dirname(script), '../../..', 'harness'));

const [entrypoint, ...args] = process.argv.slice(2);
if (!entrypoint) throw new Error('Usage: node plugin_eval_without_human.mjs <installed CLI.js> <command> <target> [options]');

fs.readdir = async (directory, ...args) => {
  await ordinaryTree(directory);
  return (await readdir(directory, ...args)).filter(entry => String(entry.name ?? entry) !== 'README.human.md');
};

const readFile = fs.readFile.bind(fs);
fs.readFile = async (file, ...args) => {
  const filename = await ordinaryPath(file);
  if (path.basename(filename) === 'README.human.md') {
    throw new Error('Reading README.human.md is forbidden; remove the human guide from the analysis inputs.');
  }
  return readFile(file, ...args);
};
for (const method of ['stat', 'access', 'realpath', 'readlink']) {
  const original = fs[method].bind(fs);
  fs[method] = async (file, ...args) => {
    await ordinaryPath(file);
    return original(file, ...args);
  };
}
const open = fs.open.bind(fs);
fs.open = async (file, flags = 'r', ...args) => {
  await ordinaryPath(file);
  if (flags !== 'r') throw new Error('This plugin-eval process only opens files for reading.');
  return open(file, flags, ...args);
};

// Analysis reports go to stdout. Reject commands/options that mutate files.
for (const method of ['writeFile', 'appendFile', 'mkdir', 'rm', 'unlink', 'rename', 'copyFile', 'cp', 'symlink', 'link']) {
  fs[method] = async () => { throw new Error('This plugin-eval process is read-only; redirect stdout for reports.'); };
}
if (args.includes('--metric-pack') || ['benchmark', 'init-benchmark'].includes(args[0])) {
  throw new Error('Metric-pack subprocesses and benchmarks require a separate workflow; this launcher filters in-process analysis only.');
}

// Check raw CLI paths before the analyzer can normalize or swallow guard errors.
const textOptions = new Set(['--format', '--request', '--goal', '--model']);
const pathOptions = new Set(['--observed-usage', '--output', '--brief-out', '--config', '--usage-out', '--result-out']);
for (let index = 1; index < args.length; index++) {
  const argument = args[index];
  if (textOptions.has(argument)) index++;
  else if (pathOptions.has(argument)) await ordinaryPath(args[++index]);
  else if (!['--dry-run', '--help', '-h'].includes(argument)) await ordinaryTree(argument);
}

const cli = await ordinaryPath(entrypoint);
process.argv = [process.execPath, cli, ...args];
await import(pathToFileURL(cli).href);
