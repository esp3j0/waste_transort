"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function customCommand(command, kernel, args) {
    if (typeof command === 'string') {
        const options = {};
        const excludeKeys = ['_', 'version', 'v', 'help', 'h', 'disable-global-config'];
        Object.keys(args).forEach(key => {
            if (!excludeKeys.includes(key)) {
                options[key] = args[key];
            }
        });
        kernel.run({
            name: command,
            opts: {
                _: args._,
                options,
                isHelp: args.h
            }
        });
    }
}
exports.default = customCommand;
//# sourceMappingURL=customCommand.js.map