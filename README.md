# SQL Playground Local

A safe, local-first SQLite playground for running SQL scripts, inspecting schemas, exporting query results, and learning SQL without a server.

> **Status:** Functional Python 3.10+ CLI. Uses only the Python standard library at runtime.

## English

### Overview
SQL Playground Local is a small command-line workspace around SQLite. It can create/open local databases, execute SQL scripts, run read-only queries with table or JSON output, inspect tables/views/indexes, describe columns, and export query results to CSV. It is useful for students, developers, quick data exploration, reproducible examples, and CI smoke checks.

### Why it exists
A database server is unnecessary for many SQL experiments. This project provides a predictable local workflow using SQLite, while adding validation, readable output, explicit read-only query mode, and machine-friendly JSON.

### Key features
- Create or open SQLite database files automatically.
- Execute `.sql` scripts transactionally with `exec`.
- Run a single **read-only** `SELECT`, `WITH`, `PRAGMA`, or `EXPLAIN` statement with `query`.
- Table and JSON query output.
- List tables, views, indexes, and triggers with `schema`.
- Describe table/view columns with `describe`.
- Export read-only query results to UTF-8 CSV with `export`.
- Parameter binding via repeated `--param name=value` arguments.
- `:memory:` support for programmatic/one-process use.
- Clear exit codes and errors; no network access or telemetry.
- Python API for embedding the core operations.

### Preview
```text
$ sql-playground demo.db exec examples/setup.sql
Script executed successfully.

$ sql-playground demo.db query "SELECT name, score FROM learners ORDER BY score DESC"
name   | score
-------+------
Layla  | 95
Omar   | 88
2 row(s)
```

This is a terminal application, so screenshots are optional. A terminal capture showing `schema`, `describe learners`, and a query is the most useful preview.

### Requirements
- Python 3.10+
- No third-party runtime dependencies

### Installation
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

### Usage
```bash
sql-playground demo.db exec examples/setup.sql
sql-playground demo.db schema
sql-playground demo.db describe learners
sql-playground demo.db query "SELECT * FROM learners WHERE score >= :min" --param min=90
sql-playground demo.db query "SELECT * FROM learners" --format json
sql-playground demo.db export "SELECT * FROM learners ORDER BY id" results.csv
```

Without installation, from the repository root:
```bash
python -m sql_playground demo.db schema
```

`exec` accepts a SQL file path or `-` for stdin. `query` intentionally accepts one read-only statement only. Named parameter values are strings; use SQL `CAST()` when a specific type is required.

### Configuration
There are no environment variables or secrets. The database path is explicit on every command. SQLite foreign keys are enabled for each connection, and busy timeout defaults to 5 seconds in the Python API.

### Python API
```python
from sql_playground.core import Playground

with Playground("demo.db") as db:
    rows = db.query("SELECT name, score FROM learners WHERE score >= :min", {"min": 90})
    print(rows.columns, rows.rows)
```

### Project structure
```text
src/sql_playground/   Core library, CLI, module entry point
tests/                Unit and CLI tests
examples/setup.sql    Reproducible sample schema/data
.github/workflows/    CI
```

