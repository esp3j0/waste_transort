interface ICreateSwcRegisterParam {
    only: any;
    plugins?: [string, any][];
}
export default function createSwcRegister({ only, plugins }: ICreateSwcRegisterParam): void;
export {};
