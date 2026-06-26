import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    rules: {
      "react-compiler/react-compiler": "off",
      "react-hooks/set-state-in-effect": "off",
      "react-hooks/purity": "warn",
      "react/no-unescaped-entities": "warn",
      "prefer-const": "warn",
      "@typescript-eslint/no-unused-vars": "warn",
    },
  },
]);

export default eslintConfig;
