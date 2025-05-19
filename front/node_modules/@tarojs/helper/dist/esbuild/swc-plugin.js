"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSwcPlugin = void 0;
const node_path_1 = require("node:path");
const core_1 = require("@swc/core");
const lodash_1 = require("lodash");
const constants_1 = require("../constants");
const utils_1 = require("../utils");
function getSwcPlugin(config) {
    return {
        name: 'swc-plugin',
        setup(build) {
            const namespace = 'tarojs:swc-helper';
            build.onResolve({ filter: constants_1.REG_SCRIPTS, namespace }, ({ resolveDir, path }) => ({
                path: (0, node_path_1.resolve)(resolveDir, path)
            }));
            build.onLoad({ filter: constants_1.REG_SCRIPTS, namespace }, (_a) => __awaiter(this, [_a], void 0, function* ({ path }) {
                const code = yield utils_1.fs.readFile(path, 'utf-8');
                const result = (0, core_1.transformSync)(code, (0, lodash_1.defaults)(config, {
                    jsc: { target: 'es2015' },
                    filename: path,
                    sourceMaps: true,
                    sourceFileName: path
                }));
                return {
                    contents: result.code,
                    loader: 'js'
                };
            }));
        }
    };
}
exports.getSwcPlugin = getSwcPlugin;
//# sourceMappingURL=swc-plugin.js.map