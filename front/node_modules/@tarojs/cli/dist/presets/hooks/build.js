"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const hooks = require("../constant");
exports.default = (ctx) => {
    [
        hooks.MODIFY_APP_CONFIG,
        hooks.MODIFY_WEBPACK_CHAIN,
        hooks.MODIFY_VITE_CONFIG,
        hooks.MODIFY_BUILD_ASSETS,
        hooks.MODIFY_MINI_CONFIGS,
        hooks.MODIFY_COMPONENT_CONFIG,
        hooks.ON_COMPILER_MAKE,
        hooks.ON_PARSE_CREATE_ELEMENT,
        hooks.ON_BUILD_START,
        hooks.ON_BUILD_FINISH,
        hooks.ON_BUILD_COMPLETE,
        hooks.MODIFY_RUNNER_OPTS
    ].forEach(methodName => {
        ctx.registerMethod(methodName);
    });
};
//# sourceMappingURL=build.js.map