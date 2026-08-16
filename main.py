@@
+import json, os
+
+# Load Telegram config from config.json if present. This overrides any hardcoded
+# TELEGRAM_TOKEN / TELEGRAM_CHAT_ID values so secrets are not kept in the repo.
+cfg_path = 'config.json'
+if os.path.exists(cfg_path):
+    try:
+        with open(cfg_path, 'r') as _f:
+            _cfg = json.load(_f)
+        TELEGRAM_TOKEN = _cfg.get('TELEGRAM_TOKEN', globals().get('TELEGRAM_TOKEN', ''))
+        TELEGRAM_CHAT_ID = _cfg.get('TELEGRAM_CHAT_ID', globals().get('TELEGRAM_CHAT_ID', ''))
+    except Exception as _e:
+        print('Failed to load config.json:', _e)
+        TELEGRAM_TOKEN = globals().get('TELEGRAM_TOKEN', '')
+        TELEGRAM_CHAT_ID = globals().get('TELEGRAM_CHAT_ID', '')
+else:
+    # If config.json is not present, fall back to any existing hardcoded values
+    TELEGRAM_TOKEN = globals().get('TELEGRAM_TOKEN', '')
+    TELEGRAM_CHAT_ID = globals().get('TELEGRAM_CHAT_ID', '')
+
@@
