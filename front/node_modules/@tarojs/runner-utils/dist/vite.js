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
exports.getViteMiniCompilerContext = exports.getViteHarmonyCompilerContext = exports.getViteH5CompilerContext = void 0;
const constant_1 = require("./constant");
function getViteH5CompilerContext(rollupPluginContext) {
    return __awaiter(this, void 0, void 0, function* () {
        const info = process.env.NODE_ENV === 'production'
            ? rollupPluginContext.getModuleInfo(constant_1.VITE_COMPILER_LABEL)
            : yield rollupPluginContext.load({ id: constant_1.VITE_COMPILER_LABEL });
        const compiler = info === null || info === void 0 ? void 0 : info.meta.viteCompilerContext;
        return compiler;
    });
}
exports.getViteH5CompilerContext = getViteH5CompilerContext;
function getViteHarmonyCompilerContext(rollupPluginContext) {
    const info = rollupPluginContext.getModuleInfo(constant_1.VITE_COMPILER_LABEL);
    const compiler = info === null || info === void 0 ? void 0 : info.meta.viteCompilerContext;
    return compiler;
}
exports.getViteHarmonyCompilerContext = getViteHarmonyCompilerContext;
function getViteMiniCompilerContext(rollupPluginContext) {
    const info = rollupPluginContext.getModuleInfo(constant_1.VITE_COMPILER_LABEL);
    const compiler = info === null || info === void 0 ? void 0 : info.meta.viteCompilerContext;
    return compiler;
}
exports.getViteMiniCompilerContext = getViteMiniCompilerContext;
