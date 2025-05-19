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
const hooks = require("../constant");
exports.default = (ctx) => {
    ctx.registerCommand({
        name: 'create',
        optionsMap: {
            '--name [name]': '名称',
            '--dir [dir]': '路径',
            '--subpkg [subpkg]': '分包路径',
            '--description [description]': '介绍',
            '--type [type]': '模版类型(page(默认)|plugin-command|plugin-build|plugin-template)'
        },
        synopsisList: [
            'taro create page',
            'taro create --name=page --description=desc',
            'taro create my-plugin --type=plugin-command',
        ],
        fn({ _, options }) {
            const type = options.type || "page" /* createTemplateTypeEnum.PAGE */;
            const name = _[1] || options.name;
            const description = options.description || '';
            const afterCreate = options.afterCreate;
            const templateSource = options.templateSource;
            const framework = options.framework;
            const css = options.css;
            const typescript = options.typescript;
            const clone = options.clone;
            const { chalk } = ctx.helper;
            const { appPath } = ctx.paths;
            switch (type) {
                case "page" /* createTemplateTypeEnum.PAGE */: {
                    if (typeof name !== 'string') {
                        return console.log(chalk.red('请输入需要创建的页面名称'));
                    }
                    const Page = require('../../create/page').default;
                    const page = new Page({
                        clone,
                        subPkg: options.subpkg,
                        framework,
                        css,
                        typescript,
                        pageDir: options.dir,
                        pageName: name,
                        projectDir: appPath,
                        description,
                        templateSource,
                        afterCreate,
                        modifyCustomTemplateConfig(cb) {
                            return __awaiter(this, void 0, void 0, function* () {
                                yield ctx.applyPlugins({ name: hooks.MODIFY_CREATE_TEMPLATE, opts: cb });
                            });
                        }
                    });
                    page.create();
                    break;
                }
                case "plugin-command" /* createTemplateTypeEnum.PLUGIN_COMMAND */:
                case "plugin-build" /* createTemplateTypeEnum.PLUGIN_BUILD */:
                case "plugin-template" /* createTemplateTypeEnum.PLUGIN_TEMPLATE */:
                    {
                        if (typeof name !== 'string') {
                            return console.log(chalk.red('请输入需要创建的插件名称'));
                        }
                        const Plugin = require('../../create/plugin').default;
                        const plugin = new Plugin({
                            pluginName: name,
                            projectDir: appPath,
                            type,
                            description,
                            template: 'plugin-compile'
                        });
                        plugin.create();
                        break;
                    }
                default:
                    break;
            }
        }
    });
};
//# sourceMappingURL=create.js.map