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
const plugin_doctor_1 = require("@tarojs/plugin-doctor");
const appConfig_1 = require("../../util/appConfig");
const hooks = require("../constant");
exports.default = (ctx) => {
    ctx.registerCommand({
        name: 'build',
        optionsMap: {
            '--type [typeName]': 'Build type, weapp/swan/alipay/tt/qq/jd/h5/rn',
            '--watch': 'Watch mode',
            '--env [env]': 'Value for process.env.NODE_ENV',
            '--pages': 'Specify the pages to be compiled, separate multiple by comma',
            '--components': 'Specify the components to be compiled, separate multiple by comma',
            '--mode [mode]': 'Value of dotenv extname',
            '-p, --port [port]': 'Specified port',
            '--no-build': 'Do not build project',
            '--platform': '[rn] Specific React-Native build target: android / ios, android is default value',
            '--reset-cache': '[rn] Clear transform cache',
            '--public-path': '[rn] Assets public path',
            '--bundle-output': '[rn] File name where to store the resulting bundle',
            '--sourcemap-output': '[rn] File name where to store the sourcemap file for resulting bundle',
            '--sourcemap-use-absolute-path': '[rn]  Report SourceMapURL using its full path',
            '--sourcemap-sources-root': '[rn] Path to make sourcemaps sources entries relative to',
            '--assets-dest': '[rn] Directory name where to store assets referenced in the bundle',
            '--qr': '[rn] Print qrcode of React-Native bundle server',
            '--blended': 'Blended Taro project in an original MiniApp project',
            '--new-blended': 'Blended Taro project in an original MiniApp project while supporting building components independently',
            '--plugin [typeName]': 'Build Taro plugin project, weapp',
            '--env-prefix [envPrefix]': "Provide the dotEnv varables's prefix",
            '--no-inject-global-style': '[H5] Do not inject global style',
            '--no-check': 'Do not check config is valid or not',
        },
        synopsisList: [
            'taro build --type weapp',
            'taro build --type weapp --watch',
            'taro build --type weapp --watch --pages pages/index/index',
            'taro build --type weapp --env production',
            'taro build --type weapp --blended',
            'taro build --type weapp --no-build',
            'taro build native-components --type weapp',
            'taro build --type weapp --new-blended',
            'taro build --plugin weapp --watch',
            'taro build --plugin weapp',
            'taro build --type weapp --mode prepare --env-prefix TARO_APP_',
        ],
        fn(opts) {
            return __awaiter(this, void 0, void 0, function* () {
                const { options, config, _ } = opts;
                const { platform, isWatch, blended, newBlended, withoutBuild, noInjectGlobalStyle, noCheck } = options;
                const { fs, chalk, PROJECT_CONFIG } = ctx.helper;
                const { outputPath, configPath } = ctx.paths;
                const { args } = options;
                if (!configPath || !fs.existsSync(configPath)) {
                    console.log(chalk.red(`找不到项目配置文件${PROJECT_CONFIG}，请确定当前目录是 Taro 项目根目录!`));
                    process.exit(1);
                }
                if (typeof platform !== 'string') {
                    console.log(chalk.red('请传入正确的编译类型！'));
                    process.exit(0);
                }
                // 校验 Taro 项目配置
                if (!noCheck) {
                    const checkResult = yield checkConfig({
                        projectConfig: ctx.initialConfig,
                        helper: ctx.helper
                    });
                    if (!checkResult.isValid) {
                        const ERROR = chalk.red('[✗] ');
                        const WARNING = chalk.yellow('[!] ');
                        const SUCCESS = chalk.green('[✓] ');
                        const lineChalk = chalk.hex('#fff');
                        const errorChalk = chalk.hex('#f00');
                        console.log(errorChalk(`Taro 配置有误，请检查！ (${configPath})`));
                        checkResult.messages.forEach((message) => {
                            switch (message.kind) {
                                case 1 /* MessageKind.Error */:
                                    console.log('  ' + ERROR + lineChalk(message.content));
                                    break;
                                case 2 /* MessageKind.Success */:
                                    console.log('  ' + SUCCESS + lineChalk(message.content));
                                    break;
                                case 3 /* MessageKind.Warning */:
                                    console.log('  ' + WARNING + lineChalk(message.content));
                                    break;
                                case 4 /* MessageKind.Manual */:
                                    console.log('  ' + lineChalk(message.content));
                                    break;
                                default:
                                    break;
                            }
                        });
                        console.log('');
                        process.exit(0);
                    }
                }
                const isProduction = process.env.NODE_ENV === 'production' || !isWatch;
                // dist folder
                fs.ensureDirSync(outputPath);
                // is build native components mode?
                const isBuildNativeComp = _[1] === 'native-components';
                yield ctx.applyPlugins(hooks.ON_BUILD_START);
                yield ctx.applyPlugins({
                    name: platform,
                    opts: {
                        config: Object.assign(Object.assign({}, config), { isWatch, mode: isProduction ? 'production' : 'development', blended,
                            isBuildNativeComp,
                            withoutBuild,
                            newBlended,
                            noInjectGlobalStyle,
                            modifyAppConfig(appConfig) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    (0, appConfig_1.extractCompileEntry)(appConfig, args, ctx);
                                    yield ctx.applyPlugins({
                                        name: hooks.MODIFY_APP_CONFIG,
                                        opts: {
                                            appConfig
                                        }
                                    });
                                });
                            },
                            modifyWebpackChain(chain, webpack, data) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    yield ctx.applyPlugins({
                                        name: hooks.MODIFY_WEBPACK_CHAIN,
                                        initialVal: chain,
                                        opts: {
                                            chain,
                                            webpack,
                                            data,
                                        },
                                    });
                                });
                            },
                            modifyViteConfig(viteConfig, data, viteCompilerContext) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    yield ctx.applyPlugins({
                                        name: hooks.MODIFY_VITE_CONFIG,
                                        initialVal: viteConfig,
                                        opts: {
                                            viteConfig,
                                            data,
                                            viteCompilerContext
                                        },
                                    });
                                });
                            },
                            modifyBuildAssets(assets, miniPlugin) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    yield ctx.applyPlugins({
                                        name: hooks.MODIFY_BUILD_ASSETS,
                                        initialVal: assets,
                                        opts: {
                                            assets,
                                            miniPlugin,
                                        },
                                    });
                                });
                            },
                            modifyMiniConfigs(configMap) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    yield ctx.applyPlugins({
                                        name: hooks.MODIFY_MINI_CONFIGS,
                                        initialVal: configMap,
                                        opts: {
                                            configMap,
                                        },
                                    });
                                });
                            },
                            modifyComponentConfig(componentConfig, config) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    yield ctx.applyPlugins({
                                        name: hooks.MODIFY_COMPONENT_CONFIG,
                                        opts: {
                                            componentConfig,
                                            config,
                                        },
                                    });
                                });
                            },
                            onCompilerMake(compilation, compiler, plugin) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    yield ctx.applyPlugins({
                                        name: hooks.ON_COMPILER_MAKE,
                                        opts: {
                                            compilation,
                                            compiler,
                                            plugin,
                                        },
                                    });
                                });
                            },
                            onParseCreateElement(nodeName, componentConfig) {
                                return __awaiter(this, void 0, void 0, function* () {
                                    yield ctx.applyPlugins({
                                        name: hooks.ON_PARSE_CREATE_ELEMENT,
                                        opts: {
                                            nodeName,
                                            componentConfig,
                                        },
                                    });
                                });
                            },
                            onBuildFinish(_a) {
                                return __awaiter(this, arguments, void 0, function* ({ error, stats, isWatch }) {
                                    yield ctx.applyPlugins({
                                        name: hooks.ON_BUILD_FINISH,
                                        opts: {
                                            error,
                                            stats,
                                            isWatch,
                                        },
                                    });
                                });
                            } }),
                    },
                });
                yield ctx.applyPlugins(hooks.ON_BUILD_COMPLETE);
            });
        },
    });
};
function checkConfig(_a) {
    return __awaiter(this, arguments, void 0, function* ({ projectConfig, helper }) {
        const result = yield (0, plugin_doctor_1.validateConfig)(projectConfig, helper);
        return result;
    });
}
//# sourceMappingURL=build.js.map