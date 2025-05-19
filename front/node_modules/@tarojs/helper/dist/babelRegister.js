"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.injectDefineConfigHeader = void 0;
/**
 * Inject `defineAppConfig` and `definePageConfig`
 * require header at the top of a config file,
 * without the need to specifically require them
 * if they are used
*/
function injectDefineConfigHeader(babel) {
    const appConfig = 'function defineAppConfig(config) { return config }';
    const pageConfig = 'function definePageConfig(config) { return config }';
    const importNative = "function importNativeComponent(path = '', name = '', exportName = '') { return name }";
    const prependHeader = (nodePath, header) => {
        var _a;
        const parsedHeader = (_a = babel.parse(header, { filename: '' })) === null || _a === void 0 ? void 0 : _a.program.body[0];
        nodePath.node.body.unshift(parsedHeader);
    };
    const enterHandler = (nodePath) => {
        const { scope, node } = nodePath;
        scope.traverse(node, {
            CallExpression(p) {
                const callee = p.node.callee;
                // @ts-ignore
                switch (callee.name) {
                    case 'defineAppConfig':
                        return prependHeader(nodePath, appConfig);
                    case 'definePageConfig':
                        return prependHeader(nodePath, pageConfig);
                    case 'importNativeComponent':
                        return prependHeader(nodePath, importNative);
                    default:
                }
            }
        });
    };
    return {
        visitor: {
            Program: { enter: enterHandler }
        }
    };
}
exports.injectDefineConfigHeader = injectDefineConfigHeader;
//# sourceMappingURL=babelRegister.js.map