function confirmDelete() {
  const currentLang = document.documentElement.dataset.lang || 'en';
  const msg = currentLang === 'km' ? 'តើអ្នកប្រាកដជាចង់លុបទំនិញនេះមែនទេ?' : 'Are you sure you want to delete this item?';
  return confirm(msg);
}

const root = document.documentElement;
const menu = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
const scrim = document.getElementById('sidebarScrim');
const themeToggle = document.getElementById('themeToggle');

function closeMenu() {
  sidebar?.classList.remove('is-open');
  scrim?.classList.remove('is-open');
  document.body.classList.remove('menu-open');
}
menu?.addEventListener('click', () => {
  sidebar?.classList.add('is-open');
  scrim?.classList.add('is-open');
  document.body.classList.add('menu-open');
});
scrim?.addEventListener('click', closeMenu);
document.querySelector('.sidebar-close')?.addEventListener('click', closeMenu);

function cssColor(name) {
  try {
    return getComputedStyle(root).getPropertyValue(name).trim();
  } catch (e) {
    return '';
  }
}

/* ==========================================================================
   TRANSLATION DICTIONARY (English <-> Khmer / ភាសាខ្មែរ)
   ========================================================================== */
const DICT_EN_TO_KM = {
  // Navigation & Shell
  "Dashboard": "ផ្ទាំងគ្រប់គ្រង",
  "Products": "ផលិតផល",
  "Sales Data": "ទិន្នន័យលក់",
  "Upload XLSX": "បញ្ចូល XLSX",
  "Inventory": "សារពើភ័ណ្ឌ",
  "Demand Forecast": "ការព្យាករណ៍តម្រូវការ",
  "Data Analytics": "វិភាគទិន្នន័យ",
  "Forecast Accuracy": "ភាពសុក្រឹតនៃការព្យាករណ៍",
  "Reports": "របាយការណ៍",
  "Walk-in Orders": "ការបញ្ជាទិញផ្ទាល់",
  "Walk-in Kiosk": "បញ្ជរបញ្ជាទិញរហ័ស",
  "Walk-in Menu": "ម៉ឺនុយហាង",
  "Recent Tickets": "ប័ណ្ណបញ្ជាទិញថ្មីៗ",
  "Admin Dashboard": "ផ្ទាំងគ្រប់គ្រង Admin",
  "All Walk-in Orders": "រាល់ការបញ្ជាទិញផ្ទាល់",
  "Django Admin": "ការគ្រប់គ្រង Django",
  "Sign out": "ចាកចេញ",
  "Sign in": "ចូលគណនី",
  "Create account": "បង្កើតគណនី",
  "Administrator": "អ្នកគ្រប់គ្រង",
  "Customer": "អតិថិជន",
  "Store Staff / Customer": "បុគ្គលិកហាង / អតិថិជន",
  "Walk-in Guest": "ភ្ញៀវទូទៅ",
  "Self-Service Mode": "របៀបស្វ័យសេវា",
  "Staff Login": "បុគ្គលិកចូលប្រើ",
  "Staff Sign in": "បុគ្គលិកចូលប្រើ",
  "COUNTER SERVICE": "សេវាបញ្ជរ",
  "MANAGEMENT": "ការគ្រប់គ្រង",
  "OPS": "ប្រតិបត្តិការ",
  "WALK-IN POS": "បញ្ជរលក់រហ័ស",
  "Operational data center": "មជ្ឈមណ្ឌលទិន្នន័យប្រតិបត្តិការ",
  "Run forecast": "ដំណើរការការព្យាករណ៍",
  "Upload sales": "បញ្ចូលទិន្នន័យលក់",
  "Cadence Walk-in Express": "Cadence បញ្ជាទិញរហ័ស",
  "Fast Table & Takeaway Counter Ordering": "ការបញ្ជាទិញរហ័សលើតុ និងខ្ចប់",
  "Active": "សកម្ម",
  "Order Ticket": "ប័ណ្ណបញ្ជាទិញ",
  "Ticket is empty": "ប័ណ្ណបញ្ជាទិញទទេ",
  "Tap items to add.": "ចុចលើមុខទំនិញដើម្បីបន្ថែម។",
  "Complete Order": "បញ្ជាក់ការបញ្ជាទិញ",
  "Complete Order •": "បញ្ជាក់ការបញ្ជាទិញ •",
  "Place Order": "បញ្ជាក់ការបញ្ជាទិញ",
  "Cart is empty": "កន្ត្រកទទេ",
  "Select items from the menu.": "សូមជ្រើសរើសមុខទំនិញពីម៉ឺនុយ។",
  "Browse Menu": "ស្វែងរកម៉ឺនុយ",
  "Order Summary": "សង្ខេបការបញ្ជាទិញ",
  "Ticket Items": "មុខទំនិញក្នុងប័ណ្ណ",
  "Sales Trend & Forecast": "និន្នាការលក់ & ការព្យាករណ៍",
  "All Products Forecast": "ការព្យាករណ៍ផលិតផលទាំងអស់",
  "Actual vs Predicted": "ជាក់ស្តែង ធៀបនឹង ការព្យាករណ៍",
  "Test Details": "ព័ត៌មានលម្អិតនៃការធ្វើតេស្ត",
  "Sales History": "ប្រវត្តិការលក់",
  "Inventory Optimization": "ការបង្កើនប្រសិទ្ធភាពស្តុក",
  "Demand Statistics": "ស្ថិតិតម្រូវការ",
  "ABC Analysis": "ការវិភាគ ABC",
  "Trends": "និន្នាការ",
  "Product Deep-Dive": "ការវិភាគស៊ីជម្រៅលើផលិតផល",
  "Top 70% revenue": "ចំណូល 70% ខ្ពស់បំផុត",
  "Price vs Units": "តម្លៃ និងបរិមាណ",
  "Monthly Demand & Revenue": "តម្រូវការ & ចំណូលប្រចាំខែ",
  "Category Revenue": "ចំណូលតាមប្រភេទ",
  "Average Baseline MAE": "MAE មូលដ្ឋានជាមធ្យម",
  "Baseline MAE": "MAE មូលដ្ឋាន",
  "Average MAE": "MAE ជាមធ្យម",
  "Average Accuracy": "ភាពសុក្រឹតជាមធ្យម",
  "Search products...": "ស្វែងរកផលិតផល...",
  "Search inventory...": "ស្វែងរកសារពើភ័ណ្ឌ...",
  "Open Kiosk": "បើកបញ្ជរ Kiosk",
  "Select a product to view forecast and trajectory.": "ជ្រើសរើសផលិតផលដើម្បីមើលការព្យាករណ៍ និងនិន្នាការ។",
  "Switch color theme": "ប្តូរពណ៌ផ្ទៃ",
  "Switch to light mode": "ប្តូរទៅផ្ទៃភ្លឺ",
  "Switch to dark mode": "ប្តូរទៅផ្ទៃងងឹត",
  "Switch language": "ប្តូរភាសា",

  // Walk-in POS Kiosk & Order Ticket
  "Search artisan drinks, food, bakery...": "ស្វែងរកភេសជ្ជៈ អាហារ នំប៉័ង...",
  "Items Available": "មុខទំនិញមានក្នុងស្តុក",
  "All Items": "មុខទំនិញទាំងអស់",
  "Walk-in Order Ticket": "ប័ណ្ណបញ្ជាទិញផ្ទាល់",
  "Counter Terminal #01": "បញ្ជរបញ្ជាទិញ #01",
  "Clear Ticket": "សម្អាតប័ណ្ណ",
  "Dine In": "ញ៉ាំនៅទីនេះ",
  "DINE IN": "ញ៉ាំនៅទីនេះ",
  "Takeaway": "ខ្ចប់ទៅក្រៅ",
  "TAKEAWAY": "ខ្ចប់ទៅក្រៅ",
  "Customer Name": "ឈ្មោះអតិថិជន",
  "Guest Name": "ឈ្មោះភ្ញៀវ",
  "Guest / Customer Name": "ឈ្មោះភ្ញៀវ / អតិថិជន",
  "Table No.": "លេខតុ",
  "Table / Buzzer #": "លេខតុ / ប៊ីសឺរ #",
  "Table or Buzzer # (optional)": "លេខតុ ឬ ប៊ីសឺរ # (មិនបង្ខំ)",
  "Table": "តុ",
  "Optional": "មិនបង្ខំ",
  "(Optional)": "(មិនបង្ខំ)",
  "e.g. Table 4": "ឧទាហរណ៍ តុលេខ 4",
  "e.g. T-04": "ឧទាហរណ៍ T-04",
  "e.g. John Doe": "ឧទាហរណ៍ សុខា",
  "Quick Table": "តុរហ័ស",
  "Counter": "បញ្ជរ",
  "Terminal": "ម៉ាស៊ីនឆូតកាត",
  "PAYMENT METHOD": "វិធីសាស្ត្រទូទាត់",
  "Payment Method": "វិធីសាស្ត្រទូទាត់",
  "Cash": "សាច់ប្រាក់",
  "Cash at Counter": "សាច់ប្រាក់នៅបញ្ជរ",
  "Bakong KHQR": "បាគង KHQR",
  "Mobile Pay": "ទូទាត់តាមទូរស័ព្ទ",
  "Card": "កាតធនាគារ",
  "Scan QR": "ស្កេន QR",
  "Items count": "ចំនួនមុខទំនិញ",
  "Subtotal": "សរុបរង",
  "Tax & Service": "ពន្ធ & សេវាកម្ម",
  "Tax (0%)": "ពន្ធ (0%)",
  "Included": "រួមបញ្ចូលរួច",
  "Total Due": "ទឹកប្រាក់ត្រូវបង់",
  "Total Amount": "ចំនួនទឹកប្រាក់សរុប",
  "TOTAL PAID": "ប្រាក់បានទូទាត់សរុប",
  "Total Paid": "ប្រាក់បានទូទាត់សរុប",
  "Complete Walk-in Order": "បញ្ជាក់ការបញ្ជាទិញ",
  "Complete Walk-in Order •": "បញ្ជាក់ការបញ្ជាទិញ •",
  "Select Items to Order": "ជ្រើសរើសទំនិញដើម្បីបញ្ជាទិញ",
  "Order Placed": "ការបញ្ជាទិញបានជោគជ័យ",
  "Digital Receipt": "វិក្កយបត្រឌីជីថល",
  "Ready for next order": "ត្រៀមខ្លួនសម្រាប់ការបញ្ជាទិញបន្ទាប់",
  "in ticket": "ក្នុងប័ណ្ណ",
  "Cash (Counter)": "សាច់ប្រាក់ (បញ្ជរ)",
  "Card (Terminal)": "កាតធនាគារ (ម៉ាស៊ីន)",
  "Scan QR (Mobile Pay)": "ស្កេន QR (ទូរស័ព្ទ)",
  "Takeaway (No Table)": "ខ្ចប់ទៅក្រៅ (មិនត្រូវការតុ)",
  "Clear Ticket": "សម្អាតប័ណ្ណ",
  "Please present your ticket number at pickup counter or table.": "សូមបង្ហាញលេខប័ណ្ណរបស់អ្នកនៅបញ្ជរទទួលទំនិញ ឬនៅតុ។",
  "Place Walk-in Order": "បញ្ជាក់ការបញ្ជាទិញ",
  "Finalize Walk-in Order": "បញ្ចប់ការបញ្ជាទិញផ្ទាល់",
  "Confirm dining option, customer details, and payment method.": "បញ្ជាក់ជម្រើសទទួលទាន ព័ត៌មានអតិថិជន និងវិធីសាស្ត្រទូទាត់។",
  "Add": "បន្ថែម",
  "Sold Out": "អស់ពីស្តុក",
  "Out of Stock": "អស់ពីស្តុក",
  "In Stock": "មានក្នុងស្តុក",
  "in stock": "មានក្នុងស្តុក",
  "Only": "នៅសល់តែ",
  "left": "",
  "No menu items found": "រកមិនឃើញមុខទំនិញទេ",
  "Reset Filters": "កំណត់តម្រងឡើងវិញ",
  "Order ticket is empty": "ប័ណ្ណបញ្ជាទិញទទេ",
  "Tap menu items on the left to start building this walk-in order.": "ចុចលើមុខទំនិញនៅខាងឆ្វេងដើម្បីចាប់ផ្តើមការបញ្ជាទិញ។",
  "Tap any menu item to begin": "ចុចលើមុខទំនិញដើម្បីចាប់ផ្តើម",
  "Clear the current walk-in order ticket?": "តើអ្នកពិតជាចង់សម្អាតប័ណ្ណបញ្ជាទិញនេះមែនទេ?",
  "Cadence Café & Eatery": "Cadence ហាងកាហ្វេ & អាហារ",
  "Express Walk-in Counter Service": "សេវាបញ្ជរបញ្ជាទិញរហ័ស",
  "WALK-IN TICKET": "ប័ណ្ណបញ្ជាទិញផ្ទាល់",
  "WALK-IN ORDER TICKET": "ប័ណ្ណបញ្ជាទិញផ្ទាល់",
  "Ticket #": "ប័ណ្ណលេខ #",
  "Ticket": "ប័ណ្ណ",
  "Order Type": "ប្រភេទបញ្ជាទិញ",
  "Date & Time": "កាលបរិច្ឆេទ & ម៉ោង",
  "Date/Time:": "កាលបរិច្ឆេទ/ម៉ោង:",
  "Date:": "កាលបរិច្ឆេទ:",
  "Guest:": "ភ្ញៀវ:",
  "Customer:": "អតិថិជន:",
  "Cashier:": "អ្នកគិតលុយ:",
  "Payment:": "ការទូទាត់:",
  "Payment": "ការទូទាត់",
  "Just now": "ទើបតែឥឡូវនេះ",
  "Items Ordered": "មុខទំនិញដែលបានកុម្ម៉ង់",
  "ITEM DESCRIPTION": "មុខទំនិញ / ការពិពណ៌នា",
  "TOTAL PAID": "បានទូទាត់សរុប",
  "Amount Tendered": "សាច់ប្រាក់ទទួលបាន",
  "Change Due": "ប្រាក់អាប់",
  "Free Wi-Fi": "Wi-Fi ឥតគិតថ្លៃ",
  "Cash Payment": "ទូទាត់ជាសាច់ប្រាក់",
  "Scan to Pay": "ស្កេនដើម្បីទូទាត់",
  "Scan with Bakong or any Mobile Banking app": "ស្កេនជាមួយកម្មវិធីបាគង ឬធនាគារណាមួយ",
  "Awaiting payment scan...": "កំពុងរង់ចាំការស្កេនទូទាត់...",
  "Order Received & Sent to Kitchen!": "ការបញ្ជាទិញទទួលបាន & បញ្ជូនទៅចង្ក្រានបាយ!",
  "Please present your ticket number at the pickup counter or table.": "សូមបង្ហាញលេខប័ណ្ណរបស់អ្នកនៅបញ្ជរទទួលទំនិញ ឬនៅតុ។",
  "Thank you for visiting Cadence Café!": "សូមអរគុណសម្រាប់ការគាំទ្រ Cadence Café!",
  "Please retain this receipt for table service or order pickup.": "សូមរក្សាទុកវិក្កយបត្រនេះសម្រាប់សេវាកម្មនៅតុ ឬទទួលទំនិញ។",
  "Print Ticket": "បោះពុម្ពវិក្កយបត្រ",
  "Next Order": "ការបញ្ជាទិញបន្ទាប់",
  "Order Completed!": "ការបញ្ជាទិញបានជោគជ័យ!",
  "Recent Walk-in Tickets": "ប័ណ្ណបញ្ជាទិញថ្មីៗ",
  "Recent Walk-in Tickets · Cadence Express": "ប័ណ្ណបញ្ជាទិញថ្មីៗ · Cadence Express",
  "Review receipts and tickets placed at the walk-in counter or kiosk.": "ពិនិត្យមើលបង្កាន់ដៃ និងប័ណ្ណបញ្ជាទិញនៅបញ្ជរ ឬ Kiosk។",
  "Back to Walk-in Menu": "ត្រឡប់ទៅម៉ឺនុយហាង",
  "Back to Menu": "ត្រឡប់ទៅម៉ឺនុយ",
  "Browse Walk-in Menu": "ស្វែងរកម៉ឺនុយហាង",
  "Order Total": "សរុបការបញ្ជាទិញ",
  "Order Options": "ជម្រើសនៃការបញ្ជាទិញ",
  "Dining Option": "ជម្រើសទទួលទាន",
  "Order Summary": "សង្ខេបការបញ្ជាទិញ",
  "Nothing to check out yet": "មិនទាន់មានអ្វីត្រូវគិតប្រាក់ទេ",
  "Add food or beverage items from the walk-in menu first.": "សូមបន្ថែមមុខទំនិញអាហារ ឬភេសជ្ជៈពីម៉ឺនុយហាងជាមុនសិន។",
  "Counter Activity": "សកម្មភាពបញ្ជរ",
  "Walk-in Menu & POS Kiosk": "ម៉ឺនុយហាង & បញ្ជរបញ្ជាទិញរហ័ស",
  "Walk-in Menu & POS Kiosk · Cadence Express": "ម៉ឺនុយហាង & បញ្ជរបញ្ជាទិញរហ័ស · Cadence Express",
  "Current Order Items": "មុខទំនិញក្នុងប័ណ្ណបច្ចុប្បន្ន",
  "Review items before finalizing this walk-in order.": "ពិនិត្យមុខទំនិញឡើងវិញមុនពេលបញ្ចប់ការបញ្ជាទិញ។",
  "Order Ticket Items": "មុខទំនិញក្នុងប័ណ្ណ",
  "Clear all items?": "តើអ្នកចង់សម្អាតគ្រប់មុខទំនិញទាំងអស់មែនទេ?",
  "Walk-in Order Cart": "កន្ត្រកបញ្ជាទិញផ្ទាល់",
  "item": "មុខទំនិញ",
  "items": "មុខទំនិញ",
  "each": "ក្នុងមួយមុខ",

  // Categories
  "Beverages": "ភេសជ្ជៈ",
  "Food": "អាហារ",
  "Coffee": "កាហ្វេ",
  "Hot Coffee": "កាហ្វេក្តៅ",
  "Iced Coffee": "កាហ្វេទឹកកក",
  "Cold Brew": "កាហ្វេ Cold Brew",
  "Tea & Matcha": "តែ & ម៉ាត់ឆា",
  "Pastries & Bakery": "នំ & នំប៉័ង",
  "Bakery": "នំប៉័ង",
  "Snacks": "អាហារសម្រន់",
  "Snacks & Sides": "អាហារសម្រន់",
  "Special": "ពិសេស",
  "General": "ទូទៅ",
  "Uncategorized": "មិនមានប្រភេទ",

  // Dashboard & Metrics
  "Inventory Forecasting": "ការព្យាករណ៍ស្តុកទំនិញ",
  "Operations overview": "ទិដ្ឋភាពទូទៅនៃប្រតិបត្តិការ",
  "Monitor sales velocity, inventory coverage, and demand risk.": "តាមដានល្បឿននៃការលក់ កម្រិតស្តុក និងហានិភ័យតម្រូវការ។",
  "Total products": "ផលិតផលសរុប",
  "Active catalog": "កាតាឡុកសកម្ម",
  "Unit sales": "ចំនួនលក់សរុប",
  "Units sold": "ចំនួនលក់",
  "Units Sold": "ចំនួនលក់",
  "Units": "ឯកតា",
  "Unit Price": "តម្លៃក្នុងមួយឯកតា",
  "Historical volume": "បរិមាណលក់កន្លងមក",
  "Revenue": "ចំណូល",
  "Revenue ($)": "ចំណូល ($)",
  "Total Revenue": "ចំណូលសរុប",
  "Total revenue": "ចំណូលសរុប",
  "Total Volume": "បរិមាណសរុប",
  "Total units sold": "ចំនួនឯកតាលក់សរុប",
  "Recorded sales": "ការលក់ដែលបានកត់ត្រា",
  "Current inventory": "ស្តុកបច្ចុប្បន្ន",
  "Current Stock": "ស្តុកបច្ចុប្បន្ន",
  "Units on hand": "ទំនិញក្នុងដៃ",
  "On hand": "ក្នុងដៃ",
  "30d demand": "តម្រូវការ 30 ថ្ងៃ",
  "Predicted demand": "តម្រូវការប៉ាន់ស្មាន",
  "Predicted": "ការព្យាករណ៍",
  "Actual": "ជាក់ស្តែង",
  "Difference": "ភាពខុសគ្នា",
  "Next forecast month": "ខែព្យាករណ៍បន្ទាប់",
  "Low stock / reorder": "ស្តុកទាប / ត្រូវកុម្ម៉ង់ថែម",
  "Low stock": "ស្តុកទាប",
  "Low Stock": "ស្តុកទាប",
  "Reorder": "កុម្ម៉ង់ថែម",
  "Reorder qty": "ចំនួនត្រូវកុម្ម៉ង់",
  "Reorder Qty": "ចំនួនត្រូវកុម្ម៉ង់ថែម",
  "Needs attention": "ត្រូវការយកចិត្តទុកដាក់",
  "Need Reorder": "ត្រូវការកុម្ម៉ង់ថែម",
  "Monthly sales trend": "និន្នាការនៃការលក់ប្រចាំខែ",
  "Monthly Demand & Revenue Trend": "និន្នាការតម្រូវការ & ចំណូលប្រចាំខែ",
  "Monthly sales": "ការលក់ប្រចាំខែ",
  "Units sold over time": "ចំនួនលក់តាមពេលវេលា",
  "Live data": "ទិន្នន័យផ្ទាល់",
  "Stock vs demand": "ស្តុក ធៀបនឹង តម្រូវការ",
  "Coverage by product": "កម្រិតគ្របដណ្តប់តាមផលិតផល",
  "Inventory attention": "សារពើភ័ណ្ឌដែលត្រូវតាមដាន",
  "Products requiring an inventory decision": "ផលិតផលដែលត្រូវការការសម្រេចចិត្តលើស្តុក",
  "View all": "មើលទាំងអស់",
  "View": "មើល",
  "Product": "ផលិតផល",
  "Status": "ស្ថានភាព",
  "All statuses": "គ្រប់ស្ថានភាពទាំងអស់",
  "All products": "គ្រប់ផលិតផលទាំងអស់",
  "All categories": "គ្រប់ប្រភេទទាំងអស់",
  "All products have sufficient stock.": "គ្រប់ផលិតផលទាំងអស់មានស្តុកគ្រប់គ្រាន់។",
  "Sufficient Stock": "ស្តុកគ្រប់គ្រាន់",
  "No forecasts yet. Generate one to compare demand.": "មិនទាន់មានការព្យាករណ៍ទេ។ សូមបង្កើតដើម្បីប្រៀបធៀបតម្រូវការ។",
  "Stock": "ស្តុក",
  "Demand": "តម្រូវការ",

  // Products & Forms
  "Products Catalog": "កាតាឡុកផលិតផល",
  "Manage catalog items, product images, pricing, and reorder thresholds.": "គ្រប់គ្រងទំនិញក្នុងកាតាឡុក រូបភាព តម្លៃ និងកម្រិតស្តុកត្រូវកុម្ម៉ង់ថែម។",
  "Add Product": "បន្ថែមផលិតផល",
  "Search product name or category...": "ស្វែងរកឈ្មោះផលិតផល ឬប្រភេទ...",
  "Search": "ស្វែងរក",
  "Clear": "សម្អាត",
  "Image": "រូបភាព",
  "Product Name": "ឈ្មោះផលិតផល",
  "Category": "ប្រភេទ",
  "Price": "តម្លៃ",
  "Price:": "តម្លៃ:",
  "Reorder Level": "កម្រិតត្រូវកុម្ម៉ង់ថែម",
  "Reorder Level:": "កម្រិតត្រូវកុម្ម៉ង់ថែម:",
  "Action": "សកម្មភាព",
  "Actions": "សកម្មភាព",
  "Edit": "កែប្រែ",
  "Delete": "លុប",
  "View stock & analytics →": "មើលស្តុក & ការវិភាគ →",
  "Cost": "ថ្លៃដើម",
  "Safety stock": "ស្តុកសុវត្ថិភាព",
  "Safety Stock": "ស្តុកសុវត្ថិភាព",
  "Safety Stock (95%)": "ស្តុកសុវត្ថិភាព (95%)",
  "Lead time": "រយៈពេលដឹកជញ្ជូន",
  "Lead time (days)": "រយៈពេលដឹកជញ្ជូន (ថ្ងៃ)",
  "Save": "រក្សាទុក",
  "Save changes": "រក្សាទុកការកែប្រែ",
  "Cancel": "បោះបង់",
  "Back": "ថយក្រោយ",
  "Upload": "បញ្ចូលឯកសារ",
  "Filter": "តម្រង",
  "Reset": "កំណត់ឡើងវិញ",

  // Inventory & Analytics & Forecast
  "Inventory Management": "ការគ្រប់គ្រងសារពើភ័ណ្ឌ",
  "Stock Status": "ស្ថានភាពស្តុក",
  "Days of Inventory": "ចំនួនថ្ងៃស្តុក",
  "Days Sales Inv (DSI)": "ចំនួនថ្ងៃស្តុក (DSI)",
  "Inventory Turnover": "អត្រាបង្វិលស្តុក",
  "Reorder Required": "ត្រូវកុម្ម៉ង់ថែម",
  "Adequate": "គ្រប់គ្រាន់",
  "Low": "ទាប",
  "Normal": "ធម្មតា",
  "Surplus": "លើសស្តុក",
  "Upload Sales Data": "បញ្ចូលទិន្នន័យលក់",
  "Historical Sales Data": "ទិន្នន័យលក់កន្លងមក",
  "Sales records": "កំណត់ត្រាលក់",
  "Download Sample": "ទាញយកគំរូ",
  "Forecast Horizon": "រយៈពេលព្យាករណ៍",
  "Select month": "ជ្រើសរើសខែ",
  "Run Forecast": "ដំណើរការការព្យាករណ៍",
  "Generate Forecast": "បង្កើតការព្យាករណ៍",
  "Method": "វិធីសាស្ត្រ",
  "Moving Average": "មធ្យមភាគចល័ត",
  "Exponential Smoothing": "Exponential Smoothing",
  "Linear Regression": "Linear Regression",
  "Accuracy": "ភាពសុក្រឹត",
  "MAE": "MAE (កម្រិតលម្អៀងមធ្យម)",
  "MAPE": "MAPE (ភាគរយលម្អៀង)",
  "RMSE": "RMSE",
  "Average accuracy (100 - MAPE)": "ភាពសុក្រឹតជាមធ្យម (100 - MAPE)",
  "Average MAE (units)": "MAE ជាមធ្យម (ឯកតា)",
  "Average baseline MAE": "MAE មូលដ្ឋានជាមធ្យម",
  "Best seller": "លក់ដាច់បំផុត",
  "Best-selling products": "ផលិតផលលក់ដាច់បំផុត",
  "Top 5 Revenue Drivers": "ផលិតផលរកចំណូលបានច្រើនបំផុត 5",
  "Category Revenue Breakdown": "ការបែងចែកចំណូលតាមប្រភេទ",
  "Choose product": "ជ្រើសរើសផលិតផល",
  "Select Product:": "ជ្រើសរើសផលិតផល:",
  "Class A": "ប្រភេទ A",
  "Class B": "ប្រភេទ B",
  "Class C": "ប្រភេទ C",
  "Class A (≤70%)": "ប្រភេទ A (≤70%)",
  "Class B (70-90%)": "ប្រភេទ B (70-90%)",
  "Class C (>90%)": "ប្រភេទ C (>90%)",
  "Drive top 70% of total revenue": "ជំរុញចំណូល 70% នៃចំណូលសរុប",
  "ABC Pareto Analysis": "ការវិភាគ ABC Pareto",
  "ABC Class A Focus": "ការផ្តោតលើទំនិញប្រភេទ A នៃ ABC",
  "Cumulative Revenue (%)": "ចំណូលបង្គរ (%)",
  "Demand Volatility": "ភាពប្រែប្រួលនៃតម្រូវការ",
  "Descriptive Demand Statistics (Summary Table)": "ស្ថិតិតម្រូវការពិពណ៌នា (តារាងសង្ខេប)",
  "Operations Research & Prescriptive Inventory Parameters": "ការស្រាវជ្រាវប្រតិបត្តិការ & ប៉ារ៉ាម៉ែត្រស្តុកណែនាំ",
  "Product Deep-Dive & Ordinary Least Squares (OLS) Regression": "វិភាគស៊ីជម្រៅលើផលិតផល & OLS Regression",
  "Product Performance Report": "របាយការណ៍លទ្ធផលផលិតផល",
  "Product Sales Volume": "បរិមាណលក់ផលិតផល",
  "Export CSV": "ទាញយក CSV",
  "Export Excel": "ទាញយក Excel",
  "Full Statistical Report": "របាយការណ៍ស្ថិតិពេញលេញ",
  "Sales Report": "របាយការណ៍លក់",
  "Inventory Report": "របាយការណ៍សារពើភ័ណ្ឌ",
  "Demand Forecast Report": "របាយការណ៍ការព្យាករណ៍តម្រូវការ",
  "Reorder Report": "របាយការណ៍កុម្ម៉ង់ទំនិញ",
  "Revenue Report": "របាយការណ៍ចំណូល",
  "Loading ABC analysis...": "កំពុងដំណើរការវិភាគ ABC...",
  "Loading prescriptive data...": "កំពុងដំណើរការទិន្នន័យណែនាំ...",
  "Loading statistics...": "កំពុងដំណើរការស្ថិតិ...",
  "Recommended ROP": "កម្រិត ROP ណែនាំ",
  "EOQ (Batch Size)": "EOQ (ទំហំបាច់)",
  "EOQ:": "EOQ:",
  "Price Elasticity": "ភាពបត់បែននៃតម្លៃ",
  "Upload History": "ប្រវត្តិនៃការបញ្ចូលឯកសារ",
  "Upload & Clean Data": "បញ្ចូល & សម្អាតទិន្នន័យ",
  "Sales XLSX file:": "ឯកសារ Excel ទិន្នន័យលក់:",
  "Year": "ឆ្នាំ",
  "Month": "ខែ",
  "Details": "ព័ត៌មានលម្អិត",
  "Date": "កាលបរិច្ឆេទ",
  "Quantity": "បរិមាណ",
  "Quantity Sold": "បរិមាណលក់",
  "Qty": "ចំនួន",

  // Auth & General
  "Sign in to manage inventory and demand forecasts.": "ចូលគណនីដើម្បីគ្រប់គ្រងស្តុក និងការព្យាករណ៍តម្រូវការ។",
  "Welcome back": "សូមស្វាគមន៍ការត្រឡប់មកវិញ",
  "Secure workspace": "កន្លែងធ្វើការសុវត្ថិភាព",
  "Create your account": "បង្កើតគណនីរបស់អ្នក",
  "Sign up with your username, email and a password.": "ចុះឈ្មោះជាមួយឈ្មោះអ្នកប្រើ អ៊ីមែល និងពាក្យសម្ងាត់។",
  "New account": "គណនីថ្មី",
  "Already have an account?": "មានគណនីរួចហើយ?",
  "New here?": "ទើបតែមកកាន់ទីនេះ?",
  "Access denied": "ការចូលប្រើត្រូវបានបដិសេធ",
  "Sign out and use an admin account": "ចាកចេញ ហើយប្រើគណនី Admin",
  "Return to sign in": "ត្រឡប់ទៅទំព័រចូលគណនី",
  "Your account is active, but an administrator must grant you workspace access before you can view it.": "គណនីរបស់អ្នកសកម្ម ប៉ុន្តែអ្នកគ្រប់គ្រងត្រូវតែផ្តល់សិទ្ធិចូលប្រើកន្លែងការងារមុនពេលអ្នកអាចមើលវាបាន។",
  "This workspace is limited to administrators.": "កន្លែងការងារនេះត្រូវបានកំណត់សម្រាប់តែអ្នកគ្រប់គ្រងប៉ុណ្ណោះ។",
  "Username:": "ឈ្មោះអ្នកប្រើ:",
  "Username": "ឈ្មោះអ្នកប្រើ",
  "Password:": "ពាក្យសម្ងាត់:",
  "Password": "ពាក្យសម្ងាត់",
  "Password confirmation:": "បញ្ជាក់ពាក្យសម្ងាត់:",
  "Email address:": "អាសយដ្ឋានអ៊ីមែល:",
  "Email:": "អ៊ីមែល:",
  "Email": "អ៊ីមែល",
  "Order History": "ប្រវត្តិនៃការបញ្ជាទិញ",
  "Order Details": "ព័ត៌មានលម្អិតនៃការបញ្ជាទិញ",
  "Total": "សរុប",
  "Order #": "ការបញ្ជាទិញ #",
  "Completed": "បានបញ្ចប់",
  "Pending": "កំពុងរង់ចាំ",
  "Processing": "កំពុងដំណើរការ",
  "Cancelled": "បានបោះបង់",

  // Missing action, inventory & catalog terms
  "Confirm Delete": "បញ្ជាក់ការលុប",
  "Save Product": "រក្សាទុកផលិតផល",
  "Back to Products": "ត្រឡប់ទៅផលិតផល",
  "Back to inventory": "ត្រឡប់ទៅសារពើភ័ណ្ឌ",
  "Back to Menu": "ត្រឡប់ទៅម៉ឺនុយ",
  "Back to Walk-in Menu": "ត្រឡប់ទៅម៉ឺនុយកម្ម៉ង់",
  "Product Image": "រូបភាពផលិតផល",
  "Out of stock (0)": "អស់ពីស្តុក (0)",
  "Update stock": "ធ្វើបច្ចុប្បន្នភាពស្តុក",
  "Current stock:": "ស្តុកបច្ចុប្បន្ន:",
  "Current Stock:": "ស្តុកបច្ចុប្បន្ន:",
  "Unit Price:": "តម្លៃឯកតា:",
  "Status:": "ស្ថានភាព:",
  "Stock:": "ស្តុក:",
  "Stock (update)": "ស្តុក (កែប្រែ)",
  "Suggested reorder:": "ការកុម្ម៉ង់ណែនាំ:",
  "Recommended Reorder Qty": "ចំនួនកុម្ម៉ង់ណែនាំ",
  "Reorder Level Threshold": "កម្រិតត្រូវកុម្ម៉ង់ថែម",
  "Forecast results (all products)": "លទ្ធផលការព្យាករណ៍ (គ្រប់ផលិតផល)",
  "Forecast month": "ខែការព្យាករណ៍",
  "Test period detail": "ព័ត៌មានលម្អិតនៃរយៈពេលសាកល្បង",
  "Train / Test months": "ខែបង្វឹក / ខែសាកល្បង",
  "Historical sales, trend line and forecast": "ការលក់កន្លងមក ខ្សែនិន្នាការ និងការព្យាករណ៍",
  "Last 12 months of sales": "ការលក់ក្នុងរយៈពេល 12 ខែចុងក្រោយ",
  "Total revenue": "ចំណូលសរុប",
  "Total units sold": "ចំនួនឯកតាលក់សរុប",
  "Walk-in Customer Orders": "ការបញ្ជាទិញរបស់អតិថិជនផ្ទាល់",
  "Walk-in Ticket": "ប័ណ្ណកម្ម៉ង់ផ្ទាល់",
  "Finalize Walk-in Order": "បញ្ចប់ការបញ្ជាទិញផ្ទាល់",
  "Order Total Due": "ទឹកប្រាក់ត្រូវទូទាត់សរុប",
  "Order Ticket Items": "មុខទំនិញក្នុងប័ណ្ណកម្ម៉ង់",
  "Your order ticket is empty": "ប័ណ្ណកម្ម៉ង់របស់អ្នកទទេ",
  "Add More Items": "បន្ថែមមុខទំនិញ",
  "Proceed to Complete Order": "បន្តដើម្បីបញ្ចប់ការបញ្ជាទិញ",
  "Clear Ticket": "សម្អាតប័ណ្ណ",
  "Recent uploads": "ឯកសារដែលបានបញ្ចូលថ្មីៗ",
  "No data for this report yet.": "មិនទាន់មានទិន្នន័យសម្រាប់របាយការណ៍នេះទេ។",
  "No uploads yet.": "មិនទាន់មានការបញ្ចូលឯកសារនៅឡើយទេ។",
  "No sales records.": "មិនទាន់មានកំណត់ត្រាលក់នៅឡើយទេ។",
  "No products match.": "គ្មានផលិតផលដែលត្រូវគ្នានោះទេ។",
  "No recent walk-in tickets yet": "មិនទាន់មានប័ណ្ណកម្ម៉ង់ថ្មីៗនៅឡើយទេ",
  "No walk-in customer orders yet. Open the walk-in kiosk storefront to place an order.": "មិនទាន់មានការបញ្ជាទិញនៅឡើយទេ។ សូមបើកផ្ទាំងកម្ម៉ង់ផ្ទាល់ដើម្បីបញ្ជាទិញ។",
  "Not enough data. Each product needs at least 4 months of sales history.": "មិនមានទិន្នន័យគ្រប់គ្រាន់។ ផលិតផលនីមួយៗត្រូវការប្រវត្តិនៃការលក់យ៉ាងហោចណាស់ 4 ខែ។",
  "Are you sure you want to delete": "តើអ្នកប្រាកដជាចង់លុប",
  "This also permanently deletes all of its sales history and forecasts.": "វានឹងលុបប្រវត្តិនៃការលក់ និងការព្យាករណ៍ទាំងអស់របស់វាជាអចិន្ត្រៃយ៍ផងដែរ។",
  "Configure product catalog details, stock thresholds, and display image.": "កំណត់ព័ត៌មានលម្អិតនៃកាតាឡុកផលិតផល កម្រិតស្តុក និងរូបភាពបង្ហាញ។",
  "Add your first product": "បន្ថែមផលិតផលដំបូងរបស់អ្នក",
  "Alerts when stock drops below this.": "ជូនដំណឹងនៅពេលស្តុកធ្លាក់ចុះក្រោមចំណុចនេះ។",
  "Across all historical sales": "នៅទូទាំងការលក់កន្លងមកទាំងអស់",
  "Units delivered": "ឯកតាដែលបានលក់ចេញ",
  "Gross sales value ($)": "តម្លៃលក់សរុប ($)",
  "File": "ឯកសារ",
  "Imported": "បានបញ្ចូល",
  "Rejected": "បានបដិសេធ",
  "From date": "ចាប់ពីថ្ងៃ",
  "To date": "ដល់ថ្ងៃ",
  "Records": "កំណត់ត្រា",
  "Checkout": "ទូទាត់ប្រាក់",
  "Dining Option": "ជម្រើសទទួលទាន",
  "Fast Table & Takeaway Counter Ordering": "ការបញ្ជាទិញនៅតុ & វេចខ្ចប់រហ័ស",
  "Counter POS #01": "បញ្ជរបង់ប្រាក់ #01",
  "Artisan Coffee Roasters • Fresh Bakery": "កាហ្វេប្រណិត • នំបុ័ងស្រស់",
  "Free Wi-Fi:": "Wi-Fi ឥតគិតថ្លៃ:",
  "Tax / VAT (10% Included)": "ពន្ធ / អាករលើតម្លៃបន្ថែម (រួមបញ្ចូល 10%)",
  "AMOUNT": "ចំនួនទឹកប្រាក់",
  "Create an account": "បង្កើតគណនី",
  "Close": "បិទ",

  // Upload and Data Processing
  "Columns:": "ជួរឈរ:",
  "(optional:": "(មិនបង្ខំ:",
  ").": ")។",
  "Optional:": "មិនបង្ខំ:",
  "Partial": "មួយផ្នែក",
  "Only .xlsx files are supported.": "គាំទ្រតែឯកសារ .xlsx ប៉ុណ្ណោះ។",
  "File must be 10 MB or smaller.": "ឯកសារត្រូវតែមានទំហំ 10 MB ឬតូចជាងនេះ។",
  "The file could not be read. Please upload a valid .xlsx workbook.": "មិនអាចអានឯកសារបានទេ។ សូមបញ្ចូលសៀវភៅការងារ .xlsx ដែលត្រឹមត្រូវ។",
  "No new valid rows to import.": "គ្មានជួរទិន្នន័យត្រឹមត្រូវថ្មីសម្រាប់បញ្ចូលទេ។",
  "No new valid rows to import": "គ្មានជួរទិន្នន័យត្រឹមត្រូវថ្មីសម្រាប់បញ្ចូលទេ",

  // Analytics Volatility & Statistical Profiling
  "Stable": "ស្ថិរភាព",
  "Moderate": "មធ្យម",
  "Erratic": "មិនទៀងទាត់",
  "STABLE": "ស្ថិរភាព",
  "MODERATE": "មធ្យម",
  "ERRATIC": "មិនទៀងទាត់",
  "Mean (μ)": "មធ្យមភាគ (μ)",
  "Mean (&mu;)": "មធ្យមភាគ (μ)",
  "Mean": "មធ្យមភាគ",
  "MEAN (Μ)": "មធ្យមភាគ (μ)",
  "MEAN (M)": "មធ្យមភាគ (μ)",
  "Median": "មេដ្យាន",
  "MEDIAN": "មេដ្យាន",
  "Std Dev (σ)": "គម្លាតស្តង់ដារ (σ)",
  "Std Dev (&sigma;)": "គម្លាតស្តង់ដារ (σ)",
  "Std Dev": "គម្លាតស្តង់ដារ",
  "Std Dev:": "គម្លាតស្តង់ដារ:",
  "STD DEV (Σ)": "គម្លាតស្តង់ដារ (σ)",
  "Variance (σ²)": "វ៉ារ្យង់ (σ²)",
  "Variance (&sigma;&sup2;)": "វ៉ារ្យង់ (σ²)",
  "Variance": "វ៉ារ្យង់",
  "VARIANCE (Σ²)": "វ៉ារ្យង់ (σ²)",
  "Skewness": "កម្រិតទ្រេត (Skewness)",
  "SKEWNESS": "កម្រិតទ្រេត (Skewness)",
  "Min - Max": "ទាបបំផុត - ខ្ពស់បំផុត",
  "MIN - MAX": "ទាបបំផុត - ខ្ពស់បំផុត",
  "CV (σ/μ)": "CV (σ/μ)",
  "CV (&sigma;/&mu;)": "CV (σ/μ)",
  "CV (Σ/Μ)": "CV (σ/μ)",
  "CV (Σ/M)": "CV (σ/μ)",
  "Priority Class": "លំដាប់អាទិភាព",
  "Revenue Share (%)": "ចំណែកចំណូល (%)",
  "Management Policy": "គោលការណ៍គ្រប់គ្រង",
  "Tight control, weekly review, low safety stock": "ការគ្រប់គ្រងតឹងរ៉ឹង ត្រួតពិនិត្យប្រចាំសប្តាហ៍ ស្តុកសុវត្ថិភាពទាប",
  "Moderate control, periodic review": "ការគ្រប់គ្រងកម្រិតមធ្យម ត្រួតពិនិត្យតាមកាលកំណត់",
  "Bulk order, relaxed controls, minimal monitoring": "ការបញ្ជាទិញច្រើន ត្រួតពិនិត្យធូររលុង តាមដានតិចតួច",
  "Regression Formula": "រូបមន្តតំរែតំរង់ (Regression)",
  "R² (Variance Explained)": "R² (កម្រិតពន្យល់វ៉ារ្យង់)",
  "Standard Error (S_e)": "កំហុសស្តង់ដារ (S_e)",
  "95% Confidence Interval": "ចន្លោះជឿជាក់ 95%",
  "Demand Mean:": "មធ្យមភាគតម្រូវការ:",
  "Product Sales Volume": "បរិមាណលក់តាមផលិតផល",
  "Price Sensitive (Elastic: Higher price reduces volume)": "ប្រែប្រួលតាមតម្លៃ (តម្លៃខ្ពស់កាត់បន្ថយបរិមាណលក់)",
  "Inelastic / Premium demand pattern": "មិនប្រែប្រួលតាមតម្លៃ / តម្រូវការទំនិញកម្រិតខ្ពស់",
  "Relatively Inelastic / Stable across prices": "មិនសូវប្រែប្រួល / មានស្ថិរភាពតាមកម្រិតតម្លៃ",
  "Insufficient data": "ទិន្នន័យមិនគ្រប់គ្រាន់",
  "Insufficient Data": "ទិន្នន័យមិនគ្រប់គ្រាន់",
  "Neutral": "អព្យាក្រឹត",
  "Price Sensitivity": "ភាពប្រែប្រួលតាមតម្លៃ",
  "Stable Demand": "តម្រូវការមានស្ថិរភាព",
  "Price Sensitive": "ប្រែប្រួលតាមតម្លៃ",
  "Premium Demand": "តម្រូវការកម្រិតខ្ពស់",
  "Price changes do not affect sales volume": "ការផ្លាស់ប្តូរតម្លៃមិនប៉ះពាល់ដល់ការលក់",
  "Higher prices reduce sales volume": "តម្លៃឡើងខ្ពស់កាត់បន្ថយការលក់",
  "Sales remain strong at higher prices": "ការលក់នៅតែខ្លាំងទោះបីតម្លៃឡើងខ្ពស់",
  "More sales history needed to analyze": "ត្រូវការទិន្នន័យប្រវត្តិបន្ថែមដើម្បីវិភាគ",
  "Price impact on demand": "ឥទ្ធិពលតម្លៃលើតម្រូវការ",
  "Score": "ពិន្ទុ",
  "Sales Growth": "កំណើននៃការលក់",
  "Growing": "កំពុងកើនឡើង",
  "Steady": "មានស្ថិរភាព",
  "Declining": "កំពុងថយចុះ",
  "MoM": "ធៀបនឹងខែមុន",
  "Month-over-month trend": "និន្នាការធៀបនឹងខែមុន",
  "Baseline month (no prior period)": "ខែគោលដំបូង (គ្មានទិន្នន័យខែមុន)",
  "revenue vs last month": "ចំណូលធៀបនឹងខែមុន",
  "units": "ឯកតា",
  "days": "ថ្ងៃ",
  "yr": "ឆ្នាំ",

  // Page Titles
  "Dashboard · Cadence": "ផ្ទាំងគ្រប់គ្រង · Cadence",
  "Products · Cadence": "ផលិតផល · Cadence",
  "Sales Data · Cadence": "ទិន្នន័យលក់ · Cadence",
  "Inventory · Cadence": "សារពើភ័ណ្ឌ · Cadence",
  "Demand Forecast · Cadence": "ការព្យាករណ៍តម្រូវការ · Cadence",
  "Forecast Accuracy · Cadence": "ភាពសុក្រឹតនៃការព្យាករណ៍ · Cadence",
  "Data Analytics & Statistical Insights · Cadence": "ការវិភាគទិន្នន័យ & ស្ថិតិ · Cadence",
  "Upload Sales · Cadence": "បញ្ចូលទិន្នន័យលក់ · Cadence",
  "Sales Report · Cadence": "របាយការណ៍លក់ · Cadence",
  "Sign in · Cadence": "ចូលគណនី · Cadence",
  "Create account · Cadence": "បង្កើតគណនី · Cadence",
  "Access denied · Cadence": "ការចូលប្រើត្រូវបានបដិសេធ · Cadence"
};

