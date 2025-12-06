# Refactoring Checklist

Используй этот чеклист в **Phase 4: Refactoring** для систематического улучшения кода.

---

## Severity Levels

- 🔴 **Critical** - Должно быть исправлено обязательно (security, data integrity, major bugs)
- 🟡 **Major** - Желательно исправить (performance, maintainability, code quality)
- 🟢 **Minor** - Nice to have (cosmetic, minor optimizations)

---

## 1. Code Quality

### 1.1 DRY (Don't Repeat Yourself)

#### ✅ Check for:

- [ ] **Code duplication**
    - Ищи одинаковые или похожие блоки кода (>5 строк)
    - Дублирование бизнес-логики в разных местах
    - Повторяющиеся валидации

#### 🎯 Actions:

- Extract common code to:
    - `utils.py` для утилитарных функций
    - `services.py` для бизнес-логики
    - Base classes для общего поведения
    - Mixins для повторяющихся паттернов

#### Example:

```python
# ❌ Bad: Duplication
# In views.py
if order.status not in ['pending', 'confirmed']:
    raise ValidationError("Invalid status")

# In services.py  
if order.status not in ['pending', 'confirmed']:
    raise ValidationError("Invalid status")

# ✅ Good: Extracted
# In validators.py
def validate_order_status(order):
    if order.status not in ['pending', 'confirmed']:
        raise ValidationError("Invalid status")
```

---

### 1.2 Naming Conventions

#### ✅ Check for:

- [ ] **Variables**: snake_case, descriptive names
    
    - `❌ d = datetime.now()` → `✅ current_datetime = datetime.now()`
    - `❌ tmp` → `✅ temporary_route_data`
- [ ] **Functions**: snake_case, verb-based names
    
    - `✅ get_orders()`, `calculate_route()`, `validate_time_window()`
    - `❌ orders()`, `route()`, `check()`
- [ ] **Classes**: PascalCase, noun-based names
    
    - `✅ OrderStatusTransition`, `RouteOptimizer`, `DeliveryService`
    - `❌ order_status`, `optimizer`, `service`
- [ ] **Constants**: UPPER_CASE
    
    - `✅ MAX_DELIVERY_DISTANCE`, `DEFAULT_TIME_WINDOW`
    - `❌ maxDistance`, `timeWindow`
- [ ] **Boolean variables**: is_, has_, can_, should_
    
    - `✅ is_active`, `has_permission`, `can_edit`
    - `❌ active`, `permission`, `edit`

#### 🎯 Django-specific:

- Models: Singular nouns (`Order`, not `Orders`)
- Managers: plural or descriptive (`objects`, `active_objects`)
- Querysets: verb-based methods (`with_routes()`, `for_date()`)

---

### 1.3 Function/Method Length

#### ✅ Check for:

- [ ] **Functions > 50 lines**
    
    - Severity: 🟡 Major
    - Action: Split into smaller functions
- [ ] **Functions > 100 lines**
    
    - Severity: 🔴 Critical
    - Action: Definitely refactor
- [ ] **Classes > 300 lines**
    
    - Severity: 🟡 Major
    - Action: Consider splitting responsibilities

#### 🎯 Actions:

- Extract helper methods
- Use composition over inheritance
- Split into multiple classes (SRP)

---

### 1.4 Complexity

#### ✅ Check for:

- [ ] **Nested if-statements (>3 levels)**
    
    - Severity: 🟡 Major
    
    ```python
    # ❌ Bad: Deep nesting
    if user:
        if user.is_active:
            if user.has_permission('edit'):
                if order.status == 'pending':
                    # do something
    
    # ✅ Good: Early returns
    if not user or not user.is_active:
        return
    if not user.has_permission('edit'):
        return
    if order.status != 'pending':
        return
    # do something
    ```
    
- [ ] **Long method chains**
    
    - Severity: 🟢 Minor
    - Break into intermediate variables for clarity
- [ ] **Complex boolean expressions**
    
    - Severity: 🟡 Major
    - Extract to well-named variables or methods

---

### 1.5 Comments and Documentation

#### ✅ Check for:

- [ ] **Public methods without docstrings**
    
    - Severity: 🟡 Major
    
    ```python
    def calculate_route_duration(stops: List[Stop], vehicle: Vehicle) -> timedelta:
        """
        Calculate total duration for a route including driving and service time.
        
        Args:
            stops: List of delivery stops
            vehicle: Vehicle assigned to the route
            
        Returns:
            Total duration as timedelta
            
        Raises:
            ValueError: If stops list is empty
        """
    ```
    
- [ ] **Complex logic without comments**
    
    - Severity: 🟡 Major
    - Add inline comments explaining WHY, not WHAT
