export interface ITemplates {
    name: string;
    value: string;
    platforms?: string | string[];
    desc?: string;
    compiler?: string[];
}
export default function fetchTemplate(templateSource: string, templateRootPath: string, clone?: boolean): Promise<ITemplates[]>;
