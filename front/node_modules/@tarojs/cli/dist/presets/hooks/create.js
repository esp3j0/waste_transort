"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const hooks = require("../constant");
exports.default = (ctx) => {
    [
        hooks.MODIFY_CREATE_TEMPLATE,
    ].forEach(methodName => {
        ctx.registerMethod(methodName);
    });
};
//# sourceMappingURL=create.js.map