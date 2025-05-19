export declare function escapeRegExp(string: string): string;
/**
 * https://github.com/babel/babel/blob/7acc68a86b70c6aadfef28e10e83d0adb2523807/packages/babel-core/src/config/pattern-to-regex.ts
 *
 * Implement basic pattern matching that will allow users to do the simple
 * tests with * and **. If users want full complex pattern matching, then can
 * always use regex matching, or function validation.
 */
export declare function pathPatternToRegex(pattern: string, dirname: string): RegExp;
