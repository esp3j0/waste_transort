import chalk from 'chalk';
interface ITerminalLinkOptions {
    target?: 'stdout' | 'stderr';
    fallback?: boolean | ((text: string, url: string) => string);
    [key: string]: unknown;
}
declare function terminalLink(text: string, url: string, { target, fallback }?: ITerminalLinkOptions): string;
declare namespace terminalLink {
    var isSupported: boolean;
    var stderr: typeof terminalLink;
}
export { chalk, terminalLink };
