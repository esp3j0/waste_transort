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
Object.defineProperty(exports, "__esModule", { value: true });
exports.patchEnv = exports.dotenvParse = exports.formatPrefix = void 0;
const path = __importStar(require("node:path"));
const dotenv_1 = require("dotenv");
const dotenv_expand_1 = require("dotenv-expand");
const fs = __importStar(require("fs-extra"));
// 支持 --env-prefix=TARO_APP_,aa 类型参数
const formatPrefix = (prefixs = ['TARO_APP_']) => {
    const prefixsArr = (Array.isArray(prefixs) ? prefixs : prefixs.split(',')).map(prefix => prefix.trim()).filter(prefix => !!prefix);
    return prefixsArr;
};
exports.formatPrefix = formatPrefix;
const dotenvParse = (root, prefixs = ['TARO_APP_'], mode) => {
    const prefixsArr = (0, exports.formatPrefix)(prefixs);
    const envFiles = new Set([
        /** default file */ `.env`,
        /** local file */ `.env.local`,
    ]);
    if (mode) {
        envFiles.add(/** mode file */ `.env.${mode}`);
        envFiles.add(/** mode local file */ `.env.${mode}.local`);
    }
    let parseTemp = {};
    const load = envPath => {
        // file doesn'et exist
        if (!fs.existsSync(envPath))
            return;
        const env = (0, dotenv_1.parse)(fs.readFileSync(envPath));
        parseTemp = Object.assign(Object.assign({}, parseTemp), env);
    };
    envFiles.forEach(envPath => {
        load(path.resolve(root, envPath));
    });
    const parsed = {};
    Object.entries(parseTemp).forEach(([key, value]) => {
        if (prefixsArr.some(prefix => key.startsWith(prefix)) || ['TARO_APP_ID'].includes(key)) {
            parsed[key] = value;
        }
    });
    (0, dotenv_expand_1.expand)({ parsed });
    return parsed;
};
exports.dotenvParse = dotenvParse;
// 扩展 env
const patchEnv = (config, expandEnv) => {
    const expandEnvStringify = {};
    for (const key in expandEnv) {
        expandEnvStringify[key] = JSON.stringify(expandEnv[key]);
    }
    return Object.assign(Object.assign({}, config.env), expandEnvStringify);
};
exports.patchEnv = patchEnv;
//# sourceMappingURL=dotenv.js.map