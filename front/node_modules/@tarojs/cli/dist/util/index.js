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
exports.isNil = exports.getPkgNameByFilterVersion = exports.execCommand = exports.clearConsole = exports.printDevelopmentTip = exports.readDirWithFileTypes = exports.getTemplateSourceType = exports.getAllFilesInFolder = exports.printPkgVersion = exports.getPkgItemByKey = exports.getPkgVersion = exports.getRootPath = void 0;
const path = require("node:path");
const helper_1 = require("@tarojs/helper");
const child_process_1 = require("child_process");
function getRootPath() {
    return path.resolve(__dirname, '../../');
}
exports.getRootPath = getRootPath;
function getPkgVersion() {
    return require(path.join(getRootPath(), 'package.json')).version;
}
exports.getPkgVersion = getPkgVersion;
function getPkgItemByKey(key) {
    const packageMap = require(path.join(getRootPath(), 'package.json'));
    if (Object.keys(packageMap).indexOf(key) === -1) {
        return {};
    }
    else {
        return packageMap[key];
    }
}
exports.getPkgItemByKey = getPkgItemByKey;
function printPkgVersion() {
    const taroVersion = getPkgVersion();
    console.log(`👽 Taro v${taroVersion}`);
    console.log();
}
exports.printPkgVersion = printPkgVersion;
const getAllFilesInFolder = (folder_1, ...args_1) => __awaiter(void 0, [folder_1, ...args_1], void 0, function* (folder, filter = []) {
    let files = [];
    const list = readDirWithFileTypes(folder);
    yield Promise.all(list.map((item) => __awaiter(void 0, void 0, void 0, function* () {
        const itemPath = path.join(folder, item.name);
        if (item.isDirectory) {
            const _files = yield (0, exports.getAllFilesInFolder)(itemPath, filter);
            files = [...files, ..._files];
        }
        else if (item.isFile) {
            if (!filter.find(rule => rule === item.name))
                files.push(itemPath);
        }
    })));
    return files;
});
exports.getAllFilesInFolder = getAllFilesInFolder;
function getTemplateSourceType(url) {
    if (/^github:/.test(url) || /^gitlab:/.test(url) || /^direct:/.test(url)) {
        return 'git';
    }
    else {
        return 'url';
    }
}
exports.getTemplateSourceType = getTemplateSourceType;
function readDirWithFileTypes(folder) {
    const list = helper_1.fs.readdirSync(folder);
    const res = list.map(name => {
        const stat = helper_1.fs.statSync(path.join(folder, name));
        return {
            name,
            isDirectory: stat.isDirectory(),
            isFile: stat.isFile()
        };
    });
    return res;
}
exports.readDirWithFileTypes = readDirWithFileTypes;
function printDevelopmentTip(platform) {
    if (process.env.NODE_ENV !== 'production' && process.env.NODE_ENV !== 'test') {
        let exampleCommand;
        if (helper_1.isWindows) {
            exampleCommand = `$ set NODE_ENV=production && taro build --type ${platform} --watch`;
        }
        else {
            exampleCommand = `$ NODE_ENV=production taro build --type ${platform} --watch`;
        }
        console.log(helper_1.chalk.yellowBright(`Tips: 预览模式生成的文件较大，设置 NODE_ENV 为 production 可以开启压缩。
Example:
${exampleCommand}
`));
    }
}
exports.printDevelopmentTip = printDevelopmentTip;
function clearConsole() {
    const readline = require('readline');
    if (process.stdout.isTTY) {
        const blank = '\n'.repeat(process.stdout.rows);
        console.log(blank);
        readline.cursorTo(process.stdout, 0, 0);
        readline.clearScreenDown(process.stdout);
    }
}
exports.clearConsole = clearConsole;
function execCommand(params) {
    const { command, successCallback, failCallback } = params;
    const child = (0, child_process_1.exec)(command);
    child.stdout.on('data', function (data) {
        successCallback === null || successCallback === void 0 ? void 0 : successCallback(data);
    });
    child.stderr.on('data', function (data) {
        failCallback === null || failCallback === void 0 ? void 0 : failCallback(data);
    });
}
exports.execCommand = execCommand;
function getPkgNameByFilterVersion(pkgString) {
    const versionFlagIndex = pkgString.lastIndexOf('@');
    return versionFlagIndex === 0 ? pkgString : pkgString.slice(0, versionFlagIndex);
}
exports.getPkgNameByFilterVersion = getPkgNameByFilterVersion;
function isNil(value) {
    return value === null || value === undefined;
}
exports.isNil = isNil;
//# sourceMappingURL=index.js.map