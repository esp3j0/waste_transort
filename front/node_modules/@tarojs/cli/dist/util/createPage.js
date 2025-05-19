"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.modifyPagesOrSubPackages = void 0;
const helper_1 = require("@tarojs/helper");
const page_1 = require("../create/page");
const t = helper_1.babelKit.types;
const generateNewSubPackageItem = (subPackage) => {
    const pageObject = t.objectProperty(t.identifier('pages'), t.arrayExpression([]));
    const subPkgRootObject = t.objectProperty(t.identifier('root'), t.stringLiteral(subPackage));
    const subPkgItemObject = t.objectExpression([subPkgRootObject, pageObject]);
    return subPkgItemObject;
};
const isValidSubPkgObject = (subPkgObject) => {
    var _a, _b;
    const properties = (subPkgObject === null || subPkgObject === void 0 ? void 0 : subPkgObject.properties) || {};
    const rootProperty = properties.find((property) => { var _a; return ((_a = property.key) === null || _a === void 0 ? void 0 : _a.name) === 'root'; });
    const pagesProperty = properties.find((property) => { var _a; return ((_a = property.key) === null || _a === void 0 ? void 0 : _a.name) === 'pages'; });
    const rootPropertyValueType = (_a = rootProperty === null || rootProperty === void 0 ? void 0 : rootProperty.value) === null || _a === void 0 ? void 0 : _a.type;
    const pagesPropertyValueType = (_b = pagesProperty === null || pagesProperty === void 0 ? void 0 : pagesProperty.value) === null || _b === void 0 ? void 0 : _b.type;
    return rootPropertyValueType === 'StringLiteral' && pagesPropertyValueType === 'ArrayExpression';
};
const addNewSubPackage = (node, page, subPackage) => {
    let subPackages = node === null || node === void 0 ? void 0 : node.properties.find(node => node.key.name === 'subPackages');
    if (!subPackages) {
        // config 文件不存在 subPackages 字段的情况，给该字段赋予默认值
        const subPkgObject = t.objectProperty(t.identifier('subPackages'), t.arrayExpression([]));
        subPackages = subPkgObject;
        node === null || node === void 0 ? void 0 : node.properties.push(subPkgObject);
    }
    const value = subPackages === null || subPackages === void 0 ? void 0 : subPackages.value;
    // 文件格式不对的情况
    if (!value || (value === null || value === void 0 ? void 0 : value.type) !== 'ArrayExpression')
        return page_1.ConfigModificationState.Fail;
    let targetSubPkgObject = value.elements.find(node => { var _a; return (_a = node === null || node === void 0 ? void 0 : node.properties) === null || _a === void 0 ? void 0 : _a.find(property => { var _a; return ((_a = property === null || property === void 0 ? void 0 : property.value) === null || _a === void 0 ? void 0 : _a.value) === subPackage; }); });
    if (!targetSubPkgObject) {
        // 不存在 当前分包配置对象的情况
        const subPkgItemObject = generateNewSubPackageItem(subPackage);
        targetSubPkgObject = subPkgItemObject;
        value.elements.push(subPkgItemObject);
    }
    if (targetSubPkgObject.type !== 'ObjectExpression' || !isValidSubPkgObject(targetSubPkgObject))
        return page_1.ConfigModificationState.Fail;
    const pagesProperty = targetSubPkgObject.properties.find((property) => { var _a; return ((_a = property.key) === null || _a === void 0 ? void 0 : _a.name) === 'pages'; });
    const currentPages = pagesProperty.value.elements;
    const isPageExists = Boolean(currentPages.find(node => node.value === page));
    if (isPageExists)
        return page_1.ConfigModificationState.NeedLess;
    currentPages.push(t.stringLiteral(page));
    return page_1.ConfigModificationState.Success;
};
const addNewPage = (node, page) => {
    const pages = node === null || node === void 0 ? void 0 : node.properties.find(node => node.key.name === 'pages');
    if (!pages)
        return page_1.ConfigModificationState.Fail;
    const value = pages === null || pages === void 0 ? void 0 : pages.value;
    // 仅处理 pages 为数组字面量的情形
    if (!value || (value === null || value === void 0 ? void 0 : value.type) !== 'ArrayExpression')
        return page_1.ConfigModificationState.Fail;
    const isPageExists = Boolean(value.elements.find(node => node.value === page));
    if (isPageExists)
        return page_1.ConfigModificationState.NeedLess;
    const newArrayElement = t.stringLiteral(page);
    value.elements.push(newArrayElement);
    return page_1.ConfigModificationState.Success;
};
const modifyPages = (path, newPageConfig, callback) => {
    let state = page_1.ConfigModificationState.Fail;
    const node = path.node.declaration;
    // Case 1. `export default defineAppConfig({})` 这种情况
    if (node.type === 'CallExpression' && node.callee.name === 'defineAppConfig') {
        const configNode = node.arguments[0];
        state = addNewPage(configNode, newPageConfig.page);
    }
    // Case 2. `export default {}` 这种情况
    if (node.type === 'ObjectExpression') {
        state = addNewPage(node, newPageConfig.page);
    }
    callback(state);
};
const modifySubPackages = (path, newPageConfig, callback) => {
    let state = page_1.ConfigModificationState.Fail;
    const node = path.node.declaration;
    // `export default defineAppConfig({})` 这种情况
    if (node.type === 'CallExpression' && node.callee.name === 'defineAppConfig') {
        const configNode = node.arguments[0];
        state = addNewSubPackage(configNode, newPageConfig.page, newPageConfig.pkg);
    }
    // `export default {}` 这种情况
    if (node.type === 'ObjectExpression') {
        state = addNewSubPackage(node, newPageConfig.page, newPageConfig.pkg);
    }
    callback(state);
};
const generateNewPageConfig = (fullPagePath, subPkgRootPath = '') => {
    const newPageConfig = {
        pkg: '',
        page: ''
    };
    if (subPkgRootPath) {
        const processedSubPkg = `${subPkgRootPath}/`;
        newPageConfig.pkg = processedSubPkg;
        newPageConfig.page = fullPagePath.split(processedSubPkg)[1];
    }
    else {
        newPageConfig.page = fullPagePath;
    }
    return newPageConfig;
};
const modifyPagesOrSubPackages = (params) => {
    const { fullPagePath, subPkgRootPath, callback, path } = params;
    const newPageConfig = generateNewPageConfig(fullPagePath, subPkgRootPath);
    subPkgRootPath
        ? modifySubPackages(path, newPageConfig, callback)
        : modifyPages(path, newPageConfig, callback);
};
exports.modifyPagesOrSubPackages = modifyPagesOrSubPackages;
//# sourceMappingURL=createPage.js.map