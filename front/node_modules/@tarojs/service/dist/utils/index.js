"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.filterGlobalConfig = exports.printHelpLog = exports.resolvePresetsOrPlugins = exports.mergePlugins = exports.convertPluginsToObject = exports.getPluginPath = exports.isNpmPkg = void 0;
const path = require("node:path");
const helper_1 = require("@tarojs/helper");
const lodash_1 = require("lodash");
const resolve = require("resolve");
const isNpmPkg = name => !(/^(\.|\/)/.test(name));
exports.isNpmPkg = isNpmPkg;
function getPluginPath(pluginPath) {
    if ((0, exports.isNpmPkg)(pluginPath) || path.isAbsolute(pluginPath))
        return pluginPath;
    throw new Error('plugin 和 preset 配置必须为绝对路径或者包名');
}
exports.getPluginPath = getPluginPath;
function convertPluginsToObject(items) {
    return () => {
        const obj = {};
        if (Array.isArray(items)) {
            items.forEach(item => {
                if (typeof item === 'string') {
                    const name = getPluginPath(item);
                    obj[name] = null;
                }
                else if (Array.isArray(item)) {
                    const name = getPluginPath(item[0]);
                    obj[name] = item[1];
                }
            });
        }
        return obj;
    };
}
exports.convertPluginsToObject = convertPluginsToObject;
function mergePlugins(dist, src) {
    return () => {
        const srcObj = convertPluginsToObject(src)();
        const distObj = convertPluginsToObject(dist)();
        return (0, lodash_1.merge)(distObj, srcObj);
    };
}
exports.mergePlugins = mergePlugins;
// getModuleDefaultExport
function resolvePresetsOrPlugins(root, args, type, skipError) {
    var _a, _b;
    // 全局的插件引入报错，不抛出 Error 影响主流程，而是通过 log 提醒然后把插件 filter 掉，保证主流程不变
    const resolvedPresetsOrPlugins = [];
    const presetsOrPluginsNames = Object.keys(args) || [];
    for (let i = 0; i < presetsOrPluginsNames.length; i++) {
        const item = presetsOrPluginsNames[i];
        let fPath;
        try {
            fPath = resolve.sync(item, {
                basedir: root,
                extensions: ['.js', '.ts']
            });
        }
        catch (err) {
            if ((_a = args[item]) === null || _a === void 0 ? void 0 : _a.backup) {
                // 如果项目中没有，可以使用 CLI 中的插件
                fPath = (_b = args[item]) === null || _b === void 0 ? void 0 : _b.backup;
            }
            else if (skipError) {
                // 如果跳过报错，那么 log 提醒，并且不使用该插件
                console.log(helper_1.chalk.yellow(`找不到插件依赖 "${item}"，请先在项目中安装，项目路径：${root}`));
                continue;
            }
            else {
                console.log(helper_1.chalk.red(`找不到插件依赖 "${item}"，请先在项目中安装，项目路径：${root}`));
                process.exit(1);
            }
        }
        const resolvedItem = {
            id: fPath,
            path: fPath,
            type,
            opts: args[item] || {},
            apply() {
                try {
                    return (0, helper_1.getModuleDefaultExport)(require(fPath));
                }
                catch (error) {
                    console.error(error);
                    // 全局的插件运行报错，不抛出 Error 影响主流程，而是通过 log 提醒然后把插件 filter 掉，保证主流程不变
                    if (skipError) {
                        console.error(`插件依赖 "${item}" 加载失败，请检查插件配置`);
                    }
                    else {
                        throw new Error(`插件依赖 "${item}" 加载失败，请检查插件配置`);
                    }
                }
            }
        };
        resolvedPresetsOrPlugins.push(resolvedItem);
    }
    return resolvedPresetsOrPlugins;
}
exports.resolvePresetsOrPlugins = resolvePresetsOrPlugins;
function supplementBlank(length) {
    return Array(length).map(() => '').join(' ');
}
function printHelpLog(command, optionsList, synopsisList) {
    console.log(`Usage: taro ${command} [options]`);
    console.log();
    console.log('Options:');
    const keys = Array.from(optionsList.keys());
    const maxLength = keys.reduce((v1, v2) => {
        return v1.length > v2.length ? v1 : v2;
    }).length + 3;
    optionsList.forEach((v, k) => {
        const supplementBlankLength = maxLength - k.length;
        console.log(`  ${k}${supplementBlank(supplementBlankLength)}${v}`);
    });
    if (synopsisList && synopsisList.size) {
        console.log();
        console.log('Synopsis:');
        synopsisList.forEach(item => {
            console.log(`  $ ${item}`);
        });
    }
}
exports.printHelpLog = printHelpLog;
const ExcludePluginTagsForNullCommand = ['@jdtaro/plugin-build-'];
function filterGlobalConfig(globalConfig, command) {
    var _a, _b;
    const config = globalConfig;
    if (!command) {
        if ((_a = config.plugins) === null || _a === void 0 ? void 0 : _a.length) {
            config.plugins = config.plugins.filter(pluginName => {
                return !ExcludePluginTagsForNullCommand.some(tag => pluginName.includes(tag));
            });
        }
        return config;
    }
    const RelatedPluginTag = `@jdtaro/plugin-${command}-`;
    if ((_b = config.plugins) === null || _b === void 0 ? void 0 : _b.length) {
        config.plugins = config.plugins.filter(pluginName => {
            return pluginName.includes(RelatedPluginTag);
        });
    }
    return config;
}
exports.filterGlobalConfig = filterGlobalConfig;
//# sourceMappingURL=index.js.map