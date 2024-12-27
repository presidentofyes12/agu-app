# === check_nostr_bridge.sh ===
#!/bin/bash
echo "Running pre-update checks for nostr_bridge module..."
echo

echo "Checking required Python libraries..."
python3 -c "import websockets" && echo "[OK] websockets is installed" || echo "[FAIL] websockets is not installed"
python3 -c "import nostr" && echo "[OK] nostr is installed" || echo "[FAIL] nostr is not installed"
echo

echo "Checking module file location..."
if [ -d "/opt/odoo/custom_addons/nostr_bridge" ]; then
    echo "[OK] Module directory exists at /opt/odoo/custom_addons/nostr_bridge"
else
    echo "[FAIL] Module directory not found"
fi

if [ -f "/opt/odoo/custom_addons/nostr_bridge/__manifest__.py" ]; then
    echo "[OK] __manifest__.py file exists"
else
    echo "[FAIL] __manifest__.py file not found"
fi
echo

echo "Checking __manifest__.py content..."
python3 -c "
import ast
with open('/opt/odoo/custom_addons/nostr_bridge/__manifest__.py', 'r') as f:
    manifest = ast.literal_eval(f.read())
assert 'depends' in manifest and 'data' in manifest
print('[OK] __manifest__.py contains \'depends\' and \'data\' sections')
" || echo "[FAIL] __manifest__.py is missing required sections"
echo

echo "Checking configuration parameters..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "
SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM ir_config_parameter WHERE key='nostr.relay_urls' AND value IS NOT NULL AND value != '')
    OR EXISTS (SELECT 1 FROM nostr_relay_urls WHERE is_active = true)
    THEN 'OK'
    ELSE 'FAIL'
END;
" | grep -q "OK" && echo "[OK] Relay URLs are set in the database" || echo "[FAIL] Relay URLs are not set in the database"
echo

echo "Testing network connectivity..."
for relay in wss://nostr-pub.wellorder.net; do
    timeout 5 python3 -c "
import asyncio, websockets
async def test_connection():
    try:
        async with websockets.connect('$relay', ping_interval=None) as ws:
            print('[OK] Successfully connected to $relay')
    except:
        print('[FAIL] Failed to connect to $relay')
asyncio.get_event_loop().run_until_complete(test_connection())
"
done
echo

echo "Pre-update checks completed."
