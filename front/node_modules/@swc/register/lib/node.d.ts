import * as swc from "@swc/core";
export interface InputOptions extends TransformOptions {
    extensions?: string[];
}
/**
 * Babel has built-in ignore & only support while @swc/core doesn't. So let's make our own!
 */
export interface TransformOptions extends swc.Options {
    only?: FilePattern;
    ignore?: FilePattern;
}
export declare type FilePattern = ReadonlyArray<string | ((filename: string, { dirname }: {
    dirname: string;
}) => any) | RegExp>;
export declare function revert(): void;
export default function register(opts?: InputOptions): void;
