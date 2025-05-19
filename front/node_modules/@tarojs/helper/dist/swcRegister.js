"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function createSwcRegister({ only, plugins }) {
    const config = {
        only: Array.from(new Set([...only])),
        jsc: {
            parser: {
                syntax: 'typescript',
                decorators: true
            },
            transform: {
                legacyDecorator: true
            }
        },
        module: {
            type: 'commonjs'
        }
    };
    if (plugins) {
        config.jsc.experimental = {
            plugins
        };
    }
    require('@swc/register')(config);
}
exports.default = createSwcRegister;
//# sourceMappingURL=swcRegister.js.map