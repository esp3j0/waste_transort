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
exports.TaroPlatformWeb = void 0;
const path = require("node:path");
const shared_1 = require("@tarojs/shared");
const lodash_1 = require("lodash");
const package_1 = require("../utils/package");
const platform_1 = require("./platform");
class TaroPlatformWeb extends platform_1.default {
    constructor() {
        super(...arguments);
        this.platformType = shared_1.PLATFORM_TYPE.WEB;
    }
    /**
     * 1. 清空 dist 文件夹
     * 2. 输出编译提示
     */
    setup() {
        return __awaiter(this, void 0, void 0, function* () {
            var _a, _b;
            yield this.setupTransaction.perform(this.setupWebApp, this);
            (_b = (_a = this.ctx).onSetupClose) === null || _b === void 0 ? void 0 : _b.call(_a, this);
        });
    }
    setupWebApp() {
        const { output } = this.config;
        // webpack5 原生支持 output.clean 选项，但是 webpack4 不支持， 为统一行为，这里做一下兼容
        // （在 packages/taro-mini-runner/src/webpack/chain.ts 和 packages/taro-webpack-runner/src/utils/chain.ts 的 makeConfig 中对 clean 选项做了过滤）
        // eslint-disable-next-line eqeqeq
        if (output == undefined || output.clean == undefined || output.clean === true) {
            this.emptyOutputDir();
        }
        else if ((0, shared_1.isObject)(output.clean)) {
            this.emptyOutputDir(output.clean.keep || []);
        }
        this.printDevelopmentTip();
    }
    printDevelopmentTip() {
        var _a;
        const tips = [];
        const config = this.config;
        const { chalk } = this.helper;
        if (this.compiler === 'webpack5' && !((_a = config.cache) === null || _a === void 0 ? void 0 : _a.enable)) {
            tips.push(chalk.yellowBright('建议开启持久化缓存功能，能有效提升二次编译速度，详情请参考: https://docs.taro.zone/docs/config-detail#cache。'));
        }
        if (tips.length) {
            console.log(chalk.yellowBright('Tips:'));
            tips.forEach((item, index) => console.log(`${chalk.yellowBright(index + 1)}. ${item}`));
            console.log('\n');
        }
    }
    /**
     * 返回当前项目内的 runner 包
     */
    getRunner() {
        return __awaiter(this, void 0, void 0, function* () {
            const { appPath } = this.ctx.paths;
            const { npm } = this.helper;
            const runnerPkg = this.compiler === 'vite' ? '@tarojs/vite-runner' : '@tarojs/webpack5-runner';
            const runner = yield npm.getNpmPkg(runnerPkg, appPath);
            return runner.bind(null, appPath);
        });
    }
    /**
     * 准备 runner 参数
     * @param extraOptions 需要额外合入 Options 的配置项
     */
    getOptions(extraOptions = {}) {
        const { sourcePath } = this.ctx.paths;
        const { initialConfig } = this.ctx;
        const { port } = this.ctx.runOpts.options;
        const { recursiveMerge, ENTRY, SOURCE_DIR, OUTPUT_DIR } = this.ctx.helper;
        const entryFileName = `${ENTRY}.config`;
        const entryFile = path.basename(entryFileName);
        const defaultEntry = {
            [ENTRY]: [path.join(sourcePath, entryFile)]
        };
        const customEntry = (0, lodash_1.get)(initialConfig, 'h5.entry');
        const config = recursiveMerge(Object.assign({}, this.config), {
            entryFileName: ENTRY,
            env: {
                FRAMEWORK: JSON.stringify(this.config.framework),
                TARO_ENV: JSON.stringify(this.platform),
                TARO_PLATFORM: JSON.stringify(this.platformType),
                TARO_VERSION: JSON.stringify((0, package_1.getPkgVersion)())
            },
            devServer: { port },
            sourceRoot: this.config.sourceRoot || SOURCE_DIR,
            outputRoot: this.config.outputRoot || OUTPUT_DIR
        });
        config.entry = (0, lodash_1.merge)(defaultEntry, customEntry);
        return Object.assign(Object.assign(Object.assign({}, config), { buildAdapter: config.platform, platformType: this.platformType }), extraOptions);
    }
    /**
     * 调用 runner 开始编译
     * @param extraOptions 需要额外传入 runner 的配置项
     */
    build() {
        return __awaiter(this, arguments, void 0, function* (extraOptions = {}) {
            var _a, _b;
            (_b = (_a = this.ctx).onBuildInit) === null || _b === void 0 ? void 0 : _b.call(_a, this);
            yield this.buildTransaction.perform(this.buildWebApp, this, extraOptions);
        });
    }
    buildWebApp() {
        return __awaiter(this, arguments, void 0, function* (extraOptions = {}) {
            const runner = yield this.getRunner();
            const options = this.getOptions(Object.assign({
                runtimePath: this.runtimePath,
            }, extraOptions));
            yield runner(options);
        });
    }
    /**
     * 调用 runner 开启编译
     */
    start() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.setup();
            yield this.build();
        });
    }
}
exports.TaroPlatformWeb = TaroPlatformWeb;
//# sourceMappingURL=web.js.map