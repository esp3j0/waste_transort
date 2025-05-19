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
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.babelKit = exports.fs = exports.removePathPrefix = exports.readConfig = exports.readPageConfig = exports.removeHeadSlash = exports.getModuleDefaultExport = exports.addPlatforms = exports.extnameExpRegOf = exports.readDirWithFileTypes = exports.getAllFilesInFolder = exports.applyArrayedVisitors = exports.mergeVisitors = exports.recursiveMerge = exports.getInstalledNpmPkgVersion = exports.getInstalledNpmPkgPath = exports.pascalCase = exports.emptyDirectory = exports.cssImports = exports.generateConstantsList = exports.getNpmPackageAbsolutePath = exports.generateEnvList = exports.resolveScriptPath = exports.resolveMainFilePath = exports.resolveSync = exports.isEmptyObject = exports.shouldUseCnpm = exports.shouldUseYarn = exports.getSystemUsername = exports.getHash = exports.getConfig = exports.getTaroPath = exports.getUserHomeDir = exports.recursiveFindNodeModules = exports.printLog = exports.resolveStylePath = exports.promoteRelativePath = exports.replaceAliasPath = exports.isAliasPath = exports.isQuickAppPkg = exports.isNpmPkg = exports.isNodeModule = exports.normalizePath = void 0;
const child_process = __importStar(require("node:child_process"));
const node_crypto_1 = require("node:crypto");
const os = __importStar(require("node:os"));
const path = __importStar(require("node:path"));
const babel = __importStar(require("@babel/core"));
const generator_1 = __importDefault(require("@babel/generator"));
const babelParser = __importStar(require("@babel/parser"));
const traverse_1 = __importDefault(require("@babel/traverse"));
const t = __importStar(require("@babel/types"));
const fs = __importStar(require("fs-extra"));
exports.fs = fs;
const lodash_1 = require("lodash");
const constants_1 = require("./constants");
const esbuild_1 = require("./esbuild");
const terminal_1 = require("./terminal");
const execSync = child_process.execSync;
function normalizePath(path) {
    return path.replace(/\\/g, '/').replace(/\/{2,}/g, '/');
}
exports.normalizePath = normalizePath;
const isNodeModule = (filename) => constants_1.REG_NODE_MODULES.test(filename);
exports.isNodeModule = isNodeModule;
function isNpmPkg(name) {
    if (/^(\.|\/)/.test(name)) {
        return false;
    }
    return true;
}
exports.isNpmPkg = isNpmPkg;
function isQuickAppPkg(name) {
    return /^@(system|service)\.[a-zA-Z]{1,}/.test(name);
}
exports.isQuickAppPkg = isQuickAppPkg;
function isAliasPath(name, pathAlias = {}) {
    const prefixes = Object.keys(pathAlias);
    if (prefixes.length === 0) {
        return false;
    }
    return prefixes.includes(name) || new RegExp(`^(${prefixes.join('|')})/`).test(name);
}
exports.isAliasPath = isAliasPath;
function replaceAliasPath(filePath, name, pathAlias = {}) {
    // 后续的 path.join 在遇到符号链接时将会解析为真实路径，如果
    // 这里的 filePath 没有做同样的处理，可能会导致 import 指向
    // 源代码文件，导致文件被意外修改
    filePath = fs.realpathSync(filePath);
    const prefixes = Object.keys(pathAlias);
    if (prefixes.includes(name)) {
        return promoteRelativePath(path.relative(filePath, fs.realpathSync(resolveScriptPath(pathAlias[name]))));
    }
    const reg = new RegExp(`^(${prefixes.join('|')})/(.*)`);
    name = name.replace(reg, function (_m, $1, $2) {
        return promoteRelativePath(path.relative(filePath, path.join(pathAlias[$1], $2)));
    });
    return name;
}
exports.replaceAliasPath = replaceAliasPath;
function promoteRelativePath(fPath) {
    const fPathArr = fPath.split(path.sep);
    let dotCount = 0;
    fPathArr.forEach((item) => {
        if (item.indexOf('..') >= 0) {
            dotCount++;
        }
    });
    if (dotCount === 1) {
        fPathArr.splice(0, 1, '.');
        return fPathArr.join('/');
    }
    if (dotCount > 1) {
        fPathArr.splice(0, 1);
        return fPathArr.join('/');
    }
    return normalizePath(fPath);
}
exports.promoteRelativePath = promoteRelativePath;
function resolveStylePath(p) {
    const realPath = p;
    const removeExtPath = p.replace(path.extname(p), '');
    const taroEnv = process.env.TARO_ENV;
    for (let i = 0; i < constants_1.CSS_EXT.length; i++) {
        const item = constants_1.CSS_EXT[i];
        if (taroEnv) {
            if (fs.existsSync(`${removeExtPath}.${taroEnv}${item}`)) {
                return `${removeExtPath}.${taroEnv}${item}`;
            }
        }
        if (fs.existsSync(`${p}${item}`)) {
            return `${p}${item}`;
        }
    }
    return realPath;
}
exports.resolveStylePath = resolveStylePath;
function printLog(type, tag, filePath) {
    const typeShow = constants_1.processTypeMap[type];
    const tagLen = tag.replace(/[\u0391-\uFFE5]/g, 'aa').length;
    const tagFormatLen = 8;
    if (tagLen < tagFormatLen) {
        const rightPadding = new Array(tagFormatLen - tagLen + 1).join(' ');
        tag += rightPadding;
    }
    const padding = '';
    filePath = filePath || '';
    if (typeof typeShow.color === 'string') {
        console.log(terminal_1.chalk[typeShow.color](typeShow.name), padding, tag, padding, filePath);
    }
    else {
        console.log(typeShow.color(typeShow.name), padding, tag, padding, filePath);
    }
}
exports.printLog = printLog;
function recursiveFindNodeModules(filePath, lastFindPath) {
    const findWorkspaceRoot = require('find-yarn-workspace-root');
    if (lastFindPath && normalizePath(filePath) === normalizePath(lastFindPath)) {
        return filePath;
    }
    const dirname = path.dirname(filePath);
    const workspaceRoot = findWorkspaceRoot(dirname);
    const nodeModules = path.join(workspaceRoot || dirname, 'node_modules');
    if (fs.existsSync(nodeModules)) {
        return nodeModules;
    }
    if (dirname.split(path.sep).length <= 1) {
        printLog("error" /* processTypeEnum.ERROR */, `在${dirname}目录下`, '未找到node_modules文件夹，请先安装相关依赖库！');
        return nodeModules;
    }
    return recursiveFindNodeModules(dirname, filePath);
}
exports.recursiveFindNodeModules = recursiveFindNodeModules;
function getUserHomeDir() {
    function homedir() {
        var _a;
        const env = process.env;
        const home = env.HOME;
        const user = env.LOGNAME || env.USER || env.LNAME || env.USERNAME;
        if (process.platform === 'win32') {
            return env.USERPROFILE || '' + env.HOMEDRIVE + env.HOMEPATH || home || '';
        }
        if (process.platform === 'darwin') {
            return home || (user ? '/Users/' + user : '');
        }
        if (process.platform === 'linux') {
            return home || (((_a = process.getuid) === null || _a === void 0 ? void 0 : _a.call(process)) === 0 ? '/root' : user ? '/home/' + user : '');
        }
        return home || '';
    }
    return typeof os.homedir === 'function' ? os.homedir() : homedir();
}
exports.getUserHomeDir = getUserHomeDir;
function getTaroPath() {
    const taroPath = path.join(getUserHomeDir(), constants_1.TARO_CONFIG_FOLDER);
    if (!fs.existsSync(taroPath)) {
        fs.ensureDirSync(taroPath);
    }
    return taroPath;
}
exports.getTaroPath = getTaroPath;
function getConfig() {
    const configPath = path.join(getTaroPath(), 'config.json');
    if (fs.existsSync(configPath)) {
        return require(configPath);
    }
    return {};
}
exports.getConfig = getConfig;
function getHash(text) {
    return (0, node_crypto_1.createHash)('sha256').update(text).digest('hex').substring(0, 8);
}
exports.getHash = getHash;
function getSystemUsername() {
    const userHome = getUserHomeDir();
    const systemUsername = process.env.USER || path.basename(userHome);
    return systemUsername;
}
exports.getSystemUsername = getSystemUsername;
function shouldUseYarn() {
    try {
        execSync('yarn --version', { stdio: 'ignore' });
        return true;
    }
    catch (e) {
        return false;
    }
}
exports.shouldUseYarn = shouldUseYarn;
function shouldUseCnpm() {
    try {
        execSync('cnpm --version', { stdio: 'ignore' });
        return true;
    }
    catch (e) {
        return false;
    }
}
exports.shouldUseCnpm = shouldUseCnpm;
function isEmptyObject(obj) {
    if (obj == null) {
        return true;
    }
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            return false;
        }
    }
    return true;
}
exports.isEmptyObject = isEmptyObject;
function resolveSync(id, opts = {}) {
    try {
        const resolve = require('resolve').sync;
        return resolve(id, Object.assign(Object.assign({}, opts), { packageFilter(pkg, pkgfile, dir) {
                var _a;
                if (opts.packageFilter) {
                    pkg = opts.packageFilter(pkg, pkgfile, dir);
                }
                else if ((_a = opts.mainFields) === null || _a === void 0 ? void 0 : _a.length) {
                    pkg.main = pkg[opts.mainFields.find((field) => pkg[field] && typeof pkg[field] === 'string') || 'main'];
                }
                return pkg;
            } }));
    }
    catch (error) {
        return null;
    }
}
exports.resolveSync = resolveSync;
function resolveMainFilePath(p, extArrs = constants_1.SCRIPT_EXT) {
    if (p.startsWith('pages/') || p === 'app.config') {
        return p;
    }
    const realPath = p;
    const taroEnv = process.env.TARO_ENV;
    for (let i = 0; i < extArrs.length; i++) {
        const item = extArrs[i];
        if (taroEnv) {
            if (fs.existsSync(`${p}.${taroEnv}${item}`)) {
                return `${p}.${taroEnv}${item}`;
            }
            if (fs.existsSync(`${p}${path.sep}index.${taroEnv}${item}`)) {
                return `${p}${path.sep}index.${taroEnv}${item}`;
            }
            if (fs.existsSync(`${p.replace(/\/index$/, `.${taroEnv}/index`)}${item}`)) {
                return `${p.replace(/\/index$/, `.${taroEnv}/index`)}${item}`;
            }
        }
        if (fs.existsSync(`${p}${item}`)) {
            return `${p}${item}`;
        }
        if (fs.existsSync(`${p}${path.sep}index${item}`)) {
            return `${p}${path.sep}index${item}`;
        }
    }
    // 存在多端页面但是对应的多端页面配置不存在时，使用该页面默认配置
    if (taroEnv && path.parse(p).base.endsWith(`.${taroEnv}.config`)) {
        const idx = p.lastIndexOf(`.${taroEnv}.config`);
        return resolveMainFilePath(p.slice(0, idx) + '.config');
    }
    return realPath;
}
exports.resolveMainFilePath = resolveMainFilePath;
function resolveScriptPath(p) {
    return resolveMainFilePath(p);
}
exports.resolveScriptPath = resolveScriptPath;
function generateEnvList(env) {
    const res = {};
    if (env && !isEmptyObject(env)) {
        for (const key in env) {
            try {
                res[`process.env.${key}`] = JSON.parse(env[key]);
            }
            catch (err) {
                res[`process.env.${key}`] = env[key];
            }
        }
    }
    return res;
}
exports.generateEnvList = generateEnvList;
/**
 * 获取 npm 文件或者依赖的绝对路径
 *
 * @param {string} 参数 1 - 组件路径
 * @param {string} 参数 2 - 文件扩展名
 * @returns {string} npm 文件绝对路径
 */
