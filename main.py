import subprocess
import os
import sys

def run_git_command(command, cwd):
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def push_to_git(project_path, repo_url):
    if not os.path.exists(project_path):
        print(f"❌ Directory {project_path} not found")
        return False

    commands = [

        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit"],
        ["git", "remote", "add", "origin", repo_url],
        ["git", "branch", "-M", "main"],
        ["git", "push", "-u", "origin", "main"]
    ]

    os.chdir(project_path)

    for cmd in commands:
        if not run_git_command(cmd, project_path):
            return False

    print("🎉 Code successfully pushed to remote repository!")
    return True

if __name__ == "__main__":
    print("=== Git Automation ===")
    path = input("📁 Enter project directory path: ").strip()
    url = input("🌐 Enter repository HTTPS/SSH URL: ").strip()

    if not push_to_git(path, url):
        print("\n❌ Push failed. Check errors above.")
        sys.exit(1)
