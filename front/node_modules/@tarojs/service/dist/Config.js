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
const path = require("node:path");
const helper_1 = require("@tarojs/helper");
const ora = require("ora");
const webpack_merge_1 = require("webpack-merge");
const utils_1 = require("./utils");
const constants_1 = require("./utils/constants");
class Config {
    constructor(opts) {
        this.appPath = opts.appPath;
        this.disableGlobalConfig = !!(opts === null || opts === void 0 ? void 0 : opts.disableGlobalConfig);
    }
    init(configEnv) {
        return __awaiter(this, void 0, void 0, function* () {
            this.initialConfig = {};
            this.initialGlobalConfig = {};
            this.isInitSuccess = false;
            this.configPath = (0, helper_1.resolveScriptPath)(path.join(this.appPath, constants_1.CONFIG_DIR_NAME, constants_1.DEFAULT_CONFIG_FILE));
            if (!helper_1.fs.existsSync(this.configPath)) {
                if (this.disableGlobalConfig)
                    return;
                this.initGlobalConfig();
            }
            else {
                this.initGlobalConfig(configEnv.command);
                (0, helper_1.createSwcRegister)({
                    only: [
                        filePath => filePath.indexOf(path.join(this.appPath, constants_1.CONFIG_DIR_NAME)) >= 0
                    ]
                });
                try {
                    const userExport = (0, helper_1.getModuleDefaultExport)(require(this.configPath));
                    this.initialConfig = typeof userExport === 'function' ? yield userExport(webpack_merge_1.merge, configEnv) : userExport;
                    this.isInitSuccess = true;
                }
                catch (err) {
                    console.log(err);
                }
            }
        });
    }
    initGlobalConfig(command = '') {
        const homedir = (0, helper_1.getUserHomeDir)();
        if (!homedir)
            return console.error('获取不到用户 home 路径');
        const globalPluginConfigPath = path.join((0, helper_1.getUserHomeDir)(), helper_1.TARO_GLOBAL_CONFIG_DIR, helper_1.TARO_GLOBAL_CONFIG_FILE);
        if (!helper_1.fs.existsSync(globalPluginConfigPath))
            return;
        const spinner = ora(`开始获取 taro 全局配置文件： ${globalPluginConfigPath}`).start();
        try {
            this.initialGlobalConfig = helper_1.fs.readJSONSync(globalPluginConfigPath) || {};
            this.initialGlobalConfig = (0, utils_1.filterGlobalConfig)(this.initialGlobalConfig, command);
            spinner.succeed('获取 taro 全局配置成功');
        }
        catch (e) {
            spinner.stop();
            console.warn(`获取全局配置失败，如果需要启用全局插件请查看配置文件: ${globalPluginConfigPath} `);
        }
    }
    getConfigWithNamed(platform, configName) {
        const initialConfig = this.initialConfig;
        const sourceDirName = initialConfig.sourceRoot || helper_1.SOURCE_DIR;
        const outputDirName = initialConfig.outputRoot || helper_1.OUTPUT_DIR;
        const sourceDir = path.join(this.appPath, sourceDirName);
        const entryName = helper_1.ENTRY;
        const entryFilePath = (0, helper_1.resolveScriptPath)(path.join(sourceDir, entryName));
        const entry = {
            [entryName]: [entryFilePath]
        };
        return Object.assign(Object.assign({ entry, alias: initialConfig.alias || {}, copy: initialConfig.copy, sourceRoot: sourceDirName, outputRoot: outputDirName, platform, framework: initialConfig.framework, compiler: initialConfig.compiler, cache: initialConfig.cache, logger: initialConfig.logger, baseLevel: initialConfig.baseLevel, csso: initialConfig.csso, sass: initialConfig.sass, uglify: initialConfig.uglify, plugins: initialConfig.plugins, projectName: initialConfig.projectName, env: initialConfig.env, defineConstants: initialConfig.defineConstants, designWidth: initialConfig.designWidth, deviceRatio: initialConfig.deviceRatio, projectConfigName: initialConfig.projectConfigName, jsMinimizer: initialConfig.jsMinimizer, cssMinimizer: initialConfig.cssMinimizer, terser: initialConfig.terser, esbuild: initialConfig.esbuild }, initialConfig[configName]), initialConfig[platform]);
    }
}
exports.default = Config;
//# sourceMappingURL=Config.js.map