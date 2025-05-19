export default class CLI {
    appPath: string;
    constructor(appPath: any);
    run(): Promise<void>;
    parseArgs(): Promise<void>;
}
