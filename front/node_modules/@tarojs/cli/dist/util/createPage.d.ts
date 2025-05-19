import { ModifyCallback } from '../create/page';
import type { ExportDefaultDeclaration } from '@babel/types';
import type { NodePath } from 'babel__traverse';
export declare const modifyPagesOrSubPackages: (params: {
    path: NodePath<ExportDefaultDeclaration>;
    fullPagePath: string;
    subPkgRootPath?: string;
    callback: ModifyCallback;
}) => void;