- [ ] **Outdated comments**
    
    - Severity: 🟢 Minor
    - Update or remove
- [ ] **Commented-out code**
    
    - Severity: 🟢 Minor
    - Remove (Git history preserves it)

#### 🎯 Type hints:

- [ ] Add type hints for function parameters and returns
    - Django 3.0+: Use from `__future__ import annotations`

---

## 2. Architecture

### 2.1 Layer Separation (Django)

#### ✅ Check for:

- [ ] **Business logic in Models**
    
    - Severity: 🟡 Major
    
    ```python
    # ❌ Bad: Business logic in model
    class Order(models.Model):
        def assign_to_nearest_driver(self):
            # complex assignment logic here
            
    # ✅ Good: Business logic in service
    # services.py
    def assign_order_to_nearest_driver(order: Order) -> Driver:
        # complex assignment logic here
    ```
    
- [ ] **Business logic in Views**
    
    - Severity: 🟡 Major
    - Extract to `services.py`
- [ ] **Database queries in Serializers**
    
    - Severity: 🟡 Major
    - Move to ViewSet or use `select_related`/`prefetch_related`
- [ ] **HTTP logic in Services**
    
    - Severity: 🟡 Major
    - Services should be HTTP-agnostic

#### 🎯 Proper layers:

```
Views/ViewSets
    ↓ (HTTP layer only)
Serializers
    ↓ (data transformation)
Services
    ↓ (business logic)
Models
    ↓ (data layer)
```

---

### 2.2 Dependencies

#### ✅ Check for:

- [ ] **Circular imports**
    
    - Severity: 🔴 Critical
    - Use `TYPE_CHECKING` or restructure
- [ ] **Tight coupling between apps**
    
    - Severity: 🟡 Major
    - Apps should be loosely coupled
- [ ] **Direct imports from other apps**
    
    - Severity: 🟢 Minor
    - Consider using signals or shared `core` app

#### Example:

```python
# ❌ Bad: Circular import
# orders/models.py
from routes.models import Route

# routes/models.py
from orders.models import Order

# ✅ Good: Using TYPE_CHECKING
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from routes.models import Route
```

---

### 2.3 Single Responsibility Principle

#### ✅ Check for:

- [ ] **Classes doing too many things**
    
    - Severity: 🟡 Major
    
    ```python
    # ❌ Bad: Too many responsibilities
    class OrderService:
        def create_order(self): ...
        def send_notification(self): ...
        def generate_invoice(self): ...
        def calculate_shipping(self): ...
    
    # ✅ Good: Separate services
    class OrderService:
        def create_order(self): ...
    
    class NotificationService:
        def send_order_notification(self): ...
        
    class InvoiceService:
        def generate_order_invoice(self): ...
    ```
    

---

## 3. Performance

### 3.1 Database Queries

#### ✅ Check for:

- [ ] **N+1 Query Problem**
    
    - Severity: 🔴 Critical
    
    ```python
    # ❌ Bad: N+1 queries
    orders = Order.objects.all()
    for order in orders:
        print(order.route.vehicle.name)  # Query for each order!
    
    # ✅ Good: select_related
    orders = Order.objects.select_related('route__vehicle').all()
    for order in orders:
        print(order.route.vehicle.name)  # No extra queries
    ```
    
- [ ] **Missing select_related / prefetch_related**
    
    - Severity: 🔴 Critical (if causing N+1)
    - Check with Django Debug Toolbar or `django-silk`
- [ ] **Fetching all records when pagination needed**
    
    - Severity: 🟡 Major
    
    ```python
    # ❌ Bad
    orders = Order.objects.all()  # Could be thousands!
    
    # ✅ Good
    orders = Order.objects.all()[:100]  # or use pagination
    ```
    
- [ ] **Missing database indexes**
    
    - Severity: 🟡 Major
    - Fields used in filters, ordering, joins should be indexed
    
    ```python
    class Order(models.Model):
        status = models.CharField(max_length=20, db_index=True)  # ✅
        created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # ✅
    ```
    

---

### 3.2 Inefficient Code

#### ✅ Check for:

- [ ] **Unnecessary computations in loops**
    
    - Severity: 🟡 Major
    
    ```python
    # ❌ Bad
    for order in orders:
        if order.total > get_threshold():  # Called every iteration!
            process_order(order)
    
    # ✅ Good
    threshold = get_threshold()  # Called once
    for order in orders:
        if order.total > threshold:
            process_order(order)
    ```
    
- [ ] **Using list when generator would work**
    
    - Severity: 🟢 Minor
    
    ```python
    # ❌ Bad: Creates full list in memory
    total = sum([order.total for order in Order.objects.all()])
    
    # ✅ Good: Generator
    total = sum(order.total for order in Order.objects.all())
    ```
    
