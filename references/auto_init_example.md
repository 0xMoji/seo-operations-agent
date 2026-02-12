# Auto-Initialization Example

This document demonstrates the automatic Airtable base creation feature.

## Example Flow

### Step 1: User Configures API Key

User adds to `.env`:
```bash
AIRTABLE_API_KEY=patXXXXXXXXXXXXXXXX
OPENAI_API_KEY=sk-XXXXXXXXXXXX
```

Note: `AIRTABLE_BASE_ID` is **not** required initially.

### Step 2: User Initiates Setup

```
User: 我想启动 SEO 自动化
```

### Step 3: System Checks and Creates

The skill automatically:

1. **Checks if API key is valid** ✅
2. **Detects no AIRTABLE_BASE_ID** → Creates new base
3. **Uses Airtable Metadata API** to:
   - Get first workspace ID
   - Create base: "SEO Content Hub"
   - Create 3 tables with complete schema:
     - Campaign_Settings (9 fields)
     - Keyword_Pool (3 fields)
     - Content_Hub (9 fields with status select options)
4. **Saves base ID to `.env`** automatically
5. **Returns base URL** for immediate access

### Step 4: System Response

```
✅ 已自动创建 Airtable Base!

📊 Base ID: appABCDEF1234567
🔗 访问链接: https://airtable.com/appABCDEF1234567

已创建的表：
- Campaign_Settings (运营计划配置)
- Keyword_Pool (关键词库)
- Content_Hub (内容中心)

⚠️ 重要：Base ID 已保存到 .env 文件，请重启 skill 使其生效。
```

---

## Edge Cases Handled

### Case 1: Base exists but missing tables

```python
# Existing base has only Campaign_Settings
# System detects missing: Keyword_Pool, Content_Hub
result = {
    "status": "updated",
    "message": "Created missing tables: Keyword_Pool, Content_Hub"
}
```

### Case 2: Base exists and complete

```python
# All 3 tables present
result = {
    "status": "exists",
    "message": "Base and tables already configured",
    "base_id": "appXXXXXXXXXX"
}
```

### Case 3: Invalid base ID

```python
# base_id in .env points to deleted/inaccessible base
# System catches exception and creates new base
result = {
    "status": "created",
    # ... new base created
}
```

---

## API Permissions Required

The auto-initialization feature requires **4 scopes**:

```json
{
  "scopes": [
    "data.records:read",      // Read records
    "data.records:write",     // Create records
    "schema.bases:read",      // Check existing schema
    "schema.bases:write"      // Create base + tables
  ]
}
```

**Without schema permissions**: User must create base manually (fallback to original setup flow).

---

## Technical Implementation

### Key Methods

1. **`check_and_initialize_base()`**
   - Entry point for auto-setup
   - Returns status dict

2. **`_get_base_schema()`**
   - Uses Metadata API to read existing structure
   - `GET /v0/meta/bases/{baseId}/tables`

3. **`_create_base_with_schema()`**
   - Creates new base with complete schema in one call
   - `POST /v0/meta/bases`

4. **`_build_schema_definition()`**
   - Returns complete JSON schema for all 3 tables
   - Includes field types, select options, etc.

5. **`_create_missing_tables()`**
   - Adds individual tables to existing base
   - `POST /v0/meta/bases/{baseId}/tables`

### Schema Definition Example

```python
{
    "name": "Content_Hub",
    "description": "Generated content library with publishing workflow",
    "fields": [
        {"name": "Title", "type": "singleLineText"},
        {"name": "Body", "type": "multilineText"},
        {
            "name": "Status",
            "type": "singleSelect",
            "options": {
                "choices": [
                    {"name": "待审核"},
                    {"name": "已批准"},
                    {"name": "已发布"}
                ]
            }
        }
    ]
}
```

---

## Benefits

✅ **Zero manual setup** - No copy-pasting field names  
✅ **Error-proof** - Correct schema guaranteed  
✅ **Fast onboarding** - From API key to working system in < 1 minute  
✅ **Idempotent** - Safe to run multiple times  
✅ **Self-healing** - Detects and fills missing tables

---

## Comparison: Before vs After

### Before (Manual Setup)
1. Get Airtable API key
2. Create base manually
3. Create Campaign_Settings table
4. Add 9 fields one by one
5. Create Keyword_Pool table
6. Add 3 fields with correct types
7. Create Content_Hub table
8. Add 9 fields with select options
9. Copy base ID
10. Update .env file

**Time**: ~15-20 minutes  
**Error-prone**: Yes (field names, types, options)

### After (Auto Setup)
1. Get Airtable API key
2. Run skill
3. Say "启动 SEO 自动化"

**Time**: < 1 minute  
**Error-prone**: No

---

## User Experience

```
User: 我想启动 SEO 自动化

Agent: ✅ 已自动创建 Airtable Base!
        📊 Base ID: appXXX
        🔗 https://airtable.com/appXXX

User: [clicks link, sees fully configured base]

User: 启动一个为期 30 天的计划...

Agent: ✅ 运营计划已创建！
```

**Seamless experience** - User never needs to touch Airtable settings.
