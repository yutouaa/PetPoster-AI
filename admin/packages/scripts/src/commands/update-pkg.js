import { execCommand } from '../shared';
export async function updatePkg(args = ['--deep', '-u']) {
    execCommand('npx', ['ncu', ...args], { stdio: 'inherit' });
}
