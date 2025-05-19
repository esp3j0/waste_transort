"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.terminalLink = exports.chalk = void 0;
const ansi_escapes_1 = __importDefault(require("ansi-escapes"));
const chalk_1 = __importDefault(require("chalk"));
exports.chalk = chalk_1.default;
const supports_hyperlinks_1 = __importDefault(require("supports-hyperlinks"));
function terminalLink(text, url, { target = 'stdout', fallback } = {}) {
    if (!supports_hyperlinks_1.default[target]) {
        if (fallback === false)
            return text;
        return typeof fallback === 'function' ? fallback(text, url) : `${text} (\u200B${url}\u200B)`;
    }
    return ansi_escapes_1.default.link(text, url);
}
exports.terminalLink = terminalLink;
terminalLink.isSupported = supports_hyperlinks_1.default.stdout;
terminalLink.stderr = ((text, url, options = {}) => terminalLink(text, url, Object.assign({ target: 'stderr' }, options)));
terminalLink.stderr.isSupported = supports_hyperlinks_1.default.stderr;
//# sourceMappingURL=terminal.js.map