### Testing
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```
CI runs the test suite on Python 3.10, 3.12, and 3.13 on Ubuntu, Windows, and macOS.

### Security & privacy
All work is local. The application does not transmit database contents. `query`/`export` reject mutating SQL and multiple statements. `exec` is intentionally powerful and can modify the selected database, so only execute SQL scripts you trust and back up valuable databases first. SQLite files may themselves contain sensitive data; protect them using normal filesystem controls.

### Limitations
- SQLite only; this is not a PostgreSQL/MySQL client.
- `exec` runs trusted scripts and is not a sandbox for hostile SQL.
- Parameter CLI values are strings.
- The table renderer is intentionally simple and does not provide an interactive TUI.
- Read-only classification is conservative and syntax-based; SQLite remains the final SQL parser.

### Optional roadmap
Possible future additions include query timing, `.dump` helpers, richer type-aware CLI parameters, and an optional interactive REPL. These are not required for the current core workflow.

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Please add tests for behavior changes and keep runtime dependencies minimal.

### License
MIT — see [LICENSE](LICENSE).

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
SQL Playground Local أداة سطر أوامر محلية مبنية على SQLite لتجربة SQL بدون خادم. تستطيع إنشاء أو فتح قاعدة بيانات، تنفيذ ملفات SQL، تشغيل استعلامات قراءة آمنة نسبيًا، استعراض المخطط، وصف الأعمدة، وتصدير النتائج إلى CSV.

### لماذا المشروع؟
كثير من تجارب SQL والدروس والفحوصات السريعة لا تحتاج خادم قواعد بيانات. يوفر المشروع سير عمل محليًا واضحًا وقابلًا للتكرار مع رسائل أخطاء مفهومة ومخرجات JSON مناسبة للأتمتة.

### الميزات
- إنشاء/فتح ملفات SQLite تلقائيًا.
- تنفيذ ملفات `.sql` من خلال أمر `exec`.
- أمر `query` مخصص لعبارة قراءة واحدة من `SELECT` أو `WITH` أو `PRAGMA` أو `EXPLAIN`.
- عرض النتائج كجدول أو JSON.
- استعراض الجداول والعروض والفهارس والمحفزات.
- وصف أعمدة جدول أو عرض.
- تصدير نتائج الاستعلام إلى CSV بترميز UTF-8.
- معاملات مسماة عبر `--param name=value`.
- دعم Python API، دون اتصال شبكة أو تتبع استخدام.

### المتطلبات والتثبيت
يتطلب Python 3.10 أو أحدث ولا توجد اعتماديات تشغيل خارجية.
```bash
python -m venv .venv
python -m pip install -e .
```

### الاستخدام
```bash
sql-playground demo.db exec examples/setup.sql
sql-playground demo.db schema
sql-playground demo.db describe learners
sql-playground demo.db query "SELECT * FROM learners WHERE score >= :min" --param min=90
sql-playground demo.db export "SELECT * FROM learners" results.csv
```
يمكن أيضًا التشغيل من جذر المشروع باستخدام `python -m sql_playground`.

### الإعداد
لا توجد متغيرات بيئة أو مفاتيح سرية. تحدد مسار قاعدة البيانات صراحة في كل أمر، ويتم تفعيل قيود المفاتيح الأجنبية لكل اتصال.

### Python API
يمكن استيراد `Playground` من `sql_playground.core` واستخدامه داخل `with` لتنفيذ الاستعلامات واستلام الأعمدة والصفوف برمجيًا.

### بنية المشروع
المصدر داخل `src/sql_playground/`، والاختبارات داخل `tests/`، والمثال داخل `examples/`، وCI داخل `.github/workflows/`.

### الاختبارات
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```
وتغطي CI إصدارات Python 3.10 و3.12 و3.13 على Linux وWindows وmacOS.

### الأمان والخصوصية
كل العمليات محلية ولا يرسل التطبيق محتوى قاعدة البيانات لأي جهة. أوامر `query` و`export` ترفض SQL المعدّل للبيانات وتعدد العبارات. أما `exec` فهو مصمم لتنفيذ سكربتات موثوقة ويمكنه تعديل قاعدة البيانات؛ لذلك لا تشغّل ملفات SQL غير موثوقة واحتفظ بنسخة احتياطية من البيانات المهمة.

### القيود
المشروع يدعم SQLite فقط، وليس بيئة sandbox لملفات SQL الخبيثة، وقيم معاملات CLI تعامل كنصوص، ولا توجد واجهة TUI تفاعلية. تصنيف القراءة محافظ ويظل SQLite هو المحلل النهائي للصياغة.

### تطوير اختياري
يمكن مستقبلًا إضافة قياس زمن الاستعلام، ومساعدات dump، ومعاملات CLI واعية بالأنواع، وREPL اختياري.

### المساهمة
راجع [CONTRIBUTING.md](CONTRIBUTING.md)، وأضف اختبارات لأي تغيير سلوكي وحافظ على بساطة الاعتماديات.

### الترخيص
MIT — راجع [LICENSE](LICENSE).

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
