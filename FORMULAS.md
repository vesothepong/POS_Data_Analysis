# Quick Formula Reference Guide

Short and simple reference for all formulas used in this project with clear code-style comments and real numerical examples.

---

## 1. Demand Forecasting

### Predicted Demand (Next Month)
```javascript
// Calculate next month sales using trend line: y = (slope * month) + intercept
Predicted Demand = (Slope * Next_Month) + Intercept
```
* **Example:**
  $$\hat{y}_4 = 10(4) + 40 = 80\text{ units}$$
* **Meaning:** If slope is $10$, baseline is $40$, and next month is month $4$, we predict **80 units** will sell next month.

---

### Trend Slope ($\beta_1$)
```javascript
// Calculate monthly sales growth (or decline) rate
Slope = sum((x - avg_x) * (y - avg_y)) / sum((x - avg_x)^2)
```
* **Example:**
  $$\text{Slope} = +10.0$$
* **Meaning:** Sales increase by **10 units every month**.

---

### Baseline Intercept ($\beta_0$)
```javascript
// Calculate starting baseline sales when month x = 0
Intercept = avg_y - (Slope * avg_x)
```
* **Example:**
  $$\text{Intercept} = 60 - (10 \times 2) = 40$$
* **Meaning:** The starting baseline is **40 units**.

---

### Model Accuracy / Fit ($R^2$)
```javascript
// Measure how reliable the trend line is (0.0 to 1.0)
R2 = 1 - (Residual_Errors / Total_Variation)
```
* **Example:**
  $$R^2 = 0.92 \quad (92\%)$$
* **Meaning:** $92\%$ of sales changes follow the trend. $\ge 0.80$ is very strong.

---

### Standard Error of Estimate ($SE$)
```javascript
// Typical unit error margin around the trend line
SE = sqrt(sum(errors^2) / (n - 2))
```
* **Example:**
  $$SE = 4.0\text{ units}$$
* **Meaning:** Actual sales usually vary by about $\pm 4$ units from the line.

---

### 95% Confidence Interval (Best/Worst Case Demand)
```javascript
// Calculate realistic range for next month (95% probability)
Margin = 1.96 * SE
Range = [Predicted - Margin, Predicted + Margin]
```
* **Example:**
  $$\text{Margin} = 1.96 \times 4.0 \approx 8\text{ units}$$
  $$\text{Range} = [80 - 8, \; 80 + 8] = [72 \text{ to } 88\text{ units}]$$
* **Meaning:** Demand next month is 95% likely to be between **72 and 88 units**.

---

## 2. Forecast Evaluation & Accuracy

### Hold-out Test Split
```javascript
// Split data into 80% training to learn, 20% testing to verify
Test_Months = round(Total_Months * 0.20)
Train_Months = Total_Months - Test_Months
```
* **Example:**
  $$10\text{ months total} \rightarrow 8\text{ train months}, \; 2\text{ test months}$$
* **Meaning:** The model trains on months 1–8 and tries to predict months 9 and 10.

---

### Mean Absolute Error (MAE)
```javascript
// Average miss in real units
MAE = sum(|Actual - Predicted|) / Number_of_Test_Months
```
* **Example:**
  $$MAE = \frac{|50 - 54| + |60 - 58|}{2} = \frac{4 + 2}{2} = 3.0\text{ units}$$
* **Meaning:** On average, the forecast misses by **3 units**.

---

### Root Mean Squared Error (RMSE)
```javascript
// Average error penalizing large mistakes more heavily
RMSE = sqrt(sum((Actual - Predicted)^2) / Number_of_Test_Months)
```
* **Example:**
  $$RMSE = \sqrt{\frac{4^2 + 2^2}{2}} = \sqrt{\frac{20}{2}} = 3.16\text{ units}$$
* **Meaning:** Overall error rate with penalties for large misses is **3.16 units**.

---

### Mean Absolute Percentage Error (MAPE)
```javascript
// Average percentage error
MAPE = avg(|Actual - Predicted| / Actual) * 100%
```
* **Example:**
  $$MAPE = \frac{|50 - 55|}{50} \times 100\% = 10\%$$
* **Meaning:** Predictions miss by an average of **10%**.

---

