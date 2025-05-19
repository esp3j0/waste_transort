import type { parse, PluginItem } from '@babel/core';
/**
 * Inject `defineAppConfig` and `definePageConfig`
 * require header at the top of a config file,
 * without the need to specifically require them
 * if they are used
*/
export declare function injectDefineConfigHeader(babel: {
    parse: typeof parse;
}): PluginItem;
