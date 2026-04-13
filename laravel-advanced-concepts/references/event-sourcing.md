# Event Sourcing in Laravel

## Why Event Sourcing?

Traditional apps store **current state** (the latest `balance`, `status`, etc.). Event sourcing stores **the sequence of events that produced that state**. Current state is derived by replaying events.

Benefits:
- Complete, immutable audit trail — no one can alter history
- Replay events to rebuild any projection (analytics, new read models)
- Debug by inspecting the exact sequence of events that led to a bug
- GDPR: encrypt each user's events with their own key; "forget" = destroy the key
- Time travel: rebuild state as of any point in time

The tradeoff: more complexity — you need to think in events, manage projections separately from events, and eventually deal with schema evolution.

**The canonical use case is a credit/wallet/points system.** Never store `balance = 100` directly. Store `CreditAdded(50)`, `CreditAdded(75)`, `CreditSpent(25)` — balance is the sum. This makes fraud detection, refunds, and audits trivial.

---

## Library 1: spatie/laravel-event-sourcing

Battle-tested, most widely used, follows classic DDD event sourcing patterns.

### Installation

```bash
composer require spatie/laravel-event-sourcing
php artisan vendor:publish --provider="Spatie\EventSourcing\EventSourcingServiceProvider"
php artisan migrate
```

### Key Concepts

- **StoredEvent**: an event persisted to the `stored_events` table
- **Aggregate**: encapsulates business logic, records events, reconstructed by replaying events
- **Projector**: listens to events and builds read-model tables (the queryable state)
- **Reactor**: listens to events and triggers side effects (emails, webhooks) — runs once, not on replay

### Defining Events

```php
use Spatie\EventSourcing\StoredEvents\ShouldBeStored;

class MoneyAdded implements ShouldBeStored
{
    public function __construct(
        public readonly string $accountUuid,
        public readonly int $amountInCents,
        public readonly string $reason,
    ) {}
}

class MoneySubtracted implements ShouldBeStored
{
    public function __construct(
        public readonly string $accountUuid,
        public readonly int $amountInCents,
        public readonly string $reason,
    ) {}
}
```

### Creating an Aggregate

```php
use Spatie\EventSourcing\AggregateRoots\AggregateRoot;

class AccountAggregate extends AggregateRoot
{
    private int $balanceInCents = 0;

    public function addMoney(int $amountInCents, string $reason): static
    {
        // Validate business rules here
        if ($amountInCents <= 0) {
            throw new InvalidAmountException();
        }

        $this->recordThat(new MoneyAdded(
            accountUuid: $this->uuid(),
            amountInCents: $amountInCents,
            reason: $reason,
        ));

        return $this;
    }

    public function subtractMoney(int $amountInCents, string $reason): static
    {
        if ($amountInCents > $this->balanceInCents) {
            throw new InsufficientFundsException();
        }

        $this->recordThat(new MoneySubtracted(
            accountUuid: $this->uuid(),
            amountInCents: $amountInCents,
            reason: $reason,
        ));

        return $this;
    }

    // Apply methods rebuild state from events (called during replay)
    protected function applyMoneyAdded(MoneyAdded $event): void
    {
        $this->balanceInCents += $event->amountInCents;
    }

    protected function applyMoneySubtracted(MoneySubtracted $event): void
    {
        $this->balanceInCents -= $event->amountInCents;
    }
}
```

### Using the Aggregate

```php
// Record new events (this persists them)
AccountAggregate::retrieve($accountUuid)
    ->addMoney(5000, 'Initial deposit')
    ->persist();

// Retrieve, apply business logic, persist
AccountAggregate::retrieve($accountUuid)
    ->subtractMoney(1000, 'Purchase #1234')
    ->persist();
```

### Creating a Projector

Projectors listen to stored events and maintain queryable Eloquent models:

```php
use Spatie\EventSourcing\EventHandlers\Projectors\Projector;

class AccountProjector extends Projector
{
    public function onMoneyAdded(MoneyAdded $event): void
    {
        $account = Account::findByUuid($event->accountUuid);
        $account->balance_in_cents += $event->amountInCents;
        $account->save();
    }

    public function onMoneySubtracted(MoneySubtracted $event): void
    {
        $account = Account::findByUuid($event->accountUuid);
        $account->balance_in_cents -= $event->amountInCents;
        $account->save();
    }
}
```

Register in `event-sourcing.php` config or auto-discover. Query the `Account` model normally:

