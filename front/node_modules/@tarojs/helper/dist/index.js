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
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createSwcRegister = exports.npm = exports.injectDefineConfigHeader = exports.createDebug = exports.chokidar = exports.swc = void 0;
exports.swc = __importStar(require("@swc/core"));
exports.chokidar = __importStar(require("chokidar"));
const createDebug = (id) => require('debug')(id);
exports.createDebug = createDebug;
var babelRegister_1 = require("./babelRegister");
Object.defineProperty(exports, "injectDefineConfigHeader", { enumerable: true, get: function () { return babelRegister_1.injectDefineConfigHeader; } });
__exportStar(require("./constants"), exports);
__exportStar(require("./dotenv"), exports);
__exportStar(require("./esbuild"), exports);
exports.npm = __importStar(require("./npm"));
var swcRegister_1 = require("./swcRegister");
Object.defineProperty(exports, "createSwcRegister", { enumerable: true, get: function () { return __importDefault(swcRegister_1).default; } });
__exportStar(require("./terminal"), exports);
__exportStar(require("./utils"), exports);
//# sourceMappingURL=index.js.map