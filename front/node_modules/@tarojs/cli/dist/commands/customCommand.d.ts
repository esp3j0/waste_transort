import { Kernel } from '@tarojs/service';
export default function customCommand(command: string, kernel: Kernel, args: {
    _: string[];
    [key: string]: any;
}): void;
