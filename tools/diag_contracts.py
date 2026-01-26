import inspect

print("=== CONTRACT DIAGNOSTIC ===\n")

# ---- UsersService ----
try:
    from core.services.users import UsersService
    sig = inspect.signature(UsersService.__init__)
    print("[UsersService.__init__] signature:", sig)
except Exception as e:
    print("[UsersService] IMPORT ERROR:", e)

print()

# ---- PostgresUsersStorage ----
try:
    from core.storage.postgres_users import PostgresUsersStorage
    sig = inspect.signature(PostgresUsersStorage.__init__)
    print("[PostgresUsersStorage.__init__] signature:", sig)
except Exception as e:
    print("[PostgresUsersStorage] IMPORT ERROR:", e)

print()

# ---- SubscriptionGate ----
try:
    from core.services.subscription_gate import SubscriptionGate
    sig = inspect.signature(SubscriptionGate.__init__)
    print("[SubscriptionGate.__init__] signature:", sig)
except Exception as e:
    print("[SubscriptionGate] IMPORT ERROR:", e)

print()

# ---- SubscriptionsService ----
try:
    from core.services.subscriptions import SubscriptionsService
    sig = inspect.signature(SubscriptionsService.__init__)
    print("[SubscriptionsService.__init__] signature:", sig)
except Exception as e:
    print("[SubscriptionsService] IMPORT ERROR:", e)

print("\n=== END ===")