### Forecast Accuracy %
```javascript
// Overall model accuracy percentage
Accuracy = 100% - MAPE
```
* **Example:**
  $$\text{Accuracy} = 100\% - 10\% = 90\%$$
* **Meaning:** The model has a **90% accuracy score**.

---

### Naive Baseline MAE (Sanity Check)
```javascript
// Error if you just guessed the simple average every month
Baseline_MAE = avg(|Actual - Historical_Average|)
```
* **Example:**
  $$\text{Model MAE} = 3.0\text{ units} \quad \text{vs} \quad \text{Baseline MAE} = 8.5\text{ units}$$
* **Meaning:** Our regression model ($3.0$) beats simple guessing ($8.5$) by a wide margin.

---

## 3. Inventory & Purchasing Optimization

### Reorder Quantity ($Q_{\text{reorder}}$)
```javascript
// How many units to buy from supplier right now
Reorder_Quantity = max(0, Predicted_Demand - Current_Stock)
```
* **Example:**
  $$\text{Reorder Quantity} = \max(0, 80 - 25) = 55\text{ units}$$
* **Meaning:** We expect to sell 80, but have 25 in stock, so **order 55 units**.

---

### Inventory Stock Status
```javascript
// Check health of stock level
if (Stock <= 0) return "Out of Stock";
if (Stock < Reorder_Level) return "Low Stock";
if (Stock < Predicted_Demand) return "Need Reorder";
return "Sufficient Stock";
```
* **Example:**
  $$\text{Stock} = 15, \quad \text{Reorder Level} = 20 \rightarrow \textbf{"Low Stock"}$$

---

### Annual Demand ($D$)
```javascript
// Extrapolate monthly demand to 1 year
Annual_Demand = Average_Monthly_Demand * 12
```
* **Example:**
  $$D = 50 \times 12 = 600\text{ units/year}$$

---

### Annual Holding Cost ($H$)
```javascript
// Cost to store and refrigerate 1 unit for a year (20% of price, min $1.00)
Holding_Cost = max(1.0, Price * 0.20)
```
* **Example:**
  $$H = 25.00 \times 0.20 = \$5.00\text{ per unit/year}$$

---

### Economic Order Quantity (EOQ)
```javascript
// Best order batch size to minimize total ordering + storage costs
EOQ = sqrt((2 * Annual_Demand * Order_Cost) / Holding_Cost)
```
* **Example:**
  $$EOQ = \sqrt{\frac{2 \times 600 \times 25}{5}} = \sqrt{6000} \approx 77\text{ units}$$
* **Meaning:** Buy in batches of **77 units** from the supplier for lowest total cost.

---

### Safety Stock ($SS$)
```javascript
// Buffer stock to protect against sudden rushes (95% service level)
Safety_Stock = round(1.65 * Demand_StdDev)
```
* **Example:**
  $$SS = 1.65 \times 6.0 \approx 10\text{ units}$$
* **Meaning:** Keep **10 extra buffer units** untouched in stock.

---

### Recommended Reorder Point (ROP)
```javascript
// Stock level that triggers placing a new order
ROP = Average_Monthly_Demand + Safety_Stock
```
* **Example:**
  $$ROP = 50 + 10 = 60\text{ units}$$
* **Meaning:** Place a supplier order as soon as stock drops to **60 units**.

---

### Inventory Turnover
```javascript
// How many times inventory sells out and is replaced per year
Turnover = Annual_Demand / max(Current_Stock, 1)
```
* **Example:**
  $$\text{Turnover} = \frac{600}{50} = 12.0\text{ times/year}$$
* **Meaning:** Stock sells out and replenishes **12 times a year** (once a month).

---

### Days Sales of Inventory (DSI)
```javascript
// How many days of sales current stock will last
DSI = 365 / Turnover
```
* **Example:**
  $$DSI = \frac{365}{12.0} \approx 30.4\text{ days}$$
* **Meaning:** Current inventory lasts **30 days**.

---

## 4. Demand Statistics & Volatility

### Sample Mean ($\bar{x}$)
```javascript
// Average monthly sales
Mean = sum(Sales) / Total_Months
```
* **Example:**
  $$\bar{x} = \frac{40 + 50 + 60}{3} = 50\text{ units}$$

---

