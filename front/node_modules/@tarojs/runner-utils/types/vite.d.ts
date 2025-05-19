import type { ViteH5CompilerContext, ViteHarmonyCompilerContext, ViteMiniCompilerContext } from '@tarojs/taro/types/compile/viteCompilerContext';
import type { PluginContext } from 'rollup';
export declare function getViteH5CompilerContext(rollupPluginContext: PluginContext): Promise<ViteH5CompilerContext | void>;
export declare function getViteHarmonyCompilerContext(rollupPluginContext: PluginContext): ViteHarmonyCompilerContext | void;
export declare function getViteMiniCompilerContext(rollupPluginContext: PluginContext): ViteMiniCompilerContext | void;
