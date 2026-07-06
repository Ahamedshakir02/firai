# Contributing to FirAI

Thank you for your interest in contributing to FirAI! This guide will help you get started.

---

## 🤝 Ways to Contribute

- **Code** — Bug fixes, new features, refactoring
- **Tests** — Unit tests, integration tests, edge cases
- **Documentation** — Guides, API examples, architecture docs
- **AI Models** — Improve classifier, add new detection models
- **Legal Data** — Update legal corpus, add case law
- **Translations** — Support additional languages

---

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/firai.git
cd firai
```

### 2. Set Up Development Environment

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Start services
cd ..
docker compose up --build
```

### 3. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bug
```

---

## Code Standards

### Python (Backend)

**Style:**
- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Document public functions

**Example:**
```python
async def classify_fir(
    narrative: str,
    db: AsyncSession = Depends(get_db),
) -> ClassificationResult:
    """
    Classify a FIR narrative.
    
    Args:
        narrative: FIR text to classify
        db: Database session
        
    Returns:
        ClassificationResult with crime type and severity
    """
    return await engine.classify(narrative)
```

### JavaScript (Frontend)

**Style:**
- Use ES6+ syntax
- Functional components with hooks
- Prop types or TypeScript
- Descriptive variable names

**Example:**
```javascript
export function FIRList({ firs, onSelect }) {
  const [filter, setFilter] = useState('');
  
  const filtered = firs.filter(fir =>
    fir.crime_type.includes(filter)
  );
  
  return (
    <div className="space-y-2">
      {filtered.map(fir => (
        <FIRCard key={fir.id} fir={fir} onSelect={onSelect} />
      ))}
    </div>
  );
}
```

---

## Adding Features

### 1. Create Tests First

```python
# tests/test_my_feature.py
@pytest.mark.asyncio
async def test_my_feature():
    """Test description."""
    result = await my_function()
    assert result is not None
```

### 2. Implement Feature

```python
# services/my_service.py
async def my_function() -> dict:
    """Implementation."""
    return {"result": "value"}
```

### 3. Add API Endpoint

```python
# routers/my_router.py
@router.post("/my-endpoint")
async def my_endpoint(
    request: MyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Endpoint description."""
    result = await MyService.process(request)
    return result
```

### 4. Add Frontend Integration

```javascript
// src/pages/MyPage.jsx
export function MyPage() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/my-endpoint')
      .then(r => r.json())
      .then(setData);
  }, []);
  
  return <div>{/* UI */}</div>;
}
```

---

## Adding AI Models

### 1. Create Model Class

```python
# backend/ai_engine/models/my_model.py
class MyModel:
    def __init__(self):
        self.model = self._load_pretrained()
    
    def predict(self, input_data: str) -> dict:
        """Run inference."""
        return {"prediction": "result"}
```

### 2. Add Training Script

```python
# backend/training/train_my_model.py
async def train_model(data, epochs=50):
    """Train the model."""
    model = MyModel()
    # Training logic
    model.save()
```

### 3. Integrate into Engine

```python
# backend/services/firai_engine.py
class FirAIEngine:
    def __init__(self):
        self.my_model = MyModel()
    
    async def my_feature(self, input_data: str):
        return self.my_model.predict(input_data)
```

### 4. Add Tests

```python
def test_my_model():
    model = MyModel()
    result = model.predict("test input")
    assert "prediction" in result
```

---

## Adding Legal Data

### 1. Update Legal Corpus

```python
# backend/ai_engine/data/legal_corpus.py
LEGAL_SECTIONS = {
    "IPC": {
        "379": {
            "description": "Theft",
            "punishment": "7 years imprisonment",
            # ...
        }
    }
}
```

### 2. Test Changes

```python
def test_legal_section():
    section = LEGAL_SECTIONS["IPC"]["379"]
    assert section["punishment"] is not None
```

### 3. Update Legal Mapper

```python
# Train the legal mapper with new data
python backend/training/train_legal_mapper.py
```

---

## Git Workflow

### Commits

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add confidence scores to FIR classifier"

# Bad
git commit -m "Fix stuff"
```

### Pull Requests

1. Push to your fork
2. Create PR to main branch
3. Link related issues
4. Describe changes and testing

**PR Template:**
```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
- [ ] Tests pass
- [ ] Feature works as expected
- [ ] No regressions

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Commits are meaningful
```

---

## Testing Requirements

### Before Submitting PR

```bash
# Run all tests
cd backend
pytest --cov=.

# Check code style
pylint services/

# Run frontend tests
cd ../frontend
npm test

# Check for TypeErrors
npm run type-check
```

### Test Coverage

Target: **70%+** code coverage

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Documentation

### Code Comments

Only comment the WHY, not the WHAT:

```python
# Good - explains WHY
# We use embedding similarity because keyword matching fails on paraphrases
embedding = encoder.encode(narrative)

# Bad - just describes WHAT
# Create embedding from narrative
embedding = encoder.encode(narrative)
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(arg1: str, arg2: int) -> dict:
    """Brief description.
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        dict: Description of return value
    """
```

### API Documentation

Update Swagger docs:

```python
@router.get("/my-endpoint")
async def my_endpoint():
    """
    My endpoint summary.
    
    Returns:
        dict: Response with fields x, y, z
    """
```

---

## Common Issues

### Import Errors

```python
# Check that module is in __init__.py
from services.my_service import MyService  # Works if in services/__init__.py
```

### Test Failures

```bash
# Run with verbose output
pytest -v tests/test_my_feature.py

# Run single test
pytest tests/test_my_feature.py::test_my_function
```

### Database Issues

```bash
# Reset database
docker compose down -v
docker compose up --build

# Check migrations
python backend/migrations/add_database_indexes.py
```

---

## Review Process

1. **Automated Checks**
   - Tests pass ✅
   - Code coverage target met ✅
   - No lint errors ✅

2. **Code Review**
   - Architecture approved
   - No security issues
   - Performance acceptable

3. **Merge**
   - Squash commits if needed
   - Merge to main
   - Deploy to staging

---

## Questions?

- Check the **13 comprehensive guides** in the repo
- Review **existing code** for patterns
- Ask in **pull request comments**
- Open a **discussion issue**

---

## Code of Conduct

- Be respectful
- Assume good intent
- Help others learn
- Follow project guidelines

---

## License

By contributing, you agree your code will be MIT licensed.

---

**Thank you for contributing to FirAI!** 🙏

