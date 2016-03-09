#!/usr/bin/env python
"""
Usage: commit-protect.py

Expects to be run in a CircleCI environment with the following additional
environment variables set:

CIRCLE_TOKEN: A CircleCI API token.
GITHUB_TOKEN: A GitHub API token with `repo` OAuth scope.

Usage in circle.yml:

deployment:
  production:
    branch: production
    commands:
      - ./commit-protect.py
      - ./deploy_prod.sh
  staging:
    branch: master
    commands:
      - ./commit-protect.py
      - ./deploy_staging.sh
"""

import sys
import os

import requests
from parse import parse

circle_api = ('https://circleci.com/api/v1/project/{circle_username}/'
              '{circle_repo}/{circle_build}?circle-token={circle_token}')
github_api = ('https://api.github.com/repos/{username}/{repo}/compare/'
              '{circle_branch}...{sha1}')

commit_pattern = '{message} - depends on {username}/{repo}#{sha1}'
error_message = ('Refusing to deploy {current_sha1}, depends on {username}/'
                 '{repo}#{sha1} being deployed to {circle_branch}.')

circle_username = os.environ.get('CIRCLE_PROJECT_USERNAME')
circle_repo = os.environ.get('CIRCLE_PROJECT_REPONAME')
circle_build = os.environ.get('CIRCLE_BUILD_NUM')
circle_branch = os.environ.get('CIRCLE_BRANCH')

circle_token = os.environ.get('CIRCLE_TOKEN')
github_token = os.environ.get('GITHUB_TOKEN')

if __name__ == '__main__':
    # Get a list of commits in the current CI build
    res = requests.get(circle_api.format(**vars()))

    # Look for commit messages matching `commit_pattern`
    for commit in res.json().get('all_commit_details', []):
        subject = commit.get('subject', '')
        current_sha1 = commit.get('commit')

        if ' - depends on ' in subject:
            # Extract dependency username/repo#sha1
            depends = parse(commit_pattern, subject)

            username = depends['username']
            repo = depends['repo']
            sha1 = depends['sha1']

            # Fetch github commit status in dependent branch
            # Will be one of `ahead`, `behind` or `identical`
            res = requests.get(github_api.format(**vars()), headers=dict(
                authorization='token {github_token}'.format(**vars()))
            )

            status = res.json().get('status')

            # Fail build if commit does not exist in dependent branch
            if status == 'behind' or status == 'identical':
                sys.exit(os.EX_OK)
            else:
                print(error_message.format(**vars()))

                sys.exit(os.EX_TEMPFAIL)
