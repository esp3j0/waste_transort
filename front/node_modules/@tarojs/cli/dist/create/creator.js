"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const path = require("node:path");
const helper_1 = require("@tarojs/helper");
const util_1 = require("../util");
class Creator {
    constructor(sourceRoot) {
        this.rootPath = this.sourceRoot(sourceRoot || path.join((0, util_1.getRootPath)()));
        this.init();
    }
    init() { }
    sourceRoot(rootPath) {
        if (typeof rootPath === 'string') {
            this._rootPath = path.resolve(rootPath);
        }
        if (!helper_1.fs.existsSync(this._rootPath)) {
            helper_1.fs.ensureDirSync(this._rootPath);
        }
        return this._rootPath;
    }
    templatePath(...args) {
        let filepath = path.join.apply(path, args);
        if (!path.isAbsolute(filepath)) {
            filepath = path.join(this._rootPath, 'templates', filepath);
        }
        return filepath;
    }
    write() { }
}
exports.default = Creator;
//# sourceMappingURL=creator.js.map