### Median ($\tilde{x}$)
```javascript
// Middle sales value (not skewed by one unusual spike)
Median = middle_value(sorted_sales)
```
* **Example:**
  $$\text{Values: } [40, 50, 150] \rightarrow \text{Median} = 50\text{ units} \quad (\text{Mean is } 80)$$
* **Meaning:** Typical sales are 50, even though one month had a large spike of 150.

---

### Sample Standard Deviation ($s$)
```javascript
// Month-to-month sales fluctuation
StdDev = sqrt(sum((x - Mean)^2) / (n - 1))
```
* **Example:**
  $$s = 6.2\text{ units}$$
* **Meaning:** Sales typically fluctuate by $\pm 6.2$ units around the average.

---

### Coefficient of Variation ($CV$) & Volatility Status
```javascript
// Volatility ratio (StdDev / Mean)
CV = StdDev / Mean

if (CV < 0.25) return "Stable";
if (CV <= 0.50) return "Moderate";
return "Erratic";
```
* **Example:**
  $$CV = \frac{6.2}{50} = 0.124 \rightarrow \textbf{"Stable"}$$
* **Meaning:** Low volatility; demand is smooth and predictable.

---

## 5. ABC Pareto Analysis (80/20 Rule)

### Cumulative Revenue %
```javascript
// Running total of revenue % from highest to lowest seller
Cumulative_Pct = (Running_Revenue / Total_Revenue) * 100%
```
* **Example:**
  $$\text{Item 1 brings \$7,000 out of \$10,000 total} \rightarrow \text{Cumulative \%} = 70.0\%$$

---

### ABC Class Assignment
```javascript
// Classify item business impact
if (Cumulative_Pct <= 70.0%) return "Class A (Top ~70% Revenue - Critical)";
if (Cumulative_Pct <= 90.0%) return "Class B (Next ~20% Revenue - Moderate)";
return "Class C (Bottom ~10% Revenue - Slow Mover)";
```
* **Meaning:**
  * **Class A:** Never run out! Your most valuable products.
  * **Class B:** Regular steady sellers.
  * **Class C:** Long-tail / slow items. Keep low stock.

---

## 6. Price Elasticity & Sales Growth

### Price Correlation ($r$)
```javascript
// Correlation between unit price and quantity sold (-1.0 to +1.0)
r = correlation(Price, Units_Sold)
```
* **Interpretation:**
  * $r < -0.3 \rightarrow$ **Price Sensitive**: Higher prices reduce sales volume.
  * $r > +0.3 \rightarrow$ **Premium Demand**: Sales stay strong even at higher prices.
  * $-0.3 \le r \le +0.3 \rightarrow$ **Stable Demand**: Price changes do not affect volume.
* **Example:**
  $$r = -0.55 \rightarrow \textbf{"Price Sensitive"}$$

---

### Month-over-Month (MoM) Growth
```javascript
// Percentage sales growth compared to last month
MoM = ((Current_Revenue - Last_Month_Revenue) / Last_Month_Revenue) * 100%
```
* **Example:**
  $$\text{MoM} = \frac{11500 - 10000}{10000} \times 100\% = +15.0\% \rightarrow \textbf{"Growing"}$$
* **Rules:**
  * $> +5.0\% \rightarrow$ **Growing**
  * $-5.0\% \text{ to } +5.0\% \rightarrow$ **Steady**
  * $< -5.0\% \rightarrow$ **Declining**

---

## 7. Point of Sale (POS) & Storefront Calculations

### Line Item Subtotal
```javascript
// Price for line of items
Subtotal = Quantity * Price
```
* **Example:**
  $$\text{Subtotal} = 3 \times \$4.50 = \$13.50$$

---

### Order Grand Total
```javascript
// Total bill at checkout
Order_Total = sum(Subtotal_1, Subtotal_2, ...)
```
* **Example:**
  $$\text{Order Total} = \$13.50 + \$6.00 = \$19.50$$

---

### Daily Resetting Ticket Number
```javascript
// Sequential kitchen ticket resetting each day
Ticket = "W-" + pad_zeros(max_ticket_today + 1, 3)
```
* **Example:**
  $$\text{First order today} \rightarrow \textbf{"W-001"}$$
  $$\text{Second order today} \rightarrow \textbf{"W-002"}$$
