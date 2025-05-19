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
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConfigModificationState = void 0;
const path = require("node:path");
const binding_1 = require("@tarojs/binding");
const helper_1 = require("@tarojs/helper");
const util_1 = require("../util");
const createPage_1 = require("../util/createPage");
const constants_1 = require("./constants");
const creator_1 = require("./creator");
const fetchTemplate_1 = require("./fetchTemplate");
const DEFAULT_TEMPLATE_INFO = {
    name: 'default',
    css: "None" /* CSSType.None */,
    typescript: false,
    compiler: "Webpack5" /* CompilerType.Webpack5 */,
    framework: "React" /* FrameworkType.React */
};
var ConfigModificationState;
(function (ConfigModificationState) {
    ConfigModificationState[ConfigModificationState["Success"] = 0] = "Success";
    ConfigModificationState[ConfigModificationState["Fail"] = 1] = "Fail";
    ConfigModificationState[ConfigModificationState["NeedLess"] = 2] = "NeedLess";
})(ConfigModificationState || (exports.ConfigModificationState = ConfigModificationState = {}));
class Page extends creator_1.default {
    constructor(args) {
        super();
        this.rootPath = this._rootPath;
        const { modifyCustomTemplateConfig, afterCreate } = args, otherOptions = __rest(args, ["modifyCustomTemplateConfig", "afterCreate"]);
        this.conf = Object.assign({
            projectDir: '',
            projectName: '',
            template: '',
            description: '',
            pageDir: ''
        }, otherOptions);
        this.conf.projectName = path.basename(this.conf.projectDir);
        this.modifyCustomTemplateConfig = modifyCustomTemplateConfig;
        this.afterCreate = afterCreate;
        this.processPageName();
    }
    processPageName() {
        const { pageName } = this.conf;
        // todo 目前还没有对 subPkg 和 pageName 这两个字段做 格式验证或者处理
        const lastDirSplitSymbolIndex = pageName.lastIndexOf('/');
        if (lastDirSplitSymbolIndex !== -1) {
            this.conf.pageDir = pageName.substring(0, lastDirSplitSymbolIndex);
            this.conf.pageName = pageName.substring(lastDirSplitSymbolIndex + 1);
        }
    }
    getPkgPath() {
        const projectDir = this.conf.projectDir;
        let pkgPath = path.join(projectDir, 'package.json');
        if (!helper_1.fs.existsSync(pkgPath)) {
            // 适配 云开发 项目
            pkgPath = path.join(projectDir, 'client', 'package.json');
            if (!helper_1.fs.existsSync(pkgPath)) {
                console.log(helper_1.chalk.yellow('请在项目根目录下执行 taro create 命令!'));
                process.exit(0);
            }
        }
        return pkgPath;
    }
    getPkgTemplateInfo() {
        const pkg = helper_1.fs.readJSONSync(this.getPkgPath());
        const templateInfo = pkg.templateInfo || DEFAULT_TEMPLATE_INFO;
        // set template name
        templateInfo.template = templateInfo.name;
        delete templateInfo.name;
        return templateInfo;
    }
    setPageEntryPath(files, handler) {
        const configFileName = files.find((filename) => /\.config\.(js|ts)$/.test(filename));
        if (!configFileName)
            return;
        const getPageFn = handler[configFileName];
        const { setPageName = '', setSubPkgName = '' } = (getPageFn === null || getPageFn === void 0 ? void 0 : getPageFn(() => { }, this.conf)) || {};
        if (this.conf.subPkg) {
            this.pageEntryPath = setSubPkgName.replace(/\.config\.(js|ts)$/, '');
        }
        else {
            this.pageEntryPath = setPageName.replace(/\.config\.(js|ts)$/, '');
        }
    }
    setCustomTemplateConfig(customTemplateConfig) {
        const pkgTemplateInfo = this.getPkgTemplateInfo();
        const { compiler, css, customTemplatePath, typescript } = customTemplateConfig;
        const conf = {
            compiler: compiler || pkgTemplateInfo.compiler,
            css: css || pkgTemplateInfo.css,
            typescript: !(0, util_1.isNil)(typescript) ? typescript : pkgTemplateInfo.typescript,
            customTemplatePath,
            isCustomTemplate: true,
        };
        this.setTemplateConfig(conf);
    }
    setTemplateConfig(templateInfo) {
        this.conf = Object.assign(this.conf, templateInfo);
    }
    fetchTemplates() {
        return __awaiter(this, void 0, void 0, function* () {
            const homedir = (0, helper_1.getUserHomeDir)();
            let templateSource = helper_1.DEFAULT_TEMPLATE_SRC;
            if (!homedir)
                helper_1.chalk.yellow('找不到用户根目录，使用默认模版源！');
            if (this.conf.templateSource) {
                templateSource = this.conf.templateSource;
            }
            else {
                const taroConfigPath = path.join(homedir, helper_1.TARO_CONFIG_FOLDER);
                const taroConfig = path.join(taroConfigPath, helper_1.TARO_BASE_CONFIG);
                if (helper_1.fs.existsSync(taroConfig)) {
                    const config = yield helper_1.fs.readJSON(taroConfig);
                    templateSource = config && config.templateSource ? config.templateSource : helper_1.DEFAULT_TEMPLATE_SRC;
                }
                else {
                    yield helper_1.fs.createFile(taroConfig);
                    yield helper_1.fs.writeJSON(taroConfig, { templateSource });
                    templateSource = helper_1.DEFAULT_TEMPLATE_SRC;
                }
            }
            // 从模板源下载模板
            yield (0, fetchTemplate_1.default)(templateSource, this.templatePath(''), this.conf.clone);
        });
    }
    create() {
        return __awaiter(this, void 0, void 0, function* () {
            const date = new Date();
            this.conf.date = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
            // apply 插件，由插件设置自定义模版 config
            yield this.modifyCustomTemplateConfig(this.setCustomTemplateConfig.bind(this));
            if (!this.conf.isCustomTemplate) {
                const pkgTemplateInfo = this.getPkgTemplateInfo();
                this.setTemplateConfig(pkgTemplateInfo);
                if (!helper_1.fs.existsSync(this.templatePath(this.conf.template))) {
                    yield this.fetchTemplates();
                }
            }
            this.write();
        });
    }
    updateAppConfig() {
        const { parse, generate, traverse } = helper_1.babelKit;
        let modifyState = ConfigModificationState.Fail;
        const { subPkg, projectDir, typescript } = this.conf;
        const [sourceString, pageString] = this.pageEntryPath.split('/src/');
        const appConfigPath = (0, helper_1.resolveScriptPath)(path.join(projectDir, sourceString, 'src', 'app.config'));
        if (!helper_1.fs.existsSync(appConfigPath)) {
            return console.log(`${helper_1.chalk.red('x ')}${helper_1.chalk.grey(`无法获取 ${appConfigPath} 配置文件，请手动到配置文件中补全新页面信息`)}`);
        }
        const configFileContent = helper_1.fs.readFileSync(appConfigPath, 'utf-8');
        const ast = parse(configFileContent, {
            sourceType: 'module',
            plugins: typescript ? ['typescript'] : []
        });
        const callback = (state) => {
            modifyState = state;
        };
        traverse(ast, {
            ExportDefaultDeclaration(path) {
                (0, createPage_1.modifyPagesOrSubPackages)({
                    path,
                    fullPagePath: pageString,
                    subPkgRootPath: subPkg,
                    callback
                });
            },
        });
        switch (modifyState) {
            case ConfigModificationState.Fail:
                console.log(`${helper_1.chalk.red('x ')}${helper_1.chalk.grey(`自动补全新页面信息失败， 请手动到 ${appConfigPath} 文件中补全新页面信息`)}`);
                break;
            case ConfigModificationState.Success:
                {
                    const newCode = generate(ast, { retainLines: true });
                    helper_1.fs.writeFileSync(appConfigPath, newCode.code);
                    console.log(`${helper_1.chalk.green('✔ ')}${helper_1.chalk.grey(`新页面信息已在 ${appConfigPath} 文件中自动补全`)}`);
                    break;
                }
            case ConfigModificationState.NeedLess:
                console.log(`${helper_1.chalk.green('✔ ')}${helper_1.chalk.grey(`新页面信息已存在在 ${appConfigPath} 文件中，不需要补全`)}`);
                break;
        }
    }
    write() {
        const { projectName, projectDir, template, pageName, isCustomTemplate, customTemplatePath, subPkg, pageDir } = this.conf;
        let templatePath;
        if (isCustomTemplate) {
            templatePath = customTemplatePath;
        }
        else {
            templatePath = this.templatePath(template);
        }
        if (!helper_1.fs.existsSync(templatePath))
            return console.log(helper_1.chalk.red(`创建页面错误：找不到模板${templatePath}`));
        // 引入模板编写者的自定义逻辑
        const handlerPath = path.join(templatePath, constants_1.TEMPLATE_CREATOR);
        const basePageFiles = helper_1.fs.existsSync(handlerPath) ? require(handlerPath).basePageFiles : [];
        const files = Array.isArray(basePageFiles) ? basePageFiles : [];
        const handler = helper_1.fs.existsSync(handlerPath) ? require(handlerPath).handler : {};
        this.setPageEntryPath(files, handler);
        (0, binding_1.createPage)({
            pageDir,
            subPkg,
            projectDir,
            projectName,
            template,
            framework: this.conf.framework,
            css: this.conf.css || "None" /* CSSType.None */,
            typescript: this.conf.typescript,
            compiler: this.conf.compiler,
            templateRoot: (0, util_1.getRootPath)(),
            version: (0, util_1.getPkgVersion)(),
            date: this.conf.date,
            description: this.conf.description,
            pageName,
            isCustomTemplate,
            customTemplatePath,
            basePageFiles: files,
            period: "CreatePage" /* PeriodType.CreatePage */,
        }, handler).then(() => {
            console.log(`${helper_1.chalk.green('✔ ')}${helper_1.chalk.grey(`创建页面 ${this.conf.pageName} 成功！`)}`);
            this.updateAppConfig();
            this.afterCreate && this.afterCreate(true);
        }).catch(err => {
            console.log(err);
            this.afterCreate && this.afterCreate(false);
        });
    }
}
exports.default = Page;
//# sourceMappingURL=page.js.map