/// <reference types="node" />
/// <reference types="node" />
import * as babel from '@babel/core';
import babelGenerator from '@babel/generator';
import * as babelParser from '@babel/parser';
import * as fs from 'fs-extra';
import { processTypeEnum } from './constants';
import type TResolve from 'resolve';
export declare function normalizePath(path: string): string;
export declare const isNodeModule: (filename: string) => boolean;
export declare function isNpmPkg(name: string): boolean;
export declare function isQuickAppPkg(name: string): boolean;
export declare function isAliasPath(name: string, pathAlias?: Record<string, any>): boolean;
export declare function replaceAliasPath(filePath: string, name: string, pathAlias?: Record<string, any>): string;
export declare function promoteRelativePath(fPath: string): string;
export declare function resolveStylePath(p: string): string;
export declare function printLog(type: processTypeEnum, tag: string, filePath?: string): void;
export declare function recursiveFindNodeModules(filePath: string, lastFindPath?: string): string;
export declare function getUserHomeDir(): string;
export declare function getTaroPath(): string;
export declare function getConfig(): Record<string, any>;
export declare function getHash(text: Buffer | string): string;
export declare function getSystemUsername(): string;
export declare function shouldUseYarn(): boolean;
export declare function shouldUseCnpm(): boolean;
export declare function isEmptyObject(obj: any): boolean;
export declare function resolveSync(id: string, opts?: TResolve.SyncOpts & {
    mainFields?: string[];
}): string | null;
export declare function resolveMainFilePath(p: string, extArrs?: string[]): string;
export declare function resolveScriptPath(p: string): string;
export declare function generateEnvList(env: Record<string, any>): Record<string, any>;
/**
 * 获取 npm 文件或者依赖的绝对路径
 *
 * @param {string} 参数 1 - 组件路径
 * @param {string} 参数 2 - 文件扩展名
 * @returns {string} npm 文件绝对路径
 */
