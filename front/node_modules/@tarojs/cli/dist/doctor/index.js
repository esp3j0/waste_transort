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
const plugin_doctor_1 = require("@tarojs/plugin-doctor");
exports.default = {
    validators: [
        () => {
            return plugin_doctor_1.validateEnv.call(this);
        },
        (args) => {
            return plugin_doctor_1.validateConfig.call(this, args.projectConfig, args.helper);
        },
        (args) => {
            return plugin_doctor_1.validatePackage.call(this, args.appPath, args.nodeModulesPath);
        },
        (args) => {
            return plugin_doctor_1.validateRecommend.call(this, args.appPath);
        },
        (args) => __awaiter(void 0, void 0, void 0, function* () {
            return yield plugin_doctor_1.validateEslint.call(this, args.projectConfig, args.chalk);
        })
    ]
};
//# sourceMappingURL=index.js.map