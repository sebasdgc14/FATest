declare module "js-yaml" {
  // Fallback minimal typing for the subset we use
  export function dump(obj: any, opts?: any): string;
  export function load(str: string, opts?: any): any;
  const _default: { dump: typeof dump; load: typeof load };
  export default _default;
}
