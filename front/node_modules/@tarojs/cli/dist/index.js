"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Project = exports.getRootPath = exports.doctor = exports.defineConfig = exports.Creator = void 0;
const creator_1 = require("./create/creator");
exports.Creator = creator_1.default;
const project_1 = require("./create/project");
exports.Project = project_1.default;
const doctor_1 = require("./doctor");
exports.doctor = doctor_1.default;
const util_1 = require("./util");
Object.defineProperty(exports, "getRootPath", { enumerable: true, get: function () { return util_1.getRootPath; } });
const defineConfig_1 = require("./util/defineConfig");
Object.defineProperty(exports, "defineConfig", { enumerable: true, get: function () { return defineConfig_1.defineConfig; } });
exports.default = {
    doctor: doctor_1.default,
    Project: project_1.default,
    Creator: creator_1.default,
    defineConfig: defineConfig_1.defineConfig,
    getRootPath: util_1.getRootPath
};
//# sourceMappingURL=index.js.map