// Reverse dictionary for English restoration
const DICT_KM_TO_EN = {};
for (const [en, km] of Object.entries(DICT_EN_TO_KM)) {
  DICT_KM_TO_EN[km] = en;
}

// Global translate helper
window.t = function(str) {
  const currentLang = root.dataset.lang || 'en';
  if (currentLang === 'km' && DICT_EN_TO_KM[str]) {
    return DICT_EN_TO_KM[str];
  }
  return str;
};

function translateSampleDetails(sample) {
  return sample
    .replace(/\brow\s+(\d+):/gi, 'ជួរ $1:')
    .replace(/invalid or missing date/gi, 'កាលបរិច្ឆេទមិនត្រឹមត្រូវ ឬបាត់')
    .replace(/missing product name/gi, 'បាត់ឈ្មោះផលិតផល')
    .replace(/invalid or missing quantity/gi, 'បរិមាណមិនត្រឹមត្រូវ ឬបាត់')
    .replace(/negative quantity/gi, 'បរិមាណអវិជ្ជមាន')
    .replace(/invalid or missing price/gi, 'តម្លៃមិនត្រឹមត្រូវ ឬបាត់')
    .replace(/negative price/gi, 'តម្លៃអវិជ្ជមាន')
    .replace(/;\s*\.\.\.\s*and\s+(\d+)\s+more/gi, '; ... និង $1 ទៀត');
}

