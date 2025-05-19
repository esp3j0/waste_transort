"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TaroPlatformWeb = exports.TaroPlatformBase = exports.TaroPlatform = exports.Kernel = exports.Config = void 0;
const Config_1 = require("./Config");
exports.Config = Config_1.default;
const Kernel_1 = require("./Kernel");
exports.Kernel = Kernel_1.default;
const platform_plugin_base_1 = require("./platform-plugin-base");
Object.defineProperty(exports, "TaroPlatform", { enumerable: true, get: function () { return platform_plugin_base_1.TaroPlatform; } });
Object.defineProperty(exports, "TaroPlatformBase", { enumerable: true, get: function () { return platform_plugin_base_1.TaroPlatformBase; } });
Object.defineProperty(exports, "TaroPlatformWeb", { enumerable: true, get: function () { return platform_plugin_base_1.TaroPlatformWeb; } });
__exportStar(require("./utils/types"), exports);
exports.default = { Config: Config_1.default, Kernel: Kernel_1.default, TaroPlatform: platform_plugin_base_1.TaroPlatform, TaroPlatformBase: platform_plugin_base_1.TaroPlatformBase, TaroPlatformWeb: platform_plugin_base_1.TaroPlatformWeb };
//# sourceMappingURL=index.js.map