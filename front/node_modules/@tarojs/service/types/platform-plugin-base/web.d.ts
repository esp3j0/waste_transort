import { PLATFORM_TYPE } from '@tarojs/shared';
import TaroPlatform from './platform';
import type { TConfig } from '../utils/types';
export declare abstract class TaroPlatformWeb<T extends TConfig = TConfig> extends TaroPlatform<T> {
    platformType: PLATFORM_TYPE;
    /**
     * 1. 清空 dist 文件夹
     * 2. 输出编译提示
     */
    private setup;
    private setupWebApp;
    protected printDevelopmentTip(): void;
    /**
     * 返回当前项目内的 runner 包
     */
    protected getRunner(): Promise<any>;
    /**
     * 准备 runner 参数
     * @param extraOptions 需要额外合入 Options 的配置项
     */
    protected getOptions(extraOptions?: {}): any;
    /**
     * 调用 runner 开始编译
     * @param extraOptions 需要额外传入 runner 的配置项
     */
    private build;
    private buildWebApp;
    /**
     * 调用 runner 开启编译
     */
    start(): Promise<void>;
}
