import Creator from './creator';
export interface IPluginConf {
    pluginName: string;
    type: string;
    description?: string;
    projectDir: string;
    projectName: string;
    template: string;
    version: string;
}
export default class Plugin extends Creator {
    conf: IPluginConf;
    constructor(options: IPluginConf);
    getCliVersion(): any;
    create(): Promise<void>;
}
