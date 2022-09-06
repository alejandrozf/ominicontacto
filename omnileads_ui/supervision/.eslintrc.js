/* eslint-disable */

module.exports = {
    root: true,
    env: {
        browser: true,
        jquery: true,
        es6: true,
        node: true
    },
    extends: [
        "@vue/standard",
        "plugin:vue/vue3-essential",
        "eslint:recommended"
    ],
    parserOptions: {
        ecmaVersion: 2018,
        sourceType: "module",
        allowImportExportEverywhere: true,
        parser: "babel-eslint"
    },
    globals: {
        Atomics: "readonly",
        SharedArrayBuffer: "readonly"
    },
    rules: {
        // disable rules from base configurations
        "for-direction": "off",
        "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
        "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
        "standard/no-callback-literal": 0,
        // enable additional rules
        indent: ["error", 4],
        "linebreak-style": ["error", "unix"],
        quotes: ["error", "single", { "allowTemplateLiterals": true }],
        semi: ["error", "always"],
        // override configuration set by extending "eslint:recommended"
        "no-empty": "warn",
        "no-cond-assign": ["error", "always"],
        "no-use-before-define": "warn",
        "spaced-comment": "warn",
        "no-prototype-builtins": "warn",
    },
    overrides: [
        {
            files: [
                "**/__tests__/*.{j,t}s?(x)",
                "**/tests/unit/**/*.spec.{j,t}s?(x)"
            ],
            env: {
                jest: true
            }
        }
    ],
};
