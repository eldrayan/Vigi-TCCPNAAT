/**
 * Descrição: Configura as regras de análise estática do dashboard React.
 * Autor: Leôncio Ferreira
 */

import js from "@eslint/js";
import babelParser from "@babel/eslint-parser";
import prettier from "eslint-config-prettier";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";

export default [
  { ignores: ["dist", "node_modules"] },
  js.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      parser: babelParser,
      parserOptions: {
        requireConfigFile: false,
        babelOptions: {
          babelrc: false,
          configFile: false,
          presets: [
            ["@babel/preset-react", { runtime: "automatic" }],
            ["@babel/preset-typescript", { allExtensions: true, isTSX: true }],
          ],
        },
      },
      globals: {
        AudioContext: "readonly",
        EventSource: "readonly",
        window: "readonly",
      },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "no-undef": "off",
      "no-unused-vars": "off",
      "react-hooks/set-state-in-effect": "off",
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
    },
  },
  prettier,
];
