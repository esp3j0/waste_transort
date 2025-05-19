import Config from './Config';
import Kernel from './Kernel';
import { TaroPlatform, TaroPlatformBase, TaroPlatformWeb } from './platform-plugin-base';
export * from './utils/types';
export { Config, Kernel, TaroPlatform, TaroPlatformBase, TaroPlatformWeb };
declare const _default: {
    Config: typeof Config;
    Kernel: typeof Kernel;
    TaroPlatform: typeof TaroPlatform;
    TaroPlatformBase: typeof TaroPlatformBase;
    TaroPlatformWeb: typeof TaroPlatformWeb;
};
export default _default;
export type { IPluginContext } from './utils/types';
