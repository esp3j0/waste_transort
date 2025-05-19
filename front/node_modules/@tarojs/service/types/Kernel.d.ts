/// <reference types="node" />
import { EventEmitter } from 'node:events';
import Plugin from './Plugin';
import type { Func, IProjectConfig, PluginItem } from '@tarojs/taro/types/compile';
import type Config from './Config';
import type { ICommand, IHook, IPaths, IPlatform, IPlugin, IPluginsObject, IPreset } from './utils/types';
interface IKernelOptions {
    appPath: string;
    config: Config;
    presets?: PluginItem[];
    plugins?: PluginItem[];
}
export default class Kernel extends EventEmitter {
    appPath: string;
    isWatch: boolean;
    isProduction: boolean;
    optsPresets: PluginItem[] | void;
    optsPlugins: PluginItem[] | void;
    plugins: Map<string, IPlugin>;
    paths: IPaths;
    extraPlugins: IPluginsObject;
    globalExtraPlugins: IPluginsObject;
    config: Config;
    initialConfig: IProjectConfig;
    initialGlobalConfig: IProjectConfig;
    hooks: Map<string, IHook[]>;
    methods: Map<string, Func[]>;
    cliCommands: string[];
    cliCommandsPath: string;
    commands: Map<string, ICommand>;
    platforms: Map<string, IPlatform>;
    helper: any;
    runnerUtils: any;
    runOpts: any;
    debugger: any;
    constructor(options: IKernelOptions);
    initConfig(): void;
    initPaths(): void;
    initHelper(): void;
    initRunnerUtils(): void;
    initPresetsAndPlugins(): void;
    resolvePresets(cliAndProjectPresets: IPluginsObject, globalPresets: IPluginsObject): void;
    resolvePlugins(cliAndProjectPlugins: IPluginsObject, globalPlugins: IPluginsObject): void;
    initPreset(preset: IPreset, isGlobalConfigPreset?: boolean): void;
    initPlugin(plugin: IPlugin): void;
    applyCliCommandPlugin(commandNames?: string[]): void;
    checkPluginOpts(pluginCtx: any, opts: any): void;
    registerPlugin(plugin: IPlugin): void;
    initPluginCtx({ id, path, ctx }: {
        id: string;
        path: string;
        ctx: Kernel;
    }): Plugin;
    applyPlugins(args: string | {
        name: string;
        initialVal?: any;
        opts?: any;
    }): Promise<any>;
    runWithPlatform(platform: any): any;
    setRunOpts(opts: any): void;
    runHelp(name: string): void;
    run(args: string | {
        name: string;
        opts?: any;
    }): Promise<void>;
}
export {};