function restoreSampleDetails(sample) {
  return sample
    .replace(/ជួរ\s+(\d+):/g, 'row $1:')
    .replace(/កាលបរិច្ឆេទមិនត្រឹមត្រូវ ឬបាត់/g, 'invalid or missing date')
    .replace(/បាត់ឈ្មោះផលិតផល/g, 'missing product name')
    .replace(/បរិមាណមិនត្រឹមត្រូវ ឬបាត់/g, 'invalid or missing quantity')
    .replace(/បរិមាណអវិជ្ជមាន/g, 'negative quantity')
    .replace(/តម្លៃមិនត្រឹមត្រូវ ឬបាត់/g, 'invalid or missing price')
    .replace(/តម្លៃអវិជ្ជមាន/g, 'negative price')
    .replace(/;\s*\.\.\.\s*និង\s+(\d+)\s+ទៀត/g, '; ... and $1 more');
}

function translateUploadMessage(text, lang) {
  if (!text) return null;
  if (lang === 'km') {
    if (!/(?:No new valid rows|duplicate rows|clean rows|invalid rows|could not be read|required columns|\binvalid\b)/i.test(text)) {
      return null;
    }
    let res = text;
    res = res.replace(/No new valid rows to import\.?/gi, 'គ្មានជួរទិន្នន័យត្រឹមត្រូវថ្មីសម្រាប់បញ្ចូលទេ។');
    res = res.replace(/Imported\s+(\d+)\s+clean\s+rows\.?/gi, 'បានបញ្ចូលទិន្នន័យត្រឹមត្រូវ $1 ជួរ។');
    res = res.replace(/Skipped\s+(\d+)\s+duplicate\s+rows\s+in\s+the\s+file\s+and\s+(\d+)\s+already\s+in\s+the\s+database\.?/gi,
      'បានរំលងទិន្នន័យស្ទួនក្នុងឯកសារ $1 ជួរ និងមានក្នុងមូលដ្ឋានទិន្នន័យរួចហើយ $2 ជួរ។');
    res = res.replace(/(?:Skipped\s+(\d+)\s+duplicate\s+rows|\b(\d+)\s+duplicate\s+rows\s+skipped)\.?/gi, (m, p1, p2) => {
      const count = p1 || p2;
      return 'បានរំលងទិន្នន័យស្ទួន ' + count + ' ជួរ។';
    });
    res = res.replace(/Rejected\s+(\d+)\s+invalid\s+rows(?:\s*\((.*?)\))?\.?/gi, (m, count, sample) => {
      if (sample) {
        return 'បានបដិសេធ ' + count + ' ជួរមិនត្រឹមត្រូវ (' + translateSampleDetails(sample) + ')។';
      }
      return 'បានបដិសេធ ' + count + ' ជួរមិនត្រឹមត្រូវ។';
    });
    res = res.replace(/\b(\d+)\s+invalid(?:\s*\((.*?)\))?\.?/gi, (m, count, sample) => {
      if (sample) {
        return count + ' ជួរមិនត្រឹមត្រូវ (' + translateSampleDetails(sample) + ')។';
      }
      return count + ' ជួរមិនត្រឹមត្រូវ។';
    });
    res = res.replace(/The file could not be read\. Please upload a valid \.xlsx workbook\.?/gi,
      'មិនអាចអានឯកសារបានទេ។ សូមបញ្ចូលសៀវភៅការងារ .xlsx ដែលត្រឹមត្រូវ។');
    res = res.replace(/Missing required columns:\s*(.*?)\.\s*Required:\s*(.*?)\.?/gi,
      'ខ្វះជួរឈរដែលត្រូវការ: $1។ ត្រូវការ: $2។');
    res = res.replace(/([។])\s+/g, '$1 ').trim();
    return res;
  } else {
    if (!/(?:គ្មានជួរទិន្នន័យត្រឹមត្រូវ|បានបញ្ចូលទិន្នន័យត្រឹមត្រូវ|បានរំលងទិន្នន័យស្ទួន|បានបដិសេធ|មិនអាចអានឯកសារបានទេ|ខ្វះជួរឈរដែលត្រូវការ)/.test(text)) {
      return null;
    }
    let res = text;
    res = res.replace(/គ្មានជួរទិន្នន័យត្រឹមត្រូវថ្មីសម្រាប់បញ្ចូលទេ។/g, 'No new valid rows to import.');
    res = res.replace(/បានបញ្ចូលទិន្នន័យត្រឹមត្រូវ\s+(\d+)\s+ជួរ។/g, 'Imported $1 clean rows.');
    res = res.replace(/បានរំលងទិន្នន័យស្ទួនក្នុងឯកសារ\s+(\d+)\s+ជួរ\s+និងមានក្នុងមូលដ្ឋានទិន្នន័យរួចហើយ\s+(\d+)\s+ជួរ។/g,
      'Skipped $1 duplicate rows in the file and $2 already in the database.');
    res = res.replace(/បានរំលងទិន្នន័យស្ទួន\s+(\d+)\s+ជួរ។/g, '$1 duplicate rows skipped.');
    res = res.replace(/បានបដិសេធ\s+(\d+)\s+ជួរមិនត្រឹមត្រូវ(?:\s*\((.*?)\))?។/g, (m, count, sample) => {
      return 'Rejected ' + count + ' invalid rows' + (sample ? ' (' + restoreSampleDetails(sample) + ')' : '') + '.';
    });
    res = res.replace(/(\d+)\s+ជួរមិនត្រឹមត្រូវ(?:\s*\((.*?)\))?។/g, (m, count, sample) => {
      return count + ' invalid' + (sample ? ' (' + restoreSampleDetails(sample) + ')' : '') + '.';
    });
    res = res.replace(/មិនអាចអានឯកសារបានទេ។ សូមបញ្ចូលសៀវភៅការងារ \.xlsx ដែលត្រឹមត្រូវ។/g,
      'The file could not be read. Please upload a valid .xlsx workbook.');
    res = res.replace(/ខ្វះជួរឈរដែលត្រូវការ:\s*(.*?)។\s*ត្រូវការ:\s*(.*?)។/g,
      'Missing required columns: $1. Required: $2.');
    return res.trim();
  }
}

