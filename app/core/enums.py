from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(str, Enum):
    FOOD = "food"
    SALARY = "salary"
    RENT = "rent"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    INVESTMENT = "investment"
    OTHER = "other"

class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"