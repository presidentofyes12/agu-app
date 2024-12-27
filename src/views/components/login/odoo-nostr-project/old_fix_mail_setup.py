import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_db_params():
    """Get database parameters from environment variables."""
    return {
        'dbname': os.environ.get('DB_NAME', 'odoodb'),
        'user': os.environ.get('DB_USER', 'odoo'),
        'password': os.environ.get('DB_PASSWORD', 'odoo'),
        'host': os.environ.get('DB_HOST', 'postgres'),
        'port': os.environ.get('DB_PORT', '5432')
    }

def check_module_installed(cursor, module_name):
    """Check if a module is installed."""
    cursor.execute("""
        SELECT state
        FROM ir_module_module
        WHERE name = %s
    """, (module_name,))
    result = cursor.fetchone()
    return result and result[0] == 'installed'

def clean_mail_channel_data(db_params):
    """Clean up existing mail channel data to prevent conflicts."""
    print("Cleaning mail channel data...")
    connection = psycopg2.connect(**db_params)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    
    try:
        # First check if mail module is installed
        if not check_module_installed(cursor, 'mail'):
            print("Mail module not installed - skipping cleanup")
            return False

        cursor.execute("""
            DO $$
            BEGIN
                -- Disable triggers temporarily
                ALTER TABLE mail_channel_member DISABLE TRIGGER ALL;
                ALTER TABLE mail_channel DISABLE TRIGGER ALL;
                
                -- Safe cleanup of existing channel data
                DELETE FROM mail_channel_member WHERE id IS NOT NULL;
                DELETE FROM mail_channel WHERE id IS NOT NULL;
                
                -- Reset sequences
                ALTER SEQUENCE IF EXISTS mail_channel_id_seq RESTART WITH 1;
                ALTER SEQUENCE IF EXISTS mail_channel_member_id_seq RESTART WITH 1;
                
                -- Clean up any orphaned references
                DELETE FROM ir_model_data 
                WHERE model IN ('mail.channel', 'mail.channel.member');
                
                -- Clean up any leftover data in related tables
                DELETE FROM mail_message WHERE model = 'mail.channel';
                DELETE FROM mail_followers WHERE res_model = 'mail.channel';
                
                -- Re-enable triggers
                ALTER TABLE mail_channel_member ENABLE TRIGGER ALL;
                ALTER TABLE mail_channel ENABLE TRIGGER ALL;
            END $$;
        """)
        print("Mail channel data cleaned successfully")
        return True
        
    finally:
        cursor.close()
        connection.close()

def setup_mail_channel(db_params):
    """Set up initial mail channel correctly."""
    print("Setting up mail channel...")
    connection = psycopg2.connect(**db_params)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    
    try:
        # Check if mail module is installed
        if not check_module_installed(cursor, 'mail'):
            print("Mail module not installed - skipping channel setup")
            return False

        # Create general channel with proper references
        cursor.execute("""
            WITH channel_creation AS (
                INSERT INTO mail_channel (
                    name, 
                    channel_type, 
                    description,
                    public,
                    group_public_id
                )
                VALUES (
                    'general', 
                    'channel', 
                    'General announcements for all employees.',
                    't',
                    (SELECT id FROM res_groups WHERE name = 'Internal User' LIMIT 1)
                )
                ON CONFLICT (name) DO UPDATE 
                SET channel_type = EXCLUDED.channel_type,
                    description = EXCLUDED.description
                RETURNING id
            )
            INSERT INTO ir_model_data (
                name, 
                model, 
                module, 
                res_id, 
                noupdate
            )
            SELECT 
                'channel_all_employees', 
                'mail.channel', 
                'mail', 
                id,
                true
            FROM channel_creation
            ON CONFLICT (module, name) 
            DO UPDATE SET res_id = EXCLUDED.res_id;
        """)
        
        # Add active users to the channel with proper partner handling
        cursor.execute("""
            WITH channel AS (
                SELECT id FROM mail_channel WHERE name = 'general'
            ),
            valid_partners AS (
                SELECT DISTINCT partner_id 
                FROM res_users 
                WHERE active = true 
                AND partner_id IS NOT NULL
            )
            INSERT INTO mail_channel_member (
                channel_id, 
                partner_id, 
                seen_message_id
            )
            SELECT 
                channel.id, 
                vp.partner_id,
                0
            FROM channel
            CROSS JOIN valid_partners vp
            WHERE NOT EXISTS (
                SELECT 1 
                FROM mail_channel_member m
                WHERE m.channel_id = channel.id
                AND m.partner_id = vp.partner_id
            );
        """)
        
        print("Mail channel setup completed successfully")
        return True
        
    except Exception as e:
        print(f"Error during mail channel setup: {str(e)}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    try:
        db_params = get_db_params()
        print(f"Connecting to PostgreSQL at {db_params['host']}:{db_params['port']}...")
        
        # Execute cleanup and setup with proper error handling
        cleanup_success = clean_mail_channel_data(db_params)
        if cleanup_success:
            print("Waiting for transactions to complete...")
            time.sleep(2)
            if setup_mail_channel(db_params):
                print("Mail channel initialization completed successfully")
            else:
                print("Failed to setup mail channel - check the logs for details")
                exit(1)
        else:
            print("Mail channel initialization deferred - waiting for mail module installation")
            exit(0)
    except Exception as e:
        print(f"Error during mail channel setup: {str(e)}")
        raise