// Translate individual text string with dictionary and dynamic pattern support
function translateText(str, targetLang) {
  if (!str) return str;
  const raw = str;
  const trimmed = raw.trim();
  if (!trimmed) return raw;

  if (targetLang === 'km') {
    // 1. Exact match
    if (DICT_EN_TO_KM[trimmed]) {
      return raw.replace(trimmed, DICT_EN_TO_KM[trimmed]);
    }

    // 2. Match with unescaped HTML entities
    const unescaped = trimmed.replace(/&amp;/g, '&');
    if (DICT_EN_TO_KM[unescaped]) {
      return raw.replace(trimmed, DICT_EN_TO_KM[unescaped]);
    }

    // 3. Dynamic upload messages
    const uploadKm = translateUploadMessage(trimmed, 'km');
    if (uploadKm) {
      return raw.replace(trimmed, uploadKm);
    }

    // 4. Pattern: "X in stock"
    let m = trimmed.match(/^(\d+)\s+in\s+stock$/i);
    if (m) return raw.replace(trimmed, `${m[1]} មានក្នុងស្តុក`);

    // 5. Pattern: "Only X left"
    m = trimmed.match(/^Only\s+(\d+)\s+left$/i);
    if (m) return raw.replace(trimmed, `នៅសល់តែ ${m[1]}`);

    // 6. Pattern: "X items" / "X item"
    m = trimmed.match(/^(\d+)\s+items?$/i);
    if (m) return raw.replace(trimmed, `${m[1]} មុខទំនិញ`);

    // 7. Pattern: "X Items Available"
    m = trimmed.match(/^(\d+)\s+items\s+available$/i);
    if (m) return raw.replace(trimmed, `${m[1]} មុខទំនិញមានក្នុងស្តុក`);

    // 8. Pattern: "$X.XX each"
    m = trimmed.match(/^(\$[\d.,]+)\s+each$/i);
    if (m) return raw.replace(trimmed, `${m[1]} ក្នុងមួយមុខ`);

    // 9. Pattern: "Complete Walk-in Order • $X.XX"
    m = trimmed.match(/^Complete\s+Walk-in\s+Order\s*•\s*(.*)$/i);
    if (m) return raw.replace(trimmed, `បញ្ជាក់ការបញ្ជាទិញ • ${m[1]}`);

    // 10. Pattern: "X in ticket"
    m = trimmed.match(/^(\d+)\s+in\s+ticket$/i);
    if (m) return raw.replace(trimmed, `${m[1]} ក្នុងប័ណ្ណ`);

    // 11. Pattern: "X units"
    m = trimmed.match(/^([\d.]+)\s+units$/i);
    if (m) return raw.replace(trimmed, `${m[1]} ឯកតា`);

    // 12. Pattern: "Xx / yr"
    m = trimmed.match(/^([\d.]+)x\s*\/\s*yr$/i);
    if (m) return raw.replace(trimmed, `${m[1]}x / ឆ្នាំ`);

    // 13. Pattern: "X days"
    m = trimmed.match(/^([\d.]+)\s+days$/i);
    if (m) return raw.replace(trimmed, `${m[1]} ថ្ងៃ`);

    return raw;
  } else {
    // Reverting to English
    if (DICT_KM_TO_EN[trimmed]) {
      return raw.replace(trimmed, DICT_KM_TO_EN[trimmed]);
    }

    const uploadEn = translateUploadMessage(trimmed, 'en');
    if (uploadEn) {
      return raw.replace(trimmed, uploadEn);
    }

    let m = trimmed.match(/^(\d+)\s+មានក្នុងស្តុក$/);
    if (m) return raw.replace(trimmed, `${m[1]} in stock`);

    m = trimmed.match(/^នៅសល់តែ\s+(\d+)$/);
    if (m) return raw.replace(trimmed, `Only ${m[1]} left`);

    m = trimmed.match(/^(\d+)\s+មុខទំនិញ$/);
    if (m) return raw.replace(trimmed, `${m[1]} items`);

    m = trimmed.match(/^(\d+)\s+មុខទំនិញមានក្នុងស្តុក$/);
    if (m) return raw.replace(trimmed, `${m[1]} Items Available`);

    m = trimmed.match(/^(\$[\d.,]+)\s+ក្នុងមួយមុខ$/);
    if (m) return raw.replace(trimmed, `${m[1]} each`);

    m = trimmed.match(/^បញ្ជាក់ការបញ្ជាទិញ\s*•\s*(.*)$/);
    if (m) return raw.replace(trimmed, `Complete Walk-in Order • ${m[1]}`);

    m = trimmed.match(/^(\d+)\s+ក្នុងប័ណ្ណ$/);
    if (m) return raw.replace(trimmed, `${m[1]} in ticket`);

    m = trimmed.match(/^([\d.]+)\s+ឯកតា$/);
    if (m) return raw.replace(trimmed, `${m[1]} units`);

    m = trimmed.match(/^([\d.]+)x\s*\/\s*ឆ្នាំ$/);
    if (m) return raw.replace(trimmed, `${m[1]}x / yr`);

    m = trimmed.match(/^([\d.]+)\s+ថ្ងៃ$/);
    if (m) return raw.replace(trimmed, `${m[1]} days`);

    return raw;
  }
}

