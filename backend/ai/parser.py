import re
import json
from typing import Optional, Dict, Any

def clean_sql(raw_text: str) -> str:
    """Strips markdown code blocks, unwanted tags, and cleans generated SQL."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    # Remove markdown code fences
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    # Ensure it ends with a semicolon
    if not text.endswith(";"):
        text += ";"
    return text

def extract_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON object from LLM response."""
    if not raw_text:
        return None
    text = raw_text.strip()
    # Remove markdown json code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text).strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: find outer curly brackets
        match = re.search(r"(\{.*\})", text, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
    return None

def format_schema_for_llm(schema_dict: Dict[str, Any]) -> str:
    """Formats an introspected schema dict into a clean text prompt representation."""
    if not schema_dict or not isinstance(schema_dict, dict):
        return "No schema available."
        
    tables = schema_dict.get("tables", {})
    if not tables:
        return "Schema contains no tables."
        
    lines = ["DATABASE SCHEMA:"]
    for table_name, meta in tables.items():
        cols = []
        for col_name, col_info in meta.get("columns", {}).items():
            if isinstance(col_info, dict):
                col_type = col_info.get("type", "TEXT")
                pk = " [PK]" if col_info.get("primary_key") else ""
                cols.append(f"{col_name} ({col_type}){pk}")
            else:
                cols.append(f"{col_name} ({col_info})")
                
        lines.append(f"\nTABLE {table_name}:")
        if meta.get("description"):
            lines.append(f"  Description: {meta['description']}")
        lines.append(f"  Columns: {', '.join(cols)}")
        
        fks = meta.get("foreign_keys", [])
        if fks:
            fk_strs = [f"{fk.get('column')} -> {fk.get('references_table')}.{fk.get('references_column')}" for fk in fks]
            lines.append(f"  Foreign Keys: {', '.join(fk_strs)}")
            
    return "\n".join(lines)
