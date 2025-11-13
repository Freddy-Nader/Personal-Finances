// Simple Node.js script to test JavaScript execution
const http = require('http');
const fs = require('fs');

// Simulate browser environment
global.window = {};
global.document = {
    getElementById: () => null,
    addEventListener: () => {},
    createElement: () => ({ addEventListener: () => {} }),
    body: { appendChild: () => {} }
};
global.console = console;

// Test loading the API module
try {
    const apiCode = fs.readFileSync('./frontend/js/api.js', 'utf8');
    console.log('✓ API.js file read successfully');

    // Try to execute the code
    eval(apiCode);
    console.log('✓ API.js executed without syntax errors');

    if (global.window.api) {
        console.log('✓ API instance created successfully');
    } else {
        console.log('✗ API instance not found in global scope');
    }
} catch (error) {
    console.log('✗ Error in API.js:', error.message);
}

// Test components.js
try {
    const componentsCode = fs.readFileSync('./frontend/js/components.js', 'utf8');
    console.log('✓ Components.js file read successfully');

    eval(componentsCode);
    console.log('✓ Components.js executed without syntax errors');

    if (global.window.UIComponents) {
        console.log('✓ UIComponents class available');
    }
} catch (error) {
    console.log('✗ Error in Components.js:', error.message);
}

// Test utils.js
try {
    const utilsCode = fs.readFileSync('./frontend/js/utils.js', 'utf8');
    console.log('✓ Utils.js file read successfully');

    eval(utilsCode);
    console.log('✓ Utils.js executed without syntax errors');

    if (global.window.FinanceUtils) {
        console.log('✓ FinanceUtils class available');
    }
} catch (error) {
    console.log('✗ Error in Utils.js:', error.message);
}

// Test transactions.js
try {
    const transactionsCode = fs.readFileSync('./frontend/js/transactions.js', 'utf8');
    console.log('✓ Transactions.js file read successfully');

    eval(transactionsCode);
    console.log('✓ Transactions.js executed without syntax errors');
} catch (error) {
    console.log('✗ Error in Transactions.js:', error.message);
}