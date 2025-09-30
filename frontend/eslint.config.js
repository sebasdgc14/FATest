import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import prettier from "eslint-config-prettier";
import tseslint from "typescript-eslint";
import { defineConfig, globalIgnores } from "eslint/config";

// Flat config version: instead of a single object with extends, we compose
// multiple config objects in the exported array. Shareable configs referenced
// by string (like "eslint-config-prettier") must be imported explicitly.

export default defineConfig([
  globalIgnores(["dist"]),
  js.configs.recommended,
  // TypeScript base + stylistic rules (flat config export array)
  ...tseslint.configs.recommended,
  reactHooks.configs["recommended-latest"],
  reactRefresh.configs.vite,
  // Prettier last to disable conflicting stylistic rules
  prettier,
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        project: false, // could enable project references later
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      "no-unused-vars": ["error", { varsIgnorePattern: "^[A-Z_]" }],
    },
  },
  {
    files: ["**/*.d.ts"],
    rules: {
      // Declaration files frequently have unused param names just to convey shape
      "no-unused-vars": "off",
    },
  },
]);
