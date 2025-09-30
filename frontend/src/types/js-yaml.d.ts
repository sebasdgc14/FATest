declare module "js-yaml" {
  // Fallback minimal typing for the subset we use
  // Using `unknown` instead of `any` to satisfy linting; callers can narrow.
  export function dump(_obj: unknown, _opts?: unknown): string;
  export function load(_str: string, _opts?: unknown): unknown;
  const _default: { dump: typeof dump; load: typeof load };
  export default _default;
}
