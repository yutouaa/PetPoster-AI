import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import progress from 'vite-plugin-progress';
import { setupElegantRouter } from './router';
import { setupUnocss } from './unocss';
import { setupUnplugin } from './unplugin';
import { setupHtmlPlugin } from './html';
import { setupDevtoolsPlugin } from './devtools';
export function setupVitePlugins(viteEnv, buildTime) {
    const plugins = [
        vue(),
        vueJsx(),
        setupDevtoolsPlugin(viteEnv),
        setupElegantRouter(),
        setupUnocss(viteEnv),
        ...setupUnplugin(viteEnv),
        progress(),
        setupHtmlPlugin(buildTime)
    ];
    return plugins;
}
