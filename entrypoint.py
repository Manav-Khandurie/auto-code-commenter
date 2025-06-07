from git import Repo
import subprocess
import os
import sys
from github import Github

def pr_exists(g, repo_name, branch):
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch}")
    return pulls.totalCount > 0

def run():
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
    GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
    BOT_NAME = os.environ.get("BOT_NAME", "code-comment-bot")
    BOT_EMAIL = os.environ.get("BOT_EMAIL", "bot@your-org.com")
    BRANCH_NAME = os.environ.get("BOT_BRANCH", "auto/comment-update")
    PR_TITLE = os.environ.get("PR_TITLE", "🤖 Add Code Comments")
    PR_BODY = os.environ.get("PR_BODY", "This PR includes auto-generated code comments.")
    
    config_arg = sys.argv[1] if len(sys.argv) > 1 else None
    src_arg = sys.argv[2] if len(sys.argv) > 2 else "."
    gh = Github(GITHUB_TOKEN)

    if pr_exists(gh, GITHUB_REPOSITORY, BRANCH_NAME):
        print("✅ PR already exists. Skipping PR creation.")
        exit(0)

    # Safe Git
    subprocess.run(["git", "config", "--global", "--add", "safe.directory", os.getcwd()], check=True)

    repo = Repo(".")

    # Auth + identity
    repo.config_writer().set_value("user", "name", BOT_NAME).release()
    repo.config_writer().set_value("user", "email", BOT_EMAIL).release()

    # Set token-based push URL
    repo_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPOSITORY}.git"
    repo.remotes.origin.set_url(repo_url)


    # Run your bot logic
    subprocess.run([
        "python", "-m", "bot.cli",
        "--config", config_arg,
        "--src", src_arg
    ], check=True)

    repo.git.checkout("-B", BRANCH_NAME)
    repo.git.add(A=True)
    repo.index.commit("🤖 Auto-commented code")
    repo.remotes.origin.push(refspec=f"{BRANCH_NAME}:{BRANCH_NAME}", force=True)


    gh_repo = gh.get_repo(GITHUB_REPOSITORY)
    gh_repo.create_pull(
        title=PR_TITLE,
        body=PR_BODY,
        head=BRANCH_NAME,
        base="main"
    )
    print("✅ Pull request created.")

if __name__ == "__main__":
    
    run()