let isTranslating = false;

// DOM translation walker
function translateSubtree(rootNode, lang) {
  if (!rootNode) return;
  isTranslating = true;

  try {
    const walker = document.createTreeWalker(rootNode, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const p = node.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        const tag = p.tagName.toLowerCase();
        if (['script', 'style', 'code', 'pre', 'noscript'].includes(tag)) return NodeFilter.FILTER_REJECT;
        if (p.closest('[data-no-translate]') || p.closest('.lang-switch-group')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });

    let node = walker.nextNode();
    while (node) {
      if (lang === 'en') {
        if (node._origEn !== undefined) {
          node.nodeValue = node._origEn;
        } else {
          node.nodeValue = translateText(node.nodeValue, 'en');
        }
      } else {
        if (node._origEn === undefined) {
          node._origEn = node.nodeValue;
        }
        node.nodeValue = translateText(node.nodeValue, 'km');
      }
      node = walker.nextNode();
    }

    // Placeholders & Titles
    if (rootNode.querySelectorAll) {
      rootNode.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
        if (lang === 'en') {
          if (el.dataset.origPlaceholder !== undefined) el.placeholder = el.dataset.origPlaceholder;
          else el.placeholder = translateText(el.placeholder, 'en');
        } else {
          if (el.dataset.origPlaceholder === undefined) el.dataset.origPlaceholder = el.placeholder;
          el.placeholder = translateText(el.placeholder, 'km');
        }
      });

      rootNode.querySelectorAll('[title]').forEach(el => {
        if (el.closest('.lang-switch-group')) return;
        if (lang === 'en') {
          if (el.dataset.origTitle !== undefined) el.title = el.dataset.origTitle;
          else el.title = translateText(el.title, 'en');
        } else {
          if (el.dataset.origTitle === undefined) el.dataset.origTitle = el.title;
          el.title = translateText(el.title, 'km');
        }
      });

      rootNode.querySelectorAll('[aria-label]').forEach(el => {
        if (el.closest('.lang-switch-group') || el.id === 'themeToggle') return;
        if (lang === 'en') {
          if (el.dataset.origAriaLabel !== undefined) el.setAttribute('aria-label', el.dataset.origAriaLabel);
          else el.setAttribute('aria-label', translateText(el.getAttribute('aria-label'), 'en'));
        } else {
          if (el.dataset.origAriaLabel === undefined) el.dataset.origAriaLabel = el.getAttribute('aria-label');
          el.setAttribute('aria-label', translateText(el.getAttribute('aria-label'), 'km'));
        }
      });
    }
  } finally {
    isTranslating = false;
  }
}

