"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.printPkgVersion = exports.getPkgVersion = exports.getRootPath = void 0;
/* eslint-disable no-console */
const path = require("node:path");
function getRootPath() {
    return path.resolve(__dirname, '../../');
}
exports.getRootPath = getRootPath;
function getPkgVersion() {
    return require(path.join(getRootPath(), 'package.json')).version;
}
exports.getPkgVersion = getPkgVersion;
function printPkgVersion() {
    console.log(`👽 Taro v${getPkgVersion()}`);
    console.log();
}
exports.printPkgVersion = printPkgVersion;
//# sourceMappingURL=package.js.map