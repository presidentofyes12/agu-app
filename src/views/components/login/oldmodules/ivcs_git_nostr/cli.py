import argparse
import logging
import sys
from odoo import api, SUPERUSER_ID
import odoo
from odoo.tools import config as odoo_config
from .models.branch_manager import BranchManager
from .utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def setup_odoo_environment():
    try:
        odoo_config.parse_config([])
        dbname = odoo_config['db_name']
        registry = odoo.registry(dbname)
        with api.Environment.manage(), registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            return env
    except Exception as e:
        logger.error(f"Error setting up Odoo environment: {str(e)}")
        sys.exit(1)

def create_branch(args, env):
    try:
        branch_manager = env['ivcs.branch.manager'].search([('ivcs_item_id.repo_path', '=', args.repo_path)], limit=1)
        if not branch_manager:
            logger.error(f"No branch manager found for repository: {args.repo_path}")
            return

        result = branch_manager.create_branch(args.branch_name)
        logger.info(f"Branch creation result: {result['message']}")
    except Exception as e:
        logger.error(f"Error creating branch: {str(e)}")

def update_branch(args, env):
    try:
        branch_manager = env['ivcs.branch.manager'].search([('ivcs_item_id.repo_path', '=', args.repo_path)], limit=1)
        if not branch_manager:
            logger.error(f"No branch manager found for repository: {args.repo_path}")
            return

        result = branch_manager.update_branch(args.branch_name)
        logger.info(f"Branch update result: {result['message']}")
    except Exception as e:
        logger.error(f"Error updating branch: {str(e)}")

def list_branches(args, env):
    try:
        branch_manager = env['ivcs.branch.manager'].search([('ivcs_item_id.repo_path', '=', args.repo_path)], limit=1)
        if not branch_manager:
            logger.error(f"No branch manager found for repository: {args.repo_path}")
            return

        branches = branch_manager.list_branches()
        logger.info(f"Branches: {branches}")
    except Exception as e:
        logger.error(f"Error listing branches: {str(e)}")

def reconstruct_branches(args, env):
    try:
        branch_manager = env['ivcs.branch.manager'].search([('ivcs_item_id.repo_path', '=', args.repo_path)], limit=1)
        if not branch_manager:
            logger.error(f"No branch manager found for repository: {args.repo_path}")
            return

        result = branch_manager.reconstruct_branches_from_events()
        logger.info(f"Reconstruction result: {result['message']}")
    except Exception as e:
        logger.error(f"Error reconstructing branches: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="IVCS Git Nostr CLI")
    parser.add_argument("repo_path", help="Path to the Git repository")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    create_parser = subparsers.add_parser("create", help="Create a new branch")
    create_parser.add_argument("branch_name", help="Name of the new branch")
    
    update_parser = subparsers.add_parser("update", help="Update an existing branch")
    update_parser.add_argument("branch_name", help="Name of the branch to update")
    
    subparsers.add_parser("list", help="List all branches")
    
    subparsers.add_parser("reconstruct", help="Reconstruct branches from Nostr events")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    env = setup_odoo_environment()
    
    if args.command == "create":
        create_branch(args, env)
    elif args.command == "update":
        update_branch(args, env)
    elif args.command == "list":
        list_branches(args, env)
    elif args.command == "reconstruct":
        reconstruct_branches(args, env)

if __name__ == "__main__":
    main()
