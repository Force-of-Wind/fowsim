---
description: Import card data, banlists, and images into the database
---

# Import Cards

Import card data from JSON sources into the database.

## Full Import

For a complete data refresh:

```bash
# Import all card data from JSON
python manage.py importjson

# Import banlist data
python manage.py importBanlist

# Download card images (requires network)
python manage.py downloadCardImages

# Link images to card records
python manage.py assign_existing_card_images
```

## Incremental Import

For updating with new cards only:

```bash
# From remote source
python manage.py incrementalCardImport

# From local JSON file
python manage.py incrementalCardImportLocal
```

## Export

To export current data:

```bash
python manage.py exportJson
```

## Notes

- Run migrations before importing: `python manage.py migrate`
- Image downloads may take significant time
- Check the JSON source files in the project for expected format
