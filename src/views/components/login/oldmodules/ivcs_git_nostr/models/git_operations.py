import logging
import git
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import traceback

logger = logging.getLogger(__name__)

class GitOperations:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except Exception as e:
            logger.error(f"Error initializing Git repository: {str(e)}")
            raise UserError(_("Failed to initialize Git repository: %s") % str(e))

    def create_branch(self, branch_name: str) -> str:
        try:
            new_branch = self.repo.create_head(branch_name)
            logger.info(f"Branch created: {branch_name}")
            return new_branch.name
        except git.GitCommandError as e:
            logger.error(f"Git command error while creating branch: {str(e)}")
            raise UserError(_("Failed to create branch: %s") % str(e))
        except Exception as e:
            logger.error(f"Error creating branch: {str(e)}")
            raise UserError(_("Failed to create branch: %s") % str(e))

    def update_branch(self, branch_name: str):
        try:
            branch = self.repo.heads[branch_name]
            branch.checkout()
            self.repo.git.pull()
            logger.info(f"Branch updated: {branch_name}")
        except git.GitCommandError as e:
            logger.error(f"Git command error while updating branch: {str(e)}")
            raise UserError(_("Failed to update branch: %s") % str(e))
        except Exception as e:
            logger.error(f"Error updating branch: {str(e)}")
            raise UserError(_("Failed to update branch: %s") % str(e))

    def list_branches(self) -> list:
        try:
            branches = [head.name for head in self.repo.heads]
            logger.info("Branches listed successfully")
            return branches
        except Exception as e:
            logger.error(f"Error listing branches: {str(e)}")
            raise UserError(_("Failed to list branches: %s") % str(e))

    def sync_repository(self):
        try:
            self.repo.git.fetch()
            self.repo.git.pull()
            logger.info("Repository synchronized successfully")
        except git.GitCommandError as e:
            logger.error(f"Git command error while syncing repository: {str(e)}")
            raise UserError(_("Failed to sync repository: %s") % str(e))
        except Exception as e:
            logger.error(f"Error syncing repository: {str(e)}")
            raise UserError(_("Failed to sync repository: %s") % str(e))
