import { IPluginContext } from '@tarojs/service';
import { AppConfig } from '@tarojs/taro';
/**
 * 按需编译功能，只编译指定的页面或组件
 * @param appConfig
 * @param args
 */
export declare function extractCompileEntry(appConfig: AppConfig, args: {
    _: string[];
    [key: string]: any;
}, ctx: IPluginContext): void;
