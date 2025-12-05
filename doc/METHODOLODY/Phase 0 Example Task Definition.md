Этот файл показывает реальный пример как работает Phase 0: Task Definition.

---

## Пример 1: Route Status Management

### Исходный запрос (нечёткий)

**Пользователь пишет**:

> "Мне нужно чтобы таблица Route также имела статусы аналогично, как это есть в Заказах. Сформулируй эту задачу, найди модули, которые могут быть как бенчмарки."

### Промпт для Claude (Phase 0)

```prompt
Помоги сформулировать задачу профессионально.

Контекст:
@_ai_context/ARCHITECTURE.md

Моё описание задачи:
"Мне нужно чтобы таблица Route также имела статусы аналогично, как это есть в Заказах"

[Дальше следуй инструкциям из WORKFLOW.md → Phase 0]
```

### Claude задаёт уточняющие вопросы

**Claude**:

> Спасибо за описание! Давайте уточним требования:
> 
> 1. **Статусы Route**: Какие конкретно статусы нужны для Route?
>     - Те же самые что у Order (Pending, Confirmed, In Transit, Delivered, Cancelled)?
>     - Или специфичные для Route (например: Planned, In Progress, Completed)?
> 2. **Кто управляет статусами**:
>     - Dispatcher может менять статусы вручную?
>     - Driver меняет статусы через мобильное приложение?
>     - Система автоматически меняет статусы при определённых событиях?
> 3. **История изменений**:
>     - Нужна ли история изменений статусов (кто, когда, почему изменил)?
> 4. **Переходы между статусами**:
>     - Должны ли быть ограничения на переходы? (например, нельзя из Completed вернуться в Planned)
>     - Нужна ли валидация переходов?
> 5. **Связь с Orders**:
>     - Как статус Route влияет на статусы Orders внутри этого Route?
>     - Например, если Route становится "In Progress", должны ли все Orders автоматически стать "In Transit"?
> 6. **Уведомления**:
>     - Нужны ли уведомления при смене статуса Route?
>     - Кому отправлять? (Driver, Dispatcher, Customers?)

### Пользователь отвечает

**Пользователь**:

> 1. Статусы Route: Planned, Assigned, In Progress, Completed, Cancelled
> 2. Dispatcher и Driver могут менять, система тоже (автоматически при событиях)
> 3. Да, история нужна с timestamp и user
> 4. Да, нужны ограничения переходов и валидация
> 5. Статус Route НЕ должен автоматически менять статусы Orders (они независимы)
> 6. Уведомления нужны только Driver'у когда Route assigned

### Claude формулирует чёткую задачу

**Claude пишет в CURRENT_TASK.md**:

