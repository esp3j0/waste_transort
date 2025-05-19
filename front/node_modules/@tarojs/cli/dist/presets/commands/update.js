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
const inquirer = require("inquirer");
const getLatestVersion = require("latest-version");
const ora = require("ora");
const semver = require("semver");
const packagesManagement_1 = require("../../config/packagesManagement");
const util_1 = require("../../util");
exports.default = (ctx) => {
    ctx.registerCommand({
        name: 'update',
        synopsisList: [
            'taro update self [version]',
            'taro update project [version]'
        ],
        optionsMap: {
            '--npm [npm]': '包管理工具',
            '-h, --help': 'output usage information'
        },
        fn(_a) {
            return __awaiter(this, arguments, void 0, function* ({ _, options }) {
                const { npm } = options;
                const [, updateType, version] = _;
                const { appPath, configPath } = ctx.paths;
                const { chalk, fs, PROJECT_CONFIG, UPDATE_PACKAGE_LIST } = ctx.helper;
                const pkgPath = path.join(appPath, 'package.json');
                const pkgName = (0, util_1.getPkgItemByKey)('name');
                const conf = {
                    npm: null
                };
                const prompts = [];
                function getTargetVersion() {
                    return __awaiter(this, void 0, void 0, function* () {
                        let targetTaroVersion;
                        if (version) {
                            targetTaroVersion = semver.clean(version);
                        }
                        else {
                            try {
                                targetTaroVersion = yield getLatestVersion(pkgName, {
                                    version: 'latest'
                                });
                            }
                            catch (e) {
                                targetTaroVersion = yield getLatestVersion(pkgName);
                            }
                        }
                        if (!semver.valid(targetTaroVersion)) {
                            console.log(chalk.red('命令错误:无效的 version ~'));
                            throw Error('无效的 version!');
                        }
                        return targetTaroVersion;
                    });
                }
                function execUpdate(command, version, isSelf = false) {
                    const updateTarget = isSelf ? ' CLI ' : ' Taro 项目依赖';
                    const spinString = `正在更新${updateTarget}到 v${version} ...`;
                    const spinner = ora(spinString).start();
                    (0, util_1.execCommand)({
                        command,
                        successCallback(data) {
                            spinner.stop();
                            console.log(data.replace(/\n$/, ''));
                        },
                        failCallback(data) {
                            spinner.stop();
                            spinner.warn(data.replace(/\n$/, ''));
                        }
                    });
                }
                /** 更新全局的 Taro CLI */
                function updateSelf() {
                    return __awaiter(this, void 0, void 0, function* () {
                        const spinner = ora('正在获取最新版本信息...').start();
                        const targetTaroVersion = yield getTargetVersion();
                        spinner.stop();
                        console.log(chalk.green(`Taro 最新版本：${targetTaroVersion}\n`));
                        askNpm(conf, prompts);
                        const answers = npm ? { npm } : yield inquirer.prompt(prompts);
                        const command = `${packagesManagement_1.default[answers.npm].globalCommand}@${targetTaroVersion}`;
                        execUpdate(command, targetTaroVersion, true);
                    });
                }
                /** 更新当前项目中的 Taro 相关依赖 */
                function updateProject() {
                    return __awaiter(this, void 0, void 0, function* () {
                        if (!configPath || !fs.existsSync(configPath)) {
                            console.log(chalk.red(`找不到项目配置文件 ${PROJECT_CONFIG}，请确定当前目录是 Taro 项目根目录!`));
                            process.exit(1);
                        }
                        const packageMap = require(pkgPath);
                        const spinner = ora('正在获取最新版本信息...').start();
                        const version = yield getTargetVersion();
                        spinner.stop();
                        const oldVersion = packageMap.dependencies['@tarojs/taro'];
                        // 更新 @tarojs/* 版本和 NervJS 版本
                        Object.keys(packageMap.dependencies || {}).forEach((key) => {
                            if (UPDATE_PACKAGE_LIST.indexOf(key) !== -1) {
                                packageMap.dependencies[key] = version;
                            }
                        });
                        Object.keys(packageMap.devDependencies || {}).forEach((key) => {
                            if (UPDATE_PACKAGE_LIST.indexOf(key) !== -1) {
                                packageMap.devDependencies[key] = version;
                            }
                        });
                        // 写入package.json
                        try {
                            yield fs.writeJson(pkgPath, packageMap, { spaces: '\t' });
                            console.log(chalk.green(`项目当前 Taro 版本：${oldVersion}，Taro 最新版本：${version}，更新项目 package.json 成功！`));
                            console.log();
                        }
                        catch (err) {
                            console.error(err);
                        }
                        askNpm(conf, prompts);
                        const answers = npm ? { npm } : yield inquirer.prompt(prompts);
                        const command = packagesManagement_1.default[answers.npm].command;
                        execUpdate(command, version);
                    });
                }
                function askNpm(conf, prompts) {
                    const packages = [
                        {
                            name: 'yarn',
                            value: 'yarn'
                        },
                        {
                            name: 'pnpm',
                            value: 'pnpm'
                        },
                        {
                            name: 'npm',
                            value: 'npm'
                        },
                        {
                            name: 'cnpm',
                            value: 'cnpm'
                        }
                    ];
                    if (typeof conf.npm !== 'string') {
                        prompts.push({
                            type: 'list',
                            name: 'npm',
                            message: '请选择包管理工具',
                            choices: packages
                        });
                    }
                }
                if (updateType === 'self')
                    return updateSelf();
                if (updateType === 'project')
                    return updateProject();
                console.log(chalk.red('命令错误:'));
                console.log(`${chalk.green('taro update self [version]')} 更新 Taro 开发工具 taro-cli 到指定版本或 Taro3 的最新版本`);
                console.log(`${chalk.green('taro update project [version]')} 更新项目所有 Taro 相关依赖到指定版本或 Taro3 的最新版本`);
            });
        }
    });
};
//# sourceMappingURL=update.js.map