- [ ] **Multiple database queries that could be one**
    
    - Severity: 🟡 Major
    - Use `bulk_create`, `bulk_update`, `update()` instead of loops

---

### 3.3 Caching

#### ✅ Check for:

- [ ] **Repeated expensive computations**
    
    - Severity: 🟡 Major (depending on cost)
    - Consider caching with Django cache framework
- [ ] **API calls in loops**
    
    - Severity: 🔴 Critical
    - Batch requests or cache results

---

## 4. Error Handling

### 4.1 Exception Handling

#### ✅ Check for:

- [ ] **Bare except clauses**
    
    - Severity: 🟡 Major
    
    ```python
    # ❌ Bad
    try:
        process_order()
    except:  # Catches everything, even KeyboardInterrupt!
        pass
    
    # ✅ Good
    try:
        process_order()
    except OrderProcessingError as e:
        logger.error(f"Failed to process order: {e}")
        raise
    ```
    
- [ ] **Silent failures**
    
    - Severity: 🔴 Critical
    
    ```python
    # ❌ Bad
    try:
        critical_operation()
    except Exception:
        pass  # Silent failure!
    
    # ✅ Good
    try:
        critical_operation()
    except Exception as e:
        logger.error(f"Critical operation failed: {e}")
        # Re-raise or handle appropriately
        raise
    ```
    
- [ ] **Generic error messages**
    
    - Severity: 🟢 Minor
    
    ```python
    # ❌ Bad
    raise ValueError("Invalid input")
    
    # ✅ Good
    raise ValueError(f"Order status '{status}' is not valid. Expected one of: {VALID_STATUSES}")
    ```
    

---

### 4.2 Logging

#### ✅ Check for:

- [ ] **Missing logging for important operations**
    
    - Severity: 🟡 Major
    - Log: errors, warnings, important state changes
- [ ] **Using print() instead of logger**
    
    - Severity: 🟢 Minor
    
    ```python
    # ❌ Bad
    print(f"Processing order {order.id}")
    
    # ✅ Good
    logger.info(f"Processing order {order.id}")
    ```
    
- [ ] **Logging sensitive data**
    
    - Severity: 🔴 Critical
    - Never log passwords, tokens, credit cards, etc.

---

### 4.3 Validation

#### ✅ Check for:

- [ ] **Missing input validation**
    
    - Severity: 🔴 Critical
    - Always validate user input
- [ ] **Validation in wrong layer**
    
    - Severity: 🟡 Major
    - Django: Use serializers, form validation, model validation
    
    ```python
    # ✅ Good: Serializer validation
    class OrderSerializer(serializers.ModelSerializer):
        def validate_delivery_date(self, value):
            if value < timezone.now().date():
                raise serializers.ValidationError("Delivery date cannot be in the past")
            return value
    ```
    

---

## 5. Security

### 5.1 Permissions

#### ✅ Check for:

- [ ] **Missing permission checks**
    
    - Severity: 🔴 Critical
    
    ```python
    # ❌ Bad: No permission check
    class OrderViewSet(viewsets.ModelViewSet):
        queryset = Order.objects.all()
    
    # ✅ Good: With permissions
    class OrderViewSet(viewsets.ModelViewSet):
        queryset = Order.objects.all()
        permission_classes = [IsAuthenticated, CanViewOrders]
    ```
    
- [ ] **Object-level permissions not checked**
    
    - Severity: 🔴 Critical
    - Use `has_object_permission`

---

### 5.2 Input Validation

#### ✅ Check for:

- [ ] **SQL Injection vulnerabilities**
    
    - Severity: 🔴 Critical
    
    ```python
    # ❌ Bad: SQL injection risk
    User.objects.raw(f"SELECT * FROM users WHERE name = '{name}'")
    
    # ✅ Good: Parameterized
    User.objects.raw("SELECT * FROM users WHERE name = %s", [name])
    
    # ✅ Best: Use ORM
    User.objects.filter(name=name)
    ```
    
- [ ] **XSS vulnerabilities**
    
    - Severity: 🔴 Critical
    - Django templates auto-escape, but check if using `|safe` or `mark_safe()`
- [ ] **CSRF protection**
    
    - Severity: 🔴 Critical
    - Ensure `@csrf_protect` or using DRF's session auth

---

### 5.3 Data Exposure

#### ✅ Check for:

- [ ] **Sensitive data in serializers**
    
    - Severity: 🔴 Critical
    
    ```python
    # ❌ Bad: Exposes password hash
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = '__all__'  # Includes password!
    
    # ✅ Good: Explicit fields
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'username', 'email']  # No password
    ```
    
- [ ] **Debug mode in production**
    
    - Severity: 🔴 Critical
    - `DEBUG = False` in production

