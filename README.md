# Personal Finance Tracker

A minimalistic web-based personal finance application for tracking cash, card, stock, and cryptocurrency transactions. Built with vanilla HTML, CSS, and JavaScript for simplicity and performance.

## Features

### Transaction Management
- **Cash & Card Transactions**: Track spending and income with date, medium (card/cash), amount, description, and inter-bank transfer flags
- **Stock Transactions**: Record buy/sell orders with symbol, quantity, price, fees, and automatic total calculation
- **Cryptocurrency Transactions**: Monitor crypto trades with coin, quantity, USD price, fees, and total value

### Dashboard & Analytics
- Real-time balance calculations across all accounts
- Time period filtering (custom date ranges)
- Transaction type filtering (cash, cards, stocks, crypto)
- Summary statistics and net worth tracking
- Transaction history with search and sort capabilities

### Management Tools
- Add/edit/remove cards and payment methods
- Customizable stock and crypto symbol lists
- Data export/import functionality (JSON format)
- Bulk transaction operations

## Quick Start

1. **Open the Application**
   ```bash
   # Simply open index.html in your web browser
   open index.html
   # or double-click index.html in your file manager
   ```

2. **Add Your First Transaction**
   - Click "Add Transaction" button
   - Select transaction type (Cash/Card, Stock, or Crypto)
   - Fill in the required fields
   - Click "Save Transaction"

3. **Set Up Your Cards**
   - Go to the Management section
   - Add your credit/debit cards for easy selection
   - Add commonly used stock symbols and crypto coins

## File Structure

```
.
├── index.html          # Main application interface
├── styles.css          # Minimalistic styling
├── app.js              # Core application logic
├── database.js         # Local storage database management
├── SPECS.md            # Technical specifications
└── README.md           # This file
```

## Data Storage

The application uses your browser's local storage to save data. This means:
-  Your data stays private and local to your device
-  No internet connection required
-  Fast performance with no server delays
-  Data is tied to your browser - export regularly for backup

## Usage Examples

### Cash Transaction
- Date: 2024-01-15
- Medium: Cash
- Amount: -45.50 (negative for expense)
- Description: Groceries at local market
- Transfer: No

### Stock Transaction
- Date: 2024-01-15
- Symbol: AAPL
- Quantity: 10
- Price: 150.00
- Type: Buy
- Fees: 2.50
- Total: 1,502.50

### Crypto Transaction
- Date: 2024-01-15
- Coin: BTC
- Quantity: 0.01
- Price: 45000.00
- Type: Buy
- Fees: 5.00
- Total: 455.00

## Filtering & Analysis

### Dashboard Filters
- **Date Range**: Select start and end dates for analysis
- **Transaction Type**: Filter by Cash, Cards, Stocks, or Crypto
- **Text Search**: Find transactions by description or symbol
- **Amount Range**: Filter by transaction amount

### Summary Statistics
- Total Cash/Card Balance
- Stock Portfolio Value
- Cryptocurrency Portfolio Value
- Net Worth Calculation
- Monthly Income vs Expenses

## Data Management

### Export Data
Click "Export Data" to download your transactions as a JSON file for backup or analysis in other tools.

### Import Data
Use "Import Data" to restore from a previously exported JSON file or migrate from another system.

### Backup Recommendations
- Export your data monthly
- Keep backups in multiple locations
- Consider syncing exports to cloud storage

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

Requires modern browser with localStorage support.

## Customization

### Adding New Transaction Types
Edit the data models in `database.js` and add corresponding UI forms in `index.html`.

### Styling Changes
Modify `styles.css` to customize colors, fonts, and layout. The CSS uses variables for easy theme customization.

### New Features
The modular JavaScript architecture makes it easy to add new features. See `SPECS.md` for detailed technical documentation.

## Security & Privacy

- All data is stored locally in your browser
- No data is transmitted to external servers
- No tracking or analytics
- Open source code for full transparency

## Troubleshooting

### Data Not Saving
- Check if your browser allows localStorage
- Clear browser cache and try again
- Export data before clearing browser data

### Performance Issues
- Large transaction lists (>1000 items) may slow down filtering
- Regular data cleanup and archiving recommended
- Use date filters to limit displayed results

## Contributing

This is a personal project, but suggestions and improvements are welcome:

1. Check `SPECS.md` for technical details
2. Test changes thoroughly with sample data
3. Maintain the minimalistic design philosophy
4. Keep dependencies at zero (vanilla JS only)

## License

This project is open source and available for personal use. Modify and distribute as needed for your own financial tracking requirements.

---

**Note**: This application is designed for personal use only. For business accounting or tax reporting, consult with professional accounting software and financial advisors.
