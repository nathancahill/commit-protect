## Commit Protect

Managing feature dependencies over multiple repos can be tricky. Commit Protect adds commit level dependency protection, so features that depend on commits in other repos are not accidentally deployed.

_company/api:_

```
$ git commit -m 'add new api call'
[feature 0d2fd93] add new api call
```

_company/frontend:_

```
$ git commit -m 'implement new api - depends on company/api#0d2fd93'
[feature 726ad6f] implement new api - depends on company/api#0d2fd93
```

Trying to deploy the develop branch of _company/frontend_ before `0d2fd93` is deployed to the develop branch of _company/api_ results in a build error:

```
Refusing to deploy 726ad6f, depends on company/api#0d2fd93 being deployed to develop
```

Dependencies are checked by branch, so stage/prod deploy patterns are supported if the repos use the same branch names.

Commit Protect using the exact pattern `:message - depends on :username/:repo#:sha1` to discover dependencies in commit messages.

### CircleCI

Include `commit-protect.py` as a circle.yml deployment step:

```yaml
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
```

Set two environment variables in Project -> Project Settings -> Environment variables:

 - `CIRCLE_TOKEN` - A CircleCI API token.
 - `GITHUB_TOKEN` - A GitHub API token with `repo` OAuth scope.

Install the Python dependencies, `requests` and `parse`:

```yaml
dependencies:
  pre:
    - pip install requests parse
```
