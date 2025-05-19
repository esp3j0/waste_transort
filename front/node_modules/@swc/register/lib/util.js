"use strict";
var __spreadArrays = (this && this.__spreadArrays) || function () {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.pathPatternToRegex = exports.escapeRegExp = void 0;
var path_1 = __importDefault(require("path"));
function escapeRegExp(string) {
    return string.replace(/[|\\{}()[\]^$+*?.]/g, "\\$&");
}
exports.escapeRegExp = escapeRegExp;
/**
 * Babel <https://babeljs.io/>
 * Released under MIT license <https://github.com/babel/babel/blob/main/LICENSE>
 */
var sep = "\\" + path_1.default.sep;
var endSep = "(?:" + sep + "|$)";
var substitution = "[^" + sep + "]+";
var starPat = "(?:" + substitution + sep + ")";
var starPatLast = "(?:" + substitution + endSep + ")";
var starStarPat = starPat + "*?";
var starStarPatLast = starPat + "*?" + starPatLast + "?";
/**
 * https://github.com/babel/babel/blob/7acc68a86b70c6aadfef28e10e83d0adb2523807/packages/babel-core/src/config/pattern-to-regex.ts
 *
 * Implement basic pattern matching that will allow users to do the simple
 * tests with * and **. If users want full complex pattern matching, then can
 * always use regex matching, or function validation.
 */
function pathPatternToRegex(pattern, dirname) {
    var parts = path_1.default.resolve(dirname, pattern).split(path_1.default.sep);
    return new RegExp(__spreadArrays([
        "^"
    ], parts.map(function (part, i) {
        var last = i === parts.length - 1;
        // ** matches 0 or more path parts.
        if (part === "**")
            return last ? starStarPatLast : starStarPat;
        // * matches 1 path part.
        if (part === "*")
            return last ? starPatLast : starPat;
        // *.ext matches a wildcard with an extension.
        if (part.indexOf("*.") === 0) {
            return (substitution + escapeRegExp(part.slice(1)) + (last ? endSep : sep));
        }
        // Otherwise match the pattern text.
        return escapeRegExp(part) + (last ? endSep : sep);
    })).join(""));
}
exports.pathPatternToRegex = pathPatternToRegex;
