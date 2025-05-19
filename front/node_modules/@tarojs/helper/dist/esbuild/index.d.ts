import { Config } from '@swc/core';
import esbuild from 'esbuild';
import type { Loader } from 'esbuild';
export declare const defaultEsbuildLoader: Record<string, Loader>;
export interface IRequireWithEsbuildOptions {
    customConfig?: Parameters<typeof esbuild.build>[0];
    customSwcConfig?: Config;
    cwd?: string;
}
/** 基于 esbuild 的 require 实现 */
export declare function requireWithEsbuild(id: string, { customConfig, customSwcConfig, cwd }?: IRequireWithEsbuildOptions): any;
export { esbuild };
export * from './utils';