function getNpmPackageAbsolutePath(npmPath, defaultFile = 'index') {
    try {
        let packageName = '';
        let componentRelativePath = '';
        const packageParts = npmPath.split(path.sep);
        // 获取 npm 包名和指定的包文件路径
        // taro-loader/path/index => packageName = taro-loader, componentRelativePath = path/index
        // @tarojs/runtime/path/index => packageName = @tarojs/runtime, componentRelativePath = path/index
        if (npmPath.startsWith('@')) {
            packageName = packageParts.slice(0, 2).join(path.sep);
            componentRelativePath = packageParts.slice(2).join(path.sep);
        }
        else {
            packageName = packageParts[0];
            componentRelativePath = packageParts.slice(1).join(path.sep);
        }
        // 没有指定的包文件路径统一使用 defaultFile
        componentRelativePath || (componentRelativePath = defaultFile);
        // require.resolve 解析的路径会包含入口文件路径，通过正则过滤一下
        const match = require.resolve(packageName).match(new RegExp('.*' + packageName));
        if (!(match === null || match === void 0 ? void 0 : match.length))
            return null;
        const packagePath = match[0];
        return path.join(packagePath, `./${componentRelativePath}`);
    }
    catch (error) {
        return null;
    }
}
exports.getNpmPackageAbsolutePath = getNpmPackageAbsolutePath;
function generateConstantsList(constants) {
    const res = {};
    if (constants && !isEmptyObject(constants)) {
        for (const key in constants) {
            if ((0, lodash_1.isPlainObject)(constants[key])) {
                res[key] = generateConstantsList(constants[key]);
            }
            else {
                try {
                    res[key] = JSON.parse(constants[key]);
                }
                catch (err) {
                    res[key] = constants[key];
                }
            }
        }
    }
    return res;
}
exports.generateConstantsList = generateConstantsList;
function cssImports(content) {
    const results = [];
    const cssImportRegx = new RegExp(constants_1.REG_CSS_IMPORT);
    let match;
    content = String(content).replace(/\/\*.+?\*\/|\/\/.*(?=[\n\r])/g, '');
    while ((match = cssImportRegx.exec(content))) {
        results.push(match[2]);
    }
    return results;
}
exports.cssImports = cssImports;
/*eslint-disable*/
const retries = process.platform === 'win32' ? 100 : 1;
function emptyDirectory(dirPath, opts = { excludes: [] }) {
    if (fs.existsSync(dirPath)) {
        fs.readdirSync(dirPath).forEach((file) => {
            const curPath = path.join(dirPath, file);
            if (fs.lstatSync(curPath).isDirectory()) {
                let removed = false;
                let i = 0; // retry counter
                do {
                    try {
                        const excludes = Array.isArray(opts.excludes) ? opts.excludes : [opts.excludes];
                        const canRemove = !excludes.length ||
                            !excludes.some((item) => typeof item === 'string' ? curPath.indexOf(item) >= 0 : item.test(curPath));
                        if (canRemove) {
                            emptyDirectory(curPath);
                            fs.rmdirSync(curPath);
                        }
                        removed = true;
                    }
                    catch (e) {
                    }
                    finally {
                        if (++i < retries) {
                            continue;
                        }
                    }
                } while (!removed);
            }
            else {
                fs.unlinkSync(curPath);
            }
        });
    }
}
exports.emptyDirectory = emptyDirectory;
/* eslint-enable */
const pascalCase = (str) => str.charAt(0).toUpperCase() + (0, lodash_1.camelCase)(str.substr(1));
exports.pascalCase = pascalCase;
function getInstalledNpmPkgPath(pkgName, basedir) {
    try {
        const resolve = require('resolve').sync;
        return resolve(`${pkgName}/package.json`, { basedir });
    }
    catch (err) {
        return null;
    }
}
exports.getInstalledNpmPkgPath = getInstalledNpmPkgPath;
function getInstalledNpmPkgVersion(pkgName, basedir) {
    const pkgPath = getInstalledNpmPkgPath(pkgName, basedir);
    if (!pkgPath) {
        return null;
    }
    return fs.readJSONSync(pkgPath).version;
}
exports.getInstalledNpmPkgVersion = getInstalledNpmPkgVersion;
const recursiveMerge = (src, ...args) => {
    return (0, lodash_1.mergeWith)(src, ...args, (value, srcValue) => {
        const typeValue = typeof value;
        const typeSrcValue = typeof srcValue;
        if (typeValue !== typeSrcValue)
            return;
        if (Array.isArray(value) && Array.isArray(srcValue)) {
            return value.concat(srcValue);
        }
        if (typeValue === 'object') {
            return (0, exports.recursiveMerge)(value, srcValue);
        }
    });
};
exports.recursiveMerge = recursiveMerge;
const mergeVisitors = (src, ...args) => {
    const validFuncs = ['exit', 'enter'];
    return (0, lodash_1.mergeWith)(src, ...args, (value, srcValue, key, object, srcObject) => {
        if (!object.hasOwnProperty(key) || !srcObject.hasOwnProperty(key)) {
            return undefined;
        }
        const shouldMergeToArray = validFuncs.indexOf(key) > -1;
        if (shouldMergeToArray) {
            return (0, lodash_1.flatMap)([value, srcValue]);
        }
        const [newValue, newSrcValue] = [value, srcValue].map((v) => {
            if (typeof v === 'function') {
                return {
                    enter: v,
                };
            }
            else {
                return v;
            }
        });
        return (0, exports.mergeVisitors)(newValue, newSrcValue);
    });
};
exports.mergeVisitors = mergeVisitors;
const applyArrayedVisitors = (obj) => {
    let key;
    for (key in obj) {
        const funcs = obj[key];
        if (Array.isArray(funcs)) {
            obj[key] = (astPath, ...args) => {
                funcs.forEach((func) => {
                    func(astPath, ...args);
                });
            };
        }
        else if (typeof funcs === 'object') {
            (0, exports.applyArrayedVisitors)(funcs);
        }
    }
    return obj;
};
exports.applyArrayedVisitors = applyArrayedVisitors;
const getAllFilesInFolder = (folder_1, ...args_1) => __awaiter(void 0, [folder_1, ...args_1], void 0, function* (folder, filter = []) {
    let files = [];
    const list = readDirWithFileTypes(folder);
    yield Promise.all(list.map((item) => __awaiter(void 0, void 0, void 0, function* () {
        const itemPath = path.join(folder, item.name);
        if (item.isDirectory) {
            const _files = yield (0, exports.getAllFilesInFolder)(itemPath, filter);
            files = [...files, ..._files];
        }
        else if (item.isFile) {
            if (!filter.find((rule) => rule === item.name))
                files.push(itemPath);
        }
    })));
    return files;
});
exports.getAllFilesInFolder = getAllFilesInFolder;
function readDirWithFileTypes(folder) {
    const list = fs.readdirSync(folder);
    const res = list.map((name) => {
        const stat = fs.statSync(path.join(folder, name));
        return {
            name,
            isDirectory: stat.isDirectory(),
            isFile: stat.isFile(),
        };
    });
    return res;
}
exports.readDirWithFileTypes = readDirWithFileTypes;
function extnameExpRegOf(filePath) {
    return new RegExp(`${path.extname(filePath)}$`);
}
exports.extnameExpRegOf = extnameExpRegOf;
function addPlatforms(platform) {
    const upperPlatform = platform.toLocaleUpperCase();
    if (constants_1.PLATFORMS[upperPlatform])
        return;
    constants_1.PLATFORMS[upperPlatform] = platform;
}
exports.addPlatforms = addPlatforms;
const getModuleDefaultExport = (exports) => (exports.__esModule ? exports.default : exports);
exports.getModuleDefaultExport = getModuleDefaultExport;
function removeHeadSlash(str) {
    return str.replace(/^(\/|\\)/, '');
}
exports.removeHeadSlash = removeHeadSlash;
// converts ast nodes to js object
function exprToObject(node) {
    const types = ['BooleanLiteral', 'StringLiteral', 'NumericLiteral'];
    if (types.includes(node.type)) {
        return node.value;
    }
    if (node.name === 'undefined' && !node.value) {
        return undefined;
    }
    if (node.type === 'NullLiteral') {
        return null;
    }
    if (node.type === 'ObjectExpression') {
        return genProps(node.properties);
    }
    if (node.type === 'ArrayExpression') {
        return node.elements.reduce((acc, el) => [
            ...acc,
            ...(el.type === 'SpreadElement' ? exprToObject(el.argument) : [exprToObject(el)]),
        ], []);
    }
}
// converts ObjectExpressions to js object
function genProps(props) {
    return props.reduce((acc, prop) => {
        if (prop.type === 'SpreadElement') {
            return Object.assign(Object.assign({}, acc), exprToObject(prop.argument));
        }
        else if (prop.type !== 'ObjectMethod') {
            const v = exprToObject(prop.value);
            if (v !== undefined) {
                return Object.assign(Object.assign({}, acc), { [prop.key.name || prop.key.value]: v });
            }
        }
        return acc;
    }, {});
}
// read page config from a sfc file instead of the regular config file
function readSFCPageConfig(configPath) {
    var _a;
    if (!fs.existsSync(configPath))
        return {};
    const sfcSource = fs.readFileSync(configPath, 'utf8');
    const dpcReg = /definePageConfig\(\{[\w\W]+?\}\)/g;
    const matches = sfcSource.match(dpcReg);
    let result = {};
    if (matches && matches.length === 1) {
        const callExprHandler = (p) => {
            const { callee } = p.node;
            if (!callee.name)
                return;
            if (callee.name && callee.name !== 'definePageConfig')
                return;
            const configNode = p.node.arguments[0];
            result = exprToObject(configNode);
            p.stop();
        };
        const configSource = matches[0];
        const program = (_a = (babel.parse(configSource, { filename: '' }))) === null || _a === void 0 ? void 0 : _a.program;
        program && babel.traverse(program, { CallExpression: callExprHandler });
    }
    return result;
}
function readPageConfig(configPath) {
    let result = {};
    const extNames = ['.js', '.jsx', '.ts', '.tsx', '.vue'];
    // check source file extension
    extNames.some((ext) => {
        const tempPath = configPath.replace('.config', ext);
        if (fs.existsSync(tempPath)) {
            try {
                result = readSFCPageConfig(tempPath);
            }
            catch (error) {
                result = {};
            }
            return true;
        }
    });
    return result;
}
exports.readPageConfig = readPageConfig;
function readConfig(configPath, options = {}) {
    let result = {};
    if (fs.existsSync(configPath)) {
        if (constants_1.REG_JSON.test(configPath)) {
            result = fs.readJSONSync(configPath);
        }
        else {
            result = (0, esbuild_1.requireWithEsbuild)(configPath, {
                customConfig: {
                    alias: options.alias || {},
                    define: (0, lodash_1.defaults)({}, options.defineConstants || {}, {
                        define: 'define', // Note: 该场景下不支持 AMD 导出，这会导致 esbuild 替换 babel 的 define 方法
                    }),
                },
                customSwcConfig: {
                    jsc: {
                        parser: {
                            syntax: 'typescript',
                            decorators: true,
                        },
                        transform: {
                            legacyDecorator: true,
                        },
                        experimental: {
                            plugins: [
                                [path.resolve(__dirname, '../swc/swc_plugin_define_config.wasm'), {}]
                            ]
                        }
                    },
                    module: {
                        type: 'commonjs',
                    },
                },
            });
        }
        result = (0, exports.getModuleDefaultExport)(result);
    }
    else {
        result = readPageConfig(configPath);
    }
    return result;
}
exports.readConfig = readConfig;
// 去除路径前缀，比如 /, ./
function removePathPrefix(filePath = '') {
    const normalizedPath = path.normalize(filePath);
    const parsedPath = path.parse(normalizedPath);
    const { root, dir, base } = parsedPath;
    let result = path.join(dir, base);
    if (result.startsWith(root)) {
        result = result.slice(root.length);
    }
    return result;
}
exports.removePathPrefix = removePathPrefix;
// 集中引入 babel 工具箱，供编译时使用
exports.babelKit = {
    types: t,
    parse: babelParser.parse,
    generate: generator_1.default,
    traverse: traverse_1.default,
};
//# sourceMappingURL=utils.js.map