module.exports = {
    "env": {
        "browser": true,
        // "commonjs": true,
        "jquery": true,
        "es6": true
    },
    "extends": "eslint:recommended",
    "globals": {
        "Atomics": "readonly",
        "ReconnectingWebSocket": "readonly",
        "SharedArrayBuffer": "readonly"
    },
    "parserOptions": {
        "ecmaVersion": 2018,
        "sourceType": "module",
    },
    "rules": {
        "no-console": "off",
        "no-unused-vars": "off",
        "indent": [
            "error",
            4
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "quotes": ["error", "single", { "allowTemplateLiterals": true }],
        "semi": [
            "error",
            "always"
        ],
        "no-prototype-builtins": "warn",
    }
};
