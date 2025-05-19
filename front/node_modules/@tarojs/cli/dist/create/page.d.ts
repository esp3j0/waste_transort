import { CompilerType, CSSType, FrameworkType, NpmType } from '@tarojs/binding';
import Creator from './creator';
export interface IPageConf {
    projectDir: string;
    projectName: string;
    npm: NpmType;
    template: string;
    clone?: boolean;
    templateSource?: string;
    description?: string;
    pageName: string;
    date?: string;
    framework: FrameworkType;
    css: CSSType;
    typescript?: boolean;
    compiler?: CompilerType;
    isCustomTemplate?: boolean;
    customTemplatePath?: string;
    pageDir?: string;
    subPkg?: string;
}
interface IPageArgs extends IPageConf {
    modifyCustomTemplateConfig: TGetCustomTemplate;
    afterCreate?: TAfterCreate;
}
interface ITemplateInfo {
    css: CSSType;
    typescript?: boolean;
    compiler?: CompilerType;
    template?: string;
    templateSource?: string;
    clone?: boolean;
}
type TCustomTemplateInfo = Omit<ITemplateInfo & {
    isCustomTemplate?: boolean;
    customTemplatePath?: string;
}, 'template'>;
export type TSetCustomTemplateConfig = (customTemplateConfig: TCustomTemplateInfo) => void;
type TGetCustomTemplate = (cb: TSetCustomTemplateConfig) => Promise<void>;
type TAfterCreate = (state: boolean) => void;
export declare enum ConfigModificationState {
    Success = 0,
    Fail = 1,
    NeedLess = 2
}
export type ModifyCallback = (state: ConfigModificationState) => void;
export default class Page extends Creator {
    rootPath: string;
    conf: IPageConf;
    private modifyCustomTemplateConfig;
    private afterCreate;
    private pageEntryPath;
    constructor(args: IPageArgs);
    processPageName(): void;
    getPkgPath(): string;
    getPkgTemplateInfo(): any;
    setPageEntryPath(files: string[], handler: any): void;
    setCustomTemplateConfig(customTemplateConfig: TCustomTemplateInfo): void;
    setTemplateConfig(templateInfo: ITemplateInfo): void;
    fetchTemplates(): Promise<void>;
    create(): Promise<void>;
    updateAppConfig(): void;
    write(): void;
}
export type { Page as PageCreator };
