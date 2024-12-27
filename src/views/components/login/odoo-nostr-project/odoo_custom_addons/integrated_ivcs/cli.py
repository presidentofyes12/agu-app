import argparse
import os
import git
from nostr.event import Event
from nostr.key import PrivateKey
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitNostrCLI:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.private_key = PrivateKey()

    def create_branch(self, branch_name):
        logger.info(f"Creating branch: {branch_name}")
        self.repo.create_head(branch_name)
        self._create_branch_event(branch_name, 'create')
        logger.info(f"Branch {branch_name} created successfully")

    def delete_branch(self, branch_name):
        logger.info(f"Deleting branch: {branch_name}")
        self.repo.delete_head(branch_name, force=True)
        self._create_branch_event(branch_name, 'delete')
        logger.info(f"Branch {branch_name} deleted successfully")

    def merge_branches(self, source_branch, target_branch):
        logger.info(f"Merging {source_branch} into {target_branch}")
        self.repo.git.checkout(target_branch)
        try:
            self.repo.git.merge(source_branch)
            self._create_branch_event(target_branch, 'merge', source_branch)
            logger.info(f"Merged {source_branch} into {target_branch} successfully")
        except git.GitCommandError as e:
            logger.error(f"Merge conflict: {str(e)}")
            self.repo.git.merge('--abort')
            logger.info("Merge aborted due to conflicts")

    def commit_changes(self, message):
        logger.info(f"Committing changes with message: {message}")
        self.repo.git.add(A=True)
        commit = self.repo.index.commit(message)
        self._create_commit_event(commit)
        logger.info(f"Changes committed successfully. Commit hash: {commit.hexsha}")

    def _create_branch_event(self, branch_name, action, additional_info=None):
        logger.info(f"Creating Nostr event for branch action: {action}")
        content = {
            "action": action,
            "branch_name": branch_name,
            "repo_name": os.path.basename(self.repo_path)
        }
        if additional_info:
            content["additional_info"] = additional_info

        event = Event(
            kind=31227,
            content=json.dumps(content),
            tags=[['r', self.repo_path]],
            public_key=self.private_key.public_key.hex()
        )
        self.private_key.sign_event(event)
        logger.info(f"Nostr event created: {event.id}")
        # Here you would typically publish the event to Nostr relays

    def _create_commit_event(self, commit):
        logger.info(f"Creating Nostr event for commit: {commit.hexsha}")
        content = json.dumps({
            "action": "commit",
            "message": commit.message,
            "author": commit.author.name,
            "email": commit.author.email,
            "date": commit.authored_datetime.isoformat(),
            "hash": commit.hexsha,
            "parent_hashes": [c.hexsha for c in commit.parents],
            "tree_hash": commit.tree.hexsha,
        })
        
        event = Event(
            kind=3121,
            content=content,
            tags=[
                ["r", self.repo_path],
                ["h", commit.hexsha],
            ],
            public_key=self.private_key.public_key.hex()
        )
        self.private_key.sign_event(event)
        logger.info(f"Nostr event created: {event.id}")
        # Here you would typically publish the event to Nostr relays

def main():
    parser = argparse.ArgumentParser(description="Git-Nostr CLI")
    parser.add_argument('repo_path', help="Path to the Git repository")
    parser.add_argument('action', choices=['create-branch', 'delete-branch', 'merge-branches', 'commit'])
    parser.add_argument('--branch-name', help="Name of the branch (for create-branch and delete-branch)")
    parser.add_argument('--source-branch', help="Source branch for merge")
    parser.add_argument('--target-branch', help="Target branch for merge")
    parser.add_argument('--commit-message', help="Commit message")

    args = parser.parse_args()

    cli = GitNostrCLI(args.repo_path)

    if args.action == 'create-branch':
        cli.create_branch(args.branch_name)
    elif args.action == 'delete-branch':
        cli.delete_branch(args.branch_name)
    elif args.action == 'merge-branches':
        cli.merge_branches(args.source_branch, args.target_branch)
    elif args.action == 'commit':
        cli.commit_changes(args.commit_message)

if __name__ == "__main__":
    main()
