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
const binding_1 = require("@tarojs/binding");
const helper_1 = require("@tarojs/helper");
const util_1 = require("../util");
const creator_1 = require("./creator");
class Plugin extends creator_1.default {
    constructor(options) {
        super();
        this.conf = Object.assign(Object.assign({}, options), { projectName: path.basename(options.projectDir), version: this.getCliVersion() });
    }
    getCliVersion() {
        const pkgPath = path.join(this._rootPath, 'package.json');
        const pkg = helper_1.fs.readJSONSync(pkgPath);
        return pkg.version;
    }
    create() {
        return __awaiter(this, void 0, void 0, function* () {
            const { projectDir, template, pluginName } = this.conf;
            const templatePath = this.templatePath(template);
            if (!helper_1.fs.existsSync(templatePath)) {
                console.log(helper_1.chalk.red(`创建插件失败：找不到模板${templatePath}`));
                return;
            }
            (0, binding_1.createPlugin)({
                projectRoot: projectDir,
                projectName: pluginName,
                templateRoot: (0, util_1.getRootPath)(),
                template,
                version: this.conf.version,
                description: this.conf.description,
                pluginType: this.conf.type,
            });
        });
    }
}
exports.default = Plugin;
//# sourceMappingURL=plugin.js.map