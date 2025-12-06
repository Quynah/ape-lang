# APE Extended Math Module Documentation (v1.0.0)

**Author:** David Van Aelst  
**Status:** Scaffold - implementation pending  
**Version:** 1.0.0

---

## Overview

The extended math module provides advanced mathematical functions including trigonometry, logarithms, rounding, and mathematical constants.

## Constants

### PI

Mathematical constant π (pi) = 3.141592653589793

**Example:**
```ape
import math_ext

task calculate_circle_area(radius: Number):
    area = math_ext.PI * radius * radius
    return area
```

### E

Mathematical constant e (Euler's number) = 2.718281828459045

**Example:**
```ape
import math_ext

task exponential_growth(rate: Number, time: Number):
    return math_ext.pow(math_ext.E, rate * time)
```

## Trigonometric Functions

All angle arguments are in **radians**.

### sin(x: Number) -> Number

Sine of x.

**Example:**
```ape
import math_ext

result = math_ext.sin(math_ext.PI / 2)  # 1.0
```

### cos(x: Number) -> Number

Cosine of x.

**Example:**
```ape
result = math_ext.cos(0)  # 1.0
```

### tan(x: Number) -> Number

Tangent of x.

**Example:**
```ape
result = math_ext.tan(math_ext.PI / 4)  # ~1.0
```

### asin(x: Number) -> Number

Arc sine (inverse sine) of x. Returns angle in radians.

**Example:**
```ape
angle = math_ext.asin(0.5)  # PI / 6
```

### acos(x: Number) -> Number

Arc cosine (inverse cosine) of x. Returns angle in radians.

**Example:**
```ape
angle = math_ext.acos(0.5)  # PI / 3
```

### atan(x: Number) -> Number

Arc tangent (inverse tangent) of x. Returns angle in radians.

**Example:**
```ape
angle = math_ext.atan(1)  # PI / 4
```

### atan2(y: Number, x: Number) -> Number

Two-argument arc tangent. Returns angle in radians, considering the correct quadrant.

**Example:**
```ape
# Get angle from origin to point (1, 1)
angle = math_ext.atan2(1, 1)  # PI / 4
```

## Logarithmic Functions

### ln(x: Number) -> Number

Natural logarithm (base e) of x.

**Example:**
```ape
result = math_ext.ln(math_ext.E)  # 1.0
```

### log10(x: Number) -> Number

Base-10 logarithm of x.

**Example:**
```ape
result = math_ext.log10(1000)  # 3.0
```

### log(x: Number, base: Number) -> Number

Logarithm of x to the given base.

**Example:**
```ape
result = math_ext.log(8, 2)  # 3.0 (2^3 = 8)
result = math_ext.log(100, 10)  # 2.0
```

## Rounding Functions

### round(x: Number, decimals: Integer) -> Number

Round x to given number of decimal places.

**Example:**
```ape
result = math_ext.round(3.14159, 2)  # 3.14
result = math_ext.round(42.7)  # 43 (default 0 decimals)
```

### floor(x: Number) -> Integer

Largest integer less than or equal to x.

**Example:**
```ape
result = math_ext.floor(3.7)  # 3
result = math_ext.floor(-2.3)  # -3
```

### ceil(x: Number) -> Integer

Smallest integer greater than or equal to x.

**Example:**
```ape
result = math_ext.ceil(3.2)  # 4
result = math_ext.ceil(-2.7)  # -2
```

## Power and Root Functions

### sqrt(x: Number) -> Number

Square root of x.

**Example:**
```ape
result = math_ext.sqrt(16)  # 4.0
result = math_ext.sqrt(2)  # ~1.414
```

### pow(x: Number, y: Number) -> Number

x raised to the power of y.

**Example:**
```ape
result = math_ext.pow(2, 8)  # 256.0
result = math_ext.pow(10, 3)  # 1000.0
```

## Complete Examples

### Trigonometric Calculations

```ape
import math_ext

task calculate_triangle_height(base: Number, angle_degrees: Number):
    # Convert degrees to radians
    angle_radians = (angle_degrees * math_ext.PI) / 180
    
    # Calculate height using tangent
    height = base * math_ext.tan(angle_radians)
    
    return height
```

### Distance Formula

```ape
import math_ext

task calculate_distance(x1: Number, y1: Number, x2: Number, y2: Number):
    dx = x2 - x1
    dy = y2 - y1
    
    distance = math_ext.sqrt(dx * dx + dy * dy)
    
    return distance
```

### Exponential Growth

```ape
import math_ext

task compound_interest(principal: Number, rate: Number, years: Number):
    # Calculate compound interest using natural exponential
    amount = principal * math_ext.pow(math_ext.E, rate * years)
    return math_ext.round(amount, 2)
```

### Statistical Functions

```ape
import math_ext

task geometric_mean(numbers: List<Number>):
    product = 1
    count = 0
    
    for num in numbers:
        product = product * num
        count = count + 1
    
    # Nth root = exp(ln(x) / n)
    result = math_ext.pow(math_ext.E, math_ext.ln(product) / count)
    
    return result
```

## Unit Conversion

### Degrees to Radians

```ape
task degrees_to_radians(degrees: Number):
    return (degrees * math_ext.PI) / 180
```

### Radians to Degrees

```ape
task radians_to_degrees(radians: Number):
    return (radians * 180) / math_ext.PI
```

## Best Practices

### 1. Use Constants Instead of Literals

```ape
# Good
circumference = 2 * math_ext.PI * radius

# Less precise
circumference = 2 * 3.14 * radius
```

### 2. Check Domain for Logarithms

```ape
task safe_log(x: Number):
    if x <= 0:
        raise ValueError("Logarithm undefined for non-positive numbers")
    return math_ext.ln(x)
```

### 3. Round Financial Calculations

```ape
task calculate_price(base_price: Number, tax_rate: Number):
    total = base_price * (1 + tax_rate)
    return math_ext.round(total, 2)  # Round to cents
```

## Mathematical Identities

The following identities hold:

- `sin²(x) + cos²(x) = 1`
- `tan(x) = sin(x) / cos(x)`
- `ln(x * y) = ln(x) + ln(y)`
- `ln(x^y) = y * ln(x)`
- `log_b(x) = ln(x) / ln(b)`

## Performance Notes

- Trigonometric functions use series approximations
- Logarithm calculations are optimized for accuracy
- Power function handles integer exponents efficiently

---

**Note:** This feature is scaffolded in v1.0.0. Full implementation is planned for a future release.