```markdown
## Task Definition

### Original Request
"Мне нужно чтобы таблица Route также имела статусы аналогично, как это есть в Заказах"

### Clarifying Questions & Answers
**Q1**: Какие статусы нужны для Route?  
**A1**: Planned, Assigned, In Progress, Completed, Cancelled

**Q2**: Кто управляет статусами?  
**A2**: Dispatcher, Driver (мобильное приложение), система (автоматически)

**Q3**: Нужна ли история изменений?  
**A3**: Да, с timestamp и user

**Q4**: Ограничения на переходы между статусами?  
**A4**: Да, нужна валидация переходов

**Q5**: Связь с Orders?  
**A5**: Статус Route НЕ влияет автоматически на статусы Orders (независимы)

**Q6**: Уведомления?  
**A6**: Только Driver'у при Route assignment

### Similar Implementations (Benchmarks)

- **Order Status Management** (apps/orders/models.py, apps/workflows/models.py)
  - Files: 
    - apps/orders/models.py (Order model with status field)
    - apps/workflows/models.py (OrderStatusSchema, OrderStatusTransition)
    - apps/orders/services.py (status change service)
  - Pattern: StatusSchema с allowed transitions, history в отдельной таблице
  - Can reuse: Schema pattern, validation logic, history tracking

- **Driver Status** (apps/drivers/models.py)
  - Files: apps/drivers/models.py
  - Pattern: Simple status field с choices
  - Can reuse: Status choices pattern

### Refined Task Description

**Task Title**: Implement Route Status Management System

**Description**: 
Add comprehensive status management to Route model with support for:
- Predefined status workflow (Planned → Assigned → In Progress → Completed/Cancelled)
- Transition validation (allowed/forbidden transitions)
- Change history tracking (who, when, why)
- Multi-actor support (Dispatcher, Driver, System)
- Driver notification on assignment

The implementation should follow the same pattern as Order status management but be independent (Route status doesn't automatically affect Order statuses).

**Use Cases**:
1. **UC1**: Dispatcher needs to assign a planned route to a driver
   - Example: Dispatcher selects Route and clicks "Assign to Driver X"
   - System validates transition Planned → Assigned
   - System creates history record
   - System sends push notification to Driver X
   
2. **UC2**: Driver needs to start delivering the route
   - Example: Driver opens app, sees assigned Route, clicks "Start Route"
   - System validates transition Assigned → In Progress
   - System records start time and location
   - System updates Route status
   
3. **UC3**: Driver or Dispatcher needs to cancel a route
   - Example: Due to vehicle breakdown, route needs to be cancelled
   - System validates transition (can cancel from any status except Completed)
   - System records reason for cancellation
   - System notifies relevant parties

4. **UC4**: System automatically marks route as completed
   - Example: When all orders in route are delivered
   - System checks if all RouteStops completed
   - System transitions Route to Completed
   - System records completion time

**Scope**:
- ✅ **In scope**:
  - Route status field with defined statuses
  - RouteStatusSchema model for workflow definition
  - RouteStatusTransition model for allowed transitions
  - RouteStatusHistory model for tracking changes
  - API endpoints for status changes
  - Validation logic for transitions
  - History tracking (who, when, optional reason)
  - Notification to Driver on assignment
  - Flutter UI updates to show and change status
  
- ❌ **Out of scope** (not in this task):
  - Automatic Order status updates based on Route status (they remain independent)
  - Complex conditional transitions (can be added later if needed)
  - Email notifications (only push notifications for now)
  - Bulk status updates (one route at a time)
  - Custom status creation by users (predefined only)

**Success Criteria**:
- [ ] Route model has status field with 5 defined statuses
- [ ] RouteStatusSchema and RouteStatusTransition models created
- [ ] RouteStatusHistory tracks all status changes with user and timestamp
- [ ] API endpoint POST /api/routes/{id}/change-status/ works correctly
- [ ] Validation prevents invalid transitions (e.g., Completed → Planned)
- [ ] Driver receives push notification when route assigned
- [ ] Flutter app displays current route status
- [ ] Flutter app allows Driver to change status (Assigned → In Progress → Completed)
- [ ] Dispatcher can change route status in Back Office
- [ ] Test coverage ≥ 85% for status management code
- [ ] Documentation includes status workflow diagram

**Technical Considerations**:
- Use existing OrderStatusSchema pattern as reference
- Consider database transactions for status changes (atomic operations)
- Add database index on Route.status for filtering
- Consider race conditions (two users changing status simultaneously)
- Push notifications via existing notification service
- Status history might grow large - consider pagination

### Complexity Assessment

**Complexity**: Medium-High

**Estimated effort**: 18-24 hours breakdown:
- Phase 0 Task Definition: 1h (done)
- Phase 1 Research: 2h (study Order status implementation)
- Phase 2 Plan: 2h (detailed plan with edge cases)
- Phase 3 Implementation: 10-12h (backend + frontend)
- Phase 4 Refactoring: 1-2h
- Phase 5 Testing: 2-3h
- Phase 6 Documentation: 1-2h

**Risk factors**:
- 🟡 **Database migration complexity**: Route table might have many records, migration could be slow
  - Mitigation: Test migration on copy of production DB first
  
- 🟡 **Race conditions**: Multiple actors changing status simultaneously
  - Mitigation: Use database-level locking or optimistic locking
  
- 🟢 **Notification delivery**: Push notifications might fail
  - Mitigation: Queue notifications, retry on failure

### Components to Modify

**Django Backend**:
- Models: 
  - apps/routes/models.py (add status field to Route)
  - apps/workflows/models.py (create RouteStatusSchema, RouteStatusTransition, RouteStatusHistory)
- Views/ViewSets: 
  - apps/routes/views.py (add change_status action to RouteViewSet)
- Serializers: 
  - apps/routes/serializers.py (add status field, history)
- Services: 
  - apps/routes/services.py (create RouteStatusService for business logic)
- Signals:
  - apps/routes/signals.py (trigger notifications on status change)
- Migrations: 
  - New migration to add status field (default='planned')
  - Data migration to populate RouteStatusSchema

**Flutter Frontend**:
- Screens: 
  - mobile/apps/driver_pro/lib/features/routes/route_detail_screen.dart
  - mobile/apps/fleet_planner/lib/features/routes/route_management_screen.dart
- Widgets: 
  - mobile/apps/driver_pro/lib/features/routes/widgets/route_status_chip.dart (new)
  - mobile/apps/driver_pro/lib/features/routes/widgets/change_status_button.dart (new)
- Providers/State: 
  - mobile/apps/driver_pro/lib/features/routes/providers/route_provider.dart (add status change method)
- Services: 
  - mobile/apps/shared/lib/services/api/routes_api_service.dart (add changeStatus method)

**Database**:
- Modified tables: 
  - routes_route (add status VARCHAR(20) NOT NULL DEFAULT 'planned')
  - Add index on status field
- New tables:
  - workflows_routestatusschema
  - workflows_routestatustransition  
  - workflows_routestatushistory

**API Changes**:
- New endpoints:
  - POST /api/routes/{id}/change-status/ (body: {status: string, reason?: string})
  - GET /api/routes/{id}/status-history/ (returns history)
  - GET /api/workflows/route-status-schemas/ (get available statuses and transitions)
- Modified endpoints:
  - GET /api/routes/ (includes status in response)
  - GET /api/routes/{id}/ (includes status and history)
- Breaking changes: No breaking changes

### Dependencies

**This task depends on**:
- Notification service must be working (for Driver notifications)
- OrderStatusSchema implementation (as reference)

**Will affect these components**:
- apps/routes/models.py (Route model)
- Driver Pro app (will need to display and change status)
- Fleet Planner app (Dispatcher interface for status management)
- Potentially: reporting queries that filter routes (will need to update to use new status field)

**External dependencies**:
- No new external dependencies needed (reuse existing patterns)

### Recommended Approach

High-level approach (will be refined in Planning phase):

1. **Backend - Models & Database**
   - Add status field to Route model (with migration)
   - Create RouteStatusSchema, RouteStatusTransition, RouteStatusHistory models
   - Populate default schema with 5 statuses and allowed transitions

2. **Backend - Business Logic**
   - Create RouteStatusService with validate_transition, change_status methods
   - Add signal to trigger Driver notification on assignment
   - Create API endpoint for status changes

3. **Backend - API**
   - Add status serialization to RouteSerializer
   - Create change_status action in RouteViewSet
   - Add permissions (Dispatcher and assigned Driver can change)

4. **Frontend - Driver Pro**
   - Add status display widget (colored chip)
   - Add status change button (only for relevant transitions)
   - Update route detail screen

5. **Frontend - Fleet Planner**
   - Add status column to routes list
   - Add status change dropdown in route detail
   - Show status history

6. **Testing**
   - Unit tests for validation logic
   - Integration tests for API endpoints
   - Test status transition workflows
   - Test permission checks

7. **Documentation**
   - Status workflow diagram
   - API documentation
   - User guide for Dispatcher and Driver
```

