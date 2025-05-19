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
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const helper_1 = require("@tarojs/helper");
const child_process = require("child_process");
const util_1 = require("../../util");
function checkReactNativeDependencies(packageInfo) {
    const packageNames = ['react', 'react-native', '@tarojs/taro-rn', '@tarojs/rn-runner'];
    const { dependencies, devDependencies } = packageInfo;
    for (let i = 0; i < packageNames.length; i++) {
        if (!dependencies[packageNames[i]] && !devDependencies[packageNames[i]]) {
            return false;
        }
    }
    return true;
}
function makeSureReactNativeInstalled(workspaceRoot) {
    return new Promise((resolve, reject) => {
        const packageInfo = JSON.parse(fs.readFileSync(path.join(workspaceRoot, 'package.json'), {
            encoding: 'utf8'
        }));
        if (checkReactNativeDependencies(packageInfo)) {
            resolve();
        }
        else {
            // 便于开发时切换版本
            const devTag = process.env.DEVTAG || '';
            console.log('Installing React-Native related packages:');
            let packages = `react@^18.2.0 react-dom@^18.2.0 react-native@^0.73.1 @react-native/metro-config@^0.73.2 expo@~50.0.2 @tarojs/taro-rn${devTag} @tarojs/components-rn${devTag} @tarojs/rn-runner${devTag} @tarojs/rn-supporter${devTag} @tarojs/runtime-rn${devTag}`;
            console.log(packages);
            // windows下不加引号的话，package.json中添加的依赖不会自动带上^
            packages = packages.split(' ').map(str => `"${str}"`).join(' ');
            let installCmd = `npm install ${packages} --save`;
            if (fs.existsSync(path.join(workspaceRoot, 'yarn.lock'))) {
                installCmd = `yarn add ${packages} --force`;
            }
            if (fs.existsSync(path.join(workspaceRoot, 'pnpm-lock.yaml'))) {
                installCmd = `pnpm add ${packages}`;
            }
            child_process.exec(installCmd, error => {
                if (error) {
                    reject(error);
                    return;
                }
                console.log(helper_1.chalk.green(`React-Native related packages have been installed successfully.${os.EOL}${os.EOL}`));
                console.log(`${helper_1.chalk.yellow('ATTEHNTION')}: Package.json has been modified automatically, please submit it by yourself.${os.EOL}${os.EOL}`);
                resolve();
            });
        }
    });
}
exports.default = (ctx) => {
    ctx.registerPlatform({
        name: 'rn',
        useConfigName: 'rn',
        fn(_a) {
            return __awaiter(this, arguments, void 0, function* ({ config }) {
                const { appPath, nodeModulesPath } = ctx.paths;
                const { npm } = ctx.helper;
                const { deviceType = 'android', port, resetCache, publicPath, bundleOutput, sourcemapOutput, sourceMapUrl, sourcemapSourcesRoot, assetsDest, qr } = ctx.runOpts.options;
                (0, util_1.printDevelopmentTip)('rn');
                // 准备 rnRunner 参数
                const rnRunnerOpts = Object.assign(Object.assign({}, config), { nodeModulesPath,
                    deviceType,
                    port,
                    qr,
                    resetCache,
                    publicPath,
                    bundleOutput,
                    sourcemapOutput,
                    sourceMapUrl,
                    sourcemapSourcesRoot,
                    assetsDest, buildAdapter: config.platform });
                if (!rnRunnerOpts.entry) {
                    rnRunnerOpts.entry = 'app';
                }
                makeSureReactNativeInstalled(appPath).then(() => __awaiter(this, void 0, void 0, function* () {
                    // build with metro
                    const rnRunner = yield npm.getNpmPkg('@tarojs/rn-runner', appPath);
                    yield rnRunner(appPath, rnRunnerOpts);
                }), error => {
                    console.log(helper_1.chalk.red('Error when detecting React-Native packages:'));
                    console.log(error);
                    console.log(`${helper_1.chalk.greenBright('TIP')}: 1) Try to remove React-Native dependencies in package.json and shoot again; 2) Install the packages above manually.`);
                });
            });
        }
    });
};
//# sourceMappingURL=rn.js.map