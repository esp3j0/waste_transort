import { PLATFORM_TYPE } from '@tarojs/shared';
import TaroPlatform from './platform';
import type { RecursiveTemplate, UnRecursiveTemplate } from '@tarojs/shared/dist/template';
import type { TConfig } from '../utils/types';
interface IFileType {
    templ: string;
    style: string;
    config: string;
    script: string;
    xs?: string;
}
export declare abstract class TaroPlatformBase<T extends TConfig = TConfig> extends TaroPlatform<T> {
    platformType: PLATFORM_TYPE;
    abstract globalObject: string;
    abstract fileType: IFileType;
    abstract template: RecursiveTemplate | UnRecursiveTemplate;
    taroComponentsPath: string;
    projectConfigJson?: string;
    private projectConfigJsonOutputPath;
    /**
     * 1. 清空 dist 文件夹
     * 2. 输出编译提示
     * 3. 生成 project.config.json
     */
    private setup;
    private setupImpl;
    protected printDevelopmentTip(platform: string): void;
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
    private buildImpl;
    /**
     * 生成 project.config.json
     * @param src 项目源码中配置文件的名称
     * @param dist 编译后配置文件的名称，默认为 'project.config.json'
     */
    protected generateProjectConfig(src: string, dist?: string): void;
    /**
     * 递归替换对象的 key 值
     */
    protected recursiveReplaceObjectKeys(obj: any, keyMap: any): void;
    /**
     * 调用 runner 开启编译
     */
    start(): Promise<void>;
}
export {};
