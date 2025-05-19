import Creator from './create/creator';
import Project from './create/project';
import doctor from './doctor';
import { getRootPath } from './util';
import { type ConfigEnv, type UserConfigExport, type UserConfigFn, defineConfig } from './util/defineConfig';
declare const _default: {
    doctor: {
        validators: ((args: any) => any)[];
    };
    Project: typeof Project;
    Creator: typeof Creator;
    defineConfig: typeof defineConfig;
    getRootPath: typeof getRootPath;
};
export default _default;
export { type ConfigEnv, type UserConfigExport, type UserConfigFn, Creator, defineConfig, doctor, getRootPath, Project };
