"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.extractCompileEntry = void 0;
const shared_1 = require("@tarojs/shared");
/**
 * 按需编译功能，只编译指定的页面或组件
 * @param appConfig
 * @param args
 */
function extractCompileEntry(appConfig, args, ctx) {
    const { chalk } = ctx.helper;
    const extractType = (0, shared_1.isString)(args.pages) ? 'pages' : (0, shared_1.isString)(args.components) ? 'components' : '';
    if (!extractType)
        return;
    const entries = args[extractType].split(',').map(item => item.trim()).filter(Boolean);
    if (!entries.length) {
        console.log(chalk.yellow(`按需编译开启失败，请指定要编译的${extractType}`));
        return;
    }
    appConfig[extractType] = entries;
    appConfig.subPackages = [];
    console.log(chalk.green(`已开启按需编译，仅编译以下${extractType}: ${appConfig[extractType]}`));
}
exports.extractCompileEntry = extractCompileEntry;
//# sourceMappingURL=appConfig.js.map