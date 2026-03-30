---
applyTo: "api/**/*.py"
---

# Python Language Instructions

- Use Python 3.11+ syntax (match statements OK, `|` union types OK)
- All async functions: use `async def`, `await` for DB and I/O ops
- Type hints on all function signatures and return types
- Pydantic v2: use `model_validator`, `field_validator`, `ConfigDict`
- SQLAlchemy 2.x: use `Mapped`, `mapped_column`, `relationship` (not legacy Column)
- Imports: stdlib first, third-party second, local third — separated by blank lines
- Error handling: raise `HTTPException` only in Services layer, never in Repositories
- Logging: `logger = logging.getLogger(__name__)` at module top
- No bare `except:` — always catch specific exceptions
- Repository methods accept `AsyncSession` as first param via DI
- Service methods orchestrate repository calls and handle commit/rollback