---

## Пример 2: Optimize Routes

### Исходный запрос (нечёткий)

**Пользователь**:

> "Сделай оптимизацию маршрутов"

### Claude задаёт вопросы

**Claude**:

> 1. Что оптимизируем? Минимизация времени, расстояния, или количества транспорта?
> 2. Автоматическая оптимизация или по запросу dispatcher?
> 3. Можно ли менять уже назначенные заказы?
> 4. Какие ограничения? (вес, время доставки, зоны)
> 5. Нужен ли preview изменений?

### Пользователь отвечает

**Пользователь**:

> 1. Минимизация времени и расстояния (оба важны)
> 2. По запросу dispatcher, с preview
> 3. Да, можно переназначать
> 4. Учитывать: грузоподъёмность, временные окна, зоны доставки
> 5. Да, обязательно preview с возможностью отмены

### Claude формулирует

**Task Title**: Implement Route Optimization with Preview

**Description**: Add route optimization feature that allows dispatcher to optimize existing routes by minimizing total distance and time while respecting constraints (vehicle capacity, time windows, delivery zones). Optimization runs on-demand with preview of changes before applying.

**Use Cases**:

1. Dispatcher clicks "Optimize Routes" button
2. System calculates optimal redistribution
3. System shows preview with metrics (time saved, distance saved)
4. Dispatcher reviews and either applies or cancels

**Scope**:

- ✅ In scope: optimization algorithm, preview modal, apply/cancel
- ❌ Out of scope: automatic scheduling, multi-depot optimization

**Success Criteria**:

- [ ] Optimization reduces total distance by 10-30%
- [ ] Preview shows before/after comparison
- [ ] All constraints respected
- [ ] Processing time < 10 seconds for 50 orders

[...и т.д.]

---

## Пример 3: Add Notifications

### Исходный запрос

**Пользователь**:

> "Добавь уведомления водителям"

### Уточняющие вопросы

**Claude**:

> 1. Какие события должны вызывать уведомления?
> 2. Push или SMS или оба?
> 3. Можно ли отключить уведомления?
> 4. Нужна ли история уведомлений?

### Ответы + формулировка

[...аналогично предыдущим примерам...]

---

## Когда использовать Phase 0

### ✅ Используй Phase 0 когда:

- Задача сформулирована нечётко ("сделай как в X")
- Не понятен scope (что входит, что нет)
- Нужно найти существующие аналоги
- Сложная задача требует уточнений
- Новая фича без чётких требований

### ❌ Можно пропустить Phase 0 когда:

- Задача предельно ясна ("добавить поле email в модель User")
- Простой bug fix с чёткими шагами воспроизведения
- Техническое улучшение с понятным scope
- Refactoring с чётким планом

---

## Польза Phase 0

**До Phase 0**:

- ❌ Неясно что конкретно делать
- ❌ Нет benchmarks
- ❌ Сложно оценить время
- ❌ Риск сделать не то что нужно

**После Phase 0**:

- ✅ Чёткая формулировка задачи
- ✅ Найдены аналоги для reference
- ✅ Понятен scope (границы)
- ✅ Реалистичная оценка времени
- ✅ Критерии успеха определены
- ✅ Research фаза будет более эффективной

---

**Вывод**: Phase 0 экономит время в дальнейших фазах, предотвращает переделки и помогает правильно понять задачу с первого раза.