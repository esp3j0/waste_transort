import type { OnResolveArgs, OnResolveResult } from 'esbuild';
export declare function externalEsbuildModule({ path, namespace, importer, pluginData }: Partial<OnResolveArgs>): OnResolveResult;