---

## 6. Testing

### 6.1 Test Coverage

#### ✅ Check for:

- [ ] **Critical paths without tests**
    
    - Severity: 🔴 Critical
    - Payment processing, authentication, data integrity
- [ ] **Edge cases not tested**
    
    - Severity: 🟡 Major
    - Empty lists, null values, boundary conditions
- [ ] **Only happy path tested**
    
    - Severity: 🟡 Major
    - Test error cases too

---

### 6.2 Test Quality

#### ✅ Check for:

- [ ] **Tests without assertions**
    
    - Severity: 🟡 Major
    
    ```python
    # ❌ Bad
    def test_create_order(self):
        order = Order.objects.create(...)
        # No assertion!
    
    # ✅ Good
    def test_create_order(self):
        order = Order.objects.create(...)
        self.assertEqual(order.status, 'pending')
        self.assertIsNotNone(order.id)
    ```
    
- [ ] **Tests depending on order of execution**
    
    - Severity: 🔴 Critical
    - Tests should be independent
- [ ] **Tests modifying production database**
    
    - Severity: 🔴 Critical
    - Use test database or transactions

---

## 7. Django-Specific

### 7.1 Models

#### ✅ Check for:

- [ ] **Missing `__str__` method**
    
    - Severity: 🟢 Minor
    - Helpful for admin and debugging
- [ ] **Missing Meta options**
    
    - Severity: 🟢 Minor
    
    ```python
    class Order(models.Model):
        class Meta:
            ordering = ['-created_at']
            verbose_name = 'Order'
            verbose_name_plural = 'Orders'
            indexes = [
                models.Index(fields=['status', 'created_at']),
            ]
    ```
    
- [ ] **Using `null=True` on CharField**
    
    - Severity: 🟡 Major
    - Use `blank=True` instead (Django convention)
    
    ```python
    # ❌ Bad
    name = models.CharField(max_length=100, null=True)
    
    # ✅ Good
    name = models.CharField(max_length=100, blank=True, default='')
    ```
    

---

### 7.2 Migrations

#### ✅ Check for:

- [ ] **Migration conflicts**
    
    - Severity: 🔴 Critical
    - Run `python manage.py makemigrations --check`
- [ ] **Data migrations without reverse**
    
    - Severity: 🟡 Major
    - Add `reverse_code` for data migrations
- [ ] **Irreversible migrations**
    
    - Severity: 🟢 Minor
    - Document why if intentional

---

## 8. Flutter-Specific (если применимо)

### 8.1 State Management

#### ✅ Check for:

- [ ] **setState called too frequently**
    
    - Severity: 🟡 Major
    - Consider Riverpod or other state management
- [ ] **Rebuilding entire widget tree**
    
    - Severity: 🟡 Major
    - Use const constructors, separate widgets

---

### 8.2 Performance

#### ✅ Check for:

- [ ] **ListView without builder**
    
    - Severity: 🟡 Major
    
    ```dart
    // ❌ Bad
    ListView(children: items.map((item) => ItemWidget(item)).toList())
    
    // ✅ Good
    ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) => ItemWidget(items[index]),
    )
    ```
    
- [ ] **Heavy computations in build()**
    
    - Severity: 🔴 Critical
    - Move to async methods or compute()

---

## Usage Instructions

### During Phase 4: Refactoring

1. **Load this checklist** in Claude chat
2. **Add all changed files** from Implementation
3. **Run through each section** systematically
4. **Document findings** in CURRENT_TASK.md
5. **Prioritize fixes**: 🔴 first, then 🟡, then 🟢

### Tools to help

**Django**:

- `pylint` or `flake8` for linting
- `mypy` for type checking
- `django-debug-toolbar` for query analysis
- `coverage.py` for test coverage

**Commands**:

```bash
# Linting
pylint apps/orders/

# Type checking
mypy apps/orders/

# Test coverage
pytest --cov=apps/orders --cov-report=html

# Check for N+1 queries
python manage.py debugsqlshell
```

---

## Severity Guidelines

### When to mark 🔴 Critical:

- Security vulnerabilities
- Data integrity issues
- Major performance problems (N+1 queries on large datasets)
- Breaking changes to API
- Silent failures

### When to mark 🟡 Major:

- Maintainability issues
- Code quality problems
- Medium performance issues
- Missing error handling
- Architectural violations

### When to mark 🟢 Minor:

- Cosmetic issues
- Missing comments (if code is clear)
- Small optimizations
- Nice-to-have improvements

---

**Remember**: Refactoring is iterative. Don't try to fix everything at once. Focus on 🔴 Critical issues first, then tackle 🟡 Major issues. 🟢 Minor issues can wait for a dedicated cleanup sprint.