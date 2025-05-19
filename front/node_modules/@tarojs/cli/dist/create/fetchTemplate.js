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
const helper_1 = require("@tarojs/helper");
const AdmZip = require("adm-zip");
const axios_1 = require("axios");
const download = require("download-git-repo");
const ora = require("ora");
const util_1 = require("../util");
const constants_1 = require("./constants");
const TEMP_DOWNLOAD_FOLDER = 'taro-temp';
function fetchTemplate(templateSource, templateRootPath, clone) {
    const type = (0, util_1.getTemplateSourceType)(templateSource);
    const tempPath = path.join(templateRootPath, TEMP_DOWNLOAD_FOLDER);
    let name;
    // eslint-disable-next-line no-async-promise-executor
    return new Promise((resolve) => __awaiter(this, void 0, void 0, function* () {
        // 下载文件的缓存目录
        if (helper_1.fs.existsSync(tempPath))
            yield helper_1.fs.remove(tempPath);
        yield helper_1.fs.mkdirp(templateRootPath);
        yield helper_1.fs.mkdir(tempPath);
        const spinner = ora(`正在从 ${templateSource} 拉取远程模板...`).start();
        if (type === 'git') {
            name = path.basename(templateSource);
            download(templateSource, path.join(tempPath, name), { clone }, (error) => __awaiter(this, void 0, void 0, function* () {
                if (error) {
                    console.log(error);
                    spinner.color = 'red';
                    spinner.fail(helper_1.chalk.red('拉取远程模板仓库失败！'));
                    yield helper_1.fs.remove(tempPath);
                    return resolve();
                }
                spinner.color = 'green';
                spinner.succeed(`${helper_1.chalk.grey('拉取远程模板仓库成功！')}`);
                resolve();
            }));
        }
        else if (type === 'url') {
            // url 模板源，因为不知道来源名称，临时取名方便后续开发者从列表中选择
            name = 'from-remote-url';
            const zipPath = path.join(tempPath, name + '.zip');
            const unZipPath = path.join(tempPath, name);
            axios_1.default.get(templateSource, { responseType: 'stream' })
                .then(response => {
                const ws = helper_1.fs.createWriteStream(zipPath);
                response.data.pipe(ws);
                ws.on('finish', () => {
                    // unzip
                    const zip = new AdmZip(zipPath);
                    zip.extractAllTo(unZipPath, true);
                    const files = (0, util_1.readDirWithFileTypes)(unZipPath).filter(file => !file.name.startsWith('.') && file.isDirectory && file.name !== '__MACOSX');
                    if (files.length !== 1) {
                        spinner.color = 'red';
                        spinner.fail(helper_1.chalk.red(`拉取远程模板仓库失败！\n${new Error('远程模板源组织格式错误')}`));
                        return resolve();
                    }
                    name = path.join(name, files[0].name);
                    spinner.color = 'green';
                    spinner.succeed(`${helper_1.chalk.grey('拉取远程模板仓库成功！')}`);
                    resolve();
                });
                ws.on('error', error => { throw error; });
            })
                .catch((error) => __awaiter(this, void 0, void 0, function* () {
                spinner.color = 'red';
                spinner.fail(helper_1.chalk.red(`拉取远程模板仓库失败！\n${error}`));
                yield helper_1.fs.remove(tempPath);
                return resolve();
            }));
        }
    })).then(() => __awaiter(this, void 0, void 0, function* () {
        const templateFolder = name ? path.join(tempPath, name) : '';
        // 下载失败，只显示默认模板
        if (!helper_1.fs.existsSync(templateFolder))
            return Promise.resolve([]);
        const isTemplateGroup = !(helper_1.fs.existsSync(path.join(templateFolder, 'package.json')) ||
            helper_1.fs.existsSync(path.join(templateFolder, 'package.json.tmpl')));
        if (isTemplateGroup) {
            // 模板组
            const files = (0, util_1.readDirWithFileTypes)(templateFolder)
                .filter(file => !file.name.startsWith('.') && file.isDirectory && file.name !== '__MACOSX')
                .map(file => file.name);
            yield Promise.all(files.map(file => {
                const src = path.join(templateFolder, file);
                const dest = path.join(templateRootPath, file);
                return helper_1.fs.move(src, dest, { overwrite: true });
            }));
            yield helper_1.fs.remove(tempPath);
            const res = files.map(name => {
                const creatorFile = path.join(templateRootPath, name, constants_1.TEMPLATE_CREATOR);
                if (!helper_1.fs.existsSync(creatorFile))
                    return { name, value: name };
                const { name: displayName, platforms = '', desc = '', isPrivate = false, compiler } = require(creatorFile);
                if (isPrivate)
                    return null;
                return {
                    name: displayName || name,
                    value: name,
                    platforms,
                    compiler,
                    desc
                };
            }).filter(Boolean);
            return Promise.resolve(res);
        }
        else {
            // 单模板
            yield helper_1.fs.move(templateFolder, path.join(templateRootPath, name), { overwrite: true });
            yield helper_1.fs.remove(tempPath);
            let res = { name, value: name, desc: type === 'url' ? templateSource : '' };
            const creatorFile = path.join(templateRootPath, name, constants_1.TEMPLATE_CREATOR);
            if (helper_1.fs.existsSync(creatorFile)) {
                const { name: displayName, platforms = '', desc = '', compiler } = require(creatorFile);
                res = {
                    name: displayName || name,
                    value: name,
                    platforms,
                    compiler,
                    desc: desc || templateSource
                };
            }
            return Promise.resolve([res]);
        }
    }));
}
exports.default = fetchTemplate;
//# sourceMappingURL=fetchTemplate.js.map