```php
Account::findByUuid($uuid)->balance_in_cents; // always up to date
```

### Creating a Reactor

Reactors are for side effects — they run once, not on replay:

```php
use Spatie\EventSourcing\EventHandlers\Reactors\Reactor;

class AccountReactor extends Reactor
{
    public function onMoneySubtracted(MoneySubtracted $event): void
    {
        // Send a receipt email — runs once when event fires, not during replay
        Mail::to($event->accountUuid)->send(new ReceiptMail($event));
    }
}
```

### Replaying Events

```bash
# Rebuild all projections from scratch
php artisan event-sourcing:replay
```

---

## Library 2: hirethunk/verbs

Newer library with a simpler, more opinionated API. Less boilerplate, type-safe state, excellent DX.

### Installation

```bash
composer require thunk/verbs
php artisan vendor:publish --provider="Thunk\Verbs\VerbsServiceProvider"
php artisan migrate
```

### Key Concepts

- **Event**: fires and mutates state directly; no separate aggregate
- **State**: typed PHP object that holds the aggregate's current state (auto-snapshotted)
- No explicit "apply" methods — state mutation happens inside the event's `apply` method
- **`handle()`**: optional side effects (emails, etc.) — not run during replay

### Defining Events with Verbs

```php
use Thunk\Verbs\Event;
use Thunk\Verbs\Attributes\Autodiscovery\AppliesToState;

#[AppliesToState(AccountState::class)]
class MoneyWasAdded extends Event
{
    public int $account_id;
    public int $amount_in_cents;
    public string $reason;

    public function apply(AccountState $state): void
    {
        $state->balance_in_cents += $this->amount_in_cents;
    }

    public function handle(): void
    {
        // Side effects go here — not replayed
        // Mail::send(...), dispatch(new SomeJob()), etc.
    }
}
```

### State class

```php
use Thunk\Verbs\State;

class AccountState extends State
{
    public int $balance_in_cents = 0;

    public function canSubtract(int $amount): bool
    {
        return $this->balance_in_cents >= $amount;
    }
}
```

### Firing events

```php
MoneyWasAdded::fire(
    account_id: $accountId,
    amount_in_cents: 5000,
    reason: 'Initial deposit',
);
```

### Reading state

```php
$state = AccountState::load($accountId);
$state->balance_in_cents; // current balance
```

### Verbs vs Spatie — Which to choose?

| | Spatie | Verbs |
|---|---|---|
| Maturity | Mature, v2 stable | Newer, actively developed |
| API complexity | Higher (Aggregate, Projector, Reactor) | Lower (Event + State) |
| Projections | Explicit Projector classes | Built into State, or custom |
| Snapshotting | Manual | Automatic |
| Resources | Many blog posts, tutorials | Growing ecosystem |
| Best for | Teams familiar with DDD/CQRS | New projects, simpler API preferred |

---

## Schema Evolution

Events are immutable, but your event classes change over time. Strategies:

1. **Upcasting** (Spatie): transform old event payloads before they're deserialized
2. **Never change events** — only add new event types; old events keep their original meaning
3. **Version your event classes**: `MoneyAddedV2` with a migration path from `MoneyAdded`

---

## Testing Event Sourcing

### Spatie
```php
// Assert events were recorded
$aggregate = AccountAggregate::retrieve($uuid);
$aggregate->addMoney(100, 'test');
// Check the recorded events before persisting
$this->assertCount(1, $aggregate->getRecordedEvents());

// Or use the fake
\Spatie\EventSourcing\Facades\EventSource::fake();
\Spatie\EventSourcing\Facades\EventSource::assertRecorded(MoneyAdded::class);
```

### Verbs
```php
Verbs::fake();
MoneyWasAdded::fire(account_id: 1, amount_in_cents: 100, reason: 'test');
Verbs::assertDispatched(MoneyWasAdded::class);
```

---

## GDPR "Right to Be Forgotten" with Event Sourcing

Encrypt each user's events with a unique key. Store the key in a separate table. To "forget" a user, delete their key — their events become unreadable (crypto-shredding):

```php
// Spatie: use the `SerializesModels` or encrypt the payload before storing
// Each user gets a unique AES-256 key stored in `encryption_keys` table
// On GDPR request: delete row from `encryption_keys`
// Events remain in storage but are unreadable (decryption fails gracefully)
```

This is the preferred approach when you can't delete events (e.g., financial compliance requires you keep events but not PII).
