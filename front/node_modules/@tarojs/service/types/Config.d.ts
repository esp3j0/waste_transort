import type { IProjectConfig } from '@tarojs/taro/types/compile';
interface IConfigOptions {
    appPath: string;
    disableGlobalConfig?: boolean;
}
export default class Config {
    appPath: string;
    configPath: string;
    initialConfig: IProjectConfig;
    initialGlobalConfig: IProjectConfig;
    isInitSuccess: boolean;
    disableGlobalConfig: boolean;
    constructor(opts: IConfigOptions);
    init(configEnv: {
        mode: string;
        command: string;
    }): Promise<void>;
    initGlobalConfig(command?: string): void;
    getConfigWithNamed(platform: any, configName: any): any;
}
export {};
