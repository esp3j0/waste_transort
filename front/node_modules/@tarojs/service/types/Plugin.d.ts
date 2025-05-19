import type { Func } from '@tarojs/taro/types/compile';
import type Kernel from './Kernel';
import type { ICommand, IHook, IPlatform } from './utils/types';
export default class Plugin {
    id: string;
    path: string;
    ctx: Kernel;
    optsSchema: Func;
    constructor(opts: any);
    register(hook: IHook): void;
    registerCommand(command: ICommand): void;
    registerPlatform(platform: IPlatform): void;
    registerMethod(...args: any[]): void;
    addPluginOptsSchema(schema: any): void;
}