function applyChartTheme() {
  if (!window.Chart) return;
  try {
    const fontFamily = "'Roboto', 'Kantumruy Pro', sans-serif";
    const muted = cssColor('--muted') || '#8796aa';
    const grid = cssColor('--chart-grid') || 'rgba(148,163,184,.1)';
    const surface = cssColor('--tooltip-bg') || cssColor('--tooltip') || '#0f172a';
    const tooltipTitle = cssColor('--tooltip-title') || '#ffffff';
    const tooltipBody = cssColor('--tooltip-body') || '#e2e8f0';
    const tooltipBorder = cssColor('--tooltip-border') || 'rgba(255,255,255,.14)';

    Chart.defaults.color = muted;
    Chart.defaults.borderColor = grid;
    Chart.defaults.font.family = fontFamily;
    if (!Chart.defaults.plugins) Chart.defaults.plugins = {};
    if (!Chart.defaults.plugins.tooltip) Chart.defaults.plugins.tooltip = {};
    Chart.defaults.plugins.tooltip.backgroundColor = surface;
    Chart.defaults.plugins.tooltip.titleColor = tooltipTitle;
    Chart.defaults.plugins.tooltip.bodyColor = tooltipBody;
    Chart.defaults.plugins.tooltip.borderColor = tooltipBorder;
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.titleFont = { family: fontFamily, size: 13, weight: '600' };
    Chart.defaults.plugins.tooltip.bodyFont = { family: fontFamily, size: 12, weight: '400' };

    Object.values(Chart.instances || {}).forEach(chart => {
      try {
        if (!chart.options.plugins) chart.options.plugins = {};
        if (!chart.options.plugins.tooltip) chart.options.plugins.tooltip = {};
        chart.options.plugins.tooltip.backgroundColor = surface;
        chart.options.plugins.tooltip.titleColor = tooltipTitle;
        chart.options.plugins.tooltip.bodyColor = tooltipBody;
        chart.options.plugins.tooltip.borderColor = tooltipBorder;
        chart.options.plugins.tooltip.borderWidth = 1;
        chart.options.plugins.tooltip.titleFont = { family: fontFamily, size: 13, weight: '600' };
        chart.options.plugins.tooltip.bodyFont = { family: fontFamily, size: 12, weight: '400' };

        if (chart.options?.plugins?.legend?.labels) {
          chart.options.plugins.legend.labels.color = muted;
          chart.options.plugins.legend.labels.font = { family: fontFamily };
        }
        if (chart.options?.scales) {
          Object.values(chart.options.scales).forEach(scale => {
            if (scale && typeof scale === 'object') {
              if (scale.ticks && typeof scale.ticks === 'object') {
                scale.ticks.color = muted;
                scale.ticks.font = { family: fontFamily };
              }
              if (scale.grid && typeof scale.grid === 'object') {
                scale.grid.color = grid;
              }
            }
          });
        }
        chart.update('none');
      } catch (err) {}
    });
  } catch (e) {
    console.warn("Chart theme update:", e);
  }
}

