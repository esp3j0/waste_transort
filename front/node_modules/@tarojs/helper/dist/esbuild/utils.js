"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.externalEsbuildModule = void 0;
const node_path_1 = require("node:path");
function externalEsbuildModule({ path, namespace, importer, pluginData }) {
    if (namespace === 'file' && importer && path) {
        path = (0, node_path_1.resolve)(importer, path);
    }
    return {
        path,
        namespace,
        pluginData,
        external: true
    };
}
exports.externalEsbuildModule = externalEsbuildModule;
//# sourceMappingURL=utils.js.map