export declare function getNpmPackageAbsolutePath(npmPath: string, defaultFile?: string): string | null;
export declare function generateConstantsList(constants: Record<string, any>): Record<string, any>;
export declare function cssImports(content: string): string[];
export declare function emptyDirectory(dirPath: string, opts?: {
    excludes: Array<string | RegExp> | string | RegExp;
}): void;
export declare const pascalCase: (str: string) => string;
export declare function getInstalledNpmPkgPath(pkgName: string, basedir: string): string | null;
export declare function getInstalledNpmPkgVersion(pkgName: string, basedir: string): string | null;
export declare const recursiveMerge: <T = any>(src: Partial<T>, ...args: (Partial<T> | undefined)[]) => any;
export declare const mergeVisitors: (src: any, ...args: any[]) => any;
export declare const applyArrayedVisitors: (obj: any) => any;
export declare const getAllFilesInFolder: (folder: string, filter?: string[]) => Promise<string[]>;
export interface FileStat {
    name: string;
    isDirectory: boolean;
    isFile: boolean;
}
export declare function readDirWithFileTypes(folder: string): FileStat[];
export declare function extnameExpRegOf(filePath: string): RegExp;
export declare function addPlatforms(platform: string): void;
export declare const getModuleDefaultExport: (exports: any) => any;
export declare function removeHeadSlash(str: string): string;
export declare function readPageConfig(configPath: string): any;
interface IReadConfigOptions {
    alias?: Record<string, any>;
    defineConstants?: Record<string, any>;
}
export declare function readConfig<T extends IReadConfigOptions>(configPath: string, options?: T): any;
export declare function removePathPrefix(filePath?: string): string;
export { fs };
export declare const babelKit: {
    types: typeof babel.types;
    parse: typeof babelParser.parse;
    generate: typeof babelGenerator;
    traverse: {
        <S>(parent: babel.types.Node, opts: import("@babel/traverse").TraverseOptions<S>, scope: import("@babel/traverse").Scope | undefined, state: S, parentPath?: babel.NodePath<babel.types.Node> | undefined): void;
        (parent: babel.types.Node, opts?: import("@babel/traverse").TraverseOptions<babel.types.Node> | undefined, scope?: import("@babel/traverse").Scope | undefined, state?: any, parentPath?: babel.NodePath<babel.types.Node> | undefined): void;
        visitors: typeof import("@babel/traverse").visitors;
        verify: typeof import("@babel/traverse").visitors.verify;
        explode: typeof import("@babel/traverse").visitors.explode;
        cheap: (node: babel.types.Node, enter: (node: babel.types.Node) => void) => void;
        node: (node: babel.types.Node, opts: import("@babel/traverse").TraverseOptions<babel.types.Node>, scope?: import("@babel/traverse").Scope | undefined, state?: any, path?: babel.NodePath<babel.types.Node> | undefined, skipKeys?: Record<string, boolean> | undefined) => void;
        clearNode: (node: babel.types.Node, opts?: babel.types.RemovePropertiesOptions | undefined) => void;
        removeProperties: (tree: babel.types.Node, opts?: babel.types.RemovePropertiesOptions | undefined) => babel.types.Node;
        hasType: (tree: babel.types.Node, type: "RestProperty" | "SpreadProperty" | "AnyTypeAnnotation" | "ArgumentPlaceholder" | "ArrayExpression" | "ArrayPattern" | "ArrayTypeAnnotation" | "ArrowFunctionExpression" | "AssignmentExpression" | "AssignmentPattern" | "AwaitExpression" | "BigIntLiteral" | "BinaryExpression" | "BindExpression" | "BlockStatement" | "BooleanLiteral" | "BooleanLiteralTypeAnnotation" | "BooleanTypeAnnotation" | "BreakStatement" | "CallExpression" | "CatchClause" | "ClassAccessorProperty" | "ClassBody" | "ClassDeclaration" | "ClassExpression" | "ClassImplements" | "ClassMethod" | "ClassPrivateMethod" | "ClassPrivateProperty" | "ClassProperty" | "ConditionalExpression" | "ContinueStatement" | "DebuggerStatement" | "DecimalLiteral" | "DeclareClass" | "DeclareExportAllDeclaration" | "DeclareExportDeclaration" | "DeclareFunction" | "DeclareInterface" | "DeclareModule" | "DeclareModuleExports" | "DeclareOpaqueType" | "DeclareTypeAlias" | "DeclareVariable" | "DeclaredPredicate" | "Decorator" | "Directive" | "DirectiveLiteral" | "DoExpression" | "DoWhileStatement" | "EmptyStatement" | "EmptyTypeAnnotation" | "EnumBooleanBody" | "EnumBooleanMember" | "EnumDeclaration" | "EnumDefaultedMember" | "EnumNumberBody" | "EnumNumberMember" | "EnumStringBody" | "EnumStringMember" | "EnumSymbolBody" | "ExistsTypeAnnotation" | "ExportAllDeclaration" | "ExportDefaultDeclaration" | "ExportDefaultSpecifier" | "ExportNamedDeclaration" | "ExportNamespaceSpecifier" | "ExportSpecifier" | "ExpressionStatement" | "File" | "ForInStatement" | "ForOfStatement" | "ForStatement" | "FunctionDeclaration" | "FunctionExpression" | "FunctionTypeAnnotation" | "FunctionTypeParam" | "GenericTypeAnnotation" | "Identifier" | "IfStatement" | "Import" | "ImportAttribute" | "ImportDeclaration" | "ImportDefaultSpecifier" | "ImportExpression" | "ImportNamespaceSpecifier" | "ImportSpecifier" | "IndexedAccessType" | "InferredPredicate" | "InterfaceDeclaration" | "InterfaceExtends" | "InterfaceTypeAnnotation" | "InterpreterDirective" | "IntersectionTypeAnnotation" | "JSXAttribute" | "JSXClosingElement" | "JSXClosingFragment" | "JSXElement" | "JSXEmptyExpression" | "JSXExpressionContainer" | "JSXFragment" | "JSXIdentifier" | "JSXMemberExpression" | "JSXNamespacedName" | "JSXOpeningElement" | "JSXOpeningFragment" | "JSXSpreadAttribute" | "JSXSpreadChild" | "JSXText" | "LabeledStatement" | "LogicalExpression" | "MemberExpression" | "MetaProperty" | "MixedTypeAnnotation" | "ModuleExpression" | "NewExpression" | "Noop" | "NullLiteral" | "NullLiteralTypeAnnotation" | "NullableTypeAnnotation" | "NumberLiteral" | "NumberLiteralTypeAnnotation" | "NumberTypeAnnotation" | "NumericLiteral" | "ObjectExpression" | "ObjectMethod" | "ObjectPattern" | "ObjectProperty" | "ObjectTypeAnnotation" | "ObjectTypeCallProperty" | "ObjectTypeIndexer" | "ObjectTypeInternalSlot" | "ObjectTypeProperty" | "ObjectTypeSpreadProperty" | "OpaqueType" | "OptionalCallExpression" | "OptionalIndexedAccessType" | "OptionalMemberExpression" | "ParenthesizedExpression" | "PipelineBareFunction" | "PipelinePrimaryTopicReference" | "PipelineTopicExpression" | "Placeholder" | "PrivateName" | "Program" | "QualifiedTypeIdentifier" | "RecordExpression" | "RegExpLiteral" | "RegexLiteral" | "RestElement" | "ReturnStatement" | "SequenceExpression" | "SpreadElement" | "StaticBlock" | "StringLiteral" | "StringLiteralTypeAnnotation" | "StringTypeAnnotation" | "Super" | "SwitchCase" | "SwitchStatement" | "SymbolTypeAnnotation" | "TSAnyKeyword" | "TSArrayType" | "TSAsExpression" | "TSBigIntKeyword" | "TSBooleanKeyword" | "TSCallSignatureDeclaration" | "TSConditionalType" | "TSConstructSignatureDeclaration" | "TSConstructorType" | "TSDeclareFunction" | "TSDeclareMethod" | "TSEnumDeclaration" | "TSEnumMember" | "TSExportAssignment" | "TSExpressionWithTypeArguments" | "TSExternalModuleReference" | "TSFunctionType" | "TSImportEqualsDeclaration" | "TSImportType" | "TSIndexSignature" | "TSIndexedAccessType" | "TSInferType" | "TSInstantiationExpression" | "TSInterfaceBody" | "TSInterfaceDeclaration" | "TSIntersectionType" | "TSIntrinsicKeyword" | "TSLiteralType" | "TSMappedType" | "TSMethodSignature" | "TSModuleBlock" | "TSModuleDeclaration" | "TSNamedTupleMember" | "TSNamespaceExportDeclaration" | "TSNeverKeyword" | "TSNonNullExpression" | "TSNullKeyword" | "TSNumberKeyword" | "TSObjectKeyword" | "TSOptionalType" | "TSParameterProperty" | "TSParenthesizedType" | "TSPropertySignature" | "TSQualifiedName" | "TSRestType" | "TSSatisfiesExpression" | "TSStringKeyword" | "TSSymbolKeyword" | "TSThisType" | "TSTupleType" | "TSTypeAliasDeclaration" | "TSTypeAnnotation" | "TSTypeAssertion" | "TSTypeLiteral" | "TSTypeOperator" | "TSTypeParameter" | "TSTypeParameterDeclaration" | "TSTypeParameterInstantiation" | "TSTypePredicate" | "TSTypeQuery" | "TSTypeReference" | "TSUndefinedKeyword" | "TSUnionType" | "TSUnknownKeyword" | "TSVoidKeyword" | "TaggedTemplateExpression" | "TemplateElement" | "TemplateLiteral" | "ThisExpression" | "ThisTypeAnnotation" | "ThrowStatement" | "TopicReference" | "TryStatement" | "TupleExpression" | "TupleTypeAnnotation" | "TypeAlias" | "TypeAnnotation" | "TypeCastExpression" | "TypeParameter" | "TypeParameterDeclaration" | "TypeParameterInstantiation" | "TypeofTypeAnnotation" | "UnaryExpression" | "UnionTypeAnnotation" | "UpdateExpression" | "V8IntrinsicIdentifier" | "VariableDeclaration" | "VariableDeclarator" | "Variance" | "VoidTypeAnnotation" | "WhileStatement" | "WithStatement" | "YieldExpression", denylistTypes?: string[] | undefined) => boolean;
        cache: typeof import("@babel/traverse").cache;
    };
};