function setTheme(theme) {
  root.dataset.theme = theme;
  try {
    localStorage.setItem('cadence-theme', theme);
  } catch(e) {}
  const isDark = theme === 'dark';
  const label = isDark ? 'Switch to light mode' : 'Switch to dark mode';
  const currentLang = root.dataset.lang || 'en';
  const translatedLabel = currentLang === 'km' ? (isDark ? 'ប្តូរទៅផ្ទៃភ្លឺ' : 'ប្តូរទៅផ្ទៃងងឹត') : label;

  themeToggle?.setAttribute('aria-label', translatedLabel);
  themeToggle?.setAttribute('title', translatedLabel);
  applyChartTheme();
  try {
    window.dispatchEvent(new CustomEvent('cadence-theme-change', { detail: { theme } }));
  } catch(e) {}
}

function setLang(lang) {
  const finalLang = (lang === 'km') ? 'km' : 'en';
  root.lang = finalLang;
  root.dataset.lang = finalLang;
  if (document.body) {
    document.body.classList.toggle('lang-km', finalLang === 'km');
  }
  try {
    localStorage.setItem('cadence-lang', finalLang);
  } catch(e) {}

  // Update switcher buttons UI
  document.querySelectorAll('.lang-btn').forEach(btn => {
    const isActive = btn.dataset.lang === finalLang;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
  });

  // Translate DOM
  if (document.body) {
    translateSubtree(document.body, finalLang);
  }

  // Update document title
  try {
    if (finalLang === 'km') {
      for (const [en, km] of Object.entries(DICT_EN_TO_KM)) {
        if (document.title.includes(en)) {
          document.title = document.title.replace(en, km);
        }
      }
    } else {
      for (const [km, en] of Object.entries(DICT_KM_TO_EN)) {
        if (document.title.includes(km)) {
          document.title = document.title.replace(km, en);
        }
      }
    }
  } catch (e) {}

  // Update theme toggle label for language
  setTheme(root.dataset.theme || 'dark');

  // Update charts
  applyChartTheme();

  // Dispatch custom event
  try {
    window.dispatchEvent(new CustomEvent('cadence-lang-change', { detail: { lang: finalLang } }));
  } catch(e) {}
}

