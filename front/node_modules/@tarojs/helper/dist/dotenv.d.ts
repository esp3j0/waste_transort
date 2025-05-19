import type { IProjectConfig } from '@tarojs/taro/types/compile';
export declare const formatPrefix: (prefixs?: string | string[]) => string[];
export declare const dotenvParse: (root: string, prefixs?: string | string[], mode?: string) => Record<string, string>;
export declare const patchEnv: (config: IProjectConfig, expandEnv: Record<string, string>) => {};
