export default [
    {
        files: ["src/ledger_api/static/**/*.js"],

        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",

            globals: {
                document: "readonly",
                window: "readonly",
                fetch: "readonly"
            }
        },

        rules: {
            "no-undef": "error",
            "no-unused-vars": "error",
            "no-console": "error",
            "no-var": "error",
            "prefer-const": "error",
            "eqeqeq": ["error", "always"]
        }
    }
];