// Expose setLang on window so inline onclick and external scripts can call it directly
window.setLang = setLang;

// Global click handler for language switch buttons
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.lang-btn');
  if (btn && btn.dataset.lang) {
    e.preventDefault();
    setLang(btn.dataset.lang);
  }
});

// Observe dynamic DOM changes to auto-translate when in Khmer
const observer = new MutationObserver((mutations) => {
  if (isTranslating || root.dataset.lang !== 'km') return;
  for (const mut of mutations) {
    for (const node of mut.addedNodes) {
      if (node.nodeType === Node.ELEMENT_NODE) {
        if (node.closest?.('.lang-switch-group')) continue;
        translateSubtree(node, 'km');
      } else if (node.nodeType === Node.TEXT_NODE) {
        if (node.parentElement?.closest('.lang-switch-group')) continue;
        if (node._origEn === undefined) {
          node._origEn = node.nodeValue;
        }
        node.nodeValue = translateText(node.nodeValue, 'km');
      }
    }
  }
});

function initObserver() {
  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
  }
}

if (document.body) {
  initObserver();
} else {
  document.addEventListener('DOMContentLoaded', initObserver);
}

themeToggle?.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'));

// Initialize on load
setTheme(root.dataset.theme || 'dark');
const initialLang = (typeof localStorage !== 'undefined' && localStorage.getItem('cadence-lang')) || 'en';
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => setLang(initialLang));
} else {
  setLang(initialLang);
}
