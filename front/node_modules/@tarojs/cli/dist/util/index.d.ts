export declare function getRootPath(): string;
export declare function getPkgVersion(): string;
export declare function getPkgItemByKey(key: string): any;
export declare function printPkgVersion(): void;
export declare const getAllFilesInFolder: (folder: string, filter?: string[]) => Promise<string[]>;
export type TemplateSourceType = 'git' | 'url';
export declare function getTemplateSourceType(url: string): TemplateSourceType;
interface FileStat {
    name: string;
    isDirectory: boolean;
    isFile: boolean;
}
export declare function readDirWithFileTypes(folder: string): FileStat[];
export declare function printDevelopmentTip(platform: string): void;
export declare function clearConsole(): void;
export declare function execCommand(params: {
    command: string;
    successCallback?: (data: string) => void;
    failCallback?: (data: string) => void;
}): void;
export declare function getPkgNameByFilterVersion(pkgString: string): string;
export declare function isNil(value: any): value is null | undefined;
export {};
