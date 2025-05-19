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
const node_events_1 = require("node:events");
const path = require("node:path");
const helper = require("@tarojs/helper");
const runnerUtils = require("@tarojs/runner-utils");
const shared_1 = require("@tarojs/shared");
const lodash_1 = require("lodash");
const tapable_1 = require("tapable");
const Plugin_1 = require("./Plugin");
const utils_1 = require("./utils");
const constants_1 = require("./utils/constants");
class Kernel extends node_events_1.EventEmitter {
    constructor(options) {
        super();
        this.debugger = process.env.DEBUG === 'Taro:Kernel' ? helper.createDebug('Taro:Kernel') : function () { };
        this.appPath = options.appPath || process.cwd();
        this.optsPresets = options.presets;
        this.optsPlugins = options.plugins;
        this.config = options.config;
        this.hooks = new Map();
        this.methods = new Map();
        this.commands = new Map();
        this.platforms = new Map();
        this.initHelper();
        this.initConfig();
        this.initPaths();
        this.initRunnerUtils();
    }
    initConfig() {
        this.initialConfig = this.config.initialConfig;
        this.initialGlobalConfig = this.config.initialGlobalConfig;
        this.debugger('initConfig', this.initialConfig);
    }
    initPaths() {
        this.paths = {
            appPath: this.appPath,
            nodeModulesPath: helper.recursiveFindNodeModules(path.join(this.appPath, helper.NODE_MODULES))
        };
        if (this.config.isInitSuccess) {
            Object.assign(this.paths, {
                configPath: this.config.configPath,
                sourcePath: path.join(this.appPath, this.initialConfig.sourceRoot),
                outputPath: path.resolve(this.appPath, this.initialConfig.outputRoot)
            });
        }
        this.debugger(`initPaths:${JSON.stringify(this.paths, null, 2)}`);
    }
    initHelper() {
        this.helper = helper;
        this.debugger('initHelper');
    }
    initRunnerUtils() {
        this.runnerUtils = runnerUtils;
        this.debugger('initRunnerUtils');
    }
    initPresetsAndPlugins() {
        const initialConfig = this.initialConfig;
        const initialGlobalConfig = this.initialGlobalConfig;
        const cliAndProjectConfigPresets = (0, utils_1.mergePlugins)(this.optsPresets || [], initialConfig.presets || [])();
        const cliAndProjectPlugins = (0, utils_1.mergePlugins)(this.optsPlugins || [], initialConfig.plugins || [])();
        const globalPlugins = (0, utils_1.convertPluginsToObject)(initialGlobalConfig.plugins || [])();
        const globalPresets = (0, utils_1.convertPluginsToObject)(initialGlobalConfig.presets || [])();
        this.debugger('initPresetsAndPlugins', cliAndProjectConfigPresets, cliAndProjectPlugins);
        this.debugger('globalPresetsAndPlugins', globalPlugins, globalPresets);
        process.env.NODE_ENV !== 'test' &&
            helper.createSwcRegister({
                only: [
                    ...Object.keys(cliAndProjectConfigPresets),
                    ...Object.keys(cliAndProjectPlugins),
                    ...Object.keys(globalPresets),
                    ...Object.keys(globalPlugins)
                ]
            });
        this.plugins = new Map();
        this.extraPlugins = {};
        this.globalExtraPlugins = {};
        this.resolvePresets(cliAndProjectConfigPresets, globalPresets);
        this.resolvePlugins(cliAndProjectPlugins, globalPlugins);
    }
    resolvePresets(cliAndProjectPresets, globalPresets) {
        const resolvedCliAndProjectPresets = (0, utils_1.resolvePresetsOrPlugins)(this.appPath, cliAndProjectPresets, constants_1.PluginType.Preset);
        while (resolvedCliAndProjectPresets.length) {
            this.initPreset(resolvedCliAndProjectPresets.shift());
        }
        const globalConfigRootPath = path.join(helper.getUserHomeDir(), helper.TARO_GLOBAL_CONFIG_DIR);
        const resolvedGlobalPresets = (0, utils_1.resolvePresetsOrPlugins)(globalConfigRootPath, globalPresets, constants_1.PluginType.Plugin, true);
        while (resolvedGlobalPresets.length) {
            this.initPreset(resolvedGlobalPresets.shift(), true);
        }
    }
    resolvePlugins(cliAndProjectPlugins, globalPlugins) {
        cliAndProjectPlugins = (0, lodash_1.merge)(this.extraPlugins, cliAndProjectPlugins);
        const resolvedCliAndProjectPlugins = (0, utils_1.resolvePresetsOrPlugins)(this.appPath, cliAndProjectPlugins, constants_1.PluginType.Plugin);
        globalPlugins = (0, lodash_1.merge)(this.globalExtraPlugins, globalPlugins);
        const globalConfigRootPath = path.join(helper.getUserHomeDir(), helper.TARO_GLOBAL_CONFIG_DIR);
        const resolvedGlobalPlugins = (0, utils_1.resolvePresetsOrPlugins)(globalConfigRootPath, globalPlugins, constants_1.PluginType.Plugin, true);
        const resolvedPlugins = resolvedCliAndProjectPlugins.concat(resolvedGlobalPlugins);
        while (resolvedPlugins.length) {
            this.initPlugin(resolvedPlugins.shift());
        }
        this.extraPlugins = {};
        this.globalExtraPlugins = {};
    }
    initPreset(preset, isGlobalConfigPreset) {
        this.debugger('initPreset', preset);
        const { id, path, opts, apply } = preset;
        const pluginCtx = this.initPluginCtx({ id, path, ctx: this });
        const { presets, plugins } = apply()(pluginCtx, opts) || {};
        this.registerPlugin(preset);
        if (Array.isArray(presets)) {
            const _presets = (0, utils_1.resolvePresetsOrPlugins)(this.appPath, (0, utils_1.convertPluginsToObject)(presets)(), constants_1.PluginType.Preset, isGlobalConfigPreset);
            while (_presets.length) {
                this.initPreset(_presets.shift(), isGlobalConfigPreset);
            }
        }
        if (Array.isArray(plugins)) {
            isGlobalConfigPreset
                ? (this.globalExtraPlugins = (0, lodash_1.merge)(this.globalExtraPlugins, (0, utils_1.convertPluginsToObject)(plugins)()))
                : (this.extraPlugins = (0, lodash_1.merge)(this.extraPlugins, (0, utils_1.convertPluginsToObject)(plugins)()));
        }
    }
    initPlugin(plugin) {
        const { id, path, opts, apply } = plugin;
        const pluginCtx = this.initPluginCtx({ id, path, ctx: this });
        this.debugger('initPlugin', plugin);
        this.registerPlugin(plugin);
        apply()(pluginCtx, opts);
        this.checkPluginOpts(pluginCtx, opts);
    }
    applyCliCommandPlugin(commandNames = []) {
        const existsCliCommand = [];
        for (let i = 0; i < commandNames.length; i++) {
            const commandName = commandNames[i];
            const commandFilePath = path.resolve(this.cliCommandsPath, `${commandName}.js`);
            if (this.cliCommands.includes(commandName))
                existsCliCommand.push(commandFilePath);
        }
        const commandPlugins = (0, utils_1.convertPluginsToObject)(existsCliCommand || [])();
        helper.createSwcRegister({ only: [...Object.keys(commandPlugins)] });
        const resolvedCommandPlugins = (0, utils_1.resolvePresetsOrPlugins)(this.appPath, commandPlugins, constants_1.PluginType.Plugin);
        while (resolvedCommandPlugins.length) {
            this.initPlugin(resolvedCommandPlugins.shift());
        }
    }
    checkPluginOpts(pluginCtx, opts) {
        if (typeof pluginCtx.optsSchema !== 'function') {
            return;
        }
        this.debugger('checkPluginOpts', pluginCtx);
        const joi = require('joi');
        const schema = pluginCtx.optsSchema(joi);
        if (!joi.isSchema(schema)) {
            throw new Error(`插件${pluginCtx.id}中设置参数检查 schema 有误，请检查！`);
        }
        const { error } = schema.validate(opts);
        if (error) {
            error.message = `插件${pluginCtx.id}获得的参数不符合要求，请检查！`;
            throw error;
        }
    }
    registerPlugin(plugin) {
        this.debugger('registerPlugin', plugin);
        if (this.plugins.has(plugin.id)) {
            throw new Error(`插件 ${plugin.id} 已被注册`);
        }
        this.plugins.set(plugin.id, plugin);
    }
    initPluginCtx({ id, path, ctx }) {
        const pluginCtx = new Plugin_1.default({ id, path, ctx });
        const internalMethods = ['onReady', 'onStart'];
        const kernelApis = [
            'appPath',
            'plugins',
            'platforms',
            'paths',
            'helper',
            'runOpts',
            'runnerUtils',
            'initialConfig',
            'applyPlugins',
            'applyCliCommandPlugin'
        ];
        internalMethods.forEach(name => {
            if (!this.methods.has(name)) {
                pluginCtx.registerMethod(name);
            }
        });
        return new Proxy(pluginCtx, {
            get: (target, name) => {
                if (this.methods.has(name)) {
                    const method = this.methods.get(name);
                    if (Array.isArray(method)) {
                        return (...arg) => {
                            method.forEach(item => {
                                item.apply(this, arg);
                            });
                        };
                    }
                    return method;
                }
                if (kernelApis.includes(name)) {
                    return typeof this[name] === 'function' ? this[name].bind(this) : this[name];
                }
                return target[name];
            }
        });
    }
    applyPlugins(args) {
        return __awaiter(this, void 0, void 0, function* () {
            let name;
            let initialVal;
            let opts;
            if (typeof args === 'string') {
                name = args;
            }
            else {
                name = args.name;
                initialVal = args.initialVal;
                opts = args.opts;
            }
            this.debugger('applyPlugins');
            this.debugger(`applyPlugins:name:${name}`);
            this.debugger(`applyPlugins:initialVal:${initialVal}`);
            this.debugger(`applyPlugins:opts:${opts}`);
            if (typeof name !== 'string') {
                throw new Error('调用失败，未传入正确的名称！');
            }
            const hooks = this.hooks.get(name) || [];
            if (!hooks.length) {
                return yield initialVal;
            }
            const waterfall = new tapable_1.AsyncSeriesWaterfallHook(['arg']);
            if (hooks.length) {
                const resArr = [];
                for (const hook of hooks) {
                    waterfall.tapPromise({
                        name: hook.plugin,
                        stage: hook.stage || 0,
                        // @ts-ignore
                        before: hook.before
                    }, (arg) => __awaiter(this, void 0, void 0, function* () {
                        const res = yield hook.fn(opts, arg);
                        if (constants_1.IS_MODIFY_HOOK.test(name) || constants_1.IS_EVENT_HOOK.test(name)) {
                            return res;
                        }
                        if (constants_1.IS_ADD_HOOK.test(name)) {
                            resArr.push(res);
                            return resArr;
                        }
                        return null;
                    }));
                }
            }
            return yield waterfall.promise(initialVal);
        });
    }
    runWithPlatform(platform) {
        if (!this.platforms.has(platform)) {
            throw new Error(`不存在编译平台 ${platform}`);
        }
        const config = this.platforms.get(platform);
        const withNameConfig = this.config.getConfigWithNamed(config.name, config.useConfigName);
        process.env.TARO_PLATFORM = (0, shared_1.getPlatformType)(config.name, config.useConfigName);
        return withNameConfig;
    }
    setRunOpts(opts) {
        this.runOpts = opts;
    }
    runHelp(name) {
        const command = this.commands.get(name);
        const defaultOptionsMap = new Map();
        defaultOptionsMap.set('-h, --help', 'output usage information');
        let customOptionsMap = new Map();
        if (command === null || command === void 0 ? void 0 : command.optionsMap) {
            customOptionsMap = new Map(Object.entries(command === null || command === void 0 ? void 0 : command.optionsMap));
        }
        const optionsMap = new Map([...customOptionsMap, ...defaultOptionsMap]);
        (0, utils_1.printHelpLog)(name, optionsMap, (command === null || command === void 0 ? void 0 : command.synopsisList) ? new Set(command === null || command === void 0 ? void 0 : command.synopsisList) : new Set());
    }
    run(args) {
        return __awaiter(this, void 0, void 0, function* () {
            var _a;
            let name;
            let opts;
            if (typeof args === 'string') {
                name = args;
            }
            else {
                name = args.name;
                opts = args.opts;
            }
            this.debugger('command:run');
            this.debugger(`command:run:name:${name}`);
            this.debugger('command:runOpts');
            this.debugger(`command:runOpts:${JSON.stringify(opts, null, 2)}`);
            this.setRunOpts(opts);
            this.debugger('initPresetsAndPlugins');
            this.initPresetsAndPlugins();
            yield this.applyPlugins('onReady');
            this.debugger('command:onStart');
            yield this.applyPlugins('onStart');
            if (!this.commands.has(name)) {
                throw new Error(`${name} 命令不存在`);
            }
            if (opts === null || opts === void 0 ? void 0 : opts.isHelp) {
                return this.runHelp(name);
            }
            if ((_a = opts === null || opts === void 0 ? void 0 : opts.options) === null || _a === void 0 ? void 0 : _a.platform) {
                opts.config = this.runWithPlatform(opts.options.platform);
                yield this.applyPlugins({
                    name: 'modifyRunnerOpts',
                    opts: {
                        opts: opts === null || opts === void 0 ? void 0 : opts.config
                    }
                });
            }
            yield this.applyPlugins({
                name,
                opts
            });
        });
    }
}
exports.default = Kernel;
//# sourceMappingURL=Kernel.js.map