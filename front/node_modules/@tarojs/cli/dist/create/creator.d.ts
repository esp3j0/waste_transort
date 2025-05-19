export default class Creator {
    protected _rootPath: string;
    rootPath: string;
    constructor(sourceRoot?: string);
    init(): void;
    sourceRoot(rootPath?: string): string;
    templatePath(...args: string[]): string;
    write(): void;
}
