"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.esbuild = exports.requireWithEsbuild = exports.defaultEsbuildLoader = void 0;
const core_1 = require("@swc/core");
const esbuild_1 = __importDefault(require("esbuild"));
exports.esbuild = esbuild_1.default;
const lodash_1 = require("lodash");
const require_from_string_1 = __importDefault(require("require-from-string"));
const constants_1 = require("../constants");
exports.defaultEsbuildLoader = {
    '.js': 'js',
    '.jsx': 'tsx',
    '.ts': 'ts',
    '.json': 'json'
};
/** 基于 esbuild 的 require 实现 */
function requireWithEsbuild(id, { customConfig = {}, customSwcConfig = {}, cwd = process.cwd() } = {}) {
    const { outputFiles = [] } = esbuild_1.default.buildSync((0, lodash_1.defaults)((0, lodash_1.omit)(customConfig, ['alias', 'define', 'loader', 'plugins']), {
        platform: 'node',
        absWorkingDir: cwd,
        bundle: true,
        define: (0, lodash_1.defaults)(customConfig.define, {
            // AMD 被 esbuild 转 ESM 后，是套着 ESM 外皮的 AMD 语法模块。
            // Webpack HarmonyDetectionParserPlugin 会阻止 AMDDefineDependencyParserPlugin 对这些模块的处理。
            // 导致这些模块报错（如 lodash）。目前的办法是把 define 置为 false，不支持 AMD 导出。
            define: 'false',
        }),
        alias: Object.fromEntries(Object.entries(customConfig.alias || {}).filter(([key]) => !key.startsWith('/'))),
        entryPoints: [id],
        format: 'esm',
        loader: (0, lodash_1.defaults)(customConfig.loader, exports.defaultEsbuildLoader),
        mainFields: [...constants_1.defaultMainFields],
        write: false,
    }));
    // Note: esbuild.buildSync 模式下不支持引入插件，所以这里需要手动转换
    const { code = '' } = (0, core_1.transformSync)(outputFiles[0].text, (0, lodash_1.defaults)(customSwcConfig, {
        jsc: { target: 'es2015' },
    }));
    return (0, require_from_string_1.default)(code, id);
}
exports.requireWithEsbuild = requireWithEsbuild;
__exportStar(require("./utils"), exports);
//# sourceMappingURL=index.js.map